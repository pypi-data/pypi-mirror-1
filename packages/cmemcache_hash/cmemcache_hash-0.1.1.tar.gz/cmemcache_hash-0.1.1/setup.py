#!/usr/bin/env python
"""``cmemcache_hash`` enables ``python-memcached`` to use the very same hashing
algorithm that the ``cmemcache`` module uses.

This is useful when you're mixing ``cmemcache`` and ``python-memcached`` or
other libraries that use the ``cmemcache``-style hashing algorithm, like
PostgreSQL's ``pgmemcache`` module.

Setup
-----

Simply install the module and import it, and it is enabled::

    import cmemcache_hash

If you feel like deactivating, use::

    cmemcache_hash.deactivate()

Or reactivating it::

    cmemcache_hash.activate()

License
-------

The BSD three-clause license. See attached `LICENSE` file.
"""

from distutils.core import setup

setup(name="cmemcache_hash", version="0.1.1",
    url="http://lericson.blogg.se/code/category/cmemcache_hash.html",
    author="Ludvig Ericson", author_email="ludvig@blogg.se",
    description="cmemcache-style CRC32 hashing for python-memcached.",
    long_description=__doc__,
    py_modules=["cmemcache_hash"])
