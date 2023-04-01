from decimal import Decimal


def round_to_nearest_hundred(x):
    if x % Decimal('100') >= Decimal('50'):
        return (x // Decimal('100') + 1) * Decimal('100')
    else:
        return (x // Decimal('100')) * Decimal('100')

def round_to_nearest_special(x):
    if x % Decimal('1') == 0:
        return x
    elif x < Decimal('100'):
        if x % Decimal('10') >= Decimal('5'):
            return (x // Decimal('10') + 1) * Decimal('10')
        else:
            return (x // Decimal('10')) * Decimal('10')
    else:
        return round(x)