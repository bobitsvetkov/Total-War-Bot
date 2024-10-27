import json
import os
import datetime
import discord
import logging
from discord.ext import commands
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TeamLeaderboardSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.k_factor = 32  # K-value for Elo rating
        self.json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'elo_rating.json')

        # Load the initial data from the JSON file
        with open(self.json_path) as f:
            self.unit_data = json.load(f)

    def calculate_expected_score(self, team_rating: float, opponent_rating: float) -> float:
        """Calculate expected score for a team"""
        return 1 / (1 + 10 ** ((opponent_rating - team_rating) / 400))

    def update_elo(self, winning_team: Dict, losing_team: Dict):
        """Update Elo ratings for the winning and losing teams"""
        expected_winner = self.calculate_expected_score(winning_team["Elo Rating"], losing_team["Elo Rating"])
        expected_loser = self.calculate_expected_score(losing_team["Elo Rating"], winning_team["Elo Rating"])

        # Update ratings
        winning_team["Elo Rating"] += self.k_factor * (1 - expected_winner)
        losing_team["Elo Rating"] += self.k_factor * (0 - expected_loser)

    def parse_teams(self, match_details: str):
        """Parse team names from the input using multiple separators"""
        match_details_lower = match_details.lower()
        if ' vs ' in match_details_lower:
            team_a, team_b = match_details.split(' vs ', 1)
        elif ' versus ' in match_details_lower:
            team_a, team_b = match_details.split(' versus ', 1)
        elif ' and ' in match_details_lower:
            team_a, team_b = match_details.rsplit(' and ', 1)
        else:
            parts = [p.strip() for p in match_details.split(',')]
            if len(parts) == 2:
                team_a, team_b = parts
            else:
                raise ValueError("Unable to parse team names. Use 'vs', 'versus', 'and', or ',' as separators.")
        return team_a.strip(), team_b.strip()

    @commands.command(name='record_match')
    async def record_match(self, ctx, *, match_details: str):
        """Record the result of a match between two teams using flexible separators"""
        try:
            logging.debug(f"Starting record_match with input: {match_details}")

            # Parse team names
            try:
                winning_team_name, losing_team_name = self.parse_teams(match_details)
            except ValueError as e:
                await ctx.send(str(e))
                return

            logging.debug(f"Winning team: {winning_team_name}, Losing team: {losing_team_name}")
            teams = self.unit_data["teams"]

            # Look up the winning and losing teams
            winning_team = next((t for t in teams if t['Team Name'].lower() == winning_team_name.lower()), None)
            losing_team = next((t for t in teams if t['Team Name'].lower() == losing_team_name.lower()), None)

            if not winning_team:
                logging.warning(f"Winning team not found: {winning_team_name}")
            if not losing_team:
                logging.warning(f"Losing team not found: {losing_team_name}")

            if not winning_team or not losing_team:
                await ctx.send("One or both teams not found!")
                return

            # Update Elo ratings
            self.update_elo(winning_team, losing_team)

            # Record the match result
            match_date = str(datetime.date.today())
            winning_team["Matches"].append({"Opponent": losing_team["Team Name"], "Result": "Win", "Date": match_date})
            losing_team["Matches"].append({"Opponent": winning_team["Team Name"], "Result": "Loss", "Date": match_date})

            # Save updated data back to JSON
            with open(self.json_path, 'w') as f:
                json.dump(self.unit_data, f, indent=4)

            await ctx.send(f"Match recorded: {winning_team_name} wins against {losing_team_name}!")

        except Exception as e:
            logging.error("Error in record_match command", exc_info=True)
            await ctx.send(f"Error recording match: {str(e)}")

    @commands.command(name='show_top_teams')
    async def show_top_teams(self, ctx):
        """Display the top 10 teams by Elo rating in an embed"""
        try:
            teams = self.unit_data["teams"]

            # Sort teams by Elo rating in descending order
            sorted_teams = sorted(teams, key=lambda x: x["Elo Rating"], reverse=True)[:10]

            # Create embed for top 10 teams
            embed = discord.Embed(title="Top 10 Teams by Elo Rating", color=discord.Color.blue())
            for team in sorted_teams:
                embed.add_field(name=team["Team Name"], value=f"Elo Rating: {team['Elo Rating']:.2f}", inline=False)

            await ctx.send(embed=embed)
        except Exception as e:
            logging.error("Error in show_top_teams command", exc_info=True)
            await ctx.send("Error displaying top teams.")

def setup(bot):
    bot.add_cog(TeamLeaderboardSystem(bot))
