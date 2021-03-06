#!/usr/bin/env python3

import scoring
from random import seed
from random import randint
from enum import Enum

#Finish dict of cards
CARD_NAMES = ['AS', 'KS', 'QS', 'JS', '10S', '9S', '8S', '7S', '6S', '5S', '4S', '3S', '2S',
              'AH', 'KH', 'QH', 'JH', '10H', '9H', '8H', '7H', '6H', '5H', '4H', '3H', '2H',
              'AC', 'KC', 'QC', 'JC', '10C', '9C', '8C', '7C', '6C', '5C', '4C', '3C', '2C',
              'AD', 'KD', 'QD', 'JD', '10D', '9D', '8D', '7D', '6D', '5D', '4D', '3D', '2D']

CARD_SET = list(range(0, 52))
CARD_ENUM = dict(zip(CARD_SET, CARD_NAMES))

STREETS = {0 : 'Preflop', 1 : 'Flop', 2 : 'Turn', 3 : 'River'}


############################
# RULESET
############################

#TODO: IMPLEMENT THESE
class Holdem_rule(Enum):
    NO_LIMIT = 1
    FIXED_LIMIT = 2
    POT_LIMIT = 3

CHECK_AND_RAISE = False
ANTE = 0
BIG_BLIND = 0
LITTLE_BLIND = 0

############################
# Players can interface through the table to their player object
# Table ensures encapsulation and validity of actions
# along with facilitating transfer of information to players
############################

class PokerTable(object):

    def __init__(self, num_players, initial_chips, ante=0, bb=0, sb=0):
        #Initialize instance variables
        self.running = False
        self.round_over = True
        
        self.dealer = -1 #-1 so that dealer will start on 1
        self.player_turn = 0
        self.street = 0
        self.street_bet = 0
        self.num_active_players = num_players
        self.active_players = []
        self.all_players = []
        
        self.player_to_pot = []
        self.pot = []
        self.amount_to_call = []
        self.ante = ante
        self.bb = bb
        self.sb = sb
        
        self.table_cards = []
        self.flop = []
        self.turn = 0
        self.river = 0
        self.hands = []
        
        
        for i in range(0, num_players):
            self.all_players.append(self.Player(i, initial_chips))
        self.active_players = self.all_players.copy()

        
        if num_players < 2:
            #Exception here
            return

        #Move this to round start
        self.__init_blinds()
        self.player_turn = (self.big_blind + 1) % self.num_active_players
            

    #Used to set the blind positions after dealer is determined
    def __init_blinds(self):
        if self.num_active_players == 2:
            self.small_blind = self.dealer
            self.big_blind = (self.small_blind + 1) % self.num_active_players
        else:
            self.small_blind = (self.dealer + 1) % self.num_active_players
            self.big_blind = (self.small_blind + 1) % self.num_active_players

    #Removes players that no longer have the chips to compete
    #Applies ante to all players on the table
    #Applies big and small blind to designated players
    def __ante_up(self):
        self.__remove_inactive_players()
        players_copy = self.active_players.copy()
        self.amount_to_call[-1] += self.ante
        for p in players_copy:
            self.pot[-1] += self.ante
            p.chips -= self.ante
            p.current_bet += self.ante
        #Init buttons
        self.dealer = (self.dealer + 1) % self.num_active_players
        self.__init_blinds()
        self.active_players[self.small_blind].chips -= self.sb
        self.active_players[self.small_blind].current_bet += self.sb
        self.pot[-1] += self.sb
        self.active_players[self.big_blind].chips -= self.bb
        self.active_players[self.big_blind].current_bet += self.bb
        self.pot[-1] += self.bb
        self.amount_to_call[-1] += self.bb
        
            
                      
    def get_player_turn(self):
        return self.active_players[self.player_turn].player_id

    def is_round_over(self):
        return self.round_over
        
    
    def get_table_vars(self):
        string = "--------------------------\n"
        string += "       PRIVATE VARS\n"
        string += "--------------------------\n"
        string += ("| Running:    " + str(self.running) + "\n")
        string += ("| Round over: " + str(self.round_over) + "\n")
        string += ("| Turn:       " + str(self.player_turn) + "\n")
        string += ("| Street:     " + str(self.street) + "\n")
        string += ("| Cards:      " + str(self.table_cards) + "\n")
        string += ("|             ")
        for t in self.table_cards:
            string += (CARD_ENUM[t] + ", ")
        string += ("\n")
        for i in range(0, len(self.hands)):
            string += ("| Player-" + str(self.active_players[i].player_id))
            string += (":   " + CARD_ENUM[self.hands[i][0]] + ", ")
            string += (CARD_ENUM[self.hands[i][1]] + "\n")
            
            
        return string
        
        
    def start_round(self) -> bool:

        if self.is_game_over():
            return False

        #Reset player variables
        self.__reset_player_var()

        self.pot = [0]
        self.amount_to_call = [0]
        
        #Ante up, apply blinds, and remove any inactive players
        self.__ante_up()

        # INITIALIZE SIDEPOT LIST
        # player_to_pot maps player to their pot layer,
        # as sidepots describe a linear ordering of players bets
        self.player_to_pot = []
        for i in range(0, len(self.all_players)):
            self.player_to_pot.append(0)
        
        # swap_mapping used to map removed cards to last card
        # in order to maintain uniform randomness over deck
        swap_mapping = {}
        seed()
        drawn_cards = []
        
        # build a correct list of drawn cards
        for i in range(0, 5 + self.num_active_players * 2):
            next_card = randint(0,51 - i)
            if next_card not in swap_mapping:
                swap_mapping[next_card] = (51 - i)
            else:
                temp_card = next_card
                next_card = swap_mapping[temp_card]
                swap_mapping[temp_card] = (51 - i)
            drawn_cards.append(next_card)

        # build hands
        self.table_cards = drawn_cards[0:5]
        self.flop = drawn_cards[0:3]
        self.turn = drawn_cards[3]
        self.river = drawn_cards[4]
        self.hands = []
        for i in range(0, self.num_active_players):
            self.hands.append([drawn_cards[5 + 2*i], drawn_cards[6 + 2*i]])

        #Initialize round variables
        self.player_turn = (self.big_blind + 1) % self.num_active_players
        self.street = 0
        self.street_bet = 0

        self.round_over = False
        self.running = True
        return True
        
    #######################################################
    # ACTION METHODS
    #######################################################
    # VARIABLES FOR ACTIONS
    # -----------------------------------------------------
    # current_bet:     amount player has in pot
    # new_bet:         amount player will add to pot
    # chips:           amount player has (not in pot)
    # amount_to_call:  total amount needed from each player 
    #######################################################

    #######################################################
    # A NOTE ON SIDEPOTS
    #######################################################
    # Sidepots are constructed so that lower indexed
    # sidepots are subsets of larger indexed ones.
    # When a raise is made that surpasses the what
    # another player has, a sidepot is built
    #
    # Notice that once a sidepot is created, that person
    # will have no chips left to bet, but other players
    # might need to call the all in
    #######################################################
    
    #Action interface function to clarify action space
    def take_action(self, player_id, action, new_bet=0) -> int:
        if self.running and (player_id == self.active_players[self.player_turn].player_id):
            self.running = False
            p = self.active_players[self.player_turn]
            call = self.amount_to_call
            if action == 0:
                self.__fold(player_id)
                return 0
            elif action == 1:
                #If we dont have the chips to make the call (and go all in)
                if self.__pot_placement(player_id) < len(call):
                    #sidepot all in
                    self.__all_in(player_id)
                    return 0
                else:
                    #If we are checking (we have the chips for it)
                    if (call[-1] - p.current_bet) == 0 and new_bet == 0:
                        p.checked = True
                        self.__call(player_id)
                        return 0
                    #If we are calling (we have the chips for it)
                    elif new_bet <= (call[-1] - p.current_bet):
                        self.__call(player_id)
                        return 0
                    #If we are raising (could be all in)
                    elif new_bet > (call[-1] - p.current_bet):
                        if not CHECK_AND_RAISE and p.checked:
                            #We know we have the chips to call
                            self.__call(player_id)
                            return 0

                        elif new_bet > p.chips:
                            #We go all in
                            self.__raise(player_id, p.chips)
                            return 0
                                
                        else:
                            #Simple raise
                            self.__raise(player_id, new_bet)
                            return 0
                        
    
                        
                            
            else:
                #Invalid action
                return 1
        else:
            #Not time to play
            return 2

    # Returns the index coorsponding to where the sidepot
    # must be created if the player goes all in,
    # but returns number of pots if no side pot need be created
    def __pot_placement(self, player_id) -> int:
        p = self.all_players[player_id]
        call = self.amount_to_call
        i = 0
        while i < len(call) and p.chips >= (call[i] - p.current_bet):
            i += 1
        return i


    #Irrelevant 
    #def __matches_sidepot(self, player_id, sidepot_index) -> bool:
    #    p = self.all_players[player_id]
    #    if p.chips == (call[sidepot_index] - p.current_bet):
    #        return True
    #    else:
    #        return False
    
    # Used to make sure all sidepots have correct
    # amount added to them after someone calls,
    # raises, or adds a new sidepot
    def __call_most_sidepots(self, current_bet, pot_index):
        call = self.amount_to_call
        i = 0
        for i in range(0, pot_index):
            if current_bet < call[i]:
                self.pot[i] += (call[i] - current_bet)
        
    # We know we don't need a sidepot here
    def __call(self, player_id):
        p = self.all_players[player_id]
        largest_call = self.amount_to_call[-1]
        self.__call_most_sidepots(p.current_bet, len(self.pot))
        p.chips -= (largest_call - p.current_bet)
        p.current_bet = largest_call
        p.has_bet = True
        self.__next_turn()

    def __build_sidepot(self, player_id):
        sidepot_index = self.__pot_placement(player_id)
        
        ###############################
        print(str(sidepot_index))
        ##############################
        
        p = self.all_players[player_id]
        call = self.amount_to_call
        
        #build the new pot
        new_pot = 0
        sidepot_call = p.chips + p.current_bet
        for i in range(0, self.num_active_players):
            new_pot += min(self.active_players[i].current_bet, sidepot_call)
        #Current bet for player_id isnt at the sidepot_limit yet
        new_pot += p.chips

        #Add chips to higher order pots
        for i in range(sidepot_index,len(self.pot)):
            self.pot[i] += p.chips
        
        #At this point the target player has added their chips to the pot
        #now we need to add the new pot and call amount to our lists
        #and we need to make sure the player has called all the lower order pots (call_most)
        

        #Putting the new pot in the correct position
        temp_call_1 = call[0:sidepot_index]
        temp_call_2 = call[sidepot_index:]
        temp_pot_1 = self.pot[0:sidepot_index]
        temp_pot_2 = self.pot[sidepot_index:]

        new_calls = temp_call_1
        new_calls.append(sidepot_call)
        new_calls.extend(temp_call_2)

        new_pots = temp_pot_1
        new_pots.append(new_pot)
        new_pots.extend(temp_pot_2)
        
        self.amount_to_call = new_calls
        self.pot = new_pots

        #call sidepots that are of a lower order
        self.__call_most_sidepots(p.current_bet, sidepot_index)

        #Update the player_to_pot mapping
        self.player_to_pot[player_id] = sidepot_index
        for i in range(0, len(self.player_to_pot)):
            if self.player_to_pot[i] >= sidepot_index and i != player_id:
                self.player_to_pot[i] += 1

        for i in range(0, len(self.pot)):
            print("| Pot-" + str(i) + ":          " + str(self.pot[i]))
            print("| Amount to Call: " + str(self.amount_to_call[i]))
        string = ""
        string += ("| Players in:     ")
        for j in range(0, len(self.player_to_pot)):
            if self.player_to_pot[j] >= i:
                string += (str(j) + ", ")
        print(string)
                
        p.current_bet = sidepot_call
        p.chips = 0
        p.has_bet = True
    
    
    # Calling all in lets us know we will be
    # building a new sidepot
    def __all_in(self, player_id):
        self.__build_sidepot(player_id)
        self.__next_turn()

    #Under the assumption that new_bet is
    #larger than call amount
    def __raise(self, player_id, new_bet):
        for p in self.active_players:
            if p.chips == 0:
                self.__build_sidepot(p.player_id)
        
        p = self.all_players[player_id]
        self.__call_most_sidepots(p.current_bet, len(self.pot) - 1)
        p.current_bet += new_bet
        p.chips -= new_bet
        p.has_bet = True
        self.pot[-1] += new_bet
        self.amount_to_call[-1] = p.current_bet
        self.__next_turn()

    def __fold(self, player_id):
        p = self.all_players[player_id]
        p.folded = True
        self.__next_turn()

    #############################################
    #############################################

    #############################################
    # METHODS FOR WORKING WITH PLAYERS
    #############################################
    
    def __reset_checks(self):
        for i in range(0, self.num_active_players):
            self.active_players[i].checked = False

    def __reset_current_bets(self):
        for i in range(0, self.num_active_players):
            self.active_players[i].current_bet = 0

    def __reset_folds(self):
        for i in range(0, self.num_active_players):
            self.active_players[i].folded = False

    def __reset_has_bet(self):
        for i in range(0, self.num_active_players):
            self.active_players[i].has_bet = False

    def __reset_player_var(self):
        self.__reset_checks()
        self.__reset_current_bets()
        self.__reset_folds()
        self.__reset_has_bet()
        
    def is_player_done_betting_street(self, player_id : int) -> bool:
        p = self.all_players[player_id]
        return self.player_done_betting_street(p)

    def player_done_betting_street(self, p) -> bool:
        call = self.amount_to_call[-1]
        return (p.current_bet == call and p.has_bet) or self.player_done_betting_round(p)
    
    def is_player_done_betting_round(self, player_id) -> bool:
        p = self.all_players[player_id]
        return self.player_done_betting_round(p)

    def player_done_betting_round(self, p) -> bool:
        return p.folded or (p.chips == 0)

    #Only call this method if all players have called 
    def all_players_ready_round(self) -> bool:
        #Return true if all but 1 folded or all in
        count = 0
        for p in self.active_players:
            if not self.player_done_betting_round(p):
                count += 1
            
        return (count <= 1)

    def all_players_ready_street(self) -> bool:
        ready = True
        for p in self.active_players:
            if not self.player_done_betting_street(p):
                ready = False
        return ready


    #Returns the winner out of a set of players
    def who_won_this_pot(self, players, calc_hands):
        i = 1
        current_winners = { 0 : players[0] }
        while i < len(players):
            p1 = players[i]
            p2 = current_winners[0]
            result = scoring.compare_hands(calc_hands[p1], calc_hands[p2])
            if result == 1:
                current_winners.clear()
                current_winners[0] = p1
            elif result == -1:
                current_winners.clear()
                current_winners[0] = p2
            else:
                current_winners[1] = p1
            i += 1

        return list(current_winners.values())
        
    
    # Returns a set of players that one this pot
    # Calc_hands passed in so hands aren't recalculated
    def choose_winner(self, pot_id, calc_hands):
        players = set()

        #For all active players
        for i in range(0, self.num_active_players):
            player_id = self.active_players[i].player_id
            #Players that are eligible for this pot, and haven't folded
            if self.player_to_pot[player_id] >= pot_id and not self.active_players[i].folded:
                players.add(i)
                #If we haven't calculated their hand, calculate it
                if i not in calc_hands:
                    calc_hands[i] = scoring.hand_score(set(self.hands[i]) | set(self.table_cards))

        players_list = list(players)


        #########################################
        # PRINTING THE HANDS OF PEOPLE WHO ARE IN
        #########################################
        for x in calc_hands:
            (hand_type, _, cards) = calc_hands[x]
            print(hand_type)
            string = ""
            for x in cards:
                for y in x:
                    string += CARD_ENUM[y] + ","
            print(string)
        #########################################

        return self.who_won_this_pot(players_list, calc_hands)


    #Used to remove players that are out at the end of rounds
    def __remove_inactive_players(self):
        players_copy = self.active_players.copy()
        for p in players_copy:
            if p.chips <= (self.ante + self.big_blind):
                self.active_players.remove(p)
                self.num_active_players -= 1
                

    #Shows cards, and calculates the winners for each sidepot
    #then gives them their chips
    #does not 
    def __flip(self):
        #show cards

        #Calculate winners and resolve pots
        calc_hands = {}
        for p in range(len(self.pot) - 1, -1, -1):
            #Pots are calculated as subsets, not as partitions of the chips
            #so we need to subtract the next lower order pot
            if p > 0:
                self.pot[p] -= self.pot[p - 1] 
            winners = self.choose_winner(p, calc_hands)

            #############################
            print("Winners: " + str(winners))
            #############################
            
            n_winners = len(winners)
            share = (self.pot[p] / n_winners)
            for i in winners:
                self.active_players[i].chips += share
        
        self.round_over = True

    def is_game_over(self) -> bool:
        return (len(self.active_players) <= 1)
        
    #Called once all players are done with current street
    def __next_street(self) -> bool:
        if self.street == 3 or self.all_players_ready_round():
            #End the round
            self.__flip()
            return True
        else:
            #Next street
            self.street += 1
            #Reset turn to first to bet
            self.player_turn = (self.big_blind + 1) % self.num_active_players
            
        #Reset checked
        self.__reset_checks()
        self.__reset_has_bet()
        while self.is_player_done_betting_street(self.player_turn):
            self.player_turn = (self.player_turn + 1) % self.num_active_players
        return True

    # Checks to see if all all players have matched bets
    # or have folded to call __next_street, otherwise
    # moves to next active player's turn
    def __next_turn(self) -> bool:
        num_folded = 0
        for p in self.active_players:
            if p.folded:
                num_folded += 1
        #Check if everyone has folded
        if (num_folded + 1) == self.num_active_players:
            for p in self.active_players:
                if not p.folded:
                    p.chips += self.pot[-1]
                    self.round_over = True
                    return True

                    
        if self.all_players_ready_street():
            self.__next_street()
            self.running = True
            return True
        
        #Find the next player whos in play if the next one isnt
        self.player_turn = (self.player_turn + 1) % self.num_active_players
        while self.is_player_done_betting_street(self.player_turn):
            self.player_turn = (self.player_turn + 1) % self.num_active_players
            
        self.running = True
        return True

    ##########################################
    # GETTER FUNCTIONS TO VIEW BOARD
    ##########################################
    def __get_hand(self, player_id):
        return self.hands[player_id]

    def __get_flop(self):
        return self.flop

    def __get_turn(self):
        return self.turn

    def __get_river(self):
        return self.river

    def get_num_players(self):
        return self.num_active_players

    def get_num_chips(self, player_id):
        return self.players[player_id].chips

    def get_all_chips(self):
        player_chips = list(int)
        for i in range(0, self.num_active_players):
            player_chips.append(self.players[i].chips)
        return player_chips

    def get_bet_amount(self, player_id):
        return self.players[player_id].current_bet
    
    def get_all_bets(self):
        player_bets = list(int)
        for i in range(0, self.num_active_players):
            player_bets.append(self.players[i].current_bet)
        return player_bets

    def get_board_string(self):
        string = "--------------------------\n"
        string += "      VISIBLE BOARD\n"
        string += "--------------------------\n"
        for i in range(0, len(self.pot)):
            string += ("| Pot-" + str(i) + ":          " + str(self.pot[i]) + "\n")
            string += ("| Amount to Call: " + str(self.amount_to_call[i]) + "\n")
            string += ("| Players in:     ")
            for j in range(0, len(self.player_to_pot)):
                if self.player_to_pot[j] >= i:
                    string += (str(j) + ", ")
            string += "\n"
        string += ("| Turn:           " + str(self.player_turn) + "\n")
        string += ("| Cards:          ")
        if self.street >= 1:
            flop = self.flop
            string += (CARD_ENUM[self.flop[0]] + ", ")
            string += (CARD_ENUM[self.flop[1]] + ", ")
            string += (CARD_ENUM[self.flop[2]])
        if self.street >= 2:
            turn = self.turn
            string += (", " + CARD_ENUM[self.turn])
        if self.street >= 3:
            turn = self.river
            string += (", " + CARD_ENUM[self.river])
        string += "\n"
        
        for i in range(0, len(self.active_players)):
            p = self.active_players[i]
            string += "--------------------------\n"
            string += "| PLAYER-" + str(p.player_id) + "\n"
            string += "| Chips: " + str(p.chips) + "\n"
            string += "| Current Bet: " + str(p.current_bet) + "\n"
            string += "| Folded: " + str(p.folded) + "\n"
        string += "--------------------------\n"
        return string
        
    ####################################################
    
    
    class Player(object):

        def __init__(self, player_id, chips):
            self.player_id = player_id
            self.chips = chips
            self.current_bet = 0
            self.folded = False
            self.checked = False
            self.has_bet = False
        
            
                
