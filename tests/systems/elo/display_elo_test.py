import pytest
from unittest.mock import AsyncMock, Mock
from utils.intents import setup_intents
from discord.ext import commands
from cogs.elo_rating.display_elo import TeamDisplaySystem
from utils.data_loader import load_elo_data

@pytest.fixture
def bot():
    """Create a test bot instance with intents."""
    intents = setup_intents()
    bot = commands.Bot(command_prefix="!", intents=intents)

    bot.login = AsyncMock()
    bot.run = AsyncMock()
    bot.wait_until_ready = AsyncMock()

    return bot


@pytest.fixture
def mock_ctx(bot):
    """Create a mock context for Discord commands."""
    ctx = Mock(spec=commands.Context)
    ctx.bot = bot
    ctx.guild = Mock()
    ctx.channel = Mock()
    ctx.author = Mock()
    ctx.message = Mock()
    ctx.send = AsyncMock()
    ctx.view = Mock()
    return ctx


@pytest.fixture
def sample_team_data():
    """Provide sample team data for testing."""
    return load_elo_data()


@pytest.mark.asyncio
async def test_show_top_teams_success(bot, mock_ctx, sample_team_data):
    """Test successful execution of the show_top_teams command."""
    sorted_teams = sorted(
        sample_team_data["teams"], key=lambda x: x["Elo Rating"], reverse=True
    )
    top_10_teams = sorted_teams[:10]

    cog = TeamDisplaySystem(bot)
    await bot.add_cog(cog)
    await bot.wait_until_ready()

    command = bot.get_command("display_team_elo")
    if command:
        await command.invoke(mock_ctx)
    else:
        print("Command not found")

    mock_ctx.send.assert_called_once()

    embed = mock_ctx.send.call_args[1]["embed"]
    assert embed.title == "Top 10 Teams by Elo Rating"
    assert len(embed.fields) == len(top_10_teams)

    for idx, team in enumerate(top_10_teams):
        assert embed.fields[idx].name == team["Team Name"]
        assert embed.fields[idx].value == f"Elo Rating: {team['Elo Rating']:.2f}"
