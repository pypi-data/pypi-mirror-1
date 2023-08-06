import re
from sqlalchemy import orm
from sqlalchemy.orm.collections import collection
import tables as ta

ARITH_NOT = 0
ARITH_NUMBER = 1
ARITH_FUNC = 2
ARITH_PRED = 3

class Expression(object):
    """
    An expression object

    Can be a predication (with truth value, and with args),
    an operation (with args)
    or an atom (with no args)

    >>> Expression(1)
    1
    >>> Expression('num', a=1)
    num(a=1)
    >>> Expression('greaterthan',a=1,f='num(s=that(d=baby,g=sucked))')
    greaterthan(a=1, f=num(s=that(d=baby, g=sucked)))
    """

    def __init__(self, symbol, **kwargs):
        """Symbol is a string or number;
        args are Expressions (or are coerced to Expressions).
        """
        self.true = True
        if isinstance(symbol, str) and symbol.startswith('~'):
            self.true = False
            symbol = symbol[1:]
        assert isinstance(symbol, str) or \
                    (isnumber(symbol) and not kwargs)
        # ARITH number
        if isnumber(symbol):
            self.arith = ARITH_NUMBER
        self.symbol = symbol
        self.arity = 0
        for arg_name, arg in kwargs.items():
            if not isinstance(arg, Expression):
                arg = expr(arg)
            arg.arg_name = arg_name
            self.arity += 1
            self.args.append(arg)
        # ARITH function
        if symbol in ops.keys():
            self.arith = ARITH_FUNC
        elif symbol in preds.keys():
            self.arith = ARITH_PRED
        elif is_variable(self):
            self.var = True
        self.set_depth()

    def __repr__(self):
        """
        """
        if len(self.args) == 0: # Constant or proposition with arity 0
            return str(self.symbol)
        true = not self.true and '~' or ''
        args = []
        for arg_name, arg in self.args.items():
            args.append('%s=%s' % (arg_name, repr(arg)))
        args.sort()
        return '%s%s(%s)' % (true, self.symbol, ', '.join(args))


    def __call__(self, **kwargs):
        """ (Taken from aima-python's logic.py)
        Self must be a symbol with no args, such as Expression('F').
        Create a new
        Expression with 'F' as op and the args as arguments."""
        assert is_symbol(self.symbol) and not self.args
        sym = self.symbol
        if not self.true:
            sym = '~' + self.symbol
        return Expression(sym, **kwargs)

    def set_depth(self, depth=0):
        self.depth = depth
        for arg in self.args:
            arg.set_depth(depth+1)

    def set_inrule(self, inrule=0):
        self.inrule = inrule
        for arg in self.args:
            arg.set_inrule(inrule)

    def covers(self, expression, substitutions=None):
        """
        self covers expression if a substitution of vars exist
        that makes self equal to expression, and returns the
        substitution (a dict of vars to expressions).
        If there is no such substition, returns False
        """
        if substitutions is None:
            substitutions = {}
        if self.true != expression.true or \
           self.arg_name != expression.arg_name or \
           self.depth != expression.depth:
            return False
        elif is_variable(self):
            try:
                subst = substitutions[self.symbol]
            except KeyError:
                substitutions[self.symbol] = expression
                return substitutions
            else:
                if subst == expression:
                    return substitutions
                return False
            # ARITH
#         elif self.arith == 2 and expression.arith == 1:
#             subs = \
#                 mods[self.symbol]['covers'](self, expression, substitutions)
#             if subs is False:
#                 return
#             for sub in subs.keys():
#                 substitutions[sub] = Expression(subs[sub])
        else:
            if self.symbol != expression.symbol or \
                    self.arity != expression.arity:
                return False
            for argname,arg in self.args.items():
                try:
                    exarg = expression.args[argname]
                except KeyError:
                    return False
                else:
                    substitutions = arg.covers(exarg, substitutions)
                    if substitutions is False:
                        break
        return substitutions

    def substitute(self, substitutions):
        if is_variable(self):
            try:
                subst = substitutions[self.symbol]
            except KeyError:
                subst = self
            subst = expr(repr(subst))
        else:
            sym = self.true and self.symbol or '~' + self.symbol
            subst = Expression(sym)
        subst.true = self.true
        for arg_name, arg in self.args.items():
            subst.args[arg_name] = arg.substitute(substitutions)
        subst.arity = len(subst.args.keys())
        # ARITH solve
        if subst.arith == ARITH_FUNC:
            subst = expr(solve(subst, ops))
        subst.set_depth(self.depth)
        subst.arg_name = self.arg_name
        return subst

preds = {'eq': '==', 'lt': '<', 'le': '<=', 'gt': '>', 'ge': '>='}
ops = {'sum': '+', 'dif': '-', 'mul': '*', 'div': '/'}

def solve(expression, ops=preds):
    op = '%s%s%s' % (expression.args['a1'].symbol,
                     ops[expression.symbol],
                     expression.args['a2'].symbol)
    try:
        result = eval(op)
    except NameError:
        return expression
    return result

class ArgList(dict):

    @collection.appender
    def append(self, item):
        self[item.arg_name] = item

    @collection.remover
    def remove(self, item):
        del self[item.arg_name]

    def __iter__(self):
        for arg in self.values():
            yield arg

orm.mapper(Expression, ta.expressions, allow_column_override=True,
                     properties={
            'args':  orm.relation(Expression,
                        collection_class=ArgList,
                        cascade="all",
                        post_update=True,
                        backref="parent"
                     )})


def expr(s):
    """Create an Expr representing a logic expression by parsing the input
    string. Symbols and numbers are automatically converted to Exprs.
    """
    if isinstance(s, Expression): return s
    if isnumber(s): return Expression(s)
    ## Replace a symbol or number, such as 'P' with 'Expr("P")'
    s=re.sub(r'(?<=[(,=])\s*(?!False|True|Expr)([a-zA-Z0-9_.~]+)\s*(?=[),(])',r'Expr("\1")', s)
    s=re.sub(r'^\s*([a-zA-Z0-9_.~]+)', r'Expr("\1")', s)
    ## Now eval the string.
    ## (A security hole; do not use with an adversary.)
    return eval(s, {'Expr':Expression})



def isnumber(x):
    "Is x a number? We say it is if it has a __int__ method."
    return hasattr(x, '__int__')

def is_symbol(s):
    "A string s is a symbol if it starts with an alphabetic char."
    return isinstance(s, str) and s[0].isalpha()

def is_var_symbol(s):
    "A logic variable symbol is an initial-uppercase string."
    return is_symbol(s) and s[0].isupper()

def is_variable(x):
    "A variable is an Expr with no args and a lowercase symbol as the op."
    return isinstance(x, Expression) and not x.args and \
                            is_var_symbol(x.symbol)

def num_or_str(x):
    """The argument is a string; convert to a number if possible, or strip it.
    >>> num_or_str('42')
    42
    >>> num_or_str(' 42x ')
    '42x'
    """
    if isnumber(x): return x
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
                return str(x).strip()


