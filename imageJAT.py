import discord
from discord.ext import commands
import random
import requests
from bs4 import BeautifulSoup

@commands.command(name='image', help='Displays a specified number of random images based on a given keyword')
async def image(ctx, *, query):
    try:
        num_results, keyword = map(str.strip, query.split(' ', 1))
        num_results = int(num_results)
    except ValueError:
        await ctx.send("Please use the format `$image (number of images) (keyword)`.")
        return

    if num_results > 4:
        await ctx.send("Whoops, you can't search more than 4 images!")
        return

    # Make a request to Google Images
    response = requests.get(f'https://www.google.com/search?q={keyword}&tbm=isch')
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img')
        if images:
            # Select random images from the search results
            random_images = random.sample(images, min(num_results, len(images)))
            for image in random_images:
                image_url = image['src']
                # Send each image to the user
                await ctx.send(image_url)
        else:
            await ctx.send("No images found for the given keyword.")
    else:
        await ctx.send("Failed to fetch images. Please try again later.")

def setup(bot):
    bot.add_command(image)