# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

import os, thread

from bsddb import db as bdb

BTREE = bdb.DB_BTREE
HASH = bdb.DB_HASH

class TransactionExpired(Exception): pass

# A transaction decorator for BDB (from rdflib)
def transaction(f, name=None, **kwds):
    def wrapped(*args, **kwargs):
        index_db = args[0].db
        retries = 10
        delay = 1
        e = None
        
        #t = kwargs['env'].txn_begin()
        while retries > 0:
            (kwargs['txn'], state) = index_db.atomic_begin()

            try:
                result = f(*args, **kwargs)
                index_db.atomic_commit()
                # returns here when the transaction was successful
                return result
            except MemoryError, e:
                # Locks are leaking in this code or in BDB
                # print "out of locks: ", e, sys.exc_info()[0], self.db_env.lock_stat()['nlocks']
                index_db.atomic_rollback()
                retries = 0
            except bdb.DBLockDeadlockError, e:
                # print "Deadlock when adding data: ", e
                index_db.atomic_rollback()
                sleep(0.1*delay)
                #delay = delay << 1
                retries -= 1
            # this is raised when the generator is supposed to finish, 
            # and should be re-raised to indicate that the generator is done
            # its also called on garbage collection (ensured by the decorated
            # methods)
            except StopIteration, e:
                raise StopIteration
                
            # if it is a generic exception, assume it comes from the user and
            # not from BerkeleyDB, abort transaction and forward to the caller.
            except Exception, e:
#                import traceback
#                traceback.print_exc()
                index_db.atomic_rollback()
                raise
                                
        #print "Retries failed!", bdb.db_env.lock_stat()['nlocks']
        raise TransactionExpired("Add failed after exception:" % str(e))

#        except Exception, e:
#            print "Got exception: ", e            
#            bdb.rollback()
            
            #t.abort()

    wrapped.__doc__ = f.__doc__
    return wrapped

class Index(object):
    def __init__(self, name, db, index_type=BTREE):
        self.__name = name
        self.db = db
        self.__db_env = db.db_env
        self.__index_type = index_type
        
        self.__index = bdb.DB(self.__db_env)
        self.__index.open(self.__name, None, self.__index_type, bdb.DB_CREATE | bdb.DB_AUTO_COMMIT)

    def __setitem__(self, key, value):
        @transaction
        def setitem(self, key, value, txn=None):
            self.__index.put(key, value, txn=txn)

        try:
            setitem(self, key, value)
        except Exception, e:
            raise e

    def __getitem__(self, key):
        @transaction
        def getitem(self, key, txn=None):
            val = self.__index.get(key, txn=txn)
            if val == None:
                raise KeyError(key)
                
            return val

        try:
            return getitem(self, key)
        except Exception, e:
            # print "Got exception in _add: ", e
            raise e

    def __delitem__(self, key):
        """Removes the key from the hash table."""
        
        @transaction
        def delitem(self, key, txn=None):
            self.__index.delete(key, txn=txn)
            
        try:
            return delitem(self, key)
        except Exception, e:
            raise e

# TODO: contains

    def __iter__(self):
        @transaction
        def _iter(self, txn):
            cursor = self.__index.cursor(txn=txn)
            current = cursor.first() # set_range(prefix)

            while current:
                try:
                    key, value = current

                    if key:                
                        yield (key, value)
                        current = cursor.next()
                        #print "next: ", current
                    else:
                        current = None
                # this exception is raised when the user does generator.close()
                except GeneratorExit, e:
                    cursor.close()
                    raise StopIteration
                except Exception, e:
                    #print e
                    cursor.close()
                
            
            cursor.close()
            raise StopIteration

        try:
            return _iter(self)
        except Exception, e:
            # print "Got exception in _add: ", e
            raise
        
    def range_query(self, prefix):
        """
        Executes a range query only returning the values starting with prefix.
        The caller can stop the generator at any time by calling close() on
        the instance (see PEP-0342 for details).
        """
        @transaction
        def _range_query(self, prefix, txn):
            cursor = self.__index.cursor(txn=txn)
            current = cursor.set_range(prefix)

            while current:
                try:
                    key, value = current

                    if key and key.startswith(prefix):                
                        yield (key, value)
                        current = cursor.next()
                        #print "next: ", current
                    else:
                        current = None
                # this exception is raised when the user does generator.close()
                except GeneratorExit, e:
                    cursor.close()
                    raise StopIteration
                except Exception, e:
                    #print e
                    cursor.close()
                
            
            cursor.close()
            raise StopIteration

        try:
            return _range_query(self, prefix)
        except Exception, e:
            # print "Got exception in _add: ", e
            raise

    def close(self):
        try:
            self.__index.close()
        except bdb.DBRunRecoveryError, e:
            # this can occur when a second process using the index crashes 
            # without closing it correctly, ignore this since recovery
            # is run on start-up
            pass
        
class DB(object):
    """
    A wrapper class for Berkeley DB transaction environments and databases.
    Hides complexity of transaction management and threads.
    """
    
    def __init__(self, db_path, cachesize=2**26):
        self.__db_path = os.path.abspath(db_path)

        # create the directory if the environment does not exist already        
        if not os.path.exists(self.__db_path):
            os.mkdir(self.__db_path)

        # initialize the environment
        self.db_env = bdb.DBEnv()
        self.db_env.set_cachesize(0, cachesize)

        # enable BDB deadlock-detection
        self.db_env.set_lk_detect(bdb.DB_LOCK_MAXLOCKS)
        
        flags = bdb.DB_CREATE | bdb.DB_INIT_MPOOL | bdb.DB_INIT_LOCK | bdb.DB_THREAD | bdb.DB_INIT_LOG | bdb.DB_INIT_TXN | bdb.DB_RECOVER
        self.db_env.open(db_path, flags)
        
        self.__txns = {}

    def atomic_begin(self):
        """
        All db calls made within an atomic block is executed with the same 
        transaction. Nested calls to atomic_begin returns the active 
        transaction.
        """
        
        active = False
        try:
            self.__txns[thread.get_ident()]
            active = True
        except KeyError:
            self.__txns[thread.get_ident()] = self.db_env.txn_begin()
        
        return (self.__txns[thread.get_ident()], active)

    def atomic_rollback(self):
        try:
            txn = self.__txns[thread.get_ident()]
            txn.abort()
            del self.__txns[thread.get_ident()]
            active = False
        except KeyError:
            active = False
        except:
            #txn.abort()
            raise
            
    def atomic_commit(self):
        # ends a currently active atomic block
        try:
            txn = self.__txns[thread.get_ident()]
            txn.commit(0)
            del self.__txns[thread.get_ident()]
            active = False
        except KeyError:
            active = False
        except:
            txn.abort()

    def close(self):
        try:
            self.db_env.close()
        except bdb.DBRunRecoveryError, e:
            # this can occur when a second process using the index crashes 
            # without closing it correctly, ignore this since recovery
            # is run on start-up
            pass            
                    
