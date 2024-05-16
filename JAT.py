
import discord,os
from discord import app_commands
from discord.ext import commands
import adminJAT, balanceJAT, blackjackJAT, connect4JAT, sayJAT, clearJAT, musicJAT, caesarJAT
import definitionsJAT, imageJAT, rolesJAT, helloJAT, suggestJAT, setstatusJAT, helpJAT, avatarJAT
import stonksJAT
from stonksJAT import change_stonk_price

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

# bot is online !
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name}')
    activity = discord.Activity(type=discord.ActivityType.playing, name="with your feelings ;)")
    await bot.change_presence(activity=activity)
    change_stonk_price.start()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name='ping', description="Shows the user their ping")
async def ping(interaction: discord.Interaction):
    bot_latency = round(bot.latency*1000)
    await interaction.response.send_message(f"Pong!... {bot_latency}ms",ephemeral=True)

# welcomes new members to the server
@bot.event
async def on_member_join(member):
    # find the welcome channel
    welcome_channel = discord.utils.get(member.guild.channels, name='welcome')
    if welcome_channel is not None:
        # send the welcome message
        await welcome_channel.send(f"Welcome {member.mention} to the server!")

@bot.event
async def on_voice_state_update(member, before, after):
    # Check if the bot is connected to a voice channel
    if bot.voice_clients:
        # Check if the bot is the only member in the voice channel
        voice_channel = bot.voice_clients[0].channel
        if len(voice_channel.members) == 1 and bot.user in voice_channel.members:
            # Disconnect the bot from the voice channel
            await bot.voice_clients[0].disconnect()

# commands go here
adminJAT.setup(bot)
balanceJAT.setup(bot)
blackjackJAT.setup(bot)
connect4JAT.setup(bot)
definitionsJAT.setup(bot)
helloJAT.setup(bot)
imageJAT.setup(bot)
rolesJAT.setup(bot)
suggestJAT.setup(bot)
sayJAT.setup(bot)
clearJAT.setup(bot)
setstatusJAT.setup(bot)
musicJAT.setup(bot)
helpJAT.setup(bot)
caesarJAT.setup(bot)
avatarJAT.setup(bot)
stonksJAT.setup(bot)

# error-handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        print(error)
        await ctx.send(f"That command doesn't exist, {ctx.author.mention}, make sure to also use proper capitalization.")
    elif isinstance(error, commands.MissingRequiredArgument):
        print(error)
        await ctx.send(f"Please provide all required arguments for the command, {ctx.author.mention}.")
    elif isinstance(error, commands.BadArgument):
        print(error)
        await ctx.send(f"Invalid argument provided, {ctx.author.mention}.")
    else:
        print(error)  # Print the error message to the console
        await ctx.send(f"An error occurred while executing the command, {ctx.author.mention}.")

file_path = os.path.join(os.path.dirname(__file__), 'token.txt')
with open(file_path, 'r') as file:
    token = file.read().strip()
bot.run(token)
