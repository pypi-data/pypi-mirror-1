"""Module providing main fog computing tools.

Generally, you should either use fogGUI.py or fogger.py if you just
want to run pyfog. See docs at http://code.google.com/p/superpy/wiki/PyFog
for how to run PyFog.
"""

import re, urllib, os, datetime, copy, logging, codecs
import feedparser, ignores
from superpy.core import Manager, Tasks, Servers, TaskInfo
from superpy.scripts import Spawn

class FogSource:
    """Abstract class representing input source for FogMachine.

    Subclasses should override GetWords as described in the docstring
    for GetWords to return a word frequency dictionary.
    """

    def __init__(self, config=None, traceDir=None):
        self.config = config
        self.traceDir = traceDir
        self.ignores = set(ignores.commonEnglish)

    def Run(self, config=None):
        """Return a dictionary representing word frequency from this source.

        This method shall be called with an instance of a FoggerConfig which
        can be None if the config was already provided previously.
        Otherwise, we set self.config to the given config.

        This method shall return a dictionary with string keys representing
        words or phrases and values of integers representing number of
        occurences in the given source.
        """
        
        raise NotImplementedError

    def Name(self):
        """Return string name for the source.

        This is used in tracking task names so each source INSTANCE should
        ideally have its own name.
        """
        
        raise NotImplementedError

    def Remoteable(self):
        """Return False if task should be run locally. Else return True.
        """

    def _GetWordsFromFD(self, config, fd):
        "Helper to read from file descriptor and call _GetWordsFromList"
        return self._GetWordsFromList(config, fd.read())

    def _GetWordsFromList(self, config, data):
        """Helper method to get words from a list and process them.
        
        INPUTS:
        
        -- config:        Instance of fogConfig.FoggerConfig containing
                          config information to use.      
        
        -- data:          List of strings representing data to count.
        
        -------------------------------------------------------
        
        RETURNS:        Dictionary of word/phrase counts.
        
        """
        result = {}
        phraseLevel = config.session.phraseLevel
        preKillData = None
        try:
            preKillData = str(codecs.encode(data, 'ascii', 'replace'))
        except Exception, e:
            logging.warning(
                "Can't decode data via codecs due to exception %s; retrying" %
                (str(e)[0:256]))
        if (preKillData is None):
            preKillData = unicode(data, errors='replace').encode(
                'ascii','ignore')
        data = re.sub(config.session.killRegexp,'',preKillData)
        if (self.traceDir is not None):
            fileName = os.path.join(self.traceDir, re.sub(
                '[^a-zA-Z0-9.]','_',self.Name()+'_preKill.txt'))
            open(fileName, 'wb').write(preKillData)
            fileName = os.path.join(self.traceDir, re.sub(
                '[^a-zA-Z0-9.]','_',self.Name()+'_postKill.txt'))
            open(fileName, 'wb').write(data)
        data = data.split()
        for i in range(phraseLevel,len(data)):
            wordList = [w.lower() for w in data[(i-phraseLevel):i]]
            wordList = [w for w in wordList if w not in self.ignores]
            word = ' '.join(wordList)
            if (word.strip() == ''):
                pass
            elif (word in result):
                result[word] += 1
            else:
                result[word] = 1
        return result
    

class WebSource(FogSource):
    """FogSource to read data from a web site.
    """

    def __init__(self, url):
        FogSource.__init__(self)
        self.url = url

    def Remoteable(self):
        "Return True so this can be run remotely."
        return True

    def Run(self, config=None):
        "Override as required by FogSource."
        try:
            if (config is None):
                config = self.config
            opener = urllib.FancyURLopener({})
            fd = opener.open(self.url)
            result = self._GetWordsFromFD(config, fd)
        except Exception, e:
            logging.error('Got exception in fogMaker.py processing %s:\n%s\n'
                          % (self.Name(), e))
            raise
        return result

    def Name(self):
        "Return name based on url"
        return '%s::%s' % (self.__class__.__name__, self.url)

class RssSource(FogSource):
    """FogSource to read data from an RSS feed.
    """

    def __init__(self, url):
        FogSource.__init__(self)
        self.url = url

    def Remoteable(self):
        "Return True so this can be run remotely."
        return True

    def Run(self, config=None):
        "Override as required by FogSource."
        try:
            if (config is None):
                config = self.config
            info = feedparser.parse(self.url)
            if (info['bozo']):
                msg = 'RSS feed for %s is malformed; skipping.' % self.url
                logging.error(msg)
            data = []
            for e in info['entries']:
                data.extend([
                    e.title,
                    e.summary 
                    ])
            result = self._GetWordsFromList(self.config, '\n'.join(data))
        except Exception, e:
            logging.error('Got exception in fogMaker.py processing %s:\n%s\n'
                          % (self.Name(), e))
            raise
        return result

    def Name(self):
        "Return name based on url"
        return '%s::%s' % (self.__class__.__name__, self.url)


class FileSource(FogSource):
    """FogSource taking input from an existing file.
    """

    def __init__(self, fileName, remoteable=False):
        FogSource.__init__(self)
        self.fileName = fileName
        self.remoteable = remoteable

    def Remoteable(self):
        "Return whether this is remoteable or not."
        return self.remoteable

    def Name(self):
        "Return name based on file"
        return '%s::%s' % (self.__class__.__name__, self.fileName)

    def Run(self, config=None):
        """Override as required by FogSource.
        """
        if (config is None):
            config = self.config
        fd = open(self.fileName,'r')
        return self._GetWordsFromFD(config, fd)

class FogMachine:
    """Class to create a word fog from many input sources.
    """

    def __init__(self, config, sources=(),):
        self.wordCount = {}
        self.sources = list(sources)
        self.config = config
        self.scheduler = self._MakeTaskScheduler(
            self.config.superpy.serverList, self.config.superpy.localServers)
        self._AddSourcesFromConfig()

    def _AddSourcesFromConfig(self):
        """Look at self.config and add any sourcs listed there.
        """
        if (self.config.session.webSourceFile not in ['', 'None', None]):
            sites = open(self.config.session.webSourceFile).read().split('\n')
            for s in sites:
                if (s.strip() != '' and len(s) and s[0]!='#'):
                    logging.debug('Adding source for %s from config file.'%s)
                    self.AddSource(WebSource(s))
        if (self.config.session.rssSourceFile not in ['', 'None', None]):
            sites = open(self.config.session.rssSourceFile).read().split('\n')
            for s in sites:
                if (s.strip() != ''):
                    logging.debug('Adding source for %s from config file.'%s)
                    self.AddSource(RssSource(s))                    

    def Reset(self):
        """Reset state of FogMachine so you can run it again.
        """
        self.wordCount = {}

    def AddSource(self, source):
        """Add a new source to pull data from.
        
        INPUTS:
        
        -- source:        Instance of FogSource.
        
        -------------------------------------------------------
        
        PURPOSE:        Tells FogMachine to add given source to list of sources
                        to analyze.
        
        """
        if (not isinstance(source, FogSource)):
            raise TypeError('FogMachine.AddSource excepts a FogSource; got %s'
                            % str(source))
        self.sources.append(source)

    def CountWords(self):
        """Count words in all sources.
        
        -------------------------------------------------------
        
        RETURNS:      Dictionary of word frequencies extracted from all
                      sources.
        
        -------------------------------------------------------
        
        PURPOSE:      Count the words in all sources.
        
        """
        self.wordCount = {}
        Manager.ProcessElements(
            self.sources, Manager.DoNothing, lambda e: self.DispatchElement(e),
            lambda e,r: self.ProcessResult(e,r))
        return self.wordCount

    def ProcessResult(self, element, result):
        """Take a FogSource and the result of running it and process it.
        
        INPUTS:
        
        -- element:        FogSource that we have run.
        
        -- result:         Results of running element.
        
        -------------------------------------------------------
        
        PURPOSE:        Update self.wordCount based on given result.
        
        """
        
        if (not isinstance(result, dict)):
            logging.error('''
            Got invalid result for element %s. Expected dict, got %s.
            Will ignore element %s and continue.''' % (
                element.Name(), result, element.Name()))
        else:
            wordCount = self.wordCount
            for (k, v) in result.items():
                if (k not in wordCount):
                    wordCount[k] = 0
                    wordCount[k] += v

    @staticmethod
    def _MakeTaskScheduler(serverList, localServers):
        """Make a task scheduler to submit superpy tasks to.

        INPUTS:

        -- serverList:  List of (host, port) pairs for existing servers.

        -- localServers: Integer for how many local servers to start.
        
        -------------------------------------------------------
        
        RETURNS:        A superpy.core.Servers.Scheduler instance including
                        all servers in serverList and locally started ones.
        
        -------------------------------------------------------
        
        PURPOSE:        This method creates a scheduler which knows about
                        all the superpy servers given and can
                        be used to submit tasks to them.
        
        """
        serverList = copy.deepcopy(serverList)
        if (serverList is None):
            serverList = []
        if (not isinstance(serverList,(list,tuple))):
            raise TypeError('serverList must be a sequence but got %s' % (
                str(serverList)))
        for _servNum in range(localServers):
            localServer = Spawn.SpawnServer(0, daemon=True, logRequests=False)
            serverList.append((localServer.Host(),localServer.Port()))
            logging.info('Spawned local server at %s.' % str(serverList[-1]))
        scheduler = Servers.Scheduler(serverList)
        return scheduler


    def _MakeTaskToRunSource(self, source):
        """Helper method to create superpy task to run the given FogSource.
        """
        workingDir = self.config.superpy.remoteWorkDir
        if (workingDir in ['', 'None', None]):
            os.path.normpath(os.getcwd())
        task = Tasks.ImpersonatingTask(
            targetTask=source,
            workingDir=workingDir,
            domain=self.config.superpy.domain,
            password=self.config.superpy.password,
            user=self.config.superpy.user,
            prependPaths=[self.config.superpy.remotePyPath.replace('\\','/')],
            name='RemoteTest/pyfog/%s/%s/%s' % (
            datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'),
            self.config.superpy.user, source.Name()),
            mode='createProcess',
            env={'USERNAME' : os.getenv('USER', os.getenv('USERNAME', None))},
            wrapTask=True)
        task.targetTask.pickleMode = 'h'
        return task


    def DispatchElement(self, element):
        """Dispatch a FogSource to as required by superpy.core.Manager.
        """
        if (element.config is None):
            element.config = self.config

        if (element.Remoteable()):
            task = self._MakeTaskToRunSource(element)
            handle = self.scheduler.SubmitTaskToBestServer(task)
        else:
            result = element.Run()
            now = datetime.datetime.now()
            handle = TaskInfo.StaticHandle(element.Name(), {
                'starttime' : now,
                'endtime' : now + datetime.timedelta(seconds=1),
                'alive' : False,
                'host' : 'localhost',
                'port' : 0,
                'mode' : 'finished',
                'result' : result,
                'pids' : []
                })
        return handle
    
    def MakeRankedResultList(self, numWords):
        """Helper method to make ranked list of results.
        
        INPUTS:
        
        -- numWords:        Maximum number of words to show data for.
        
        -------------------------------------------------------
        
        RETURNS:        Results or processing given soures formatted
                        as string showing a table of results.
        
        -------------------------------------------------------
        
        PURPOSE:        Helper for MakeFog to make main output data.
        
        """
        if (not len(self.wordCount)):
            self.wordCount = self.CountWords()

        total = float(sum(self.wordCount.values()))
        sortedCounts = list(reversed(sorted(
            self.wordCount.items(), key=lambda pair:pair[1])))

        result = ['Word'.ljust(33) + 'hits'.ljust(13) + '%'.ljust(10)]
        result.extend(
            [word.ljust(33) + ('%i'%count).ljust(13) +
             ('%.5f%%'%(count/total*100.0))
             for (word, count) in sortedCounts[0:numWords]])
        
        return '\n'.join(result)

    def MakeFog(self):
        """Top level method to process data and return result.
        """
        outputFile = self.config.session.outputFile
        result = self.MakeRankedResultList(self.config.session.maxWords)
        if (outputFile in ['', 'None', None]):
            return result
        else:
            open(outputFile,'wb').write(result)
        
        
    @staticmethod
    def _regr_test_simple():
        """Simple regression test for FogMachine.

>>> import os, shutil, tempfile, inspect, sys, logging
>>> logging.getLogger('').setLevel(logging.DEBUG)
>>> netPyPath = os.path.abspath(os.getcwd() + '../../..')
>>> if (os.name == 'nt'):
...     import win32net
...     drive, path = os.path.splitdrive(netPyPath)
...     drive = win32net.NetUseGetInfo(None, drive, 0)['remote']
...     netPyPath = drive + path
... 
>>> netPyPath = netPyPath.replace('%c'%92,'%c'%47)#replace \ with /
>>> sys.path.insert(0, netPyPath)
>>> from superpy.demos.pyfog import fogMaker, fogConfig
>>> myDir = tempfile.mkdtemp(suffix='_fogTest')
>>> fd, webFile = tempfile.mkstemp(dir=myDir,suffix='_web.txt')
>>> _ignore = os.write(fd,'''
... http://www.mit.edu/~emin/short_bio.html
... ''')
>>> os.close(fd)
>>> fd, outFile = tempfile.mkstemp(dir=myDir,suffix='_output.txt')
>>> os.close(fd)
>>> fd, confFile = tempfile.mkstemp(dir=myDir,suffix='_fogConf.txt')
>>> user = os.getenv('USER', os.getenv('USERNAME', 'unknown'))
>>> _ignore = os.write(fd, '''
... logLevel=DEBUG
... maxWords=3
... phraseLevel=1
... webSourceFile=%s
... remotePyPath=%s
... #If using some remote servers running as different usernames, you
... #will need to provide username and password info.
... #user=FIXME
... #domain=FIXME
... #password=FIXME
... ''' % (webFile, netPyPath))
>>> os.close(fd)
>>> fd, sourceFile = tempfile.mkstemp(dir=myDir,suffix='_sourceData.txt')
>>> _ignore = os.write(fd, inspect.getsource(fogConfig))
>>> os.close(fd)
>>> sys.argv = [''] # clear argv so config parsing does not get confused.
>>> myConf = fogConfig.FoggerConfig(configFile=confFile)
>>> myConf.Validate()
>>> maker = fogMaker.FogMachine(myConf)
Entering service loop forever or until killed...
Entering service loop forever or until killed...
Entering service loop forever or until killed...
Entering service loop forever or until killed...
>>> maker.AddSource(fogMaker.FileSource(sourceFile))
>>> maker.AddSource(fogMaker.WebSource(
... 'http://www.mit.edu/~emin/long_bio.html'))
>>> print maker.MakeFog() #doctest: +ELLIPSIS
Word                             hits         %         
def                              36           2...%
none                             30           2...%
name                             26           2...%
>>> shutil.rmtree(myDir)
>>> os.path.exists(myDir)
False
        """

def _test():
    "Test docstrings"
    import doctest
    doctest.testmod()

if __name__ == "__main__":    
    _test()
    print 'Test finished.'
            
