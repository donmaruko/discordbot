import discord
from discord.ext import commands

# Define the Connect 4 game class
class Connect4Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.board = [['⚪' for _ in range(7)] for _ in range(6)]
        self.winner = None

    def make_move(self, column):
        for row in range(5, -1, -1):
            if self.board[row][column-1] == '⚪':
                self.board[row][column-1] = '🔴' if self.current_player == self.player1 else '🟡'
                if self.check_winner(row, column-1):
                    self.winner = self.current_player
                    return  # Exit the function if a winner is found
                self.switch_player()
                break
        else:
            raise ValueError("Invalid move!")

    def check_winner(self, row, col):
        directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
        current_color = self.board[row][col]  # Get the color of the current disc
        for dx, dy in directions:
            count = 1
            for i in range(1, 4):
                r = row + i * dx
                c = col + i * dy
                if 0 <= r < 6 and 0 <= c < 7 and self.board[r][c] == current_color:
                    count += 1
                else:
                    break
            if count == 4:
                return True
        return False


    def switch_player(self):
        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1

    def is_board_full(self):
        for row in self.board:
            if '⚪' in row:
                return False
        return True

    def display_board(self):
        return '```' + '\n'.join(['|'.join(row) for row in self.board]) + '```'

game = None

# Command to start a Connect 4 game
@commands.command()
async def connect4(ctx, opponent: discord.Member):
    global game
    if game is not None:
        await ctx.send("A game is already in progress.")
    elif opponent == ctx.author:
        await ctx.send("You cannot play against yourself!")
    else:
        game = Connect4Game(ctx.author, opponent)
        await ctx.send(f"{ctx.author.mention} vs {opponent.mention}. Let the game begin!\n\n{game.display_board()}")

# Command to make a move in the Connect 4 game
@commands.command()
async def drop(ctx, column: int):
    global game
    if game is None:
        await ctx.send("No game in progress. Start a game using !connect4.")
    elif ctx.author != game.current_player:
        await ctx.send("It's not your turn!")
    else:
        try:
            game.make_move(column)
            if game.winner is not None:
                await ctx.send(f"{game.winner.mention} wins!\n\n{game.display_board()}")
                game = None
            elif game.is_board_full():
                await ctx.send("It's a tie!\n\nGame Over.\n\n" + game.display_board())
                game = None
            else:
                await ctx.send(f"{game.current_player.mention}'s turn.\n\n{game.display_board()}")
        except ValueError as e:
            await ctx.send(str(e))

def setup(bot):
    bot.add_command(connect4)
    bot.add_command(drop)
