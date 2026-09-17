from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)


class AgriculturalAdvice(BaseModel):
    summary: str = Field(
        description="Short farmer-friendly summary"
    )

    recommendation: str = Field(
        description="Main recommended action"
    )

    reasons: list[str] = Field(
        description="Main reasons supporting the recommendation"
    )

    expected_impact: list[str] = Field(
        description="Expected effects on yield, water, risk, profit or sustainability"
    )

    warnings: list[str] = Field(
        description="Important risks or limitations"
    )

    next_steps: list[str] = Field(
        description="Practical next steps for the farmer"
    )

    language: str = Field(
        description="Response language"
    )


def generate_ai_advice(
    crop: str,
    predicted_yield_kg_per_ha: float,
    water_coverage_percent: float,
    fertilizer_priority: str,
    sustainability_score: float,
    climate_risk: float,
    recommended_water_liters: float = 0.0,
    rainfall_mm: float | None = None,
    avg_temp_c: float | None = None,
    max_temp_c: float | None = None,
    min_temp_c: float | None = None,
    soil_ph: float | None = None,
    organic_matter: float | None = None,
    language: str = "English",
) -> dict:

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured"
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    farm_context = {
        "crop": crop,
        "predicted_yield_kg_per_ha": predicted_yield_kg_per_ha,
        "water_coverage_percent": water_coverage_percent,
        "fertilizer_priority": fertilizer_priority,
        "sustainability_score": sustainability_score,
        "climate_risk": climate_risk,
        "recommended_water_liters": recommended_water_liters,
        "rainfall_mm": rainfall_mm,
        "avg_temp_c": avg_temp_c,
        "max_temp_c": max_temp_c,
        "min_temp_c": min_temp_c,
        "soil_ph": soil_ph,
        "organic_matter": organic_matter,
    }

    prompt = f"""
You are an agricultural decision-support assistant for AgriTwin AI.

Your job is to EXPLAIN structured outputs produced by the application's
existing ML, optimization and rule-based systems.

Do NOT invent measurements, prices, field conditions, disease diagnoses,
or guaranteed outcomes.

Do NOT replace the application's numerical calculations.

Use only the supplied farm context.

Explain the results in a practical and conservative way.

The user requested this language:
{language}

Farm and model context:
{farm_context}

Return:
1. A short summary.
2. The main recommended action.
3. The reasons behind it.
4. Expected impacts/trade-offs.
5. Important warnings or uncertainty.
6. Concrete next steps.

For safety:
- Treat model predictions as estimates.
- Do not claim certainty.
- Clearly mention missing data when important.
- Never recommend unsafe chemical application rates.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": AgriculturalAdvice,
        },
    )

    result = AgriculturalAdvice.model_validate_json(
        response.text
    )

    return result.model_dump()