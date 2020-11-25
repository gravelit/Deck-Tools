# ----------------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------------
import argparse
import re

from scryfall.api import ScryfallAPI
from scryfall.output import output_card, output_sideboard, output_total

# ----------------------------------------------------------------------------------
# Types
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# Globals
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------
def deck_calculator(decklist, foil=False, api=None):
    # Initialize the API if one wasn't given
    if not api:
        api = ScryfallAPI()

    # Regex for a card in the decklist exported from MTG Top 8 as MTGA, examples:
    # 2 Lightning Bolt (MM2)
    # 1 Worldslayer (MRD) 276
    # 4 Thalia, Guardian of Thraben (DKA)
    card_pattern = r'^(?P<amount>\d+)(?P<name>\s*[^(]+)\((?P<expansion>[0-9A-Z]{3})\)\s*(\d+)?\s*$'

    # Open the decklist file
    with open(decklist, "r") as file:
        # Total dollar amount for deck
        total = 0
        total_foil = 0

        # Iterate over each line in the decklist
        for line in file:
            # Check if the line in the decklist matches the card pattern
            # we are looking for
            match = re.match(card_pattern, line)
            if match:
                # Parse the number of cards, card name, and set from the line
                amount = int(match.groupdict()["amount"].strip())
                name = match.groupdict()["name"].strip()
                expansion = match.groupdict()["expansion"].strip()

                # Determine the rarity of the card
                rarity = api.get_card_rarity(name, expansion)

                price = api.get_card_price(name, expansion)
                price_foil = api.get_card_price(name, expansion, 'usd_foil')

                # No USD price associated with this card
                # This could be due to it only being released on MTGO
                if not price:
                    price = '0.00'
                total += float(price) * amount

                # If foil price is not available, use regular price
                if not price_foil:
                    price_foil = price
                total_foil += float(price_foil) * amount

                # Print out the card
                if foil:
                    output_card(name, amount, price_foil, expansion, rarity)
                else:
                    output_card(name, amount, price, expansion, rarity)

            else:
                # If a sideboard was included, indicate that in the output
                if 'sideboard' in line.lower():
                    output_sideboard()

        if foil:
            output_total(total_foil, foil)
        else:
            output_total(total, foil)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculates the cost of a deck using the Scryfall API')
    parser.add_argument(dest='decklist', nargs='?', default='decklist.dec', help='Deck file name')
    parser.add_argument('--foil', dest='foil', action='store_true', help='Foils out the deck')
    args = parser.parse_args()

    deck_calculator(args.decklist, args.foil)