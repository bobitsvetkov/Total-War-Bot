import discord
from discord.ext import commands
import logging
import matplotlib.pyplot as plt
import matplotlib.axes
import numpy as np
from typing import Optional
from io import BytesIO
from utils.data_loader import load_unit_data

class UnitStatsComparison(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.unit_data = load_unit_data()
    def query_unit_stats(self, unit_name):
        """Extract specific stat information for a unit."""
        logging.info(f"Looking for unit: {unit_name}")
        return next((unit for unit in self.unit_data if unit['Unit'].lower() == unit_name.lower()), None)

    def compare_stats(self, unit1, unit2):
        """Generate a comparison image for unit damage stats."""
        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=(20, 8), dpi=100)

        stats = [
            'Base Damage', 'AP Damage', 'Weapon Damage',
            'Bonus vs Large', 'Bonus vs Infantry',
            'Charge Bonus', 'Melee Defense', 'Melee Attack',
            'Armor', 'HP', 'Morale', 'Range',
            'Base Missile Damage', 'AP Missile Damage',
            'Total Missile Damage', 'Missile Block Chance', 'Ammo'
        ]

        unit1_stats = [unit1.get(stat, 0) for stat in stats]
        unit2_stats = [unit2.get(stat, 0) for stat in stats]

        color1, color2 = '#2ecc71', '#3498db'
        bar_width = 0.35
        index = np.arange(len(stats))

        bars1 = ax.bar(index, unit1_stats, bar_width, color=color1, alpha=0.8)
        bars2 = ax.bar(index + bar_width, unit2_stats, bar_width, color=color2, alpha=0.8)

        self.add_value_labels(bars1, ax)
        self.add_value_labels(bars2, ax)

        self.setup_axes(ax, unit1, unit2, stats, index, bar_width)

        buf = BytesIO()
        plt.savefig(buf, format='png', facecolor='white', edgecolor='none',
                    bbox_inches='tight', pad_inches=0.3)
        buf.seek(0)
        plt.close()
        return buf

    def add_value_labels(self, bars, ax):
        """Add value labels on top of the bars."""
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{int(height)}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold', color='#444444')

    def setup_axes(self, ax: matplotlib.axes.Axes, unit1, unit2, stats, index, bar_width):
        """Setup the axes for the comparison plot."""
        ax.set_xlabel('Unit Statistics', fontsize=12, fontweight='bold', labelpad=15)
        ax.set_ylabel('Values', fontsize=12, fontweight='bold', labelpad=15)
        ax.set_title(f"{unit1['Unit']} vs {unit2['Unit']}\n"
                     f"[{unit1['Faction']} vs {unit2['Faction']}]", fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(index + bar_width / 2)
        ax.set_xticklabels(stats, fontsize=10, rotation=45, ha='right')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_facecolor('white')

        custom_legend_labels = [f"{unit1['Unit']} (Green)", f"{unit2['Unit']} (Blue)"]
        ax.legend(custom_legend_labels, loc='upper right', fontsize=12, frameon=False)

    @commands.command(name='compare_stats', help='Compare damage stats of two units')
    async def compare_stats_command(self, ctx: commands.Context, *, units: Optional[str] = None):
        guidance_message = ("Please provide two units to compare using one of these formats:\n"
                            "- `!compare_stats Unit1 vs Unit2`\n"
                            "- `!compare_stats Unit1 and Unit2`\n"
                            "- `!compare_stats Unit1, Unit2`\n"
                            "Example: `!compare_stats Evocati Cohort vs Sword Followers`")
        
        if not units:
            await ctx.send(guidance_message)
            return

        # Parse unit names based on common conjunctions
        units_lower = units.lower()
        if ' vs ' in units_lower:
            unit1_name, unit2_name = units.split(' vs ', 1)
        elif ' versus ' in units_lower:
            unit1_name, unit2_name = units.split(' versus ', 1)
        elif ' and ' in units_lower:
            unit1_name, unit2_name = units.rsplit(' and ', 1)
        else:
            parts = [p.strip() for p in units.split(',')]
            if len(parts) == 2:
                unit1_name, unit2_name = parts
            else:
                await ctx.send(guidance_message)
                return

        unit1_name = unit1_name.strip()
        unit2_name = unit2_name.strip()

        # Query and validate unit stats
        unit1 = self.query_unit_stats(unit1_name)
        unit2 = self.query_unit_stats(unit2_name)

        if not unit1:
            await ctx.send(f"Unit not found: {unit1_name}")
            return
        if not unit2:
            await ctx.send(f"Unit not found: {unit2_name}")
            return

        # Run the comparison and send the result
        comparison_image = self.compare_stats(unit1, unit2)
        file = discord.File(fp=comparison_image, filename='stats_comparison.png')
        await ctx.send(file=file)
