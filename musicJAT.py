import discord
from discord import app_commands
import yt_dlp
from discord.ext import commands
import asyncio

ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch',
    'quiet': True,  # Reduce yt_dlp output
    'no_warnings': True,
}

ytdl = yt_dlp.YoutubeDL(ytdl_opts)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, options='-vn'), data=data)

def setup(bot):
    @bot.tree.command(name='play', description='Play a song from a keyword or URL')
    @app_commands.describe(query="Use keyword search or URL!")
    async def play(interaction: discord.Interaction, query: str):
        if not interaction.user.voice:
            await interaction.response.send_message("You need to be in a voice channel to use this command.", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)

        if not vc:
            vc = await voice_channel.connect()

        await interaction.response.defer()  # Defer the response to avoid timeout

        async with interaction.channel.typing():
            try:
                player = await YTDLSource.from_url(query, loop=bot.loop, stream=True)
                if not vc.is_connected():
                    await voice_channel.connect()

                vc.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
                await interaction.followup.send(f'Alright, now playing {player.title}')  # Use followup to send the message after deferring
            except Exception as e:
                await interaction.followup.send(f'An error occurred: {str(e)}')

    @bot.tree.command(name='pause', description='Pause the currently playing audio')
    async def pause(interaction: discord.Interaction):
        vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if not vc or not vc.is_playing():
            await interaction.response.send_message("No audio is playing currently.", ephemeral=True)
            return
        vc.pause()

    @bot.tree.command(name='resume', description='Resume the paused audio')
    async def resume(interaction: discord.Interaction):
        vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if not vc or not vc.is_paused():
            await interaction.response.send_message("No audio is paused currently.", ephemeral=True)
            return
        vc.resume()

    @bot.tree.command(name='stop', description='Stop the currently playing audio')
    async def stop(interaction: discord.Interaction):
        vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if not vc or not vc.is_playing():
            await interaction.response.send_message("No audio is playing currently.", ephemeral=True)
            return
        vc.stop()

    @bot.tree.command(name='leave', description='Leave the voice channel')
    async def leave(interaction: discord.Interaction):
        vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if not vc:
            await interaction.response.send_message("The bot is not in a voice channel.", ephemeral=True)
            return
        await vc.disconnect()
    
    @bot.tree.command(name='queue', description='Queue a song from a keyword or URL')
    @app_commands.describe(query="Use keyword search or URL!")
    async def queue(interaction: discord.Interaction, query: str):
        if not interaction.user.voice:
            await interaction.response.send_message("You need to be in a voice channel to use this command.", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)

        if not vc:
            vc = await voice_channel.connect()

        await interaction.response.defer()  # Defer the response to avoid timeout

        async with interaction.channel.typing():
            try:
                player = await YTDLSource.from_url(query, loop=bot.loop, stream=True)
                if not vc.is_connected():
                    await voice_channel.connect()

                vc.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
                await interaction.followup.send(f'Added {player.title} to the queue.')  # Use followup to send the message after deferring
            except Exception as e:
                await interaction.followup.send(f'An error occurred: {str(e)}')