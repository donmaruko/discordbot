import discord
from discord.ext import commands

# poll command
@commands.command(name='poll', help='Create a poll with any number of options.')
async def poll(ctx, *options: str):
    if len(options) < 2:
        await ctx.send("Please provide at least two options for the poll.")
        return

    # Generate the poll message content
    poll_content = f"{ctx.author.mention} has created a poll!\n\n"
    for i, option in enumerate(options, start=1):
        poll_content += f"Option {i}: {option}\n"

    # Send the poll message
    poll_message = await ctx.send(poll_content)

    # Add reactions to the poll message
    for i in range(1, len(options) + 1):
        await poll_message.add_reaction(f"{i}\N{combining enclosing keycap}")

def setup(bot):
    bot.add_command(poll)
