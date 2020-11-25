# ----------------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# Globals
# ----------------------------------------------------------------------------------

_NORMAL = "\033[38;5;{color}m"
_BOLDED = "\033[1;38;5;{color}m"
_RESET = "\033[0m"

# ----------------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------------
def output_card(card, amount, price, expansion, rarity, bold=False):
    # curl -s https://gist.githubusercontent.com/HaleTom/89ffe32783f89f403bba96bd7bcd1263/raw/ | bash
    colors = {
        'common': 58,
        'uncommon': 244,
        'rare': 184,
        'mythic': 166,
        'unknown': 1,
    }

    style = _NORMAL
    if bold:
        style = _BOLDED

    rarity = rarity.lower()

    output = 'x{amount} {name:<33} | {expansion} | ${price:<7}'.format(name=card,
                                                                       amount=amount,
                                                                       price=price,
                                                                       expansion=expansion)

    print(style.format(color=colors[rarity]) + output + _RESET)

# ------------------------------------------------------------------------
def output_sideboard():
    print('' + _RESET)

# ------------------------------------------------------------------------
def output_total(total, foil=False):
    if foil:
        text = 'Total (Foil)'
    else:
        text = 'Total (Non-foil)'
    print('\n{text:<44} ${total:.2f}'.format(text=text, total=total) + _RESET)
