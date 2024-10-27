import discord
from discord.ext import commands
import json
import os

class PlayerProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.profile_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'player_profiles.json')
        if not os.path.exists(self.profile_data_path):
            with open(self.profile_data_path, 'w') as f:
                json.dump({}, f)

    def load_profiles(self):
        with open(self.profile_data_path, 'r') as f:
            return json.load(f)

    def save_profiles(self, profiles):
        with open(self.profile_data_path, 'w') as f:
            json.dump(profiles, f, indent=4)

    @commands.command(name='set_profile')
    async def set_profile(self, ctx, key: str = None, *, value: str = None):
        """Set or update your player profile. Usage: !setprofile <key> <value>"""
        if key is None:
            help_message = (
                "Usage: `!set_profile <key> <value>`\n"
                "Available keys:\n"
                "`fav_faction`: Set your favorite faction.\n"
                "`fav_units`: Set your favorite unit (comma-separated).\n"
                "`bio`: Set your bio.\n"
                "`playstyle`: Set your playstyle.\n"
                "`fav_map`: Set your favorite map.\n"
                "Example: `!set_profile favorite_faction Odrysian Kingdom`"
            )
            await ctx.send(help_message)
            return

        profiles = self.load_profiles()
        user_id = str(ctx.author.id)

        # Ensure the profile only gets updated for the user invoking the command
        if user_id not in profiles:
            profiles[user_id] = {}

        # Map the key to the actual profile property
        key_mapping = {
            'fav_faction': 'Faction',
            'fav_units': 'Favorite Units',
            'bio': 'Bio',
            'playstyle': 'Playstyle',
            'fav_map': 'Favorite Map'
        }

        # Check if the key is valid (case insensitive)
        normalized_key = key.lower()
        if normalized_key in key_mapping:
            if normalized_key == 'fav_units' and value:
                # Join the favorite units into a single string
                profiles[user_id][key_mapping[normalized_key]] = ', '.join(value.split(',')).strip()  # Split and join to ensure formatting
            else:
                profiles[user_id][key_mapping[normalized_key]] = value or "N/A"  # Set to "N/A" if no value is provided

            profiles[user_id]['Last Updated'] = str(ctx.message.created_at)
            self.save_profiles(profiles)

            await ctx.send(f"Your profile has been updated: {key_mapping[normalized_key]} set to '{profiles[user_id][key_mapping[normalized_key]]}'!")
        else:
            await ctx.send(f"Invalid key! Use one of the following: {', '.join(key_mapping.keys())}.")

    @commands.command(name='view_profile')
    async def view_profile(self, ctx, member: discord.Member = None):
        """View a player's profile."""
        profiles = self.load_profiles()
        user_id = str((member or ctx.author).id)

        if user_id not in profiles:
            await ctx.send("Profile not found! Use `!set_profile` to create one.")
            return

        profile = profiles[user_id]
        embed = discord.Embed(
            title=f"{member.display_name}'s Profile" if member else f"Your Profile",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Faction", value=profile.get("Faction", "N/A"), inline=True)
        embed.add_field(name="Favorite Units", value=profile.get("Favorite Units", "N/A"), inline=True)  # Changed to "Favorite Unit"
        embed.add_field(name="Bio", value=profile.get("Bio", "N/A"), inline=False)
        embed.add_field(name="Playstyle", value=profile.get("Playstyle", "N/A"), inline=True)
        embed.add_field(name="Favorite Map", value=profile.get("Favorite Map", "N/A"), inline=True)
        embed.set_footer(text=f"Last Updated: {profile.get('Last Updated')}")

        await ctx.send(embed=embed)
