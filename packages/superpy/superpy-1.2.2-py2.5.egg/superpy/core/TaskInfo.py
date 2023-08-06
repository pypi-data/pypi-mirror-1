"""Module containing various classes to provide information about tasks.
"""

import socket, xmlrpclib, logging, time, datetime, threading, copy
import PicklingXMLRPC

class GenericProcessHandle:
    """Abstract interface that process handles should follow.
    """

    def __init__(self):
        pass

    def Name(self):
        "Return string name"
        raise NotImplementedError

    def Kill(self):
        "Kill the task"
        raise NotImplementedError

    def StatusInfo(self):
        """Return dictionary containing the following status info:

           'starttime' : A datetime representing when task started.
           'endtime'   : A datetime representing when task ended.
           'alive'     : True if task is still running.
           'host'      : String name of host process is running on.
           'port'      : Port to use to communicate with process.
           'mode'      : Short string indicating current status. This
                         may be 'queued', 'running', 'finished'.
           'result'    : Result of process if it is finished.
           'pids'      : List of integer process ids related to task.
        """
        raise NotImplementedError

    def Cleanup(self):
        "Cleanup anything related to process"
        raise NotImplementedError

    def StaleP(self):
        "Return True if handle is stale and UpdatedHandle must be called."
        raise NotImplementedError

    def UpdatedHandle(self,timeout=None,numAttempts=3,serverTimeout=None):
        """Update handle with given timeout and numAttempts.
        
        INPUTS:
        
        -- timeout=None:        Timeout in seconds to wait for handle to
                                update.
        
        -- numAttempts=3:       Maximum number of retries to attempt. 
        
        -- serverTimeout=None:  Timeout in seconds to give to server.      
        
        -------------------------------------------------------
        
        RETURNS:        An updated version of the current handle if possible.
        
        -------------------------------------------------------
        
        PURPOSE:        This method attempts to return an updated version
                        of the current handle by requesting status from
                        the server. There are two possible timeout
                        arguments, timeout and serverTimeout. The former
                        controls how long we wait before raising a
                        socket.timeout exception. The latter controls
                        the timeout argument we give to the server.

                        Generally, serverTimeout should be less than
                        timeout since you want to give the server a
                        chance to timeout and report that timeout back
                        to the client. If serverTimeout is None, we
                        try to set it to something reasonable and less
                        than timeout.
        """
        raise NotImplementedError

    def WaitForUpdatedHandle(self, waitInSeconds=10, pollTime=3, *args, **kw):
        """Wait for a period of time for task to finish.
        
        INPUTS:
        
        -- waitInSeconds=10:   Max time to wait before returning.
        
        -- pollTime=3:         How often to update handle.
        
        -- *args, **kw:        Additional args for self.UpdatedHandle.
        
        -------------------------------------------------------
        
        RETURNS:        The result of UpdatedHandle(*args, **kw).
        
        -------------------------------------------------------
        
        PURPOSE:        This method updates the handle, checks if it is
                        finished, sleeps for pollTime if it is not done,
                        and keeps doing that until waitInSeconds seconds
                        have elapsed or the task for this handle finishes.
                        In any case, the latest updated handle is returned.
        
        """
        handle = self
        startTime = time.time()
        while (time.time() - startTime < waitInSeconds):
            handle = handle.UpdatedHandle(*args, **kw)
            info = handle.StatusInfo()
            if (info['mode'] == 'finished'):
                return handle
            else:
                time.sleep(pollTime)
        return handle
        

    def Pretty(self):
        """Print a pretty version of self suitable for display.
        """
        raise NotImplementedError

class InvalidHandle(GenericProcessHandle):
    """Handle like object for cases when there is no valid handle.
    """

    def __init__(self, name, infoDict):
        GenericProcessHandle.__init__(self)
        self.name = name
        self.infoDict = infoDict

    def Name(self):
        "Return name"
        return self.name

    @staticmethod
    def _ComplainInvalid(func):
        "Helper function to complain that invalid handle does not support func"
        raise Exception('InvalidHandle does not support the %s method.'%func)
        

    def Kill(self):
        "Not implemented for invalid handle"
        self._ComplainInvalid('Kill')

    def Cleanup(self):
        "Not implemented for invalid handle"
        self._ComplainInvalid('Cleanup')

    def StaleP(self):
        "InvalidHandle is never stale so just returns False."
        return False

    def UpdatedHandle(self,timeout=None,numAttempts=3,serverTimeout=None):
        "Just return self since no need to update an invalid handle."
        _ignore = timeout, numAttempts, serverTimeout
        return self

    def WaitForUpdatedHandle(self, waitInSeconds=10, pollTime=3, *args, **kw):
        "Just return self since no need to update an invalid handle."
        _ignore = waitInSeconds, pollTime, args, kw
        return self

    def Pretty(self):
        "Return pretty version of self."
        return 'InvalidHandle:\n    ' + ',\n    '.join([
            '.%s=%s' % (n, repr(getattr(self,n))) for n in [
            'name','infoDict']])

    def StatusInfo(self):
        "Return status info as required by GenericProcessHandle"
        return copy.deepcopy(self.infoDict)

class StaticHandle(GenericProcessHandle):
    """Handle like object for cases when task is already processed.
    """

    def __init__(self, name, infoDict=None):
        """Initializer.
        
        INPUTS:
        
        -- name:       String name for handle. 
        
        -- infoDict=None:        Optional dictionary of status info as
                                 StatusInfo method returns. Any items not
                                 provided are filled in with reasonable
                                 defaults.
        
        """
        GenericProcessHandle.__init__(self)
        self.name = name
        self.infoDict = dict(infoDict)

        now = datetime.datetime.now()
        defaults = {
            'starttime' : now, 'endtime' : now + datetime.timedelta(seconds=1),
            'alive' : False, 'host' : socket.gethostname(), 'port' : 0,
            'mode' : 'finished', 'result' : None, 'pids' : []
            }
        for (k, v) in defaults.items():
            if (k not in self.infoDict):
                self.infoDict[k] = v

    def Name(self):
        "Return name"
        return self.name

    @staticmethod
    def _ComplainInvalid(func):
        "Helper function to complain that static handle does not support func"
        raise Exception('StaticHandle does not support the %s method.'%func)
        

    def Kill(self):
        "Not implemented for static handle"
        self._ComplainInvalid('Kill')

    def Cleanup(self):
        "Just do nothing since nothing to cleanup."
        pass


    def StaleP(self):
        "StaticHandle is never stale so just returns False."
        return False

    def UpdatedHandle(self,timeout=None,numAttempts=3,serverTimeout=None):
        "Just return self since no need to update a static handle."
        _ignore = timeout, numAttempts, serverTimeout
        return self

    def WaitForUpdatedHandle(self, waitInSeconds=10, pollTime=3, *args, **kw):
        "Just return self since no need to update a static handle."
        _ignore = waitInSeconds, pollTime, args, kw
        return self

    def Pretty(self):
        "Return pretty version of self."
        return 'StaticHandle:\n    ' + ',\n    '.join([
            '.%s=%s' % (n, repr(getattr(self,n))) for n in [
            'name','infoDict']])

    def StatusInfo(self):
        "Return status info as required by GenericProcessHandle"
        return copy.deepcopy(self.infoDict)
    
        

class TaskHandle(GenericProcessHandle):
    """Handle representing information about a running task.
    """

    def __init__(self,name,started,finished,alive,host,port,result,
                 starttime,endtime,user='unknown',taskRepr='',pids=None,
                 tokens=None):
        GenericProcessHandle.__init__(self)
        if (tokens is None): tokens = []
        self.name = name
        self.started = started        
        self.finished = finished
        self.alive = alive
        self.host = host
        self.port = port
        self.result = result
        self.starttime = starttime
        self.endtime = endtime
        self.user = user
        self.taskRepr = taskRepr
        self.pids = pids
        self._stale = False
        self._tokens = tokens

        assert isinstance(host,(str,unicode)), (
            "Expected str for host; got %s of %s" % (host,type(host)))
        assert isinstance(port,int), (
            "Expected int for port; got %s of %s" % (port,type(port)))        

    def Name(self):
        "Return name."
        return str(self.name)

    def Pretty(self):
        "Uses __str__ to show pretty version"
        return str(self)

    def UpdatedHandle(self,timeout=None,numAttempts=3,serverTimeout=None):
        """Update handle with given timeout and numAttempts.
        
        INPUTS:
        
        -- timeout=None:        Timeout in seconds to wait for handle to
                                update.
        
        -- numAttempts=3:       Maximum number of retries to attempt. 
        
        -- serverTimeout=None:  Timeout in seconds to give to server.      
        
        -------------------------------------------------------
        
        RETURNS:        An updated version of the current handle if possible.
        
        -------------------------------------------------------
        
        PURPOSE:        This method attempts to return an updated version
                        of the current handle by requesting status from
                        the server. There are two possible timeout
                        arguments, timeout and serverTimeout. The former
                        controls how long we wait before raising a
                        socket.timeout exception. The latter controls
                        the timeout argument we give to the server.

                        Generally, serverTimeout should be less than
                        timeout since you want to give the server a
                        chance to timeout and report that timeout back
                        to the client. If serverTimeout is None, we
                        try to set it to something reasonable and less
                        than timeout.
        """
        result, exc = None, None
        connString = 'http://%s:%i' % (self.host,self.port)
        oldtimeout = socket.getdefaulttimeout()        
        if (timeout is None):
            timeout = 60*10
        if (serverTimeout is None):
            serverTimeout = max(1, timeout-4)

        args = getattr(self,'_tokens',[]) + [self.name,serverTimeout]
        for _attempt in range(numAttempts):
            try:
                socket.setdefaulttimeout(timeout)
                logging.debug('Connecting to %s' % connString)
                connection = PicklingXMLRPC.PicklingServerProxy(connString)
                result = connection.Status(*args)
                break
            except xmlrpclib.ProtocolError, exc:
                logging.warning('Got protocol error %s while getting status'
                                % str(exc))
                raise
            except socket.error, exc:
                logging.warning(
                    'Exception updating status with server %s:\n%s\n'
                    % (connString, str(exc)))
                raise
            finally:
                socket.setdefaulttimeout(oldtimeout)
            time.sleep(1) #Pause for a second before trying again

        for name in self.__dict__.keys():
            if ('_' != name[0]):
                setattr(self,name,property(
                    self._Invalid,self._Invalid,
                    doc="Object is stale; last valid value for %s was %s"
                    % (name,str(getattr(self,name)))))
        self._stale = True
        return result

    def Kill(self):
        "Kill task"
        connString = 'http://%s:%i' % (self.host,self.port)
        logging.debug('Connecting to %s' % connString)
        connection = PicklingXMLRPC.PicklingServerProxy(connString)
        result = connection.RemoveFromQueue(
            *(getattr(self,'_tokens',[]) + [self]))
        return result


    def StaleP(self):
        "Return True if handle is stale."
        return self._stale

    @staticmethod
    def _Invalid(*args,**kw):
        "raise an exception since the handle is invalid"
        raise Exception("This object has become stale.")

    def __str__(self):
        if (self._stale): self._Invalid()
        result = self.__class__.__name__ + '(\n' + ',\n'.join(
            ['    %s=%s'%(item,repr(getattr(self,item,'unknown')))
             for item in ['name','started','finished','alive','host','port',
                          'result','starttime','endtime','user',
                          'taskRepr', 'pids']])+')\n'
        return result

    def Cleanup(self):
        """Removes task represented by handle from the server
        """
        connection = PicklingXMLRPC.PicklingServerProxy(
                'http://%s:%i' % (self.host, self.port))
        connection.RemoveFromQueue(*(getattr(self,'_tokens',[]) + [self]))

    def StatusMode(self):
        'Return short string indicating status'

        if (not self.started):
            return 'queued'
        if (self.alive): # started and alive
            if (self.finished): # should not be finished then
                raise Exception('Weird status: alive but finished too')
            else:
                return 'running'
        else: # started but not alive, should be finished
            if (not self.finished): #should be alive then
                raise Exception('Weird status: not alive but finished')
            else:
                return 'finished'

    def StatusInfo(self):
        """Return dictionary containing the following status info:

           'starttime' : A datetime representing when task started.
           'endtime'   : A datetime representing when task ended.
           'alive'     : True if task is still running.
           'host'      : String name of host process is running on.
           'port'      : Port to use to communicate with process.
           'mode'      : Short string indicating current status. This
                         may be 'queued', 'running', 'finished'.
           'result'    : Result of process if it is finished.
           'pids'      : List of integer process ids related to task.           
        """
        return {
            'starttime' : self.starttime,
            'endtime' : self.endtime,
            'alive' : self.alive,
            'host' : self.host,
            'port' : self.port,
            'mode' : self.StatusMode(),
            'result' : self.result,
            'pids' : self.pids,
            }
            

class _ThreadRunner(threading.Thread):
    """Helper class to call ProcessObject.
    """

    def __init__(self, token, target, connection, callbacks,
                 *threadArgs, **threadKW):
        """Initializer.
        
        INPUTS:
        
        -- token:      Token to use in sending commands to connection.  
        
        -- target:     Target task to run remotely. Must be something
                       with a run or __call__ method.

        -- connection: Connection to a Process.RemoteProcess object or
                       something similar which supports ProcessObject method. 
        
        -- callbacks:  List of callables to call after target is done.      
        
        -- *threadArgs, **threadKW:    Passed to threading.Thread.__init__.
        """
        threading.Thread.__init__(self, *threadArgs, **threadKW)
        self.token = token
        self.target = target
        self.connection = connection
        self.callbacks = callbacks
        self.result = None

    def run(self):
        "Override threading.Thread to process the desired target objct."
        self.result = self.connection.ProcessObject(self.token, self.target)
        for c in self.callbacks:
            c()

class ThreadHandle(GenericProcessHandle):
    """Subclass of GenericProcessHandle to run a process in a thread.

    This class makes a call to connection.ProcessObject inside a separate
    thread. That allows the caller to keep on processing while waiting
    for the connection.ProcessObject call to finish.
    """

    def __init__(self,token,target,connection,pipe,host,port,name='unnamed',
                 extraInfo=None):
        """Initializer.
        
        INPUTS:
        
        -- token:      Token to use in making commands to connection.  
        
        -- target:     Target to task to run remotely (must be something
                       with a run or __call__ method. 

        -- connection: Connection to a Process.RemoteProcess object or
                       something similar which supports ProcessObject method. 
        
        -- pipe:       Optional pipe to remote process.
        
        -- host:       Host process is running on. 
        
        -- port:       Port process is running on. 
        
        -- name='unnamed':   Optional name for process.

        -- extraInfo=None: Dictionary of extra info to put into self.info
                           and report in self.StatusInfo().
        """
        GenericProcessHandle.__init__(self)
        self.token = token
        self.target = target
        self.connection = connection
        self.pipe = pipe
        self.thread = _ThreadRunner(token, target, connection, [
            lambda : self._Finish()])
        self.thread.start()
        self.info = {
            'starttime' : datetime.datetime.now(),
            'endtime' : None,
            'alive' : True,
            'host' : host,
            'port' : port,
            'mode' : 'running',
            'result' : None,
            'name' : name,
            }
        if (extraInfo is not None):
            for (k, v) in extraInfo.items():
                assert k not in self.info, 'Specified %s multiple ways' % str(k)
                self.info[k] = v

    def Pretty(self):
        "Return a pretty version of self"
        
        return 'TaskHandle:\n    ' + ',\n    '.join([
            '.%s=%s' % (n, repr(getattr(self,n))) for n in [
            'target','connection','pipe','thread','info']])

    def Name(self):
        "Return name"
        return self.info['name']

    def Kill(self):
        "Unsupported version of kill."

        raise Exception('Kill is not supported yet by this class.')

    def Cleanup(self):
        "Cleanup as required by GenericProcessHandle.Cleanup"

        if (self.pipe is not None and hasattr(self.pipe, 'wait')):
            logging.debug('Waiting for pipe...')
            self.pipe.wait()
            logging.debug('Pipe finished')

    def StatusInfo(self):
        """Return dictionary containing the following status info:

           'starttime' : A datetime representing when task started.
           'endtime'   : A datetime representing when task ended.
           'alive'     : True if task is still running.
           'host'      : String name of host process is running on.
           'port'      : Port to use to communicate with process.
           'mode'      : Short string indicating current status. This
                         may be 'queued', 'running', 'finished'.
           'result'    : Result of process if it is finished.
           'pids'      : List of integer process ids related to task.           
        """
        return dict(self.info)

    def StaleP(self):
        "This object is never stale."
        return False

    def _Finish(self):
        """Helper function to setup info when we finish running process.

        Intended to be called by a callback of thread running the process.
        """
        self.info['endtime'] = datetime.datetime.now()
        self.info['result'] = self.thread.result
        self.info['finished'] = True
        self.info['alive'] = False
        self.info['mode'] = 'finished'
        self.connection.Die(self.token) # kill connection now that we are done

    def UpdatedHandle(self,timeout=None,numAttempts=3,serverTimeout=None):
        """Implement as required by GenericProcessHandle.UpdatedHandle.
        """
        _ignore = numAttempts, serverTimeout
        self.thread.join(timeout)
        return self
        

        
