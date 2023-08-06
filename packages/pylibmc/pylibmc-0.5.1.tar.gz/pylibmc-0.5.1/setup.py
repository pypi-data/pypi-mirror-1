"""`pylibmc` is a Python wrapper around the accompanying C Python extension
`_pylibmc`, which is a wrapper around `libmemcached` from TangentOrg.

You have to install `libmemcached` separately, and have your compiler and
linker find the include files and libraries.

With `libmemcached` installed and this package set up, the following basic
usage example should work::

    >>> import pylibmc
    >>> mc = pylibmc.Client(["127.0.0.1:11211"])
    >>> mc.set("foo", "Hello world!")
    True
    >>> mc.get("foo")
    'Hello world!'

The API is pretty much `python-memcached`. Some parts of `libmemcached` aren't
exposed yet. I think.

Behaviors
=========

`libmemcached` has ways of telling it how to behave. You'll have to refer to
its documentation on what the different behaviors do.

To change behaviors, quite simply::

    >>> mc.behaviors["hash"] = "fnv1a_32"

Change Log
==========

New in version 0.5
------------------

Fixed some memory leaks, and added support for `libmemcached` 0.23.

New in version 0.4
------------------

Renamed the C module to `_pylibmc`, and added lots of `libmemcached` constants
to it, as well as implemented behaviors.
"""

from distutils.core import setup, Extension

pylibmc_ext = Extension("_pylibmc", ["_pylibmcmodule.c"],
                        libraries=["memcached"])

setup(name="pylibmc", version="0.5.1",
      url="http://lericson.blogg.se/code/category/pylibmc.html",
      author="Ludvig Ericson", author_email="ludvig.ericson@gmail.com",
      description="libmemcached wrapper", long_description=__doc__,
      ext_modules=[pylibmc_ext], py_modules=["pylibmc"])
