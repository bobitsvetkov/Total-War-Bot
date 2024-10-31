import discord
import os
import logging
import json
from discord.ext import commands
from dotenv import load_dotenv
from scripts.unit_comparison import UnitStatsComparisonCog
from cogs.faction_analysis.bot import FactionAnalysisBot
from cogs.faction_comparison.faction_comparison import FactionComparisonBot
from cogs.unit_stats.unit_stats import UnitStatsCog
from cogs.tier_list.tier_list import TierListCog
from cogs.commands.commands_list import CommandsListCog
from cogs.historical_results.historical_results import HistoricalResults
from cogs.elo_rating.display_elo import TeamDisplaySystem

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
json_path = os.path.join(os.path.dirname(__file__), 'data', 'units_stats.json')

with open(json_path) as f:
    unit_data = json.load(f)

load_dotenv("secret.env")
bot_token = os.getenv("BOT_TOKEN")
if not bot_token:
    raise ValueError("Discord bot token is not set. Please set it in your environment variables.")

channel_id = int(os.getenv("CHANNEL", "0"))  # Ensure conversion to integer

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def is_in_correct_channel(ctx):
    if ctx.channel.id == channel_id or ctx.channel.id == 524522932823785485:
        return True
    else:
        # Notify the user they are in the wrong channel
        allowed_channel = bot.get_channel(channel_id)
        await ctx.send(f"Please use bot commands in {allowed_channel.mention}.")
        return False

async def setup_bot():
    await bot.add_cog(FactionAnalysisBot(bot))
    await bot.add_cog(FactionComparisonBot(bot))
    await bot.add_cog(UnitStatsCog(bot))
    await bot.add_cog(TierListCog(bot))
    await bot.add_cog(CommandsListCog(bot))
    await bot.add_cog(HistoricalResults(bot))
    await bot.add_cog(TeamDisplaySystem(bot))
    await bot.add_cog(UnitStatsComparisonCog(bot))

@bot.event
async def on_ready():
    logging.info(f'Bot is ready. Logged in as {bot.user}')
    bot.add_check(is_in_correct_channel)
    await setup_bot()

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    bot.run(bot_token)
