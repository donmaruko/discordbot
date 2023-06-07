import discord,os
from discord.ext import commands
import adminJAT, balanceJAT, blackjackJAT, clearJAT
import imageJAT, rolesJAT, helloJAT, pollJAT, musicJAT

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

# bot is online !
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

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
clearJAT.setup(bot)
helloJAT.setup(bot)
imageJAT.setup(bot)
musicJAT.setup(bot)
pollJAT.setup(bot)
rolesJAT.setup(bot)

# error-handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"That command doesn't exist, {ctx.author.mention}, make sure to also use proper capitalization.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide all required arguments.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument.")
    else:
        await ctx.send("An error occurred while executing the command.")

file_path = os.path.join(os.path.dirname(__file__), 'token.txt')
with open(file_path, 'r') as file:
    token = file.read().strip()
bot.run(token)