from discord.ext import commands
import logging
from utils.data_loader import load_unit_data

logging.basicConfig(level=logging.INFO)

unit_data = load_unit_data()

def query_unit_stats(unit_name):
    """Extract specific stat information for a unit."""
    logging.info(f"Looking for unit: {unit_name}")
    for unit in unit_data:
        if unit['Unit'].lower() == unit_name.lower():
            return unit
    return "Unit not found"

class UnitStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='unit_stats', help='Get information for a specified unit')
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
