import discord
from discord.ext import commands

@commands.command(name='hello', help='The classic greeting command!')
async def hello(ctx):
    await ctx.send(f'Hey, {ctx.author.mention}!')

def setup(bot):
    bot.add_command(hello)