import json
import os
import datetime
import logging
from discord.ext import commands
from typing import Dict

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TeamRecordingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.k_factor = 32
        self.json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'elo_rating.json')

        with open(self.json_path) as f:
            self.unit_data = json.load(f)

    def calculate_expected_score(self, team_rating: float, opponent_rating: float) -> float:
        """Calculate expected score for a team"""
        return 1 / (1 + 10 ** ((opponent_rating - team_rating) / 400))

    def update_elo(self, winning_team: Dict, losing_team: Dict, playoff_multiplier: float = 1.0):
        """Update Elo ratings for the winning and losing teams"""
        expected_winner = self.calculate_expected_score(winning_team["Elo Rating"], losing_team["Elo Rating"])
        expected_loser = self.calculate_expected_score(losing_team["Elo Rating"], winning_team["Elo Rating"])

        # Apply multiplier if it's a playoff match
        adjustment = self.k_factor * playoff_multiplier

        # Update ratings
        winning_team["Elo Rating"] += adjustment * (1 - expected_winner)
        losing_team["Elo Rating"] += adjustment * (0 - expected_loser)

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

    def add_team_if_not_exists(self, team_name: str):
        """Add a new team to the data if it doesn't already exist"""
        if not any(team['Team Name'].lower() == team_name.lower() for team in self.unit_data['teams']):
            logging.info(f"Adding new team: {team_name}")
            new_team = {
                "Team Name": team_name,
                "Elo Rating": 1000.0,
                "Matches": []
            }
            self.unit_data["teams"].append(new_team)

    @commands.command(name='record_match')
    @commands.is_owner()
    async def record_match(self, ctx, match_type: str, *, match_details: str):
        """Record the result of a match between two teams, creating teams if they don't exist"""
        try:
            logging.debug(f"Starting record_match with input: {match_type}, {match_details}")

            # Determine playoff multiplier
            playoff_multiplier = 1.5 if match_type.lower() == "playoff" else 1.0

            # Parse team names
            try:
                winning_team_name, losing_team_name = self.parse_teams(match_details)
            except ValueError as e:
                await ctx.send(str(e))
                return

            # Ensure both teams exist in the data
            self.add_team_if_not_exists(winning_team_name)
            self.add_team_if_not_exists(losing_team_name)

            # Look up the winning and losing teams
            teams = self.unit_data["teams"]
            winning_team = next(t for t in teams if t['Team Name'].lower() == winning_team_name.lower())
            losing_team = next(t for t in teams if t['Team Name'].lower() == losing_team_name.lower())

            self.update_elo(winning_team, losing_team, playoff_multiplier=playoff_multiplier)

            # Record the match result
            match_date = str(datetime.date.today())
            winning_team["Matches"].append({"Opponent": losing_team["Team Name"], "Result": "Win", "Date": match_date})
            losing_team["Matches"].append({"Opponent": winning_team["Team Name"], "Result": "Loss", "Date": match_date})

            # Save updated data back to the JSON file
            with open(self.json_path, 'w') as f:
                json.dump(self.unit_data, f, indent=4)

            await ctx.send(f"Match recorded: {winning_team_name} wins against {losing_team_name}!")

        except Exception as e:
            logging.error("Error in record_match command", exc_info=True)
            await ctx.send(f"Error recording match: {str(e)}")

    @record_match.error
    async def record_match_error(self, ctx, error):
        """Handle errors for the record_match command."""
        if isinstance(error, commands.NotOwner):
            await ctx.send("Only my creator can use this command.")
        else:
            await ctx.send("An error occurred while processing the command.")
