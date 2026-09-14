# ============================================================
# AGRITWIN AI - INTEGRATED DECISION PIPELINE
# ============================================================

import os
import joblib
import pandas as pd

from .crop_optimizer import select_best_crops
from .profit_optimizer import calculate_profit
from .sustainability_engine import calculate_sustainability_score
from .climate_risk import calculate_climate_risk
from .explainable_ai import explain_farming_decision
from .agricultural_advisor import generate_agricultural_advice


# ============================================================
# LOAD XGBOOST YIELD MODEL
# ============================================================

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "models",
    "yield_prediction_model.pkl"
)

yield_model = joblib.load(MODEL_PATH)


# ============================================================
# YIELD PREDICTION HELPER
# ============================================================

def predict_yield_for_crop(
    district_code: int,
    state_code: int,
    year: int,
    crop: str,
    district: str,
    state_name: str,
    area_1000_ha: float,
    rainfall_mm: float,
    avg_temp_c: float,
    max_temp_c: float,
    min_temp_c: float
) -> float:

    input_data = pd.DataFrame([
        {
            "district_code": district_code,
            "state_code": state_code,
            "year": year,
            "crop": crop,
            "district": district,
            "state_name": state_name,
            "area_1000_ha": area_1000_ha,
            "rainfall_mm": rainfall_mm,
            "avg_temp_c": avg_temp_c,
            "max_temp_c": max_temp_c,
            "min_temp_c": min_temp_c
        }
    ])

    prediction = yield_model.predict(
        input_data
    )[0]

    return max(
        0.0,
        float(prediction)
    )


# ============================================================
# INTEGRATED DECISION PIPELINE
# ============================================================

def run_decision_pipeline(
    district_code: int,
    state_code: int,
    year: int,
    district: str,
    state_name: str,
    area_1000_ha: float,

    farm_size_acres: float,
    previous_crop: str,

    nitrogen: float,
    phosphorus: float,
    potassium: float,
    ph: float,
    organic_matter: float,

    available_water_liters: float,
    irrigation_type: str,

    rainfall_mm: float,
    avg_temp_c: float,
    max_temp_c: float,
    min_temp_c: float
):

    # ========================================================
    # 1. CROP SELECTION
    # ========================================================

    crop_candidates = select_best_crops(
        available_water_liters=available_water_liters,
        farm_size_acres=farm_size_acres,
        previous_crop=previous_crop,
        nitrogen=nitrogen,
        phosphorus=phosphorus,
        potassium=potassium,
        avg_temp_c=avg_temp_c,
        top_n=5
    )

    # ========================================================
    # 2. CROP-SPECIFIC YIELD + PROFIT
    # ========================================================

    evaluated_crops = []

    for candidate in crop_candidates:

        crop = candidate["crop"]

        predicted_yield = predict_yield_for_crop(
            district_code=district_code,
            state_code=state_code,
            year=year,
            crop=crop,
            district=district,
            state_name=state_name,
            area_1000_ha=area_1000_ha,
            rainfall_mm=rainfall_mm,
            avg_temp_c=avg_temp_c,
            max_temp_c=max_temp_c,
            min_temp_c=min_temp_c
        )

        profit = calculate_profit(
            crop=crop,
            farm_size_acres=farm_size_acres,
            predicted_yield_kg_per_ha=predicted_yield
        )

        evaluated_crops.append({
            **candidate,
            "predicted_yield_kg_per_ha": round(
                predicted_yield,
                2
            ),
            "estimated_profit": profit[
                "estimated_profit"
            ],
            "estimated_profit_per_acre": profit[
                "estimated_profit_per_acre"
            ]
        })

    # ========================================================
    # 3. FINAL CROP SELECTION
    # ========================================================
    # We balance crop suitability and expected profit.

    for crop in evaluated_crops:

        suitability_score = crop["score"]

        profit_per_acre = crop[
            "estimated_profit_per_acre"
        ]

        # Normalize profit roughly for ranking.
        if profit_per_acre >= 75000:
            profit_score = 100.0
        elif profit_per_acre >= 50000:
            profit_score = 90.0
        elif profit_per_acre >= 30000:
            profit_score = 75.0
        elif profit_per_acre >= 15000:
            profit_score = 60.0
        else:
            profit_score = 40.0

        crop["decision_score"] = round(
            0.65 * suitability_score
            + 0.35 * profit_score,
            2
        )

    evaluated_crops.sort(
        key=lambda item: item["decision_score"],
        reverse=True
    )

    best_crop = evaluated_crops[0]

    # ========================================================
    # 4. FERTILIZER PRIORITY
    # ========================================================

    nutrient_ratios = {
        "Nitrogen": nitrogen / 120.0,
        "Phosphorus": phosphorus / 60.0,
        "Potassium": potassium / 40.0
    }

    priority_nutrient = min(
        nutrient_ratios,
        key=nutrient_ratios.get
    )

    lowest_ratio = nutrient_ratios[
        priority_nutrient
    ]

    if lowest_ratio < 0.40:
        fertilizer_priority = "High"

    elif lowest_ratio < 0.90:
        fertilizer_priority = "Moderate"

    else:
        fertilizer_priority = "Low"

    # ========================================================
    # 5. ORGANIC MATTER STATUS
    # ========================================================

    if organic_matter >= 2.0:
        organic_matter_status = "Good"

    elif organic_matter >= 1.0:
        organic_matter_status = "Moderate"

    else:
        organic_matter_status = "Low"

    # ========================================================
    # 6. WATER COVERAGE
    # ========================================================

    estimated_water_need = (
        farm_size_acres * 9800
    )

    if estimated_water_need <= 0:
        water_coverage_percent = 100.0

    else:
        water_coverage_percent = min(
            100.0,
            (
                available_water_liters
                / estimated_water_need
            ) * 100
        )

    # ========================================================
    # 7. CLIMATE RISK
    # ========================================================

    climate = calculate_climate_risk(
        crop=best_crop["crop"],
        avg_temp_c=avg_temp_c,
        rainfall_mm=rainfall_mm
    )

    climate_risk = climate["climate_risk"]

    # ========================================================
    # 8. SUSTAINABILITY
    # ========================================================

    sustainability = calculate_sustainability_score(
        water_coverage_percent=water_coverage_percent,
        fertilizer_priority=fertilizer_priority,
        organic_matter_status=organic_matter_status,
        irrigation_type=irrigation_type,
        crop_rotation_score=best_crop[
            "rotation_fit"
        ],
        estimated_profit_per_acre=best_crop[
            "estimated_profit_per_acre"
        ]
    )

    # ========================================================
    # 9. EXPLAINABLE AI
    # ========================================================

    explanation = explain_farming_decision(
        crop=best_crop["crop"],
        crop_score=best_crop["score"],
        water_fit=best_crop["water_fit"],
        nutrient_fit=best_crop["nutrient_fit"],
        rotation_fit=best_crop["rotation_fit"],
        temperature_fit=best_crop["temperature_fit"],
        fertilizer_priority=fertilizer_priority,
        water_coverage_percent=water_coverage_percent,
        sustainability_score=sustainability[
            "sustainability_score"
        ],
        climate_risk=climate_risk
    )

    # ========================================================
    # 10. AGRICULTURAL ADVISOR
    # ========================================================

    advisor = generate_agricultural_advice(
        crop=best_crop["crop"],
        predicted_yield_kg_per_ha=best_crop[
            "predicted_yield_kg_per_ha"
        ],
        water_coverage_percent=water_coverage_percent,
        fertilizer_priority=fertilizer_priority,
        sustainability_score=sustainability[
            "sustainability_score"
        ],
        climate_risk=climate_risk,
        recommended_water_liters=available_water_liters
    )

    # ========================================================
    # 11. FINAL RECOMMENDATION
    # ========================================================

    final_recommendation = (
        f"AgriTwin AI recommends {best_crop['crop']} "
        f"with a decision score of "
        f"{best_crop['decision_score']}%. "
        f"Expected yield is approximately "
        f"{best_crop['predicted_yield_kg_per_ha']:.2f} kg/ha "
        f"and estimated profit is "
        f"₹{best_crop['estimated_profit']:.2f}. "
        f"Sustainability score is "
        f"{sustainability['sustainability_score']}/100."
    )

    # ========================================================
    # 12. RETURN COMPLETE DECISION
    # ========================================================

    return {
        "recommended_crop": best_crop,

        "crop_comparison": evaluated_crops,

        "fertilizer_analysis": {
            "priority_nutrient": priority_nutrient,
            "fertilizer_priority": fertilizer_priority
        },

        "water_analysis": {
            "available_water_liters": round(
                available_water_liters,
                2
            ),
            "estimated_water_need_liters": round(
                estimated_water_need,
                2
            ),
            "water_coverage_percent": round(
                water_coverage_percent,
                2
            )
        },

        "climate_analysis": climate,

        "sustainability": sustainability,

        "explanation": explanation,

        "advisor": advisor,

        "final_recommendation": final_recommendation
    }