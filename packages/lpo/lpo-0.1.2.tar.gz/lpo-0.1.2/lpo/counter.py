# vim: set fileencoding=utf-8 :
from sqlalchemy import orm
import tables as ta

class Counter(object):
    """
    """
    def __init__(self, name, start=0, algo=None):
        self.name = name
        self.count = start
        if algo is None:
            algo = lambda x: x+1
        self.algo = algo

    def __call__(self, count=None):
        if count is None:
            self.count = self.algo(self.count)
        else:
            self.count = count
        return self.count

    def reset(self, start=0):
        self.count = start

orm.mapper(Counter, ta.counters)

