import discord
import sqlite3
import random
import asyncio
from discord.ext import commands, tasks
from discord import app_commands

# Database setup
conn = sqlite3.connect('balances.db')
c = conn.cursor()

# Create tables for balances and stonks
c.execute('''CREATE TABLE IF NOT EXISTS balances
             (user_id INTEGER PRIMARY KEY, balance INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS stonks
             (user_id INTEGER, stonk_type TEXT, stonks INTEGER, PRIMARY KEY (user_id, stonk_type))''')
c.execute('''CREATE TABLE IF NOT EXISTS stonk_price
             (stonk_type TEXT PRIMARY KEY, price INTEGER)''')

# Initialize stonk prices if not already initialized
stonks_initial_prices = {'Gneeb': 100, 'Gnorb': 250, 'Porp': 1500, 'Alethea': 750, 'Pakuwon': 20000, 'Santoso': 1000000, 'Veron': 2}
for stonk, price in stonks_initial_prices.items():
    c.execute('''INSERT OR IGNORE INTO stonk_price (stonk_type, price) VALUES (?, ?)''', (stonk, price))
conn.commit()

# tax system


# Helper functions
def get_balance(user_id):
    c.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if result is not None:
        return result[0]
    else:
        return 0

def update_balance(user_id, balance):
    if balance < 0:
        balance = 0
    c.execute("INSERT OR REPLACE INTO balances (user_id, balance) VALUES (?, ?)", (user_id, balance))
    conn.commit()

def get_stonks(user_id, stonk_type):
    c.execute("SELECT stonks FROM stonks WHERE user_id=? AND stonk_type=?", (user_id, stonk_type))
    result = c.fetchone()
    if result is not None:
        return result[0]
    else:
        return 0

stonk_limits = {
    'Gneeb': 10000,
    'Gnorb': 8000,
    'Porp': 3200,
    'Alethea': 9000,
    'Pakuwon': 2000,
    'Santoso': 30,
    'Veron': 1111}

def update_stonks(user_id, stonk_type, stonks_change):
    current_stonks = get_stonks(user_id, stonk_type)
    new_stonks = current_stonks + stonks_change
    if new_stonks < 0:
        new_stonks = 0
    max_stonks = stonk_limits.get(stonk_type, float('inf'))
    if new_stonks > max_stonks:
        new_stonks = max_stonks
    c.execute("INSERT OR REPLACE INTO stonks (user_id, stonk_type, stonks) VALUES (?, ?, ?)", (user_id, stonk_type, new_stonks))
    conn.commit()

def get_stonk_price(stonk_type):
    c.execute("SELECT price FROM stonk_price WHERE stonk_type=?", (stonk_type,))
    result = c.fetchone()
    if result is not None:
        return result[0]
    else:
        return 100

def set_stonk_price(stonk_type, price):
    c.execute("UPDATE stonk_price SET price = ? WHERE stonk_type = ?", (price, stonk_type))
    conn.commit()

# Task to update stonk prices
@tasks.loop(minutes=1)
async def change_stonk_price():
    stonk_price_ranges = {
        'Gneeb': (50, 150),
        'Gnorb': (125, 625),
        'Porp': (1250, 3150),
        'Alethea': (500, 900),
        'Pakuwon': (15000, 25000),
        'Veron': (1, 2)
    }
    for stonk_type, price_range in stonk_price_ranges.items():
        new_price = random.randint(*price_range)
        set_stonk_price(stonk_type, new_price)

@tasks.loop(minutes=5)
async def change_santoso_price():
    new_price = random.randint(900000, 1350000)
    set_stonk_price('Santoso', new_price)

def setup(bot):

    @bot.tree.command(name='stonk', description='Check the current stonk prices')
    async def stonk(interaction: discord.Interaction):
        prices = {stonk_type: get_stonk_price(stonk_type) for stonk_type in stonks_initial_prices.keys()}
        price_message = "\n".join([f"Current {stonk_type} stonk price is **{price}** dabloons." for stonk_type, price in prices.items()])
        await interaction.response.send_message(price_message, ephemeral=True)

    @bot.tree.command(name='buystonk', description='Buy stonks')
    @app_commands.describe(stonk_type='Type of stonk to buy', amount='Number of stonks to buy or "max" to buy the maximum you can afford')
    async def buystonk(interaction: discord.Interaction, stonk_type: str, amount: str):
        stonk_type = stonk_type.capitalize()
        if stonk_type not in stonks_initial_prices:
            await interaction.response.send_message(f"Invalid stonk type: {stonk_type}.", ephemeral=True)
            return
        
        user_id = interaction.user.id
        price = get_stonk_price(stonk_type)
        balance = get_balance(user_id)
        current_stonks = get_stonks(user_id, stonk_type)
        max_stonks = stonk_limits.get(stonk_type, float('inf'))

        if amount.lower() == "max":
            amount = min(balance // price, max_stonks - current_stonks)
        else:
            amount = int(amount)
        
        if current_stonks + amount > max_stonks:
            amount = max_stonks - current_stonks
        
        total_cost = price * amount

        if balance >= total_cost:
            update_balance(user_id, balance - total_cost)
            update_stonks(user_id, stonk_type, amount)
            await interaction.response.send_message(f'You bought {amount} {stonk_type} stonks for {total_cost} dabloons.', ephemeral=True)
        else:
            await interaction.response.send_message(f'You do not have enough dabloons. You need {total_cost} dabloons but you have {balance}.', ephemeral=True)

    @bot.tree.command(name='sellstonk', description='Sell stonks')
    @app_commands.describe(stonk_type='Type of stonk to sell', amount='Number of stonks to sell or "max" to sell all you have')
    async def sellstonk(interaction: discord.Interaction, stonk_type: str, amount: str):
        stonk_type = stonk_type.capitalize()
        if stonk_type not in stonks_initial_prices:
            await interaction.response.send_message(f"Invalid stonk type: {stonk_type}.", ephemeral=True)
            return

        user_id = interaction.user.id
        price = get_stonk_price(stonk_type)
        current_stonks = get_stonks(user_id, stonk_type)

        if amount.lower() == "max":
            amount = current_stonks
        else:
            amount = int(amount)

        if amount > current_stonks:
            await interaction.response.send_message(f'You do not have enough {stonk_type} stonks. You have {current_stonks} but you tried to sell {amount}.', ephemeral=True)
            return

        total_income = price * amount

        update_stonks(user_id, stonk_type, -amount)  # Reduce the stonks count
        balance = get_balance(user_id)
        update_balance(user_id, balance + total_income)
        await interaction.response.send_message(f'You sold {amount} {stonk_type} stonks for {total_income} dabloons.', ephemeral=True)

    @bot.tree.command(name='clearstonk', description='Admin command to remove stonks from a user')
    @app_commands.describe(user='User to remove stonks from', stonk_type='Type of stonk to remove', amount='Number of stonks to remove')
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(administrator=True)
    async def clearstonk(interaction: discord.Interaction, user: discord.User, stonk_type: str, amount: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        stonk_type = stonk_type.capitalize()
        if stonk_type not in stonks_initial_prices:
            await interaction.response.send_message(f"Invalid stonk type: {stonk_type}.", ephemeral=True)
            return

        user_id = user.id
        current_stonks = get_stonks(user_id, stonk_type)

        if current_stonks >= amount:
            update_stonks(user_id, stonk_type, current_stonks - amount)
            await interaction.response.send_message(f'Removed {amount} {stonk_type} stonks from {user.mention}.', ephemeral=True)
        else:
            await interaction.response.send_message(f'{user.mention} does not have enough {stonk_type} stonks. They have {current_stonks} but you tried to remove {amount}.', ephemeral=True)

    @bot.tree.command(name='transfer', description='Transfer dabloons to another player')
    @app_commands.describe(user='User to transfer dabloons to', amount='Amount of dabloons to transfer')
    async def transfer(interaction: discord.Interaction, user: discord.User, amount: int):
        if amount <= 0:
            await interaction.response.send_message("The transfer amount must be positive.", ephemeral=True)
            return

        sender_id = interaction.user.id
        recipient_id = user.id
        sender_balance = get_balance(sender_id)

        if sender_balance < amount:
            await interaction.response.send_message(f"You do not have enough dabloons. You have {sender_balance} but tried to transfer {amount}.", ephemeral=True)
            return

        recipient_balance = get_balance(recipient_id)
        update_balance(sender_id, sender_balance - amount)
        update_balance(recipient_id, recipient_balance + amount)
        await interaction.response.send_message(f"You have successfully transferred {amount} dabloons to {user.mention}.", ephemeral=True)
