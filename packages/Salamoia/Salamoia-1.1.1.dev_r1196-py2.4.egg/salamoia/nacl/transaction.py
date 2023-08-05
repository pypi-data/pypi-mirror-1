from salamoia.h2o.transaction import *
from salamoia.h2o.logioni import *
from salamoia.h2o.exception import *

class Transaction(object):
    def __init__(self):
        self.objects = {}
        self.modes = {}

    def __repr__(self):
        return "Transaction(%s)" % (str(self.objects.keys()))

    @classmethod
    def new(cls):
        obj = cls()
        return (id(obj), obj)

class TransactionControl(object):
    def __init__(self):
        Ione.log("TransactionControl init")
        super(TransactionControl, self).__init__()

        self.transactions = {}

    def beginTransaction(self):
        id, obj = Transaction.new()
        self.transactions[id] = obj
        print "created transaction with id", id
        print "transactions present:", self.transactions
        return TransactionProxy(id)

    def _deleteTransaction(self, proxy):
        del self.transactions[proxy.id]
        print "transactions present:", self.transactions
        
    def commitTransaction(self, proxy):
        """
        performs all stores in the transaction atomically
        
        TODO: if an operation fails it should revert to the last stable state
        """
        
        print "committing transaction", proxy

        if proxy.id not in self.transactions:
            raise TransactionDoesNotExist

        transaction = self.transactions[proxy.id]
        try:
            for id in transaction.objects.keys():
                obj = transaction.objects[id]
                mode = transaction.modes[id]
                super(TransactionControl, self).store(obj, mode)
        finally:
            pass

        self._deleteTransaction(proxy)
        return 0

    def abortTransaction(self, proxy):
        print "aborting transaction", proxy

        if proxy.id not in self.transactions:
            raise TransactionDoesNotExist

        self._deleteTransaction(proxy)
        return 0

    def transactionFetch(self, proxy, id):
        Ione.log("transaction fetch", proxy, id)
        if id in self.transactions[proxy.id].objects:
            return self.transactions[proxy.id].objects[id]
        
        return super(TransactionControl, self).baseFetch(id)

    def transactionStore(self, proxy, object, mode="auto"):
        Ione.log("store in transaction", proxy,  object.id)
        self.transactions[proxy.id].objects[object.id] = object
        self.transactions[proxy.id].modes[object.id] = mode

        print "transactions present:", self.transactions
        return 0

    ## hooks

    def store(self, object, mode="auto"):
        Ione.log("transaction store", object.id)
        return super(TransactionControl, self).store(object, mode)
