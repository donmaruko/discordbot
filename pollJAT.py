import discord,asyncio
from discord.ext import commands

@commands.command(name='poll', help='Create a poll with any number of options.')
async def poll(ctx):
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    await ctx.send("How many options do you want for the poll? Please enter a number.")
    try:
        reply = await ctx.bot.wait_for('message', check=check, timeout=60)
        num_options = int(reply.content)
        if num_options < 2:
            await ctx.send("Please provide at least two options for the poll.")
            return
    except ValueError:
        await ctx.send("Invalid input. Please provide a valid number.")
        return
    except asyncio.TimeoutError:
        await ctx.send("Timeout. Please try again.")
        return

    await ctx.send("Please name each option you provided, separating them with commas.")
    try:
        reply = await ctx.bot.wait_for('message', check=check, timeout=60)
        options = reply.content.split(',')
        options = [option.strip() for option in options]
        if len(options) != num_options:
            await ctx.send("The number of options provided does not match the specified number. Please try again.")
            return
    except asyncio.TimeoutError:
        await ctx.send("Timeout. Please try again.")
        return

    poll_content = f"{ctx.author.mention} has created a poll!\n\n"
    for i, option in enumerate(options, start=1):
        poll_content += f"Option {i}: {option}\n"

    poll_message = await ctx.send(poll_content)

    for i in range(1, len(options) + 1):
        await poll_message.add_reaction(f"{i}\N{combining enclosing keycap}")

def setup(bot):
    bot.add_command(poll)