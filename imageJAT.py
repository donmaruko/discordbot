import discord
from discord.ext import commands
import random
import requests
from bs4 import BeautifulSoup

@commands.command(name='image', help='Displays a random image based on a given keyword')
async def image(ctx, keyword):
    # Make a request to Google Images
    response = requests.get(f'https://www.google.com/search?q={keyword}&tbm=isch')
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img')
        
        if images:
            # Select a random image from the search results
            image_url = random.choice(images)['src']
            
            # Send the image to the user
            await ctx.send(image_url)
        else:
            await ctx.send("No images found for the given keyword.")
    else:
        await ctx.send("Failed to fetch images. Please try again later.")

def setup(bot):
    bot.add_command(image)