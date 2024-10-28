import discord
from discord.ext import commands
import json
import os
from typing import Optional, List, Dict

class HistoricalResults(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'player_stats_historical.json')

    def _parse_percentage(self, percentage_str: Optional[str]) -> float:
        """Convert a percentage string or numeric to a float."""
        if not percentage_str:
            return 0.0
        try:
            return float(str(percentage_str).strip('%'))
        except ValueError:
            return 0.0

    def calculate_player_rating(self, player_data: dict) -> float:
        """Calculates the player's rating based on various metrics."""
        base_rating = 1000.0
        win_percentage = self._parse_percentage(player_data.get('Win %', ''))
        playoff_rate = self._parse_percentage(player_data.get('Playoff Rate', ''))
        games_played = int(player_data.get('Games Played', 0) or 0)

        # Calculate the rating
        performance_multiplier = 0.5 if games_played < 20 else 1.0
        rating = base_rating + (win_percentage * 5) + (float(player_data.get('K/D ratio', 0) or 0) * 100)
        rating += float(player_data.get('Chevrons/game', 0) or 0) * 25

        # Add extra points for achievements
        achievements = {
            'Championships': 30, 
            'Runner-ups': 20, 
            'Third Places': 10, 
            'Top 3 Best KD Ratios': 5, 
            'Top 3 Most Chevrons/Game': 5
        }
        for key, points in achievements.items():
            rating += int(player_data.get(key, 0) or 0) * points

        rating += playoff_rate * 3
        rating *= performance_multiplier
        return round(rating, 2)

    def load_player_data(self) -> List[dict]:
        """Loads player data from a JSON file."""
        with open(self.player_data_path, 'r') as f:
            return json.load(f)

    def generate_leaderboard(self) -> List[Dict[str, any]]:
        """Generates a leaderboard based on player ratings."""
        players_data = self.load_player_data()
        leaderboard = [
            {
                'Player': player['Player'],
                'Rating': self.calculate_player_rating(player),
                'Games Played': int(player.get('Games Played', 0) or 0),
                'Win %': player.get('Win %', ''),
                'K/D ratio': player.get('K/D ratio', ''),
                'Chevrons/game': player.get('Chevrons/game', ''),
                'Championships': player.get('Championships', 0)
            }
            for player in players_data if int(player.get('Games Played', 0) or 0) >= 10
        ]
        return sorted(leaderboard, key=lambda x: x['Rating'], reverse=True)

    def generate_metric_leaderboard(self, metric_key: str) -> List[Dict[str, any]]:
        """Generates a leaderboard based on a specific metric."""
        players_data = self.load_player_data()
        leaderboard = [
            {
                'Player': player['Player'],
                metric_key: self._parse_percentage(player.get(metric_key, '0')),
                'Games Played': int(player.get('Games Played', 0) or 0)
            }
            for player in players_data if int(player.get('Games Played', 0) or 0) >= 20
        ]
        return sorted(leaderboard, key=lambda x: x[metric_key], reverse=True)

    def get_player_history(self, player_name: str) -> Optional[dict]:
        """Retrieve a player's historical data by name."""
        players_data = self.load_player_data()
        player = next((p for p in players_data if p['Player'].lower() == player_name.lower()), None)
        if player:
            return {key: player.get(key, 'N/A') for key in (
                "Total Kills", "Total Losses", "Games Played", "Games Won",
                "Win %", "DC's/Forfeits", "Championships", "Runner-ups",
                "Third Places", "Playoff Appearances", "Playoff Rate"
            )}
        return None

    async def display_leaderboard(self, ctx, title: str, leaderboard: List[dict], metric: str):
        """Send an embedded leaderboard message."""
        embed = discord.Embed(title=title, color=discord.Color.gold())
        for rank, player in enumerate(leaderboard[:10], 1):
            embed.add_field(
                name=f"{rank}. {player['Player']}",
                value=f"{metric}: {player[metric]}, Games Played: {player['Games Played']}",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name='player_history')
    async def show_player_history(self, ctx, *, player_name: str):
        history = self.get_player_history(player_name)
        if not history:
            await ctx.send(f"No historical data found for player '{player_name}'!")
            return

        rating = self.calculate_player_rating(history)
        embed = discord.Embed(title=f"Historical Results: {player_name}", color=discord.Color.purple())
        for stat, value in history.items():
            embed.add_field(name=stat, value=value, inline=True)

        embed.add_field(name="Rating", value=rating, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='historical_leaderboard')
    async def show_leaderboard(self, ctx):
        leaderboard = self.generate_leaderboard()
        await self.display_leaderboard(ctx, "Top Players Leaderboard", leaderboard, "Rating")

    @commands.command(name='win_percentage_leaderboard')
    async def win_percentage_leaderboard(self, ctx):
        leaderboard = self.generate_metric_leaderboard("Win %")
        await self.display_leaderboard(ctx, "Top Players by Win %", leaderboard, "Win %")

    @commands.command(name='kd_ratio_leaderboard')
    async def kd_ratio_leaderboard(self, ctx):
        leaderboard = self.generate_metric_leaderboard("K/D ratio")
        await self.display_leaderboard(ctx, "Top Players by K/D Ratio", leaderboard, "K/D ratio")

def setup(bot):
    bot.add_cog(HistoricalResults(bot))
