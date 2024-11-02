import discord

def setup_intents():
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    return intents