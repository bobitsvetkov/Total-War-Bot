import discord
from discord.ext import commands
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict
import io
import os

class LeaderboardSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Scoring weights
        self.weights = {
            'chevrons_per_game': 0.35,  # 35% of total score
            'kd_ratio': 0.25,           # 25% of total score
            'kills_per_game': 0.25,     # 25% of total score
            'win_rate': 0.15,           # 15% of total score
            'dc_penalty': 0.90          # 10% penalty for disconnects
        }
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'players_stats.json')
        with open(json_path) as f:
            self.unit_data = json.load(f)

    def calculate_player_score(self, player: Dict) -> float:
        """Calculate player score based on weighted metrics"""
        # Normalize values to 0-100 scale
        chevron_score = (player['Chevrons/game'] / 9) * 100
        kd_score = player['K/D ratio'] * 100
        kills_per_game_score = (player['Kills/Game'] / 2000) * 100
        
        # Calculate win rate
        games_played = player['Games Played']
        if games_played > 0:
            win_rate = (player['Games Won'] / games_played) * 100
        else:
            win_rate = 0

        # Calculate weighted score
        score = (
            chevron_score * self.weights['chevrons_per_game'] +
            kd_score * self.weights['kd_ratio'] +
            kills_per_game_score * self.weights['kills_per_game'] +
            win_rate * self.weights['win_rate']
        )

        # Apply DC penalty if applicable
        if player["DC's/Forfeits"] != "-":
            score *= self.weights['dc_penalty']

        if games_played < 4:
            score *= 0.5  # Reduce score by 50%
        return score

    def create_leaderboard_image(self, players: List[Dict]) -> io.BytesIO:
        """Create a visual leaderboard using matplotlib"""
        # Calculate scores and sort players in descending order
        for player in players:
            player['Score'] = self.calculate_player_score(player)
        sorted_players = sorted(players, key=lambda x: x['Score'], reverse=True)

        # Set up the plot size and theme
        plt.figure(figsize=(42, 18))
        sns.set_theme(style="darkgrid")

        # Reverse the order of y positions to have top players at the top
        scores = [player['Score'] for player in sorted_players]
        names = [player['Player Name'] for player in sorted_players]

        # Plot top players in distinct colors
        bars = plt.bar(names, scores, color=['#FFD700', '#C0C0C0', '#CD7F32'] + ['#1f77b4'] * (len(players) - 3))

        # Label the top 3 players
        for bar in bars:
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{bar.get_height():.1f}',
                    ha='center', va='bottom', fontweight='bold')

        # Customize plot
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.ylabel('Score', fontsize=14)
        plt.title('Total War Player Rankings', fontsize=16)

        # Save plot to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        plt.close()
        return buffer

    @commands.command(name='leaderboard')
    async def show_leaderboard(self, ctx):
        """Display the player leaderboard"""
        try:
            # Load player data
            players = self.unit_data

            # Create and add leaderboard image
            leaderboard_image = self.create_leaderboard_image(players)
            file = discord.File(leaderboard_image, filename="leaderboard.png")

            # Create embed and attach the image
            embed = discord.Embed(
                title="🏆 Total War Player Rankings",
                color=discord.Color.gold()
            )
            embed.set_image(url="attachment://leaderboard.png")

            # Send the embed with the image only
            await ctx.send(embed=embed, file=file)

        except Exception as e:
            await ctx.send(f"Error generating leaderboard: {str(e)}")

    @commands.command(name='player_stats')
    async def show_player_stats(self, ctx, *, player_name: str):
        """Display detailed stats for a specific player"""
        try:
            players = self.unit_data
            player = next((p for p in players if p['Player Name'].lower() == player_name.lower()), None)

            if not player:
                await ctx.send(f"Player '{player_name}' not found!")
                return

            score = self.calculate_player_score(player)
            
            embed = discord.Embed(
                title=f"Player Stats: {player['Player Name']}",
                color=discord.Color.blue()
            )

            # Basic stats
            embed.add_field(
                name="Overview",
                value=(
                    f"Team: **{player['Team Name']}**\n"
                    f"Score: **{score:.1f}**\n"
                    f"Rank: **{sum(self.calculate_player_score(p) > score for p in players) + 1}**"
                ),
                inline=False
            )

            # Combat stats
            embed.add_field(
                name="Combat Performance",
                value=(
                    f"K/D Ratio: **{player['K/D ratio']}**\n"
                    f"Kills/Game: **{player['Kills/Game']}**\n"
                    f"Chevrons/Game: **{player['Chevrons/game']}**"
                ),
                inline=True
            )

            # Game stats
            win_rate = player['Games Won'] / player['Games Played'] * 100
            embed.add_field(
                name="Game Statistics",
                value=(
                    f"Games Played: **{player['Games Played']}**\n"
                    f"Win Rate: **{win_rate:.1f}%**\n"
                    f"DC's/Forfeits: **{player['DC\'s/Forfeits']}**"
                ),
                inline=True
            )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Error retrieving player stats: {str(e)}")

def setup(bot):
    bot.add_cog(LeaderboardSystem(bot))
