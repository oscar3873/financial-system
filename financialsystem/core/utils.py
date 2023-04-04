from decimal import Decimal


def round_to_nearest_hundred(x):
    if x % Decimal('100') >= Decimal('50'):
        return (x // Decimal('100') + 1) * Decimal('100')
    else:
        return (x // Decimal('100')) * Decimal('100')

def round_to_nearest_special(x):
    if x < 150:
        return round(x / 10) * 10
    else:
        base = round(x / 100) * 100
        if x - base < 50:
            return base
        else:
            return base + 100