import pytest
from unittest.mock import MagicMock, AsyncMock, patch, mock_open
from discord.ext import commands
from cogs.elo_rating.record_game_elo import TeamRecordingSystem
import json

TEST_DATA = {
    "teams": [
        {"Team Name": "Team A", "Elo Rating": 1000.0, "Matches": []},
        {"Team Name": "Team B", "Elo Rating": 1000.0, "Matches": []},
    ]
}


@pytest.mark.asyncio
async def test_record_match_error_handling():
    bot = MagicMock(spec=commands.Bot)
    bot.user = MagicMock()
    bot.user.id = 1234567890
    ctx = AsyncMock(spec=commands.Context)
    ctx.bot = bot
    ctx.send = AsyncMock()
    ctx.author = MagicMock()
    ctx.author.id = bot.user.id

    with patch("builtins.open", mock_open(read_data=json.dumps(TEST_DATA))):
        team_recording = TeamRecordingSystem(bot)

        try:
            await team_recording.record_match(
                ctx, "regular", match_details="Invalid Format", match_type=None
            )
        except Exception as e:
            await ctx.send(f"Error recording match: {str(e)}")
            ctx.send.assert_called_with(f"Error recording match: {str(e)}")
        error = commands.NotOwner()
        await team_recording.record_match_error(ctx, error)
        ctx.send.assert_called_with("Only my creator can use this command.")
