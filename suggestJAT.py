import discord
from discord.ext import commands

@commands.command(name='suggest', help='Suggest something to the bot author.')
async def suggest(ctx, *, suggestion):
    with open('suggestions.txt', 'a') as file:
        file.write(f'{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}): {suggestion}\n')

    print(f'Suggestion added: {suggestion}')  # Debugging statement
    await ctx.send(f'Thank you for your suggestion, {ctx.author.mention}!')

@commands.command(name='readsuggestions', help='Read all the suggestions.')
@commands.has_permissions(administrator=True)
async def readsuggestions(ctx):
    with open('suggestions.txt', 'r') as file:
        suggestions = file.readlines()
    await ctx.send("Here are the suggestions:\n" + "".join(suggestions))

@commands.command(name='clearsuggestions', help='Clear a specified number of suggestions.')
@commands.has_permissions(administrator=True)
async def clearsuggestions(ctx, num: int):
    with open('suggestions.txt', 'r+') as file:
        lines = file.readlines()
        file.seek(0)  # Move the file pointer to the beginning
        file.truncate()  # Clear the file content
        file.writelines(lines[num:])  # Write back the remaining lines after the specified number
    await ctx.send(f'{num} suggestions cleared successfully!')

def setup(bot):
    bot.add_command(suggest)
    bot.add_command(readsuggestions)
    bot.add_command(clearsuggestions)