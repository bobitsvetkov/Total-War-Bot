import discord
from discord.ext import commands
import os
import logging
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from langchain_ollama import OllamaLLM
import textwrap
from scripts.utils import make_hashable_unit, analyze_faction_weights

# Set up a ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)

def interpret_score(stat_value: int, stat_type: str) -> str:
    """Interpret the given stat value based on the type of stat."""
    thresholds = {
        "Tankiness": [(2600, "weak"), (3000, "average"), (float("inf"), "strong")],
        "Melee": [(1000, "weak"), (2600, "average"), (float("inf"), "strong")],
        "Ranged": [(2000, "poor"), (2600, "decent"), (float("inf"), "impressive")]
    }

    for threshold, descriptor in thresholds.get(stat_type, []):
        if stat_value <= threshold:
            return f"The {stat_type.lower()} is {descriptor}."
    return f"Unknown stat type: {stat_type}"

class FactionAnalysisBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.analysis_cache = {}
        self.model = OllamaLLM(model="llama3", temperature=0.7, num_ctx=2048)
        
        # Load unit data
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'units_stats.json')
        with open(json_path, 'r') as f:
            self.unit_data = json.load(f)
        
        self.factions = self._group_units_by_faction()

    def _group_units_by_faction(self):
        factions = {}
        for unit in self.unit_data:
            factions.setdefault(unit["Faction"], []).append(unit)
        return factions

    async def generate_analysis(self, faction_name: str, stats: dict) -> str:
        template = (
            "Analyze the {faction_name} faction with these stats:\n"
            "Tankiness: {tankiness_desc}\nMelee: {melee_desc}\nRanged: {ranged_desc}\n"
            "Tankiness over 3000 is strong, melee score over 1000 is strong, and ranged scores over 5000 are impressive. "
            "For multiplayer battles, focus on key strengths and weaknesses. Odrysian Kingdom is a glass cannon with very low tankiness."
        )

        prompt = template.format(
            faction_name=faction_name,
            tankiness_desc=interpret_score(stats['tankiness'], 'Tankiness'),
            melee_desc=interpret_score(stats['melee_strength'], 'Melee'),
            ranged_desc=interpret_score(stats['ranged_strength'], 'Ranged')
        )

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(executor, self.model.invoke, prompt)
            return str(response)[:1900]
        except Exception as e:
            logging.error(f"Error generating analysis: {e}")
            return "Error generating analysis. Please try again."

    async def send_long_message(self, ctx, faction_name: str, content: str):
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
        stats = analyze_faction_weights(units_tuple)
        analysis = await self.generate_analysis(faction_name, stats)
        self.analysis_cache[faction_name] = analysis
        return analysis

    @commands.command(name='faction_analysis', help='Analyze the strengths and weaknesses of a faction.')
    async def faction_analysis_command(self, ctx, *, faction_name: str):
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

# Define intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}!')

# Setup function to add the cog
async def setup(bot):
    await bot.add_cog(FactionAnalysisBot(bot))
