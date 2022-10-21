#!/usr/bin/env python3

import random
import itertools

trials_per_config = 1000
best_config = []
best_rate = 0

def run_trial(cards, drawn, energy, locked):
    random.shuffle(cards)
    hand = cards[:drawn]
    # early outs before we to the MATHS
    if not sum(hand) == energy:
        return False
    if not locked[0] and not any(x for x in hand[:4] if x == 1):
        return False
    drawn_by_2 = 5
    if locked[0]:
        drawn_by_2 = 4
    if not locked[1] and not any(x for x in hand[:drawn_by_2] if x == 2):
        return
    ones_by_three = len([x for x in hand[:drawn_by_2 + 1] if x == 1])
    if locked[0]:
        ones_by_three += 1
    if ones_by_three < 2 and len([x for x in hand[:drawn_by_2 + 1] if x == 3]) == 0:
        return False
    if len([x for x in hand if x >= 4]) > 3:
        return False
    if len([x for x in hand if x >= 5]) > 2:
        return False
    if len([x for x in hand if x >= 6]) > 1:
        return False
    # MATHS
    for i in range(6): # Add the locked cards back in so that the MATHS can avoid special casing it
        if locked[i]:
            if i == 0:
                hand.insert(0, 1)
            else:
                hand.insert(i + 3, i + 1)
    for c in itertools.combinations(hand, 6):
        card_used = [False] * len(hand)
        # we have to play at least one card per turn, so the cards in the combination are our anchor card
        c = sorted(c)
        valid_sln = True
        for t in range(6):
            if c[t] > t + 1: # Cheapest card was too expensive
                valid_sln = False
                break 
            i = next((x for x in range(len(hand)) if hand[x] == c[t] and not card_used[x]), -1)
            if i > t + 3: # Have we drawn this card yet? on turn 0, we have access to indicies 0, 1, 2, 3
                valid_sln = False
                break
            card_used[i] = True
        if not valid_sln:
            continue
        for t in range(6):
            if c[t] == t + 1: # Have we spent all the energy already?
                continue
            r = (t + 1) - c[t]
            available_indicies = [x for x in range(len(hand) - 5 + t) if not card_used[x]]
            found = False
            for count in range(1, len(available_indicies) + 1):
                for sc in itertools.combinations(available_indicies, count):
                    cost = sum(hand[x] for x in sc)
                    if cost == r:
                        found = True
                        for i in sc:
                            card_used[i] = True
                        break
                if found:
                    break
            if not found:
                valid_sln = False
                break
        if valid_sln: # we already know the total energy works out, so if there's a solution to every turn, we don't have to check all cards are used
            return True
    return False

def try_config(config, locked):
    global best_config, best_rate
    successes = 0
    cards = []
    total_cost = 0
    drawn = 3 + 6 - sum(locked)
    for cost in range(6):
        cards_of_cost = config[cost]
        if locked[cost]:
            cards_of_cost -= 1
        else:
            total_cost += cost + 1
        if cards_of_cost < 0:
            return 
        cards += [cost + 1] * cards_of_cost
    for i in range(trials_per_config):
        if run_trial(cards, drawn, total_cost, locked):
            successes += 1
    rate = successes / trials_per_config
    if rate > best_rate:
        best_config = config
        best_rate = rate

def try_configs(locked, min_counts):
    cards = sum(locked)
    for sixes in range(min_counts[5], 12 - cards):
        cards += sixes
        for fives in range(min_counts[4], 12 - cards):
            cards += fives
            for fours in range(min_counts[3], 12 - cards):
                cards += fours
                for threes in range(min_counts[2], 12 - cards):
                    cards += threes
                    for twos in range(min_counts[1], 12 - cards):
                        ones = 12 - cards - twos
                        try_config([ones, twos, threes, fours, fives, sixes], locked)
                    cards -= threes
                cards -= fours
            cards -= fives
        cards -= sixes

def reset_globals():
    global best_rate, best_config
    best_config = []
    best_rate = 0

if __name__ == '__main__':
    #import pdb;pdb.set_trace()
    try_configs([False, False, False, False, False, False], [1] * 6)
    print(f"No fixed: {best_config}, {best_rate:2.7%}")
    reset_globals()
    try_configs([True, False, False, False, False, False], [1] * 6)
    print(f"With Quicksilver: {best_config}, {best_rate:2.7%}")
    reset_globals()
    try_configs([False, True, False, False, False, False], [1] * 6)
    print(f"With Domina: {best_config}, {best_rate:2.7%}")
    reset_globals()
    try_configs([True, True, False, False, False, False], [1] * 6)
    print(f"With Both: {best_config}, {best_rate:2.7%}")
