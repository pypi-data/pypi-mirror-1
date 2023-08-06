"""Module containing code to represent a superpy server.

The main class users will interact with is the Scheduler class which is
used to submit tasks to the best server in a group. See docs for the
Scheduler class for details.
"""

import os, socket, threading, SocketServer, logging, re, time, datetime


import Tasks, PicklingXMLRPC, SimpleXMLRPCServer, DataStructures


class Scheduler:
    """Class representing a scheduler to balance tasks among multiple servers.
    """

    def __init__(self,hostList):
        self.hosts = {}
        for i in range(len(hostList)):
            entry = hostList[i]
            if (isinstance(entry,(str,unicode))): entry = [entry]
            if (len(entry) == 1): host,port=entry[0],BasicRPCServer.defaultPort
            elif (len(entry) == 2): host,port = entry
            else:
                raise Exception("Entry %i=%s is not a valid host,port pair." % (
                    i,entry))
            if ((host,port) in self.hosts):
                raise Exception("Pair %s:%s was specified more than once." % (
                    host, port))
            else:
                logging.debug('Making connection to %s' % ([host,port]))
                connection = PicklingXMLRPC.PicklingServerProxy(
                    'http://%s:%i' % (host,port))
                self.hosts[(host,port)] = connection

    def SubmitTaskToBestServer(self,task,*args,**kw):
        """Submit a task to the best available server.
        
        INPUTS:
        
        -- task:        Subclass of Tasks.BasicTask to submit.
        
        -- *args, **kw: Passed to Submit method of best server.
        
        -------------------------------------------------------
        
        RETURNS:        Handle for newly submitted task.
        
        -------------------------------------------------------
        
        PURPOSE:        Submit a task to the best available server.
        
        """
        assert None != task.Name(), 'Task must have a name!'
        logging.debug('Requesting loads from known servers.')
        newtimeout = 30
        loads = []
        for (k,v) in self.hosts.iteritems():
            try:
                oldtimeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(
                    newtimeout) # set timeout in case server dead
                logging.debug('Contacting %s:%s...' % (str(k), str(v)))
                cpuLoad = v.CPULoad()
            except socket.error, e:
                logging.warning('Unable to contact %s:%s because %s;skipping'% (
                    str(k),str(v),str(e)))
            except Exception, e:
                logging.warning('Unable to contact %s:%s because %s;skipping'% (
                    str(k),str(v),str(e)))
            else:
                loads.append((k, v, cpuLoad))
                logging.debug('Got load of %s from %s:%s' % (loads[-1],k,v))
                socket.setdefaulttimeout(oldtimeout)
            finally:
                socket.setdefaulttimeout(oldtimeout)
                
        if len(loads) < 1:
            raise Exception(
                'No server can be reached in %s seconds, re-try later'
                %newtimeout)
        loads.sort(key=lambda entry: entry[2])
        logging.debug('Loads are %s' % str(loads))
        handle = loads[0][1].Submit(task,*args,**kw)
        return handle

    def ShowQueue(self, host, port, timeout=3):
        """Show queue for server at given host, port.
        """
        try:
            oldtimeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout) # set timeout in case server dead
            logging.debug('Contacting %s:%s...' % (host, port))
            connection = self.hosts[(host, port)]
            return connection.ShowQueue()
        except Exception, e:
            logging.info('Timeout: Unable to contact %s:%s because %s' % (
                str(host),str(port),str(e)))
        finally:
            socket.setdefaulttimeout(oldtimeout)

    def CleanOldTasks(self, host, port):
        """Call CleanOldTasks for server at given host, port.
        """
        connection = self.hosts[(host, port)]
        return connection.CleanOldTasks()
        

class BasicRPCServer(PicklingXMLRPC.PicklingXMLRPCServer,
                     SocketServer.ThreadingMixIn):
    """Class representing server to run remote tasks.

    This class represents a server to run superpy tasks. It is not
    really intended to be used directly but to be called by the
    Spawn.py and SpawnAsService.py scripts.

    Once instantiated, it listens for requests from clients to run tasks.
    """

    # The following list of functions are the ones that we allow to be
    # called via RPC.
    _RPCFunctions = ['Submit','Terminate','RemoveFromQueue','Status',
                     'CountNumCPUs','CPULoad','ShowQueue', 'CleanFromQueue',
                     'CleanOldTasks']
    defaultPort = 9287
    def __init__(self,cpus=None,host=None,port=None, *args, **kw):
        """Initializer.
        
        INPUTS:
        
        -- cpus=None:  Optional integer indicating number of CPUs server has.
        
        -- host=None:  String indicating name of host to run on. If this is
                       None, then we lookup name of localhost. 
        
        -- port=None:  Integer port to listen on. If 0, we dynamically generate
                       port num which you can get via self.socket.getsockname()
        
        -- *args, **kw: Additional args to PicklingXMLRPCServer.__init__.
        """
        
        if (None == host): host = socket.gethostname()
        if (None == port): port = self.defaultPort
        #if (None == cpus): cpus = self.CountNumCPUs()
        cpus = 1
        
        self._quit = False
        self._thread = None
        self._host = host
        self._port = port
        self._cpus = cpus
        self._queue = DataStructures.NamedQueue()
        self._active = DataStructures.NamedQueue()
        self._uaSemaphore = threading.Semaphore()

        logging.debug('Starting BasicRPCServer on %s:%i.' % (host,port))
        PicklingXMLRPC.PicklingXMLRPCServer.__init__(
            self,(host,port), requestHandler = NewRequestHandler, *args, **kw)
        self.allow_reuse_address = 1        
        if (port == 0): # if provided port was 0, set self._port to real port
            self._port = self.socket.getsockname()[1]
        self.register_introspection_functions()
        for name in self._RPCFunctions:
            self.register_function(getattr(self,name))

    def __del__(self):
        "Shutdown server. Usually called automatically by python."
        
        logging.info('Shutting down server at %s:%s' % (self._host, self._port))

    def Terminate(self):
        """Stop running.

        This method sets self._quit to True. Other things should look
        at that periodically and die after cleaning up.
        """

        
        self._quit = True

    def serve_forever(self):
        """Serve requests.

        Either this or serve_forever_as_thread are the main functions to
        call to have the server process requests.
        """
        print 'Entering service loop forever or until killed...'
        while (not self._quit):
            self.handle_request()

    def serve_forever_as_thread(self, daemon=False):
        """Starts a new thread and runs self.serve_forever in that thread.

        This is probably the main function you want to use to start the
        server handling requests. It runs self.serve_forever in a new
        thread. This lets you just call self.Terminate whenever you want
        the server to stop.

        If the daemon argument is True, then the thread is run as a daemon
        so it exits if there are no other threads running the program.
        """
        self._thread = threading.Thread(target = self.serve_forever,verbose=0)
        self._thread.setDaemon(daemon)
        self._thread.start()

    def Submit(self,task,emailList=None,callbacks=None): 
        """Submit a task to this server.
        
        INPUTS:
        
        -- task:        Instance of subclass of BasicTask to submit.
        
        -- emailList=None:  Optional list of strings representing email
                            addresses to email when task finishes.
        
        -- callbacks=None:  Optional list of Tasks.BasicCallback instances
                            to call when task completes.    
        
        -------------------------------------------------------
        
        RETURNS:        Handle to newly submitted task.
        
        -------------------------------------------------------
        
        PURPOSE:        Submit a task to the server to run.
        
        """
        assert isinstance(task,Tasks.BasicTask), """
        Expected instance of Tasks.BasicTask but got %s.
        """ % str(task)
        callbacks = [] if callbacks is None else list(callbacks) + [
            lambda : self.UpdateActives]
        serverTask = Tasks.ServerSideTask(
            task,self._host,self._port,emailList,callbacks)
        self._queue.Push(task.Name(), serverTask)
        result = serverTask.GetHandle()

        self.UpdateActives()
        
        return result

    def RemoveFromQueue(self,handle):
        """Remove a task from the server's queue.
        
        INPUTS:
        
        -- handle:        Instance of TaskInfo.TaskHandle representing the
                          task to remove. Handles are returned by self.Submit.
        
        -------------------------------------------------------
        
        PURPOSE:        Find task to remove, ask it to stop if it is not
                        finished, kill it if it does not stop, and then
                        call task.Finish.

                        This is useful for removing a task you no longer
                        want to be processed.
        
        """
        
        name = handle.Name()
        task = self._queue[name]

        if (task.started.isSet()):
            if (not task.finished.isSet()):
                logging.info('Asking task %s to stop.' % name)
                task.Stop()
                time.sleep(3)
                if (not task.finished.isSet()):
                    logging.warning('Task %s did not stop; killing.' % name)
                    task.Kill()
                    task.Finish()
                    
        assert (not task.started.isSet()) or task.finished.isSet(), ''''
        Task in a weird state: %s It should either be finished or unstarted.
        ''' % str(task)
        
        return self.CleanFromQueue(handle)
        
    def CleanFromQueue(self, handle):
        """Take a task out of the queue.
        
        INPUTS:
        
        --handle: An instance of TaskHandle to be removed form its server's
                  queue.
                  
        ---------------------------------------------------------------
        PURPOSE:
        
        Slightly different implementation of RemoveFromQueue from
        Servers.BasicRPCServer, that doesn't call the task's Finish() method.
        However, it is an error to call this function if the task wasn't
        finished.
        
        """
        name = handle.Name()
        task = self._queue.PopItem(name)

        if (task.started.isSet() and not task.finished.isSet()):
            raise Exception('''
            Tried to clean up started but unfinished task %s!
            Use RemoveFromQueue if you want to remove unfinished task.
            ''' % str(name))
        name = task.clientTask.Name()
        
        self.UpdateActives()

        return 0

    def CPULoad(self):
        """Return number of unfinished tasks minus number of cpus.

        This is a rough measure of how loaded the server is and is used
        by the Scheduler class.
        """
        
        count = sum([1 if (not task.finished.isSet()) else 0
                     for (_name,task) in self._queue.ShowItems()])
        return count - self._cpus


    def ShowQueue(self,regexp='.*',timeout=0):
        """Show all tasks in the queue.
        
        INPUTS:
        
        -- regexp='.*':    Regular expression for names of tasks to show.
        
        -- timeout=60:     Timeout in seconds to allow when checking
                           status of task.
        
        -------------------------------------------------------
        
        RETURNS:        List of TaskInfo.TaskHandle objects representing
                        items in the queue.
        
        -------------------------------------------------------
        
        PURPOSE:        Useful to see what the server is doing.
        
        """
        compiledRegexp = re.compile(regexp) if isinstance(
            regexp,(str,unicode)) else regexp
        result = []
        for n, _t in sorted(self._queue.ShowItems(),key=lambda pair: pair[0]):
            if (compiledRegexp.search(n)):
                logging.debug('Contacting %s to get queue (timeout=%s' % (
                    n, timeout))
                result.append(self.Status(n,timeout=timeout))
            else:
                logging.debug('Skipping %s since regexp does not match' % n)

        return result

    def CleanOldTasks(self, allowedLag=86400):
        """Clean out old finished tasks from the queue.
        
        INPUTS:
        
        -- allowedLag=86400:        Lag in seconds between when a task is
                                    finished and when it is considered old.
                                    For example, 86400 means tasks that finished
                                    more than one day ago are old and should
                                    be cleaned.

        -------------------------------------------------------

        RETURNS:        Returns list of names of cleaned tasks.
        
        -------------------------------------------------------
        
        PURPOSE:        Provide a simple way to clean out old tasks.
        
        """
        now = datetime.datetime.now()
        tasksToClean = [(name, task) for (name, task) in self._queue.ShowItems()
                        if (task.finished.isSet() and (
            (now - task.endtime ) > datetime.timedelta(seconds=allowedLag)))]
        for (name, task) in tasksToClean:
            logging.info('Cleaning finished task %s:\n%s\n' % (name, task))
            self._queue.PopItem(name)

        self.UpdateActives()
        
        return [name for (name, _task) in tasksToClean]

    def UpdateActives(self):
        """Updates which tasks are active and spawns new tasks if necessary.
        """

        try:
            logging.info('trying to aquire self._uaSempahore w/o blocking')
            if (not self._uaSemaphore.acquire(blocking=False)):
                logging.warning('Blocking to aquire self._uaSempahore')
                self._uaSemaphore.acquire(blocking=True)
            # First remove any finished or dead items form self._active
            activeItems = self._active.ShowItems()
            for (name, item) in activeItems:
                if (item.finished.isSet() or not item.isAlive()): 
                    self._active.PopItem(name)

            # Now try to start any pending items if necessary
            activeItems = self._active.ShowItems()
            while (len(activeItems) < self._cpus):
                pendingItems = [
                    (name, task) for (name, task) in self._queue.ShowItems()
                    if not task.started.isSet()]
                if (len(pendingItems) == 0):
                    break # nothing left to start
                else:
                    name, task = pendingItems[0]                    
                    logging.debug('Starting task %s: %s' % (name, task))
                    task.callbacks.append(UpdateActivesCallback(self))
                    task.start()
                    self._active.Push(name, task)
                    activeItems = self._active.ShowItems()
        finally:
            logging.debug('Releaseing self._uaSempahore')
            self._uaSemaphore.release()
            

    def Status(self,handle,timeout=0):
        """
        
	INPUTS:
        
	-- handle:	Either a string name or a TaskHandle object.
        
	-- timeout=None:	Optional integer timeout to say how many
                                seconds to wait for task to complete if it
                                is still running. A timeout of None means
                                wait until the task is done.
        
	-------------------------------------------------------
        
	RETURNS:        A TaskHandle object providing information about the
                        task.
        
	-------------------------------------------------------
        
	PURPOSE:        Get the status of a remote task.
        
        """
        _ignore = timeout
        
        name = handle if isinstance(handle, (str, unicode)) else handle.Name()
        task = self._queue[name]
        handle = task.GetHandle()

        return handle

    @staticmethod
    def CountNumCPUs():
        """Determine number of cpus on this machine and return it.
        """

        cpus = os.environ.get("NUMBER_OF_PROCESSORS",None)
        if (None != cpus): return int(cpus)
        elif (hasattr(os, 'sysconf')): # Check if system supports sysconf
            cpus = getattr(os, 'sysconf_names').get("SC_NPROCESSORS_ONLN")
            if (isinstance(cpus, int) and cpus > 0): return cpus
        else: # Maybe the machine is a Mac...
            try:
                cpus = int(os.popen2("sysctl -n hw.ncpu")[1].read())
                return int(cpus)
            except Exception, _e:
                return 1 # couldn't figure it out so just say 1 cpu

    def Host(self):
        "Return name of host server is running on."
        return self._host

    def Port(self):
        "Return port server is running on."
        return self._port
    

class UpdateActivesCallback(Tasks.BasicCallback):
    """Callback to update active tasks in server.

    This callback is meant to be run after a task finishes to tell the
    server to update the active tasks to mark finished stuff as done and
    to potentially spawn new tasks.
    """

    def __init__(self, server):
        """Initailizer.
        
        INPUTS:
        
        -- server:     Instance of BasicRPCServer to call UpdateActives method
                       on. 
        """
        Tasks.BasicCallback.__init__(self, None)
        self.server = server

    def __call__(self):
        "Call UpdateActives method on self.server."
        
        self.server.UpdateActives()

class NewRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    """
    Fixes the 500 Internal Server Error Bug. This forces us to read data in
    smaller chunks (5MB instead of the previous 10MB limit. The actual problem
    seems to be with Python's socket() implementation on Windows, which gives
    Memory Errors otherwise.
    
    python.org bug report:
    http://mail.python.org/pipermail/python-bugs-list/2007-May/038493.html
    """
    def do_POST(self):
        """Handles the HTTP POST request.

        Attempts to interpret all HTTP POST requests as XML-RPC calls,
        which are forwarded to the server's _dispatch method for handling.
        """
        # Check that the path is legal
        if not self.is_rpc_path_valid():
            self.report_404()
            return

        try:
            # Get arguments by reading body of request.
            # We read this in chunks to avoid straining
            # socket.read(); around the 10 or 15Mb mark, some platforms
            # begin to have problems (bug #792570).
            
            
            #MODIFICATION:
            #max_chunk_size = 10*1024*1024
            max_chunk_size = 2*1024*1024 
            
            
            size_remaining = int(self.headers["content-length"])
            L = []
            while size_remaining:
                chunk_size = min(size_remaining, max_chunk_size)
                L.append(self.rfile.read(chunk_size))
                size_remaining -= len(L[-1])
            data = ''.join(L)

            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response = self.server._marshaled_dispatch(#pylint:disable-msg=W0212
                    data, getattr(self, '_dispatch', None)
                )
        except: # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            self.send_response(500)#pylint:disable-msg=W0702
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown(1)
    
