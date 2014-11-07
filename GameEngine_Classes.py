# Game Engine Classes
from random import shuffle # Shuffles the deck
from GameEngine_Functions import *
from GameEngine_AI import *

class Card:
    def __init__(self, name, value): # note that suits don't matter
        self.name, self.value = name, value # Names are like "2", "3", or "Ace"; Values are like 2, 3, or 14

class Deck:
    def __init__(self): # Build the deck
        self.cards = []
        for suit in range(4):
            for x in range(2, 11):
                self.cards.append(Card(name=str(x), value=x))
            names = ['Jack', 'Queen', 'King', 'Ace']
            for name in names:
                self.cards.append(Card(name=name, value=names.index(name)+11))
        shuffle(self.cards) # shuffle modifies in-place, no need to assign nor return

    def draw(self): # Draw a card from the deck
        return self.cards.pop(0)

class Player: # Players can be human or ai

    count = 0
    human_pcount = 0 # for checking that there are at least 2 players
    cpu_pcount = 0 # and for naming cpus
    taken_names = [] # for keeping player names unique

    def initial_swap(self): # Executes setup of hand and faceups (in the game, you're allowed to swap between the two before the first turn)
        choices = []
        for x in range(3):
            choices.append(self.faceups.pop())
            choices.append(self.hand.pop())
        if self.is_human: # If human player
            choices = sort_cards(choices)
            while len(self.faceups) < 3:
                self.faceups.append(choices[choose(choices)])
        else: # If computer player
            choices_values = [card.value for card in choices]
            while 10 in choices_values and len(self.faceups) < 3:
                self.faceups.append(choices.pop(choices_values.index(10))
                choices_values.remove(10)
            while 2 in choices_values and len(self.faceups) < 3:
                self.faceups.append(choices.pop(choices_values.index(2))
                choices_values.remove(2)
            while len(self.faceups) < 3:
                self.faceups.append(choices.pop(choices_values.index(max(choices_values))))
                choices_values.remove(max(choices_values))
        for x in range(3):
            self.hand.append(choices.pop()) 

    def __init__(self, is_human, deck):
        self.is_human = is_human
        self.hand = [deck.draw() for x in range(3)]
        self.faceups = [deck.draw() for x in range(3)]
        self.facedowns = [deck.draw() for x in range(3)]
        if is_human:
            self.name = get_name(Player.taken_names)
            Player.taken_names.append(self.name)
            Player.human_pcount+=1
        else:
            self.name = "CPU-" + str(Player.cpu_pcount)
            Player.cpu_pcount+=1
            self.ai = AI(get_difficulty(self.name)) # CPU wishes it had a brain :P
        self.initial_swap()
        Player.count+=1

    def play(self, from_where, pile): # Play a card
        assert from_where in ['hand', 'faceups', 'facedowns']
        if from_where == 'facedowns':
            return [self.facedowns.pop()] # Play randomly from facedowns
        elif from_where == 'hand':
            cards = self.hand
        elif from_where == 'faceups':
            cards = self.faceups
        chosen_cards = []
        if not can_play(cards, pile):
            return chosen_cards # Has to pickup()
        if self.is_human:
            chosen_index = None
            while chosen_index is None:
                chosen = cards[choose(cards)]
                if playable(chosen, pile):
                    count = 0
                    for card in cards:
                        if card.value == chosen.value:
                            count+=1
                    how_many = 1
                    if count > 1:
                        how_many = get_int_input(1, count, "How many would you like to play?")
                    index = 0
                    if from_where == 'hand':
                        while len(chosen_cards) < how_many:
                            if self.hand[index].value == chosen.value:
                                chosen_cards.append(self.hand.pop(index))
                            else:
                                index+=1
                    elif from_where == 'faceups':
                        while len(chosen_cards) < how_many:
                            if self.faceups[index].value == chosen.value:
                                chosen_cards.append(self.faceups.pop(index))
                            else:
                                index+=1
                    return chosen_cards
                else:
                    chosen_index = None
        else: # Elif not is_human
            chosen_cards = self.ai.cpu_choose()
            raise NotImplementedError
            if from_where == 'hand':
                for card in chosen_cards:
                    self.hand.remove(card)
            elif from_where == 'faceups':
                for card in chosen_cards:
                    self.faceups.remove(card)
            return chosen_cards

class Game: # Tying it all together
    def __init__(self):
        self.deck = Deck()
        self.players = []
        self.pile = []
        human_pcount = get_int_input(0, 5, "How many human players? [0-5]")
        cpu_pcount = get_int_input(2-human_pcount if human_pcount < 2 else 0, 5-human_pcount, "How many cpu players?")
        for x in range(human_pcount):
            self.players.append(Player(is_human=True, deck=self.deck))
        for x in range(cpu_pcount):
            self.players.append(Player(is_human=False, deck=self.deck))
        assert human_pcount+cpu_pcount == Player.count and Player.count <= 5

    def pickup(self, player):
        display(player.name + " has to pick up the pile!")
        for x in range(len(self.pile)):
            player.hand.append(self.pile.pop())

    def blowup(self, name):
        display(name + " blew up the pile!")
        self.pile = []

    def turn(self, player):
        played = []
        if player.hand:
            player.hand = sort_cards(player.hand)
            played = player.play('hand', self.pile)
        elif player.faceups:
            played = player.play('faceups', self.pile)
        elif player.facedowns:
            played = player.play('facedowns', self.pile)
        if not played:
            self.pickup(player)
            return True
        while self.deck.cards and len(player.hand) < 3:
            player.hand.append(self.deck.draw())
        for card in played:
            self.pile.insert(0, card)
        if self.pile[0].value == 10:
            self.blowup(player.name)
            return False
        elif len(self.pile) >= 4: 
            if self.pile[0].value == self.pile[1].value == self.pile[2].value == self.pile[3].value:
                self.blowup(player.name)
                return False
        return True

    def main(self):
        winner = None
        while winner is None:
            try:
                for player in self.players:
                    for player in self.players:
                        if not player.is_human:
                            player.ai.update(self)
                    turn_done = False
                    display(player.name + "'s turn:")
                    while not turn_done:
                        if not player.is_human:
                            turn_done = self.turn(player)
                    # display_cards(self.pile)
                    if len(player.hand)+len(player.facedowns) == 0:
                        winner = player
            except KeyboardInterrupt:
                print() # Carriage return the calling terminal for neatness
                return 1
        display(winner.name + " is the winner!")
        return 0
