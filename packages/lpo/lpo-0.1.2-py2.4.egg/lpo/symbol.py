from sqlalchemy import orm
import tables as ta

class Symbol(object):
    """
    A symbol object.
    Has a name and an arity.

    >>> symbol = Symbol('one', 2)
    >>> symbol.name
    'one'
    >>> symbol.arity
    2
    """

    def __init__(self, name, arity):
        """
        """
        self.name = name
        self.arity = arity

orm.mapper(Symbol, ta.symbols)
