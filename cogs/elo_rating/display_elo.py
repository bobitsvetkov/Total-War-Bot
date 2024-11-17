import logging
import discord
from discord.ext import commands
from utils.data_loader import load_elo_data

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TeamDisplaySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.unit_data = load_elo_data()

    @commands.command(name='display_team_elo', help = 'Display the top 10 teams by Elo rating in an embed')
    async def show_top_teams(self, ctx):
        try:
            teams = self.unit_data["teams"]
            
            if not teams:
                embed = discord.Embed(title="Top 10 Teams by Elo Rating", description="No teams available.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            sorted_teams = sorted(teams, key=lambda x: x["Elo Rating"], reverse=True)[:10]
            embed = discord.Embed(title="Top 10 Teams by Elo Rating", color=discord.Color.blue())
            for team in sorted_teams:
                embed.add_field(name=team["Team Name"], value=f"Elo Rating: {team['Elo Rating']:.2f}", inline=False)

            await ctx.send(embed=embed)
        except Exception as e:
            logging.error("Error in show_top_teams command", exc_info=True)
            await ctx.send(f"Error displaying top teams: {str(e)}")