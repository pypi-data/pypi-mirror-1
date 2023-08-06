import re
from sqlalchemy import orm
import tables as ta, expression as ex

MODEL = 0
PREM = 1
CONS = 2

class Rule(object):
    """
    >>> Rule(prems=[1], cons=[2])
    1
    -->
    2
    """

    def __init__(self, prems=None, cons=None):
        """
        """
        if prems:
            for prem in prems:
                prem = ex.expr(prem)
                prem.set_inrule(PREM)
                self.sentences.append(prem)
        if cons:
            for con in cons:
                con = ex.expr(con)
                con.set_inrule(CONS)
                self.sentences.append(con)

    def __repr__(self):
        """
        """
        prems = self.get_prems()
        prems = map(repr, prems)
        prems.sort()
        cons = self.get_cons()
        cons = map(repr, cons)
        cons.sort()
        return "%s\n-->\n%s" % (';\n'.join(prems),
                                ';\n'.join(cons))

    def get_prems(self, exclude=None):
        prems = []
        for s in self.sentences:
            if s.inrule == PREM and repr(s) != repr(exclude):
                prems.append(s)
        return prems

    def get_cons(self):
        cons = []
        for s in self.sentences:
            if s.inrule == CONS:
                cons.append(s)
        return cons

orm.mapper(Rule, ta.rules,
                     properties={
            'sentences':  orm.relation(ex.Expression,
        primaryjoin=ta.expressions.c.rule_id==ta.rules.c.rule_id,
                        cascade="all",
                        backref=orm.backref("rule")
                     )})


def rule(r):
    """Create an Expr representing a logic expression by parsing the input
    string. Symbols and numbers are automatically converted to Exprs.
    """
    if isinstance(r, Rule): return r
    r = re.sub(r'\s+', r'', r)
    m = re.match(r'^(.*)-->(.*)$', r)
    prems = m.group(1).split(';')
    cons = m.group(2).split(';')
    return Rule(prems, cons)
