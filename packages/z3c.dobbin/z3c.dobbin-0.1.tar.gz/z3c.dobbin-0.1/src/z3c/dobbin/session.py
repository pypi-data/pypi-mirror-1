from zope import interface

from transaction.interfaces import ISavepointDataManager
from transaction import get as getTransaction

import bootstrap

from ore.alchemist import Session

class Savepoint:
    """Transaction savepoint."""

    def rollback(self):
        raise NotImplementedError("Rollbacks are not implemented.")

class TransactionManager(object):
    """Transaction manager for the database session.

    This is used to synchronize relations to concrete items.    
    """
    
    interface.implements(ISavepointDataManager)

    def __init__(self, obj):
        self.registered = False
        self.vote = False
        self.obj = obj

        session = Session()

        try:
            session._d_pending[obj._d_uuid] = obj
        except AttributeError:
            session._d_pending = {obj._d_uuid: obj}
        
    def register(self):
        if not self.registered:
            getTransaction().join(self)
            self.registered = True
            
    def savepoint(self):
        return Savepoint()

    def tpc_begin(self, transaction):
        pass

    def commit(self, transaction):
        obj = self.obj
        uuid = obj._d_uuid
        instance = bootstrap.lookup(uuid)

        # set attributes on instance
        for iface in interface.providedBy(obj):
            for name in iface.names():
                value = getattr(obj, name)
                setattr(instance, name, value)

        session = Session()
        del session._d_pending[uuid]
        
    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        self.registered = False

    def tpc_abort(self, transaction):
        raise NotImplemented("Abort not implemented.")
        self.registered = False

    abort = tpc_abort

    def sortKey(self):
        return id(self)

def getTransactionManager(obj):
    return TransactionManager(obj)
