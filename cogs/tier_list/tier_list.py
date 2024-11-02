import discord
from discord.ext import commands
import os

class TierList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tier_list', help='Send the tier list image')
    async def send_tierlist(self, ctx):
        image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', '3v3 Tier List.png')
        if os.path.exists(image_path):
            await ctx.send(file=discord.File(image_path))
        else:
            await ctx.send("Tier list image not found!")
