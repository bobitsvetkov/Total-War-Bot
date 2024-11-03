from discord.ext import commands
import logging
from typing import Dict, List, Any, Optional
import textwrap
from concurrent.futures import ThreadPoolExecutor
from utils.data_loader import load_unit_data
from utils.gemini_prompt import generate_analysis
from utils.unit_performance import make_hashable_unit, analyze_faction_weights, calculate_all_faction_stats

UnitData = Dict[str, Any]
FactionData = Dict[str, List[UnitData]]

logging.basicConfig(level=logging.INFO)
executor = ThreadPoolExecutor(max_workers=4)

class FactionAnalysisBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.analysis_cache: Dict[str, str] = {}
        self.unit_data: List[UnitData] = load_unit_data()
        self.factions: Dict[str, List[UnitData]] = self._group_units_by_faction()

    def _group_units_by_faction(self) -> Dict[str, List[UnitData]]:
        """Organize units by faction."""
        factions: Dict[str, List[UnitData]] = {}
        for unit in self.unit_data:
            factions.setdefault(unit["Faction"], []).append(unit)
        return factions

    async def send_long_message(self, ctx: commands.Context, faction_name: str, content: str) -> None:
        """Send a long message in chunks to avoid character limits."""
        chunks = textwrap.wrap(content, 1900, replace_whitespace=False)
        await ctx.send(f"**Analysis for {faction_name}:**")
        for chunk in chunks:
            await ctx.send(chunk)

    async def get_or_generate_analysis(self, faction_name: str) -> str:
        """Retrieve cached analysis or generate new analysis for a faction."""
        if faction_name in self.analysis_cache:
            return self.analysis_cache[faction_name]

        units_tuple = tuple(make_hashable_unit(unit) for unit in self.factions[faction_name])
        stats = analyze_faction_weights(units_tuple, faction_name)
        all_factions_stats = calculate_all_faction_stats(self.factions)
        analysis = generate_analysis(faction_name, stats, all_factions_stats)
        self.analysis_cache[faction_name] = analysis
        return analysis

    @commands.command(name='faction_analysis', help='Analyze the strengths and weaknesses of a faction.')
    async def faction_analysis_command(self, ctx: commands.Context, *, faction_name: Optional[str] = None) -> None:
        """Command handler to analyze a faction's strengths and weaknesses."""
        guidance_message = "Please specify a faction name to analyze. Example: `!faction_analysis Rome`"
    
        # Check if faction name is provided
        if not faction_name:
            await ctx.send(guidance_message)
            return
        if faction_name not in self.factions:
            await ctx.send(f"Faction '{faction_name}' not found.")
            return

        async with ctx.typing():
            try:
                analysis = await self.get_or_generate_analysis(faction_name)
                await self.send_long_message(ctx, faction_name, analysis)
            except Exception as e:
                logging.error(f"Error analyzing faction {faction_name}: {e}")
                await ctx.send(f"Error analyzing faction {faction_name}. Please try again later.")