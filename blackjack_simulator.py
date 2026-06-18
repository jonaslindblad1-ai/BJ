import argparse
import math
from card_deck import CardDeck


HI_LO_VALUES = {
    "2": 1,
    "3": 1,
    "4": 1,
    "5": 1,
    "6": 1,
    "7": 0,
    "8": 0,
    "9": 0,
    "10": -1,
    "J": -1,
    "Q": -1,
    "K": -1,
    "A": -1,
}


def card_value(rank):
    if rank == "A":
        return 11
    if rank in ["J", "Q", "K"]:
        return 10
    return int(rank)


def hand_value(cards):
    total = 0
    aces = 0
    for r, _ in cards:
        if r == "A":
            aces += 1
        total += 11 if r == "A" else (10 if r in ["J", "Q", "K"] else int(r))
    # adjust aces
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def update_count_for_card(card, running_count):
    rank, _ = card
    return running_count + HI_LO_VALUES.get(rank, 0)


def play_one_hand(shoe, running_count, base_bet):
    # Bet sizing using simple true count multiplier
    true_count = running_count / shoe.decks_remaining()
    bet_multiplier = 1
    if true_count >= 2:
        bet_multiplier = int(true_count)
    bet = base_bet * max(1, bet_multiplier)

    # initial deal
    player = [shoe.deal_card(), shoe.deal_card()]
    dealer = [shoe.deal_card(), shoe.deal_card()]

    # update count for all seen cards
    running_count = update_count_for_card(player[0], running_count)
    running_count = update_count_for_card(player[1], running_count)
    running_count = update_count_for_card(dealer[0], running_count)
    running_count = update_count_for_card(dealer[1], running_count)

    # check for blackjacks
    player_total = hand_value(player)
    dealer_total = hand_value(dealer)
    profit = 0
    # player blackjack
    if player_total == 21 and len(player) == 2:
        if dealer_total == 21 and len(dealer) == 2:
            profit = 0  # push
        else:
            profit = 1.5 * bet
        return profit, running_count
    # dealer blackjack
    if dealer_total == 21 and len(dealer) == 2:
        profit = -bet
        return profit, running_count

    # player play: simple strategy - hit until 17 or more
    while hand_value(player) < 17:
        card = shoe.deal_card()
        player.append(card)
        running_count = update_count_for_card(card, running_count)
        if hand_value(player) > 21:
            profit = -bet
            return profit, running_count

    # dealer play: hit until 17 (stand on soft 17)
    while hand_value(dealer) < 17:
        card = shoe.deal_card()
        dealer.append(card)
        running_count = update_count_for_card(card, running_count)
        if hand_value(dealer) > 21:
            profit = bet
            return profit, running_count

    # compare
    player_total = hand_value(player)
    dealer_total = hand_value(dealer)
    if player_total > dealer_total:
        profit = bet
    elif player_total < dealer_total:
        profit = -bet
    else:
        profit = 0

    return profit, running_count


def simulate(hands=1000, decks=6, penetration=0.75, base_bet=10, verbose=False):
    shoe = CardDeck(decks=decks, penetration=penetration)
    running_count = 0
    total_profit = 0.0
    total_bet = 0.0
    for i in range(hands):
        if shoe.needs_reshuffle():
            shoe.shuffle()
            running_count = 0
            if verbose:
                print(f"Reshuffle at hand {i}")

        profit, running_count = play_one_hand(shoe, running_count, base_bet)
        total_profit += profit
        # estimate bet used (profit can be fractional for blackjack)
        # approximate bet as abs(profit) when won/lost, else base_bet
        total_bet += base_bet

    roi = (total_profit / total_bet) * 100 if total_bet else 0.0
    return {
        "hands": hands,
        "decks": decks,
        "penetration": penetration,
        "base_bet": base_bet,
        "profit": total_profit,
        "total_bet": total_bet,
        "roi_percent": roi,
    }


def main():
    parser = argparse.ArgumentParser(description="Simple Blackjack card-counting simulator")
    parser.add_argument("--hands", type=int, default=1000)
    parser.add_argument("--decks", type=int, default=6)
    parser.add_argument("--penetration", type=float, default=0.75)
    parser.add_argument("--base-bet", type=float, default=10.0)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    result = simulate(hands=args.hands, decks=args.decks, penetration=args.penetration, base_bet=args.base_bet, verbose=args.verbose)
    print("Simulation result:")
    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
