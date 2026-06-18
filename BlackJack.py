


class CardDeck:
    def __init__(self, decks=1):
        self.decks = decks
        self.cards = self._create_deck()

    def _create_deck(self):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        single_deck = [(rank, suit) for suit in suits for rank in ranks]
        return single_deck * self.decks

    def shuffle(self):
        import random
        random.shuffle(self.cards)

    def deal(self, count=1):
        dealt = self.cards[:count]
        self.cards = self.cards[count:]
        return dealt


def main():
    pass


if __name__ == "__main__":
    main()
