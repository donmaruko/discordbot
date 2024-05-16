from discord.ext import commands
from discord import app_commands
import discord

def setup(bot):
    @bot.tree.command(name='suggest', description="Suggest something to the bot author")
    @app_commands.describe(suggestion='What will be your suggestion?')
    async def suggest(interaction: discord.Interaction, suggestion: str):
        if len(suggestion) >= 200:
            await interaction.response.send_message("Please keep your suggestion within 200 characters, thank you..", ephemeral=True)
            return

        with open('suggestions.txt', 'a') as file:
            file.write(f'{interaction.user.name}#{interaction.user.discriminator} ({interaction.user.id}): {suggestion}\n')

        print(f'Suggestion added: {suggestion}')  # Debugging statement
        await interaction.response.send_message(f'Thank you for your suggestion, {interaction.user.mention}!')

    @bot.tree.command(name='readsuggestions', description="Admin only, reads user suggestions")
    @commands.has_permissions(administrator=True)
    async def readsuggestions(interaction: discord.Interaction):
        with open('suggestions.txt', 'r') as file:
            suggestions = file.readlines()
        await interaction.response.send_message("Here are the suggestions:\n" + "".join(suggestions), ephemeral=True)

    @bot.tree.command(name="clearsuggestions", description="Clear a number of suggestions")
    @app_commands.describe(num="How many suggestions to clear?")
    @commands.has_permissions(administrator=True)
    async def clearsuggestions(interaction: discord.Interaction, num: int):
        with open('suggestions.txt', 'r+') as file:
            lines = file.readlines()
            file.seek(0)  # Move the file pointer to the beginning
            file.truncate()  # Clear the file content
            file.writelines(lines[num:])  # Write back the remaining lines after the specified number
        await interaction.response.send_message(f'{num} suggestions cleared successfully!', ephemeral=True)