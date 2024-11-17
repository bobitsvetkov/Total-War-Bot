import pytest
from unittest.mock import AsyncMock, MagicMock
from discord.ext import commands
from cogs.faction_analysis.bot import FactionAnalysisBot


@pytest.mark.asyncio
async def test_faction_analysis_command():
    bot = MagicMock(spec=commands.Bot)
    ctx = AsyncMock(spec=commands.Context)
    ctx.send = AsyncMock()

    faction_bot = FactionAnalysisBot(bot)
    faction_bot.all_factions_stats = {
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

    faction_bot.get_or_generate_analysis = AsyncMock(
        return_value="Odrysian Kingdom is a balanced faction."
    )

    command_callback = faction_bot.faction_analysis_command.callback

    await command_callback(faction_bot, ctx, faction_name="Odrysian Kingdom")

    assert len(ctx.send.call_args_list) == 2, "Expected exactly 2 messages to be sent"

    calls = ctx.send.call_args_list
    assert calls[0][0][0] == "**Analysis for Odrysian Kingdom:**"
    assert calls[1][0][0] == "Odrysian Kingdom is a balanced faction."
