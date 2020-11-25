# ----------------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------------
import argparse
import os
import sys
import re

from deck_calculator import deck_calculator
from scryfall.api import ScryfallAPI
from scryfall.output import output_card

# ----------------------------------------------------------------------------------
# Types
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# Globals
# ----------------------------------------------------------------------------------
_VALID_COLORS = ['U', 'B', 'G', 'R', 'W']

# ----------------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------------
def check_card(card, entry, deck_colors):
    return \
    check_price(card) and \
    check_legality(card) and \
    check_color(card, deck_colors) and \
    check_type(card, entry['types']) and \
    check_cmc(card, entry['cmc'])

# ----------------------------------------------------------------------------
def check_color(card, deck_colors):
    card_colors = card['color_identity']

    # Allow colorless for all cards
    if not card_colors: return True

    # Look at the card's color identity, if there is a color that is not in the
    # deck's colors, do not allow the card to be put into the deck
    allow_card = True
    for color in card_colors:
        if not color in deck_colors:
            allow_card = False
            break

    return allow_card

# ----------------------------------------------------------------------------
def check_cmc(card, cmc):
    if not cmc: return True
    if int(card['cmc']) == int(cmc): return True
    return False

# ----------------------------------------------------------------------------
def check_price(card, price=1.00):
    valid = False
    if card['prices']['usd']:
        valid = (float(card['prices']['usd']) <= price)
    return valid

# ----------------------------------------------------------------------------
def check_legality(card):
    valid = card['legalities']['legacy'] == 'legal' and 'paper' in card['games']
    return valid

# ----------------------------------------------------------------------------
def check_type(card, types):
    if types.lower() in card['type_line'].lower():

        if 'token' in card['type_line'].lower():  # Allow any card that doesn't have the word token
            return False

        elif types.lower() == 'artifact':  # Only allows pure artifacts
            if 'creature' in card['type_line'].lower():
                return False

        elif types.lower() == 'enchantment':  # Only allows pure enchantments
            if 'creature' in card['type_line'].lower():
                return False

        return True

    else:
        return False

# ----------------------------------------------------------------------------
def sanatize_colors(input_colors):
    sanatized = []
    for color in input_colors:
        if color.upper() in _VALID_COLORS:
            sanatized.append(color.upper())

    return sanatized

# ----------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------
def deck_generator(deck_colors):
    # Generate a name for the deck
    decklist = None
    for i in range(10000):
        name = 'decklist_{}.dec'.format(i)
        if not os.path.exists(name):
            decklist = name
            break

    # Exit the program if all decklist names are taken
    if not decklist: sys.exit('A deck name could not be generated, exiting program')

    # Initialize the API
    api = ScryfallAPI()

    # Create a list to hold all the cards we need to find
    generated_decklist = []

    # Open the decklist to generate
    with open("generate.dec", "r") as file:
        # pattern that matches a card for generation, exmaples
        # 4, Creature, 1
        # 1, Artifact
        # 2, Enchantment, 4
        generated_card_pattern = r'^(?P<amount>\d+),\s*(?P<types>\w+),?\s*(?P<cmc>\w+)?\s*$'

        for line in file:
            match = re.match(generated_card_pattern, line)
            if match:
                generated_decklist.append(match.groupdict())

    with open(decklist, 'w') as deck:
        for entry in generated_decklist:
            watchdog = api.database_size * 2  # In theory should loop over every card twice
            while watchdog:
                random_card = api.get_random_card_from_database()
                if check_card(random_card, entry, deck_colors):
                    card = '{amount} {name} ({expansion})\n'.format(amount=entry['amount'],
                                                                    name=random_card['name'],
                                                                    expansion=random_card['set'].upper() )
                    deck.write(card)
                    break

    deck_calculator(decklist=decklist, foil=False, api=api)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generates a random deck')
    parser.add_argument(dest='colors', nargs='*', default=[], help='Deck file name')
    args = parser.parse_args()
    deck_colors = sanatize_colors(args.colors)
    print("Generating a deck with the following colors: {}".format(', '.join(deck_colors)))

    deck_generator(deck_colors=deck_colors)