import discord
from discord import app_commands

# Function to perform Caesar cipher encryption
def caesar_cipher(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            shift_amount = shift % 26
            if char.islower():
                start = ord('a')
                result += chr((ord(char) - start + shift_amount) % 26 + start)
            elif char.isupper():
                start = ord('A')
                result += chr((ord(char) - start + shift_amount) % 26 + start)
        else:
            result += char
    return result

# Setup function to add commands to the bot
def setup(bot):
    @bot.tree.command(name='encrypt', description='Encrypts a message using Caesar cipher')
    @app_commands.describe(message='The message to encrypt', shift='The shift for the Caesar cipher')
    async def encrypt(interaction: discord.Interaction, message: str, shift: int):
        if len(message) > 100:
            await interaction.response.send_message("Please limit your message to 100 characters.")
        else:
            encrypted_message = caesar_cipher(message, shift)
            await interaction.response.send_message(f"Encrypted message: {encrypted_message}")