import discord
from discord.ext import commands

@commands.command(name='avatar', help='Get the profile picture of a user in the server.')
async def avatar(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author
    try:
        avatar_url = user.avatar_url
        await ctx.send(f"Here is {user.name}'s profile picture:\n{avatar_url}")
    except discord.errors.NotFound:
        await ctx.send("Invalid user. Please mention a valid user.")
def setup(bot):
    bot.add_command(avatar)
