from config.discord_settings import load_config
async def is_in_correct_channel(ctx):
    config = load_config()
    if ctx.channel.id == config["channel_id"] or ctx.channel.id == config["dev_channel_id"]:
        return True
    else:
        allowed_channel = ctx.bot.get_channel(config["channel_id"])
        await ctx.send(f"Please use bot commands in {allowed_channel.mention}.")
        return False