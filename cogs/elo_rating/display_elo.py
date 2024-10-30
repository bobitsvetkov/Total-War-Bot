import json
import os
import logging
import discord
from discord.ext import commands

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TeamDisplaySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'elo_rating.json')

        # Load the initial data from the JSON file
        with open(self.json_path) as f:
            self.unit_data = json.load(f)

    @commands.command(name='display_team_elo')
    async def show_top_teams(self, ctx):
        """Display the top 10 teams by Elo rating in an embed"""
        try:
            teams = self.unit_data["teams"]

            sorted_teams = sorted(teams, key=lambda x: x["Elo Rating"], reverse=True)[:10]

            embed = discord.Embed(title="Top 10 Teams by Elo Rating", color=discord.Color.blue())
            for team in sorted_teams:
                embed.add_field(name=team["Team Name"], value=f"Elo Rating: {team['Elo Rating']:.2f}", inline=False)

            await ctx.send(embed=embed)
        except Exception as e:
            logging.error("Error in show_top_teams command", exc_info=True)
            await ctx.send(f"Error displaying top teams: {str(e)}")
