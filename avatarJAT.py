import discord
from discord import app_commands

def setup(bot):
    @bot.tree.command(name='avatar', description="Grabs the avatar of a user")
    @app_commands.describe(user="The user whose avatar you want to see")
    async def avatar(interaction: discord.Interaction, user: discord.User = None):
        if user is None:
            user = interaction.user
        avatar_url = user.display_avatar.url
        await interaction.response.send_message(f"Here is {user.display_name}'s profile picture:\n{avatar_url}")