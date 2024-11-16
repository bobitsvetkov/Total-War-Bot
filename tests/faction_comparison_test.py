import pytest
from unittest.mock import Mock, patch
from discord.ext import commands
from cogs.faction_comparison.faction_comparison import FactionComparison


@pytest.fixture
def mock_stats():
    return {
        "Rome": {
            "survivability": 75,
            "melee_strength": 88.08,
            "ranged_strength": 45,
            "cavalry_prowess": 60,
            "pilla_prowess": 50,
        },
        "Odrysian Kingdom": {
            "survivability": 70,
            "melee_strength": 80.08,
            "ranged_strength": 40,
            "cavalry_prowess": 55,
            "pilla_prowess": 45,
        },
    }


@pytest.fixture
def faction_cog(mock_stats):
    with patch("utils.unit_performance.analyze_faction_weights") as mock_analyze:
        mock_analyze.side_effect = lambda faction_name: mock_stats[faction_name]
        bot = Mock(spec=commands.Bot)
        cog = FactionComparison(bot)
        bot.add_cog = Mock()
        return cog


@pytest.mark.asyncio
async def test_compare_factions(faction_cog, mock_stats):
    result = await faction_cog.compare_factions("Rome", "Odrysian Kingdom")
    assert "Comparison between Rome and Odrysian Kingdom" in result

    melee_strength_diff = abs(
        mock_stats["Rome"]["melee_strength"]
        - mock_stats["Odrysian Kingdom"]["melee_strength"]
    )

    assert melee_strength_diff > 0
    result = await faction_cog.compare_factions("Invalid", "Rome")
    assert "not found" in result
