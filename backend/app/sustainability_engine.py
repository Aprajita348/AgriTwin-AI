# ============================================================
# AGRITWIN AI - SUSTAINABILITY ENGINE
# ============================================================


def calculate_sustainability_score(
    water_coverage_percent: float,
    fertilizer_priority: str,
    organic_matter_status: str,
    irrigation_type: str,
    crop_rotation_score: float,
    estimated_profit_per_acre: float
) -> dict:

    # --------------------------------------------------------
    # Water efficiency score
    # --------------------------------------------------------

    water_score = min(
        max(water_coverage_percent, 0.0),
        100.0
    )

    # --------------------------------------------------------
    # Fertilizer score
    # --------------------------------------------------------

    fertilizer_scores = {
        "Low": 100.0,
        "Moderate": 75.0,
        "High": 45.0
    }

    fertilizer_score = fertilizer_scores.get(
        fertilizer_priority,
        60.0
    )

    # --------------------------------------------------------
    # Soil health score
    # --------------------------------------------------------

    soil_scores = {
        "Good": 100.0,
        "Moderate": 70.0,
        "Low": 40.0
    }

    soil_score = soil_scores.get(
        organic_matter_status,
        60.0
    )

    # --------------------------------------------------------
    # Irrigation efficiency
    # --------------------------------------------------------

    irrigation_scores = {
        "Drip": 100.0,
        "Sprinkler": 80.0,
        "Flood": 55.0
    }

    irrigation_score = irrigation_scores.get(
        irrigation_type,
        55.0
    )

    # --------------------------------------------------------
    # Rotation score
    # --------------------------------------------------------

    rotation_score = min(
        max(crop_rotation_score, 0.0),
        100.0
    )

    # --------------------------------------------------------
    # Profit sustainability contribution
    # --------------------------------------------------------

    if estimated_profit_per_acre >= 50000:
        profit_score = 100.0

    elif estimated_profit_per_acre >= 25000:
        profit_score = 85.0

    elif estimated_profit_per_acre >= 10000:
        profit_score = 70.0

    elif estimated_profit_per_acre >= 0:
        profit_score = 50.0

    else:
        profit_score = 25.0

    # --------------------------------------------------------
    # Final weighted sustainability score
    # --------------------------------------------------------

    sustainability_score = (
        0.25 * water_score
        + 0.20 * fertilizer_score
        + 0.20 * soil_score
        + 0.15 * irrigation_score
        + 0.15 * rotation_score
        + 0.05 * profit_score
    )

    sustainability_score = round(
        sustainability_score,
        2
    )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    if sustainability_score >= 80:
        sustainability_level = "Excellent"

    elif sustainability_score >= 65:
        sustainability_level = "Good"

    elif sustainability_score >= 50:
        sustainability_level = "Moderate"

    else:
        sustainability_level = "Needs Improvement"

    return {
        "water_score": round(water_score, 2),
        "fertilizer_score": round(fertilizer_score, 2),
        "soil_health_score": round(soil_score, 2),
        "irrigation_efficiency_score": round(
            irrigation_score,
            2
        ),
        "crop_rotation_score": round(
            rotation_score,
            2
        ),
        "profit_score": round(
            profit_score,
            2
        ),
        "sustainability_score": sustainability_score,
        "sustainability_level": sustainability_level
    }