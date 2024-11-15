import pytest
import discord
from unittest.mock import MagicMock, patch, AsyncMock
from discord.ext import commands
from cogs.tier_list.tier_list import TierList
import os


@pytest.fixture
def bot():
    bot = MagicMock(spec=commands.Bot)
    return bot


@pytest.fixture
def cog(bot):
    return TierList(bot)


@pytest.fixture
def ctx():
    ctx = MagicMock(spec=commands.Context)
    ctx.send = AsyncMock()
    return ctx


# Test when the image exists
@pytest.mark.asyncio
@patch("os.path.exists")
async def test_send_tierlist_image_found(mock_exists, cog, ctx):
    mock_exists.return_value = True

    image_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "images",
        "3v3 Tier List.png",
    )
    image_path = os.path.abspath(image_path)

    command = cog.send_tierlist.callback
    await command(cog, ctx)


    ctx.send.assert_called_once()

    call_args = ctx.send.call_args[1]["file"]
    assert isinstance(call_args, discord.File)
    assert call_args.filename == "3v3 Tier List.png"


# Test when the image does not exist
@pytest.mark.asyncio
@patch("os.path.exists")
async def test_send_tierlist_image_not_found(mock_exists, cog, ctx):
    mock_exists.return_value = False

    command = cog.send_tierlist.callback
    await command(cog, ctx)

    ctx.send.assert_called_once_with("Tier list image not found!")
