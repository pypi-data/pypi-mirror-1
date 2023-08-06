Changes
=======

0.2
~~~

New Response API
----------------

All API methods now return a `fom.db.FluidResponse` object instead of the
`(status, response)` tuple. This object is backwards compaible in that it will
iterate into a tuple. It can be used to access the status, value, and other
things relating to the response from FluidDB.

Thus code that was::

    >>> status, response = fluid.users[u'aliafshar'].get()
    >>>> print status, response

Is now::

    >>> r = fluid.users[u'aliafshar'].get()
    >>> print r.status, r.response

The backwards compatibility layer offers the following transformation, which
is deprecated::

    >>> status, response = r = fluid.users[u'aliafshar'].get()


Login API
---------

Login method is now available on the Fluid object, so code that was::

    >>> fluid.db.client.login(...

Is now::

    >>> fluid.login(...

The client attribute is linked correctly, for backwards compatibility, so old
code will still work, but this is deprecated, and should not be used in new
code.


FluidDB Error Responses
-----------------------

Non-200 responses from FluidDB are translated into Exceptions in Fom. The are
individually typed for each Exception type, so that they can be caught
individually, or globally by their superclass::

    >>> from fom.session import Fluid
    >>> fdb = Fluid()
    >>> fdb.users['idontexist'].get()
    Traceback (most recent call last):
        ...
    fom.errors.Fluid404Error: <TNoSuchUser (404 Not Found)>

0.1
~~~

This was probbly never released.
