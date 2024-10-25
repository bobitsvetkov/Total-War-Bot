import discord
import os
import logging
import json
from discord.ext import commands
from dotenv import load_dotenv
from scripts.unit_comparison import compare_stats_command
from scripts.bot import FactionAnalysisBot
from scripts.faction_comparison import FactionComparisonBot

from cogs.unit_stats import UnitStatsCog
from cogs.tier_list import TierListCog
from cogs.commands_list import CommandsListCog

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
json_path = os.path.join(os.path.dirname(__file__), 'data', 'units_stats.json')

# Load unit data from JSON
with open(json_path) as f:
    unit_data = json.load(f)

load_dotenv("secret.env")
bot_token = os.getenv("BOT_TOKEN")

# Define intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Add commands from other scripts
bot.add_command(compare_stats_command)

# Setup function for adding all cogs
async def setup_bot():
    await bot.add_cog(FactionAnalysisBot(bot))
    await bot.add_cog(FactionComparisonBot(bot))
    await bot.add_cog(UnitStatsCog(bot))
    await bot.add_cog(TierListCog(bot))
    await bot.add_cog(CommandsListCog(bot))

# This will run the setup before the bot starts
@bot.event
async def on_ready():
    logging.info(f'Bot is ready. Logged in as {bot.user}')
    # Add all cogs after the bot is ready
    await setup_bot()

# Run the bot
bot.run(bot_token)
