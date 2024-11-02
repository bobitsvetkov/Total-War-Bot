from discord.ext import commands
from googleapiclient.discovery import build # type: ignore
import asyncio
import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv("secret.env")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    raise ValueError("YouTube API Key is not found!")

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

class LandGuidePlaylist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="land_guide_playlist", help='Display a playlist with guide videos about Land Battles')
    async def land_guide_playlist(self, ctx):
        await ctx.send("Please enter the faction you need help with:")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            faction_msg = await self.bot.wait_for("message", check=check, timeout=30.0)
            faction_name = faction_msg.content.lower()

            playlist_id = os.getenv("PLAYLIST_LINK")
            
            if not playlist_id:
                raise ValueError("Link to the playlist is not found!")

            video_url = self.search_youtube_for_faction(faction_name, playlist_id)
            
            if video_url:
                await ctx.send(f"Here’s a guide for **{faction_name}**: {video_url}")
            else:
                await ctx.send(f"Sorry, no guides found for **{faction_name}**.")

        except asyncio.TimeoutError:
            await ctx.send("You didn't respond in time. Please try again.")
    @lru_cache(maxsize=32)
    def search_youtube_for_faction(self, faction_name, playlist_id):
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=35
        )
        response = request.execute()
        videos = response.get("items", [])
        if not videos:
            return f"Sorry, no guides found for **{faction_name}** in the playlist."
        for video in videos:
            title = video["snippet"]["title"].lower()
            if faction_name in title:
                return f"https://www.youtube.com/watch?v={video['snippet']['resourceId']['videoId']}"
        return None
