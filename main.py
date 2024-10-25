import discord
import sys
from scripts.keep_alive import keep_alive
import os
import logging
import json
from discord.ext import commands
from dotenv import load_dotenv
from scripts.unit_stats_query import query_unit_stats
from scripts.unit_comparison import compare_stats_command
# from scripts.analyze_faction import FactionAnalysisBot  # Adjusted import
from scripts.bot import FactionAnalysisBot
from scripts.faction_comparison import FactionComparisonBot
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
json_path = os.path.join(os.path.dirname(__file__), 'data', 'units_stats.json')
keep_alive()
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


# Create a setup function for adding the FactionAnalysisBot
async def setup_bot():
    await bot.add_cog(FactionAnalysisBot(bot))
    await bot.add_cog(FactionComparisonBot(bot))

# This will run the setup before the bot starts
@bot.event
async def on_ready():
    logging.info(f'Bot is ready. Logged in as {bot.user}')
    # Add the cog after the bot is ready
    await setup_bot()

@bot.command(name='unit_stats')
async def unit_stats(ctx, *, unit_name: str):  # Capture the entire unit name
    logging.info(f"Received unit name: '{unit_name}'")
    unit_info = query_unit_stats(unit_name)
    if unit_info == "Unit not found":
        await ctx.send(unit_info)
    else:
        # Format the response with bullet points, excluding 'Unit', 'Soldiers', and 'Campaign Cost'
        response = f"Information for {unit_name}:\n```"
        for key, value in unit_info.items():
            if key not in ['Unit', 'Soldiers', 'Campaign Cost']:
                response += f"• {key}: {value}\n"
        response += "```"
        await ctx.send(response)

# Command to send an image
@bot.command(name='tier_list')
async def send_tierlist(ctx):
    # Specify the path to your image
    image_path = os.path.join(os.path.dirname(__file__), 'images', '3v3 Tier List.png')

    if os.path.exists(image_path):
        # Send the image if it exists
        await ctx.send(file=discord.File(image_path))
    else:
        # Send an error message if the image is not found
        await ctx.send("Tier list image not found!")

# Run the bot
bot.run(str(bot_token))
