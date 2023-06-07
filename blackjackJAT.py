import discord
from discord.ext import commands
import random,sqlite3,asyncio,traceback

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
    if balance < 0: # no negative balances
        balance = 0
    c.execute("INSERT OR REPLACE INTO balances (user_id, balance) VALUES (?, ?)", (user_id, balance))
    conn.commit()

# function to calculate the sum of cards in a hand, accounting for aces
def sum_cards(cards):
    total = sum(cards)
    if total > 21 and 11 in cards:
        total -= 10
    return total

# blackjack game
@commands.command(aliases=['bj'], help='Starts a game of blackjack with the bot.')
async def blackjack(ctx, bet:int=0):
    balance = get_balance(ctx.author.id)
    if balance is None:
        balance = 500
        update_balance(ctx.author.id, balance)
    if bet <= 0:
        await ctx.send("Well, how much do you wanna bet?")
        return
    if bet > balance:
        await ctx.send("Oops, sorry, you don't have enough dabloons for that.")
        return

    # deck initialization
    deck = [2,3,4,5,6,7,8,9,10,10,10,10,11]*4
    random.shuffle(deck)

    # initialize player and dealer hands
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    # show the player's hand and the dealer's face up card
    await ctx.send(f"Your hand: {player_hand} ({sum_cards(player_hand)})\nDealer's up card: {dealer_hand[0]}")

    # check for blackjack
    if sum_cards(player_hand) == 21:
        await ctx.send(f"Blackjack! You win! {ctx.author.mention} gained {bet} dabloons.")
        balance += bet * 2
        update_balance(ctx.author.id, balance)
        return
    
    # player turn
    while True:
        # ask the player to hit or stand
        message = await ctx.send("Would you like to hit or stand? Type 'h' or 's'.")
        response = await ctx.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.content.lower() in ['h', 's'], timeout=30)

        # if the player hits, draw a card and display the new hand
        if response.content.lower() == 'h':
            player_hand.append(deck.pop())
            await message.delete()
            await response.delete()
            await ctx.send(f"Your hand: {player_hand} ({sum_cards(player_hand)})\nDealer's up card: {dealer_hand[0]}")

            # if the player busts, end the game
            if sum_cards(player_hand) > 21:
                await ctx.send(f"You bust! {ctx.author.mention} lost {bet} dabloons.")
                balance -= bet
                update_balance(ctx.author.id, balance)
                return
            if sum_cards(player_hand) == 21:
                await ctx.send(f"Blackjack! You win! {ctx.author.mention} gained {bet} dabloons!")
                balance += bet * 2
                update_balance(ctx.author.id, balance)
                return

        # if the player stands, the game moves on to the dealer's turn
        elif response.content.lower() == 's':
            await message.delete()
            await response.delete()
            break

    # check for a hand of 21
    if sum_cards(player_hand) == 21:
        await ctx.send(f"21! You win! {ctx.author.mention} gained {bet} dabloons.")
        balance += bet
        update_balance(ctx.author.id, balance)
        return
    
    # dealer turn
    while sum_cards(dealer_hand) < 17:
        dealer_hand.append(deck.pop())

    # show the dealer's hand and determine the winner
    await ctx.send(f"Dealer's hand: {dealer_hand} ({sum_cards(dealer_hand)})")

    if sum_cards(dealer_hand) > 21:
        await ctx.send(f"Dealer busts! You win! {ctx.author.mention} gained {bet} dabloons.")
        balance += bet
        update_balance(ctx.author.id, balance)
        return
    elif sum_cards(dealer_hand) == sum_cards(player_hand):
        await ctx.send("It's a tie!")
        return
    elif sum_cards(dealer_hand) == 21:
        await ctx.send(f"Dealer has blackjack! {ctx.author.mention} lost {bet} dabloons.")
        balance -= bet
        update_balance(ctx.author.id, balance)
        return
    elif sum_cards(dealer_hand) > sum_cards(player_hand):
        await ctx.send(f"Dealer wins! {ctx.author.mention} lost {bet} dabloons.")
        balance -= bet
        update_balance(ctx.author.id, balance)
        return
    else:
        await ctx.send(f"You win! {ctx.author.mention} gained {bet} dabloons.")
        balance += bet
        update_balance(ctx.author.id, balance)
        return
# ERROR HANDLING FOR BLACKJACK
@blackjack.error
async def blackjack_error(ctx, error):
    traceback.print_exc()  # Print the traceback of the error
    if isinstance(error, commands.BadArgument):
        await ctx.send("Invalid bet amount, please enter a whole number greater than 0.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter an amount to bet.")
    else:
        await ctx.send("An error occurred while executing the command.")


def setup(bot):
    bot.add_command(blackjack)