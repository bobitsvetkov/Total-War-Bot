import pytest
from unittest.mock import Mock, AsyncMock
from discord.ext import commands
from cogs.commands.commands_list import CommandsList

@pytest.fixture
def bot():
    return Mock(spec=commands.Bot)

@pytest.fixture
def cog(bot):
    return CommandsList(bot)

@pytest.mark.asyncio
async def test_list_commands(cog, bot):
    bot.commands = [
        Mock(name='command1', help='Command 1 description'),
        Mock(name='command2', help='Command 2 description'),
        Mock(name='command3', help='Command 3 description')
    ]

    ctx = Mock(spec=commands.Context)
    ctx.send = AsyncMock()

    command = cog.list_commands.callback
    await command(cog, ctx)

    expected_message = f"Here are the available commands:\n" \
                    f"`{bot.commands[0].name}`: {bot.commands[0].help}\n" \
                    f"`{bot.commands[1].name}`: {bot.commands[1].help}\n" \
                    f"`{bot.commands[2].name}`: {bot.commands[2].help}"
    ctx.send.assert_called_once_with(expected_message)