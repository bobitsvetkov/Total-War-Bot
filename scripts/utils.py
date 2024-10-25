from functools import lru_cache
from typing import Dict, Any, Tuple
import logging
# Define weights and special units here
WEIGHTS = {
            "tankiness": {
                "Missile Block Chance": 17.0,
                "HP": 20.0,
                "Armor": 8.0,
                "Morale": 6.0,
                "Melee Defense": 8.0,
            },
            "melee": {
                "Melee Attack": 20.0,
                "Base Damage": 10.0,
                "AP Damage": 13.0,
                "Charge Bonus": 7.0,
                'Bonus vs Infantry': 12.0,
                'Bonus vs Large': 10.0,
            },
            "ranged": {
                "Base Missile Damage": 2.0,
                "AP Missile Damage": 4.0,
                "Total Missile Damage": 4.0,
                "Ammo": 15.0,
                "Accuracy": 2.0,
                "Range": 15.0
            }
}

SPECIAL_UNITS = {
    "Mercenary Cretan Archers": {
        "ranged_strength": 5.0
    },
    "Cretan Archers": {
        "ranged_strength": 5.0
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
        "ranged_strength": 5.0
    },
    "Syrian Heavy Archers": {
        "ranged_strength": 5.0
    },
    "Cimmerian Heavy Archers": {
        "ranged_strength": 3.0
    },
    "Nabataean Heavy Archers": {
        "ranged_strength": 5.0
    },
    "Auxiliary Syrian Archers": {
        "ranged_strength": 5.0
    },
    "Mercenary Rhodian Slingers": {
        "ranged_strength": 5.0
    },
    "Thracian Nobles": {
        "melee_strength": 10.0,
    },
    "Auxiliary Balearic Slingers": {
        "ranged_strength": 5.0,
    },
    "Mercenary Balearic Slingers": {
        "ranged_strength": 5.0,
    },
    "Mercenary Syrian Archers": {
        "ranged_strength": 5.0,
    },
    "Balearic Slingers": {
        "ranged_strength": 5.0,
    },
    "Veteran Shield Warriors": {
        "melee_strength": 4.0,
    },
    "Galatian Legionaries": {
        "melee_strength": 4.0,
        "tankiness": 2.0
    },
    "Chosen Sword Band": {
        "melee_strength": 2.5,
        "tankiness": 1.0
    },
    "Briton Slingers": {
        "ranged_strength": 3.0,
    },
    "Chosen Swordsmen": {
        "melee_strength": 3.0,
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

