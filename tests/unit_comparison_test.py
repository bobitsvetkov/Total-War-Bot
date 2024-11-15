import pytest
from unittest.mock import patch, MagicMock
from discord.ext import commands
from cogs.unit_comparison.unit_comparison import UnitStatsComparison
from utils.intents import setup_intents


@pytest.fixture
def bot():
    intents = setup_intents()
    return commands.Bot(intents=intents, command_prefix="!")


@pytest.fixture
def cog(bot):
    return UnitStatsComparison(bot)

@pytest.fixture
def ctx():
    ctx = MagicMock(spec=commands.Context)
    ctx.send = MagicMock()
    return ctx

@pytest.fixture
def all_units_data():
    return [
        {
            "Unit": "Thracian Nobles",
            "Faction": "Odrysian Kingdom",
            "Melee Attack": 100,
            "AP Damage": 50,
        },
        {
            "Unit": "Oathsworn",
            "Faction": "Arverni",
            "Melee Attack": 80,
            "AP Damage": 40,
        },
    ]


@pytest.mark.asyncio
@patch("cogs.unit_comparison.unit_comparison.UnitStatsComparison.query_unit_stats")
async def test_unit_stats_for_each_unit(
    mock_query_unit_stats, cog, ctx, all_units_data
):
    """Test unit_stats command with each unit from the dataset."""

    async def mock_query(unit_name):
        return next(
            (
                unit
                for unit in all_units_data
                if unit["Unit"].lower() == unit_name.lower()
            ),
            None,
        )

    mock_query_unit_stats.side_effect = mock_query

    for unit_data in all_units_data:
        unit_name = unit_data["Unit"]

        await cog.query_unit_stats(unit_name=unit_name)
