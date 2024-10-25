import json
import os
from typing import Dict, List
from langchain_ollama import OllamaLLM
from discord.ext import commands
from scripts.utils import make_hashable_unit, analyze_faction_weights

class FactionComparisonBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.faction_cache = {}
        self.analysis_cache = {}
        self.model = OllamaLLM(
            model="llama3",
            temperature=0.7,
            num_ctx=2048,
        )
        
        # Load unit data
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'units_stats.json')
        with open(json_path, 'r') as f:
            self.unit_data = json.load(f)
        
        self.factions: Dict[str, List[dict]] = {}
        self._group_units_by_faction()

    def _group_units_by_faction(self):
        for unit in self.unit_data:
            faction = unit["Faction"]
            if faction not in self.factions:
                self.factions[faction] = []
            self.factions[faction].append(unit)

    async def compare_factions(self, faction1: str, faction2: str) -> str:
        """
        Compare two factions based on their melee, ranged, and tankiness scores.
        Provide a summary and recommend counters.
        """
        if faction1 not in self.factions or faction2 not in self.factions:
            return f"One or both factions '{faction1}' and '{faction2}' not found."

        # Calculate stats for faction 1
        units_tuple_faction1 = tuple(make_hashable_unit(unit) for unit in self.factions[faction1])
        stats_faction1 = analyze_faction_weights(units_tuple_faction1)

        # Calculate stats for faction 2
        units_tuple_faction2 = tuple(make_hashable_unit(unit) for unit in self.factions[faction2])
        stats_faction2 = analyze_faction_weights(units_tuple_faction2)

        # Compare the stats
        comparison = (
            f"**Comparison between {faction1} and {faction2}:**\n\n"
            f"**{faction1}**\n"
            f"Tankiness: {stats_faction1['tankiness']}\n"
            f"Melee: {stats_faction1['melee_strength']}\n"
            f"Ranged: {stats_faction1['ranged_strength']}\n\n"
            f"**{faction2}**\n"
            f"Tankiness: {stats_faction2['tankiness']}\n"
            f"Melee: {stats_faction2['melee_strength']}\n"
            f"Ranged: {stats_faction2['ranged_strength']}\n\n"
        )

        # Determine advantages
        tankiness_diff = stats_faction1['tankiness'] - stats_faction2['tankiness']
        melee_diff = stats_faction1['melee_strength'] - stats_faction2['melee_strength']
        ranged_diff = stats_faction1['ranged_strength'] - stats_faction2['ranged_strength']

        # Provide recommendations based on differences
        if tankiness_diff > 0:
            comparison += f"**{faction1}** has a stronger tanky front line, making them harder to break in melee engagements.\n"
        else:
            comparison += f"**{faction2}** has a tougher front line, making them better suited for prolonged battles.\n"

        if melee_diff > 0:
            comparison += f"**{faction1}** excels in melee combat and can break the enemy lines faster.\n"
        else:
            comparison += f"**{faction2}** dominates in melee and is likely to overpower enemy infantry.\n"

        if ranged_diff > 0:
            comparison += f"**{faction1}** has superior ranged units, allowing them to wear down enemies before engaging in melee.\n"
        else:
            comparison += f"**{faction2}** has better ranged firepower, so avoid prolonged missile exchanges.\n"

       # Recommend counters based on the strengths of each faction
        if stats_faction1['tankiness'] > stats_faction2['tankiness'] and stats_faction1['melee_strength'] > stats_faction2['melee_strength']:
            comparison += f"**Counter {faction1}**: Try to use your skirmishers to whittle down their powerful frontline units\n"
        else:
            comparison += f"**Counter {faction2}**: Use armor-piercing units to deal with their tanky units.\n"

        if stats_faction1['melee_strength'] > stats_faction2['melee_strength']:
            comparison += f"**Counter {faction1}**: Use delaying tactics, skirmishers, and pilla to weaken the enemy before engaging.\n"
        else:
            comparison += f"**Counter {faction2}**: Use delaying tactics, skirmishers, and pilla to weaken the enemy before engaging.\n"

        if stats_faction1['ranged_strength'] > stats_faction2['ranged_strength']:
            comparison += f"**Counter {faction1}**: Engage as fast as possible. Try to deal with the enemy skirmishers by using your own or surprise attacks to destroy the enemy ranged superiority.\n"
        else:
            comparison += f"**Counter {faction2}**: Engage as fast as possible. Try to deal with the enemy skirmishers by using your own or surprise attacks to destroy the enemy ranged superiority.\n"

        return comparison


    @commands.command(name='faction_compare')
    async def faction_compare_command(self, ctx: commands.Context, *, factions: str):
        """Compare two factions based on their stats."""
        # Split the input on 'vs', 'versus', 'and', or ',' if present
        factions_lower = factions.lower()
        if ' vs ' in factions_lower:
            faction1_name, faction2_name = factions.split(' vs ', 1)
        elif ' versus ' in factions_lower:
            faction1_name, faction2_name = factions.split(' versus ', 1)
        elif ' and ' in factions_lower:
            faction1_name, faction2_name = factions.rsplit(' and ', 1)
        else:
            parts = [p.strip() for p in factions.split(',')]
            if len(parts) == 2:
                faction1_name, faction2_name = parts
            else:
                await ctx.send("Please provide two factions to compare using one of these formats:\n"
                               "- `!faction_compare Faction1 vs Faction2`\n"
                               "- `!faction_compare Faction1 and Faction2`\n"
                               "- `!faction_compare Faction1, Faction2`\n"
                               "Example: `!faction_compare Odrysian Kingdom vs Rome`")
                return

        # Trim whitespace
        faction1_name = faction1_name.strip()
        faction2_name = faction2_name.strip()

        # Proceed with the analysis logic
        comparison_result = await self.compare_factions(faction1_name, faction2_name)

        # Send the comparison result
        await ctx.send(comparison_result)
