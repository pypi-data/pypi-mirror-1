"""Script to clean out old tasks from server on current machine.
"""

import logging, socket, time

import Servers, PicklingXMLRPC

def Go(host=None,port=None,allowedLag=86400):
    "Run the script."
    if (host == None): host = socket.gethostname()
    if (port == None): port = Servers.BasicRPCServer.defaultPort
    logging.info('Making connection to %s' % ([host,port]))
    connection = PicklingXMLRPC.PicklingServerProxy(
        'http://%s:%i' % (host,port))
    result = connection.CleanOldTasks(allowedLag)
    print 'Cleaned:\n' + '\n'.join(map(str,result))

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.INFO)
    Go()
    pause = 3600
    print 'Pausing for %i seconds' % pause
    time.sleep(pause)
