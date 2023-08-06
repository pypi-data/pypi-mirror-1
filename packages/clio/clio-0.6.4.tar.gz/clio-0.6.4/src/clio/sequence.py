"""
Implementation of a Sequence-like object for MySQL.
"""

from sqlalchemy import Table, Column, Integer
from sqlalchemy.sql import select

class Sequence(object):
    def __init__(self, name, metadata):
        self.name = name
        self.table = Table(name, metadata,
                           Column('id', Integer, nullable=False),
                           mysql_engine='InnoDB',
                           )
        self._initialized = False

    def _initialize(self, session):
        self._initialized = True
        # XXX is it correct to get the engine this way?
        self.table.create(bind=session.bind, checkfirst=True)
        r = session.execute(select([self.table]))
        if not r.fetchall():
            session.execute(self.table.insert().values(id=0))

    def __call__(self, session):
        if not self._initialized:
            self._initialize(session)            
        result = session.execute(
            'update %s set id=last_insert_id(id +1)' % self.name)
        return result.lastrowid

    def reinitialize(self):
        self._initialized = False

    def update(self, session, nr):
        """Update from table.
        """
        if not self._initialized:
            self._initialize(session)
        u = self.table.update().values(id=nr)
        session.execute(u)
        
