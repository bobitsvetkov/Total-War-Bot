import discord
from discord.ext import commands
import logging
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from io import BytesIO
# Define intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix = "!", intents=intents)

json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'units_stats.json')

# Load unit data from JSON
with open(json_path) as f:
    unit_data = json.load(f)
def query_unit_stats(unit_name):
    """Extract specific stat information for a unit."""
    logging.info(f"Looking for unit: {unit_name}")
    for unit in unit_data:
        if unit['Unit'].lower() == unit_name.lower():
            return unit
    return None

def compare_stats(unit1, unit2):
    """Generate a modern-styled comparison image for damage stats."""
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(20, 8), dpi=100)

    # Define stats and get values
    stats = ['Base Damage', 'AP Damage', 'Weapon Damage',
             'Bonus vs Large', 'Bonus vs Infantry',
             'Charge Bonus', 'Melee Defense', 'Melee Attack',
             'Armor', 'HP', 'Morale','Range', 'Base Missile Damage',
             'AP Missile Damage', 'Total Missile Damage',
             'Missile Block Chance', 'Ammo']

    unit1_stats = [unit1.get(stat, 0) for stat in stats]
    unit2_stats = [unit2.get(stat, 0) for stat in stats]

    color1 = '#2ecc71'  # Green
    color2 = '#3498db'  # Blue

    bar_width = 0.35
    index = np.arange(len(stats))

    bars1 = ax.bar(index, unit1_stats, bar_width,
                   color=color1, alpha=0.8)

    bars2 = ax.bar(index + bar_width, unit2_stats, bar_width,
                   color=color2, alpha=0.8)

    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom',
                   fontsize=10, fontweight='bold',
                   color='#444444')

    add_value_labels(bars1)
    add_value_labels(bars2)

    ax.set_xlabel('Unit Statistics', fontsize=12, fontweight='bold', labelpad=15)
    ax.set_ylabel('Values', fontsize=12, fontweight='bold', labelpad=15)

    title = f"{unit1['Unit']} vs {unit2['Unit']}\nUnit Statistics Comparison"
    subtitle = f"[{unit1['Faction']} vs {unit2['Faction']}]"
    ax.set_title(title + '\n' + subtitle + '\n',
                 fontsize=14, fontweight='bold', pad=20)

    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(stats, fontsize=10, rotation=45, ha='right')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')

    custom_legend_labels = [f"{unit1['Unit']} (Green)", f"{unit2['Unit']} (Blue)"]
    ax.legend(custom_legend_labels, loc='upper right', fontsize=12, frameon=False)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf,
                format='png',
                facecolor='white',
                edgecolor='none',
                bbox_inches='tight',
                pad_inches=0.3)
    buf.seek(0)

    plt.close()
    return buf

@bot.command(name='compare_stats')
async def compare_stats_command(ctx: commands.Context, *, units: str):
    """Compare damage stats of two units."""
    # Split the input on 'vs' or 'versus' if present
    if ' vs ' in units.lower():
        unit1_name, unit2_name = units.split(' vs ', 1)
    elif ' versus ' in units.lower():
        unit1_name, unit2_name = units.split(' versus ', 1)
    else:
        # If no 'vs' or 'versus', try to find the last occurrence of 'and'
        if ' and ' in units.lower():
            unit1_name, unit2_name = units.split(' and ', 1)
        else:
            # If no clear separator, look for the comma
            parts = [p.strip() for p in units.split(',')]
            if len(parts) == 2:
                unit1_name, unit2_name = parts
            else:
                await ctx.send("Please provide two units to compare using one of these formats:\n"
                             "- `!compare_stats Unit1 vs Unit2`\n"
                             "- `!compare_stats Unit1 and Unit2`\n"
                             "- `!compare_stats Unit1, Unit2`\n"
                             "Example: `!compare_stats Evocati Cohort vs Sword Followers`")
                return

    # Clean up the unit names
    unit1_name = unit1_name.strip()
    unit2_name = unit2_name.strip()

    # Query the stats using the clean names
    unit1 = query_unit_stats(unit1_name)
    unit2 = query_unit_stats(unit2_name)

    if not unit1:
        await ctx.send(f"Unit not found: {unit1_name}")
        return
    if not unit2:
        await ctx.send(f"Unit not found: {unit2_name}")
        return

    # Generate the comparison image for damage stats
    comparison_image = compare_stats(unit1, unit2)

    # Send the generated image
    file = discord.File(fp=comparison_image, filename='stats_comparison.png')
    await ctx.send(file=file)