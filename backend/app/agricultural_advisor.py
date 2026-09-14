# ============================================================
# AGRITWIN AI - AGRICULTURAL ADVISOR
# ============================================================


def generate_agricultural_advice(
    crop: str,
    predicted_yield_kg_per_ha: float,
    water_coverage_percent: float,
    fertilizer_priority: str,
    sustainability_score: float,
    climate_risk: float,
    recommended_water_liters: float = 0.0
) -> dict:
    """
    Generate a transparent agricultural action plan.

    This version is rule-based and deterministic.
    It is designed so a GenAI model/API can later be plugged
    into the same interface.
    """

    crop = crop.upper().strip()

    actions = []
    priorities = []

    # --------------------------------------------------------
    # Yield
    # --------------------------------------------------------

    actions.append(
        f"Expected yield for {crop} is approximately "
        f"{predicted_yield_kg_per_ha:.2f} kg/ha."
    )

    # --------------------------------------------------------
    # Water
    # --------------------------------------------------------

    if water_coverage_percent < 70:

        priorities.append("High")
        actions.append(
            "Prioritize water conservation and irrigation "
            "during critical crop-growth stages."
        )

    elif water_coverage_percent < 90:

        priorities.append("Moderate")
        actions.append(
            "Monitor soil moisture and avoid unnecessary "
            "irrigation losses."
        )

    else:

        priorities.append("Low")
        actions.append(
            "Current estimated water availability is sufficient "
            "for the planned requirement."
        )

    # --------------------------------------------------------
    # Fertilizer
    # --------------------------------------------------------

    if fertilizer_priority == "High":

        priorities.append("High")
        actions.append(
            "Address the major nutrient requirement using "
            "split and need-based fertilizer application."
        )

    elif fertilizer_priority == "Moderate":

        priorities.append("Moderate")
        actions.append(
            "Use a moderate, targeted fertilizer application "
            "instead of unnecessary blanket application."
        )

    else:

        priorities.append("Low")
        actions.append(
            "Avoid unnecessary fertilizer application and "
            "continue soil monitoring."
        )

    # --------------------------------------------------------
    # Climate risk
    # --------------------------------------------------------

    if climate_risk >= 80:

        priorities.append("High")
        actions.append(
            "Prepare an adaptive plan for severe climate risk, "
            "including irrigation and crop-stress monitoring."
        )

    elif climate_risk >= 60:

        priorities.append("High")
        actions.append(
            "Closely monitor weather conditions and adjust "
            "irrigation and farm operations."
        )

    elif climate_risk >= 30:

        priorities.append("Moderate")
        actions.append(
            "Monitor weather forecasts and maintain a flexible "
            "farm-management plan."
        )

    else:

        priorities.append("Low")
        actions.append(
            "Current climate risk is relatively low."
        )

    # --------------------------------------------------------
    # Sustainability
    # --------------------------------------------------------

    if sustainability_score >= 80:

        actions.append(
            "Maintain current resource-efficient practices "
            "because the sustainability score is strong."
        )

    elif sustainability_score >= 60:

        actions.append(
            "Improve water, nutrient and soil-management "
            "practices to raise sustainability."
        )

    else:

        actions.append(
            "Prioritize sustainable resource use and soil-health "
            "improvements."
        )

    # --------------------------------------------------------
    # Overall priority
    # --------------------------------------------------------

    if "High" in priorities:
        overall_priority = "High"

    elif "Moderate" in priorities:
        overall_priority = "Moderate"

    else:
        overall_priority = "Low"

    # --------------------------------------------------------
    # Final message
    # --------------------------------------------------------

    if overall_priority == "High":

        message = (
            f"For {crop}, focus first on the highest-risk resource "
            f"or climate constraint before making additional farm "
            f"inputs."
        )

    elif overall_priority == "Moderate":

        message = (
            f"For {crop}, current conditions are manageable, but "
            f"water, nutrients and climate indicators should be "
            f"actively monitored."
        )

    else:

        message = (
            f"For {crop}, current conditions appear stable. "
            f"Continue monitoring and avoid unnecessary inputs."
        )

    return {
        "crop": crop,
        "overall_priority": overall_priority,
        "advice": message,
        "actions": actions,
        "recommended_water_liters": round(
            recommended_water_liters,
            2
        )
    }