import discord
from discord.ext import commands
import random,asyncio,youtube_dl,spotipy
from youtube_search import YoutubeSearch

queue = []

@commands.command(name='play', help='Play a YouTube video via link.')
async def play(ctx, url):
    # Check if the user is in a voice channel
    if ctx.author.voice is None:
        await ctx.send("You are not connected to a voice channel.")
        return
    # Get the voice channel that the user is in
    voice_channel = ctx.author.voice.channel
    # Check if the bot is already connected to a voice channel
    if ctx.voice_client is None:
        # Connect to the voice channel
        voice_client = await voice_channel.connect()
    else:
        voice_client = ctx.voice_client
    try:
        # Create a youtube_dl extractor
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Extract audio information from the YouTube video
            info = ydl.extract_info(url, download=False)
            # Get the audio stream URL
            audio_url = info['formats'][0]['url']
        # Create an FFmpegPCMAudio object with the audio stream URL
        audio_source = discord.FFmpegPCMAudio(audio_url)
        # Play the audio source in the voice channel
        voice_client.play(audio_source)
        # Send a message to indicate that the video is now playing
        await ctx.send(f'Now playing: {info["title"]}')
    except Exception as e:
        print(f'An error occurred: {e}')
        await ctx.send('An error occurred while playing the video.')
    # Check if there are any videos in the queue
    if queue and not voice_client.is_playing():
        # Get the next video URL from the queue
        next_url = queue.pop(0)
        # Play the next video
        await play(ctx, next_url)
    elif not queue and not voice_client.is_playing():
        await ctx.send('The queue is now empty.')

@commands.command(name='pause', help='Pause a YouTube video.')
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Pausing...")
    else:
        await ctx.send("No audio is currently playing.")

@commands.command(name='resume', help='Resume a YouTube video.')
async def resume(ctx):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Resumed!")
    else:
        await ctx.send("Playback is not paused.")

@commands.command(name='leave', help='Stop playing a YouTube video.')
async def leave(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await ctx.send("Buh-bye!")
    else:
        await ctx.send("I'm not connected to a voice channel.")

@commands.command(name='queue', help='Queue a YouTube video.')
async def queuevid(ctx, url):
    # Add the video URL to the queue
    queue.append(url)
    await ctx.send(f'Video queued: {url}')

@commands.command(name='skip', help='Skip the currently playing YouTube video.')
async def skip(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Skipping the current video...")
    elif voice_client.is_paused():
        await ctx.send("The video is currently paused. Use the $resume command to resume playback.")
    else:
        await ctx.send("No audio is currently playing.")
    # Check if there are any videos in the queue
    if queue:
        # Get the next video URL from the queue
        next_url = queue.pop(0)
        # Play the next video if the voice channel is connected
        if voice_client.is_connected():
            await play(ctx, next_url)
        else:
            queue.insert(0, next_url)  # Re-insert the skipped video back to the front of the queue

@commands.command(name='clearq', help='Clear the queue.')
async def clearq(ctx):
    queue.clear()
    await ctx.send("The queue has been cleared.")

@commands.command(name='showq', help='Show the current queue.')
async def showq(ctx):
    if queue:
        queue_list = '\n'.join(queue)
        await ctx.send(f'Current Queue:\n{queue_list}')
    else:
        await ctx.send('The queue is currently empty.')

@commands.command(name='shuffleq', help='Shuffle the queue.')
async def shuffleq(ctx):
    if len(queue) < 2:
        await ctx.send("The queue must have at least 2 videos to shuffle.")
    else:
        random.shuffle(queue)
        queue_list = '\n'.join(queue)
        await ctx.send(f'The queue has been shuffled:\n{queue_list}')

loop_flag = False
looped_video = None
@commands.command(name='loop', help='Toggle looping of the currently playing YouTube video.')
async def loop(ctx):
    global loop_flag, looped_video
    voice_client = ctx.guild.voice_client
    if voice_client.is_playing():
        if loop_flag:
            loop_flag = False
            looped_video = None
            await ctx.send("Looping disabled.")
        else:
            loop_flag = True
            looped_video = ctx.voice_client.source
            await ctx.send("Looping enabled.")
    else:
        await ctx.send("No audio is currently playing.")
@commands.command(name='unloop', help='Disable looping of the currently playing YouTube video.')
async def unloop(ctx):
    global loop_flag, looped_video
    if loop_flag:
        loop_flag = False
        looped_video = None
        await ctx.send("Looping disabled.")
    else:
        await ctx.send("Looping is already disabled.")

@commands.command(name='current', help='Check the currently playing song.')
async def current(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        current_song = voice_client.source.title
        await ctx.send(f'Currently playing: {current_song}')
    else:
        await ctx.send('No audio is currently playing.')

@commands.command(name='search', help='Search for a YouTube video.')
async def search(ctx, query):
    # Perform the YouTube search using the query
    results = YoutubeSearch(query, max_results=5).to_dict()
    # Check if there are any search results
    if not results:
        await ctx.send("No search results found.")
        return
    # Create a formatted list of search results
    search_list = ""
    for i, video in enumerate(results, start=1):
        search_list += f"{i}. {video['title']}\n"
    # Send the search results to the user
    await ctx.send(f"Search results for '{query}':\n{search_list}\nEnter the number of the video you want to play.")
    try:
        # Wait for the user's response
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        response = await ctx.bot.wait_for('message', check=check, timeout=30)
        # Validate and process the user's response
        video_index = int(response.content)
        if video_index < 1 or video_index > len(results):
            await ctx.send("Invalid selection.")
            return
        # Get the selected video URL
        video_url = f"https://www.youtube.com/watch?v={results[video_index-1]['id']}"
        # Check if there is a current video playing
        if ctx.voice_client and ctx.voice_client.is_playing():
            # Add the selected video URL to the queue
            queue.append(video_url)
            await ctx.send(f"Video queued: {video_url}")
        else:
            # Play the selected video directly
            await play(ctx, video_url)
    except asyncio.TimeoutError:
        await ctx.send("No response received. Search canceled.")
    except ValueError:
        await ctx.send("Invalid input. Search canceled.")

def setup(bot):
    bot.add_command(play)
    bot.add_command(pause)
    bot.add_command(resume)
    bot.add_command(leave)
    bot.add_command(queuevid)
    bot.add_command(skip)
    bot.add_command(clearq)
    bot.add_command(showq)
    bot.add_command(shuffleq)
    bot.add_command(loop)
    bot.add_command(unloop)
    bot.add_command(search)
    bot.add_command(current)