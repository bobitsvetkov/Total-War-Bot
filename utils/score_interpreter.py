def interpret_score(stat_value: int, stat_type: str) -> str:
    """Interpret a stat value for descriptive feedback."""
    thresholds = {
        "Tankiness": [(3100, "weak"), (3300, "average"), (float("inf"), "strong")],
        "Melee": [(2000, "weak"), (2600, "average"), (float("inf"), "strong")],
        "Ranged": [(2000, "poor"), (3500, "decent"), (float("inf"), "impressive")]
    }
    for threshold, descriptor in thresholds.get(stat_type, []):
        if stat_value <= threshold:
            return f"The {stat_type.lower()} is {descriptor}."
    return f"Unknown stat type: {stat_type}"
