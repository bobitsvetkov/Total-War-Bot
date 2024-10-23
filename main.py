import discord
import os
from discord.ext import commands
from parse import (
    query_unit_stats
)
import logging
import json
from dotenv import load_dotenv
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
json_path = os.path.join(os.path.dirname(__file__), 'data', 'unit_stats.json')

# Load unit data from JSON
with open(json_path) as f:
    unit_data = json.load(f)

# logging.info(unit_data)
load_dotenv("privateData.env")

bot_token = os.getenv("BOT_TOKEN")

# Define intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command(name='unit_stats')
async def unit_stats(ctx, *, unit_name: str):  # Capture the entire unit name
    logging.info(f"Received unit name: '{unit_name}'")
    unit_info = query_unit_stats(unit_name)  # Get the unit info
    if unit_info == "Unit not found":
        await ctx.send(unit_info)  # Send the error message if unit not found
    else:
        # Format the response with bullet points, excluding 'Unit', 'Soldiers', and 'Campaign Cost'
        response = f"Information for {unit_name}:\n```"
        for key, value in unit_info.items():
            if key not in ['Unit', 'Soldiers', 'Campaign Cost']:  # Exclude specified keys
                response += f"• {key}: {value}\n"
        response += "```"
        await ctx.send(response)  # Send the formatted response

bot.run(bot_token)
