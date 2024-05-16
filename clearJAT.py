from discord import app_commands
import discord

def setup(bot):
    @bot.tree.command(name='clear', description="Clears 1-25 messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    @app_commands.describe(amount="How many messages to clear?")
    async def clear(interaction: discord.Interaction, amount: int):
        # Acknowledge the interaction first if the operation might take longer
        await interaction.response.defer(ephemeral=True)

        try:
            if 0 < amount <= 25:
                await interaction.channel.purge(limit=amount)
                await interaction.followup.send(f"Cleared {amount} messages.", ephemeral=True)
            else:
                await interaction.followup.send("Please provide a number between 1 and 25.", ephemeral=True)
        except discord.errors.NotFound:
            print("Interaction not found or already resolved.")