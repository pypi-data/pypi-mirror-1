Introduction
============

`unimr.memcachedlock` implements a distributed "soft" locking
mechanism using memcached. It provides factory functions and
decorators for a primitive locking, a reentrant locking and a special
locking for zeo-clients.

The native locking methods of python's threading module supports
thread safe locking and therefore, provides only full locking support
for single zope installations. However, zeo-clients have no locking
mechanism beetween each other for concurrent write operations on
identical objects (e.g. Catalog) and are unnecessarily stressed to
resolve ConflictErrors on heavy load. The reason for this problem is
the optimistic concurrency control of the ZODB which primarly prepares
the changes of an object (in many cases expensive calculations) and
thereafter checks the validity of the object for the write
process. The higher the number of writes on the same object
the higher the risk that a concurrent zeo-client has already
invalidated the object while another zeo-client has still this object
in use. The client with the invalidated object is constrained to roll
back its changes and to recalculate the changes based on the refreshed
object. At worst, this state goes in circles and results in a
ConflictError. The optimistic concurrency control therefore perfectly
fits only concurrent write operations on distinct objects.

Memcache locking overcomes this problem because it extends the regular
concurrency mechanism by a shared locking beetween all involved
zeo-clients by serializing the concurrent write operations before a
ConflictError is provoked. This mechanism is also known as
`pessimistic concurrency control`.


Risks 
===== 

There is no risk of loosing data within a zope environment because
memcachedlock will always fall back to zope's transaction control.


Usage
=====

`unimr.memcachedlock` easily serializes concurrent writes

>>> from unimr.memcachedlock import memcachedlock
...
... # define an invariant unique key of an instance
... def get_key(fun,*args,**kargs):
...    fun, instance = args[0:2]
...    return '/'.join(instance.getPhysicalPath())


>>> # lock decorator
... @memcachedlock.lock(get_key)
... def concurrent_write(self, *args, **kw):
...    """  method which produces many conflict errors (bottle neck)"""
...    # ...


or for recursive function calls


>>> # rlock decorator
... @memcachedlock.rlock(get_key)
... def concurrent_write(self, *args, **kw):
...    """  method which produces many conflict errors (bottle neck)"""
...    # ...


or for function calls of zeo-clients providing a special ConflictError
handling to interact properly with the optimistic concurrency control


>>> # zlock decorator
... @memcachedlock.zlock(get_key)
... def concurrent_write(self, *args, **kw):
...    """  method which produces many conflict errors (bottle neck)"""
...    # ...


The decorators ``@memcachedlock.lock``, ``@memcachedlock.rlock`` or
``@memcachedlock.zlock`` take exactly one argument

   get_key
       function which returns an invariant unique key of an instance
       known by all zeo-clients (required)


and two optional keywords:

   
   timeout
       livetime in seconds of the lock (default: 30)
   
   interval
       retrial interval of the lock check in seconds (default: 0.05)


Catalog Patch
=============

`unimr.memcachedlock` already includes a patch for zope's Catalog to
enable locking for the catalog_object method. Uncomment corresponding
lines in configure.zcml of this package.


Configuring memcached servers
=============================

You can configure one ore mor memcached servers by adding the
environment variable MEMCACHEDLOCK_SERVERS to the
buildout.cfg as follows (default server: 127.0.0.1:11211):


::


   [instance]
   ...
   zope-conf-additional = 
     <environment>
        MEMCACHEDLOCK_SERVERS <ip/hostname of host1>:<port>,<ip/hostname of host2>:<port>
     </environment> 


Todo
====

  - Tests ...
  - Pessimistic concurrency control implementation by means of native zeo server protocol.
