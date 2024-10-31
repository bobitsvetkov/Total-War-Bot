import json
import os
from typing import List, Dict, Any

def load_unit_data() -> List[Dict[str, Any]]:
    """Load unit data from a JSON file."""
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'units_stats.json')
    with open(json_path, 'r') as f:
        return json.load(f)
    
def load_player_data() -> List[Dict[str, Any]]:
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'player_stats_historical.json')
    with open(json_path, 'r') as f:
        return json.load(f)

def load_elo_data() -> List[Dict[str, Any]]:
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'elo_rating.json')
    with open(json_path, 'r') as f:
        return json.load(f)
    
def load_factions_from_data(file_path: str):
    """Extracts unique faction names from units_stats.json."""
    with open(file_path, 'r') as f:
        units_data = json.load(f)
    return list({unit["Faction"] for unit in units_data})

def load_faction_modifiers(file_path: str) -> Dict[str, Dict[str, float]]:
    """Load faction modifiers data from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)