from decimal import Decimal


def round_to_nearest_hundred(x):
    if x % Decimal('100') >= Decimal('50'):
        return (x // Decimal('100') + 1) * Decimal('100')
    else:
        return (x // Decimal('100')) * Decimal('100')
