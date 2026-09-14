# ============================================================
# AGRITWIN AI - DECISION REPLAY & FEEDBACK ENGINE
# ============================================================


def calculate_decision_accuracy(
    predicted_value,
    actual_value
):
    """
    Calculate percentage error and a simple accuracy indicator.
    """

    if predicted_value is None or actual_value is None:
        return {
            "percentage_error": None,
            "accuracy": None
        }

    if actual_value == 0:

        if predicted_value == 0:
            accuracy = 100.0
        else:
            accuracy = 0.0

        return {
            "percentage_error": None,
            "accuracy": accuracy
        }

    percentage_error = (
        abs(actual_value - predicted_value)
        / abs(actual_value)
    ) * 100

    accuracy = max(
        0.0,
        100.0 - percentage_error
    )

    return {
        "percentage_error": round(
            percentage_error,
            2
        ),
        "accuracy": round(
            accuracy,
            2
        )
    }


def build_decision_replay(
    recommendation_id,
    decision_taken,
    predicted_yield,
    actual_yield,
    predicted_water,
    actual_water,
    predicted_profit,
    actual_profit,
    notes=None
):
    """
    Compare predicted outcomes with actual outcomes.
    """

    yield_result = calculate_decision_accuracy(
        predicted_yield,
        actual_yield
    )

    water_result = calculate_decision_accuracy(
        predicted_water,
        actual_water
    )

    profit_result = calculate_decision_accuracy(
        predicted_profit,
        actual_profit
    )

    return {
        "recommendation_id": recommendation_id,
        "decision_taken": decision_taken,
        "yield_comparison": yield_result,
        "water_comparison": water_result,
        "profit_comparison": profit_result,
        "notes": notes
    }