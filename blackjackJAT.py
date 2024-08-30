import discord
from discord import app_commands
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
        return 0
# function to update the user's balance in the database
def update_balance(user_id, balance):
    if balance < 0:  # no negative balances
        balance = 0
    c.execute("INSERT OR REPLACE INTO balances (user_id, balance) VALUES (?, ?)", (str(user_id), balance))
    conn.commit()

def sum_cards(cards):
    total = sum(card if card != 11 else 1 for card in cards)
    aces = cards.count(11)
    while total <= 11 and aces:
        total += 10
        aces -= 1
    return total

def display_cards(cards):
    return ', '.join(str(card) for card in cards)

def deal_card():
    return random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11])

# blackjack game
def setup(bot):
    @bot.tree.command(name="blackjack", description="Starts a game of blackjack")
    @app_commands.describe(bet="How much you wanna bet?")
    async def blackjack(interaction: discord.Interaction, bet: int):
        user_id = interaction.user.id
        current_balance = get_balance(user_id)

        if bet > current_balance:
            await interaction.response.send_message("Come back when you actually have that much money..")
            return

        player_cards = [deal_card(), deal_card()]
        dealer_cards = [deal_card(), deal_card()]

        player_total = sum_cards(player_cards)
        dealer_total = sum_cards([dealer_cards[0]])  # Initially consider only the first card

        player_blackjack = (player_total == 21)

        # Show only the first dealer card initially and bold the total
        await interaction.response.send_message(f"Your cards: {display_cards(player_cards)} (Total: **{sum_cards(player_cards)}**)\n"
                                                f"Dealer's cards: {dealer_cards[0]}, ?\n"
                                                "Respond with 'h' to hit and 's' to stand")

        def check(m):
            return m.author == interaction.user and m.content.lower() in ["h", "s"]

        while player_total < 21:
            msg = await bot.wait_for('message', check=check)
            if msg.content.lower() == "h":
                player_cards.append(deal_card())
                player_total = sum_cards(player_cards)
                await interaction.followup.send(f"You drew a card: {player_cards[-1]}\n"
                                                f"Your hand is now: {display_cards(player_cards)} (Total: **{player_total}**)\n"
                                                f"Dealer's cards: {dealer_cards[0]}, ?")
            elif msg.content.lower() == "s":
                break
            await msg.delete() 

        # Reveal the dealer's second card and continue the game
        dealer_total = sum_cards(dealer_cards)
        await interaction.followup.send(f"Dealer's second card is revealed: {dealer_cards[1]}\n"
                                        f"Dealer's hand is now: {display_cards(dealer_cards)} (Total: **{dealer_total}**)")

        while dealer_total < 17:
            new_card = deal_card()
            dealer_cards.append(new_card)
            dealer_total = sum_cards(dealer_cards)
            await interaction.followup.send(f"Dealer draws: {new_card}\n"
                                            f"Dealer's hand is now: {display_cards(dealer_cards)} (Total: **{dealer_total}**)")

        result_message = f"Your total: **{player_total}**, Dealer's total: **{dealer_total}**\n"
        if player_total > 21:
            result_message += f"You bust! You lost **{bet}** dabloons!"
            update_balance(user_id, current_balance - bet)
        elif dealer_total > 21 or (player_blackjack and player_total > dealer_total):
            if player_blackjack:
                winnings = int(1.5 * bet)
                result_message += f"Blackjack! You won **{winnings}** dabloons!"
            else:
                result_message += f"Dealer busts! You won **{bet}** dabloons!"
            update_balance(user_id, current_balance + winnings if player_blackjack else current_balance + bet)
        elif player_total == dealer_total:
            result_message += "It's a push!"
        elif player_total > dealer_total:
            if player_blackjack:
                winnings = int(1.5 * bet)
                result_message += f"Blackjack! You won **{winnings}** dabloons!"
                update_balance(user_id, current_balance + winnings)
            else:
                result_message += f"You won **{bet}** dabloons!"
                update_balance(user_id, current_balance + bet)
        else:
            result_message += f"You lost **{bet}** dabloons!"
            update_balance(user_id, current_balance - bet)

        await interaction.followup.send(result_message)

    blackjack_command = bot.tree.get_command("blackjack")
    if blackjack_command:
        bot.tree.add_command(app_commands.Command(name="bj", callback=blackjack_command.callback,
                                                  description=blackjack_command.description))
