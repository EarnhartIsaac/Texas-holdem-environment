from enum import Enum

class OrderedEnum(Enum):
     def __ge__(self, other):
         if self.__class__ is other.__class__:
             return self.value >= other.value
         return NotImplemented
     def __gt__(self, other):
         if self.__class__ is other.__class__:
             return self.value > other.value
         return NotImplemented
     def __le__(self, other):
         if self.__class__ is other.__class__:
             return self.value <= other.value
         return NotImplemented
     def __lt__(self, other):
         if self.__class__ is other.__class__:
             return self.value < other.value
         return NotImplemented

#Finish dict of cards                                                                                
CARD_NAMES = ['AS', 'KS', 'QS', 'JS', '10S', '9S', '8S', '7S', '6S', '5S', '4S', '3S', '2S',
              'AH', 'KH', 'QH', 'JH', '10H', '9H', '8H', '7H', '6H', '5H', '4H', '3H', '2H',
              'AC', 'KC', 'QC', 'JC', '10C', '9C', '8C', '7C', '6C', '5C', '4C', '3C', '2C',
              'AD', 'KD', 'QD', 'JD', '10D', '9D', '8D', '7D', '6D', '5D', '4D', '3D', '2D']

CARD_SET = list(range(0, 52))
CARD_ENUM = dict(zip(CARD_SET, CARD_NAMES))
CARD_ENUM_REV = dict(zip(CARD_NAMES, CARD_SET))

class Hands(OrderedEnum):
    ROYAL_FLUSH = 1
    STRAIGHT_FLUSH = 2
    FOUR_OF_A_KIND = 3
    FULL_HOUSE = 4
    FLUSH = 5
    STRAIGHT = 6
    THREE_OF_A_KIND = 7
    TWO_PAIR = 8
    ONE_PAIR = 9
    HIGH_CARD = 10
    NO_HAND = 11

ROYAL_FLUSHES = [ {0,1,2,3,4},
                  {13,14,15,16,17},
                  {26,27,28,29,30},
                  {39,40,41,42,43} ]


STRAIGHT_FLUSHES = []
STRAIGHT_FLUSH_HIGHS = []
#Identifies the high(lowest) card cooresponding to straight_flush                                   

#-------------------------------------
# Building Straight flush lists
#-------------------------------------
start_straight = set([0,1,2,3,4])
temp_set = set()
for i in range(0, 4):
     STRAIGHT_FLUSHES.append(start_straight)
     temp_straight = start_straight.copy()
     temp_set.clear()
     for j in range(5, 13):
          STRAIGHT_FLUSH_HIGHS.append(j - 5)
          temp_straight.remove(j - 5 + i*13)
          temp_straight.add(j + i*13)
          STRAIGHT_FLUSHES.append(temp_straight.copy())
     STRAIGHT_FLUSH_HIGHS.append(8)
     #Add in A, 2, 3, etc. straight
     STRAIGHT_FLUSH_HIGHS.append(0)
     temp_straight.remove(8 + i*13)
     temp_straight.add(i*13)
     STRAIGHT_FLUSHES.append(temp_straight.copy())
     
     temp_straight = start_straight.copy()
     for j in range(0, 5):
          temp = temp_straight.pop()
          temp_set.add(temp + 13)
     start_straight = temp_set.copy()
#--------------------------------------


# Returns the subset of cards to make the flush
# along with the high cards
def is_flush(cards : set):
    suits = [[], [], [], []]
    for x in cards:
        if x < 13:
            suits[0].append(x)
        elif x < 26:
            suits[1].append(x)
        elif x < 39:
            suits[2].append(x)
        else:
            suits[3].append(x)

    flush_suit_high_cards = [13, 13, 13, 13, 13]
    flush_suit = -1
    for i in range(0, len(suits)):
        suits[i].sort()
        if len(suits[i]) >= 5:
            j = 0
            #Just in case we have multiple flushes, find best one
            while (suits[i][j] % 13) == flush_suit_high_cards[j]:
                j += 1
            if (suits[i][j] % 13) < flush_suit_high_cards[j]:
                flush_suit_high_cards = suits[i]
                flush_suit = i

    #Normalize high cards
    for i in range(0,len(flush_suit_high_cards)):
        flush_suit_high_cards[i] = flush_suit_high_cards[i] % 13
    
    if flush_suit == -1:
        return (set(), [])
    else:
        return (set(suits[flush_suit][0:5]), suits[flush_suit][0:5])

def is_straight(cards : set):
     cards_proj = {}
     for x in cards:
         #duplicates shouldnt matter
          cards_proj[x % 13] = x
     for i in range(0, len(STRAIGHT_FLUSHES)):
          if STRAIGHT_FLUSHES[i].issubset(set(cards_proj.keys())):
               used_cards = set()
               for key in cards_proj:
                    if key in STRAIGHT_FLUSHES[i]:
                         used_cards.add(cards_proj[key])
               return (used_cards, [STRAIGHT_FLUSH_HIGHS[0], 13, 13, 13, 13])
     return (set(), [])
        

def new_found_hand(new_hand, best_hand,
                   new_high_card, best_high_card,
                   new_used_cards, best_used_cards):
    if best_hand > new_hand:
        best_high_card = (new_high_card % 13)
        best_hand = new_hand
        best_used_cards = new_used_cards
    elif best_hand is new_hand:
        if best_high_card > (new_high_card % 13):
            best_used_cards = new_used_cards
        best_high_card = min(best_high_card, (new_high_card % 13))
    return (best_hand, best_high_card, best_used_cards)

# Returns the best hand, along with a list of high cards and
# the set of cards used
def hand_score(cards : set):
    best_hand = Hands.HIGH_CARD
    list_cards = list(cards)
    list_cards.sort()
    high_cards = [13, 13, 13, 13, 13]
    used_cards = [set([]),set([])]
    
    #Royal Flush
    for x in ROYAL_FLUSHES:
        if x.issubset(cards):
            (bh, bhc, buc) = new_found_hand(Hands.ROYAL_FLUSH, best_hand,
                           0, high_cards[0],
                           x, used_cards[0])
            best_hand = bh
            high_cards[0] = bhc
            used_cards[0] = buc
            high_cards = [high_cards[0], 13, 13, 13, 13]
            used_cards[1] = set([])
    
    #Straight Flush
    for i in range(0, len(STRAIGHT_FLUSHES)):
        if STRAIGHT_FLUSHES[i].issubset(cards):
            (bh, bhc, buc) = new_found_hand(Hands.STRAIGHT_FLUSH, best_hand,
                           STRAIGHT_FLUSH_HIGHS[i], high_cards[0],
                           STRAIGHT_FLUSHES[i], used_cards[0])
            best_hand = bh
            high_cards[0] = bhc
            used_cards[0] = buc
            high_cards = [high_cards[0], 13, 13, 13, 13]
            used_cards[1] = set([])

    #-----------------
    # PAIR MATCHING
    #-----------------
    # Optimized so that known matches
    # can be directly converted into
    # higher hands
    #-----------------
    
    cards_copy = cards.copy()
    # For all cards given
    num_cards = len(cards_copy)
    i = 0
    while i < num_cards:
        temp_card = cards_copy.pop()
        temp_high_card = temp_card % 13
        temp_set = set([temp_card])
        temp_card = temp_card % 13
        for j in range(0, 4):
             if temp_card in cards_copy:
                 cards_copy.remove(temp_card)
                 i += 1
                 temp_set.add(temp_card)
             temp_card += 13
        i += 1
        
        count = len(temp_set)

        if count == 4:
            (bh, bhc, buc) = new_found_hand(Hands.FOUR_OF_A_KIND, best_hand,
                           temp_high_card, high_cards[0],
                           temp_set, used_cards[0])
            best_hand = bh
            high_cards[0] = bhc
            used_cards[0] = buc
            
        if count == 3:
            if best_hand == Hands.ONE_PAIR or best_hand == Hands.TWO_PAIR:
                high_cards[1] = high_cards[0]
                used_cards[1] = used_cards[0]
                (bh, bhc, buc) = new_found_hand(Hands.FULL_HOUSE, best_hand,
                               temp_high_card, high_cards[0],
                               temp_set, used_cards[0])
                best_hand = bh
                high_cards[0] = bhc
                used_cards[0] = buc
                
                
            elif best_hand == Hands.FULL_HOUSE:
                if temp_high_card < high_cards[0]:
                    if high_cards[0] < high_cards[1]:
                        high_cards[1] = high_cards[0]
                        used_cards[1] = used_cards[0]
                        #We use our other three of a kind for pair in full house
                        used_cards[1].pop()
                    #Set full house 3 to our new 3 of a kind
                    high_cards[0] = temp_high_card
                    used_cards[0] = temp_set
                elif temp_high_card < high_cards[1]:
                    high_cards[1] = temp_high_card
                    used_cards[1] = temp_set
                    #We use this three of a kind as pair for full house
                    used_cards[1].pop()

            elif best_hand == Hands.THREE_OF_A_KIND:
                if temp_high_card < high_cards[0]:
                    high_cards[1] = high_cards[0]
                    used_cards[1] = used_cards[0]
                    #We use our other three of a kind for pair in full house
                    used_cards[1].pop()
                    (bh, bhc, buc) = new_found_hand(Hands.FULL_HOUSE, best_hand,
                                          temp_high_card, high_cards[0],
                                          temp_set, used_cards[0])
                    best_hand = bh
                    high_cards[0] = bhc
                    used_cards[0] = buc
                else:
                    high_cards[1] = temp_high_card
                    used_cards[1] = temp_set
                    best_hand = Hands.FULL_HOUSE
            else:
                (bh, bhc, buc) = new_found_hand(Hands.THREE_OF_A_KIND, best_hand,
                               temp_high_card, high_cards[0],
                               temp_set, used_cards[0])
                best_hand = bh
                high_cards[0] = bhc
                used_cards[0] = buc

        #2 case complete
        if count == 2:
            if best_hand == Hands.ONE_PAIR:
                if temp_high_card < high_cards[0]:
                    high_cards[1] = high_cards[0]
                    used_cards[1] = used_cards[0]
                    (bh, bhc, buc) = new_found_hand(Hands.TWO_PAIR, best_hand,
                                   temp_high_card, high_cards[0],
                                   temp_set, used_cards[0])
                    best_hand = bh
                    high_cards[0] = bhc
                    used_cards[0] = buc
                else:
                    high_cards[1] = temp_high_card
                    used_cards[1] = temp_set
                    best_hand = Hands.TWO_PAIR
                

            elif best_hand == Hands.TWO_PAIR:
                if temp_high_card < high_cards[0]:
                    high_cards[1] = high_cards[0]
                    used_cards[1] = used_cards[0]
                    high_cards[0] = temp_high_card
                    used_cards[0] = temp_set
                elif temp_high_card < high_cards[1]:
                    high_cards[1] = temp_high_card
                    used_cards[1] = temp_set
                

            elif best_hand == Hands.THREE_OF_A_KIND:
                high_cards[1] = temp_high_card
                used_cards[1] = temp_set
                best_hand = Hands.FULL_HOUSE
                

            elif best_hand == Hands.FULL_HOUSE:
                if temp_high_card < high_cards[1]:
                    high_cards[1] = temp_high_card
                    used_cards[1] = temp_set
                

            else:
                (bh, bhc, buc) = new_found_hand(Hands.ONE_PAIR, best_hand,
                               temp_high_card, high_cards[0],
                               temp_set, used_cards[0])
                best_hand = bh
                high_cards[0] = bhc
                used_cards[0] = buc
            

    #Checking for flush
    (temp_set, temp_high_card) = is_flush(cards)
    if len(temp_set) != 0:
        if best_hand > Hands.FLUSH:
            best_hand = Hands.FLUSH
            high_cards = temp_high_card
            used_cards[0] = temp_set
            used_cards[1] = set([])


    #Checking for straight
    (temp_set, temp_high_card) = is_straight(cards)
    if len(temp_set) != 0:
        if best_hand > Hands.STRAIGHT:
            best_hand = Hands.STRAIGHT
            high_cards = temp_high_card
            used_cards[0] = temp_set
            used_cards[1] = set([])

    #Adding high cards for calculations
    rest = set()
    rest |= cards
    for s in used_cards:
        rest -= s
    for x in rest:
        x = x % 13
    rest_list = list(rest)
    for i in range(0, len(rest_list)):
         rest_list[i] = rest_list[i] % 13
    rest_list.sort()
        
    if best_hand == Hands.FOUR_OF_A_KIND:
        high_cards[4] = 13
        high_cards[3] = 13
        high_cards[2] = 13
        high_cards[1] = rest_list[0]
    elif best_hand == Hands.FULL_HOUSE:
        high_cards[4] = 13
        high_cards[3] = 13
        high_cards[2] = 13
    elif best_hand == Hands.THREE_OF_A_KIND:
        high_cards[4] = 13
        high_cards[3] = 13
        high_cards[2] = rest_list[1]
        high_cards[1] = rest_list[0]
    elif best_hand == Hands.TWO_PAIR:
        high_cards[4] = 13
        high_cards[3] = 13
        high_cards[2] = rest_list[0]
    elif best_hand == Hands.ONE_PAIR:
        high_cards[4] = 13
        high_cards[3] = rest_list[2]
        high_cards[2] = rest_list[1]
        high_cards[1] = rest_list[0]
    elif best_hand == Hands.HIGH_CARD:
        high_cards = rest_list[0:5]
    
    return (best_hand, high_cards, used_cards)

def compare_hands(score_1, score_2) -> int:
    (type_1, high_cards_1, set_1) = score_1
    (type_2, high_cards_2, set_2) = score_2
    if type_1 > type_2:
        return -1
    elif type_2 > type_1:
        return 1
    else:
        i = 0
        while high_cards_1[i] != high_cards_2[i]:
            i += 1
            if i == 5:
                return 0
        if high_cards_1[i] > high_cards_2[i]:
            return -1
        else:
            return 1
