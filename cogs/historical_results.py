import discord
from discord.ext import commands
import json
import os

class HistoricalResults(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'player_stats_historical.json')
        self.player_data_path = json_path

    def calculate_player_rating(self, player_data):
        base_rating = 1000.0

        def parse_percentage(percentage_str):
            if not percentage_str:
                return 0.0

            if isinstance(percentage_str, (int, float)):
                return float(percentage_str)

            percentage_str = percentage_str.strip().strip('%')

            try:
                return float(percentage_str)
            except ValueError:
                return 0.0

        win_percentage = parse_percentage(player_data.get('Win %', ''))
        playoff_rate = parse_percentage(player_data.get('Playoff Rate', ''))
        games_played = int(player_data.get('Games Played', 0) or 0)

        performance_multiplier = 0.5 if games_played < 20 else 1.0
        rating = base_rating + (win_percentage * 5) + (float(player_data.get('K/D ratio', 0) or 0) * 100)
        rating += float(player_data.get('Chevrons/game', 0) or 0) * 25

        championships = int(player_data.get('Championships', 0) or 0)
        runner_ups = int(player_data.get('Runner-ups', 0) or 0)
        third_places = int(player_data.get('Third Places', 0) or 0)
        top_3_best_kd_ratios = int(player_data.get('Top 3 Best KD Ratios', 0) or 0)
        top_3_most_chevrons_game = int(player_data.get('Top 3 Most Chevrons/Game', 0) or 0)

        rating += championships * 30
        rating += runner_ups * 20
        rating += third_places * 10
        rating += top_3_best_kd_ratios * 5
        rating += top_3_most_chevrons_game * 5
        rating += playoff_rate * 3
        rating *= performance_multiplier
        return round(rating, 2)

    def generate_leaderboard(self):
        with open(self.player_data_path, 'r') as f:
            players_data = json.load(f)

        leaderboard = []
        for player in players_data:
            games_played = int(player.get('Games Played', 0) or 0)
            if games_played < 10:
                continue  # Skip players with less than 10 games played

            rating = self.calculate_player_rating(player)
            leaderboard.append({
                'Player': player['Player'],
                'Rating': rating,
                'Games Played': games_played,
                'Win %': player['Win %'],
                'K/D ratio': player['K/D ratio'],
                'Chevrons/game': player['Chevrons/game'],
                'Championships': player['Championships']
            })

        leaderboard.sort(key=lambda x: x['Rating'], reverse=True)
        return leaderboard

    def get_player_history(self, player_name: str):
        with open(self.player_data_path, 'r') as f:
            players_data = json.load(f)

        player = next((p for p in players_data if p['Player'].lower() == player_name.lower()), None)
        if not player:
            return None

        history = {
            "Total Kills": player["Total Kills"],
            "Total Losses": player["Total Losses"],
            "Games Played": player["Games Played"],
            "Games Won": player["Games Won"],
            "Win %": player["Win %"],
            "DC's/Forfeits": player["DC's/Forfeits"],
            "Championships": player["Championships"],
            "Runner-ups": player["Runner-ups"],
            "Third Places": player["Third Places"],
            "Playoff Appearances": player["Playoff Appearances"],
            "Playoff Rate": player["Playoff Rate"]
        }
        return history

    @commands.command(name='player_history')
    async def show_player_history(self, ctx, *, player_name: str):
        history = self.get_player_history(player_name)

        if not history:
            await ctx.send(f"No historical data found for player '{player_name}'!")
            return

        rating = self.calculate_player_rating(history)
        embed = discord.Embed(
            title=f"Historical Results: {player_name}",
            color=discord.Color.purple()
        )
        for stat, value in history.items():
            embed.add_field(name=stat, value=value, inline=True)

        embed.add_field(name="Rating", value=rating, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='historical_leaderboard')
    async def show_leaderboard(self, ctx):
        leaderboard = self.generate_leaderboard()
        embed = discord.Embed(title="Top Players Leaderboard", color=discord.Color.gold())
        
        for rank, player in enumerate(leaderboard[:15], 1):
            embed.add_field(
                name=f"{rank}. {player['Player']}",
                value=f"Rating: {player['Rating']}, Win %: {player['Win %']}, K/D Ratio: {player['K/D ratio']}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    def generate_metric_leaderboard(self, metric_key):
        """Generates leaderboard based on a specific metric."""
        with open(self.player_data_path, 'r') as f:
            players_data = json.load(f)

        def parse_metric(value):
            if metric_key in ["Win %", "Playoff Rate"]:
                return float(value.strip('%')) if value else 0.0
            else:
                return float(value) if value else 0.0

        leaderboard = [
            {
                'Player': player['Player'],
                metric_key: parse_metric(player.get(metric_key, '0')),
                'Games Played': int(player.get('Games Played', 0) or 0)
            }
            for player in players_data
            if int(player.get('Games Played', 0) or 0) >= 20
        ]

        leaderboard.sort(key=lambda x: x[metric_key], reverse=True)
        return leaderboard

    @commands.command(name='win_percentage_leaderboard')
    async def win_percentage_leaderboard(self, ctx):
        """Display leaderboard by Win %."""
        leaderboard = self.generate_metric_leaderboard("Win %")
        embed = discord.Embed(title="Top Players by Win %", color=discord.Color.blue())
        
        for rank, player in enumerate(leaderboard[:10], 1):
            embed.add_field(
                name=f"{rank}. {player['Player']}",
                value=f"Win %: {player['Win %']}%",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    @commands.command(name='kd_ratio_leaderboard')
    async def kd_ratio_leaderboard(self, ctx):
        """Display leaderboard by K/D Ratio."""
        leaderboard = self.generate_metric_leaderboard("K/D ratio")
        embed = discord.Embed(title="Top Players by K/D Ratio", color=discord.Color.purple())
        
        for rank, player in enumerate(leaderboard[:10], 1):
            embed.add_field(
                name=f"{rank}. {player['Player']}",
                value=f"K/D Ratio: {player['K/D ratio']}",
                inline=False
            )
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(HistoricalResults(bot))
