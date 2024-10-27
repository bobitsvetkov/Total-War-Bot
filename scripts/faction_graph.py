import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import numpy as np
import json
import logging
import os
from io import BytesIO
from functools import lru_cache

# Define intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Create the bot instance with intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Define weights and special units here
WEIGHTS = {
    "tankiness": {
        "Missile Block Chance": 17.0,
        "HP": 20.0,
        "Armor": 8.0,
        "Morale": 6.0,
        "Melee Defense": 8.0,
    },
    "melee": {
        "Melee Attack": 20.0,
        "Base Damage": 10.0,
        "AP Damage": 13.0,
        "Charge Bonus": 7.0,
        'Bonus vs Infantry': 12.0,
        'Bonus vs Large': 10.0,
    },
    "ranged": {
        "Base Missile Damage": 2.0,
        "AP Missile Damage": 4.0,
        "Total Missile Damage": 4.0,
        "Ammo": 15.0,
        "Accuracy": 2.0,
        "Range": 15.0
    }
}

# Define a function to load unit data
def load_unit_data():
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'units_stats.json')
    with open(json_path) as f:
        return json.load(f)

# Function to calculate faction scores and assign tiers
def calculate_faction_tiers(unit_data):
    faction_scores = {}
    
    for unit in unit_data:
        faction = unit['Faction']

        # Calculate strengths based on weights
        tankiness = sum(unit.get(stat, 0) * weight for stat, weight in WEIGHTS["tankiness"].items())
        melee_strength = sum(unit.get(stat, 0) * weight for stat, weight in WEIGHTS["melee"].items())
        ranged_strength = sum(unit.get(stat, 0) * weight for stat, weight in WEIGHTS["ranged"].items())
        
        total_score = melee_strength + ranged_strength + tankiness
        logging.info(f"{unit['Unit']} - Faction: {faction}, Total Stats: {total_score}")
        
        if faction not in faction_scores:
            faction_scores[faction] = 0
        faction_scores[faction] += total_score

    # Assign tiers based on total scores
    tiered_factions = []
    for faction, score in faction_scores.items():
        if score >= 300:  # Adjust these thresholds as needed
            tier = 'S'
        elif score >= 200:
            tier = 'A'
        elif score >= 100:
            tier = 'B'
        elif score >= 50:
            tier = 'C'
        elif score >= 25:
            tier = 'D'
        elif score >= 10:
            tier = 'E'
        else:
            tier = 'F'
        
        tiered_factions.append((faction, tier, score))

    return tiered_factions

# Function to visualize the tier list
def visualize_tier_list(tiered_factions):
    plt.figure(figsize=(10, 6), dpi=100)
    
    # Prepare data for plotting
    factions = [f[0] for f in tiered_factions]
    tiers = [f[1] for f in tiered_factions]
    scores = [f[2] for f in tiered_factions]

    # Color mapping for tiers
    tier_colors = {
        'S': '#2ecc71',  # Green
        'A': '#3498db',  # Blue
        'B': '#f1c40f',  # Yellow
        'C': '#e67e22',  # Orange
        'D': '#e74c3c',  # Red
        'E': '#9b59b6',  # Purple
        'F': '#7f8c8d',  # Grey
    }
    
    # Create a horizontal bar plot
    y_pos = np.arange(len(factions))
    plt.barh(y_pos, scores, color=[tier_colors[t] for t in tiers], edgecolor='black')

    plt.yticks(y_pos, factions)
    plt.xlabel('Total Score', fontsize=12, fontweight='bold')
    plt.title('Faction Tier List', fontsize=14, fontweight='bold')
    
    # Add tier labels
    for index, value in enumerate(scores):
        plt.text(value, index, f' {tiers[index]}', va='center', fontsize=10, fontweight='bold')

    plt.xlim(0, max(scores) + 50)  # Add some padding to the x-axis

    # Save the figure to a BytesIO buffer
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    return buf

# Create the Discord command
@bot.command(name='faction_tiers')
async def faction_tiers_command(ctx: commands.Context):
    """Display a tier list of factions based on their strengths."""
    unit_data = load_unit_data()
    tiered_factions = calculate_faction_tiers(unit_data)
    
    # Generate the tier list visualization
    tier_list_image = visualize_tier_list(tiered_factions)

    # Send the generated image
    file = discord.File(fp=tier_list_image, filename='tier_list.png')
    await ctx.send(file=file)

# Run the bot with your token
# bot.run('YOUR_BOT_TOKEN')
