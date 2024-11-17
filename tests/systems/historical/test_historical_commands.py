import pytest
from unittest.mock import patch
import discord


@pytest.mark.asyncio
async def test_show_player_history_found(
    historical_results, mock_ctx, sample_player_data
):
    """Test player history display when player is found."""
    with patch("utils.data_loader.load_player_data", return_value=[sample_player_data]):
        command = historical_results.show_player_history.callback
        await command(historical_results, mock_ctx, player_name="Bobi")
    assert mock_ctx.send.called
    call_args = mock_ctx.send.call_args
    args, kwargs = call_args
    assert "embed" in kwargs
    embed = kwargs["embed"]
    assert isinstance(embed, discord.Embed)
    assert embed.title == "Historical Results: Bobi"


@pytest.mark.asyncio
async def test_show_player_history_not_found(historical_results, mock_ctx):
    """Test player history display when player is not found."""
    with patch("utils.data_loader.load_player_data", return_value=[]):
        command = historical_results.show_player_history.callback
        await command(historical_results, mock_ctx, player_name="NonexistentPlayer")
    mock_ctx.send.assert_called_once_with(
        "No historical data found for player 'NonexistentPlayer'!"
    )


@pytest.mark.asyncio
async def test_command_historical_leaderboard(
    historical_results, mock_ctx, sample_player_data
):
    """Test the historical_leaderboard command."""
    with patch("utils.data_loader.load_player_data", return_value=[sample_player_data]):
        command = historical_results.show_leaderboard.callback
        await command(historical_results, mock_ctx)
    mock_ctx.send.assert_called_once()
    call_args = mock_ctx.send.call_args[1]
    assert "embed" in call_args
    embed = call_args["embed"]
    assert isinstance(embed, discord.Embed)
    assert embed.title == "Top Players Leaderboard"
