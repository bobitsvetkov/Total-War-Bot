from functools import lru_cache
from typing import Dict, Any, Tuple
import logging
from utils.data_loader import load_factions_from_data, load_faction_modifiers

factions = load_factions_from_data('data/units_stats.json')
modifiers = load_faction_modifiers('data/faction_modifiers.json')




@lru_cache(maxsize=32)
def analyze_faction_weights(faction_units: Tuple[Dict[str, Any]], faction_name: str) -> Dict[str, float]:
    """
    Analyze faction units and calculate weighted stats.
    Returns a dictionary with survivability, melee_strength, and ranged_strength values.
    """
    if not faction_units:
        logging.warning("No units provided for analysis")
        return {"survivability": 0.00, "melee_strength": 0.00,
                "ranged_strength": 0.00, "cavalry_prowess": 0.00,
                "pilla_prowess": 0.00}

    # Initialize stats
    faction_stats = {
    "survivability": 0.0,
    "melee_strength": 0.0,
    "ranged_strength": 0.0,
    "cavalry_prowess": 0.0,
    "pilla_prowess": 0.0
}

    # Convert tuple of units to list of dicts
    faction_units_dicts = [dict(unit) for unit in faction_units]
    total_units = len(faction_units_dicts)
    missile_units = sum(1 for unit in faction_units_dicts if unit.get("Base Missile Damage", 0) > 0)


    cavalry_units = [unit for unit in faction_units_dicts if unit.get("Class") in ["Shock Cavalry", "Melee Cavalry"]]
    for unit in cavalry_units:
        faction_stats["cavalry_prowess"] += (
            unit.get("Charge Bonus", 0) + unit.get("Melee Attack", 0) + unit.get("Armor", 0)
    )

    pilla_units = [unit for unit in faction_units_dicts if 0 < unit.get("Range", 0) <= 80]
    for unit in pilla_units:
        faction_stats["pilla_prowess"] += (
            unit.get("Missile Damage", 0) + unit.get("AP Damage", 0) + unit.get("Ammo", 0)
        )
    # Calculate base stats
    for unit in faction_units_dicts:
        # Calculate weighted stats
        faction_stats["survivability"] += unit.get("Armor", 0)
        + unit.get("HP", 0) + unit.get("Morale", 0)
        + unit.get("Missile Block Chance", 0) + unit.get("Melee Defense")
        
        faction_stats["melee_strength"] += unit.get("Melee Attack", 0)
        + unit.get("Base Damage", 0) + unit.get("Charge Bonus", 0)
        + unit.get("AP Damage", 0) + unit.get("Bonus vs Infantry")
        
        if unit.get("Range", 0) > 80:
            faction_stats["ranged_strength"] += unit.get("Base Missile Damage", 0)
            + unit.get("Accuracy", 0) + unit.get("AP Missile Damage", 0)
            + unit.get("Range", 0) + unit.get("Ammo", 0)

    # Apply faction modifiers
    faction_modifier = modifiers.get(faction_name, {"survivability": 1.0, "melee_strength": 1.0, "ranged_strength": 1.0, "cavalry_prowess": 1.0, "pilla_prowess": 1.0})

    try:
         final_stats = {
            "survivability": round((faction_stats["survivability"] / total_units) * faction_modifier["survivability"], 2),
            "melee_strength": round((faction_stats["melee_strength"] / total_units) * faction_modifier["melee_strength"], 2),
            "ranged_strength": round((faction_stats["ranged_strength"] / missile_units) * faction_modifier["ranged_strength"], 2) if missile_units > 0 else 0.00,
            "cavalry_prowess": round((faction_stats["cavalry_prowess"] / len(cavalry_units)) * faction_modifier["cavalry_prowess"], 2) if cavalry_units else 0.00,
            "pilla_prowess": round((faction_stats["pilla_prowess"] / len(pilla_units)) * faction_modifier["pilla_prowess"], 2) if pilla_units else 0.00
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


def calculate_all_faction_stats(factions: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """Calculate and return stats for all factions."""
    all_factions_stats = {}

    for faction_name, faction_units in factions.items():
        units_tuple = tuple(make_hashable_unit(unit) for unit in faction_units)
        faction_stats = analyze_faction_weights(units_tuple, faction_name)
        all_factions_stats[faction_name] = faction_stats

    return all_factions_stats
