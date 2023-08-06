"""Script to show what is happening with server on current machine.
"""

import logging, socket, time

import Servers, PicklingXMLRPC

def Show(host=None,port=None):
    """Show all tasks running on given host and port.

    If host and port are None, we use localhost and default superpy server port.
    """

    if (host == None): host = socket.gethostname()
    if (port == None): port = Servers.BasicRPCServer.defaultPort
    logging.debug('Making connection to %s' % ([host,port]))
    connection = PicklingXMLRPC.PicklingServerProxy(
        'http://%s:%i' % (host,port))
    result = connection.ShowQueue()
    print 'Result = ' + '\n'.join(map(str,result))

if __name__ == '__main__':
    logging.getLogger('').setLevel(0)
    Show()
    pause = 3600
    print 'Pausing for %i seconds' % pause
    time.sleep(pause)
