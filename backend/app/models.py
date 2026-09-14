from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


# ============================================================
# 1. FARM
# ============================================================

class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    farm_name = Column(String(100), nullable=False)
    farm_size_acres = Column(Float, nullable=False)

    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    soil_profile = relationship(
        "SoilProfile",
        back_populates="farm",
        uselist=False,
        cascade="all, delete-orphan"
    )

    crop_profile = relationship(
        "CropProfile",
        back_populates="farm",
        uselist=False,
        cascade="all, delete-orphan"
    )

    water_profile = relationship(
        "WaterProfile",
        back_populates="farm",
        uselist=False,
        cascade="all, delete-orphan"
    )

    weather_records = relationship(
        "WeatherRecord",
        back_populates="farm",
        cascade="all, delete-orphan"
    )

    predictions = relationship(
        "Prediction",
        back_populates="farm",
        cascade="all, delete-orphan"
    )

    simulations = relationship(
        "Simulation",
        back_populates="farm",
        cascade="all, delete-orphan"
    )

    recommendations = relationship(
        "Recommendation",
        back_populates="farm",
        cascade="all, delete-orphan"
    )

    decision_feedback = relationship(
        "DecisionFeedback",
        back_populates="farm",
        cascade="all, delete-orphan"
    )


# ============================================================
# 2. SOIL PROFILE
# ============================================================

class SoilProfile(Base):
    __tablename__ = "soil_profiles"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, unique=True)

    soil_type = Column(String(100), nullable=False)
    ph = Column(Float, nullable=True)

    nitrogen = Column(Float, nullable=True)
    phosphorus = Column(Float, nullable=True)
    potassium = Column(Float, nullable=True)

    organic_matter = Column(Float, nullable=True)

    farm = relationship("Farm", back_populates="soil_profile")


# ============================================================
# 3. CROP PROFILE
# ============================================================

class CropProfile(Base):
    __tablename__ = "crop_profiles"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, unique=True)

    crop_name = Column(String(100), nullable=False)
    previous_crop = Column(String(100), nullable=True)

    sowing_date = Column(Date, nullable=True)
    farming_method = Column(String(100), nullable=True)

    farm = relationship("Farm", back_populates="crop_profile")


# ============================================================
# 4. WATER PROFILE
# ============================================================

class WaterProfile(Base):
    __tablename__ = "water_profiles"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, unique=True)

    availability = Column(String(50), nullable=False)
    irrigation_type = Column(String(100), nullable=True)

    available_water_liters = Column(Float, nullable=True)

    farm = relationship("Farm", back_populates="water_profile")


# ============================================================
# 5. WEATHER RECORD
# ============================================================

class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)

    date = Column(Date, nullable=False)

    temperature = Column(Float, nullable=True)
    rainfall = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)

    farm = relationship("Farm", back_populates="weather_records")


# ============================================================
# 6. PREDICTION
# ============================================================

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)

    predicted_yield = Column(Float, nullable=True)
    water_requirement = Column(Float, nullable=True)

    disease_risk = Column(Float, nullable=True)
    climate_risk = Column(Float, nullable=True)
    crop_stress = Column(Float, nullable=True)

    confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="predictions")


# ============================================================
# 7. SIMULATION
# ============================================================

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)

    scenario_name = Column(String(100), nullable=False)
    crop = Column(String(100), nullable=False)

    irrigation_level = Column(Float, nullable=True)
    fertilizer_level = Column(Float, nullable=True)

    rainfall_change = Column(Float, nullable=True)
    temperature_change = Column(Float, nullable=True)

    predicted_yield = Column(Float, nullable=True)
    estimated_profit = Column(Float, nullable=True)

    water_used = Column(Float, nullable=True)
    sustainability_score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="simulations")


# ============================================================
# 8. RECOMMENDATION
# ============================================================

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)

    recommendation_type = Column(String(100), nullable=False)

    recommendation = Column(Text, nullable=False)
    reason = Column(Text, nullable=True)
    expected_impact = Column(Text, nullable=True)

    confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="recommendations")


# ============================================================
# 9. DECISION FEEDBACK
# ============================================================

class DecisionFeedback(Base):
    __tablename__ = "decision_feedback"

    id = Column(Integer, primary_key=True, index=True)

    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    recommendation_id = Column(
        Integer,
        ForeignKey("recommendations.id"),
        nullable=True
    )

    decision_taken = Column(String(100), nullable=False)

    actual_yield = Column(Float, nullable=True)
    actual_water_used = Column(Float, nullable=True)
    actual_profit = Column(Float, nullable=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="decision_feedback")