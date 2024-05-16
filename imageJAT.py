import discord
from discord.ext import commands
from discord import app_commands
import random
import requests
from bs4 import BeautifulSoup

def setup(bot):
    @bot.tree.command(name='image', description="Searches a number of images (1-4)")
    @app_commands.describe(num_results="How many images should I search?",keyword='What should I search for?')
    async def image(interaction: discord.Interaction, num_results: int, keyword: str):
        if num_results > 4:
            await interaction.response.send_message("Whoops, you can't search more than 4 images!")
            return

        # Make a request to Google Images
        response = requests.get(f'https://www.google.com/search?q={keyword}&tbm=isch&tbs=isz:l')
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            images = soup.find_all('img')
            if images:
                # Select random images from the search results
                random_images = random.sample(images, min(num_results, len(images)))
                # Acknowledge the interaction
                await interaction.response.send_message("Here are your images:")
                for image in random_images:
                    image_url = image['src']
                    # Send each image to the user
                    await interaction.followup.send(image_url)
            else:
                await interaction.response.send_message("No images found for the given keyword.")
        else:
            await interaction.response.send_message("Failed to fetch images. Please try again later.")