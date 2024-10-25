import discord
from discord.ext import commands
from scripts.unit_stats_query import query_unit_stats
import logging

logging.basicConfig(level=logging.INFO)

class UnitStatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='unit_stats', help='Get information for a specified unit.')
    async def unit_stats(self, ctx, *, unit_name: str):
        logging.info(f"Received unit name: '{unit_name}'")
        unit_info = query_unit_stats(unit_name)
        if unit_info == "Unit not found":
            await ctx.send(unit_info)
        else:
            response = f"Information for {unit_name}:\n```"
            for key, value in unit_info.items():
                if key not in ['Unit', 'Soldiers', 'Campaign Cost']:
                    response += f"• {key}: {value}\n"
            response += "```"
            await ctx.send(response)

def setup(bot):
    bot.add_cog(UnitStatsCog(bot))
