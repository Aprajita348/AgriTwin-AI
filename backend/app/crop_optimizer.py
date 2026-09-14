# ============================================================
# AGRITWIN AI - CROP SELECTION & ROTATION ENGINE
# ============================================================

from typing import Dict, List


# Approximate crop characteristics for MVP decision logic.
CROP_DATA: Dict[str, Dict[str, float]] = {
    "WHEAT": {
        "water_need": 0.65,
        "nitrogen_demand": 0.75,
        "profit_factor": 1.00,
        "rotation_value": 0.55,
        "heat_tolerance": 0.55
    },
    "RICE": {
        "water_need": 1.00,
        "nitrogen_demand": 0.75,
        "profit_factor": 0.95,
        "rotation_value": 0.35,
        "heat_tolerance": 0.70
    },
    "MAIZE": {
        "water_need": 0.70,
        "nitrogen_demand": 0.90,
        "profit_factor": 1.10,
        "rotation_value": 0.70,
        "heat_tolerance": 0.75
    },
    "CHICKPEA": {
        "water_need": 0.35,
        "nitrogen_demand": 0.35,
        "profit_factor": 0.90,
        "rotation_value": 0.95,
        "heat_tolerance": 0.80
    },
    "PIGEONPEA": {
        "water_need": 0.40,
        "nitrogen_demand": 0.40,
        "profit_factor": 0.92,
        "rotation_value": 0.90,
        "heat_tolerance": 0.90
    },
    "GROUNDNUT": {
        "water_need": 0.55,
        "nitrogen_demand": 0.40,
        "profit_factor": 1.05,
        "rotation_value": 0.80,
        "heat_tolerance": 0.85
    },
    "COTTON": {
        "water_need": 0.65,
        "nitrogen_demand": 0.80,
        "profit_factor": 1.15,
        "rotation_value": 0.55,
        "heat_tolerance": 0.95
    },
    "BARLEY": {
        "water_need": 0.55,
        "nitrogen_demand": 0.60,
        "profit_factor": 0.85,
        "rotation_value": 0.60,
        "heat_tolerance": 0.65
    },
    "SOYABEAN": {
        "water_need": 0.55,
        "nitrogen_demand": 0.35,
        "profit_factor": 1.00,
        "rotation_value": 0.90,
        "heat_tolerance": 0.80
    }
}


def calculate_crop_score(
    crop: str,
    available_water_liters: float,
    farm_size_acres: float,
    previous_crop: str,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    avg_temp_c: float
) -> Dict[str, float]:

    crop_data = CROP_DATA[crop]

    # --------------------------------------------------------
    # Water suitability
    # --------------------------------------------------------

    # Rough daily water capacity score.
    water_per_acre = (
        available_water_liters /
        max(farm_size_acres, 0.1)
    )

    if water_per_acre >= 12000:
        water_score = 1.00
    elif water_per_acre >= 8000:
        water_score = 0.80
    elif water_per_acre >= 5000:
        water_score = 0.60
    else:
        water_score = 0.35

    # Lower-water crops receive a benefit when water is limited.
    water_fit = (
        water_score * (1.0 - 0.35 * crop_data["water_need"])
    )

    # --------------------------------------------------------
    # Soil nutrient fit
    # --------------------------------------------------------

    nitrogen_score = min(
        nitrogen / 120.0,
        1.0
    )

    phosphorus_score = min(
        phosphorus / 60.0,
        1.0
    )

    potassium_score = min(
        potassium / 50.0,
        1.0
    )

    nutrient_demand = crop_data["nitrogen_demand"]

    nutrient_fit = (
        (
            nitrogen_score
            + phosphorus_score
            + potassium_score
        ) / 3.0
    )

    nutrient_fit = (
        nutrient_fit * (1.0 - 0.25 * nutrient_demand)
    )

    # --------------------------------------------------------
    # Rotation fit
    # --------------------------------------------------------

    previous_crop = previous_crop.upper().strip()

    if previous_crop == crop:
        rotation_fit = 0.35
    elif crop in {"CHICKPEA", "PIGEONPEA", "SOYABEAN"}:
        rotation_fit = min(
            1.0,
            crop_data["rotation_value"] + 0.10
        )
    else:
        rotation_fit = crop_data["rotation_value"]

    # --------------------------------------------------------
    # Temperature fit
    # --------------------------------------------------------

    if avg_temp_c <= 20:
        temperature_fit = 0.70

    elif avg_temp_c <= 25:
        temperature_fit = 0.90

    elif avg_temp_c <= 30:
        temperature_fit = 0.95

    elif avg_temp_c <= 35:
        temperature_fit = 0.80

    else:
        temperature_fit = 0.60

    # Heat-tolerant crops benefit under higher temperatures.
    if avg_temp_c > 30:
        temperature_fit *= (
            0.75 + 0.25 * crop_data["heat_tolerance"]
        )

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    final_score = (
        0.30 * water_fit
        + 0.25 * nutrient_fit
        + 0.20 * rotation_fit
        + 0.15 * temperature_fit
        + 0.10 * crop_data["profit_factor"]
    )

    return {
        "water_fit": round(water_fit * 100, 2),
        "nutrient_fit": round(nutrient_fit * 100, 2),
        "rotation_fit": round(rotation_fit * 100, 2),
        "temperature_fit": round(temperature_fit * 100, 2),
        "score": round(final_score * 100, 2)
    }


def select_best_crops(
    available_water_liters: float,
    farm_size_acres: float,
    previous_crop: str,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    avg_temp_c: float,
    top_n: int = 5
) -> List[dict]:

    results = []

    for crop in CROP_DATA:

        scores = calculate_crop_score(
            crop=crop,
            available_water_liters=available_water_liters,
            farm_size_acres=farm_size_acres,
            previous_crop=previous_crop,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            avg_temp_c=avg_temp_c
        )

        results.append({
            "crop": crop,
            **scores
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_n]