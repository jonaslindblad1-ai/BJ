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


INDEX_PLAYS = {
    # (hand type, total, dealer upcard) -> (action, true count threshold)
    ("hard", 16, 10): ("stand", 0),
    ("hard", 15, 10): ("stand", 4),
    ("hard", 13, 2): ("stand", -1),
    ("hard", 12, 3): ("stand", 2),
    ("hard", 12, 2): ("stand", 3),
    ("hard", 11, 11): ("double", 1),
    ("hard", 10, 11): ("double", 4),
    ("hard", 9, 2): ("double", 1),
    ("hard", 9, 7): ("double", 3),
    ("hard", 16, 9): ("stand", 1),
    ("hard", 15, 9): ("stand", 2),
    ("hard", 13, 3): ("stand", -1),
    ("hard", 12, 4): ("stand", 0),
    ("hard", 12, 5): ("stand", 0),
    ("hard", 12, 6): ("stand", 0),
    ("soft", 18, 6): ("double", 1),
}

BASIC_HARD = {
    5: {i: "hit" for i in range(2, 12)},
    6: {i: "hit" for i in range(2, 12)},
    7: {i: "hit" for i in range(2, 12)},
    8: {i: "hit" for i in range(2, 12)},
    9: {2: "hit", 3: "double", 4: "double", 5: "double", 6: "double", 7: "hit", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    10: {2: "double", 3: "double", 4: "double", 5: "double", 6: "double", 7: "double", 8: "double", 9: "double", 10: "hit", 11: "hit"},
    11: {2: "double", 3: "double", 4: "double", 5: "double", 6: "double", 7: "double", 8: "double", 9: "double", 10: "double", 11: "hit"},
    12: {2: "hit", 3: "hit", 4: "stand", 5: "stand", 6: "stand", 7: "hit", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    13: {2: "stand", 3: "stand", 4: "stand", 5: "stand", 6: "stand", 7: "hit", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    14: {2: "stand", 3: "stand", 4: "stand", 5: "stand", 6: "stand", 7: "hit", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    15: {2: "stand", 3: "stand", 4: "stand", 5: "stand", 6: "stand", 7: "hit", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    16: {2: "stand", 3: "stand", 4: "stand", 5: "stand", 6: "stand", 7: "hit", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    17: {i: "stand" for i in range(2, 12)},
    18: {i: "stand" for i in range(2, 12)},
    19: {i: "stand" for i in range(2, 12)},
    20: {i: "stand" for i in range(2, 12)},
    21: {i: "stand" for i in range(2, 12)},
}

BASIC_SOFT = {
    13: {2: "hit", 3: "hit", 4: "hit", 5: "double", 6: "double", 7: "hit", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    14: {2: "hit", 3: "hit", 4: "double", 5: "double", 6: "double", 7: "hit", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    15: {2: "hit", 3: "hit", 4: "double", 5: "double", 6: "double", 7: "hit", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    16: {2: "hit", 3: "double", 4: "double", 5: "double", 6: "double", 7: "hit", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    17: {2: "hit", 3: "double", 4: "double", 5: "double", 6: "double", 7: "stand", 8: "stand", 9: "hit", 10: "hit", 11: "hit"},
    18: {2: "stand", 3: "stand", 4: "stand", 5: "double", 6: "double", 7: "stand", 8: "stand", 9: "stand", 10: "stand", 11: "stand"},
    19: {i: "stand" for i in range(2, 12)},
    20: {i: "stand" for i in range(2, 12)},
    21: {i: "stand" for i in range(2, 12)},
}

PAIR_STRATEGY = {
    2: {2: "split", 3: "split", 4: "split", 5: "split", 6: "split", 7: "split", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    3: {2: "split", 3: "split", 4: "split", 5: "split", 6: "split", 7: "split", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    4: {2: "hit", 3: "hit", 4: "hit", 5: "split", 6: "split", 7: "hit", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    5: {2: "double", 3: "double", 4: "double", 5: "double", 6: "double", 7: "double", 8: "double", 9: "double", 10: "hit", 11: "hit"},
    6: {2: "split", 3: "split", 4: "split", 5: "split", 6: "split", 7: "hit", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    7: {2: "split", 3: "split", 4: "split", 5: "split", 6: "split", 7: "split", 8: "hit", 9: "hit", 10: "hit", 11: "hit"},
    8: {i: "split" for i in range(2, 12)},
    9: {2: "split", 3: "split", 4: "split", 5: "split", 6: "split", 7: "stand", 8: "split", 9: "split", 10: "stand", 11: "stand"},
    10: {i: "stand" for i in range(2, 12)},
    11: {i: "split" for i in range(2, 12)},
}


def basic_strategy_action(cards, dealer_card, can_double, can_split):
    up = card_value(dealer_card[0])
    ranks = [c[0] for c in cards]
    if len(cards) == 2 and can_split and ranks[0] == ranks[1]:
        pair_rank = ranks[0]
        rank_val = 11 if pair_rank == "A" else (10 if pair_rank in ["10", "J", "Q", "K"] else int(pair_rank))
        action = PAIR_STRATEGY.get(rank_val, {}).get(up)
        if action:
            return action

    soft = any(rank == "A" for rank in ranks) and hand_value(cards) <= 21 and hand_value(cards) - 10 <= 11
    total = hand_value(cards)
    if soft and total in BASIC_SOFT:
        return BASIC_SOFT[total].get(up, "hit") if can_double else ("hit" if BASIC_SOFT[total].get(up, "hit") == "double" else BASIC_SOFT[total].get(up, "hit"))
    if total in BASIC_HARD:
        action = BASIC_HARD[total].get(up, "hit")
        if action == "double" and not can_double:
            return "hit"
        return action
    return "hit"


def get_true_count(running_count, shoe):
    return running_count / shoe.decks_remaining()


def is_soft_hand(cards):
    if not any(rank == "A" for rank, _ in cards):
        return False
    total = 0
    for r, _ in cards:
        total += 11 if r == "A" else (10 if r in ["J", "Q", "K"] else int(r))
    return total <= 21


def apply_index_play(action, cards, dealer_card, true_count):
    if len(cards) != 2 or dealer_card is None:
        return action
    hand_total = hand_value(cards)
    up = card_value(dealer_card[0])
    hand_type = "hard"
    if is_soft_hand(cards):
        hand_type = "soft"
    index_key = (hand_type, hand_total, up)
    if index_key not in INDEX_PLAYS:
        return action
    deviation_action, threshold = INDEX_PLAYS[index_key]
    if true_count >= threshold:
        return deviation_action
    return action


def play_one_hand(shoe, running_count, base_bet):
    # Bet sizing using true count multiplier
    true_count = get_true_count(running_count, shoe)
    bet_multiplier = min(max(1, int(true_count) + 1), 8)
    bet = base_bet * bet_multiplier

    # initial deal
    player = [shoe.deal_card(), shoe.deal_card()]
    dealer = [shoe.deal_card(), shoe.deal_card()]

    # update count for all seen cards
    running_count = update_count_for_card(player[0], running_count)
    running_count = update_count_for_card(player[1], running_count)
    running_count = update_count_for_card(dealer[0], running_count)
    running_count = update_count_for_card(dealer[1], running_count)

    insurance_bet = 0
    if dealer[0][0] == "A" and true_count >= 3:
        insurance_bet = bet / 2
    insurance_profit = -insurance_bet

    # check for blackjacks
    player_total = hand_value(player)
    dealer_total = hand_value(dealer)
    profit = 0
    # player blackjack
    if player_total == 21 and len(player) == 2:
        if dealer_total == 21 and len(dealer) == 2:
            profit = 0
            if insurance_bet:
                insurance_profit = insurance_bet * 2
        else:
            profit = 1.5 * bet
        return profit + insurance_profit, running_count, bet + insurance_bet
    # dealer blackjack
    if dealer_total == 21 and len(dealer) == 2:
        profit = -bet
        if insurance_bet:
            insurance_profit = insurance_bet * 2
        return profit + insurance_profit, running_count, bet + insurance_bet

    # player play using basic strategy with splitting and doubling
    def decide_action(cards, dealer_card, can_double, can_split, true_count):
        action = basic_strategy_action(cards, dealer_card, can_double, can_split)
        return apply_index_play(action, cards, dealer_card, true_count)

    total_wager = bet + insurance_bet
    # support multiple hands from splits
    hands = [(player, bet, True, True)]  # (cards, bet, can_double, can_split)
    total_profit = 0

    i = 0
    while i < len(hands):
        cards, this_bet, can_double, can_split = hands[i]
        action = decide_action(cards, dealer[0], can_double, can_split, true_count)
        if action == "stand":
            i += 1
            continue
        if action == "hit":
            card = shoe.deal_card()
            cards.append(card)
            running_count = update_count_for_card(card, running_count)
            if hand_value(cards) > 21:
                total_profit -= this_bet
                i += 1
            continue
        if action == "double":
            # draw one card and resolve
            card = shoe.deal_card()
            cards.append(card)
            running_count = update_count_for_card(card, running_count)
            # double the bet
            this_bet *= 2
            total_wager += this_bet / 2
            # if busted
            if hand_value(cards) > 21:
                total_profit -= this_bet
                i += 1
                continue
            # mark as stand
            hands[i] = (cards, this_bet, False, False)
            i += 1
            continue
        if action == "split":
            # split into two hands, draw one card for each
            r = cards[0][0]
            first = [cards[0], shoe.deal_card()]
            second = [cards[1], shoe.deal_card()]
            running_count = update_count_for_card(first[1], running_count)
            running_count = update_count_for_card(second[1], running_count)
            total_wager += this_bet
            # replace current hand with first, append second
            hands[i] = (first, this_bet, True, False)
            hands.insert(i + 1, (second, this_bet, True, False))
            # do not increment i so we process the new first hand next
            continue

    # after player hands resolved (some may have already added profit/loss), play dealer if any hands remain unresolved
    # Determine which hands still need comparison (those not busted and not resolved by doubling loss/win)
    # If all hands busted, return profit
    remaining = [h for h in hands if hand_value(h[0]) <= 21]
    if not remaining:
        total_profit += insurance_profit
        return total_profit, running_count, total_wager

    # dealer play: hit until 17 (stand on soft 17)
    while hand_value(dealer) < 17:
        card = shoe.deal_card()
        dealer.append(card)
        running_count = update_count_for_card(card, running_count)
        if hand_value(dealer) > 21:
            # all remaining hands win
            for cards, this_bet, _, _ in remaining:
                total_profit += this_bet
            total_profit += insurance_profit
            return total_profit, running_count, total_wager

    dealer_total = hand_value(dealer)
    # compare each remaining hand
    for cards, this_bet, _, _ in hands:
        pv = hand_value(cards)
        if pv > 21:
            # already handled
            continue
        if pv > dealer_total:
            total_profit += this_bet
        elif pv < dealer_total:
            total_profit -= this_bet
        else:
            total_profit += 0

    total_profit += insurance_profit
    return total_profit, running_count, total_wager


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

        profit, running_count, wager = play_one_hand(shoe, running_count, base_bet)
        total_profit += profit
        total_bet += wager

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
