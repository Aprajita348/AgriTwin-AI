# ============================================================
# AGRITWIN AI - EARLY WARNING ENGINE
# ============================================================


def generate_early_warnings(
    crop: str,
    avg_temp_c: float,
    rainfall_mm: float,
    available_water_liters: float,
    farm_size_acres: float,
    nitrogen: float,
    phosphorus: float,
    potassium: float
) -> dict:

    crop = crop.upper().strip()

    warnings = []

    # --------------------------------------------------------
    # Heat warning
    # --------------------------------------------------------

    if avg_temp_c >= 35:
        warnings.append({
            "type": "Heat Stress",
            "severity": "High",
            "message": (
                "Temperature is high enough to create significant "
                "crop heat-stress risk."
            )
        })

    elif avg_temp_c >= 30:
        warnings.append({
            "type": "Heat Stress",
            "severity": "Moderate",
            "message": (
                "Temperature is elevated. Monitor crop stress "
                "and irrigation needs."
            )
        })

    # --------------------------------------------------------
    # Low rainfall warning
    # --------------------------------------------------------

    if rainfall_mm < 100:

        warnings.append({
            "type": "Low Rainfall",
            "severity": "High",
            "message": (
                "Rainfall is very low. Water availability should "
                "be monitored closely."
            )
        })

    elif rainfall_mm < 250:

        warnings.append({
            "type": "Low Rainfall",
            "severity": "Moderate",
            "message": (
                "Rainfall is limited. Irrigation planning may "
                "be required."
            )
        })

    # --------------------------------------------------------
    # Water availability warning
    # --------------------------------------------------------

    estimated_minimum_water_need = (
        farm_size_acres * 5000
    )

    if available_water_liters < estimated_minimum_water_need:

        warnings.append({
            "type": "Water Shortage",
            "severity": "High",
            "message": (
                "Available water is below the minimum planning "
                "requirement for the farm."
            )
        })

    # --------------------------------------------------------
    # Nutrient warnings
    # --------------------------------------------------------

    if nitrogen < 50:

        warnings.append({
            "type": "Nitrogen Deficiency",
            "severity": "High",
            "message": (
                "Soil nitrogen is low and may restrict crop growth."
            )
        })

    elif nitrogen < 90:

        warnings.append({
            "type": "Nitrogen Deficiency",
            "severity": "Moderate",
            "message": (
                "Soil nitrogen is below the preferred planning level."
            )
        })

    if phosphorus < 30:

        warnings.append({
            "type": "Phosphorus Deficiency",
            "severity": "High",
            "message": (
                "Soil phosphorus is low and should be addressed."
            )
        })

    if potassium < 30:

        warnings.append({
            "type": "Potassium Deficiency",
            "severity": "High",
            "message": (
                "Soil potassium is low and may reduce crop "
                "strength and stress tolerance."
            )
        })

    # --------------------------------------------------------
    # Overall alert level
    # --------------------------------------------------------

    if any(
        warning["severity"] == "High"
        for warning in warnings
    ):
        overall_alert = "High"

    elif any(
        warning["severity"] == "Moderate"
        for warning in warnings
    ):
        overall_alert = "Moderate"

    else:
        overall_alert = "Low"

    # --------------------------------------------------------
    # No-warning case
    # --------------------------------------------------------

    if not warnings:

        warnings.append({
            "type": "System Status",
            "severity": "Low",
            "message": (
                "No major early-warning condition detected."
            )
        })

    return {
        "crop": crop,
        "overall_alert": overall_alert,
        "warning_count": len(warnings),
        "warnings": warnings
    }