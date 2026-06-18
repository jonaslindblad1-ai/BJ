class CardDeck:
    def __init__(self, decks=6, penetration=0.75):
        self.decks = int(decks)
        self.penetration = float(penetration)
        self._build_shoe()

    def _build_shoe(self):
        import random
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        single_deck = [(rank, suit) for suit in suits for rank in ranks]
        self.cards = single_deck * self.decks
        random.shuffle(self.cards)
        self.total_cards = len(self.cards)
        # reshuffle when remaining cards fall below the cutoff (i.e., penetration reached)
        self.reshuffle_cut = int(self.total_cards * (1 - self.penetration))

    def shuffle(self):
        self._build_shoe()

    def deal_card(self):
        if not self.cards:
            self.shuffle()
        return self.cards.pop(0)

    def cards_left(self):
        return len(self.cards)

    def decks_remaining(self):
        return max(0.1, self.cards_left() / 52.0)

    def needs_reshuffle(self):
        return self.cards_left() <= self.reshuffle_cut
