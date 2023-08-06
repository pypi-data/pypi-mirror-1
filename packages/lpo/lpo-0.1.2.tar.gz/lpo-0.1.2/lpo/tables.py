import sqlalchemy as sa
from sqlalchemy.orm import scoped_session, sessionmaker
import config


engine = sa.create_engine(config.URL)
metadata = sa.MetaData(engine)
Session = scoped_session(sessionmaker(autoflush=True, transactional=True))

expressions = sa.Table('expressions', metadata,
    sa.Column('expression_id', sa.Integer,
                    sa.Sequence('expression_seq'),
                        primary_key=True),
    # the identifier / repr of the sentence
    # only for sentences in the model.
    sa.Column('name', sa.String, index=True),
    # the symbol (predicate/operator/atom) of this expression:
    # predicate nas null parent and arity > 0,
    # operator has parent and arity > 0,
    # atom has parent and arity == 0
    sa.Column('symbol', sa.String, index=True),
    # Predicates and operators have named args;
    # arg_name is the name of the arg for operations and atoms.
    sa.Column('arg_name', sa.String, nullable=True),
    # negation:
    # True/False for expressions with predicate (null parent),
    # Null for expressions with operators and atoms
    sa.Column('true', sa.Boolean, default=True),
    # an expression in a sentence in a rule can be a variable
    sa.Column('var', sa.Boolean, default=False),
    # Expressions can be sets, where args are unnamed,
    # or not, with named args
    sa.Column('depth', sa.Integer, default=0),
    # If a predicate or functor, n, if atom or var, 0
    sa.Column('arity', sa.Integer, default=0),
    # ARITH Expressions can be not arithmetic (0),
    # numbers, (1) or functions (2), or predicates (3)
    sa.Column('arith', sa.Integer, default=0),
    # Null for expressions with predicate (null parent),
    # expression_id for expressions with operators and atoms
    sa.Column('parent_id', sa.Integer,
                     sa.ForeignKey('expressions.expression_id'),
                             nullable=True, index=True),
    # If this expression is a prem or cons in a rule,
    # rule indicates to what rule it belongs
    sa.Column('rule_id', sa.Integer, sa.ForeignKey('rules.rule_id'),
                             nullable=True, index=True),
    # If this is a Prem, inrule is PREM (1); if a cons, CONS (2);
    # And if this expression is not in a rule (is in the model,)
    # inrule is MODEL (0)
    sa.Column('inrule', sa.Integer, default=0))

sa.Index('covering_expr1_ix', expressions.c.symbol,
                          expressions.c.arity)

sa.Index('covering_expr2_ix', expressions.c.true,
                          expressions.c.depth,
                          expressions.c.arg_name,
                          expressions.c.inrule)

sa.Index('extend_ix', expressions.c.inrule,
                          expressions.c.parent_id,
                          expressions.c.depth,
                          expressions.c.expression_id)

rules = sa.Table('rules', metadata,
    sa.Column('rule_id', sa.Integer,
            sa.Sequence('rule_seq'), primary_key=True),
    # the identifier for the rule
    sa.Column('name', sa.String, index=True))

proofs = sa.Table('proofs', metadata,
    sa.Column('step_id', sa.Integer,
                    sa.Sequence('proof_seq'),
                        primary_key=True),
    sa.Column('parent_expr', sa.Integer,
                     sa.ForeignKey('expressions.expression_id'),
                             index=True),
    sa.Column('parent_rule', sa.Integer, sa.ForeignKey('rules.rule_id'),
                             index=True),
    sa.Column('isrule', sa.Boolean, default=False),
    sa.Column('child_expr', sa.Integer,
                     sa.ForeignKey('expressions.expression_id'),
                             nullable=True, index=True),
    sa.Column('child_rule', sa.Integer, sa.ForeignKey('rules.rule_id'),
                             nullable=True, index=True))

counters = sa.Table('counters', metadata,
    sa.Column('counter_id', sa.Integer, sa.Sequence('counter_id_seq'),
                        primary_key=True),
    sa.Column('name', sa.String, index=True, unique=True),
    sa.Column('count', sa.Integer))

try:
    metadata.create_all()
except SQLError:
    rules = sa.Table('rules', metadata, autoload=True)
    expressions = sa.Table('expressions', metadata, autoload=True)
    counters = sa.Table('counters', metadata, autoload=True)
    proofs = sa.Table('proofs', metadata, autoload=True)
