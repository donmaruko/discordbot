import discord
import asyncio
import sqlite3
from discord import app_commands

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

class Connect4Game:
    def __init__(self, player1, player2):
        self.board = [['⚪' for _ in range(7)] for _ in range(6)]
        self.players = [player1, player2]
        self.current_player = 0  # index of current player

    def insert_piece(self, column):
        # Adjust column to be 0-indexed
        column -= 1
        # Insert piece in the lowest available row in the specified column
        for row in reversed(range(6)):
            if self.board[row][column] == '⚪':
                self.board[row][column] = '🔴' if self.current_player == 0 else '🟡'
                return True
        return False

    def check_winner(self):
        # Horizontal, vertical, and diagonal checks
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for row in range(6):
            for col in range(7):
                if self.board[row][col] != '⚪':
                    for dr, dc in directions:
                        line = [self.get_cell(row + i*dr, col + i*dc) for i in range(4)]
                        if all(cell == self.board[row][col] for cell in line):
                            return True
        return False

    def get_cell(self, row, col):
        if 0 <= row < 6 and 0 <= col < 7:
            return self.board[row][col]
        return None

    def is_full(self):
        return all(self.board[0][col] != '⚪' for col in range(7))

    def display_board(self):
        display = ""
        for row in self.board:
            display += "║" + "║".join(row) + "║\n"
        return display

def setup(bot):
    @bot.tree.command(name='connect4', description="Starts a game of Connect 4 with a wager")
    @app_commands.describe(user="Who will you challenge?", wager="Amount of money to bet")
    async def connect4(interaction: discord.Interaction, user: discord.Member, wager: int):
        if user.bot:
            await interaction.response.send_message("Please challenge an actual user and not a bot :/")
            return

        if wager < 0:
            await interaction.response.send_message("You can't wager a negative amount..")
            return

        # Check if both players have enough balance
        challenger_balance = get_balance(interaction.user.id)
        challengee_balance = get_balance(user.id)
        if challenger_balance < wager or challengee_balance < wager:
            await interaction.response.send_message("One or both players don't have enough dabloons to cover this wager.")
            return

        await interaction.response.send_message(f"{user.mention}, you have been challenged to a game of Connect 4 by {interaction.user.mention} for a wager of {wager} dabloons. Do you accept? (yes/no)")

        def check(m):
            return m.author == user and m.content.lower() in ["yes", "no"]

        try:
            msg = await interaction.client.wait_for('message', check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await interaction.followup.send("Challenge timed out.")
            return

        if msg.content.lower() == "no":
            await interaction.followup.send("Challenge declined.. maybe next time")
            return

        game = Connect4Game(interaction.user, user)
        await interaction.followup.send("Alright, here we go!")
        current_player_mention = game.players[game.current_player].mention
        current_player_color = '🔴' if game.current_player == 0 else '🟡'
        board_message = await interaction.followup.send(f"{current_player_mention}'s turn ({current_player_color}). Choose a column (1-7)\n" + game.display_board())

        while not game.is_full():

            def column_check(m):
                return m.author == game.players[game.current_player] and m.content.isdigit() and 1 <= int(m.content) <= 7

            msg = await interaction.client.wait_for('message', check=column_check)
            column = int(msg.content)

            await msg.delete()

            if not game.insert_piece(column):
                await interaction.followup.send("Column is full. Try another one.", ephemeral=True)
                continue

            if game.check_winner():
                winner = game.players[game.current_player]
                loser = game.players[1 - game.current_player]
                update_balance(winner.id, get_balance(winner.id) + wager)
                update_balance(loser.id, get_balance(loser.id) - wager)
                await board_message.edit(content=f"Congratulations! {winner.mention} won {wager} dabloons!\n" + game.display_board())
                return

            game.current_player = 1 - game.current_player
            current_player_mention = game.players[game.current_player].mention
            current_player_color = '🔴' if game.current_player == 0 else '🟡'
            await board_message.edit(content=f"Game in Progress:\n{current_player_mention}'s turn ({current_player_color}). Choose a column (1-7)\n" + game.display_board())

        await board_message.edit(content="It's a draw! Well played!\n" + game.display_board())
