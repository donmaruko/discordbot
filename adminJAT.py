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
        return 0
# function to update the user's balance in the database
def update_balance(user_id, balance):
    if balance < 0:  # no negative balances
        balance = 0
    c.execute("INSERT OR REPLACE INTO balances (user_id, balance) VALUES (?, ?)", (str(user_id), balance))
    conn.commit()

# mercy for broke people
@commands.command(name='mercy', help='Gives a truly broke user 500 dabloons.')
async def mercy(ctx):
    balance = get_balance(ctx.author.id)
    if balance == 0:
        balance += 500
        update_balance(ctx.author.id, balance)
        await ctx.send(f"500 dabloons has been added into {ctx.author.mention}'s balance, don't mess yourself up again. :/")
    else:
        await ctx.send("Sorry, you can only be granted 500 dabloons if you're TRULY BROKE.")

@commands.command(name='grant', help='Admin only, grants a user a given amount of dabloons.')
@commands.has_permissions(administrator=True)
async def grant(ctx, user: discord.Member = None, amount: int = None):
    if user is None and amount is None:
        await ctx.send("Who shall I grant dabloons to? Specify the user and amount, please.")
        return
    if user is None:
        await ctx.send("Who shall I grant dabloons to?")
        return
    if amount is None:
        await ctx.send(f"How many dabloons do you want to grant to {user.name}?")
        return
    balance = get_balance(user.id)
    balance += amount
    update_balance(user.id, balance)
    await ctx.send(f"Ckckck.. you dirty cheater, {user.name}.")
@grant.error
async def grant_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    else:
        await ctx.send("Please input the correct arguments, e.g., $grant @user 1.")

# admin only
@commands.command(name='punish', help='Removes 5000 dabloons from a given user.')
@commands.has_permissions(administrator=True)
async def punish(ctx, user: discord.Member = None):
    if not user:
        await ctx.send("Who shall I punish?")
        return
    balance = get_balance(user.id)
    balance -= 5000
    update_balance(user.id, balance)
    await ctx.send(f"You think you're slick, {user.name}?")
@punish.error
async def punish_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    else:
        await ctx.send("Oops! Something went wrong. Please try again.")

def setup(bot):
    bot.add_command(mercy)
    bot.add_command(grant)
    bot.add_command(punish)