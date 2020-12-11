#!/usr/bin/env python3                                                                               

from random import seed
from random import randint
import scoring


print(scoring.STRAIGHT_FLUSHES)
print(scoring.STRAIGHT_FLUSH_HIGHS)
with open('scoring_test.txt') as fd:
    print(scoring.ROYAL_FLUSHES)
    for line in fd:
        card_list = line.split(",")
        cards = set()
        for i in card_list:
            cards.add(int(i))
        print(cards)
        string = ""
        for x in cards:
            string += scoring.CARD_ENUM[x] + ", "
        print(string)
        print(scoring.hand_score(cards))

for i in range(0, 50):
    # swap_mapping used to map removed cards to last card                                        
    # in order to maintain uniform randomness over deck                                          
    swap_mapping = {}
    seed()
    drawn_cards = []

    # build a correct list of drawn cards                                                        
    for i in range(0, 7):
        next_card = randint(0,51 - i)
        if next_card not in swap_mapping:
            swap_mapping[next_card] = (51 - i)
        else:
            temp_card = next_card
            next_card = swap_mapping[temp_card]
            swap_mapping[temp_card] = (51 - i)
        drawn_cards.append(next_card)

    cards = set(drawn_cards)
    print(cards)
    string = ""
    for x in cards:
        string += scoring.CARD_ENUM[x] + ", "
    print(string)
    print(scoring.hand_score(cards))
    

        
