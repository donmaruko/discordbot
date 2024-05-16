import discord
from discord.ext import commands
from discord import app_commands
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

roles = {
    'Pathetic': 1,
    'Novice': 1000,
    'Intermediate': 5000,
    'Experienced': 10000,
    'Seasoned': 20000,
    'Master': 30000,
    'Grandmaster': 50000,
    'Legend': 80000,
    'Mythical': 123456,
    'Divine': 500000,
    'Almighty': 2500000
    # bot name's personal toy: 999999999
}

# displays shop of roles
def setup(bot):
    @bot.tree.command(name='roleshop', description="Lists the roles available to buy")
    @app_commands.describe()
    async def roleshop(interaction: discord.Interaction):
        roleshop_message = "```Available Roles:\n\n"
        for role_name, role_price in roles.items():
            roleshop_message += f"{role_name}: {role_price} dabloons\n"
        roleshop_message += "```"
        await interaction.response.send_message(roleshop_message)

    @bot.tree.command(name='buy', description="Buy a role listed in the role shop")
    @app_commands.describe(role_name="What role shall you buy?")
    async def buy(interaction: discord.Interaction, *, role_name: str):
        role_name = role_name.title()
        if role_name not in roles:
            await interaction.response.send_message(f"Sorry, the role {role_name} doesn't exist.")
            return
        if discord.utils.get(interaction.user.roles, name=role_name):
            await interaction.response.send_message(f"You already have that role, {interaction.user.mention}!")
            return
        dabloons = get_balance(interaction.user.id)
        role_price = roles[role_name]
        if dabloons < role_price:
            await interaction.response.send_message("Sorry, you do not have enough dabloons to purchase this role.")
            return
        # Add role to user and deduct dabloons from balance
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        await interaction.user.add_roles(role)
        update_balance(interaction.user.id, dabloons - role_price)
        await interaction.response.send_message(f"Congratulations, you have purchased the {role_name} role for {role_price} dabloons!")

    @buy.error
    async def buy_error(interaction: discord.Interaction, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await interaction.response.send_message("Well, what role do you wanna buy?")