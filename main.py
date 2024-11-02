import logging
from discord.ext import commands
from utils.intents import setup_intents
from config.discord_settings import load_config
from utils.channel_validator import is_in_correct_channel
from config.cog_loader import setup_cogs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize bot and load configurations
config = load_config()
intents = setup_intents()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Bot is ready. Logged in as {bot.user}')
    bot.add_check(is_in_correct_channel)
    await setup_cogs(bot)

def start_bot():
    bot.run(config["bot_token"])

if __name__ == '__main__':
    start_bot()
