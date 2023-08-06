"""Script to spawn server on current machine.
"""


import logging, sys

from superpy.core import Servers

def SpawnServer(targetPort=None, daemon=False, **kw):
    """Spawn a new server on this machine.
    
    INPUTS:
    
    -- targetPort=None:        Target port to listen on. If 0, this is
                               dynamically determined. If None, the default
                               superpy port is used.
    
    -- pythonPath=None:        Optional string to use for PYTHONPATH.

    """
    server = Servers.BasicRPCServer(port = targetPort, **kw)
    
    logging.info('sys.path is: ' + '\n'.join(sys.path))
    logging.info('port is %i' % server.socket.getsockname()[1])

    if (daemon): server.serve_forever_as_thread(daemon=True)
    else: server.serve_forever()
    
    return server


if __name__ == '__main__':
    
    # allow caller to pass one port
    args = sys.argv[1:]
    port = int(args[0]) if len(args) > 0 else None

    SpawnServer(port)
