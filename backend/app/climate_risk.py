# ============================================================
# AGRITWIN AI - CLIMATE RISK ENGINE
# ============================================================


def calculate_climate_risk(
    crop: str,
    avg_temp_c: float,
    rainfall_mm: float,
    temperature_change: float = 0.0,
    rainfall_change_percent: float = 0.0
) -> dict:

    crop = crop.upper().strip()

    future_temperature = avg_temp_c + temperature_change

    future_rainfall = (
        rainfall_mm *
        (1 + rainfall_change_percent / 100)
    )

    # --------------------------------------------------------
    # Temperature risk
    # --------------------------------------------------------

    if future_temperature <= 20:
        temperature_risk = 15.0

    elif future_temperature <= 28:
        temperature_risk = 20.0

    elif future_temperature <= 32:
        temperature_risk = 45.0

    elif future_temperature <= 36:
        temperature_risk = 70.0

    else:
        temperature_risk = 90.0

    # --------------------------------------------------------
    # Rainfall risk
    # --------------------------------------------------------

    if future_rainfall >= 800:
        rainfall_risk = 15.0

    elif future_rainfall >= 500:
        rainfall_risk = 25.0

    elif future_rainfall >= 250:
        rainfall_risk = 50.0

    elif future_rainfall >= 100:
        rainfall_risk = 70.0

    else:
        rainfall_risk = 90.0

    # Extreme rainfall condition
    if future_rainfall > 1800:
        rainfall_risk = 85.0

    # --------------------------------------------------------
    # Crop-specific sensitivity
    # --------------------------------------------------------

    temperature_sensitive_crops = {
        "WHEAT": 1.15,
        "CHICKPEA": 1.05,
        "RICE": 0.90,
        "MAIZE": 1.00,
        "BARLEY": 1.10,
        "PIGEONPEA": 0.90,
        "GROUNDNUT": 0.90,
        "COTTON": 0.85,
        "SOYABEAN": 0.95
    }

    sensitivity = temperature_sensitive_crops.get(
        crop,
        1.0
    )

    temperature_risk *= sensitivity

    temperature_risk = min(
        temperature_risk,
        100.0
    )

    # --------------------------------------------------------
    # Overall climate risk
    # --------------------------------------------------------

    climate_risk = (
        0.55 * temperature_risk
        + 0.45 * rainfall_risk
    )

    climate_risk = round(
        min(max(climate_risk, 0.0), 100.0),
        2
    )

    if climate_risk < 30:
        risk_level = "Low"

    elif climate_risk < 60:
        risk_level = "Moderate"

    elif climate_risk < 80:
        risk_level = "High"

    else:
        risk_level = "Severe"

    # --------------------------------------------------------
    # Main risk drivers
    # --------------------------------------------------------

    drivers = []

    if temperature_risk >= 60:
        drivers.append(
            "High temperature stress risk"
        )

    elif temperature_risk >= 30:
        drivers.append(
            "Moderate temperature stress risk"
        )

    if rainfall_risk >= 60:
        drivers.append(
            "Rainfall-related water stress or extreme rainfall risk"
        )

    elif rainfall_risk >= 30:
        drivers.append(
            "Moderate rainfall-related risk"
        )

    # If overall risk is moderate/high but no single component
    # crossed the driver thresholds, provide a consistent message.
    if not drivers and climate_risk >= 30:

        drivers.append(
            "Combined temperature and rainfall conditions "
            "create a moderate climate risk"
        )

    if not drivers:

        drivers.append(
            "No major climate stress detected under this scenario"
        )

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    if risk_level in {"High", "Severe"}:

        recommendation = (
            "Prepare an adaptive farming strategy by improving "
            "irrigation planning, crop timing and stress monitoring."
        )

    elif risk_level == "Moderate":

        recommendation = (
            "Monitor weather closely and maintain flexible "
            "irrigation and crop-management plans."
        )

    else:

        recommendation = (
            "Current climate scenario presents relatively low risk."
        )

    return {
        "crop": crop,

        "current_avg_temp_c": round(
            avg_temp_c,
            2
        ),

        "future_avg_temp_c": round(
            future_temperature,
            2
        ),

        "current_rainfall_mm": round(
            rainfall_mm,
            2
        ),

        "future_rainfall_mm": round(
            future_rainfall,
            2
        ),

        "temperature_risk": round(
            temperature_risk,
            2
        ),

        "rainfall_risk": round(
            rainfall_risk,
            2
        ),

        "climate_risk": climate_risk,

        "risk_level": risk_level,

        "drivers": drivers,

        "recommendation": recommendation
    }