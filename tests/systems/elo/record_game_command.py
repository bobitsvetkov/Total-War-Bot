import pytest

def test_calculate_expected_score(team_recording_system):
    assert team_recording_system.calculate_expected_score(1000, 1000) == pytest.approx(
        0.5
    )
    assert team_recording_system.calculate_expected_score(1200, 1000) > 0.5
    assert team_recording_system.calculate_expected_score(800, 1000) < 0.5

def test_update_elo(team_recording_system):
    winning_team = {"Elo Rating": 1000.0}
    losing_team = {"Elo Rating": 1000.0}
    team_recording_system.update_elo(winning_team, losing_team)
    assert winning_team["Elo Rating"] > 1000.0
    assert losing_team["Elo Rating"] < 1000.0
