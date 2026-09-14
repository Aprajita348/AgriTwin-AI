# ============================================================
# AGRITWIN AI - WHAT-IF DIGITAL FARM SIMULATOR
# ============================================================

from .climate_risk import calculate_climate_risk


def simulate_farm_scenario(
    crop: str,
    farm_size_acres: float,
    baseline_yield_kg_per_ha: float,
    baseline_profit: float,
    baseline_water_liters: float,
    baseline_sustainability_score: float,
    avg_temp_c: float,
    rainfall_mm: float,
    temperature_change: float = 0.0,
    rainfall_change_percent: float = 0.0,
    irrigation_change_percent: float = 0.0,
    fertilizer_change_percent: float = 0.0
) -> dict:

    # --------------------------------------------------------
    # Scenario weather
    # --------------------------------------------------------

    scenario_temperature = (
        avg_temp_c + temperature_change
    )

    scenario_rainfall = (
        rainfall_mm *
        (1 + rainfall_change_percent / 100)
    )

    # --------------------------------------------------------
    # Yield impact
    # --------------------------------------------------------

    temperature_penalty = 0.0

    if temperature_change > 0:
        temperature_penalty += (
            temperature_change * 2.5
        )

    elif temperature_change < 0:
        temperature_penalty += (
            temperature_change * 1.0
        )

    rainfall_penalty = 0.0

    if rainfall_change_percent < 0:
        rainfall_penalty = (
            abs(rainfall_change_percent) * 0.12
        )

    elif rainfall_change_percent > 30:
        rainfall_penalty = (
            (rainfall_change_percent - 30) * 0.05
        )

    # Better irrigation can partially offset water stress.
    irrigation_benefit = max(
        0.0,
        irrigation_change_percent * 0.08
    )

    # Excess fertilizer does not automatically increase yield.
    fertilizer_effect = 0.0

    if fertilizer_change_percent < -30:
        fertilizer_effect = (
            fertilizer_change_percent * 0.05
        )

    elif fertilizer_change_percent > 0:
        fertilizer_effect = min(
            fertilizer_change_percent * 0.03,
            10.0
        )

    total_yield_change_percent = (
        -temperature_penalty
        -rainfall_penalty
        +irrigation_benefit
        +fertilizer_effect
    )

    # Limit extreme outputs.
    total_yield_change_percent = max(
        -60.0,
        min(total_yield_change_percent, 20.0)
    )

    scenario_yield = (
        baseline_yield_kg_per_ha
        * (
            1
            + total_yield_change_percent / 100
        )
    )

    scenario_yield = max(
        0.0,
        scenario_yield
    )

    # --------------------------------------------------------
    # Water usage
    # --------------------------------------------------------

    scenario_water = (
        baseline_water_liters
        * (
            1 + irrigation_change_percent / 100
        )
    )

    scenario_water = max(
        0.0,
        scenario_water
    )

    # --------------------------------------------------------
    # Profit impact
    # --------------------------------------------------------

    yield_ratio = (
        scenario_yield /
        max(baseline_yield_kg_per_ha, 0.1)
    )

    scenario_profit = (
        baseline_profit * yield_ratio
    )

    # --------------------------------------------------------
    # Sustainability impact
    # --------------------------------------------------------

    sustainability_change = 0.0

    sustainability_change -= (
        abs(rainfall_change_percent) * 0.05
    )

    sustainability_change -= (
        max(0.0, fertilizer_change_percent) * 0.08
    )

    sustainability_change += (
        max(0.0, irrigation_change_percent) * 0.05
    )

    scenario_sustainability = (
        baseline_sustainability_score
        + sustainability_change
    )

    scenario_sustainability = round(
        max(
            0.0,
            min(scenario_sustainability, 100.0)
        ),
        2
    )

    # --------------------------------------------------------
    # Climate risk
    # --------------------------------------------------------

    climate = calculate_climate_risk(
        crop=crop,
        avg_temp_c=avg_temp_c,
        rainfall_mm=rainfall_mm,
        temperature_change=temperature_change,
        rainfall_change_percent=rainfall_change_percent
    )

    # --------------------------------------------------------
    # Comparison
    # --------------------------------------------------------

    yield_change = (
        scenario_yield
        - baseline_yield_kg_per_ha
    )

    profit_change = (
        scenario_profit
        - baseline_profit
    )

    water_change = (
        scenario_water
        - baseline_water_liters
    )

    sustainability_change_actual = (
        scenario_sustainability
        - baseline_sustainability_score
    )

    # --------------------------------------------------------
    # Decision interpretation
    # --------------------------------------------------------

    if (
        scenario_profit > baseline_profit
        and scenario_sustainability >=
        baseline_sustainability_score
    ):
        decision = (
            "Scenario is financially and environmentally favorable."
        )

    elif scenario_profit > baseline_profit:
        decision = (
            "Scenario improves estimated profit but should be "
            "checked for sustainability trade-offs."
        )

    elif scenario_yield > baseline_yield_kg_per_ha:
        decision = (
            "Scenario improves yield but does not improve "
            "estimated profitability."
        )

    else:
        decision = (
            "Baseline scenario is preferable under the current "
            "assumptions."
        )

    return {
        "crop": crop,
        "scenario": {
            "temperature_change": temperature_change,
            "rainfall_change_percent": rainfall_change_percent,
            "irrigation_change_percent": irrigation_change_percent,
            "fertilizer_change_percent": fertilizer_change_percent
        },
        "baseline": {
            "yield_kg_per_ha": round(
                baseline_yield_kg_per_ha,
                2
            ),
            "profit": round(
                baseline_profit,
                2
            ),
            "water_liters": round(
                baseline_water_liters,
                2
            ),
            "sustainability_score": round(
                baseline_sustainability_score,
                2
            )
        },
        "scenario_result": {
            "yield_kg_per_ha": round(
                scenario_yield,
                2
            ),
            "profit": round(
                scenario_profit,
                2
            ),
            "water_liters": round(
                scenario_water,
                2
            ),
            "sustainability_score": scenario_sustainability
        },
        "change": {
            "yield_change_kg_per_ha": round(
                yield_change,
                2
            ),
            "profit_change": round(
                profit_change,
                2
            ),
            "water_change_liters": round(
                water_change,
                2
            ),
            "sustainability_change": round(
                sustainability_change_actual,
                2
            )
        },
        "climate_risk": climate,
        "decision": decision
    }