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
stonks_initial_prices = {'Gneeb': 100, 'Gnorb': 1000}
for stonk, price in stonks_initial_prices.items():
    c.execute('''INSERT OR IGNORE INTO stonk_price (stonk_type, price) VALUES (?, ?)''', (stonk, price))
conn.commit()

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

def update_stonks(user_id, stonk_type, stonks):
    if stonks < 0:
        stonks = 0
    c.execute("INSERT OR REPLACE INTO stonks (user_id, stonk_type, stonks) VALUES (?, ?, ?)", (user_id, stonk_type, stonks))
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
        'Gnorb': (500, 3000)
    }
    for stonk_type, price_range in stonk_price_ranges.items():
        new_price = random.randint(*price_range)
        set_stonk_price(stonk_type, new_price)

def setup(bot):
    @bot.tree.command(name='stonk', description='Check the current stonk prices')
    async def stonk(interaction: discord.Interaction):
        prices = {stonk_type: get_stonk_price(stonk_type) for stonk_type in stonks_initial_prices.keys()}
        price_message = "\n".join([f"Current {stonk_type} stonk price is {price} dabloons." for stonk_type, price in prices.items()])
        await interaction.response.send_message(price_message, ephemeral=True)

    @bot.tree.command(name='buystonk', description='Buy stonks')
    @app_commands.describe(stonk_type='Type of stonk to buy', amount='Number of stonks to buy')
    async def buystonk(interaction: discord.Interaction, stonk_type: str, amount: int):
        stonk_type = stonk_type.capitalize()
        if stonk_type not in stonks_initial_prices:
            await interaction.response.send_message(f"Invalid stonk type: {stonk_type}.", ephemeral=True)
            return
        
        user_id = interaction.user.id
        price = get_stonk_price(stonk_type)
        total_cost = price * amount
        balance = get_balance(user_id)

        if balance >= total_cost:
            update_balance(user_id, balance - total_cost)
            current_stonks = get_stonks(user_id, stonk_type)
            update_stonks(user_id, stonk_type, current_stonks + amount)
            await interaction.response.send_message(f'You bought {amount} {stonk_type} stonks for {total_cost} dabloons.', ephemeral=True)
        else:
            await interaction.response.send_message(f'You do not have enough dabloons. You need {total_cost} dabloons but you have {balance}.', ephemeral=True)

    @bot.tree.command(name='sellstonk', description='Sell stonks')
    @app_commands.describe(stonk_type='Type of stonk to sell', amount='Number of stonks to sell')
    async def sellstonk(interaction: discord.Interaction, stonk_type: str, amount: int):
        stonk_type = stonk_type.capitalize()
        if stonk_type not in stonks_initial_prices:
            await interaction.response.send_message(f"Invalid stonk type: {stonk_type}.", ephemeral=True)
            return
        
        user_id = interaction.user.id
        price = get_stonk_price(stonk_type)
        total_income = price * amount
        current_stonks = get_stonks(user_id, stonk_type)

        if current_stonks >= amount:
            update_stonks(user_id, stonk_type, current_stonks - amount)
            balance = get_balance(user_id)
            update_balance(user_id, balance + total_income)
            await interaction.response.send_message(f'You sold {amount} {stonk_type} stonks for {total_income} dabloons.', ephemeral=True)
        else:
            await interaction.response.send_message(f'You do not have enough {stonk_type} stonks. You have {current_stonks} but you tried to sell {amount}.', ephemeral=True)