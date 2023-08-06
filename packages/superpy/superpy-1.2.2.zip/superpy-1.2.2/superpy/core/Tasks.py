"""Module providing various tasks to be excuted remotely.
"""

import os, threading, logging, sys, imp, stat, time
import tempfile, smtplib, datetime
from email import MIMEMultipart, MIMENonMultipart, Encoders
from email.mime.text import MIMEText

import config, Process
from TaskInfo import TaskHandle
        
            
class ServerSideTask(threading.Thread):
    """Task to run something on the server.
    """

    def __init__(self,clientTask,host,port,emailList,callbacks,
                 *threadInitArgs,**threadInitKW):


        if (callbacks is None): callbacks = []
        if (not hasattr(callbacks, 'append')):
            # Make sure we can append to callbacks later if necessary
            # This is required for task queueing to work properly.
            raise Exception('callbacks must be a list or something with append')
        
        self.host = host
        self.port = port
        self.emailList = emailList
        self.callbacks = callbacks        
        self.clientTask = clientTask
        self.finished = threading.Event()
        self.started = threading.Event()
        self.die = threading.Event()
        self.semaphore = None
        self.starttime = None
        self.endtime = None        

        
        threading.Thread.__init__(self,*threadInitArgs,**threadInitKW)

        # Set server task to daemonic since we want it to die if there
        # is nothing else left to keep it alive.
        self.setDaemon(True)        

    def GetHandle(self):
        "Get the handle for the client task and return"
        
        assert None != self.clientTask.Name(), 'Task must have a name!.'

        secsToWaitForCleanup = 5
        while (self.started.isSet() and self.finished.isSet()
               and self.isAlive() and secsToWaitForCleanup):
            # Task in a weird state where it is technically finished
            # but still alive. This can happen if cleanups after
            # task finishes have not completed. So we wait a little
            # while for cleanups to finish.
            logging.debug('waiting for cleanup...')
            time.sleep(.1)
            secsToWaitForCleanup -= .1
        if (self.started.isSet() and self.finished.isSet()
            and self.isAlive()):
            raise Exception('Task %s finsihed but still alive; cleanups fail'
                            % self.clientTask.Name())
        result = TaskHandle(
            self.clientTask.Name(),self.started.isSet(),self.finished.isSet(),
            self.isAlive(),self.host,self.port,self.clientTask.result,
            self.starttime,self.endtime,self.clientTask.user,
            taskRepr=repr(self.clientTask),pids=self.clientTask.GetPids())

        return result

    def run(self):
        """Main run method that will be called to run the thread.

        IMPORTANT: DO NOT OVERRIDE THIS! If you want to change what
                   the task does, override the Go method instead.
                   
        """
        try:
            self.PrepareToStart() # get ready to start
            self.Go() # do the actual work
            self.Finish()
            self.ReportSuccess()
        except Exception, e:
            (exc_info,exc_type) = (sys.exc_info(),sys.exc_type)
            extraMsg = '''Did you setup PYTHONPATH properly on the server?\n
            exc_info = %s\n
            exc_type = %s\n
            ''' % (exc_info, exc_type)
            logging.debug('Exception in running task %s\n%s' % (
                self.clientTask.Name(), extraMsg))
            try:
                errTrace = Process.MakeErrTrace(e)
                logging.debug('Exception trace = %s' % str(errTrace))
                self.clientTask.result = e
                self.Finish()
                self.ReportFailure(errTrace)
                #FIXME: Ideally we should also report error to submitter somehow
                raise Exception(errTrace)
            
            except Exception, doubleE:
                logging.error('Got second exception while processing first: %s'
                              % str(doubleE))
                raise
        

    def PrepareToStart(self):
        "Prepare to start running the task on the server."
        if (None != self.semaphore): self.semaphore.acquire()
        self.started.set()
        self.starttime = datetime.datetime.now()

    def Finish(self):
        "Do things required to finish running the task."
        
        if (self.finished.isSet()):
            logging.warning('Called Finish on %s multiple times.' %
                            self.clientTask.Name())
        else:
            self.finished.set()
            self.endtime = datetime.datetime.now()
            logging.debug('Executing callbacks for %s.'%self.clientTask.Name())
            for item in self.callbacks:
                logging.debug('Doing callback %s' % str(item))
                item()

    def ReleaseSemaphore(self):
        "Release sempahore if we have it acquired."
        if (None != self.semaphore):
            self.semaphore.release()
        self.semaphore = None

    def Stop(self):
        "Ask task to stop."
        self.clientTask.Stop()
        self.Finish()

    def Kill(self):
        "Kill client task immiedately."
        self.clientTask.Kill()
        self.Finish()

    def ReportSuccess(self):
        "Report that we fiished running the task successfully."
        
        msg = 'Task %s completed successfully on %s:%i at %s.' % (
            self.clientTask.Name(),self.host,self.port,datetime.datetime.now())
        logging.debug(msg)
        if (self.emailList is not None and len(self.emailList)):
            sendEmail = EmailingCallback(emailList=self.emailList,
                                         message=msg)
            sendEmail(self.clientTask)

    def ReportFailure(self,errTrace):
        "Report that we failed in running the task."
        msg = 'Task %s failed on %s:%i at %s:\n%s' % (
            self.clientTask.Name(),self.host,self.port,datetime.datetime.now(),
            errTrace)
        logging.debug(msg)
        if ([] != self.emailList):
            sendEmail = EmailingCallback(emailList=self.emailList,message=msg)
            sendEmail(self.clientTask)


    def Go(self):
        """Main method to run the action for this task.

        This is the method you should override to have your task do something
        different.
        """
        logging.debug('%s start running client task' % self.Name())
        try:
            self.clientTask.Run()
        except Exception, e:
            logging.error('%s got exception running client task: %s\nre-raise'
                          % (self.Name(), str(e)))
            raise
        logging.debug('%s finished running client task' % self.Name())

    def Die(self):
        """Should terminate the task if it is running.
        """
        self.die.set()

    def Name(self):
        "Return name of self.clientTask."

        return self.clientTask.Name()

class BasicCallback:
    """Class representing basic callback.

    Users can subclass this for other kinds of callbacks to use when
    a server finishes running a task.
    """

    def __init__(self,func):
        """Initializer.
        
        INPUTS:
        
        -- func:       Callable object to run as callback. 
        """
        self.func = func

    def __call__(self):
        return self.func()

class EmailingCallback(BasicCallback):
    """Callback to email people when task finishes on server.
    """

    def __init__(self,emailList=None,message='',subject='Task Report',
                 attachments=[],fromName='automated-report',
                 smtpServer=None):
        if (smtpServer is None): smtpServer = config.smtpServer

        if (None == emailList):
            emailList = [os.getenv('USER',os.getenv('USERNAME',None))]
            if (emailList[0] is None):
                logging.error('Could not find user to email.')
                raise Exception('Could not find user to email')
        assert list == type(emailList) or tuple == type(emailList), (
            'emailList must be a list or tuple not a %s' % type(emailList))

        self.emailList = emailList
        self.message = message
        self.subject = subject
        self.attachments = attachments
        self.fromName = fromName
        self.smtpServer = smtpServer

    def __call__(self):
        self.Report()

    def Report(self):
        """

        PURPOSE:    Sends an email to the recipients listed in self.emailList.

        """
        
        msg = MIMEMultipart.MIMEMultipart()
        msg['Subject'] = self.subject
        msg['From'] = self.fromName
        msg['To'] = "To: " + ','.join(self.emailList)
        msg.preamble = self.message
        msg.attach(MIMEText(self.message))

        for (itemName,itemData) in self.attachments:
            attachment = MIMENonMultipart.MIMENonMultipart(
                'application','octet-stream')
            attachment.add_header(
                'Content-Disposition', 'attachment',filename=itemName)
            attachment.set_payload(itemData)
            Encoders.encode_base64(attachment)
            msg.attach(attachment)

        server = smtplib.SMTP(self.smtpServer)
        server.sendmail(msg['From'],msg['To'], msg.as_string())
        server.quit()        
        
class BasicTask:
    """Skeleton for basic task.
    """

    # The parameters property controls what _MakeRepr shows.
    parameters = ['name','user'] #sub-classes may add to this

    def __init__(self,name,user=None):
        if (user is None):
            user = os.getenv('USER',os.getenv('USERNAME','unknown'))        
        self.name = name
        self.result = None
        self.user = user

    def GetPids(self):
        """Return list of process id for task.

        Subclasses should override this method to return a list of process
        ids for all tasks running under this task. The idea is that by
        killing all processs with the given pids, you can kill the task.

        Usually, a list with only a single pid will be returned. An empty
        list indicates that getting pids is unsupported by the given task.
        """
        return ['task %s does not support GetPids; please fix' % str(self)]

    def Name(self):
        """Must return a unique name for the task.
        """
        return self.name

    def Stop(self):
        "Stop running the task"

        #sub-classes can overwride to stop more cracefully if desired.
        return self.Kill()

    def Kill(self):
        "Kill the running task immeidately."

        pidList = self.GetPids()
        if (pidList):
            for pid in pidList:
                self._DoKill(pid)
        else:
            raise Exception('Task %s is unkillable (no pids).' % self.Name())
        
    def _MakeRepr(self,params):
        "Make string for __repr__ based on class parameters."
        
        return self.__class__.__name__ + '('+',\n'.join(
            '%s=%s' % (n,str(getattr(self,n,'unknown'))[0:512])
            for n in params) + ')'


    def __repr__(self):
        return self._MakeRepr(self.__class__.parameters)

    def _DoKill(self, pid):
        "Kill the given pid on current os."

        # Kill the proces using pywin32 and pid
        logging.warning('Task: %s : killing pid %s from pid %s' % (
            self.Name(), str(pid), os.getpid()))
        logging.warning('Killing pid %s' % str(pid))        
        if (os.name == 'nt'):
            import win32api, win32process, win32con
            handle = win32api.OpenProcess(
                1, win32con.PROCESS_TERMINATE, pid)
            win32process.TerminateProcess(handle, -1)
            win32api.CloseHandle(handle)
        elif hasattr(os, 'kill'):
            os.kill(pid, signals.SIGABRT)
        else:
            raise Exception('Do not know how to kill on os.name=%s' % (
                str(os.name)))
        logging.warning('Finished killing pid %s' % str(pid))

class ImportPyTask(BasicTask):
    """Task to import a python script.

    This class will import the given file name. After that, it will try
    to run methods in self.methodsToTry in the imported file.

    This is useful for creating simple python scripts to run via superpy.
    """

    parameters = BasicTask.parameters + ['fileName']

    def __init__(self,fileName,*args,**kw):
        """Initializer.
        
        INPUTS:
        
        -- fileName:   String name of file to import.

        -- methodsToTry=('Go', 'Run', 'main'): List of strings indicating
                                               methods to try to run
                                               in imported file.
        
        -- *args, **kw:        Passed to BasicTask.__init__.
        """
        BasicTask.__init__(self,*args,**kw)        

        if ('methodsToTry' in kw):
            self.methodsToTry = kw['methodsToTry']
            del kw['methodsToTry']
        else:
            self.methodsToTry = ['Go', 'Run', 'main']
            
        self.fileName = fileName

    def GetPids(self):
        "Returns process id for current process."
        return [os.getpid()]

    def Run(self):
        "Run the script"

        try:
            modName = os.path.split(self.fileName)[1][0:-3]
            modInfo = imp.find_module(modName,[os.path.dirname(self.fileName)])
            mod = imp.load_module(modName, *modInfo)
            self.result = 'imported modName'
            for name in self.methodsToTry:
                if (hasattr(mod,name)):
                    methodToTry = getattr(mod,name)
                    if (callable(methodToTry)):
                        methodResult = methodToTry()
                        self.result += ', did %s, got %s' % (name, methodResult)
            self.result += ', done'            
        except Exception, e:
            try:
                extraMsg = Process.MakeErrTrace(e)
                topDir = os.listdir(sys.path[0])
            except Exception, eAgain:
                topDir = 'Got Exception again in Tasks.py: %s' % str(eAgain)
            msg = 'Got exception in Tasks.py:\n%s\nenv=%s\npath=%s\n%s\n%s' % (
                str(e),'\n'.join(map(str,os.environ.items())),
                '\n'.join(sys.path),
                ('os.listdir(%s)=%s'%(sys.path[0],topDir)), extraMsg)
                                                           
            logging.error(msg)
            self.result = msg
        return self.result

    run = Run # alias run to Run

    @staticmethod
    def MakeSimpleScript(contents, fileName=None):
        if (fileName is None):
            fd, fileName = tempfile.mkstemp(suffix='_simpleScript.py')
            os.write(fd, contents)
            os.close(fd)
        else:
            open(fileName, 'wb').write(contents)
        os.chmod(fileName, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
        return fileName
            

class ImpersonatingTask(BasicTask):
    """Class to run task as another user.

    This set of steps is somewhat complicated. The client needs to send
    a task to the server. This sent task needs to be a class both client
    and server know about. That is what this class is.

    The server will run this class. On the server, this class will spawn
    a remote process so that it can ask the remote process to become a
    different user. This task cannot directly become another user since
    that would change the user of the server which is not desirable.

    The remote process will be asked to change its user as desired. The
    remote process will then run the targetTask passed as input to __init__.
    """

    parameters = BasicTask.parameters + [
        'targetTask', 'workingDir', 'prependPaths', 'env']

    def __init__(self,targetTask,workingDir,prependPaths=None,
                 domain=None,password=None,wrapTask=False,mode='subprocess',
                 env=None,*args,**kw):
        """
        
        INPUTS:
        
        -- targetTask:        An object with a Run method to run remotely.
        
        -- workingDir:        String representing path to run target in.
        
        -- prependPaths=None: List of strings to prepend to target's sys.path.
        
        -- domain=None:       String domain for remote user. 
        
        -- password=None:     String password for remote user.   
        
        -- wrapTask=False:    If True, wrap the task in a pickle.     
        
        -- mode='subprocess': Mode used to spawn task:

                                'subprocess' : Spawn via subprocess.py. Things
                                               spawned by subprocess will have
                                               same permissions as grandparent.

                                'logonW' : Spawn via CreateProcessWithLogonW.
                                           Things spawned as subprocesses will
                                           inherit proper permissions. The
                                           problem with logonW is that it
                                           does not work well when used inside
                                           a windows service. Using
                                           'createProcess' works well in
                                           a windows service.

                                'createProcess':  Spawn via CreateProcessAsUser.
                                           Things spawned as createProcess will
                                           inherit proper permissions. Unlike
                                           logonW, createProcess mode will
                                           also work well in windows services.
                                           The only drawback is that you have
                                           to grant the adjust memory quota
                                           and replace a token privledges
                                           in the local security policy.
        
        -- env=None:   Dictionary representing env vars to preserve.
        
        -- *args, **kw:       Additional args to BasicTask.__init__.
        
        """

        BasicTask.__init__(self,*args,**kw)
        workingDir = os.path.normpath(workingDir)

        if (prependPaths is None):
            prependPaths = list(reversed(
                ListAllParents(workingDir) + [workingDir]))
        if (not isinstance(prependPaths,(list,tuple))):
            raise Exception(
                'prependPaths must be list or tuple not %s'%prependPaths)
        self.targetTask = (targetTask if not wrapTask else
                           Process.PickledTaskWrapper(targetTask))
        self.remoteTask = None
        self.workingDir = workingDir
        self.prependPaths = prependPaths
        self.domain = domain
        self.password = password
        self.credentials = {
            'user' : self.user, 'password' : password, 'domain' : domain}
        self.exe = sys.executable
        self.mode = mode
        self.env = env
        self._ValidateMode()

    def _ValidateMode(self):
        """Warn user if mode settings are weird and change if necessary.

        The subprocess mode works pretty well if you are not doing a
        change user. Thus, if you specify another mode and do not provide
        a password, we force the mode to be subprocess so things will
        not break due to lack of credentials.

        This generally lets you specify a default mode of 'createProcess',
        but if credentials are not provided then 'subprocess' gets used.
        """
        if (self.mode != 'subprocess'):
            if (self.credentials is None or len(self.credentials) == 0
                or self.credentials.get('password', None) is None):
                logging.warning('''
           Setting self.mode="subprocess" since no credentials given.
           In this case, mode="subprocess" can work but
           mode="%s" probably would not work.
           ''' % self.mode)
                self.mode = 'subprocess'


    def GetPids(self):
        "Return pid for local task and remote task."

        pids = []
        if (self.remoteTask is not None):
            pids += self.remoteTask.GetPids()
        return pids

    def Run(self, wait=True, reRaise=False):
        """Spawn targetTask as new user and return result it gives.
        """
        # FIXME
        # The following use getattr for backward compatability with
        # earlier versions that didn't set these. Once everyone upgrades
        # the getattrs can be replaced with usual property access.
        myMode = getattr(self, 'mode', 'subprocess')
        myEnv = getattr(self, 'env', None)
        try:
            class Task(Process.RemoteProcess):
                "Simple task to run script in a remote process."

                def __init__(self, myTargetTask, remotePyPath, cred, exe,
                             myWorkingDir, myPrependPaths, *args, **kw):
                    self.remotePyPath = remotePyPath
                    self.myTargetTask = myTargetTask
                    self.cred = cred
                    self.myExe = exe
                    self.myWorkingDir = myWorkingDir
                    self.myPrependPaths = myPrependPaths
                    Process.RemoteProcess.__init__(self, *args, **kw)

                def run(self):
                    "Method to run remotely."
                    
                    logging.debug('Spawning task')
                    fileInfo = Process.RemoteFileInfo(
                        childStdin=None,childStdout=None,childStderr=None,
                        prependPaths=self.myPrependPaths,
                        workingDir=self.myWorkingDir,exe=self.myExe)
                    result = self.SpawnTask(
                        target=self.myTargetTask,fileInfo=fileInfo,
                        debug=False,credentials=self.cred,wait=wait,mode=myMode,
                        env=myEnv)
                    logging.debug('Got result: %s from spawning task' % (
                        str(result)))
                    return result

            self.remoteTask = Task(
                self.targetTask,os.getenv('PYTHONPATH',None),self.credentials,
                self.exe, self.workingDir, self.prependPaths)
            logging.debug('Running remoteTask for %s from server'
                          % self.targetTask)
            try:
                self.result = self.remoteTask.run()
            except Exception, e:
                logging.warning(
                    'got exception from running remoteTask %s: %s; re-raise' % (
                    self.targetTask, str(e)))
                raise
            logging.debug(
                'finished running remoteTask %s: got %s' % (
                self.targetTask, self.result))
        except Exception, e:
            self.result = 'Got Exception in Tasks.py: %s\n' % (str(e))
            if (reRaise):
                raise
                    
        return self.result

def ListAllParents(dirName):
    """Return list all parents of given dirName.
    """
    result = [os.path.dirname(dirName).rstrip('/').rstrip('\\').rstrip(os.sep)]
    if (not len(result[0]) or result[0][-1] in ['/', '\\', ':', '']):
        logging.debug('Not including path of %s since it looks like root' %
                      result[0])
        return []
    elif (dirName == result[0] or len(dirName) == len(result[0])):
        return result
    else:
        return ListAllParents(result[0]) + result

def _test():
    "Test module"
    import doctest
    doctest.testmod()
    
if __name__ == '__main__':
    _test()
    print 'Test finished.'
