from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import joblib
import pandas as pd
from pydantic import BaseModel, Field

from .database import Base, engine, get_db
from .models import  (
    Farm,
    SoilProfile,
    CropProfile,
    WaterProfile,
    WeatherRecord,
    Prediction,
    Simulation,
    Recommendation,
    DecisionFeedback
)
from .schemas import (
    FarmCreate,
    FarmResponse,
    SoilProfileCreate,
    SoilProfileResponse,
    CropProfileCreate,
    CropProfileResponse,
    WaterProfileCreate,
    WaterProfileResponse,
    WeatherRecordCreate,
    WeatherRecordResponse,
    PredictionCreate,
    PredictionResponse,
    SimulationCreate,
    SimulationResponse,
    RecommendationCreate,
    RecommendationResponse,
    DecisionFeedbackCreate,
    DecisionFeedbackResponse
)

from . import models
from .water_optimizer import calculate_water_optimization
from .fertilizer_optimizer import calculate_fertilizer_optimization
from .crop_optimizer import select_best_crops
from .profit_optimizer import calculate_profit, compare_crop_profitability
from .sustainability_engine import calculate_sustainability_score
from .climate_risk import calculate_climate_risk
from .early_warning import generate_early_warnings
from .what_if_simulator import simulate_farm_scenario
from .crop_calendar import get_crop_calendar
from .explainable_ai import explain_farming_decision
from .agricultural_advisor import generate_agricultural_advice
from .decision_replay import build_decision_replay
from .decision_pipeline import run_decision_pipeline


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AgriTwin AI",
    description="AI-powered sustainable farming decision and simulation platform",
    version="1.0.0"
)
# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "models",
    "yield_prediction_model.pkl"
)

class YieldPredictionRequest(BaseModel):
    district_code: int = Field(..., ge=1)
    state_code: int = Field(..., ge=1)
    year: int = Field(..., ge=1900, le=2100)

    crop: str = Field(..., min_length=2, max_length=100)
    district: str = Field(..., min_length=2, max_length=100)
    state_name: str = Field(..., min_length=2, max_length=100)

    area_1000_ha: float = Field(..., gt=0)
    rainfall_mm: float = Field(..., ge=0)
    avg_temp_c: float = Field(..., ge=-20, le=60)
    max_temp_c: float = Field(..., ge=-20, le=70)
    min_temp_c: float = Field(..., ge=-30, le=60)

yield_model = joblib.load(MODEL_PATH)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to AgriTwin AI",
        "status": "success"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "AgriTwin AI Backend",
        "database": "connected"
    }


# ============================================================
# FARM APIs
# ============================================================

# CREATE FARM
@app.post("/farms", response_model=FarmResponse)
def create_farm(
    farm: FarmCreate,
    db: Session = Depends(get_db)
):
    new_farm = Farm(
        farm_name=farm.farm_name,
        farm_size_acres=farm.farm_size_acres,
        state=farm.state,
        district=farm.district,
        latitude=farm.latitude,
        longitude=farm.longitude
    )

    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)

    return new_farm


# GET ALL FARMS
@app.get("/farms", response_model=list[FarmResponse])
def get_farms(db: Session = Depends(get_db)):
    farms = db.query(Farm).all()
    return farms


# GET FARM BY ID
@app.get("/farms/{farm_id}", response_model=FarmResponse)
def get_farm(
    farm_id: int,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    return farm


# UPDATE FARM
@app.put("/farms/{farm_id}", response_model=FarmResponse)
def update_farm(
    farm_id: int,
    farm_data: FarmCreate,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    farm.farm_name = farm_data.farm_name
    farm.farm_size_acres = farm_data.farm_size_acres
    farm.state = farm_data.state
    farm.district = farm_data.district
    farm.latitude = farm_data.latitude
    farm.longitude = farm_data.longitude

    db.commit()
    db.refresh(farm)

    return farm


# DELETE FARM
@app.delete("/farms/{farm_id}")
def delete_farm(
    farm_id: int,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    db.delete(farm)
    db.commit()

    return {
        "message": "Farm deleted successfully",
        "farm_id": farm_id
    }


# ============================================================
# SOIL PROFILE APIs
# ============================================================

# CREATE SOIL PROFILE
@app.post(
    "/farms/{farm_id}/soil",
    response_model=SoilProfileResponse
)
def create_soil_profile(
    farm_id: int,
    soil: SoilProfileCreate,
    db: Session = Depends(get_db)
):
    # Check whether farm exists
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    # A farm can have only one soil profile
    existing_soil = (
        db.query(SoilProfile)
        .filter(SoilProfile.farm_id == farm_id)
        .first()
    )

    if existing_soil is not None:
        raise HTTPException(
            status_code=409,
            detail="Soil profile already exists for this farm"
        )

    new_soil = SoilProfile(
        farm_id=farm_id,
        soil_type=soil.soil_type,
        ph=soil.ph,
        nitrogen=soil.nitrogen,
        phosphorus=soil.phosphorus,
        potassium=soil.potassium,
        organic_matter=soil.organic_matter
    )

    db.add(new_soil)
    db.commit()
    db.refresh(new_soil)

    return new_soil


# GET SOIL PROFILE
@app.get(
    "/farms/{farm_id}/soil",
    response_model=SoilProfileResponse
)
def get_soil_profile(
    farm_id: int,
    db: Session = Depends(get_db)
):
    # Check farm
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    soil = (
        db.query(SoilProfile)
        .filter(SoilProfile.farm_id == farm_id)
        .first()
    )

    if soil is None:
        raise HTTPException(
            status_code=404,
            detail="Soil profile not found"
        )

    return soil


# UPDATE SOIL PROFILE
@app.put(
    "/farms/{farm_id}/soil",
    response_model=SoilProfileResponse
)
def update_soil_profile(
    farm_id: int,
    soil_data: SoilProfileCreate,
    db: Session = Depends(get_db)
):
    soil = (
        db.query(SoilProfile)
        .filter(SoilProfile.farm_id == farm_id)
        .first()
    )

    if soil is None:
        raise HTTPException(
            status_code=404,
            detail="Soil profile not found"
        )

    soil.soil_type = soil_data.soil_type
    soil.ph = soil_data.ph
    soil.nitrogen = soil_data.nitrogen
    soil.phosphorus = soil_data.phosphorus
    soil.potassium = soil_data.potassium
    soil.organic_matter = soil_data.organic_matter

    db.commit()
    db.refresh(soil)

    return soil
# ============================================================
# CROP PROFILE APIs
# ============================================================

@app.post(
    "/farms/{farm_id}/crop",
    response_model=CropProfileResponse
)
def create_crop_profile(
    farm_id: int,
    crop: CropProfileCreate,
    db: Session = Depends(get_db)
):
    # Check whether farm exists
    farm = (
        db.query(Farm)
        .filter(Farm.id == farm_id)
        .first()
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    # Check whether crop profile already exists
    existing_crop = (
        db.query(CropProfile)
        .filter(CropProfile.farm_id == farm_id)
        .first()
    )

    if existing_crop is not None:
        raise HTTPException(
            status_code=409,
            detail="Crop profile already exists for this farm"
        )

    # Create crop profile
    new_crop = CropProfile(
        farm_id=farm_id,
        crop_name=crop.crop_name,
        previous_crop=crop.previous_crop,
        sowing_date=crop.sowing_date,
        farming_method=crop.farming_method
    )

    db.add(new_crop)
    db.commit()
    db.refresh(new_crop)

    return new_crop


@app.get(
    "/farms/{farm_id}/crop",
    response_model=CropProfileResponse
)
def get_crop_profile(
    farm_id: int,
    db: Session = Depends(get_db)
):
    # Check whether farm exists
    farm = (
        db.query(Farm)
        .filter(Farm.id == farm_id)
        .first()
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    # Get crop profile
    crop = (
        db.query(CropProfile)
        .filter(CropProfile.farm_id == farm_id)
        .first()
    )

    if crop is None:
        raise HTTPException(
            status_code=404,
            detail="Crop profile not found"
        )

    return crop


@app.put(
    "/farms/{farm_id}/crop",
    response_model=CropProfileResponse
)
def update_crop_profile(
    farm_id: int,
    crop_data: CropProfileCreate,
    db: Session = Depends(get_db)
):
    # Get crop profile
    crop = (
        db.query(CropProfile)
        .filter(CropProfile.farm_id == farm_id)
        .first()
    )

    if crop is None:
        raise HTTPException(
            status_code=404,
            detail="Crop profile not found"
        )

    # Update fields
    crop.crop_name = crop_data.crop_name
    crop.previous_crop = crop_data.previous_crop
    crop.sowing_date = crop_data.sowing_date
    crop.farming_method = crop_data.farming_method

    db.commit()
    db.refresh(crop)

    return crop
# ============================================================
# WATER PROFILE APIs
# ============================================================

@app.post(
    "/farms/{farm_id}/water",
    response_model=WaterProfileResponse
)
def create_water_profile(
    farm_id: int,
    water: WaterProfileCreate,
    db: Session = Depends(get_db)
):
    # Check whether farm exists
    farm = (
        db.query(Farm)
        .filter(Farm.id == farm_id)
        .first()
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    # Check whether water profile already exists
    existing_water = (
        db.query(WaterProfile)
        .filter(WaterProfile.farm_id == farm_id)
        .first()
    )

    if existing_water is not None:
        raise HTTPException(
            status_code=409,
            detail="Water profile already exists for this farm"
        )

    # Create water profile
    new_water = WaterProfile(
        farm_id=farm_id,
        availability=water.availability,
        irrigation_type=water.irrigation_type,
        available_water_liters=water.available_water_liters
    )

    db.add(new_water)
    db.commit()
    db.refresh(new_water)

    return new_water


@app.get(
    "/farms/{farm_id}/water",
    response_model=WaterProfileResponse
)
def get_water_profile(
    farm_id: int,
    db: Session = Depends(get_db)
):
    # Check whether farm exists
    farm = (
        db.query(Farm)
        .filter(Farm.id == farm_id)
        .first()
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    # Get water profile
    water = (
        db.query(WaterProfile)
        .filter(WaterProfile.farm_id == farm_id)
        .first()
    )

    if water is None:
        raise HTTPException(
            status_code=404,
            detail="Water profile not found"
        )

    return water


@app.put(
    "/farms/{farm_id}/water",
    response_model=WaterProfileResponse
)
def update_water_profile(
    farm_id: int,
    water_data: WaterProfileCreate,
    db: Session = Depends(get_db)
):
    # Get water profile
    water = (
        db.query(WaterProfile)
        .filter(WaterProfile.farm_id == farm_id)
        .first()
    )

    if water is None:
        raise HTTPException(
            status_code=404,
            detail="Water profile not found"
        )

    # Update fields
    water.availability = water_data.availability
    water.irrigation_type = water_data.irrigation_type
    water.available_water_liters = water_data.available_water_liters

    db.commit()
    db.refresh(water)

    return water
# ============================================================
# WEATHER APIs
# ============================================================

@app.post(
    "/farms/{farm_id}/weather",
    response_model=WeatherRecordResponse
)
def create_weather_record(
    farm_id: int,
    weather: WeatherRecordCreate,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    new_weather = WeatherRecord(
        farm_id=farm_id,
        date=weather.date,
        temperature=weather.temperature,
        rainfall=weather.rainfall,
        humidity=weather.humidity,
        wind_speed=weather.wind_speed
    )

    db.add(new_weather)
    db.commit()
    db.refresh(new_weather)

    return new_weather


@app.get(
    "/farms/{farm_id}/weather",
    response_model=list[WeatherRecordResponse]
)
def get_weather_records(
    farm_id: int,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    weather_records = (
        db.query(WeatherRecord)
        .filter(WeatherRecord.farm_id == farm_id)
        .order_by(WeatherRecord.date)
        .all()
    )

    return weather_records


@app.delete("/weather/{weather_id}")
def delete_weather_record(
    weather_id: int,
    db: Session = Depends(get_db)
):
    weather = (
        db.query(WeatherRecord)
        .filter(WeatherRecord.id == weather_id)
        .first()
    )

    if weather is None:
        raise HTTPException(
            status_code=404,
            detail="Weather record not found"
        )

    db.delete(weather)
    db.commit()

    return {
        "message": "Weather record deleted successfully",
        "weather_id": weather_id
    }
# ============================================================
# PREDICTION APIs
# ============================================================

@app.post(
    "/farms/{farm_id}/predictions",
    response_model=PredictionResponse
)
def create_prediction(
    farm_id: int,
    prediction: PredictionCreate,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    new_prediction = Prediction(
        farm_id=farm_id,
        predicted_yield=prediction.predicted_yield,
        water_requirement=prediction.water_requirement,
        disease_risk=prediction.disease_risk,
        climate_risk=prediction.climate_risk,
        crop_stress=prediction.crop_stress,
        confidence=prediction.confidence
    )

    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    return new_prediction


@app.get(
    "/farms/{farm_id}/predictions",
    response_model=list[PredictionResponse]
)
def get_predictions(
    farm_id: int,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    predictions = (
        db.query(Prediction)
        .filter(Prediction.farm_id == farm_id)
        .order_by(Prediction.created_at.desc())
        .all()
    )

    return predictions
# ============================================================
# SIMULATION APIs
# ============================================================

@app.post(
    "/farms/{farm_id}/simulations",
    response_model=SimulationResponse
)
def create_simulation(
    farm_id: int,
    simulation: SimulationCreate,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    new_simulation = Simulation(
        farm_id=farm_id,
        scenario_name=simulation.scenario_name,
        crop=simulation.crop,
        irrigation_level=simulation.irrigation_level,
        fertilizer_level=simulation.fertilizer_level,
        rainfall_change=simulation.rainfall_change,
        temperature_change=simulation.temperature_change,
        predicted_yield=simulation.predicted_yield,
        estimated_profit=simulation.estimated_profit,
        water_used=simulation.water_used,
        sustainability_score=simulation.sustainability_score
    )

    db.add(new_simulation)
    db.commit()
    db.refresh(new_simulation)

    return new_simulation


@app.get(
    "/farms/{farm_id}/simulations",
    response_model=list[SimulationResponse]
)
def get_simulations(
    farm_id: int,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    simulations = (
        db.query(Simulation)
        .filter(Simulation.farm_id == farm_id)
        .order_by(Simulation.created_at.desc())
        .all()
    )

    return simulations
# ============================================================
# RECOMMENDATION APIs
# ============================================================

@app.post(
    "/farms/{farm_id}/recommendations",
    response_model=RecommendationResponse
)
def create_recommendation(
    farm_id: int,
    recommendation: RecommendationCreate,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    new_recommendation = Recommendation(
        farm_id=farm_id,
        recommendation_type=recommendation.recommendation_type,
        recommendation=recommendation.recommendation,
        reason=recommendation.reason,
        expected_impact=recommendation.expected_impact,
        confidence=recommendation.confidence
    )

    db.add(new_recommendation)
    db.commit()
    db.refresh(new_recommendation)

    return new_recommendation


@app.get(
    "/farms/{farm_id}/recommendations",
    response_model=list[RecommendationResponse]
)
def get_recommendations(
    farm_id: int,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    recommendations = (
        db.query(Recommendation)
        .filter(Recommendation.farm_id == farm_id)
        .order_by(Recommendation.created_at.desc())
        .all()
    )

    return recommendations
# ============================================================
# DECISION FEEDBACK APIs
# ============================================================

@app.post(
    "/farms/{farm_id}/feedback",
    response_model=DecisionFeedbackResponse
)
def create_decision_feedback(
    farm_id: int,
    feedback: DecisionFeedbackCreate,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    if feedback.recommendation_id is not None:
        recommendation = (
            db.query(Recommendation)
            .filter(
                Recommendation.id == feedback.recommendation_id,
                Recommendation.farm_id == farm_id
            )
            .first()
        )

        if recommendation is None:
            raise HTTPException(
                status_code=404,
                detail="Recommendation not found for this farm"
            )

    new_feedback = DecisionFeedback(
        farm_id=farm_id,
        recommendation_id=feedback.recommendation_id,
        decision_taken=feedback.decision_taken,
        actual_yield=feedback.actual_yield,
        actual_water_used=feedback.actual_water_used,
        actual_profit=feedback.actual_profit,
        notes=feedback.notes
    )

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    return new_feedback


@app.get(
    "/farms/{farm_id}/feedback",
    response_model=list[DecisionFeedbackResponse]
)
def get_decision_feedback(
    farm_id: int,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    feedback = (
        db.query(DecisionFeedback)
        .filter(DecisionFeedback.farm_id == farm_id)
        .order_by(DecisionFeedback.created_at.desc())
        .all()
    )

    return feedback
@app.post("/predict-yield")
def predict_yield(data: YieldPredictionRequest):

    input_data = pd.DataFrame([
        {
            "district_code": data.district_code,
            "state_code": data.state_code,
            "year": data.year,
            "crop": data.crop,
            "district": data.district,
            "state_name": data.state_name,
            "area_1000_ha": data.area_1000_ha,
            "rainfall_mm": data.rainfall_mm,
            "avg_temp_c": data.avg_temp_c,
            "max_temp_c": data.max_temp_c,
            "min_temp_c": data.min_temp_c
        }
    ])

    prediction = yield_model.predict(input_data)[0]

    prediction = max(0, float(prediction))

    return {
        "predicted_yield_kg_per_ha": round(prediction, 2),
        "model_r2": 0.8066,
        "confidence": 80.66
    }
# ============================================================
# WATER OPTIMIZATION API
# ============================================================

class WaterOptimizationRequest(BaseModel):
    farm_size_acres: float
    crop: str
    rainfall_mm: float
    avg_temp_c: float
    available_water_liters: float
    irrigation_type: str


@app.post("/optimize-water")
def optimize_water(data: WaterOptimizationRequest):

    result = calculate_water_optimization(
        farm_size_acres=data.farm_size_acres,
        crop=data.crop,
        rainfall_mm=data.rainfall_mm,
        avg_temp_c=data.avg_temp_c,
        available_water_liters=data.available_water_liters,
        irrigation_type=data.irrigation_type
    )

    return result
# ============================================================
# FERTILIZER OPTIMIZATION API
# ============================================================

class FertilizerOptimizationRequest(BaseModel):
    farm_size_acres: float
    crop: str
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    organic_matter: float


@app.post("/optimize-fertilizer")
def optimize_fertilizer(
    data: FertilizerOptimizationRequest
):

    result = calculate_fertilizer_optimization(
        farm_size_acres=data.farm_size_acres,
        crop=data.crop,
        nitrogen=data.nitrogen,
        phosphorus=data.phosphorus,
        potassium=data.potassium,
        ph=data.ph,
        organic_matter=data.organic_matter
    )

    return result
# ============================================================
# CROP SELECTION & ROTATION API
# ============================================================

class CropSelectionRequest(BaseModel):
    available_water_liters: float
    farm_size_acres: float
    previous_crop: str
    nitrogen: float
    phosphorus: float
    potassium: float
    avg_temp_c: float
    top_n: int = 5


@app.post("/select-crops")
def select_crops(data: CropSelectionRequest):

    results = select_best_crops(
        available_water_liters=data.available_water_liters,
        farm_size_acres=data.farm_size_acres,
        previous_crop=data.previous_crop,
        nitrogen=data.nitrogen,
        phosphorus=data.phosphorus,
        potassium=data.potassium,
        avg_temp_c=data.avg_temp_c,
        top_n=data.top_n
    )

    return {
        "recommended_crops": results
    }


# ============================================================
# PROFIT OPTIMIZATION API
# ============================================================

class ProfitOptimizationRequest(BaseModel):
    crop: str
    farm_size_acres: float
    predicted_yield_kg_per_ha: float


@app.post("/optimize-profit")
def optimize_profit(data: ProfitOptimizationRequest):

    return calculate_profit(
        crop=data.crop,
        farm_size_acres=data.farm_size_acres,
        predicted_yield_kg_per_ha=data.predicted_yield_kg_per_ha
    )


# ============================================================
# PROFIT COMPARISON API
# ============================================================

class CropProfitComparisonRequest(BaseModel):
    farm_size_acres: float
    crop_predictions: dict[str, float]


@app.post("/compare-crop-profits")
def compare_crop_profits(
    data: CropProfitComparisonRequest
):

    results = compare_crop_profitability(
        farm_size_acres=data.farm_size_acres,
        crop_predictions=data.crop_predictions
    )

    return {
        "crop_profitability": results
    }


# ============================================================
# SUSTAINABILITY API
# ============================================================

class SustainabilityRequest(BaseModel):
    water_coverage_percent: float
    fertilizer_priority: str
    organic_matter_status: str
    irrigation_type: str
    crop_rotation_score: float
    estimated_profit_per_acre: float


@app.post("/sustainability-score")
def sustainability_score(
    data: SustainabilityRequest
):

    return calculate_sustainability_score(
        water_coverage_percent=data.water_coverage_percent,
        fertilizer_priority=data.fertilizer_priority,
        organic_matter_status=data.organic_matter_status,
        irrigation_type=data.irrigation_type,
        crop_rotation_score=data.crop_rotation_score,
        estimated_profit_per_acre=data.estimated_profit_per_acre
    )


# ============================================================
# COMBINED FARMING DECISION API
# ============================================================

class FarmingDecisionRequest(BaseModel):
    farm_size_acres: float
    previous_crop: str

    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    organic_matter: float

    available_water_liters: float
    irrigation_type: str

    rainfall_mm: float
    avg_temp_c: float

    predicted_yield_kg_per_ha: float


@app.post("/farming-decision")
def farming_decision(
    data: FarmingDecisionRequest
):

    # --------------------------------------------------------
    # 1. Crop selection
    # --------------------------------------------------------

    crop_results = select_best_crops(
        available_water_liters=data.available_water_liters,
        farm_size_acres=data.farm_size_acres,
        previous_crop=data.previous_crop,
        nitrogen=data.nitrogen,
        phosphorus=data.phosphorus,
        potassium=data.potassium,
        avg_temp_c=data.avg_temp_c,
        top_n=5
    )

    # Best recommended crop
    best_crop = crop_results[0]

    # --------------------------------------------------------
    # 2. Profit calculation for recommended crop
    # --------------------------------------------------------

    profit_result = calculate_profit(
        crop=best_crop["crop"],
        farm_size_acres=data.farm_size_acres,
        predicted_yield_kg_per_ha=data.predicted_yield_kg_per_ha
    )

    # --------------------------------------------------------
    # 3. Fertilizer priority logic
    # --------------------------------------------------------

    nitrogen_ratio = (
        data.nitrogen / 120
    )

    phosphorus_ratio = (
        data.phosphorus / 60
    )

    potassium_ratio = (
        data.potassium / 40
    )

    nutrient_ratios = {
        "Nitrogen": nitrogen_ratio,
        "Phosphorus": phosphorus_ratio,
        "Potassium": potassium_ratio
    }

    lowest_nutrient = min(
        nutrient_ratios,
        key=nutrient_ratios.get
    )

    lowest_ratio = nutrient_ratios[
        lowest_nutrient
    ]

    if lowest_ratio < 0.40:
        fertilizer_priority = "High"

    elif lowest_ratio < 0.90:
        fertilizer_priority = "Moderate"

    else:
        fertilizer_priority = "Low"

    # --------------------------------------------------------
    # 4. Soil health
    # --------------------------------------------------------

    if data.organic_matter >= 2:
        organic_matter_status = "Good"

    elif data.organic_matter >= 1:
        organic_matter_status = "Moderate"

    else:
        organic_matter_status = "Low"

    # --------------------------------------------------------
    # 5. Water coverage
    # --------------------------------------------------------

    # Simple planning estimate.
    estimated_water_need = (
        data.farm_size_acres
        * 9800
    )

    if estimated_water_need <= 0:
        water_coverage = 100.0

    else:
        water_coverage = min(
            100.0,
            (
                data.available_water_liters
                / estimated_water_need
            ) * 100
        )

    # --------------------------------------------------------
    # 6. Sustainability
    # --------------------------------------------------------

    sustainability = calculate_sustainability_score(
        water_coverage_percent=water_coverage,
        fertilizer_priority=fertilizer_priority,
        organic_matter_status=organic_matter_status,
        irrigation_type=data.irrigation_type,
        crop_rotation_score=best_crop["rotation_fit"],
        estimated_profit_per_acre=profit_result[
            "estimated_profit_per_acre"
        ]
    )

    # --------------------------------------------------------
    # 7. Final recommendation
    # --------------------------------------------------------

    recommendation = (
        f"Prefer {best_crop['crop']} for the next cycle. "
        f"It achieved a crop suitability score of "
        f"{best_crop['score']}%. "
        f"Estimated profit is "
        f"₹{profit_result['estimated_profit']:.2f} "
        f"for the farm. "
        f"Fertilizer priority is "
        f"{fertilizer_priority}. "
        f"Sustainability score is "
        f"{sustainability['sustainability_score']}."
    )

    return {
        "recommended_crop": best_crop,
        "alternative_crops": crop_results[1:],
        "profit_analysis": profit_result,
        "fertilizer_priority": fertilizer_priority,
        "sustainability": sustainability,
        "final_recommendation": recommendation
    }
# ============================================================
# CLIMATE RISK API
# ============================================================

class ClimateRiskRequest(BaseModel):
    crop: str
    avg_temp_c: float
    rainfall_mm: float
    temperature_change: float = 0.0
    rainfall_change_percent: float = 0.0


@app.post("/climate-risk")
def climate_risk(
    data: ClimateRiskRequest
):

    return calculate_climate_risk(
        crop=data.crop,
        avg_temp_c=data.avg_temp_c,
        rainfall_mm=data.rainfall_mm,
        temperature_change=data.temperature_change,
        rainfall_change_percent=data.rainfall_change_percent
    )


# ============================================================
# EARLY WARNING API
# ============================================================

class EarlyWarningRequest(BaseModel):
    crop: str
    avg_temp_c: float
    rainfall_mm: float
    available_water_liters: float
    farm_size_acres: float
    nitrogen: float
    phosphorus: float
    potassium: float


@app.post("/early-warning")
def early_warning(
    data: EarlyWarningRequest
):

    return generate_early_warnings(
        crop=data.crop,
        avg_temp_c=data.avg_temp_c,
        rainfall_mm=data.rainfall_mm,
        available_water_liters=data.available_water_liters,
        farm_size_acres=data.farm_size_acres,
        nitrogen=data.nitrogen,
        phosphorus=data.phosphorus,
        potassium=data.potassium
    )


# ============================================================
# WHAT-IF DIGITAL FARM API
# ============================================================

class WhatIfRequest(BaseModel):
    crop: str
    farm_size_acres: float
    baseline_yield_kg_per_ha: float
    baseline_profit: float
    baseline_water_liters: float
    baseline_sustainability_score: float
    avg_temp_c: float
    rainfall_mm: float

    temperature_change: float = 0.0
    rainfall_change_percent: float = 0.0
    irrigation_change_percent: float = 0.0
    fertilizer_change_percent: float = 0.0


@app.post("/what-if")
def what_if(
    data: WhatIfRequest
):

    return simulate_farm_scenario(
        crop=data.crop,
        farm_size_acres=data.farm_size_acres,
        baseline_yield_kg_per_ha=data.baseline_yield_kg_per_ha,
        baseline_profit=data.baseline_profit,
        baseline_water_liters=data.baseline_water_liters,
        baseline_sustainability_score=data.baseline_sustainability_score,
        avg_temp_c=data.avg_temp_c,
        rainfall_mm=data.rainfall_mm,
        temperature_change=data.temperature_change,
        rainfall_change_percent=data.rainfall_change_percent,
        irrigation_change_percent=data.irrigation_change_percent,
        fertilizer_change_percent=data.fertilizer_change_percent
    )


# ============================================================
# CROP CALENDAR API
# ============================================================

class CropCalendarRequest(BaseModel):
    crop: str


@app.post("/crop-calendar")
def crop_calendar(
    data: CropCalendarRequest
):

    return get_crop_calendar(
        crop=data.crop
    )
# ============================================================
# EXPLAINABLE AI API
# ============================================================

class ExplainDecisionRequest(BaseModel):
    crop: str
    crop_score: float
    water_fit: float
    nutrient_fit: float
    rotation_fit: float
    temperature_fit: float
    fertilizer_priority: str
    water_coverage_percent: float
    sustainability_score: float
    climate_risk: float


@app.post("/explain-decision")
def explain_decision(
    data: ExplainDecisionRequest
):

    return explain_farming_decision(
        crop=data.crop,
        crop_score=data.crop_score,
        water_fit=data.water_fit,
        nutrient_fit=data.nutrient_fit,
        rotation_fit=data.rotation_fit,
        temperature_fit=data.temperature_fit,
        fertilizer_priority=data.fertilizer_priority,
        water_coverage_percent=data.water_coverage_percent,
        sustainability_score=data.sustainability_score,
        climate_risk=data.climate_risk
    )


# ============================================================
# AGRICULTURAL ADVISOR API
# ============================================================

class AgriculturalAdvisorRequest(BaseModel):
    crop: str
    predicted_yield_kg_per_ha: float
    water_coverage_percent: float
    fertilizer_priority: str
    sustainability_score: float
    climate_risk: float
    recommended_water_liters: float = 0.0


@app.post("/agricultural-advisor")
def agricultural_advisor(
    data: AgriculturalAdvisorRequest
):

    return generate_agricultural_advice(
        crop=data.crop,
        predicted_yield_kg_per_ha=data.predicted_yield_kg_per_ha,
        water_coverage_percent=data.water_coverage_percent,
        fertilizer_priority=data.fertilizer_priority,
        sustainability_score=data.sustainability_score,
        climate_risk=data.climate_risk,
        recommended_water_liters=data.recommended_water_liters
    )


# ============================================================
# DECISION REPLAY API
# ============================================================

class DecisionReplayRequest(BaseModel):
    recommendation_id: int
    decision_taken: str

    predicted_yield: float | None = None
    actual_yield: float | None = None

    predicted_water: float | None = None
    actual_water: float | None = None

    predicted_profit: float | None = None
    actual_profit: float | None = None

    notes: str | None = None


@app.post("/decision-replay")
def decision_replay(
    data: DecisionReplayRequest
):

    return build_decision_replay(
        recommendation_id=data.recommendation_id,
        decision_taken=data.decision_taken,
        predicted_yield=data.predicted_yield,
        actual_yield=data.actual_yield,
        predicted_water=data.predicted_water,
        actual_water=data.actual_water,
        predicted_profit=data.predicted_profit,
        actual_profit=data.actual_profit,
        notes=data.notes
    )

# ============================================================
# INTEGRATED AGRITWIN DECISION PIPELINE API
# ============================================================

class DecisionPipelineRequest(BaseModel):
    district_code: int = Field(..., ge=1)
    state_code: int = Field(..., ge=1)
    year: int = Field(..., ge=1900, le=2100)

    district: str = Field(..., min_length=2, max_length=100)
    state_name: str = Field(..., min_length=2, max_length=100)
    area_1000_ha: float = Field(..., gt=0)

    farm_size_acres: float = Field(..., gt=0)
    previous_crop: str = Field(..., min_length=2, max_length=100)

    nitrogen: float = Field(..., ge=0)
    phosphorus: float = Field(..., ge=0)
    potassium: float = Field(..., ge=0)

    ph: float = Field(..., ge=0, le=14)
    organic_matter: float = Field(..., ge=0)

    available_water_liters: float = Field(..., ge=0)
    irrigation_type: str = Field(..., min_length=2, max_length=100)

    rainfall_mm: float = Field(..., ge=0)
    avg_temp_c: float = Field(..., ge=-20, le=60)
    max_temp_c: float = Field(..., ge=-20, le=70)
    min_temp_c: float = Field(..., ge=-30, le=60)


@app.post("/decision-pipeline")
def decision_pipeline(
    data: DecisionPipelineRequest
):

    return run_decision_pipeline(
        district_code=data.district_code,
        state_code=data.state_code,
        year=data.year,
        district=data.district,
        state_name=data.state_name,
        area_1000_ha=data.area_1000_ha,

        farm_size_acres=data.farm_size_acres,
        previous_crop=data.previous_crop,

        nitrogen=data.nitrogen,
        phosphorus=data.phosphorus,
        potassium=data.potassium,
        ph=data.ph,
        organic_matter=data.organic_matter,

        available_water_liters=data.available_water_liters,
        irrigation_type=data.irrigation_type,

        rainfall_mm=data.rainfall_mm,
        avg_temp_c=data.avg_temp_c,
        max_temp_c=data.max_temp_c,
        min_temp_c=data.min_temp_c
    )