"""The superpy module provides super-computing for python.

The superpy package allows you to distribute python programs across a
cluster of machines or across multiple processers on a single
machine. This is a coarse-grained form of parallelism in the sense
that remote tasks generally run in separate processes and do not share
memory with the caller.

What makes superpy different than the many other excellent parallel
processing packages already available for python? The superpy package
is designed to allow sending jobs across a large number of machines
(both Windows and LINUX). This requires the ability to monitor, debug,
and otherwise get information about the status of jobs. Such job
control features (and Windows support) was not widely available in
other packages at the time superpy was created.

Some key features of superpy include:

 * Send tasks to remote servers or to same machine via XML RPC call
 * GUI to launch, monitor, and kill remote tasks
   * GUI can automatically launch tasks every day, hour, etc.
 * Works on the Microsoft Windows operating system
   * Can run as a windows service
   * Jobs submitted to windows can run as submitting user or as service
 * Inputs/outputs are python objects via python pickle
 * Pure python implementation
 * Supports simple load-balancing to send tasks to best servers 

The following provides a simple example to show how superpy can be
used in practice.

   First you would generally use the Spawn script on various machines to
   spawn superpy servers. Better yet would be to setup a windows
   service or similar script to make superpy spawn servers
   automatically. To illustrate this in a doctest, we import the
   Spawn script and call the SpawnServer function directly to setup
   a few servers. (Note that usually you would only do this once or
   not even have to do it at all if your servers start automatically
   as services).
   
>>> from superpy.scripts import Spawn
>>> try:
...     server1 = Spawn.SpawnServer(0, daemon=True) #doctest: +ELLIPSIS
...     server2 = Spawn.SpawnServer(0, daemon=True) #doctest: +ELLIPSIS
...     import time; time.sleep(3) # wait for servers to start
...     # The sleep is only necessary for doctest verfication .
... except Exception, e:
...     raise
Entering service loop forever or until killed...
Entering service loop forever or until killed...
    
    Next we instantiate an instance of the scheduler class and tell it
    about the servers we have instantiated:

>>> from superpy.core import Servers
>>> myServers = [
... (server1._host,server1._port),(server2._host,server2._port)]
>>> s = Servers.Scheduler(myServers)

    Now we can submit tasks to the servers. The tasks can represent
    pretty much anything you want to do in python. The only real
    constraint is that since we use pickle, the tasks must be
    unpickleable on the remote machine. This basically means that
    tasks must be objects in modules the remote machine can see. For
    this example, we use the example in Process._ExampleForTest, but
    you can easily create your own tasks by simply providing an object
    with a run method.

>>> import os
>>> from superpy.core import Tasks, Process
>>> target = Process._ExampleForTest(  # create an example task with delay
... func=sum,args=[[1,2,3],5],delay=10)# of 10 to illustate timeout
>>> task = Tasks.ImpersonatingTask(
... name='example',targetTask=target,workingDir=os.getcwd())
>>> handle = s.SubmitTaskToBestServer(task)
>>> time.sleep(1) # give task a chance to get started
>>> handle = handle.UpdatedHandle(timeout=3) # Try to quickly get update.
>>> # The above should get a handle showing tasks status as not finished.
>>> print handle # doctest: +ELLIPSIS
TaskHandle(
    name='example',
    started=True,
    finished=False,
    alive=True,
    host='...',
    port=...,
    result=None,
    starttime=datetime.datetime(...),
    endtime=None,
    user='...',
    taskRepr="ImpersonatingTask(...)",
    pids=[...])
<BLANKLINE>
>>> handle = handle.WaitForUpdatedHandle(60) # wait for task to finish
>>> print handle.result # show result
11
>>> handle.Cleanup() # cleans task out of server queue

"""


def _test():
    "Test docstrings in module"
    import doctest
    doctest.testmod()
    
if __name__ == '__main__':
    _test()
    print 'Test finished.'
