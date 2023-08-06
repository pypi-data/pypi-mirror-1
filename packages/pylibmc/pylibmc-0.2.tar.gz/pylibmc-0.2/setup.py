"""`pylibmc` is a Python wrapper around the C Python extension `handmc`, which
is a wrapper around `libmemcached` from TangentOrg.

Basic usage example::

    >>> import pylibmc
    >>> mc = pylibmc.Client(["127.0.0.1:11211"])
    >>> mc.set("foo", "Hello world!")
    True
    >>> mc.get("foo")
    'Hello world!'

The API is pretty much `python-memcached`. Some parts of `libmemcached` aren't
exposed yet, one example is behaviors.
"""

from distutils.core import setup, Extension

handmc_ext = Extension("handmc", ["handmcmodule.c"], libraries=["memcached"])

setup(name="pylibmc", version="0.2",
      url="http://lericson.blogg.se/code/category/pylibmc.html",
      author="Ludvig Ericson", author_email="ludvig.ericson@gmail.com",
      description="libmemcached wrapper", long_description=__doc__,
      ext_modules=[handmc_ext], py_modules=["pylibmc"])
