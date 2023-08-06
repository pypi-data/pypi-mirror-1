"""Module to test some superpy stuff.
"""

import unittest, socket, time, logging, threading, re

from superpy.core import Tasks, Servers, PicklingXMLRPC

class TestScriptTaskInIsolation(unittest.TestCase):
    """Test to make sure the ScriptTask class works in isolation.
    """

    def setUp(self):
        "Prepare for testing."
        # set up a simple task
        self.task = Tasks.ScriptTask('echo hello',shell=True,sleepInterval=0.5,
                                     name='echoHelloIsolated')

    def testRun(self):
        "Do the test itself."
        self.task.Run()
        self.assertEqual(type(self.task.result),str)
        self.assertEqual('hello\n',self.task.result.replace('\r',''))

    def tearDown(self):
        "Cleanup after the test."
        pass

class BasicTest(unittest.TestCase):
    """Basic test case.

>>> import logging; logging.getLogger('').setLevel(logging.DEBUG)
>>> import _test
>>> classToTest = _test.BasicTest
>>> testNames = [n for n in dir(classToTest) if n[0:4]=='test']
>>> for name in testNames:
...     logging.debug('Testing %s' % name)
...     t = _test.BasicTest(methodName=name)
...     t.debug()
... 
Entering service loop forever or until killed...
Entering service loop forever or until killed...
Entering service loop forever or until killed...
Entering service loop forever or until killed...
Entering service loop forever or until killed...
    """

    # See docs in setUp for description of portIncrement
    portIncrement = 10

    def setUp(self):
        """Set up the test.

        Note that since the unittest module runs the different tests at
        unpredictable times, it is important to make sure that each time
        the setUp method is called, we use a different port.
        We also want to prevent these from conflicting with actual ports
        used by real users.
        """
        BasicTest.portIncrement += 1
        port = Servers.BasicRPCServer.defaultPort + BasicTest.portIncrement
        self.server = Servers.BasicRPCServer(cpus=1,port=port)
        self.server.serve_forever_as_thread()
        logging.debug('Starting server on port %i' % port)
        self.scheduler = Servers.Scheduler(
            [(socket.gethostname(),self.server._port)])
        
    def tearDown(self):
        "Shutdown the server after test is finished."
        
        logging.debug('Terminating server')
        self.server.Terminate()
        oldtimeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(5)        
        try: #poke the server to make sure it processes stuff
            connection = PicklingXMLRPC.PicklingServerProxy(
                'http://%s:%i' % (getattr(self.server,'_host'),
                                  getattr(self.server,'_port')))
            connection.system.listMethods()
        except Exception, e:
            #Not a big deal
            logging.error('Unable to contact server: %s; it probably shutdown'
                          % str(e))
        finally:
            socket.setdefaulttimeout(oldtimeout)

        time.sleep(1) # give everything time to shutdown
        self.assertEqual(False,getattr(self.server,'_thread').isAlive())
        self.assertEqual(1,threading.activeCount(),"""While running %s
        Some non-main threads still survive: %s""" % (
            self._testMethodName, str(threading.enumerate())))

        logging.debug('Finished teardown.')
        
    def testMain(self):
        "Main test to see if we can submit tasks."
        
        task = Tasks.ScriptTask('echo hello',shell=True,sleepInterval=0.5,
                                name='echohello')
        handle = self.scheduler.SubmitTaskToBestServer(task)
        handle = handle.WaitForUpdatedHandle()
        self.failUnless(handle.finished)
        self.assertEqual(type(handle.result),str)
        self.assertEqual('hello\n',handle.result.replace('\r','')[-6:])

    def testScript(self):
        "Another test to make sure we can submit script tests."
        
        task = Tasks.ScriptTask(command=None,contents='print "HI"',
                                name='printHi',shell=True,sleepInterval=0.5)
        handle = self.scheduler.SubmitTaskToBestServer(task)
        handle = handle.WaitForUpdatedHandle()
        self.assert_(isinstance(handle.result,(str,unicode)),
                     'result should be a string.')
        self.assertEqual('HI\n',handle.result.replace('\r','')[-3:])
                                
    def testErrorHandling(self):
        "Make sure the server can keep going despite task exceptions."

        task = Tasks.ScriptTask(command=None,contents='frooble # cause error',
                                name='causeError',shell=True,sleepInterval=0.5)
        handle = self.scheduler.SubmitTaskToBestServer(task)
        handle = handle.WaitForUpdatedHandle()

        self.failUnless(handle.finished)

        # Make sure error was caught
        self.failUnless(re.compile('Traceback').search(handle.result))

        # Make sure task is done
        self.assertEqual([True,True,False],[getattr(handle,n) for n in [
            'started','finished','alive']])

        # Make sure the server updated its cpu load properly
        self.assertEqual(-1,self.scheduler.hosts.values()[0].CPULoad())

    def testRemoveTask(self):
        "Make sure we can remove tasks."

        task = Tasks.ScriptTask(command=None,contents='while 1: pass\n',
                                name='loop',shell=True,sleepInterval=1)
        handle = self.scheduler.SubmitTaskToBestServer(task)
        connection = PicklingXMLRPC.PicklingServerProxy(
            'http://%s:%i' % (handle.host,handle.port))
        self.assertEqual(0,connection.CPULoad())        
        connection.RemoveFromQueue(handle)
        self.assertEqual(-1,connection.CPULoad())

    def testCleanOldTasks(self):
        "Test the CleanOldTasks method."

        task = Tasks.ScriptTask(command=None,contents='print "HI"',
                                name='printHi',shell=True,sleepInterval=0.5)
        handle = self.scheduler.SubmitTaskToBestServer(task)
        handle = handle.WaitForUpdatedHandle()            
        if (not handle.finished):
            raise Exception('Waited for handle but it did not finish.')
        self.assertEqual(type(handle.result),str)

        # Windows sometimes prints really stupid messages when you run
        # remote tasks. For example, it complains if you start processes
        # in a UNC path. The following assertion check ignores everything
        # except the last three characters to get around this stupidity.
        
        self.assertEqual('HI\n',handle.result.replace('\r','')[-3:])
        connection = PicklingXMLRPC.PicklingServerProxy(
            'http://%s:%i' % (handle.host,handle.port))
        time.sleep(2) # wait for task to finish
        cleaned = connection.CleanOldTasks(0)
        
        self.assertEqual(cleaned,['printHi']) #Make sure we cleaned the task
        self.assertEqual(connection.ShowQueue(),[]) #Make sure queue is empty


if __name__ == '__main__':
    import doctest; doctest.testmod()
        
