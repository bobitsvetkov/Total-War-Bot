import discord
import os
import logging
import json
from discord.ext import commands
from dotenv import load_dotenv
from scripts.unit_comparison import compare_stats_command
from scripts.bot import FactionAnalysisBot
from scripts.faction_comparison import FactionComparisonBot
from cogs.leaderboard_system import LeaderboardSystem
from cogs.unit_stats import UnitStatsCog
from cogs.tier_list import TierListCog
from cogs.commands_list import CommandsListCog
from cogs.player_profile import PlayerProfile

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
json_path = os.path.join(os.path.dirname(__file__), 'data', 'units_stats.json')

# Load unit data from JSON
with open(json_path) as f:
    unit_data = json.load(f)

# Load environment variables
load_dotenv("secret.env")
bot_token = os.getenv("BOT_TOKEN")
channel_id = int(os.getenv("CHANNEL", "0"))  # Ensure conversion to integer

# Define intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Add commands from other scripts
bot.add_command(compare_stats_command)
# bot.add_cog(PlayerProfile(bot))

# Helper function to restrict commands to a specific channel
async def is_in_correct_channel(ctx):
    if ctx.channel.id == channel_id or ctx.channel.id == 524522932823785485:
        return True
    else:
        # Notify the user they are in the wrong channel
        allowed_channel = bot.get_channel(channel_id)
        await ctx.send(f"Please use bot commands in {allowed_channel.mention}.")
        return False

# Setup function for adding all cogs
async def setup_bot():
    await bot.add_cog(FactionAnalysisBot(bot))
    await bot.add_cog(FactionComparisonBot(bot))
    await bot.add_cog(UnitStatsCog(bot))
    await bot.add_cog(TierListCog(bot))
    await bot.add_cog(CommandsListCog(bot))
    await bot.add_cog(LeaderboardSystem(bot))
    await bot.add_cog(PlayerProfile(bot))

# Event to indicate the bot is ready
@bot.event
async def on_ready():
    logging.info(f'Bot is ready. Logged in as {bot.user}')
    # Apply the channel check to all commands
    bot.add_check(is_in_correct_channel)
    await setup_bot()

# Run the bot
bot.run(bot_token)
