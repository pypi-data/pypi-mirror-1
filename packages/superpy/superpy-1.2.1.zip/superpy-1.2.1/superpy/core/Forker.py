"""This is a script to 'fork' into a separate process to run tasks.

Usage:

  <prog_name> <peer_host_name> <peer_port_number> [<logFileName>]

where <prog_name> is the name of this script and
(<peer_host_name>,<port_number>) is a pair indicating an Internet
address representing a peer that will control this process. The
first action of this process is to make an XML-RPC call to that
address to call the HandShake method. After that, this process
will listen for XML-RPC requests from that peer.
"""


import sys, logging, time, tempfile

import Process

def Usage():
    "Print usage information."
    return __doc__

def MakeCommandLine(exe,scriptName,hostName,portNumber,logFile=None):
    "Make command line to call program."

    cmdLine = [exe,scriptName,str(hostName),str(portNumber)]
    if (logFile):
        cmdLine += [logFile]
    return cmdLine

def ProcessCommandLine(argv):
    "Split command line into dictionary of keyword arguments."
    if (len(argv) == 3):
        return {'progName' : argv[0], 'host' : argv[1], 'port' : int(argv[2])}
    elif (len(argv) == 4):
        return {'progName' : argv[0], 'host' : argv[1], 'port' : int(argv[2]),
                'logFile' : argv[3]}
    else:
        raise Exception("Invalid arguments (got: %s).\n%s\n" % (
            str(argv), Usage()))
    


def StartServer(progName,host,port,logFile=None,outFile=None):
    """Start the server on the given port.
    
    INPUTS:
    
    -- progName:        Name for the running program.

    -- host:        Name of host to contact.
    
    -- port:        Integer port for host to contact.

    -- logFile:     Optional log file to send logging messages to
    
    -------------------------------------------------------
    
    PURPOSE:    Listen for XML-RPC requests on the given port.
    
    """
    if (logFile is not None):
        logging.basicConfig(filename=logFile,level=logging.DEBUG)
    logging.debug('Starting server as program name %s.' % progName)
    if (outFile is None):
        outFile = tempfile.NamedTemporaryFile(suffix='_Forker_log.txt')
        logging.info('Redirecting output to temp file %s' % outFile.name)
        sys.stdout = outFile.file
        sys.stderr = outFile.file
    else:
        logging.info('Redirecting output to %s' % str(outFile))
        sys.stdout = outFile
        sys.stderr = outFile
    try:
        server = Process.RemoteProcess()
        time.sleep(0)
        server.RequestMaster(host,port)
        server.Run()
    except Exception, e:
        logging.error('Got Exception in Forker.py: %s' % str(e))
    
if __name__ == '__main__':
    args = ProcessCommandLine(sys.argv)
    StartServer(**args)
