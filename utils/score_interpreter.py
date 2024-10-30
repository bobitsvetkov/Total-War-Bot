def interpret_score(stat_value: float, stat_type: str) -> str:
    """Interpret a stat value for descriptive feedback based on a 0-100 scoring system."""
    thresholds = {
        "Survivability": [(0, "very fragile"), (30.00, "fragile"), (50, "adequate"), (70, "resilient"), (90, "formidable"), (100, "unbreakable")],
        "Melee": [(0, "very underpowered"), (30.00, "underpowered"), (50, "balanced"), (70, "potent"), (90, "dominant"), (100, "unstoppable")],
        "Ranged": [(0, "very limited"), (30.00, "limited"), (50, "effective"), (70, "deadly"), (90, "lethal"), (100, "masterful")]
    }
    
    for threshold, descriptor in thresholds.get(stat_type, []):
        if stat_value <= threshold:
            return f"The {stat_type.lower()} is {descriptor}."
    
    return f"The {stat_type.lower()} is outstanding."
