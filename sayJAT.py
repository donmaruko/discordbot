import discord
from discord import app_commands

def setup(bot):
    @bot.tree.command(name='say', description="Well, says a message")
    @app_commands.describe(thing_to_say="What should I say?")
    async def say(interaction: discord.Interaction, thing_to_say: str):
        await interaction.response.send_message(thing_to_say)