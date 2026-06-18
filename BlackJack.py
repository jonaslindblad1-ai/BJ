

from card_deck import CardDeck


def main():
    # Delegate to the simulator CLI in blackjack_simulator.py
    try:
        import blackjack_simulator
    except Exception:
        print("Could not import blackjack_simulator. Make sure blackjack_simulator.py is present.")
        return
    blackjack_simulator.main()


if __name__ == "__main__":
    main()
