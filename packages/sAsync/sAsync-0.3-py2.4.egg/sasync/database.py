# sAsync:
# An enhancement to the SQLAlchemy package that provides persistent
# dictionaries, text indexing and searching, and an access broker for
# conveniently managing database access, table setup, and
# transactions. Everything is run in an asynchronous fashion using the Twisted
# framework and its deferred processing capabilities.
#
# Copyright (C) 2006 by Edwin A. Suominen, http://www.eepatents.com
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
Asynchronous database transactions via SQLAlchemy.
"""

import time, traceback
from twisted.internet import defer
from twisted.python import failure
import sqlalchemy as SA

import taskqueue


class DatabaseError(Exception):
    """
    A problem occured when trying to access the database.
    """


def transact(f):
    """
    Use this function as a decorator to wrap the supplied method I{f} of
    L{AccessBroker} in a transaction that runs C{f(*args, **kw)} in its own
    transaction.

    Immediately returns an instance of L{twisted.internet.defer.Deferred} that
    will eventually have its callback called with the result of the
    transaction. Inspired by and largely copied from Valentino Volonghi's
    C{makeTransactWith} code.

    You can add the following keyword options to your function call:

    @keyword niceness: Scheduling niceness, an integer between -20 and 20,
        with lower numbers having higher scheduling priority as in UNIX C{nice}
        and C{renice}.

    @keyword doNext: Set C{True} to assign highest possible priority, even
        higher than with niceness = -20.                

    @keyword doLast: Set C{True} to assign lower possible priority, even
        lower than with niceness = 20.

    @keyword session: Set this option to C{True} to use a session for the
        transaction, flushing it at the end.

    @type session: Boolean option, default C{False}

    @keyword ignore: Set this option to C{True} to have errors in the
        transaction function ignored and just do the rollback quietly.

    @type ignore: Boolean option, default C{False}
    
    """
    def substituteFunction(self, *args, **kw):
        """
        Puts the original function in the synchronous task queue and returns a
        deferred to its result when it is eventually run.

        This function will be given the same name as the original function so
        that it can be asked to masquerade as the original function. As a
        result, the threaded call to the original function that it makes inside
        its C{transaction} sub-function will be able to use the arguments for
        that original function. (The caller will actually be calling this
        substitute function, but it won't know that.)

        The original function should be a method of a L{AccessBroker} subclass
        instance, and the queue for that instance will be used to run it.
        """
        ignore = kw.pop('ignore', False)
        def transaction(func, session):
            """
            Everything making up a transaction, and everything run in the
            thread, is contained within this little function, including of
            course a call to C{func}.
            """
            usingSession = isinstance(session, SA.engine.base.Transaction)
            if not usingSession:
                trans = self.q.connection.begin()
            try:
                result = func(self, *args, **kw)
            except:
                if not usingSession:
                    trans.rollback()
                if not ignore:
                    raise DatabaseError(
                        "Error trying transaction with function '%s':\n%s" \
                        % (repr(func), traceback.format_exc()))
            else:
                if usingSession:
                    session.flush()
                else:
                    trans.commit()
                return result
            return failure.Failure()

        def doTransaction(sessionObject):
            """
            Queues up the transaction and immediately returns a deferred to
            its eventual result.
            """
            return self.q.call(
                transaction, f, sessionObject,
                niceness=kw.pop('niceness', 0),
                doNext=kw.pop('doNext', False),
                doLast=kw.pop('doLast', False)
                )

        def started(null):
            self.ranStart = True
            del self._transactionStartupDeferred

        useSession = kw.pop('session', False)
        if hasattr(self.q, 'connection') and getattr(self, 'ranStart', False):
            # We already have a connection, let's get right to the transaction
            if useSession:
                d = self.session().addCallback(doTransaction)
            else:
                d = doTransaction(None)
        elif hasattr(self, '_transactionStartupDeferred') and \
             not self._transactionStartupDeferred.called:
            # Startup is in progress, make a new Deferred to the start of the
            # transaction and chain it to the startup Deferred.
            d = defer.Deferred()
            if useSession:
                d.addCallback(getSession)
            d.addCallback(doTransaction)
            self._transactionStartupDeferred.chainDeferred(d)
        else:
            # We need to start things up before doing the transaction
            d = self._transactionStartupDeferred = self.startup()
            d.addCallback(started)
            if useSession:
                d.addCallback(getSession)
            d.addCallback(doTransaction)
        # Return whatever Deferred we've got
        return d

    substituteFunction.__name__ = f.__name__
    return substituteFunction


class AccessBroker(object):
    """
    I manage asynchronous access to a database.

    Before you use any instance of me, you must specify the parameters for
    creating an SQLAlchemy database engine. A single argument is used, which
    specifies a connection to a database via an RFC-1738 url. In addition, the
    following keyword options can be employed, which are listed below with
    their default values.

    You can set an engine globally, for all instances of me via the
    L{sasync.engine} package-level function, or via my L{engine} class
    method. Alternatively, you can specify an engine for one particular
    instance by supplying the parameters to the constructor.
          
    SQLAlchemy has excellent documentation, which describes the engine
    parameters in plenty of detail. See
    U{http://www.sqlalchemy.org/docs/dbengine.myt}.
    """
    globalParams = ('', {})
    queues = {}
    
    def __init__(self, *url, **kw):
        """
        Constructs an instance of me, optionally specifying parameters for an
        SQLAlchemy engine object that serves this instance only.
        """
        self.selects = {}
        if url:
            self.engineParams = (url[0], kw)
        else:
            self.engineParams = self.globalParams
        self.running = False

    @classmethod
    def engine(cls, url, **kw):
        """
        Sets default connection parameters for all instances of me.
        """
        cls.globalParams = (url, kw)

    def _getQueue(self):
        """
        Returns a threaded task queue that is dedicated to the connection
        specified by the supplied connection parameters, (re)creating the queue
        if necessary.
        """
        def newQueue():
            queue = taskqueue.ThreadQueue(1)
            self.running = True
            self.queues[key] = queue
            return queue

        if hasattr(self, '_currentQueue'):
            return self._currentQueue
        url, kw = self.engineParams
        key = hash((url,) + tuple(kw.items()))
        if key in self.queues:
            queue = self.queues[key]
            if not queue.isRunning():
                queue = newQueue()
        else:
            queue = newQueue()
        self._currentQueue = queue
        return queue

    q = property(_getQueue, doc="""
    Accessing the 'q' attribute will always return a running queue object that
    is dedicated to this instance's connection parameters
    """)

    def connect(self, *null):
        """
        Generates and returns a singleton connection object.
        """
        def getEngine():
            if hasattr(self.q, 'dEngine'):
                d = defer.Deferred().addCallback(getConnection)
                self.q.dEngine.chainDeferred(d)
            else:
                d = self.q.dEngine = \
                    self.q.call(createEngine, doNext=True)
                d.addCallback(gotEngine)
            return d

        def createEngine():
            url, kw = self.engineParams
            kw['strategy'] = 'threadlocal'
            return SA.create_engine(url, **kw)
        
        def gotEngine(engine):
            del self.q.dEngine
            self.q.engine = engine
            return getConnection()

        def getConnection(*null):
            if hasattr(self.q, 'connection'):
                d = defer.succeed(self.q.connection)
            elif hasattr(self.q, 'dConnect'):
                d = defer.Deferred().addCallback(lambda _: self.q.connection)
                self.q.dConnect.chainDeferred(d)
            else:
                d = self.q.dConnect = \
                    self.q.call(self.q.engine.contextual_connect, doNext=True)
                d.addCallback(gotConnection)
            return d

        def gotConnection(connection):
            del self.q.dConnect
            self.q.connection = connection
            return connection

        # After all these function definitions, the method begins here
        if hasattr(self.q, 'engine'):
            return getConnection()
        else:
            return getEngine()

    def session(self, *null):
        """
        Get a comittable session object
        """
        def getSession(connection):
            return self.q.call(
                SA.create_session, bind_to=connection, doNext=True)

        return self.connect().addCallback(getSession)
    
    def table(self, name, *cols, **kw):
        """
        Instantiates a new table object, creating it in the transaction thread
        as needed.

        """
        def create(null):
            def _table():
                if not hasattr(self.q, 'meta'):
                    self.q.meta = SA.BoundMetaData(self.q.engine)
                kw.setdefault('useexisting', True)
                table = SA.Table(name, self.q.meta, *cols, **kw)
                table.create(checkfirst=True)
                setattr(self, name, table)
            
            return self.q.call(_table, doNext=True)
        
        if hasattr(self, name):
            return defer.succeed(False)
        else:
            return self.connect().addCallback(create)

    def startup(self, *null):
        """
        This method runs before the first transaction to start my synchronous
        task queue. B{Override it} to get whatever pre-transaction stuff you
        have run.

        Alternatively, with legacy support for the old API, your
        pre-transaction code can reside in a L{userStartup} method of your
        subclass.
        """
        userStartup = getattr(self, 'userStartup', None)
        if callable(userStartup):
            return defer.maybeDeferred(userStartup)
        else:
            return defer.succeed(None)
    
    def userStartup(self):
        """
        If this method is defined and L{startup} is not overridden in your
        subclass, however, this method will be run as the first callback in the
        deferred processing chain, after my synchronous task queue is safely
        underway.

        The method should return either an immediate result or a deferred to
        an eventual result.

        B{Deprecated}: Instead of defining this method, your subclass should
        simply override L{startup} with your custom startup stuff.

        """

    def shutdown(self, *null):
        """
        Shuts down my database transaction functionality and threaded task
        queue, returning a deferred that fires when all queued tasks are
        done and the shutdown is complete.
        """
        def finalTask():
            if hasattr(self.q, 'connection'):
                self.q.connection.close()
            self.running = False

        if self.running:
            d = self.q.call(finalTask)
            d.addBoth(lambda _: self.q.shutdown())
        else:
            d = defer.succeed(None)
        return d
    
    def s(self, *args, **kw):
        """
        Polymorphic method for working with C{select} instances within a cached
        selection subcontext.

            - When called with a single argument, I{name}, this method
              indicates if the named select object already exists and sets its
              selection subcontext to I{name}.
            
            - With multiple arguments, the method acts like a call to
              C{sqlalchemy.select(...).compile()}, except that nothing is
              returned. Instead, the resulting select object is stored in the
              current selection subcontext.
            
            - With no arguments, the method returns the select object for the
              current selection subcontext.
              
        """
        if len(args) == 1:
            context = args[0]
            self.context = context
            return self.selects.has_key(context)
        else:
            context = getattr(self, 'context', None)
            if len(args) == 0:
                return self.selects.get(context)
            else:
                self.selects[context] = SA.select(*args, **kw).compile()

    def deferToQueue(self, func, *args, **kw):
        """
        Dispatches I{callable(*args, **kw)} as a task via the like-named method
        of my synchronous queue, returning a deferred to its eventual result.

        Scheduling of the task is impacted by the I{niceness} keyword that can
        be included in I{**kw}. As with UNIX niceness, the value should be an
        integer where 0 is normal scheduling, negative numbers are higher
        priority, and positive numbers are lower priority.
        
        @keyword niceness: Scheduling niceness, an integer between -20 and 20,
            with lower numbers having higher scheduling priority as in UNIX
            C{nice} and C{renice}.
        
        """
        return self.q.call(func, *args, **kw)


__all__ = ['transact', 'AccessBroker', 'SA']

