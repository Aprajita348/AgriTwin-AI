# ============================================================
# AGRITWIN AI - WATER OPTIMIZATION ENGINE
# ============================================================

from typing import Dict


# Crop water-use coefficients for MVP decision logic.
# These are simplified planning coefficients, not field-calibrated values.
CROP_COEFFICIENTS: Dict[str, float] = {
    "RICE": 1.15,
    "WHEAT": 1.05,
    "MAIZE": 1.10,
    "BARLEY": 1.00,
    "CHICKPEA": 0.90,
    "PIGEONPEA": 0.90,
    "GROUNDNUT": 1.00,
    "COTTON": 1.10,
    "SUGARCANE": 1.20,
    "SOYABEAN": 1.05,
    "FINGER MILLET": 0.90,
    "PEARL MILLET": 0.85,
    "SORGHUM": 0.90,
    "RAPESEED AND MUSTARD": 0.90
}


# Irrigation efficiency used for estimating gross irrigation demand.
IRRIGATION_EFFICIENCY: Dict[str, float] = {
    "Drip": 0.90,
    "Sprinkler": 0.80,
    "Flood": 0.60
}


def calculate_water_optimization(
    farm_size_acres: float,
    crop: str,
    rainfall_mm: float,
    avg_temp_c: float,
    available_water_liters: float,
    irrigation_type: str
):
    """
    Estimate daily crop water demand and recommend an irrigation strategy.

    This is an MVP rule-based optimization engine.
    """

    crop = crop.upper().strip()

    if crop in CROP_COEFFICIENTS:
        crop_coefficient = CROP_COEFFICIENTS[crop]
    else:
        crop_coefficient = 1.00

    if irrigation_type not in IRRIGATION_EFFICIENCY:
        irrigation_type = "Flood"

    irrigation_efficiency = IRRIGATION_EFFICIENCY[irrigation_type]

    # Convert acres -> hectares
    farm_size_hectares = farm_size_acres * 0.404686

    # Temperature-based reference water demand proxy.
    # Higher temperatures increase crop water demand.
    base_et_mm = 4 + (0.15 * (avg_temp_c - 20))

    # Keep the estimate within a practical MVP range.
    base_et_mm = max(3.0, min(base_et_mm, 8.0))

    # Crop-adjusted evapotranspiration demand.
    crop_water_demand_mm = base_et_mm * crop_coefficient

    # Assume part of the rainfall contributes effectively to crop water needs.
    effective_rainfall_mm = rainfall_mm * 0.70

    # Net irrigation requirement after rainfall contribution.
    net_irrigation_mm = max(
        0.0,
        crop_water_demand_mm - effective_rainfall_mm
    )

    # Gross irrigation requirement considering irrigation efficiency.
    gross_irrigation_mm = (
        net_irrigation_mm / irrigation_efficiency
    )

    # 1 mm water over 1 hectare = 10,000 liters.
    daily_water_demand_liters = (
        gross_irrigation_mm
        * farm_size_hectares
        * 10000
    )

    # Water that can actually be supplied.
    recommended_water_liters = min(
        daily_water_demand_liters,
        available_water_liters
    )

    if daily_water_demand_liters == 0:
        water_coverage_percent = 100.0
    else:
        water_coverage_percent = (
            recommended_water_liters
            / daily_water_demand_liters
        ) * 100

    water_shortage_liters = max(
        0.0,
        daily_water_demand_liters - available_water_liters
    )

    # Decide strategy.
    if water_shortage_liters == 0:
        strategy = "Full irrigation requirement can be met."

    elif irrigation_type == "Drip":
        strategy = (
            "Use deficit irrigation with drip and prioritize "
            "critical crop growth periods."
        )

    else:
        strategy = (
            "Water is insufficient. Shift toward drip irrigation "
            "and prioritize critical crop growth periods."
        )

    if water_coverage_percent >= 90:
        risk_level = "Low"
    elif water_coverage_percent >= 70:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return {
        "crop": crop,
        "farm_size_hectares": round(farm_size_hectares, 2),
        "crop_coefficient": crop_coefficient,
        "base_et_mm": round(base_et_mm, 2),
        "effective_rainfall_mm": round(effective_rainfall_mm, 2),
        "net_irrigation_mm": round(net_irrigation_mm, 2),
        "gross_irrigation_mm": round(gross_irrigation_mm, 2),
        "daily_water_demand_liters": round(
            daily_water_demand_liters,
            2
        ),
        "available_water_liters": round(
            available_water_liters,
            2
        ),
        "recommended_water_liters": round(
            recommended_water_liters,
            2
        ),
        "water_shortage_liters": round(
            water_shortage_liters,
            2
        ),
        "water_coverage_percent": round(
            water_coverage_percent,
            2
        ),
        "irrigation_type": irrigation_type,
        "risk_level": risk_level,
        "strategy": strategy
    }