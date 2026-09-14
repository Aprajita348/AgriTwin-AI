# ============================================================
# AGRITWIN AI - EXPLAINABLE AI ENGINE
# ============================================================


def explain_farming_decision(
    crop: str,
    crop_score: float,
    water_fit: float,
    nutrient_fit: float,
    rotation_fit: float,
    temperature_fit: float,
    fertilizer_priority: str,
    water_coverage_percent: float,
    sustainability_score: float,
    climate_risk: float
) -> dict:
    """
    Generate human-readable explanations for a farming decision.

    This is a transparent rule-based explanation layer.
    It explains which factors positively or negatively affected
    the recommendation.
    """

    crop = crop.upper().strip()

    factors = []
    positive_factors = []
    negative_factors = []

    # --------------------------------------------------------
    # Crop suitability
    # --------------------------------------------------------

    if crop_score >= 80:
        positive_factors.append(
            f"{crop} has a strong overall suitability score "
            f"of {crop_score}%."
        )

    elif crop_score >= 65:
        factors.append(
            f"{crop} has a moderate suitability score "
            f"of {crop_score}%."
        )

    else:
        negative_factors.append(
            f"{crop} has a relatively low suitability score "
            f"of {crop_score}%."
        )

    # --------------------------------------------------------
    # Water
    # --------------------------------------------------------

    if water_fit >= 80:
        positive_factors.append(
            f"Water availability is favorable for {crop} "
            f"(water-fit score: {water_fit}%)."
        )

    elif water_fit >= 60:
        factors.append(
            f"Water availability is acceptable but not ideal "
            f"(water-fit score: {water_fit}%)."
        )

    else:
        negative_factors.append(
            f"Water availability may restrict the crop "
            f"(water-fit score: {water_fit}%)."
        )

    # --------------------------------------------------------
    # Nutrients
    # --------------------------------------------------------

    if nutrient_fit >= 80:
        positive_factors.append(
            f"Soil nutrient conditions fit the crop well "
            f"(nutrient-fit score: {nutrient_fit}%)."
        )

    elif nutrient_fit >= 60:
        factors.append(
            f"Soil nutrient conditions are moderately suitable "
            f"(nutrient-fit score: {nutrient_fit}%)."
        )

    else:
        negative_factors.append(
            f"Soil nutrient conditions may limit performance "
            f"(nutrient-fit score: {nutrient_fit}%)."
        )

    # --------------------------------------------------------
    # Rotation
    # --------------------------------------------------------

    if rotation_fit >= 80:
        positive_factors.append(
            f"Crop rotation suitability is strong "
            f"({rotation_fit}%)."
        )

    elif rotation_fit >= 60:
        factors.append(
            f"Crop rotation suitability is moderate "
            f"({rotation_fit}%)."
        )

    else:
        negative_factors.append(
            f"Crop rotation suitability is weak "
            f"({rotation_fit}%)."
        )

    # --------------------------------------------------------
    # Temperature
    # --------------------------------------------------------

    if temperature_fit >= 80:
        positive_factors.append(
            f"Current temperature conditions are favorable "
            f"({temperature_fit}%)."
        )

    elif temperature_fit >= 60:
        factors.append(
            f"Temperature conditions are moderately suitable "
            f"({temperature_fit}%)."
        )

    else:
        negative_factors.append(
            f"Temperature conditions may create crop stress "
            f"({temperature_fit}%)."
        )

    # --------------------------------------------------------
    # Water coverage
    # --------------------------------------------------------

    if water_coverage_percent >= 90:
        positive_factors.append(
            f"Estimated water coverage is high at "
            f"{water_coverage_percent}%."
        )

    elif water_coverage_percent >= 70:
        factors.append(
            f"Estimated water coverage is moderate at "
            f"{water_coverage_percent}%."
        )

    else:
        negative_factors.append(
            f"Water coverage is limited at "
            f"{water_coverage_percent}%."
        )

    # --------------------------------------------------------
    # Fertilizer
    # --------------------------------------------------------

    if fertilizer_priority == "Low":
        positive_factors.append(
            "Current fertilizer priority is low, reducing "
            "the risk of unnecessary nutrient application."
        )

    elif fertilizer_priority == "Moderate":
        factors.append(
            "Moderate fertilizer attention is required."
        )

    else:
        negative_factors.append(
            "High fertilizer priority indicates a significant "
            "nutrient-management requirement."
        )

    # --------------------------------------------------------
    # Sustainability
    # --------------------------------------------------------

    if sustainability_score >= 80:
        positive_factors.append(
            f"The overall sustainability score is strong "
            f"at {sustainability_score}/100."
        )

    elif sustainability_score >= 60:
        factors.append(
            f"The sustainability score is moderate at "
            f"{sustainability_score}/100."
        )

    else:
        negative_factors.append(
            f"The sustainability score is low at "
            f"{sustainability_score}/100."
        )

    # --------------------------------------------------------
    # Climate risk
    # --------------------------------------------------------

    if climate_risk < 30:
        positive_factors.append(
            f"Climate risk is currently low "
            f"({climate_risk})."
        )

    elif climate_risk < 60:
        factors.append(
            f"Climate risk is moderate "
            f"({climate_risk})."
        )

    else:
        negative_factors.append(
            f"Climate risk is high "
            f"({climate_risk})."
        )

    # --------------------------------------------------------
    # Build summary
    # --------------------------------------------------------

    if negative_factors:
        summary = (
            f"The recommendation for {crop} is supported by "
            f"{len(positive_factors)} favorable factors, but "
            f"{len(negative_factors)} risk factors should be "
            f"monitored."
        )
    else:
        summary = (
            f"The recommendation for {crop} is supported by "
            f"the current water, soil, rotation, climate and "
            f"sustainability conditions."
        )

    return {
        "crop": crop,
        "summary": summary,
        "positive_factors": positive_factors,
        "neutral_factors": factors,
        "negative_factors": negative_factors,
        "factor_count": {
            "positive": len(positive_factors),
            "neutral": len(factors),
            "negative": len(negative_factors)
        }
    }