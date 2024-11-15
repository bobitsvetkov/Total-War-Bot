import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from discord.ext import commands
from cogs.land_guide.land_guide_command import (
    LandGuidePlaylist,
)


@pytest.fixture
def bot():
    bot = MagicMock(spec=commands.Bot)
    bot.wait_for = AsyncMock()
    return bot


@pytest.fixture
def cog(bot):
    return LandGuidePlaylist(bot)


@pytest.fixture
def ctx(bot):
    ctx = MagicMock(spec=commands.Context)
    ctx.send = AsyncMock()
    ctx.bot = bot
    return ctx


@pytest.mark.asyncio
@patch("googleapiclient.discovery.build")
async def test_land_guide_playlist_video_found(mock_build, cog, ctx):
    mock_youtube = MagicMock()
    mock_playlist = MagicMock()
    mock_request = MagicMock()
    mock_request.execute.return_value = {
        "items": [
            {"snippet": {"title": "Carthage Guide", "resourceId": {"videoId": "12345"}}}
        ]
    }
    mock_youtube.playlistItems.return_value = mock_playlist
    mock_playlist.list.return_value = mock_request
    mock_build.return_value = mock_youtube

    mock_message = MagicMock()
    mock_message.content = "Carthage"
    ctx.bot.wait_for.return_value = mock_message

    command = cog.land_guide_playlist.callback
    await command(cog, ctx)

    assert len(ctx.send.call_args_list) >= 2, "Expected at least 2 calls to ctx.send"

    first_call = ctx.send.call_args_list[0]
    first_call_message = (
        first_call.args[0].replace("‘", "'").replace("’", "'")
    )
    assert "Please enter the faction you need help with:" == first_call_message

    second_call = ctx.send.call_args_list[1]
    second_call_message = (
        second_call.args[0].replace("‘", "'").replace("’", "'")
    )
    assert "Here's a guide for **carthage**:" in second_call_message
    assert "https://www.youtube.com/watch?v=inKpoTFPiRg" in second_call_message