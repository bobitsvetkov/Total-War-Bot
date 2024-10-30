from functools import lru_cache
from typing import Dict, Any, Tuple
import logging
import json
from utils.faction_modifiers import FACTION_MODIFIERS

def load_factions_from_data(file_path: str):
    """Extracts unique faction names from units_stats.json."""
    with open(file_path, 'r') as f:
        units_data = json.load(f)
    return list({unit["Faction"] for unit in units_data})

# Example use
factions = load_factions_from_data('data/units_stats.json')




@lru_cache(maxsize=32)
def analyze_faction_weights(faction_units: Tuple[Dict[str, Any]], faction_name: str) -> Dict[str, float]:
    """
    Analyze faction units and calculate weighted stats.
    Returns a dictionary with survivability, melee_strength, and ranged_strength values.
    """
    if not faction_units:
        logging.warning("No units provided for analysis")
        return {"survivability": 0.00, "melee_strength": 0.00, "ranged_strength": 0.00}

    # Initialize stats
    faction_stats = {"survivability": 0.0, "melee_strength": 0.0, "ranged_strength": 0.0}
    
    # Convert tuple of units to list of dicts
    faction_units_dicts = [dict(unit) for unit in faction_units]
    total_units = len(faction_units_dicts)
    missile_units = sum(1 for unit in faction_units_dicts if unit.get("Base Missile Damage", 0) > 0)

    # Calculate base stats
    for unit in faction_units_dicts:
        # Calculate weighted stats
        faction_stats["survivability"] += unit.get("Armor", 0)
        + unit.get("HP", 0) + unit.get("Morale", 0)
        + unit.get("Missile Block Chance", 0) + unit.get("Melee Defense")
        
        faction_stats["melee_strength"] += unit.get("Melee Attack", 0)
        + unit.get("Base Damage", 0) + unit.get("Charge Bonus", 0)
        + unit.get("AP Damage", 0) + unit.get("Bonus vs Infantry")
        
        if unit.get("Range", 0) >= 80:
            faction_stats["ranged_strength"] += unit.get("Base Missile Damage", 0)
            + unit.get("Accuracy", 0) + unit.get("AP Missile Damage", 0)
            + unit.get("Range", 0) + unit.get("Ammo", 0)

    # Apply faction modifiers
    faction_modifier = FACTION_MODIFIERS.get(faction_name, {"survivability": 1.0, "melee_strength": 1.0, "ranged_strength": 1.0})

    try:
        final_stats = {
            "survivability": round((faction_stats["survivability"] / total_units) * faction_modifier["survivability"], 2),
            "melee_strength": round((faction_stats["melee_strength"] / total_units) * faction_modifier["melee_strength"], 2),
            "ranged_strength": round((faction_stats["ranged_strength"] / missile_units) * faction_modifier["ranged_strength"], 2) if missile_units > 0 else 0.00
        }
    except ZeroDivisionError as e:
        logging.error(f"Division by zero error when calculating stats: {e}")
        return {"survivability": 0.00, "melee_strength": 0.00, "ranged_strength": 0.00}
    except Exception as e:
        logging.error(f"Unexpected error when calculating faction stats: {e}")
        raise

    logging.info(f"Final faction stats for {faction_name}: {final_stats}")
    return final_stats

def make_hashable_unit(unit: dict) -> Tuple[Tuple[str, Any], ...]:
    """Convert a unit dict into a hashable form by recursively making all nested dicts/lists hashable."""
    def make_hashable(item):
        if isinstance(item, dict):
            return tuple((k, make_hashable(v)) for k, v in sorted(item.items()))
        elif isinstance(item, list):
            return tuple(make_hashable(i) for i in item)
        return item

    return tuple(sorted((k, make_hashable(v)) for k, v in unit.items()))
