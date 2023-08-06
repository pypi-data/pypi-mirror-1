import re
import sqlalchemy as sa
from sqlalchemy.exceptions import InvalidRequestError
import tables as ta, expression as ex, counter as co, rule, proofs

class ParadoxError(Exception):
    """
    """
    def __init__(self, expr1, expr2, messg):
        self.expr1 = expr1
        self.expr2 = expr2
        self.message = messg

    def __str__(self):
        return """Contradiction between \n%s\nand\n%s""" % (self.expr1,
                                                            self.expr2)

def get_counter():
    counter = \
     ta.Session().query(co.Counter).filter_by(name='extension').all()
    if counter:
        counter = counter[0]
        counter.algo = lambda x: x
    else:
        counter = co.Counter('extension',
                        start=0,
                        algo=lambda x: x)
        ta.Session().save(counter)
    return counter

def add_expr(e, flush=True, step=None):
    e = ex.expr(e)
    e.name = re.sub(r'\s+', r'', repr(e))
#     if e.name == 'isa(c=fact,e=prop(s=john,t=0,v=haspermission(action=view,content=doc1)))':
#         import pdb;pdb.set_trace()
    try:
        return \
     ta.Session().query(ex.Expression).filter_by(name=e.name).one()
    except InvalidRequestError:
        pass
    negated = ex.expr(repr(e))
    negated.true = not e.true
    negated = get_same_expr(negated)
    if negated:
        raise ParadoxError(e, negated, 'there is a contradiction')
    if e.arith == ex.ARITH_PRED:
        truth = ex.solve(e)
        if isinstance(truth, int):
            if not truth:
                raise ParadoxError(e, e, 'Arithmetic falsity')
            else:
                return e
    ta.Session().save(e)
    if flush:
        ta.Session().flush()
    return e

def add_rule(r, flush=True, step=None):
    if isinstance(r, basestring):
        r = rule.rule(r)
    r.name = re.sub(r'\s+', r'', repr(r))
    try:
        return ta.Session().query(rule.Rule).filter_by(name=r.name).one()
    except InvalidRequestError:
        pass
    ta.Session().save(r)
    if flush:
        ta.Session().flush()
    return r

def tell(sen):
    sen = ('-->' in sen) and add_rule(sen) or add_expr(sen)
    return sen

def delete(e, _first_round=True):# XXX falsta poder borrar rules
    if isinstance(e, str):
        e = get_same_expr(e)
    if e is None:
        return
    if _first_round and e.antecedent:
        raise ParadoxError(e, e, "you cannot delete consecuences")
    for consec in e.consecuences:
        child = consec.child()
        ta.Session().delete(consec)
        delete(child, _first_round=False)
    ta.Session().delete(e)
    ta.Session().expunge(e)
    if _first_round:
        ta.Session().flush()

def get_same_expr(expression):
    """
    """
    expression = ex.expr(expression)
    name = re.sub(r'\s+', r'', repr(expression))
    old = ta.Session().query(ex.Expression).filter_by(name=name).all()
    return old and old[0] or None



def get_covering_exprs(expr, inrule=rule.PREM):
    """
    """
    query=ta.Session().query(ex.Expression)
    query = query.filter(sa.and_(ex.Expression.c.true==expr.true,
                                ex.Expression.c.depth==expr.depth,
                                ex.Expression.c.arg_name==expr.arg_name,
                                ex.Expression.c.inrule==inrule,
                                sa.or_(
                                 sa.and_(ex.Expression.c.symbol==expr.symbol,
                                          ex.Expression.c.arity==expr.arity),
                                       ex.Expression.c.var==True,
                                       sa.and_(expr.arith==1,
                                            ex.Expression.c.arith==2))))
    if query.count() <= 0:
        return []
    else:
        for subexpr in expr.args.values():
            subs = get_covering_exprs(subexpr,
                                        inrule)
            if not subs:
                return []
            subs = [int(sub.parent_id) for sub in subs]
            query = query.filter(sa.or_(
                                ex.Expression.c.var==True,
                                ex.Expression.c.expression_id.in_(*subs)))
    return query.all() # XXX no select, subqueries en vez de subs
                          # performancewise?

def extend():
    """
    Given a sentence set, extend it to contain all sentences (and rules)
    that are consecuences of the sentences (and rules) it contains.
    """
    counter = get_counter()
    exprq = ta.Session().query(ex.Expression)
    ruleq = ta.Session().query(rule.Rule)
    sentences = exprq.filter(sa.and_(ex.Expression.c.name!=None,
                            ex.Expression.c.expression_id>counter())
                ).order_by(sa.asc(ex.Expression.c.expression_id))
    if sentences.count() == 0:
        return True
    for sentence in sentences:
        prems = get_covering_exprs(sentence)
        for p in prems:
            var_dict = p.covers(sentence)
            if var_dict is False:
                continue
            old_rule = ruleq.filter_by(rule_id=p.rule_id).one()
            sister_prems = old_rule.get_prems(p)
            cons = old_rule.get_cons()
            bad_rule = False
            if sister_prems:
                new_rule = rule.Rule()
                for prem in sister_prems:
                    new_prem = prem.substitute(var_dict)
                    if new_prem.arith == ex.ARITH_PRED:
                        truth = ex.solve(e)
                        if isinstance(truth, int):
                            if not truth:
                                bad_rule = True
                                break
                            else:
                                continue
                    new_prem.set_inrule(rule.PREM)
                    new_rule.sentences.append(new_prem)
                if not bad_rule:
                    for con in cons:
                        new_con = con.substitute(var_dict)
                        new_con.set_inrule(rule.CONS)
                        new_rule.sentences.append(new_con)
                    add_rule(new_rule,
                          step=proofs.Step(old_rule, sentence, new_rule))
            else:
                for con in cons:
                    new_sen = con.substitute(var_dict)
                    new_sen.set_inrule(rule.MODEL)
                    #new_sen.parents = parents
                    add_expr(new_sen,
                              step=proofs.Step(old_rule, sentence, new_sen))
        counter(sentence.expression_id)
        ta.Session().flush()
    return extend()

def ask(q, mod='truth'):
    if mod == 'truth':
        #import pdb; pdb.set_trace()
        a = get_same_expr(ex.expr(q))
        return a and a or False



# def get_covered_exprs(expr):
#     """
#     """
#     query=ta.session.query(Expression)
#     if expr.var:
#         query = query.filter_by(
#                     inrule=expr.inrule or 0,
#                             true=expr.true,
#                                 arg_name=expr.arg_name)
#     else:
#         query = query.filter_by(
#                     symbol=expr.symbol,
#                         set=expr.set or False,
#                             true=expr.true)
#     #import pdb;pdb.set_trace()
#     if query.count() <= 0:
#         return []
#     elif not expr.var:
#         for subexpr in expr.args.values():
#             subs = get_covered_exprs(subexpr)  # XXX meter with_parent puede ahorrar
#             if not subs:
#                 return []
#             subs = [int(sub.parent_id) for sub in subs]
#             query = query.filter(
#                             ta.expressions.c.expression_id.in_(*subs))
#     return query.select()   return False
