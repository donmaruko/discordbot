import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from stonksJAT import get_stonks

conn = sqlite3.connect('balances.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS balances
             (user_id INTEGER PRIMARY KEY, balance INTEGER)''')
conn.commit()

# SQLite functions
def get_balance(user_id):
    c.execute("SELECT balance FROM balances WHERE user_id=?", (str(user_id),))
    result = c.fetchone()
    if result is not None:
        return result[0]
    else:
        return None

def update_balance(user_id, balance):
    if balance < 0:
        balance = 0
    c.execute("INSERT OR REPLACE INTO balances (user_id, balance) VALUES (?, ?)", (str(user_id), balance))
    conn.commit()

# check user balance
def setup(bot):
    @bot.tree.command(name='bal', description="Checks user balance")
    async def balance(interaction: discord.Interaction):
        user_id = interaction.user.id
        balance = get_balance(user_id)
        gneeb_stonks = get_stonks(user_id, 'Gneeb')
        gnorb_stonks = get_stonks(user_id, 'Gnorb')

        message = f"{interaction.user.mention}'s balance is {balance} dabloons\n"
        message += f"{gneeb_stonks} Gneeb stonks\n{gnorb_stonks} Gnorb stonks"

        if balance == 0:
            message += "\nOof! Use the mercy command, I almost feel bad for you."
        
        await interaction.response.send_message(message, ephemeral=True)

    # leaderboard
    @bot.tree.command(name='lb', description="Checks server's balance leaderboard")
    @app_commands.describe()
    async def players(interaction: discord.Interaction):
        # Get all members in the server
        members = interaction.guild.members
        # Get the balance for each member and add it to a list
        balances = []
        for member in members:
            balance = get_balance(member.id)
            if balance is None:
                balance = 500
                update_balance(member.id, balance)
            balances.append((member.display_name, balance))
        # Sort the list by balance in descending order
        balances = sorted(balances, key=lambda x: x[1], reverse=True)
        # Format the list as a string and send it as a message
        balance_str = "Balances:\n"
        for name, balance in balances:
            balance_str += f"{name}: {balance} dabloons\n"
        await interaction.response.send_message(balance_str)