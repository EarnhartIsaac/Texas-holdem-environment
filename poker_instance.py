#!/usr/bin/env python3

import poker_interface as poker

NUM_PLAYERS = 3

table = poker.PokerTable(NUM_PLAYERS, 100, ante=2)

table.start_round()

with open('poker_test.txt') as fd:    
    for line in fd:
        if table.is_round_over():
            table.start_round()
        print(table.get_board_string())
        print(table.get_table_vars())
        current_turn = table.get_player_turn()
        amount = 0
        action = int(line)
        print("Player-" + str(current_turn) + " action: " + str(action))
        if action == 1:
            amount = int(next(fd))
            print("Amount: " + str(amount))
        table.take_action(current_turn, action, amount)
        
"""
while(not table.is_game_over()):
    table.start_round()
    while(not table.is_round_over()):
        print(table.get_board_string())
        print(table.get_table_vars())
        current_turn = table.get_player_turn()
        amount = 0
        action = int(("Player-" + str(current_turn) + "\n0: Fold\n1: Bet\nPlease enter an action: "))
        if action == 1:
            amount = int(input("Please enter a bet amount: "))
        table.take_action(current_turn, action, amount) 
"""
        

