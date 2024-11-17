import pytest
from unittest.mock import Mock, AsyncMock
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
def mock_ctx():
    """Mock the Discord context object."""
    ctx = Mock(spec=commands.Context)
    ctx.send = AsyncMock()
    ctx.author = Mock(name="Author")
    ctx.guild = Mock(name="Guild")
    return ctx


@pytest.fixture
def sample_player_data() -> Dict[str, Any]:
    """Provide sample player data for tests."""
    return {
        "Player": "Bobi",
        "K/D ratio": 1.01,
        "Chevrons/game": 7.95,
    }