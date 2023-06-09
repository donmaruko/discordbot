import discord
from discord.ext import commands
import sqlite3

# sqlite
conn = sqlite3.connect('balances.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS balances
             (user_id INTEGER PRIMARY KEY, balance INTEGER)''')
conn.commit()

# sqlite stuff
def get_balance(user_id):
    c.execute("SELECT balance FROM balances WHERE user_id=?", (str(user_id),)) # convert user id to string
    result = c.fetchone()
    if result is not None:
        return result[0]
    else:
        return None
# function to update the user's balance in the database
def update_balance(user_id, balance):
    if balance < 0:  # no negative balances
        balance = 0
    c.execute("INSERT OR REPLACE INTO balances (user_id, balance) VALUES (?, ?)", (str(user_id), balance))
    conn.commit()

# check user balance
@commands.command(aliases=['bal'], help="Checks for a user's balance.")
async def balance(ctx):
    balance = get_balance(ctx.author.id)
    if balance == 0:
        await ctx.send(f"{ctx.author.mention}'s balance is {balance} dabloons. Oof! Use the mercy command, I almost feel bad for you.")
    else:
        await ctx.send(f"{ctx.author.mention}'s balance is {balance} dabloons.")
# leaderboard
@commands.command(aliases=['lb'], help='Gives the balance leaderboard of the users in the server.')
async def players(ctx):
    # Get all members in the server
    members = ctx.guild.members
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
    await ctx.send(balance_str)

def setup(bot):
    bot.add_command(balance)
    bot.add_command(players)