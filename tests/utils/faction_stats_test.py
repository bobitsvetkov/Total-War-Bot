import pytest
import json
from utils.unit_performance import (
    analyze_faction_weights,
    make_hashable_unit,
    calculate_all_faction_stats,
)


@pytest.fixture(scope="module")
def faction_data():
    """Load data from JSON files and organize units by faction."""
    with open("data/units_stats.json", "r") as units_file:
        units_data = json.load(units_file)

    factions = {}
    for unit in units_data:
        faction_name = unit.get("Faction")
        if faction_name not in factions:
            factions[faction_name] = []
        factions[faction_name].append(unit)

    with open("data/faction_modifiers.json", "r") as modifiers_file:
        modifiers = json.load(modifiers_file)

    return factions, modifiers


def test_analyze_faction_weights(faction_data):
    factions, _ = faction_data

    rome_units = tuple(make_hashable_unit(unit) for unit in factions["Rome"])
    rome_stats = analyze_faction_weights(rome_units, "Rome")

    expected_rome_stats = {
        "survivability": 92.21,
        "melee_strength": 88.08,
        "ranged_strength": 88.4,
        "cavalry_prowess": 42.5,
        "pilla_prowess": 52.61,
    }

    for key, value in expected_rome_stats.items():
        assert rome_stats[key] == pytest.approx(value, rel=1e-2), f"{key} mismatch!"


@pytest.mark.parametrize("unit_key", ["Rome"])
def test_make_hashable_unit(faction_data, unit_key):
    factions, _ = faction_data
    unit = factions[unit_key][0]
    hashable_unit = make_hashable_unit(unit)
    assert isinstance(hashable_unit, tuple), "Unit is not converted to tuple!"


def test_calculate_all_faction_stats(faction_data):
    factions, _ = faction_data

    all_factions_stats = calculate_all_faction_stats(factions)
    rome_stats = all_factions_stats["Rome"]

    assert isinstance(rome_stats, dict), "Rome stats are not a dictionary!"
    assert "survivability" in rome_stats, "Survivability stat missing!"
    assert "melee_strength" in rome_stats, "Melee strength stat missing!"
    assert "ranged_strength" in rome_stats, "Ranged strength stat missing!"
    assert "cavalry_prowess" in rome_stats, "Cavalry prowess stat missing!"
    assert "pilla_prowess" in rome_stats, "Pilla prowess stat missing!"
