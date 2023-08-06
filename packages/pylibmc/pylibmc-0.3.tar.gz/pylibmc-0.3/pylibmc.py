"""`python-memcached`-compatible wrapper around `handmc`.

>>> mc = Client(["127.0.0.1"])
"""

import handmc

class Client(handmc.client):
    def __init__(self, servers, *args, **kwds):
        addr_tups = []
        for server in servers:
            addr = server
            port = 11211
            if server.startswith("udp:"):
                stype = handmc.server_type_udp
                addr = addr[4:]
                if ":" in server:
                    (addr, port) = addr.split(":", 1)
                    port = int(port)
            elif ":" in server:
                stype = handmc.server_type_tcp
                (addr, port) = server.split(":", 1)
                port = int(port)
            elif "/" in server:
                stype = handmc.server_type_unix
                port = 0
            else:
                stype = handmc.server_type_tcp
            addr_tups.append((stype, addr, port))
        super(Client, self).__init__(addr_tups)
