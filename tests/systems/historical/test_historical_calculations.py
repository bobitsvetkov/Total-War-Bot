import pytest
from unittest.mock import patch
import discord


def test_calculate_player_rating(historical_results, sample_player_data):
    """Test player rating calculation."""
    rating = historical_results.calculate_player_rating(sample_player_data)
    assert isinstance(rating, float)
    assert rating > 0


def test_generate_leaderboard(historical_results, sample_player_data):
    """Test generating the leaderboard."""
    with patch("utils.data_loader.load_player_data", return_value=[sample_player_data]):
        leaderboard = historical_results.generate_leaderboard()
    assert isinstance(leaderboard, list)
    assert len(leaderboard) > 0
    assert all("Player" in entry for entry in leaderboard)
    assert all(isinstance(entry["Rating"], float) for entry in leaderboard)


@pytest.mark.asyncio
async def test_display_leaderboard(historical_results, mock_ctx):
    """Test leaderboard display functionality."""
    test_leaderboard = [
        {"Player": "Player1", "Rating": 1500, "Games Played": 50},
        {"Player": "Player2", "Rating": 1400, "Games Played": 45},
    ]
    await historical_results.display_leaderboard(
        mock_ctx, "Test Leaderboard", test_leaderboard, "Rating"
    )
    mock_ctx.send.assert_called_once()
    call_args = mock_ctx.send.call_args[1]
    assert "embed" in call_args
    embed = call_args["embed"]
    assert isinstance(embed, discord.Embed)
    assert embed.title == "Test Leaderboard"
    assert len(embed.fields) == len(test_leaderboard)
