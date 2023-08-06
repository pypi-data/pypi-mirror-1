"""Module containing classes for various types of local/remote processes.

The main item in this module intended to be used is the RemoteProcess
class which is used to spawn a remote process on the local machine.
See documentation for RemoteProcess class for details.

To run a RemoteProcess on another machine, see the Servers.py module
for how to setup a server to listen and how to send it tasks.
"""


import sys, os, random, subprocess, logging, re, copy, time, threading, cPickle
import traceback, socket

import PicklingXMLRPC, Forker, TaskInfo

try:
    from superpy.utils import WindowsUtils, WindowsSubprocess, winprocess
except ImportError, importException:
    logging.debug('''
    Unable to import Microsoft windows utilities due to exception: %s
    This is not a problem if you are not running on windows.
    ''' % str(importException))

def ChangeUser(domain, user, password):
    """Impersonate a different user.

        INPUTS:

        -- domain:        String name of user's domain.

        -- user:          String name of user to impersonate.

        -- password:      String password for user.  

        -------------------------------------------------------

        PURPOSE:          Run as a different user. This method handles
                          low-level details of switching user including
                          updating USER/USERNAME environment variables.     
    """
    import win32security, win32con
    handle = win32security.LogonUser(
        user,domain,password,win32con.LOGON32_LOGON_INTERACTIVE,
        win32con.LOGON32_PROVIDER_DEFAULT)

    win32security.ImpersonateLoggedOnUser(handle)

    os.environ['USER'] = user
    os.environ['USERNAME'] = user
    os.putenv('USER', user)
    os.putenv('USERNAME', user)    

class RemoteFileInfo:
    """Class to hold information about files/paths for remote process.

    See __init__ for details about arguments.
    """

    def __init__(self, childStdin, childStdout, childStderr, prependPaths,
                 appendPaths=('.',), remotePyPath=None, workingDir=None,
                 exe=None):
        """Initializer.
        
        INPUTS:

        -- childStdin:    File descriptor for child's stdin.
        
        -- childStdout:   File descriptor for child's stout.
        
        -- childStderr:   File descriptor for child's stderr.

        -- prependPaths:  List of strings representing paths to PREPEND to
                          sys.path for remote isntance before executing.
                          
                          IMPORANT: The remote process will often be unpickling
                          things which cause implicit imports. If you do not
                          set prependPaths properly, these imports may 
                          happen in places you don't want and cause difficulty
                          debugging later. Make sure to set prependPaths
                          properly.

        -- appendPaths=('.',): Sequence of strings indicating extra paths to
                               add to the remote instance before executing.
                               These are APPENDED to sys.path. The default
                               is '.' which is the current directory. You
                               should generally use prependPaths and only
                               use extraPaths for things you definetly want
                               to be inferior to default paths.

        -- remotePyPath=None:  Optional string indicating PYTHONPATH to use
                               for remote process.

        -- workingDir=None:    String indicating directory to run remotely in.

        -- exe=None:           Optional string indication python executable
                               to use. If this is None and sys.executable
                               does not match the regular expression 'service',
                               then we use sys.executable.

        """
        if (appendPaths is None): appendPaths = []
        if (workingDir is None): workingDir = os.getcwd()
        if (exe is None): exe = sys.executable
        if (re.compile('service').search(exe)):
            raise Exception('Refusing to use service executable: %s' % exe)

        self.childStdin = childStdin
        self.childStdout = childStdout
        self.childStderr = childStderr
        self.prependPaths = prependPaths
        self.appendPaths = appendPaths
        self.remotePyPath = remotePyPath
        self.workingDir = workingDir
        self.exe = exe

class PeerRelationship:
    """Class representing relationship between peers.
    """

    def __init__(self,host,port,allowedMethods,uniqueID,relation):
        """Initializer.
        
        INPUTS:
        
        -- host:       Internet host name for peer.
        
        -- port:       Integer port to talk to host on. 
        
        -- allowedMethods:        List of strings indicating names of methods
                                  the host may ask us to run.

        -- uniqueID:    Unique long integer identifying relationship.

        -- relation:    String indicating relationship type (e.g., 'peer',
                        'master','student').
        
        """
        self.host = host
        self.port = port
        self.allowedMethods = allowedMethods
        self.uniqueID = uniqueID
        self.relation = relation

class RemoteProcess:
    """Class representing a remote process.
    """

    # List of methods anyone may call by default
    _publicMethods = ['AcceptStudent']
    
    # List of methods a master may call on a student
    _masterMethods = ['ShowPath','SetCWD','ExtendSysPath','ProcessObject',
                      'Die','PrependSysPath','SetUser','Wait','Result',
                      'CleanFromQueue', 'SetEnv']

    def __init__(self):

        self.quit = False

        self._peers = {}
        self._server = None
        self._w32Handle = None
        self._result = None
        self._pipePid = None

    @staticmethod
    def ShowPath():
        "Show current path."
        
        return sys.path

    @staticmethod
    def SetCWD(cwd, retries=9, pause=2):
        """Set current working directory to the given value.
        
        INPUTS:
        
        -- cwd:        Path to change to.
        
        -- retries=9:  Number of times to retry.       
        
        -- pause=2:    We wait pause**i after the ith retry.    
        
        -------------------------------------------------------
        
        PURPOSE:        Change current directory in a safe manner. We
                        retry multiple times because sometimes network errors
                        may prevent changing the directory and so we retry.
        
        """


        assert retries >= 0
        assert pause > 0
        for i in range(1+retries):
            cwd = os.path.abspath(cwd)
            logging.debug('Changing cwd to %s (attempt %i)' % (str(cwd),i+1))
            try:
                os.chdir(cwd)
            except Exception, myException:
                pause = pause**i
                logging.error('''
                Got exception in doing os.chdir(%s) in Process.py: %s.
                Will retry after pausing %f
                ''' % (cwd, myException, pause))
                time.sleep(pause)
        return os.getcwd()

    @staticmethod
    def SetEnv(env, retries=9, pause=2):
        """Set given env variables
        
        INPUTS:
        
        -- env:        List of pairs representing environment variables to set.
        
        -- retries=9:  Number of times to retry.       
        
        -- pause=2:    We wait pause**i after the ith retry.    
        
        -------------------------------------------------------
        
        PURPOSE:        Set given environment variables.

        """

        assert retries >= 0
        assert pause > 0
        for (name, value) in env:
            for i in range(1+retries):
                logging.debug('setting %s=%s (attempt %i)' % (name,value,i+1))
                try:
                    os.environ[name] = value
                except Exception, myException:
                    pause = pause**i
                    logging.error('Got exception %s. Retry after pausing %f'
                                  % (myException, pause))
                    time.sleep(pause)


    @staticmethod
    def SetUser(domain,user,password):
        """Impersonate a different user.
        
        INPUTS:
        
        -- domain:        String name of user's domain.
        
        -- user:          String name of user to impersonate.
        
        -- password:      String password for user.  
        
        -------------------------------------------------------
        
        PURPOSE:          Run as a different user.
        
        """
        try:
            currentUser = os.getenv('USER', os.getenv('USERNAME', 'unknown'))
            if (user == currentUser):
                msg = 'Ignore change user request for same source/target user.'
                logging.info(msg)
            else:
                msg = 'Changing user from %s to %s\\%s' % (
                    currentUser, domain, user)
                logging.info(msg)
                ChangeUser(domain, user, password)
        except Exception, e:
            msg = 'Got Exception in Process.py: %s' % str(e)
            msg += MakeErrTrace(e)
        return msg

    @staticmethod
    def ExtendSysPath(pathList):
        "Extend sys.path by the given list."
        
        sys.path.extend(pathList)

    @staticmethod
    def PrependSysPath(pathList):
        "Put the given list of strings at the front of sys.path."

        if (not isinstance(pathList,(list, tuple))):
            raise Exception(
                'Expected pathList to be a list or tuple but got %s.' % 
                repr(pathList))
        indexes = range(len(pathList))
        for i in indexes: # error check things in original order
            if (not isinstance(pathList[i],(str,unicode))):
                raise Exception('Expected pathList[%i] to be str; got %s.' % (
                    i, repr(pathList[i])))
            elif (len(pathList[i]) and pathList[i][-1] in ['/','\\',os.sep]):
                logging.warning('''
                pathList[%i]=%s ends with %s. This is bad since it may
                confuse pythons import procedure. Ignoring last character
                ''' % (i,pathList[i],pathList[i][-1]))
                pathList[i] = pathList[i][0:-1]
        for i in reversed(indexes):         # push onto front in reverse order
            sys.path.insert(0, pathList[i]) # so they end up in right order

    @staticmethod
    def ProcessObject(obj):
        """Call run method or __call__ method of an object and return result.

        INPUTS:

        -- obj:        Object with either a run or a __call__ method.

        -------------------------------------------------------

        RETURNS:    The result of calling obj.run (if it exists) or
                    obj.__call__. 

        -------------------------------------------------------

        PURPOSE:    Run an object remotely.

        """
        result = CallIt(obj)
        return result

    @staticmethod
    def MakeRandomToken(bits=1024):
        "Make random token with given number of bits."
        return random.getrandbits(bits)

    def _GetTokenAndPeerWithMaxID(self):
        "Helper method to get most recent token."
        if (len(self._peers) == 0):
            return (0,None)
        else:
            return max(self._peers.items(),key=lambda (token,relationship):
                       relationship.uniqueID)

    def _GetNewUniqueID(self):
        "Helper method to create a new unique id."
        
        if (len(self._peers) == 0): return 1
        else: return self._GetTokenAndPeerWithMaxID()[1].uniqueID + 1
    
    def RequestMaster(self,host,port):
        """Ask a process running at the given host and port to be our master.
        
        INPUTS:
        
        -- host:        String name representing machine address of host.
        
        -- port:        Integer port number to contact master on.
        
        -------------------------------------------------------
        
        PURPOSE:        This method contacts the given server and asks it
                        to be our master and accept us as its 'student'.
                        The purpose of this is to give the master the
                        ability to issue commands to this remote process.
        
        """
        
        if (self._server is None): self.PrepareServer()
        token = self.MakeRandomToken()
        uniqueID = self._GetNewUniqueID()
        newPeers = {token : PeerRelationship(
            host,port,self._masterMethods,uniqueID,'master')}
        proxy = PicklingXMLRPC.PicklingServerProxy('http://%s:%i'%(host,port))
        myHost, myPort = self.SockName()
        proxy.AcceptStudent(None,myHost,myPort,token)
        self._peers = newPeers

    def AcceptStudent(self,host,port,token):
        """Accept another process as a student/slave.
        
        INPUTS:

        -- host:        String name representing machine address of host.
        
        -- port:        Integer port number to contact student on.
        
        -- token:       Integer token to use to prove to student we are
                        the master.
        
        -------------------------------------------------------
        
        PURPOSE:        When a student wants this process to be its master,
                        it contacts self and calls this method. This basically
                        gives self a token to use in instructing the student
                        to do things.
        
        """
        
        if (token in self._peers):
            raise Exception('Cannot re-handshake for token %s.')
        else:
            uniqueID = self._GetNewUniqueID()
            self._peers[token] = PeerRelationship(
                host,port,[],uniqueID,'student')

    def Die(self):
        "Shutdown this server."

        print 'Remote process on %s dying...' % str(self.SockName())
        self.quit = True        

    def CleanFromQueue(self, task):
        """Support the idea of cleaning a task from the queue.

        Since a RemoteProcess object can only ever have one class,
        this is aliased to Die.
        """
        _ignore = task
        self.quit = True

    def PrepareServer(self,host='localhost',port=0):
        """Prepare XML-RPC server to listen for commands to this process.
        
        INPUTS:
        
        -- host='localhost':        Host to listen at.
        
        -- port=0:        Port to listen at; 0 means next free port.
        
        -------------------------------------------------------
        
        PURPOSE:        This sets up a server to listen for requests to
                        this process. This is how we do interprocess
                        communication.
        
        """
        
        self._server = PicklingXMLRPC.PicklingXMLRPCServer((host,port))
        self._server.allow_reuse_address = 1
        self._server.register_instance(self)        
        self._server.register_introspection_functions()

    def SockName(self):
        "Return socket name for current server."
        return self._server.socket.getsockname()
        
    def Run(self):
        """Run as a server

        Causes this process to go into a loop where we listen for requests
        and handle them until we are asked to Die.
        """
        
        if (self._server is None): self.PrepareServer()
        while not self.quit:
            logging.debug('Waiting for request')
            self._server.handle_request()
        logging.debug('Finished processing requests')            

    def SpawnTask(self,target,fileInfo,
                  host='localhost',wait=True,port=None,debug=False,
                  credentials=None,priority=None,mode='subprocess',env=None):
        """Method to run an object in a separate process.

        INPUTS:

        -- target:        Object with a run or a __call__ method.

        -- fileInfo:  Instance of RemoteFileInfo representing remote file info.
        
        -- host='localhost':   String name of host to run process on.
        
        -- wait=True:          Boolean indicating whether to wait for execution
                               to finnish before returning when running target.

        -- port=None:          Integer port to use in talking to child. If
                               this is None, port will be dynamically made. 
        
        -- debug=False:        Boolean indicating whether to emit additional
                               debug information (this may come in the form
                               of logging.debug messages).
        
        -- priority=None:      Optinoal priority as expected by
                               WindowsUtils.SetPriority. Note that for servers
                               running as a windows service, setting the
                               priority can do weird things and make things
                               start working. So for servers running as
                               services, you should leave priority as None.

        -------------------------------------------------------
        
        RETURNS:        Returns result of calling target remotely on host if
                        wait is True. Otherwise, we return a
                        TaskInfo.TaskHandle instance representing a handle
                        to the task. The user should remember to call
                        Cleanup on the handle if a handle is returned
                        otherwise the remote process will be left dangling.
        
        -------------------------------------------------------
        
        PURPOSE:        This is the main method for the Process class. It
                        spawns a separate process and asks it to run
                        the target object.
            

    This method is designed to run a target object in a separate process.
    This is useful both for parallel processing as well as for running
    tasks in isolation (e.g., if you want to run a regression test in
    a separate process).

    The idea is that you create a a target object that has a run method
    and pass that to this function which arranges for the run method
    of the target to be called in a separate process.

    See the docstrings for the following methods for some examples:

      _simpleExample
      _exampleWithNoWait
      _picklingExample

        """
        if (self._server is None): self.PrepareServer()

        host, port = self.SockName()
                
        forkArgs = Forker.MakeCommandLine(
            fileInfo.exe,Forker.__file__,host,port)
        
        childProc, self._pipePid = self._CreateSubprocess(
            forkArgs,fileInfo,mode,credentials)

        oldToken = self._GetTokenAndPeerWithMaxID()[0]
        self._server.handle_request() # wait for student to connect back
        newToken, newPeer = self._GetTokenAndPeerWithMaxID()
        if (oldToken == newToken):
            raise Exception('Expected student to connect, but it did not.')
        try:
            ### IMPORTANT: We must make sure to do SetUser before setting
            ###            paths. Otherwise, python gets into a weird state
            ###            where it sees paths it can't access and then
            ###            never looks at those paths even if it can
            ###            access them later.
            connectionToChild = PicklingXMLRPC.PicklingServerProxy(
                'http://%s:%i' % (newPeer.host,newPeer.port))
            if (credentials is not None and len(credentials)==3):
                if (mode == 'subprocess'):
                    logging.info('Requestig change user to %s' %
                                 credentials['user'])
                    msg = connectionToChild.SetUser(
                        newToken,credentials['domain'],credentials['user'],
                        credentials['password'])
                    logging.info('Change user result = %s' % str(msg))
                else:
                    newEnv = [('USERNAME',credentials['user']),
                              ('USER', credentials['user'])]
                    logging.info('Set child user env vars to: %s'%str(newEnv))
                    connectionToChild.SetEnv(newToken, newEnv)
            else:
                logging.info('Not requestig change user.')                
            if (len(fileInfo.prependPaths)): connectionToChild.PrependSysPath(
                newToken,fileInfo.prependPaths)
            if (len(fileInfo.appendPaths)): connectionToChild.ExtendSysPath(
                newToken,fileInfo.appendPaths)        
            if (priority is not None):
                WindowsUtils.SetPriority(newToken,priority)
            connectionToChild.SetCWD(newToken,fileInfo.workingDir)
            if (env):
                connectionToChild.SetEnv(newToken, env.items())
            if (debug):
                logging.info('path of child is:\n\n%s\n\n' %
                             connectionToChild.ShowPath(newToken))
                logging.info('cwd of child is: %s' % fileInfo.workingDir)
            if (wait):
                logging.debug('Asking child to process target...')
                oldtimeout = socket.getdefaulttimeout()
                sd = None # clear the timeout if wait is True
                logging.debug('Making old timeout of %s to %s'%(oldtimeout,sd))
                socket.setdefaulttimeout(sd) 
                result = connectionToChild.ProcessObject(newToken,target)
                logging.debug('Waiting for child...')
                try:
                    connectionToChild.Die(newToken)
                except Exception, myException:
                    logging.error('Ignoring error %s when asking child to die.'
                                  % str(myException))
                finally:
                    socket.setdefaulttimeout(oldtimeout)
                if (hasattr(childProc, 'wait')):
                    childProc.wait()
            else:
                result = TaskInfo.ThreadHandle(
                    newToken,target,connectionToChild,childProc,
                    newPeer.host,newPeer.port)
        except Exception, e:
            # Tell the child to die if we got an exception
            logging.error('Killing child %s due to exception: %s\n%s' % (
                target,e,MakeErrTrace(e)))
            connectionToChild.Die(newToken)
            raise
            
        return result

    @staticmethod
    def _CreateSubprocess(cmdLine, fileInfo, mode, credentials):      
        """Create a subprocess.
        
        INPUTS:
        
        -- cmdLine:        List of strings represneting command line.
        
        -- fileInfo:       Instance of RemoteFileInfo indicating file
                           descriptors to use.
        
        -- mode:           How to create subprocess:

                        'subprocess'    : Spawn via subprocess.py.
                        'createProcess' : Spawn via CreateProcessAsUser.
                        'logonW'        : Spawn via CreateProcessWithLogonW.
        
        -- credentials:    Dictioanry of credntial to use for remote login.    
        
        -------------------------------------------------------
        
        RETURNS:        COnnection to new child process.
        
        """
        if (mode == 'subprocess'):
            newEnv = copy.deepcopy(os.environ)
            if (fileInfo.remotePyPath is not None):
                newEnv['PYTHONPATH'] = os.path.normpath(
                    fileInfo.remotePyPath).replace('\\','/')
                logging.info('Using env:\n%s\n' % str(newEnv))
            pipeToChild = subprocess.Popen(
                cmdLine,stdin=fileInfo.childStdin,stdout=fileInfo.childStdout,
                stderr=fileInfo.childStderr,env=newEnv)
            pid = pipeToChild.pid
        elif (mode == 'createProcess'):
            pipeToChild = winprocess.Process(
                ' '.join(cmdLine),'%s\n%s\n%s'%(
                credentials['domain'],credentials['user'], 
                credentials['password']))
            # With CreateProcess must not set cwd until after
            # the process starts. Use SetCWD later to set working dir
            pid = pipeToChild.PId
        elif (mode == 'logonW'):
            pipeToChild = WindowsSubprocess.CreateProcessWithLogonW(
                credentials['user'], credentials['domain'],
                credentials['password'], 0, cmdLine[0], ' '.join(cmdLine),
                lpCurrentDirectory=os.path.normpath(os.getcwd()),
                dwCreationFlags = 0)
            # With CreateProcessWithLogonW, must not set cwd until after
            # the process starts. Use SetCWD later to set working dir
            pid = pipeToChild.dwProcessId
        else:
            raise Exception('Invalid mode %s' % str(mode))
        
        return pipeToChild, pid
        

    @staticmethod
    def _simpleExample():
        """Docstring illustrating a simple example of usage.

>>> import logging; logging.info('Doctest for _simpleExample')        
>>> import Process, tempfile, os, time
>>> outputLog = tempfile.mktemp()
>>> outputLogFD = open(outputLog,'w')
>>> t = Process.RemoteProcess()
>>> fileInfo = Process.RemoteFileInfo(
... prependPaths=[],
... childStdin=None,childStdout=outputLogFD,childStderr=outputLogFD)
>>> try:
...     t.SpawnTask(Process._ExampleForTest(), fileInfo)
... except Exception, e:
...     print 'Got exception e:\\n' + str(e)
...     print 'output log is:\\n' + open(outputLog,'r').read()
... 
42
>>> outputLogFD.close()
>>> os.remove(outputLog)
>>> os.path.exists(outputLog)
False
        """

    @staticmethod
    def _exampleWithNoWait():
        """Docstring illustrating simple example with wait=False.

>>> import logging; logging.info('Doctest for _exampleWithNoWait')
>>> import Process, tempfile, os, time
>>> outputLog = tempfile.mktemp()
>>> outputLogFD = open(outputLog,'w')
>>> t = Process.RemoteProcess()
>>> fileInfo = Process.RemoteFileInfo(
... prependPaths=[],
... childStdin=None,childStdout=outputLogFD,childStderr=outputLogFD)
>>> try:
...     handle = t.SpawnTask(Process._ExampleForTest(), fileInfo, wait=False)
... except Exception, e:
...     print 'Got exception e:\\n' + str(e)
...     print 'output log is:\\n' + open(outputLog,'r').read()
... 
>>> handle = handle.UpdatedHandle(timeout=10)
>>> handle.StatusInfo()['result']
42
>>> outputLogFD.close()
>>> handle.Cleanup()
>>> os.remove(outputLog)
>>> os.path.exists(outputLog)
False
    """

    @staticmethod
    def _picklingExample():
        """Docstring illustrating simple example with pickling wrapper.

        Sometimes you want to pickle the task you are spawning remotely.
        This is often necessary if you need to have the remote instance
        run under a different username. This example does not call
        SetUser, but it is intended to work with that.

>>> import logging; logging.info('Doctest for _picklingExample')
>>> import Process, tempfile, os, time, pickle
>>> outputLog = tempfile.mktemp()
>>> outputLogFD = open(outputLog,'w')
>>> t = Process.RemoteProcess()
>>> fileInfo = Process.RemoteFileInfo(
... prependPaths=[],
... childStdin=None,childStdout=outputLogFD,childStderr=outputLogFD)
>>> target = Process._ExampleForTest()
>>> pickledTarget = Process.PickledTaskWrapper(target)
>>> try:
...     result = t.SpawnTask(pickledTarget, fileInfo)
...     result = pickle.loads(result)
...     result
... except Exception, e:
...     print 'Got exception e:\\n' + str(e)
...     print 'output log is:\\n' + open(outputLog,'r').read()
... 
42
>>> outputLogFD.close()
>>> os.remove(outputLog)
>>> os.path.exists(outputLog)
False
        """

    @staticmethod
    def _doubleExample():
        """Docstring illustrating a simple example of usage.

        This test will raise an exception. It is mostly meant to
        be useful as a template for manual testing since it requires
        people to enter passwords.

>>> import logging; logging.info('Doctest for _doubleExample')        
>>> import Process, tempfile, os, time
>>> outputLog = tempfile.mktemp()
>>> outputLogFD = open(outputLog,'w')
>>> t = Process.RemoteProcess()
>>> fileInfo = Process.RemoteFileInfo(
... prependPaths=[],
... childStdin=None,childStdout=outputLogFD,childStderr=outputLogFD)
>>> try: # try to use UNC path if possible.
...     fileInfo.workingDir = Process.GetUNCPath(fileInfo.workingDir)
... except Exception, e:
...     pass
... 
>>> credentials = {'user' : 'FIX', 'domain' : 'FIX', 'password' : 'FIX'}
>>> # The following won't work unless password is provided
>>> try: #doctest: +ELLIPSIS
...     t.SpawnTask(Process._DoubleSpawnExample(credentials=credentials),
...                 fileInfo, credentials=credentials, mode='createProcess')
... except Exception, e:
...     print 'Got exception %s:\\n' % str(e)
...     print 'output log is:\\n' + open(outputLog,'r').read()
...
Got exception ...
<BLANKLINE>
output log is:
<BLANKLINE>
>>> outputLogFD.close()
>>> os.remove(outputLog)
>>> os.path.exists(outputLog)
False
        """

    def GetPids(self):
        "Return list of process ids for remote task(s)."
        
        if (self._pipePid is None):
            return []
        else:
            return [self._pipePid]

    def _dispatch(self, method, params):
        """Helper method to mediate call from xml-rpc.
        
        INPUTS:
        
        -- method:        Name of method to call.
        
        -- params:        List where params[0] is the authentication token
                          required to call the given method and params[1:]
                          are the parameters for the method.
        
        -------------------------------------------------------
        
        RETURNS:        Result of calling getattr(self,method)(*params[1:]).
        
        -------------------------------------------------------
        
        PURPOSE:        This method first makes sure that the token in
                        params[0] gives the caller the right to call the
                        desired method and then executes the method. This
                        ensures that only authenticated XML-RPC calls
                        get run.
        
        """
        
        if (len(params) == 0):
            raise Exception("""
            Must provide token as first argument for any method call.
            For public methods, you may provide the token '' or None.
            """)
        token = params[0]
        if (token is None or token == ''):
            allowedMethods = self._publicMethods
        elif (token not in self._peers):
            raise Exception('Invalid or unknown token: %s.' % token)
        else:
            allowedMethods = self._peers[token].allowedMethods

        if (method not in allowedMethods):
            raise Exception(
                'Invalid method name %s for token %s. Allowed methods=\n%s\n'%(
                method,token,'\n'.join(map(str,allowedMethods))))
        else:
            return getattr(self,method)(*params[1:])

class ThreadToRunTask(threading.Thread):
    """Simple class to run a given target task in a separate thread.
    """
    
    def __init__(self, task, callbacks, joins=None):
        """Initializer.
        
        INPUTS:
        
        -- task:       Object with a run or __call__ method to run
                       in separate thread. 
        
        -- callbacks:  List of objects with __call__ methods to call
                       when task finishes.

        -- joins:      List of threads to join before starting when
                       run is called. 
        
        """
        if (joins is None): joins = []
        self.task = task
        self.callbacks = callbacks
        self.joins = joins
        self.result = None
        threading.Thread.__init__(self)

    def run(self):
        """Run given task in a thread.

        When task finishes, self.callbacks will be called and self.result
        will contain result of calling self.task.
        """
        for t in self.joins:
            print '--> joining %s' % str(t)
            t.join()
        self.result = CallIt(self.task)
        for c in self.callbacks:
            print '--> calling %s' % str(c)
            CallIt(c)
        return self.result

def GetCallMethod(obj, options=('Run','run','__call__')):
    """Extract the desired call method for a given object.
    
    INPUTS:
    
    -- obj:        An object with some type of call method.
    
    -- options=('Run','run','__call__'):   List of strings representing
                                           possible call methods.
                                           
    -------------------------------------------------------
    
    RETURNS:    The first attribute of obj which is in options. If none of
                these are present an Exception is raised.
    
    -------------------------------------------------------
    
    PURPOSE:    Figure out whether an object as a callable method.
    
    """
    for name in options:
        if (hasattr(obj,name)):
            return getattr(obj,name)
    raise Exception(
        "Object %s does not have any methods in %s" % (str(obj), options))


def CallIt(obj, options=('Run','run','__call__')):
    """Callt he desired call method on the given object.
    
    INPUTS:
    
    -- obj:        An object with some type of call method. Alternatively,
                   this can be a string representing a pickled version of
                   such an object.
    
    -- options=('Run','run','__call__'):   List of strings representing
                                           possible call methods.
                                           
    -------------------------------------------------------
    
    RETURNS:    The result of calling the first attribute of obj which is in
                options. If none of these are present an Exception is raised.
    
    -------------------------------------------------------
    
    PURPOSE:    Figure out whether an object as a callable method and call it.
    
    """

    if (isinstance(obj, (str, unicode))):
        obj = cPickle.loads(obj)    
    method = GetCallMethod(obj, options)
    return method()


class _ExampleForTest:
    "Class to illustrate how to use Process class."

    def __init__(self, delay=0, func=sum, args=((42,),)):
        self.delay = delay
        self.func = func
        self.args = args
    
    def run(self):
        "run the task"
        if (self.delay):
            time.sleep(self.delay)
        return self.func(*self.args)

class _DoubleSpawnExample:
    "Helper class used for doctest"

    def __init__(self, credentials=None, mode='createProcess',
                 prependPaths=None):
        self.proc = None
        self.result = None
        self.credentials = credentials
        self.mode = mode
        self.prependPaths = prependPaths if prependPaths else []

    def run(self):
        "Method to run simple test by spawning a remote _ExampleForTest."
        self.proc = RemoteProcess()
        fileInfo = RemoteFileInfo(
            prependPaths=self.prependPaths,childStdin=None,childStdout=None,
            childStderr=None)
        logging.warning('Doing double spawn')
        self.result = self.proc.SpawnTask(
            _ExampleForTest(), fileInfo, credentials=self.credentials,
            mode=self.mode)
        return self.result

class PickleHolder:
    """Simple class to hold a pickled string.

    This is sometimes useful if you want to distinguish between a
    simple string and a pickled object. Putting something in a
    PickleHolder automatically indicates that it's a pickled object.
    """

    def __init__(self, thingToPickle):
        self.pickledString = cPickle.dumps(thingToPickle)

    def Extract(self):
        "Extract pickled string into result."
        return cPickle.loads(self.pickledString)

class PickledTaskWrapper:
    """Class to take a target task and wrap it as a pickle.

    The idea is that sometimes you want to pass around a target task as
    a pickled string. This lets you keep the target task pickled but
    still provides an easy way to unpickle it and run it.
    """

    def __init__(self, target, pickleResult=True, pickleMode='s'):
        """Initializer.
        
        INPUTS:
        
        -- target:     A target task with some kind of call method
                       as determined by GetCallMethod. 
        
        -- pickleResult=True:   Whether to pickle the result of running
                                target.
        
        -- pickleMode='s':      How to pickle the result:

                                  's' : return as pickled string
                                  'h' : return as PickleHolder.
        
        """
        _callMethod = GetCallMethod(target) # make sure has call method
        self.reprTarget = repr(target)
        self.target = cPickle.dumps(target)
        self.pickleResult = pickleResult
        self.pickleMode = pickleMode

    def Run(self):
        """Run the task and return the result.
        """
        unpickled = cPickle.loads(self.target)
        result = CallIt(unpickled)
        self.reprTarget = repr(unpickled)
        try:
            self.target = cPickle.dumps(unpickled)
        except Exception, myExc:
            msg = 'Got Exception when trying to pickle self.target:\n%s' % (
                '\n'.join([str(self.target),'Exception info:',str(myExc),
                           MakeErrTrace(myExc)]))
            logging.error(msg)
            raise Exception(msg)

        if (self.pickleResult):
            if (self.pickleMode == 's'):
                result = cPickle.dumps(result)
            elif (self.pickleMode == 'h'):
                result = PickleHolder(result)
            else:
                raise Exception('Invalid pickleMode=%s.' % str(self.pickleMode))
        return result

    def __repr__(self):
        "Provide string representation of class isntance."

        args = ', '.join(['%s=%s' % (name, repr(getattr(self, name))[0:128])
                          for name in ['target', 'pickleResult']])
        result = '%s(%s)' % (self.__class__.__name__, args)
        return result

def GetUNCPath(arg):
    """Return full UNC path for a given local path.
    
    INPUTS:
    
    -- arg:        A local path to translate to UNC.
    
    -------------------------------------------------------
    
    RETURNS:    UNC path matching local path.
    
    """
    import win32net
    drive, path = os.path.splitdrive(os.path.abspath(arg))
    uncDrive = win32net.NetUseGetInfo(None, drive, 0)['remote']
    fullUNCSrcPath = uncDrive + path
    return fullUNCSrcPath


def MakeErrTrace(myException, extraMsg=''):
    "Return string indicating traceback for exception"
    
    return ('Exception of type \'' + str(sys.exc_type) + '\':  \'' + 
            myException.__str__() + '\'.\n\n\n' + extraMsg + 
            ''.join(traceback.format_tb(sys.exc_info()[2])) +
            str(sys.exc_info))

def _test():
    "Test docstrings in module"
    import doctest
    doctest.testmod()
    
if __name__ == '__main__':
    logging.getLogger('').setLevel(0)
    _test()
    print 'Test finished.'
