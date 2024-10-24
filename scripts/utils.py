from functools import lru_cache
from typing import Dict, Any, Tuple
import logging
# Define weights and special units here
WEIGHTS = {
            "tankiness": {
                "Missile Block Chance": 4.0,
                "HP": 4.0,
                "Armor": 5.0,
                "Morale": 5.0,
                "Melee Defense": 4.0,
            },
            "melee": {
                "Melee Attack": 20.0,
                "Base Damage": 2.5,
                "AP Damage": 2.7,
                "Weapon Damage": 2.4,
                "Charge Bonus": 10,
                'Bonus vs Infantry': 100,
                'Bonus vs Large': 20,
            },
            "ranged": {
                "Base Missile Damage": 3.7,
                "AP Missile Damage": 3.7,
                "Total Missile Damage": 3.7,
                "Ammo": 5.0,
                "Accuracy": 2.0,
                "Range": 5.0
            }
}

SPECIAL_UNITS = {
    "Mercenary Cretan Archers": {
        "ranged_strength": 3.0
    },
    "Cretan Archers": {
        "ranged_strength": 3.0
    },
    "Evocati Cohort": {
        "melee_strength": 3.0,
        "tankiness": 3.0
    },
    "Tribal Warriors": {
        "melee_strength": 3.0
    },
    "Sword Follower": {
        "melee_strength": 3.0
    },
    "Rhodian Slingers": {
        "ranged_strength": 3.0
    },
    "Cimmerian Heavy Archers": {
        "ranged_strength": 5.0
    },
    "Auxiliary Syrian Archers": {
        "ranged_strength": 3.0
    },
    "Mercenary Rhodian Slingers": {
        "ranged_strength": 3.0
    },
    "Thracian Nobles": {
        "melee_strength": 10.0
    },
    "Auxiliary Balearic Slingers": {
        "ranged_strength": 3.0,
    },
    "Mercenary Balearic Slingers": {
        "ranged_strength": 3.0,
    }
}

@lru_cache(maxsize=32)
def analyze_faction_weights(faction_units: Tuple[Tuple[str, Any]]) -> Dict[str, Any]:
    faction_stats = {"tankiness": 0, "melee_strength": 0, "ranged_strength": 0}
    faction_units_dicts = [dict(unit) for unit in faction_units]
    
    special_unit_multipliers = {
        "tankiness": 1.0,
        "melee_strength": 1.0,
        "ranged_strength": 1.0
    }

    for unit in faction_units_dicts:
        unit_name = unit.get("Unit", "")
        if unit_name in SPECIAL_UNITS:
            for stat_type, multiplier in SPECIAL_UNITS[unit_name].items():
                special_unit_multipliers[stat_type] = max(
                    special_unit_multipliers[stat_type],
                    multiplier
                )
        else:
            logging.info(f"No special multipliers for {unit_name}")

    missile_units = sum(bool(unit.get("Base Missile Damage", 0)) for unit in faction_units_dicts)
    total_units = len(faction_units_dicts)

    for unit in faction_units_dicts:
        faction_stats["tankiness"] += sum(unit.get(stat, 0) * weight 
                                            for stat, weight in WEIGHTS["tankiness"].items())
        faction_stats["melee_strength"] += sum(unit.get(stat, 0) * weight 
                                                 for stat, weight in WEIGHTS["melee"].items())
        
        if unit.get("Base Missile Damage", 0) > 0:
            faction_stats["ranged_strength"] += sum(unit.get(stat, 0) * weight 
                                                      for stat, weight in WEIGHTS["ranged"].items())
    
    if total_units > 0:
        faction_stats = {
            "tankiness": int((faction_stats["tankiness"] // total_units) * special_unit_multipliers["tankiness"]),
            "melee_strength": int((faction_stats["melee_strength"] // total_units) * special_unit_multipliers["melee_strength"]),
            "ranged_strength": int((faction_stats["ranged_strength"] // missile_units) * special_unit_multipliers["ranged_strength"]) if missile_units > 0 else 0,
        }
    return faction_stats

def make_hashable_unit(unit: dict) -> Tuple[Tuple[str, Any], ...]:
        """Convert a unit dict into a hashable form by recursively making all nested dicts/lists hashable."""
        def make_hashable(item):
            if isinstance(item, dict):
                return tuple((k, make_hashable(v)) for k, v in sorted(item.items()))
            elif isinstance(item, list):
                return tuple(make_hashable(i) for i in item)
            return item
        
        return tuple(sorted((k, make_hashable(v)) for k, v in unit.items()))

