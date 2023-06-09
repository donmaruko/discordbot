import discord
from discord.ext import commands

@commands.command(name='clear', help='Clears a given number of messages.')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = None):
    """Clears a specified amount of messages in the chat."""
    if amount is None:
        await ctx.send("Please specify the number of messages to clear.")
        return
    if amount > 50:
        await ctx.send("Chill, only 50 messages tops!")
        return
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{amount} messages have been cleared.")

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify the number of messages to clear.")
    else:
        raise error

def setup(bot):
    bot.add_command(clear)
