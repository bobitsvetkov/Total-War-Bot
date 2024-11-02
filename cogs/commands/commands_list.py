from discord.ext import commands

class CommandsList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='commands')
    async def list_commands(self, ctx):
        """Display a list with all of the bot commands"""
        commands_list = [f"`{command.name}`: {command.help}" for command in self.bot.commands]
        commands_message = "Here are the available commands:\n" + "\n".join(commands_list)
        await ctx.send(commands_message)
