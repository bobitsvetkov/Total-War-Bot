import os
from dotenv import load_dotenv

def load_config():
    load_dotenv("secret.env")

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("Discord bot token is not set. Please set it in your environment variables.")

    dev_channel_id = int(os.getenv("DEV_CHANNEL_ID", "0"))
    if not dev_channel_id:
        raise ValueError("Channel for testing and dev purposes not set.")

    channel_id = int(os.getenv("CHANNEL", "0"))

    return {
        "bot_token": bot_token,
        "dev_channel_id": dev_channel_id,
        "channel_id": channel_id
    }