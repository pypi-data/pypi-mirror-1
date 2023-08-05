from datetime import date
from decimal import Decimal

from peak.api import *


ZERO = Decimal("0.00")


class Date(date):

    def __str__(self):
        return self.strftime("%d.%m.%Y")


class DateRange(object):

    def __init__(self, d1, d2):
        self.d1 = d1
        self.d2 = d2
        
    def contains(self, date):
        return self.d1 <= date <= self.d2


class Currency(model.Enumeration):

    USD = model.enum('USD')
    EUR = model.enum('EUR')  


class Money(model.Struct):

    """Immutable Money type containing amount and currency."""

    class amount(model.structField):
        referencedType = Decimal
        defaultValue = ZERO

    class currency(model.structField):
        referencedType = Currency
        defaultValue = Currency.EUR
    
    def __init__(self, amount=0, currency=Currency.EUR):
        super(Money, self).__init__(
            amount=Decimal(str(amount)), currency=currency)
    
    def __add__(self, other):
        assert isinstance(other, Money)
        assert self.currency == other.currency
        return Money(amount=self.amount+other.amount, 
                            currency=self.currency)
    
    def __sub__(self, other):
        assert isinstance(other, Money)
        assert self.currency == other.currency
        return Money(amount=self.amount-other.amount,
                            currency=self.currency)
    
    def __str__(self):
        if self.amount == ZERO:
            return "0.00"
        else:
            return moneyformat(self.amount, overall=None)

    def __nonzero__(self):
        return self.amount != 0

    def mdl_normalize(klass, value):
        return value

    def mdl_fromFields(klass, fieldSeq):
        """Return a new instance from a sequence of fields"""
        return klass()
    
    def mdl_fromString(klass, value):
        return klass(amount=Decimal(value))

    def mdl_toString(klass, value):
        return value.amount + value.currency

    def __neg__(self):
        return Money(-self.amount, self.currency)


Money.Zero = Money()


class MovementType(model.Enumeration):

    CREDIT = model.enum()
    DEBIT = model.enum()


def moneyformat(value, places=2, curr='', sep='.', dp=',', pos='', 
                        neg='-', overall=10):
    """ Convert Decimal ``value'' to a money-formatted string. 
    
    places:    required number of places after the decimal point 
    curr:       optional currency symbol before the sign (may be blank) 
    sep:        optional grouping separator (comma, period, or blank) every 3 
    dp:         decimal point indicator (comma or period); 
                    only specify as blank when places is zero 
    pos:        optional sign for positive numbers: "+", space or blank 
    neg:        optional sign for negative numbers: "-", "(", space or blank 
    overall:   optional overall length of result, adds padding on the left, 
                    between the currency symbol and digits 
    """
    q = Decimal((0, (1,), -places))     # 2 places --> '0.01' 
    sign, digits, exp = value.quantize(q).as_tuple( ) 
    result = [ ] 
    digits = map(str, digits) 
    append, next = result.append, digits.pop 
    for i in range(places): 
        if digits: 
            append(next( ))
        else: 
            append('0') 
    append(dp) 
    i = 0 
    while digits: 
        append(next( )) 
        i += 1 
        if i == 3 and digits: 
            i = 0 
            append(sep) 
    while len(result) < overall: 
        append(' ') 
    append(curr) 
    if sign: append(neg) 
    else: append(pos) 
    result.reverse( ) 
    return ''.join(result)
