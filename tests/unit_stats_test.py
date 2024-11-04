import pytest
from unittest.mock import AsyncMock, Mock, patch
from discord.ext import commands
from cogs.unit_stats.unit_stats import UnitStats
from utils.data_loader import load_unit_data

@pytest.fixture(scope="module")
def all_units_data():
    return load_unit_data()

@pytest.fixture
def bot():
    return Mock(spec=commands.Bot)

@pytest.fixture
def cog(bot):
    return UnitStats(bot)

@pytest.fixture
def ctx():
    ctx = Mock(spec=commands.Context)
    ctx.send = AsyncMock()
    return ctx

@pytest.mark.asyncio
async def test_unit_stats_for_each_unit(cog, ctx, all_units_data):
    """Test unit_stats command with each unit from the dataset."""
    for unit_data in all_units_data:
        unit_name = unit_data["Unit"]

        print(f"Testing unit: {unit_name}")

        with patch("cogs.unit_stats.unit_stats.query_unit_stats", return_value=unit_data):
            command = cog.unit_stats.callback
            await command(cog, ctx, unit_name=unit_name)

            print(f"Mocked query_unit_stats returned: {unit_data}")
