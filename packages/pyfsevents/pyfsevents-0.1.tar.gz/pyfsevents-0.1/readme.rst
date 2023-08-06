.. contents::

Introduction
============
pyfsevents is a C extension providing a Python interface for Mac OS X 10.5 and
later which allows monitoring for file system events, using FSEvents.

pyfsevents uses a callback mechanism: see `Module Documentation`_.

Installation
============
``python setup.py install``

License
=======
Distributed under the terms of the MIT License.

Requirements
============
Mac OS X >= 10.5 Leopard

Limitations
===========
Thread-unsafe: CFRunLoop's and Python threads do not quite interact well
when put together :)

Module Documentation
====================
pyfsevents uses a callback mechanism.

It provides two functions:

* ``registerfd(fd, callback[, mask])``
* ``registerpath(path, callback)``

to register objects to monitor.

After registration, ``listen()`` should be called to wait for events.
The call is blocking: callbacks are fired on events.

``stop()`` is available to stop the ``listen()`` call. ``stop()`` should be called
from a different thread.

Please see *examples/* for use cases of the extension.

callback signatures
-------------------
The ``callback`` arguments passed to ``register*`` functions will be fired on
events. These callback functions should be functions callable with two
arguments, as ``listen`` will call these functions with two arguments:

- For File descriptors, ``registerfd`` callbacks will be passed (fd, mask) arguments:

    *fd*
        file descriptor which changed and fired the callback.
    
    *mask*
        the POLLIN / POLLOUT mask, similar to the `select.poll <http://docs.python.org/library/select.html#select.poll.register>`_ module.

- For FSEvents, ``registerpath`` callbacks will be passed (path, recursive) arguments:

    *path*
        the path where the event occurred.
    
    *recursive*
        a boolean: if True, the caller should check recursively the directory tree for changes, and not only the specified directory.
