"""Provides xml-rpc servers and server proxies that pickle parameters.

The xmlrpclib and SimpleXMLRPCServer are great built-in python modules,
but they have a few minor drawbacks:

  1. They don't allow you to send python objects over xml-rpc.
  2. They don't report very useful information to the client when
     there is an exception on the server.

This module provides the PicklingServerProxy and PicklingXMLRPCServer classes
to solve these problems. Basically, you can just use PicklingServerProxy
as a drop-in replacement for xmlrpclib.Server/ServerProxy and use
PicklingXMLRPCServer as a drop-in replacement for SimpleXMLRPCServer. See
documentation for those classes for details.
"""

import xmlrpclib, cPickle, sys, logging, traceback
from SimpleXMLRPCServer import SimpleXMLRPCServer

class RemoteException(Exception):
    """Exception that occured on remote server.
    """

class _PicklingMethod(xmlrpclib._Method):
    """Modifies xmlrpclib._Method to pickle params and report remote exceptions.
    """
    def __call__(self,*args,**kw):
        if (len(kw)):
            raise Exception('''
            Cannot use keyword arguments for XML server proxies.\nGot kw=%s.\n
            ''' % kw)
        args = [cPickle.dumps(a) for a in args]
        #Uncomment below for debug logging. This can print lots of junk...
        #logging.debug('Pickled args=\n    %s\n' % '\n    '.join(args))
        result = xmlrpclib._Method.__call__(self,*args)
        result = cPickle.loads(result)
        if (isinstance(result,RemoteException)): raise result
        else: return result

class PicklingServerProxy(xmlrpclib.ServerProxy):
    """Overrides xmlrpclib.Server/ServerProxy to pickle params.

    You can use this as a drop-in replacement to xmlrpclib.ServerProxy
    to automatically pickle arguments you send to a PicklingXMLRPCServer.
    """
    def __getattr__(self, name):
        "Override xmlrpclib.__getattr__ to do pickling/unpickling."
        return _PicklingMethod(self._ServerProxy__request, name)

class PicklingXMLRPCServer(SimpleXMLRPCServer):
    """Overrides SimpleXMLRPCServer.SimpleXMLRPCServer to handle pickling.

    You can use this as a drop-in replacement to SimpleXMLRPCServer.
    It will automatically unpickle the incoming arguments. This is most
    useful in conjuction with PicklingServerProxy
    """

    def _dispatch(self, method, params):
        try:
            unpickledParams = [cPickle.loads(p) for p in params]
            result = SimpleXMLRPCServer._dispatch(
                self,method,unpickledParams)
        except Exception, e:
            (exc_info,exc_type) = (sys.exc_info(),sys.exc_type)
            logging.debug('In except block...')
            strParams = str(params)
            if (len(strParams) > 2048):
                strParams = strParams[0:(2048-1-3)] + '...'
            errTrace = ('Exception of type \'' + `exc_type` + '\':  \'' + 
                        e.__str__() + '\'.\n\n\n' +
                        ''.join(traceback.format_tb(exc_info[2])) +
                        `exc_info` + ('\nmethod=%s\nparams=%s\nsys.path=%s' % (
                str(method), strParams, sys.path)))
            logging.debug('''Got exception in PicklingXMLRPC:
            \n%s\n
            method=%s\nparams=%s\n''' % (errTrace, str(method), strParams))
            result = RemoteException(errTrace)
        return cPickle.dumps(result)


    
