from typing import Dict, List
from langchain_ollama import OllamaLLM
from discord.ext import commands
from utils.unit_performance import make_hashable_unit, analyze_faction_weights
from utils.data_loader import load_unit_data

class FactionComparisonBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = OllamaLLM(
            model="llama3",
            temperature=0.7,
            num_ctx=2048,
        )
        self.unit_data = load_unit_data()

        self.factions: Dict[str, List[dict]] = {}
        self._group_units_by_faction()

    def _group_units_by_faction(self):
        for unit in self.unit_data:
            faction = unit["Faction"]
            if faction not in self.factions:
                self.factions[faction] = []
            self.factions[faction].append(unit)

    async def compare_factions(self, faction1: str, faction2: str) -> str:
        if faction1 not in self.factions or faction2 not in self.factions:
            return f"One or both factions '{faction1}' and '{faction2}' not found."

        stats_faction1 = analyze_faction_weights(tuple(make_hashable_unit(unit)
                        for unit in self.factions[faction1]),faction_name=faction1)
        stats_faction2 = analyze_faction_weights(tuple(make_hashable_unit(unit) 
                        for unit in self.factions[faction2]), faction_name=faction2)

        comparison = (
            f"**Comparison between {faction1} and {faction2}:**\n\n"
            f"**{faction1}**\n"
            f"Survivability: {stats_faction1['survivability']}\n"
            f"Melee: {stats_faction1['melee_strength']}\n"
            f"Ranged: {stats_faction1['ranged_strength']}\n\n"
            f"**{faction2}**\n"
            f"Survivability: {stats_faction2['survivability']}\n"
            f"Melee: {stats_faction2['melee_strength']}\n"
            f"Ranged: {stats_faction2['ranged_strength']}\n\n"
        )

        focus = "Focus on maximizing your strengths and mitigating weaknesses based on these stats."
        return comparison + focus

    @commands.command(name='faction_compare')
    async def faction_compare_command(self, ctx: commands.Context, *, factions: str):
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

        faction1_name = faction1_name.strip()
        faction2_name = faction2_name.strip()

        comparison_result = await self.compare_factions(faction1_name, faction2_name)
        await ctx.send(comparison_result)
