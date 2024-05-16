import discord
from discord import app_commands

def setup(bot):
    activity_types = {
        "playing": discord.ActivityType.playing,
        "streaming": discord.ActivityType.streaming,
        "listening": discord.ActivityType.listening,
        "watching": discord.ActivityType.watching,
        "competing": discord.ActivityType.competing
    }

    @bot.tree.command(name='setstatus', description="Admin only, set a custom status for the bot")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(administrator=True)
    @app_commands.describe(activity_type="Type of activity (playing, streaming, listening to, watching, competing, custom)",
                           status="What shall be the bot's new status?")
    async def setstatus(interaction: discord.Interaction, activity_type: str, status: str):
        if activity_type.lower() == "custom":
            activity = discord.Activity(type=discord.ActivityType.custom, name=status)
        elif activity_type.lower() in activity_types:
            activity = discord.Game(name=status) if activity_type.lower() == "playing" else discord.Activity(type=activity_types[activity_type.lower()], name=status)
        else:
            await interaction.response.send_message("Invalid activity type. Choose from playing, streaming, listening, watching, competing, or custom.", ephemeral=True)
            return

        await bot.change_presence(activity=activity)
        await interaction.response.send_message(f"My status has been updated to: {status} ({activity_type})", ephemeral=True)