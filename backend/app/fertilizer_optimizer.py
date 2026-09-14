# ============================================================
# AGRITWIN AI - FERTILIZER OPTIMIZATION ENGINE
# ============================================================

from typing import Dict


# ============================================================
# CROP NUTRIENT REQUIREMENTS
# ============================================================
# Approximate nutrient requirements in kg/ha for MVP planning.
CROP_REQUIREMENTS: Dict[str, Dict[str, float]] = {
    "WHEAT": {
        "nitrogen": 120,
        "phosphorus": 60,
        "potassium": 40
    },
    "RICE": {
        "nitrogen": 100,
        "phosphorus": 50,
        "potassium": 50
    },
    "MAIZE": {
        "nitrogen": 140,
        "phosphorus": 70,
        "potassium": 50
    },
    "BARLEY": {
        "nitrogen": 100,
        "phosphorus": 50,
        "potassium": 40
    },
    "CHICKPEA": {
        "nitrogen": 40,
        "phosphorus": 50,
        "potassium": 40
    },
    "PIGEONPEA": {
        "nitrogen": 45,
        "phosphorus": 50,
        "potassium": 40
    },
    "GROUNDNUT": {
        "nitrogen": 40,
        "phosphorus": 50,
        "potassium": 50
    },
    "COTTON": {
        "nitrogen": 120,
        "phosphorus": 60,
        "potassium": 60
    },
    "SUGARCANE": {
        "nitrogen": 180,
        "phosphorus": 80,
        "potassium": 100
    },
    "SOYABEAN": {
        "nitrogen": 60,
        "phosphorus": 60,
        "potassium": 50
    }
}


# ============================================================
# NUTRIENT CLASSIFICATION
# ============================================================

def classify_nutrient(
    value: float,
    crop_requirement: float
) -> str:
    """
    Classify soil nutrient availability relative
    to the crop requirement.
    """

    ratio = value / crop_requirement

    if ratio < 0.40:
        return "Low"

    elif ratio < 0.90:
        return "Moderate"

    else:
        return "Adequate"


# ============================================================
# MAIN FERTILIZER OPTIMIZATION FUNCTION
# ============================================================

def calculate_fertilizer_optimization(
    farm_size_acres: float,
    crop: str,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    ph: float,
    organic_matter: float
):
    """
    Generate an MVP fertilizer recommendation using:

    - Farm size
    - Crop
    - Soil nitrogen
    - Soil phosphorus
    - Soil potassium
    - Soil pH
    - Organic matter
    """

    # --------------------------------------------------------
    # Normalize crop name
    # --------------------------------------------------------

    crop = crop.upper().strip()

    # --------------------------------------------------------
    # Get crop nutrient requirements
    # --------------------------------------------------------

    requirements = CROP_REQUIREMENTS.get(
        crop,
        {
            "nitrogen": 100,
            "phosphorus": 50,
            "potassium": 40
        }
    )

    # --------------------------------------------------------
    # Convert acres -> hectares
    # --------------------------------------------------------

    farm_size_hectares = farm_size_acres * 0.404686

    # --------------------------------------------------------
    # Classify soil nutrients
    # --------------------------------------------------------

    nitrogen_status = classify_nutrient(
        nitrogen,
        requirements["nitrogen"]
    )

    phosphorus_status = classify_nutrient(
        phosphorus,
        requirements["phosphorus"]
    )

    potassium_status = classify_nutrient(
        potassium,
        requirements["potassium"]
    )

    # --------------------------------------------------------
    # Calculate nutrient gaps
    # --------------------------------------------------------

    nitrogen_gap = max(
        0.0,
        requirements["nitrogen"] - nitrogen
    )

    phosphorus_gap = max(
        0.0,
        requirements["phosphorus"] - phosphorus
    )

    potassium_gap = max(
        0.0,
        requirements["potassium"] - potassium
    )

    # --------------------------------------------------------
    # Generate recommendations
    # --------------------------------------------------------

    recommendations = []

    # Nitrogen recommendation
    if nitrogen_status == "Low":

        recommendations.append(
            "Increase nitrogen application in split doses."
        )

    elif nitrogen_status == "Moderate":

        recommendations.append(
            "Apply a moderate nitrogen dose and monitor crop growth."
        )

    # Phosphorus recommendation
    if phosphorus_status == "Low":

        recommendations.append(
            "Apply phosphorus fertilizer before or during sowing."
        )

    elif phosphorus_status == "Moderate":

        recommendations.append(
            "Use a moderate phosphorus application."
        )

    # Potassium recommendation
    if potassium_status == "Low":

        recommendations.append(
            "Increase potassium application to support crop strength "
            "and stress tolerance."
        )

    elif potassium_status == "Moderate":

        recommendations.append(
            "Apply a moderate potassium dose."
        )

    # --------------------------------------------------------
    # Soil pH analysis
    # --------------------------------------------------------

    if ph < 5.5:

        ph_status = "Strongly acidic"

        recommendations.append(
            "Soil is strongly acidic; consider soil amendment "
            "before heavy fertilizer application."
        )

    elif ph < 6.0:

        ph_status = "Moderately acidic"

    elif ph <= 7.5:

        ph_status = "Suitable"

    elif ph <= 8.0:

        ph_status = "Moderately alkaline"

        recommendations.append(
            "Monitor soil pH because alkalinity can reduce "
            "availability of some nutrients."
        )

    else:

        ph_status = "Strongly alkaline"

        recommendations.append(
            "Soil is strongly alkaline; nutrient availability "
            "should be monitored carefully."
        )

    # --------------------------------------------------------
    # Organic matter analysis
    # --------------------------------------------------------

    if organic_matter < 1.0:

        organic_status = "Low"

        recommendations.append(
            "Increase organic matter using compost or other "
            "organic amendments."
        )

    elif organic_matter < 2.0:

        organic_status = "Moderate"

    else:

        organic_status = "Good"

    # --------------------------------------------------------
    # Find priority nutrient
    # --------------------------------------------------------

    gaps = {
        "Nitrogen": nitrogen_gap,
        "Phosphorus": phosphorus_gap,
        "Potassium": potassium_gap
    }

    priority_nutrient = max(
        gaps,
        key=gaps.get
    )

    # --------------------------------------------------------
    # Calculate total nutrient gap
    # --------------------------------------------------------

    total_nutrient_gap_per_hectare = (
        nitrogen_gap
        + phosphorus_gap
        + potassium_gap
    )

    total_nutrient_gap = (
        total_nutrient_gap_per_hectare
        * farm_size_hectares
    )

    # --------------------------------------------------------
    # Fertilizer priority
    # --------------------------------------------------------

    if total_nutrient_gap == 0:

        fertilizer_priority = "Low"

    elif total_nutrient_gap < 150:

        fertilizer_priority = "Moderate"

    else:

        fertilizer_priority = "High"

    # --------------------------------------------------------
    # If no nutrient-specific recommendation exists
    # --------------------------------------------------------

    if not recommendations:

        recommendations.append(
            "Soil nutrient levels are adequate. Avoid unnecessary "
            "fertilizer application and continue soil monitoring."
        )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "crop": crop,

        "farm_size_hectares": round(
            farm_size_hectares,
            2
        ),

        "nitrogen_status": nitrogen_status,

        "phosphorus_status": phosphorus_status,

        "potassium_status": potassium_status,

        "nitrogen_gap_kg_per_ha": round(
            nitrogen_gap,
            2
        ),

        "phosphorus_gap_kg_per_ha": round(
            phosphorus_gap,
            2
        ),

        "potassium_gap_kg_per_ha": round(
            potassium_gap,
            2
        ),

        "priority_nutrient": priority_nutrient,

        "ph_status": ph_status,

        "organic_matter_status": organic_status,

        "total_nutrient_gap_kg_per_ha": round(
            total_nutrient_gap_per_hectare,
            2
        ),

        "estimated_total_nutrient_gap_kg": round(
            total_nutrient_gap,
            2
        ),

        "fertilizer_priority": fertilizer_priority,

        "recommendations": recommendations
    }