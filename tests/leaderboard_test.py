import pytest
from unittest.mock import Mock, patch, AsyncMock
import discord
from discord.ext import commands
from typing import Dict, Any


@pytest.fixture
def bot():
    """Mock the Discord bot instance."""
    return Mock(spec=commands.Bot)


@pytest.fixture
def historical_results(bot):
    """Import and initialize the HistoricalResults cog."""
    from cogs.historical_results.historical_results import HistoricalResults

    return HistoricalResults(bot)


@pytest.fixture
def sample_player_data() -> Dict[str, Any]:
    """Provide sample player data for tests."""
    return {
        "Player": "Bobi",
        "K/D ratio": 1.01,
        "Chevrons/game": 7.95,
        "Total Chevrons": 175,
        "Total Kills": "43,582",
        "Total Losses": "43,190",
        "Kills per Game": "1,981",
        "Losses per Game": "1,963",
        "Games Played": 22,
        "Games Won": 17,
        "Games Lost": 7,
        "Win %": "70.8%",
        "DC's/Forfeits": 2,
        "Seasons Played": 3,
        "Playoff Appearances": 3,
        "Playoff Rate": "100.0%",
        "Third Places": "",
        "Runner-ups": "",
        "Championships": 1,
        "Top 3 Best KD Ratios": "",
        "Top 3 Most Chevrons/Game": "",
    }


@pytest.fixture
def mock_ctx():
    """Mock the Discord context object."""
    ctx = Mock(spec=commands.Context)
    ctx.send = AsyncMock()
    ctx.author = Mock(name="Author")
    ctx.guild = Mock(name="Guild")
    return ctx


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("75%", 75.0),
        ("0%", 0.0),
        ("100%", 100.0),
        (None, 0.0),
        ("", 0.0),
        ("invalid", 0.0),
        ("50.5%", 50.5),
    ],
)
def test_parse_percentage(historical_results, input_str, expected):
    """Test parsing percentage strings."""
    result = historical_results._parse_percentage(input_str)
    assert result == expected


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
async def test_show_player_history_found(
    historical_results, mock_ctx, sample_player_data
):
    """Test player history display when player is found."""
    with patch("utils.data_loader.load_player_data", return_value=[sample_player_data]):
        command = historical_results.show_player_history.callback
        await command(historical_results, mock_ctx, player_name="Bobi")

    # Verify that send was called
    assert mock_ctx.send.called

    # Get the arguments from the first call
    call_args = mock_ctx.send.call_args

    args, kwargs = call_args

    # Print for debugging
    print(f"Call args: {call_args}")
    print(f"Args: {args}")
    print(f"Kwargs: {kwargs}")

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
