import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import time

# sqlite
conn = sqlite3.connect('balances.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS balances
             (user_id INTEGER PRIMARY KEY, balance INTEGER)''')
conn.commit()

# Cooldown Manager
class CooldownManager:
    def __init__(self, rate, per):
        self.cooldowns = {}
        self.rate = rate
        self.per = per

    def is_on_cooldown(self, user_id):
        if user_id in self.cooldowns:
            if time.time() - self.cooldowns[user_id] < self.per:
                return True, self.per - (time.time() - self.cooldowns[user_id])
        return False, 0

    def update_cooldown(self, user_id):
        self.cooldowns[user_id] = time.time()

cooldown_manager = CooldownManager(rate=1, per=3600)  # 1 hour cooldown

# Function to get the balance from the database
def get_balance(user_id):
    c.execute("SELECT balance FROM balances WHERE user_id=?", (str(user_id),))
    result = c.fetchone()
    if result is not None:
        return result[0]
    else:
        return 0

# Function to update the user's balance in the database
def update_balance(user_id, balance):
    if balance < 0:  # Ensure no negative balances
        balance = 0
    c.execute("INSERT OR REPLACE INTO balances (user_id, balance) VALUES (?, ?)", (str(user_id), balance))
    conn.commit()

def setup(bot):
    @bot.tree.command(name="mercy", description="Grants a rock-bottom user 500 dabloons")
    async def mercy(interaction: discord.Interaction):
        on_cooldown, retry_after = cooldown_manager.is_on_cooldown(interaction.user.id)
        if on_cooldown:
            await interaction.response.send_message(f"Nuh-uh, don't be greedy now, try again in {retry_after:.2f} seconds.")
            return
        balance = get_balance(interaction.user.id)
        if balance == 0:
            balance += 500
            update_balance(interaction.user.id, balance)
            cooldown_manager.update_cooldown(interaction.user.id)
            await interaction.response.send_message(f"500 dabloons have been added to {interaction.user.mention}'s balance, don't mess yourself up again. :/")
        else:
            await interaction.response.send_message("Sorry, you can only be granted 500 dabloons if you're TRULY BROKE.")

    @bot.tree.command(name="grant", description="Admin only, grants a user a number of dabloons")
    @app_commands.describe(user="The user to grant dabloons to.", amount="The amount of dabloons to grant.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(administrator=True)
    async def grant(interaction: discord.Interaction, user: discord.Member, amount: int):
        balance = get_balance(user.id)
        balance += amount
        update_balance(user.id, balance)
        await interaction.response.send_message(f"Ckckck.. you dirty cheater, {user.name}.")

    @grant.error
    async def grant_error(interaction: discord.Interaction, error):
        if isinstance(error, commands.MissingPermissions):
            await interaction.response.send_message("You do not have permission to use this command.")
        else:
            await interaction.response.send_message("Please input the correct arguments, e.g., /grant @user 1.")

    @bot.tree.command(name="punish", description="Admin only, deducts 5000 dabloons from a user")
    @app_commands.describe(user="The user to punish by deducting 5000 dabloons from their balance.", amount="The amount of dabloons to deduct.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(administrator=True)
    async def punish(interaction: discord.Interaction, user: discord.Member, amount: int):
        balance = get_balance(user.id)
        balance -= amount
        update_balance(user.id, balance)
        await interaction.response.send_message(f"You think you're slick, {user.name}?")

    @punish.error
    async def punish_error(interaction: discord.Interaction, error):
        if isinstance(error, commands.MissingPermissions):
            await interaction.response.send_message("You do not have permission to use this command.")
        else:
            await interaction.response.send_message("Oops! Something went wrong. Please try again.")