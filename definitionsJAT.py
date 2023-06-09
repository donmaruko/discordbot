import discord
from discord.ext import commands
import requests

@commands.command(name='define', help='Get the definition of a word.')
async def define(ctx, *, word):
    response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
    
    if response.status_code == 200:
        data = response.json()
        if data:
            definitions = data[0]['meanings'][0]['definitions']
            if definitions:
                definition = definitions[0]['definition']
                await ctx.send(f"**{word.capitalize()}**: {definition}")
                return
    await ctx.send(f"Sorry, I can't find a definition for '{word}'.")

@commands.command(name='urban', help='Get the definition of a slang word or phrase from Urban Dictionary.')
async def urban(ctx, *, term):
    response = requests.get(f'https://api.urbandictionary.com/v0/define?term={term}')
    if response.status_code == 200:
        data = response.json()
        if data['list']:
            definition = data['list'][0]['definition']
            example = data['list'][0]['example']
            await ctx.send(f"**{term.capitalize()}**: {definition}\nExample: {example}")
            return
    await ctx.send(f"No definition found for '{term}' on Urban Dictionary.")

def setup(bot):
    bot.add_command(define)
    bot.add_command(urban)