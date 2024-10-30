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
