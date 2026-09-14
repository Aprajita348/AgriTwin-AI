from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# FARM SCHEMAS
# ============================================================

class FarmCreate(BaseModel):
    farm_name: str = Field(..., min_length=2, max_length=100)
    farm_size_acres: float = Field(..., gt=0)

    state: str = Field(..., min_length=2, max_length=100)
    district: str = Field(..., min_length=2, max_length=100)

    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)


class FarmResponse(FarmCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# SOIL PROFILE SCHEMAS
# ============================================================

class SoilProfileCreate(BaseModel):
    soil_type: str = Field(..., min_length=2, max_length=100)

    ph: Optional[float] = Field(
        default=None,
        ge=0,
        le=14
    )

    nitrogen: Optional[float] = Field(
        default=None,
        ge=0
    )

    phosphorus: Optional[float] = Field(
        default=None,
        ge=0
    )

    potassium: Optional[float] = Field(
        default=None,
        ge=0
    )

    organic_matter: Optional[float] = Field(
        default=None,
        ge=0
    )


class SoilProfileResponse(SoilProfileCreate):
    id: int
    farm_id: int

    model_config = ConfigDict(from_attributes=True)
    # ============================================================
# CROP PROFILE SCHEMAS
# ============================================================

from datetime import date


class CropProfileCreate(BaseModel):
    crop_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    previous_crop: Optional[str] = Field(
        default=None,
        max_length=100
    )

    sowing_date: Optional[date] = None

    farming_method: Optional[str] = Field(
        default=None,
        max_length=100
    )


class CropProfileResponse(CropProfileCreate):
    id: int
    farm_id: int

    model_config = ConfigDict(from_attributes=True)
    # ============================================================
# WATER PROFILE SCHEMAS
# ============================================================

class WaterProfileCreate(BaseModel):
    availability: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    irrigation_type: Optional[str] = Field(
        default=None,
        max_length=100
    )

    available_water_liters: Optional[float] = Field(
        default=None,
        ge=0
    )


class WaterProfileResponse(WaterProfileCreate):
    id: int
    farm_id: int

    model_config = ConfigDict(from_attributes=True)
    # ============================================================
# WEATHER RECORD SCHEMAS
# ============================================================

class WeatherRecordCreate(BaseModel):
    date: date

    temperature: Optional[float] = None

    rainfall: Optional[float] = Field(
        default=None,
        ge=0
    )

    humidity: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )

    wind_speed: Optional[float] = Field(
        default=None,
        ge=0
    )


class WeatherRecordResponse(WeatherRecordCreate):
    id: int
    farm_id: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# PREDICTION SCHEMAS
# ============================================================

class PredictionCreate(BaseModel):
    predicted_yield: Optional[float] = Field(
        default=None,
        ge=0
    )

    water_requirement: Optional[float] = Field(
        default=None,
        ge=0
    )

    disease_risk: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )

    climate_risk: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )

    crop_stress: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )

    confidence: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )


class PredictionResponse(PredictionCreate):
    id: int
    farm_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# SIMULATION SCHEMAS
# ============================================================

class SimulationCreate(BaseModel):
    scenario_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    crop: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    irrigation_level: Optional[float] = Field(
        default=None,
        ge=0
    )

    fertilizer_level: Optional[float] = Field(
        default=None,
        ge=0
    )

    rainfall_change: Optional[float] = None

    temperature_change: Optional[float] = None

    predicted_yield: Optional[float] = Field(
        default=None,
        ge=0
    )

    estimated_profit: Optional[float] = None

    water_used: Optional[float] = Field(
        default=None,
        ge=0
    )

    sustainability_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )


class SimulationResponse(SimulationCreate):
    id: int
    farm_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# RECOMMENDATION SCHEMAS
# ============================================================

class RecommendationCreate(BaseModel):
    recommendation_type: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    recommendation: str = Field(
        ...,
        min_length=2
    )

    reason: Optional[str] = None

    expected_impact: Optional[str] = None

    confidence: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )


class RecommendationResponse(RecommendationCreate):
    id: int
    farm_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# DECISION FEEDBACK SCHEMAS
# ============================================================

class DecisionFeedbackCreate(BaseModel):
    recommendation_id: Optional[int] = None

    decision_taken: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    actual_yield: Optional[float] = Field(
        default=None,
        ge=0
    )

    actual_water_used: Optional[float] = Field(
        default=None,
        ge=0
    )

    actual_profit: Optional[float] = None

    notes: Optional[str] = None


class DecisionFeedbackResponse(DecisionFeedbackCreate):
    id: int
    farm_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)