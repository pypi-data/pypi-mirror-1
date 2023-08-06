"""Module providing a client manager to help distribute tasks over superpy.
"""

import datetime, socket, logging, math, cPickle
import TaskInfo, Process, Tasks

class GenericElement:
    """Abstract class representing a generic element we can process in parallel.

    You can sub-class this to provide the Name and Run methods and then
    pass a list of GenericElement instances to SimpleElementProcessor
    which will handle processing them in parallel for you.
    """

    def __init__(self):
        pass

    def Name(self):
        """Return string name for element.
        
        Names should be unique enough that you can process a list of
        elements and not have a name conflict.
        """
        raise NotImplementedError

    def Run(self):
        """Run the task for this element and return a result if necessary.
        """
        raise NotImplementedError

class SimpleElementProcessor:
    """Class to handle processing a list of elements in parallel.

    The SimpleElementProcessor class handles the details of spawning a list
    of elements via superpy, collecting results when they finish, cleaning
    up, etc. This makes it more convenient to spawn a bunch of processes.

    The following example illustrates usage by spawning a group of
    ExampleElement instances and processing them in parallel. The ExampleElement
    class is just an example class that has a Run method to take the sqrt
    of its input argument at __init__ and a Name method to provide a name
    for each instance as required by GenericElement. In the example below
    we set scheduler = None for simplicity. Things still work in this case
    and are all run locally in sequence. You could provide an instance of
    superpy.core.Servers.Scheduler to spawn things in parallel.

>>> from superpy.core import Manager
>>> myElements = [Manager.ExampleElement(i) for i in range(4)]
>>> scheduler = None 
>>> processor = Manager.SimpleElementProcessor(
... scheduler, myElements, workingDir = 'c:/')
>>> processor.Process() #doctest: +ELLIPSIS
Running ExampleElement_0_... to get 0.0000
Running ExampleElement_1_... to get 1.0000
Running ExampleElement_2_... to get 1.4142
Running ExampleElement_3_... to get 1.7321
>>> print ','.join(['%.4f'%result for (_name, result) in processor.results])
0.0000,1.0000,1.4142,1.7321


    You can also create local servers to run things in parallel locally.
    This will be useful if you have multiple CPUs on your machine. Of
    course, you could easily adapt this example to multiple seperate
    machines as well by not spawning servers and instead providing the
    host:port data for existing superpy servers.

>>> from superpy.scripts import Spawn
>>> try:
...     server1 = Spawn.SpawnServer(0, daemon=True)
...     server2 = Spawn.SpawnServer(0, daemon=True)
...     import time; time.sleep(3) # wait for servers to start
...     # The sleep is only necessary for doctest verfication .
... except Exception, e:
...     raise
... 
Entering service loop forever or until killed...
Entering service loop forever or until killed...
>>> from superpy.core import Servers
>>> myServers = [
... (server1._host,server1._port),(server2._host,server2._port)]
>>> scheduler = Servers.Scheduler(myServers)
>>> myElements = [Manager.ExampleElement(i) for i in range(4)]
>>> processor = Manager.SimpleElementProcessor(
... scheduler, myElements, workingDir='c:/')
>>> processor.Process() #doctest: +ELLIPSIS
>>> print ','.join([
... '%.4f'%result for (_name, result) in sorted(processor.results)])
0.0000,1.0000,1.4142,1.7321
    """

    def __init__(self, scheduler, elementList, workingDir,
                 credentials=None):
        """Initializer.
        
        INPUTS:
        
        -- scheduler:  Instance of superpy.core.Servers.Scheduler representing
                       scheduler for how to distribute tasks to servers. If
                       None is provided, tasks will all be done locally.
        
        -- elementList:  List of GenericElement instances representing elements
                         we want to process remotely.

        -- workingDir:  String indicating path for working directory to use on
                        remote servers. This should be a network path or a
                        path that all remote servers can access.
        
        -- credentials=None:  Optional dictionary with keys 'domain',
                              'username', and 'password' that will be passed
                              into superpy.core.Tasks.ImpersonatingTask in
                              preparing task to run remotely.

        """
        self.scheduler = scheduler
        self.elementList = elementList
        self.results = []
        self.credentials = {} if credentials is None else dict(credentials)
        self.workingDir = workingDir

    def Process(self, procParams=None):
        """Main method to process tasks.
        
        INPUTS:
        
        -- procParams=None:   Optional instance of ProcParams class describing
                              how to do the processing.
        
        -------------------------------------------------------
        
        PURPOSE:        This method handles the work of doing the processing
                        of all elements in self.elementList. It works by
                        calling the ProcessElements function and passing
                        in self._DecorateElement, self._DispatchElement,
                        self._HandleResult and procArgs.
        
        """
        ProcessElements(self.elementList, self._DecorateElement,
                        self._DispatchElement, self._HandleResult, procParams)

    def _DecorateElement(self, element):
        """Decoreate element in preparation for dispatch it to be processed.
        
        INPUTS:
        
        -- element:        Input element to decorate.
        
        -------------------------------------------------------
        
        RETURNS:        A "decorated" element suitable for passing to a
                        dispatch function like self._DispatchElement. The
                        default version just returns element and does
                        nothing. Sub-classes may wish to override.
        
        -------------------------------------------------------
        
        PURPOSE:        Allowing decoration can be useful since it lets
                        you have a simple, compact list of elements that
                        later get packaged up right beforing dispatch.
        
        """
        _ignore = self
        return element
    
    def _HandleResult(self, decElement, result):
        """Handle the result of running a given element.
        
        INPUTS:
        
        -- decElement:        A decorated element that has been dispatched
                              and returned a result.  
        
        -- result:            Result of running decElement.
        
        -------------------------------------------------------
        
        PURPOSE:        Does the work to handle the result of processing
                        decElement. This can be something simple like
                        putting the result in a list which is what
                        the default version does. Sub-classes can override.
        """
        unpickled = cPickle.loads(result)
        self.results.append((decElement, unpickled))

    def _DispatchElement(self, element):
        """Dispatch a decorated element for processing.
        
        INPUTS:
        
        -- element:        A decorated element that we should dispatch
                           for processing.     
        
        -------------------------------------------------------
        
        RETURNS:        Instance of superpy.core.TaskInfo.GenericProcessHandle
                        representing dispatched task.
        
        -------------------------------------------------------
        
        PURPOSE:        This method dispatches an element for processing and
                        returns a handle. The handle can be used to keep track
                        of whether the task has finished, what its result is,
                        etc.

                        Sub-classes may override.
        
        """
        if (self.scheduler):
            logging.debug('Creating impersonating task for element %s' %
                          element.Name())
            impTask = Tasks.ImpersonatingTask(
                element, workingDir=self.workingDir, prependPaths=None,
                wrapTask=True, mode='createProcess', name=element.Name(),
                **self.credentials)
            handle = self.scheduler.SubmitTaskToBestServer(impTask)
            return handle
        else:
            logging.debug('Locally running element for %s' % element.Name())
            result = element.Run() #do it locally and return fake handle
            return TaskInfo.StaticHandle(element.Name(), {
                'result' : cPickle.dumps(result)})

class ExampleElement(GenericElement):
    """Example of GenericElement useful in doctests.
    """

    def __init__(self, target):
        GenericElement.__init__(self)
        self.target = target
        self.name = 'ExampleElement_%s_%s' % (target, datetime.datetime.now())

    def Name(self):
        "Return name"
        return self.name

    def Run(self):
        "Compute sqrt of self.target and return it."

        result = math.sqrt(self.target)
        print 'Running %s to get %.4f' % (self.Name(), result)
        return result

class TimeStampingElement(GenericElement):
    """Simple sub-class of GenericElement which provides a default Name method.

    This is intended to be a mix-in that you can inherit from if you want
    to define the Name element to just be class name plus a time stamp.
    """
    
    def __init__(self):
        GenericElement.__init__(self)

    def Name(self):
        "Return name based on class name and time stamp."
        return self.__class__.__name__ + '_' + datetime.datetime.now()

    def Run(self):
        "Sub-classes should override otherwise an exception is raised.."
        raise TypeError('Do not know what to do. Sub-classes must override Run')

class ProcParams:
    """Class containing parameters on how to do processing for ProcessElements.
    """

    def __init__(self, maxTime=0, maxUnfinished=4):
        """Initializer

        INPUTS:

        -- maxTime=0:       Optional integer representing maximum time to
                        allow an element to run (or 0 meaning no time limit).
                        Elements which have not finished in this amount
                        of time will be killed.

        -- maxUnfinished=4: Maxium number of unfinished elements to spawn at one
                        time. If this many elements have been spawned, we
                        wait for at least one to finish before spawning more.

        """
        self.maxTime = maxTime
        self.maxUnfinished = maxUnfinished


def ProcessElements(elements, decorateElement, dispatchElement, handleResult,
                    procParams=None):
    """Process elements in parallel.
    
    INPUTS:
    
    -- elements:        List of instances of GenericElement that we
                        want to process in parallel.

    -- decorateElement: A callable object that is given an element and
                        "decoreates" it to return a "decoreated element".
                        The decorating allows you to package up an element
                        into something suitable for dispatch at dispatch time.
                        By default you can pass in DoNothing if you have no
                        special decoration to do.
    
    -- dispatchElement: A callable object that can be called and given
                        a "decorated element" to process and will return
                        a handle.
    
    -- handleResult:    A callable object that can be called and given
                        a handle produced by dispatchElement and do
                        the appropriate thing with the result.

    -- procParams=None: Instance of ProcParams class describing how to
                        do the processing.
        
    -------------------------------------------------------
    
    PURPOSE:    This function provides a simple way to take a list of elements
                and process them with whatever superpy servers you have
                available. This function handles issues like spawning each
                element in a new task, waiting for them to finish, etc.
    
    """
    if (procParams is None): procParams = ProcParams()
    unfinishedHandles = []
    numElements = len(elements)
    elementNum = 0
    while (elementNum < numElements):
        element = elements[elementNum]
        decoratedElement = decorateElement(element)
        handle = dispatchElement(decoratedElement)
        unfinishedHandles.append((handle, decoratedElement))
        elementNum += 1
        untilFinished = None if (len(unfinishedHandles) <
                                 procParams.maxUnfinished) else 1
        finishedHandles, unfinishedHandles = WaitForTasks(
            unfinishedHandles, untilFinished=untilFinished,
            maxTime=procParams.maxTime)
        CleanupFinishedHandles(finishedHandles, handleResult)
    finishedHandles, unfinishedHandles = WaitForTasks(
        unfinishedHandles, untilFinished=len(unfinishedHandles))
    CleanupFinishedHandles(finishedHandles, handleResult)



def WaitForTasks(handles, untilFinished=None, maxTime=0, handleException=None):
    """Wait for tasks to finish.

    INPUTS:

    -- handles:        List of pairs of the form (handle, element) where
                       handle is a handle to a task that is not finished
                       yet and element is the underlying task element.

    -- untilFinished=None:        Either None or an integer indicating
                                  how man tasks must finish before we
                                  stop waiting.

    -- maxTime=0:   Max time to allow for a test (0 means infinite).

    -- handleException=None:    Optional callable object that can be called as
                                handleException(handle, element, exception).
                                This will be called whenever we get an
                                exception waiting for a task.

    -------------------------------------------------------

    RETURNS:        The pair of lists (finishedHandles, unfinishedHandles)
                    representing tasks that finished or may not yet be
                    finished. Each is a list of pairs of the form
                    (handle, element) like the input.

    -------------------------------------------------------

    PURPOSE:        Takes a list of taskHandles, periodically checking if
                    some or all are finished. When all tasks are
                    done, return a list of handles to the finished
                    tasks. 
    """
    numHandles = len(handles)    
    if (handleException is None):
        handleException = lambda _h, _el, exc: logging.debug(
            'Ignoring exception %s' % str(exc))
        
    threshold = datetime.datetime.now() + datetime.timedelta(maxTime)
    finishedHandles, tempHandles = [], []
    keepGoing = True
    while(keepGoing):
        tempHandles = []
        for (handle, element) in handles:
            newHandle = None
            try:
                oldInfo = handle.StatusInfo()                
                newHandle = handle.UpdatedHandle(timeout = 3)
                info = newHandle.StatusInfo()
                if (info['mode'] == 'finished'):
                    finishedHandles.append((newHandle, element))
                elif (maxTime and newHandle.started and
                      info['starttime'] > threshold):
                    logging.warning('Timeout exceeded; killing task %s'
                                    % str(newHandle))
                    newHandle.Kill()
                    # put back in tempHandles so we clean it up later
                    tempHandles.append((newHandle, element))
                else:
                    tempHandles.append((newHandle, element))
            except socket.error, e:
                logging.warning("""
                Got exception: %s while waiting for task:\n%s
                Will assume task has same status as before and
                continue.""" % (str(e), str(handle)))
                tempHandles.append((handle, element))
            except Exception, e:
                handleInfo = 'unknown'
                try:
                    handleInfo = str(handle)
                except Exception, eAgain:
                    logging.error(
                        'Could not show handle info due to exception:%s'
                        % str(eAgain))
                logging.error("Got exception: %s while waiting for task:\n%s"
                              % (str(e), str(handleInfo)))
                handleException(handle, element, e)
                oldInfo['result'] = 'Got Exception in WaitForTasks: %s'%str(e)
                handle = TaskInfo.InvalidHandle(element.Name(), oldInfo)
                finishedHandles.append((handle, element))

        handles = tempHandles
        keepGoing = (len(handles) > 0 and (
            untilFinished is not None and len(finishedHandles) < untilFinished))
    assert len(finishedHandles)+len(tempHandles) == numHandles
        
    return finishedHandles, tempHandles

def CleanupFinishedHandles(finishedHandles, handleResult):
    """Cleanup handles that have finished running.

    INPUTS:

    -- finishedHandles:        List of pairs for the form (handle, element)
                               representing handles for finished tasks
                               and the corresponding test plan elements.

    -- handleResult:           Function which takes an element and the
                               corresponding result obtained by running the
                               task and processes that in an appropriate
                               manner.

    -------------------------------------------------------

    PURPOSE:        Remove finished tasks from queue of servers.

    """
    for (h, element) in finishedHandles:
        info = h.StatusInfo()
        theResult = info['result']
        if (isinstance(theResult, Process.PickleHolder)):
            theResult = theResult.Extract()

        handleResult(element, theResult)
        try:
            h.Cleanup()
        except Exception, e:
            logging.warning('Unable to clean handle %s because %s' % (
                str(h), str(e)))

def DoNothing(arg):
    "Reutrn input arg without doing anything."
    return arg


def _test():
    "Test module"
    import doctest
    doctest.testmod()
    
if __name__ == '__main__':
    _test()
    print 'Test finished.'
