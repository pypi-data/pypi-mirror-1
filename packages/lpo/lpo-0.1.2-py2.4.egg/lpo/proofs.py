from sqlalchemy import orm
import tables as ta, expression as ex, rule

MODEL = 0
PREM = 1
CONS = 2

class Step(object):
    """
    """

    def __init__(self, parent_rule, parent_expr, child):
        """
        """
        self.antecedent_rule = parent_rule
        self.antecedent_expr = parent_expr
        if isinstance(child, ex.Expression):
            self.isrule = False
            self.consecuent_expr = child
        else:
            self.consecuent_rule = child
            self.isrule = True


    def __repr__(self):
        """
        """
        output = ''
        for parent in (self.parent_rule, self.parent_expr):
            if parent.antecedent is not None:
                output += repr(parent.antecedent)
        output += '-'*80 + '\n' + ' '*34 + 'PARENT RULE\n' +\
                        '-'*80 + '\n\n'
        output += repr(self.antecedent_rule)
        output += '\n\n' + '-'*80 + '\n' + ' '*31 + \
                                'PARENT EXPRESSION\n' +'-'*80 + '\n\n'
        output += repr(self.antecedent_expr)
        output += '\n\n' + '-'*80 + '\n' + ' '*34 + \
                                'CONSECUENCE\n' +'-'*80 + '\n\n'
        output += repr(self.child())
        output += '\n\n' + '-'*80 + '\n'

        return output

    def child(self):
        return self.isrule and self.consecuent_rule or self.consecuent_expr

orm.mapper(Step, ta.proofs,
                     properties={
            'antecedent_rule':  orm.relation(rule.Rule, uselist=False,
        primaryjoin=ta.rules.c.rule_id==ta.proofs.c.parent_rule,
          cascade='none', backref=orm.backref("consecuences", uselist=True,
        primaryjoin=ta.proofs.c.parent_rule==ta.rules.c.rule_id,
                lazy=True, cascade='none')),
            'antecedent_expr':  orm.relation(ex.Expression, uselist=False,
        primaryjoin=ta.expressions.c.expression_id==ta.proofs.c.parent_expr,
          cascade='none', backref=orm.backref("consecuences", uselist=True,
        primaryjoin=ta.proofs.c.parent_expr==ta.expressions.c.expression_id,
                lazy=True, cascade='none')),
            'consecuent_rule':  orm.relation(rule.Rule, uselist=False,
        primaryjoin=ta.rules.c.rule_id==ta.proofs.c.child_rule,
          cascade='none', backref=orm.backref("antecedent", uselist=False,
        primaryjoin=ta.proofs.c.child_rule==ta.rules.c.rule_id,
                            lazy=True, cascade="all")),
            'consecuent_expr':  orm.relation(ex.Expression, uselist=False,
        primaryjoin=ta.expressions.c.expression_id==ta.proofs.c.child_expr,
          cascade='none', backref=orm.backref("antecedent", uselist=False,
        primaryjoin=ta.proofs.c.child_expr==ta.expressions.c.expression_id,
                            lazy=True, cascade="all"))})
