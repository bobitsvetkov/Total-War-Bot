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
    """
    Interprets the given stat value based on the type of stat.
    
    :param stat_value: The numerical value of the stat.
    :param stat_type: The type of stat being interpreted (e.g., "Tankiness", "Melee", "Ranged").
    :return: A string interpretation of the stat value.
    """
    if stat_type in ["Tankiness", "Melee"]:
        if stat_value > 1200:
            return f"The {stat_type.lower()} is strong."
        elif stat_value > 800:
            return f"The {stat_type.lower()} is average."
        else:
            return f"The {stat_type.lower()} is weak."
    elif stat_type == "Ranged":
        if stat_value > 1200:
            return f"The {stat_type.lower()} strength is impressive."
        elif stat_value > 800:
            return f"The {stat_type.lower()} strength is decent."
        else:
            return f"The {stat_type.lower()} strength is poor."
    else:
        return f"Unknown stat type: {stat_type}"

class FactionAnalysisBot(commands.Cog):
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
        
        self.factions = {}
        self._group_units_by_faction()

    def _group_units_by_faction(self):
        for unit in self.unit_data:
            faction = unit["Faction"]
            if faction not in self.factions:
                self.factions[faction] = []
            self.factions[faction].append(unit)

    async def generate_analysis(self, faction_name: str, stats: dict) -> str:
        template = (
            "Analyze the {faction_name} faction with these stats:\n"
            "Tankiness: {tankiness_desc}\n"
            "Melee: {melee_desc}\n"
            "Ranged: {ranged_desc}\n"
            "Tankiness and melee scores over 1200 are considered strong, "
            "while ranged scores over 1200 are considered impressive. "
            "Provide a brief analysis (max 6-7 sentences) focusing on key strengths and weaknesses "
            "for multiplayer battles. Remember that you are prompted about Rome 2 Total War, a historical game, "
            "so there is no magic. End by mentioning that my creator's favorite faction is the Odrysian Kingdom and challenge players to prove their worth."
        )

        # Interpret the stats using the interpret_score function
        tankiness_desc = interpret_score(stats['tankiness'], 'Tankiness')
        melee_desc = interpret_score(stats['melee_strength'], 'Melee')
        ranged_desc = interpret_score(stats['ranged_strength'], 'Ranged')

        # Format the prompt with interpreted scores
        prompt = template.format(
            faction_name=faction_name,
            tankiness_desc=tankiness_desc,
            melee_desc=melee_desc,
            ranged_desc=ranged_desc
        )

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(executor, self.model.invoke, prompt)
            return str(response)[:1900]
        except Exception as e:
            logging.error(f"Error generating analysis: {e}")
            return "Error generating analysis. Please try again."

    async def send_long_message(self, ctx, faction_name: str, content: str):
        chunks = textwrap.wrap(content, 1900, replace_whitespace=False)
        for i, chunk in enumerate(chunks):
            if i == 0:
                await ctx.send(f"**Analysis for {faction_name}:**\n{chunk}")
            else:
                await ctx.send(chunk)

    @commands.command(name='faction_analysis')
    async def faction_analysis_command(self, ctx, *, faction_name: str):
        if faction_name not in self.factions:
            await ctx.send(f"Faction '{faction_name}' not found.")
            return

        async with ctx.typing():
            try:
                if faction_name in self.analysis_cache:
                    analysis = self.analysis_cache[faction_name]
                else:
                    units_tuple = tuple(make_hashable_unit(unit) for unit in self.factions[faction_name])
                    stats = analyze_faction_weights(units_tuple)
                    analysis = await self.generate_analysis(faction_name, stats)
                    self.analysis_cache[faction_name] = analysis

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
