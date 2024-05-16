import discord
from discord.ext import commands
from discord import app_commands
import requests

def setup(bot):
    @bot.tree.command(name="define", description="Searches the definition of a word")
    @app_commands.describe(word="The word you want to define")
    async def define(interaction: discord.Interaction, word: str):
        response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
        
        if response.status_code == 200:
            data = response.json()
            if data:
                definitions = data[0]['meanings'][0]['definitions']
                if definitions:
                    definition = definitions[0]['definition']
                    await interaction.response.send_message(f"**{word.capitalize()}**: {definition}")
                    return
        await interaction.response.send_message(f"Sorry, I can't find a definition for '{word}'.")

    @bot.tree.command(name="urban", description="Searches the Urban Dictionary definition of a word")
    @app_commands.describe(term="The term you want to define")
    async def urban(interaction: discord.Interaction, term: str):
        response = requests.get(f'https://api.urbandictionary.com/v0/define?term={term}')
        if response.status_code == 200:
            data = response.json()
            if data['list']:
                definition = data['list'][0]['definition']
                example = data['list'][0]['example']
                await interaction.response.send_message(f"**{term.capitalize()}**: {definition}\nExample: {example}")
                return
        await interaction.response.send_message(f"No definition found for '{term}' on Urban Dictionary.")