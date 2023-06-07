import discord
from discord.ext import commands
import sqlite3

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
    if balance < 0: # no negative balances
        balance = 0
    c.execute("INSERT OR REPLACE INTO balances (user_id, balance) VALUES (?, ?)", (user_id, balance))
    conn.commit()

# sqlite
conn = sqlite3.connect('balances.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS balances
             (user_id INTEGER PRIMARY KEY, balance INTEGER)''')
conn.commit()

roles = {
    'Novice': 1000,
    'Intermediate': 5000,
    'Experienced': 10000,
    'Seasoned': 20000,
    'Master': 30000,
    'Grandmaster': 50000,
    'Legend': 80000,
    'Mythical': 123456
}
# displays shop of roles
@commands.command(name='roleshop',help='Displays the roles available for purchase.')
async def roleshop(ctx):
    roleshop_message = "```Available Roles:\n\n"
    for role_name, role_price in roles.items():
        roleshop_message += f"{role_name}: {role_price} dabloons\n"
    roleshop_message += "```"
    await ctx.send(roleshop_message)
# buy roles here
@commands.command(name='buy',help='Purchase a role from the role shop.')
async def buy(ctx, *, role_name: str):
    role_name = role_name.title()
    if role_name not in roles:
        await ctx.send(f"Sorry, the role {role_name} doesn't exist.")
        return
    if discord.utils.get(ctx.author.roles, name=role_name):
        await ctx.send(f"You already have that role, {ctx.author.mention}!")
        return
    dabloons = get_balance(ctx.author.id)
    role_price = roles[role_name]
    if dabloons < role_price:
        await ctx.send("Sorry, you do not have enough dabloons to purchase this role.")
        return
    # Add role to user and deduct dabloons from balance
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    await ctx.author.add_roles(role)
    update_balance(ctx.author.id, dabloons - role_price)
    await ctx.send(f"Congratulations, you have purchased the {role_name} role for {role_price} dabloons!")
# error-handling
@buy.error
async def buy_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Well, what role do you wanna buy?")

def setup(bot):
    bot.add_command(roleshop)
    bot.add_command(buy)