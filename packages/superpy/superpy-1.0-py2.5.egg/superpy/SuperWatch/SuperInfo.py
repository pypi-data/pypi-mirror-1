"""Module providing useful ways of getting information about superpy cluster
"""

import re, logging, threading, datetime

def SearchForTasks(scheduler, hostRE='.', portRE='.', taskRE='.',
                   threaded=True,idle=None):
    """Search for desired tasks.

    INPUTS:

    -- scheduler:     Instance of a superpy scheduler holding info on
                      which host/port superpy servers are running on.  

    -- hostRE:        String regular expression for hosts to search.

    -- portRE:        String regular expression for ports to search.

    -- taskRE:        String regular expression for tasks to search.

    -- threaded=True: If True, use separate threads to contact superpy
                      servers in parallel (this is faster than contacting
                      sequentially).

    -------------------------------------------------------

    RETURNS:        List of handles to tasks matching given criteria.

    -------------------------------------------------------

    PURPOSE:        Go through all tasks which match the given regular
                    expressions. This is useful for other commands that
                    want to do something to a subset of tasks.

    """
    if (idle is None): idle = lambda : None
    hostRE = re.compile(hostRE)
    portRE = re.compile(portRE)
    taskRE = re.compile(taskRE)

    myThreads, msg = [], []
    if (scheduler is None):
        return [], '\n'.join(msg)
    for (host, port) in sorted(scheduler.hosts):
        msg.append('\n\n********\n\n%s:%s ::\n    ' % (host, port))
        if (hostRE.search(host) and portRE.search(str(port))):
            myThreads.append(ShowHostQueue(scheduler,host,port,taskRE))
    if (threaded):
        for t in myThreads:
            t.start()
        pending = list(myThreads)
        while len(pending):
            oldPending, pending = pending, []
            for t in oldPending:
                if (t.isAlive()):
                    t.join(3)
                    logging.debug('idling for %s' % str(t))
                    idle()
                if (t.isAlive()):
                    pending.append(t)
            
        logging.debug('threads finished')
    else:
        for t in myThreads:
            t.run()
    tasks = sum([t.tasks for t in myThreads],[])
    msg = 'Searched the following servers to get tasks:\n' + '\n'.join(
        sum([t.msg for t in myThreads],[]))

    return tasks, msg

def MakeTaskDict(*searchArgs, **searchKW):
    """Call SearchForTasks and put results in a dictionary.

    INPUTS:

    -- *searchArgs, **searchKW: Args and keywords for SearchForTasks.

    -------------------------------------------------------

    RETURNS:        The pair (taskDict, msg) where taskDict is
                    a dictionary with taskDict[name] being a sub-dictionary
                    with keys of the form (host, port) and values of
                    tasks with given name running on given host, port.
                    The msg is the message returned by SearchForTasks.

    -------------------------------------------------------

    PURPOSE:        Create a dictionary of tasks for ease of processing.

    """
    allTasks, msg = SearchForTasks(*searchArgs, **searchKW)

    taskDict = {}
    for t in allTasks:
        name = t.Name()
        if (name not in taskDict):
            taskDict[name] = {}
        subDict = taskDict[name]
        if ((t.host, t.port) in subDict):
            raise Exception(
                'Got multiple tasks with same name, host, port:\n%s,%s,%s'
                % (name, t.host, t.port))
        subDict[(t.host, t.port)] = t
        
    return taskDict, msg


class ShowHostQueue(threading.Thread):
    """A thread to lookup information in a superpy host's queue.
    """

    def __init__(self, scheduler, host, port, taskRE, attempts=20, timeout=3):
        """Initializer.
        
        INPUTS:
        
        -- scheduler:  Servers.Scheduler object containing information about
                       superpy servers.
        
        -- host,port:  Which superpy server to contact.      
        
        -- taskRE:     String regular expression for task names.   
        
        -- attempts=20:  Attempts to make to contact server before giving up.
        
        -- timeout=3:    Timeout in each attempt on server.    
        
        """
        threading.Thread.__init__(self)
        self.scheduler = scheduler
        self.host = host
        self.port = port
        self.taskRE = taskRE
        self.attempts = attempts
        self.timeout = timeout
        self.msg = []
        self.tasks = []

    def run(self):
        """Try to get tasks on server maching self.taskRE.
        
        After completion, self.tasks contains a list of handles from the
        serrver and self.msg contains info on how we got the information.
        """
        try:
            for i in range(self.attempts):
                myTimeout = self.timeout
                logging.debug('Checking %s:%s (attempt %i), timeout=%f' % (
                    self.host, self.port, i, myTimeout))
                candidateTasks = self.scheduler.ShowQueue(
                    self.host, self.port, myTimeout)
                if (candidateTasks is None): # got timeout
                    logging.debug('Got timeout on attempt %i' % i)
                else:
                    break

            if (candidateTasks is None):
                self.msg.append(
                    'Unable to contact %s:%s in %s attempts. Ignoring' % (
                    self.host, self.port, self.attempts))
                logging.warning(self.msg[-1])
                candidateTasks = []
            found = [t for t in candidateTasks
                     if self.taskRE.search(t.Name())]
            self.msg.extend(['\n    ' + t.Name() for t in found])
            self.tasks.extend(found)
            logging.debug('Found %i tasks on %s:%s.' % (
                len(found), self.host, self.port))
        except Exception, e:
            errMsg = 'Error checking %s:%s: %s' % (self.host, self.port, str(e))
            logging.warning(errMsg)
            self.msg.append(errMsg)
            
        
def CleanTasks(scheduler, hostRE, portRE, taskRE, threshold):
    """Clean and remove desired tasks.

    INPUTS:

    -- scheduler:     Instance of a superpy scheduler holding info on
                      which host/port superpy servers are running on.  

    -- hostRE:        String regular expression for hosts to search.

    -- portRE:        String regular expression for ports to search.

    -- taskRE:        String regular expression for tasks to search.

    -- threshold:     Integer representing how many seconds old task
                      must be to get cleaned.

    -------------------------------------------------------

    RETURNS:        String message describing what we cleaned.

    -------------------------------------------------------

    PURPOSE:        Go through all tasks which match the given regular
                    expressions and have been finished for at least
                    threshold seconds and clean them up. This is useful
                    for getting rid of old tasks that have been finished.

    """
    threshold = datetime.timedelta(seconds=threshold)
    cleaned = []
    left = []
    allTasks, msg = SearchForTasks(scheduler, hostRE, portRE, taskRE)
    for task in allTasks:
        if (task.finished and (
            (datetime.datetime.now() - task.endtime) > threshold)):
            logging.info('Cleaning task:\n%s\n' % str(task))
            task.Cleanup()
            cleaned.append(task)
        else:
            left.append(task)

    msg = """
    Cleaned %i tasks:\n%s\n
    ************************************************************
    Left %i tasks:\n%s\n
    ************************************************************
    Search history was:\n%s\n
    """ % (len(cleaned), '\n'.join([t.Name() for t in cleaned]),
           len(left), '\n'.join(t.Name() for t in left), msg)
    return msg    

def RefreshInfo(scheduler, info, timeout=3, cache=None, idle=None):
    """Show status of task.

    INPUTS:

    -- scheduler:     Instance of a superpy scheduler holding info on
                      which host/port superpy servers are running on.  

    -- info:        TaskInfo instance representing task to show.

    -- timeout=3:   Optional timeout in seconds for how long to wait
                    to get status.

    -- cache=None:  Optional list of task handles matching info.name
                    (e.g., as returened by SearchForTasks or by
                    MakeTaskDict(...)[info.name]). If not provided, we
                    will lookup but this is useful to provide if you make lots
                    of calls in a row to avoid repeating the lookup.

    -------------------------------------------------------

    RETURNS:        String message indicating status of task.

    -------------------------------------------------------

    PURPOSE:        Provide a way to get status of task. This method
                    also modifies info to refresh its status.

    """
    if (isinstance(info.handle, (str, unicode))):
        raise Exception('Got unexpected string "%s" as info.handle.' % (
            info.handle))
    if (info.server.get() == '<local>' and info.handle is not None and
        not info.handle.StaleP()):
        msg = 'Updating handle for local task %s.' % info.name
        logging.debug(msg[0])
        info.handle = info.handle.UpdatedHandle(timeout=timeout)
        tasks = [info.handle]
    else:
        tasks, msg = [], ''

    if (cache is None):
        cache, _msg= SearchForTasks(scheduler, taskRE='^%s$' % info.name,
                                    idle=idle)

    tasks.extend(cache)
    
    if (len(tasks) == 0):
        info.Reset()
        msg += '''Task %s not running. Task status reset.''' % info.name
    elif (len(tasks) == 1):
        info.handle = tasks[0]
        info.SetFromHandle()
        msg += 'Handle info for task %s\n%s\n'%(info.name, info.handle.Pretty())
    else: # Found multiple tasks, this is not supposed to happen
        msg += _HandleMultipleTasks(tasks, info, msg)
        
    return msg

def _HandleMultipleTasks(tasks, info, msg):
    """Helper function to clean-up multiple tasks with same name/host/port.
    
    INPUTS:
    
    -- tasks:        List of task handles to cleanup.
    
    -- info:         Instance of SPWidgets.TaskInfo for task.
    
    -- msg:          String prefix for msg to return.
    
    -------------------------------------------------------
    
    RETURNS:    Message describe what happened.
    
    -------------------------------------------------------
    
    PURPOSE:    This fucntion finds duplicate task handles and tries to
                kill off finished tasks to remove duplicates.
    
    """
    msg += 'Found %i tasks for name %s:\n%s\n. Cleaning finished tasks.' % (
        len(tasks), info.name, '\n'.join([t.Pretty() for t in tasks]))
    killMsg, unfinished = KillMultipleTasks(tasks)
    msg += '\n' + killMsg + '\n'
    if (len(unfinished) == 0):
        msg += 'No live tasks left. Task status reset'
        info.Reset()
    elif (len(unfinished) == 1):
        msg +='Setting status to sole survivor %s.' % unfinished[0].Pretty()
        info.handle = unfinished[0]
        info.SetFromHandle()
    else:
        msg += msg + ('''
        Cannot show task when multiple live tasks exist for name %s.
        ''' % (info.name))
        logging.error(msg)
        raise Exception(msg)
    
    return msg


def KillMultipleTasks(tasks):
    """Kill list of tasks.
    
    INPUTS:
    
    -- tasks:   List of task handles.
    
    -------------------------------------------------------
    
    RETURNS:    The pair (msg, unfinished) where msg is a string
                describing what happened and unfinished is a list
                of tasks in the input which were not finished and
                therefore were not killed.
    
    -------------------------------------------------------
    
    PURPOSE:    Kills all finished tasks in the input tasks list.
    
    """
    msg, unfinished = [], []
    for t in tasks:
        status = t.StatusInfo()
        pretty = t.Pretty()
        if (status['mode'] == 'finished'):
            myMsg = 'Cleaning finished task %s.' % pretty
            t.Cleanup()
        else:
            unfinished.append(t)
            myMsg = 'Not cleaning unfinished task %s.' % pretty
        logging.info(myMsg)
        msg.append(myMsg)

    return '\n'.join(msg), unfinished
            
