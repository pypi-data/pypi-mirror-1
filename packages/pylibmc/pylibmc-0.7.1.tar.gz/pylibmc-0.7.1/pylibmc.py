"""`python-memcached`-compatible wrapper around `_pylibmc`.

The interface is pretty much exactly the same as python-memcached, with some
minor differences. If you should happen to spot any, file a bug!

>>> mc = Client(["127.0.0.1"])
>>> b = mc.behaviors
>>> b.keys()
['hash', 'connect timeout', 'cache lookups', 'buffer requests', 'verify key', 'support cas', 'poll timeout', 'no block', 'tcp nodelay', 'distribution', 'sort hosts']
>>> b["hash"]
'default'
>>> b["hash"] = 'fnv1a_32'
>>> mc.behaviors["hash"]
'fnv1a_32'
"""

import _pylibmc

__all__ = ["hashers", "distributions", "Client"]

hashers = {}
distributions = {}
# Not the prettiest way of doing things, but works well.
for name in dir(_pylibmc):
    if name.startswith("hash_"):
        hashers[name[5:]] = getattr(_pylibmc, name)
    elif name.startswith("distribution_"):
        distributions[name[13:].replace("_", " ")] = getattr(_pylibmc, name)

hashers_rvs = dict((v, k) for (k, v) in hashers.iteritems())
distributions_rvs = dict((v, k) for (k, v) in distributions.iteritems())

class BehaviorDict(dict):
    def __init__(self, client, *args, **kwds):
        super(BehaviorDict, self).__init__(*args, **kwds)
        self.client = client

    def __setitem__(self, name, value):
        super(BehaviorDict, self).__setitem__(name, value)
        self.client.behaviors = self

    def update(self, *args, **kwds):
        super(BehaviorDict, self).update(*args, **kwds)
        self.client.behaviors = self

class Client(_pylibmc.client):
    def __init__(self, servers, *args, **kwds):
        """Initialize a memcached client instance.

        This connects to the servers in *servers*, which will default to being
        TCP servers. If it looks like a filesystem path, a UNIX socket. If
        prefixed with `udp:`, a UDP connection.
        """
        addr_tups = []
        for server in servers:
            addr = server
            port = 11211
            if server.startswith("udp:"):
                stype = _pylibmc.server_type_udp
                addr = addr[4:]
                if ":" in server:
                    (addr, port) = addr.split(":", 1)
                    port = int(port)
            elif ":" in server:
                stype = _pylibmc.server_type_tcp
                (addr, port) = server.split(":", 1)
                port = int(port)
            elif "/" in server:
                stype = _pylibmc.server_type_unix
                port = 0
            else:
                stype = _pylibmc.server_type_tcp
            addr_tups.append((stype, addr, port))
        super(Client, self).__init__(addr_tups)

    def get_behaviors(self):
        """Gets the behaviors from the underlying C client instance.

        Reverses the integer constants for `hash` and `distribution` into more
        understandable string values. See *set_behaviors* for info.
        """
        behaviors = super(Client, self).get_behaviors()
        behaviors["hash"] = hashers_rvs[behaviors["hash"]]
        behaviors["distribution"] = distributions_rvs[behaviors["distribution"]]
        return BehaviorDict(self, behaviors)

    def set_behaviors(self, behaviors):
        """Sets the behaviors on the underlying C client instance.

        Takes care of morphing the `hash` key, if specified, into the
        corresponding integer constant (which the C client expects.) If,
        however, an unknown value is specified, it's passed on to the C client
        (where it most surely will error out.)

        This also happens for `distribution`.
        """
        behaviors = behaviors.copy()
        if behaviors.get("hash", None) in hashers:
            behaviors["hash"] = hashers[behaviors["hash"]]
        if behaviors.get("distribution") in distributions:
            behaviors["distribution"] = distributions[behaviors["distribution"]]
        return super(Client, self).set_behaviors(behaviors)

    behaviors = property(get_behaviors, set_behaviors)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
