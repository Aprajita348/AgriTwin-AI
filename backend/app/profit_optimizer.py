# ============================================================
# AGRITWIN AI - PROFIT OPTIMIZATION ENGINE
# ============================================================

from typing import Dict


# Approximate planning values for MVP simulation.
# These are not market quotes and should not be treated as
# current farm-market prices.
CROP_ECONOMICS: Dict[str, Dict[str, float]] = {
    "WHEAT": {
        "price_per_kg": 25.0,
        "cost_per_acre": 18000.0
    },
    "RICE": {
        "price_per_kg": 24.0,
        "cost_per_acre": 22000.0
    },
    "MAIZE": {
        "price_per_kg": 22.0,
        "cost_per_acre": 19000.0
    },
    "BARLEY": {
        "price_per_kg": 23.0,
        "cost_per_acre": 17000.0
    },
    "CHICKPEA": {
        "price_per_kg": 65.0,
        "cost_per_acre": 16000.0
    },
    "PIGEONPEA": {
        "price_per_kg": 75.0,
        "cost_per_acre": 18000.0
    },
    "GROUNDNUT": {
        "price_per_kg": 55.0,
        "cost_per_acre": 20000.0
    },
    "COTTON": {
        "price_per_kg": 70.0,
        "cost_per_acre": 24000.0
    },
    "SOYABEAN": {
        "price_per_kg": 45.0,
        "cost_per_acre": 18000.0
    }
}


def calculate_profit(
    crop: str,
    farm_size_acres: float,
    predicted_yield_kg_per_ha: float
) -> dict:

    crop = crop.upper().strip()

    economics = CROP_ECONOMICS.get(
        crop,
        {
            "price_per_kg": 30.0,
            "cost_per_acre": 18000.0
        }
    )

    farm_size_hectares = (
        farm_size_acres * 0.404686
    )

    total_production_kg = (
        predicted_yield_kg_per_ha
        * farm_size_hectares
    )

    revenue = (
        total_production_kg
        * economics["price_per_kg"]
    )

    total_cost = (
        farm_size_acres
        * economics["cost_per_acre"]
    )

    estimated_profit = (
        revenue - total_cost
    )

    profit_per_acre = (
        estimated_profit /
        max(farm_size_acres, 0.1)
    )

    return {
        "crop": crop,
        "farm_size_hectares": round(
            farm_size_hectares,
            2
        ),
        "predicted_yield_kg_per_ha": round(
            predicted_yield_kg_per_ha,
            2
        ),
        "estimated_production_kg": round(
            total_production_kg,
            2
        ),
        "assumed_price_per_kg": round(
            economics["price_per_kg"],
            2
        ),
        "estimated_revenue": round(
            revenue,
            2
        ),
        "estimated_cost": round(
            total_cost,
            2
        ),
        "estimated_profit": round(
            estimated_profit,
            2
        ),
        "estimated_profit_per_acre": round(
            profit_per_acre,
            2
        )
    }


def compare_crop_profitability(
    farm_size_acres: float,
    crop_predictions: Dict[str, float]
) -> list:

    results = []

    for crop, predicted_yield in crop_predictions.items():

        result = calculate_profit(
            crop=crop,
            farm_size_acres=farm_size_acres,
            predicted_yield_kg_per_ha=predicted_yield
        )

        results.append(result)

    results.sort(
        key=lambda item: item["estimated_profit"],
        reverse=True
    )

    return results