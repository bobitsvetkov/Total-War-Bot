from discord.ext import commands

class CommandsListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='commands')
    async def list_commands(self, ctx):
        commands_list = [f"`{command.name}`: {command.help}" for command in self.bot.commands]
        commands_message = "Here are the available commands:\n" + "\n".join(commands_list)
        await ctx.send(commands_message)

def setup(bot):
    bot.add_cog(CommandsListCog(bot))
