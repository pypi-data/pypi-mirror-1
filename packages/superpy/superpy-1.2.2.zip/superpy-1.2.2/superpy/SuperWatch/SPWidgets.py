"""Module providing widgets for SuperWatch.
"""

import Tkinter
import Pmw
import csv, datetime, logging, os, traceback, sys, threading, time, smtplib

import GUIValidators, GUIUtils, Periodicity, SuperInfo, MsgWindow
from superpy.core import Servers, Tasks

class HelperPage:
    """Abstract class for pages of the master monitor notebook.

    Each page in the MasterMonitor is represented by a HelperPage.
    Sub-classes should override MakeFrame to create things they need.
    """

    def __init__(self, master, name):
        """Initializer.
        
        INPUTS:
        
        -- master:     MasterMonitor object holding this page.   
        
        -- name:       String name of this item. 
        
        PURPOSE:
        
        """
        self.name = name
        self.master = master
        self.frame = None     #Gets set by self.MakeFrame.

    def Help(self):
        """Return string providing help for page.
        """
        return self.__class__.__doc__

    def MakeFrame(self, notebook):
        """Create the frame for this object in the given notebook.
        
        INPUTS:
        
        -- notebook:        Instance of Pmw.NoteBook which will hold self.
        
        -------------------------------------------------------
        
        PURPOSE:        Create page for self in the notebook.
        
        """
        page = notebook.add(self.name)
        self.frame = getattr(Pmw,'ScrolledFrame')(
            page, labelpos='n', horizflex='expand', vertflex='expand')
        self.frame.pack(expand=1,fill='both')
        self.frame = self.frame.interior()

class ConfigPage(HelperPage):
    """The Config page allows the user to setup various configuration parameters

    Many of these parameters take effect immediately. To make sure to apply
    all configuration changes (especially things like loading scripts
    ans servers) click the Apply button.
    """

    def __init__(self, master, defaults):
        HelperPage.__init__(self, master, name='Config')
        self.defaults = defaults
        self.confItemDict = None

    def MakeFrame(self, notebook):
        "Make the frame as expected by HelperPage.MakeFrame."
        
        HelperPage.MakeFrame(self, notebook)
        self._MakeConfigPage()

    def _MakeConfigPage(self):
        """Make config page in GUI
        """
        defaults = self.defaults
        argFrame = Tkinter.Frame(self.frame)
        buttonFrame = Tkinter.Frame(self.frame)

        confItems = [
            ('enableAutoRun', EnableScripts(argFrame)),
            ('servers', ServerConfItem(argFrame)),
            ('smtp', SMTPConfItem(argFrame)),
            ('scripts', ScriptConfItem(argFrame)),
            ('logLevel', LogConfItem(argFrame)),
            ('pollFrequency', PollFrequency(argFrame)),
            ('majorPollFrequency', MajorPollFrequency(argFrame)),
            ('autoClean', AutoCleanConfItem(argFrame)),
            ('domain', DomainConfItem(argFrame)),
            ('user', UserConfItem(argFrame)),
            ('password', PasswordConfItem(argFrame)),
                     ]

        button = Tkinter.Button(
            buttonFrame, text='Apply', command=GUIUtils.GenericGUICommand(
            'ApplyConfig', lambda : [
            item.Apply(self.master) for (_name, item) in confItems]))
        button.pack(side='left',fill='x',expand=1)
        buttonFrame.pack(side='bottom',fill='x',expand=0)
        argFrame.pack(side='top',fill='both',expand=1)

        self.confItemDict = dict(confItems)
        for (name, value) in defaults.items():
            if (name not in self.confItemDict):
                raise Exception(
                    'Invalid default item "%s". Possible values are:\n%s'
                    % (name, '\n'.join(sorted(self.confItemDict))))
            else:
                self.confItemDict[name].entry.set(value)

class TaskPage(HelperPage):
    """Page listing subset of tasks running via superpy.

    These tasks are added using Actions-->Import. The purpose of these
    tasks is to let you monitor what the tasks are doing.

    See the Actions menu for other useful commands.
    """

    def __init__(self, master):
        HelperPage.__init__(self, master, name='Tasks')
        self.commands = {}

    def MakeFrame(self, notebook):
        "Make the frame as expected by HelperPage.MakeFrame."
        
        HelperPage.MakeFrame(self, notebook)
        self._MakeTaskFrameMenu()

    def _MakeTaskFrameMenu(self):
        """Make frame for the task menu.

        This frame shows the menu for the 'Tasks' page.
        """
        master = self.master
        frame = self.frame
        menuButtonFrame = Tkinter.Frame(frame, name='menuFrame')
        menuButton = Tkinter.Menubutton(menuButtonFrame)
        menu = Tkinter.Menu(menuButton, tearoff=0)
        menuButton.configure(menu=menu)
        menuButton.configure(text='Actions')
        menu.add_command(label='ImportTasks',command=ImportTasksCmd(
            master, '.', '.', '.'))
        menu.add_command(label='CleanTasks',command=CleanTasksCmd(
            master, '.', '.', '.', master.GetParam('autoClean')))
        menuButton.pack(side='top',fill='x',expand=1)
        menuButtonFrame.pack(side='top',expand=0,fill='x')        

    def MakeTaskFrameItems(self, allTasks):
        """Put items representing tasks into self.frame
        
        INPUTS:
        
        -- allTasks:        List of TaskInfo instances representing
                            tasks to show in self.frame frame.
        
        -------------------------------------------------------
        
        PURPOSE:        This method redraws the Tasks frame to contain
                        new tasks.
        
        """

        self.commands = {} # forget all previous task commands
        frame = self.frame
        if ('itemFrame' in frame.children):
            frame.children['itemFrame'].destroy()

        headers = ['name', 'action', 'server', 'status', 'started', 'finished',
                   'autoRunAt']
        hColDict = dict([(h, c) for (c, h) in enumerate(headers)])
        mainFrame = Tkinter.Frame(frame, name='itemFrame')
        for h in headers:
            Tkinter.Label(mainFrame,text=h).grid(row=0,column=hColDict[h])
        for (row, task) in enumerate(allTasks):
            server = '%s:%s' % (task.host, task.port)
            info = self.master.MakeTaskItems(
                mainFrame, task.Name(),[server], server, None)
            if (task.Name() not in self.commands):
                self.commands[task.Name()] = {}
            self.commands[task.Name()][server] = info
            for (name, item) in info.itemList:
                item.grid(row=row+1, column=hColDict[name])
                
            info.server.set(server)
            info.SetFromHandle(task)

        mainFrame.pack(side='top',expand=1,fill='both')
        logging.debug('Finished packing task frame items.')        

    def Kill(self, info):
        """Kill a task.
        
        INPUTS:

        -- info:        TaskInfo instance representing task to launch.        

        -------------------------------------------------------
        
        PURPOSE:        Kill a task. Things pretty much only works for
                        tasks which are finished since we don't yet support
                        killing running tasks.
        
        """
        _ignore = self
        if (info.status.get() == 'unknown'):
            raise Exception(
                'Task "%s" not connected. Try Show or Launch first.'
                % info.name)
        else:
            info.handle = info.handle.UpdatedHandle(timeout=3)
            if (info.handle.StatusInfo()['alive']):
                info.handle.Kill()
            else:
                info.handle.Cleanup()
            info.SetFromHandle(status='cleaned')                

    def KillAndReset(self, info):
        """Kill a task and reset its status if possible.
        
        INPUTS:
        
        -- info:        TaskInfo instance representing task to launch.
        
        -------------------------------------------------------
        
        PURPOSE:        Kill a task like in self.Kill but then try to
                        reset its status if possible. This is useful
                        in cleaning things up so it can auto-run again.
        
        """
        _ignore = self        
        if (info.status.get() == 'unknown'):
            raise Exception(
                'Task "%s" not connected. Try Show or Launch first.'
                % info.name)
        else:
            info.handle = info.handle.UpdatedHandle(timeout=3)
            if (info.handle.StatusInfo()['alive']):
                info.handle.Kill()
            else:
                info.handle.Cleanup()
            info.server.set(info.defaultServer)
            info.SetFromHandle(status='cleaned')

class ScriptPage(HelperPage):
    """Page showing scripts user has loaded.

    This page lets you launch scripts.
    """

    def __init__(self, master):
        HelperPage.__init__(self, master, name='Scripts')        
        self.commands = {}
        self.scriptDict = {}

    def MakeFrame(self, notebook):
        "Make the frame as expected by HelperPage.MakeFrame."
        
        HelperPage.MakeFrame(self, notebook)

    def ReloadScripts(self, scriptFile):
        """Reload scripts into Scripts page.
        
        INPUTS:
        
        -- scriptFile:        String path to file containing scripts.
        
        -------------------------------------------------------
        
        PURPOSE:        Load all the scripts into the Scripts page.
        
        """
        scripts = self._ParseScriptFile(scriptFile)
        self.scriptDict = dict(scripts)
        self._AddScriptsToNotebook(scripts)

    @staticmethod
    def _ParseScriptFile(scriptFile):
        """Parse a script file to extract scripts.
        
        INPUTS:
        
        -- scriptFile:        String path to script file.
        
        -------------------------------------------------------
        
        RETURNS:        List of lists representing scripts parsed from file.
        
        -------------------------------------------------------
        
        PURPOSE:        This method reads a file and extracts desired scripts.
                        See docs for ScriptConfItem for format for scriptFile.
        
        """
        varDict = {
            'user' : os.getenv('USER', os.getenv('USERNAME', 'unknown')),
            'cwd'  : os.getcwd()
            }
        varDict.update(os.environ)
        scripts = []
        headers = ['scriptName', 'scriptFile', 'autoRunAt', 'workingDir',
                   'server', 'page']
        fd = open(scriptFile, 'rb')
        reader = csv.reader(fd)
        line = reader.next()
        if (line != headers):
            raise Exception('Invalid headers. Expected %s; got %s' % (
                str(headers), str(line)))
        for num, line in enumerate(reader):
            if (len(line) == 0 or map(len, line) == [0]*len(line)
                or line[0][0] == '#'): # blank line or comment so skip it
                pass
            elif (len(line) != len(headers)):
                raise Exception(
                    'Line %i invalid: expected %i fields, got %i :\n%s\n' % (
                    num, len(headers), len(line), line))
            else:
                line = [item % varDict for item in line]
                if (not os.path.exists(line[1])):
                    raise Exception('No script named %s exists' % str(line[1]))
                scripts.append((line[0], dict(zip(headers,line))))
        return scripts

    def _AddScriptsToNotebook(self, scripts):
        """Add scripts to Scripts frame in notebook.
        
        INPUTS:
        
        -- scripts:        List of lists obtained from self._ParseScriptFile
                           representing scripts to show.     
        
        -------------------------------------------------------
        
        PURPOSE:        Display and setup new scripts that the user wants
                        to load.
        
        """
        self.commands = {} # forget all previous script commands
        headers = ['enable', 'name', 'action', 'server', 'status',
                   'started', 'finished', 'autoRunAt']
        hColDict = dict([(h, c) for (c, h) in enumerate(headers)])
        mainFrame = self.frame

        #Use getattr to suppress pylint warnings
        myNotebook = getattr(Pmw,'NoteBook')(mainFrame)
        myNotebook.pack(side='top',fill='both',expand=1)
        pageFrames = {}
        pages = sorted(set([item['page'] for item in self.scriptDict.values()]))
        for page in pages:
            pageFrame = myNotebook.add(page)
            #Use getattr to suppress pylint warnings            
            frame = getattr(Pmw,'ScrolledFrame')(
                pageFrame, labelpos='n', horizflex='expand', vertflex='expand')
            frame.pack(expand=1,fill='both')
            pageFrames[page] = frame.interior()
            serverOptions = (['<best>','<local>']+[
                '%s:%s' % (host, port) for (host, port)
                in self.master.helpers['Servers'].servers])
            for h in headers:
                Tkinter.Label(pageFrames[page],
                              text=h).grid(row=0,column=hColDict[h])

        numItems = dict([(n, 0) for n in pageFrames])
        for rowData in scripts:
            scriptName = rowData[0]
            params = self.scriptDict[scriptName]
            params['period'] = Periodicity.ParsePeriod(
                params['autoRunAt'],failureMsgPrefix='''
                Could not parse period for script %s. Using Never.
                ''' % scriptName)
            info = self.master.MakeTaskItems(
                pageFrames[params['page']], scriptName, serverOptions,
                params['server'],params['scriptFile'], params['period'],
                1 + numItems[params['page']])
            if (scriptName not in self.commands):
                self.commands[scriptName] = {}
            self.commands[scriptName][params['server']] = info
            for (name, item) in info.itemList:
                item.grid(row=1+numItems[params['page']], column=hColDict[name])
            numItems[params['page']] += 1
                          
                       
        myNotebook.setnaturalsize()

    def CheckAutoRunScripts(self):
        """Check whether to launch scripts that have valid autoRunAt settings.

        Meant to mainly be called by master._DoUpdates.
        """
        try:
            for (script, _params) in self.scriptDict.items():
                theDict = self.commands[script]
                self.frame.update_idletasks()                
                if (len(theDict) == 0):
                    pass
                elif (len(theDict) > 1):
                    raise Exception(
                        'Cannot handle script with multiple servers: %s' %
                        (str(script, sorted(theDict))))
                else:
                    logging.debug('%s:Checking whether to run %s...' % (
                        datetime.datetime.now(), script))
                    info = theDict.values()[0]
                    self._DoAutoRun(script, info)
        except Exception, e:
            logging.error('Got exception in CheckAutoRunScripts: %s' % str(e))
            errTrace = ('Exception of type \'' + `sys.exc_type` + '\':  \'' + 
                        e.__str__() + '\'.\n\n\n' +
                        ''.join(traceback.format_tb(sys.exc_info()[2])),
                        sys.exc_info())
            GUIUtils.ComplainAboutException(e,errTrace,window=None)

    def _DoAutoRun(self, script, info):
        """Helper function to try to auto-run a given script.
        
        INPUTS:
        
        -- script:        Script to auto-run.
        
        -- info:          TaskInfo instance for script to run.
        
        -------------------------------------------------------
        
        PURPOSE:        Check whether to auto-activate script and so
                        if it is time.
        
        """
        try:
            Flash(dict(info.itemList)['autoRunAt'])
            if (info.enable.get() and info.period.ActivateP()):
                logging.info('Auto-activating script %s' % script)
                try: # Do a show to refresh status
                    self.master.helpers['Servers'].ShowTask(info)
                except Exception, e:
                    self.master.MakeWarning(
                        'update problem',
                        'Got exception when updating task %s:\n%s'
                        % (info.name, str(e)))
                self.master.helpers['Scripts'].Launch(info)
        except Exception, e:
            errTrace = ('Exception of type %s:\n%s\n%s\n%s\n' % (
                str(sys.exc_type), e.__str__(), ''.join(
                traceback.format_tb(sys.exc_info()[2])), sys.exc_info()))
            self.master.MakeWarning('autoRun invalid','''
            Got exception when checking auto run script %s:\n%s\n
            Will no longer try to auto-run it.
            Setting autoRun to invalid and not attempting auto run.
            Traceback: %s
            ''' % (script, e, errTrace), email=True)
            info.period = Periodicity.NoPeriod(None)
            info.autoRunAt.set('invalid')


    def Launch(self, info, useSetServer=False):
        """Launch a script.
        
        INPUTS:
        
        -- info:          TaskInfo instance representing task to launch.

        -- useSetServer:  Whether to use the server set in info. If False,
                          then choose server based on script file.
        
        -------------------------------------------------------
        
        PURPOSE:        Launch a script either as requested by user or
                        from autoRunAt.
        
        """
        logging.debug('Called launch on %s:' % str(info))
        if (info.status.get() not in ['unknown', 'cleaned']):
            try: # try to refresh the handle
                info.status.set('unknown') #default to unknown if ShowTask fails
                self.master.helpers['Servers'].ShowTask(info, timeout=0)
            except Exception, e:
                logging.debug('ignoring exception: %s' % str(e))
        if (info.status.get() == 'finished'):
            logging.debug('Killing finished task %s' % repr(info))
            try:
                self.master.helpers['Tasks'].KillAndReset(info)
            except Exception, e:
                self.master.MakeWarning('bad launch','''
                In Launch, doing KillAndReset got exception %s''' % str(e))
        if (info.status.get() in ['unknown', 'cleaned']):
            params = self.scriptDict[info.name]
            workingDir = params['workingDir']
            if (workingDir in ['None',None,'','<default>']):
                workingDir = os.path.dirname(params['scriptFile'])
            task = Tasks.ImpersonatingTask(
                targetTask=Tasks.ImportPyTask(
                fileName=params['scriptFile'],name=info.name),
                workingDir=workingDir,
                domain=self.master.GetParam('domain'),
                password=self.master.GetParam('password'),
                user=self.master.GetParam('user'),
                name=info.name,mode='createProcess')

            if (useSetServer):
                server = info.server.get()                
            else:
                server = params['server']
                info.server.set(server)
            handle = self.master.helpers['Servers'].SubmitTask(task, server)
            info.SetFromHandle(handle=handle)
        else:
            raise Exception('''Task "%s" has invalid status %s for launch.
            Can only launch task if status is clean or unknown.
            Otherwise you must kill the task or try Show to get status
            ''' % (info.name, info.status.get()))
        

class ServerPage(HelperPage):
    """Page listing all servers monitored by SuperWatch.
    """

    def __init__(self, master):
        HelperPage.__init__(self, master, name='Servers')
        self.servers = []
        self.scheduler = None

    def ReloadServers(self, serverData):
        """Reload servers that the monitor knows about.
        
        INPUTS:
        
        -- serverData:        List of (host, port) pairs representing
                              servers to use.  
        
        -------------------------------------------------------
        
        PURPOSE:        This sets up the servers we know to talk to.
        
        """
        self.master.notebook.selectpage('Servers')
        self.scheduler = Servers.Scheduler(serverData)
        self.servers = serverData
        
        for host, port in serverData:
            itemFrame = Tkinter.Frame(self.frame)
            itemName = Tkinter.Label(itemFrame, text='%s:%s'%(host,port))
            menuButtonFrame = Tkinter.Frame(itemFrame,borderwidth=2,
                                            relief='raised')
            menuButton = Tkinter.Menubutton(menuButtonFrame)
            menu = Tkinter.Menu(menuButton, tearoff=0)
            menuButton.configure(menu=menu)
            menuButton.configure(text='Actions')
            menu.add_command(label='Show', command = GUIUtils.GenericGUICommand(
                'Show %s:%s'%(host,port), self.ShowServer, (host,port)))
            menu.add_command(label='Clean',command = CleanTasksCmd(
                self.master, host,port,'.',self.master.GetParam('autoClean')))
            menu.add_command(label='Import',command= ImportTasksCmd(
                self.master, host, port, '.'))
            menu.add_command(label='Launch',command= LaunchTasksCmd(
                self.master, host))            

            menuButton.pack(fill='x',expand=1,side='left')
            for thing in [itemName, menuButtonFrame]:
                thing.pack(fill='x',expand=1,side='left')
            itemFrame.pack(fill='x',expand=1,side='top')

    def ShowServer(self, host, port):
        """Show information about the given server.
        
        INPUTS:
        
        -- host, port:        Information of server to contact.
        
        -------------------------------------------------------
        
        RETURNS:        String showing status of given server.
        
        """
        result = self.scheduler.ShowQueue(host, port)
        msg = """
        Queue for %s:%s is:\n%s\n
        """ % (host, port, '\n'.join(map(str, result)))
        return msg

    def SubmitTask(self, task, server):
        """Submit a task to the given server.
        
        INPUTS:
        
        -- info:        Task to run remotely via superpy.
        
        -- server:      Either '<best>' or '<host>:<port>' indicating
                        server to run on.
        
        -------------------------------------------------------
        
        RETURNS:        Handle to newly submittined task.
        
        -------------------------------------------------------
        
        PURPOSE:        Take care of submitting task to a server.
        
        """
        if (server == '<best>'):
            logging.debug('Submitting task to best server; task=%s\n'
                          % repr(task))
            handle = self.scheduler.SubmitTaskToBestServer(task)
        elif (server == '<local>'):
            logging.debug('Running task locally; task=%s\n'% repr(task))
            task.mode = 'subprocess'
            handle = task.Run(wait=False)
        else:
            logging.debug('Submitting task to server %s; task=%s\n'
                          % (server, repr(task)))
            host, port = server.split(':'); port = int(port)
            handle = self.scheduler.hosts[(host, port)].Submit(task)
        return handle

    def ShowTask(self, info, timeout=3, cache=None):
        """Show status of task.
        
        INPUTS:
        
        -- info:        TaskInfo instance representing task to show.
        
        -- timeout=3:   Optional timeout in seconds for how long to wait
                        to get status.

        -- cache=None:  Optional list of task handles matching info.name
                    (e.g., as returened by SuperInfo.SearchForTasks or by
                    SuperInfo.MakeTaskDict(...)[info.name]). If not provided, we
                    will lookup but this is useful to provide if you make lots
                    of calls in a row to avoid repeating the lookup.
        
        -------------------------------------------------------
        
        RETURNS:        String message indicating status of task.
        
        -------------------------------------------------------
        
        PURPOSE:        Provide a way to get status of task. This method
                        also modifies info to refresh its status.
        
        """
        return SuperInfo.RefreshInfo(
            self.scheduler, info, timeout, cache,
            idle=self.master.notebook.update_idletasks)


class MasterMonitor:
    """Master class to monitor + run superpy tasks
    """

    def __init__(self, parent, defaults):

        self.notebook = None
        self.msgWindow = None
        self._MakeMainFrame(parent)        
        self.helpers = dict((item.name, item) for item in [
            TaskPage(self), ScriptPage(self), ServerPage(self),
            ConfigPage(self, defaults)
            ])
        self._lastMajorUpdates = datetime.datetime.now()


        self._MakeHelperFrames()
        self._DoUpdates()
        self.notebook.setnaturalsize()
        self._emailsSent = [datetime.date.today(), 0]

    def MakeWarning(self, title, detail, email=False):
        """Make a warning that gets logged and shows up in message window.
        
        INPUTS:
        
        -- title:        Short title for warning.
        
        -- detail:       Detailed info for warning.

        -- email=False:  Whether to email user about the warning.
        
        """
        logging.warning(detail)
        self.msgWindow.MakeMsg(title, detail)

        if (email):
            smtp = self.GetParam('smtp')
            user = self.GetParam('user')
            if (smtp is not None and smtp.strip() not in ['','None']):
                if (self._emailsSent[1] > 100):
                    if (self._emailsSent[0] == datetime.date.today()):
                        logging.warning(
                            'Already sent too many emails today. Not sending')
                        return
                    else:
                        self._emailsSent[0] = datetime.date.today()
                msg = 'Subject: %s\n\n%s' % (title, detail)
                server = smtplib.SMTP(smtp)
                #server.set_debuglevel(1) # uncomment for debug info
                server.sendmail(user,[user],msg)
                server.quit()
                self._emailsSent[1] += 1
        

    def _MakeSuperWatchButtonFrame(self, rootWindow, quitCmd):
        """Make super watch buttons.

        INPUTS:

        -- rootWindow:        Top level window for superwatch.

        -- quitCmd:           Command to call when quit button pushed.

        -------------------------------------------------------

        RETURNS:    Frame containing packed buttons.

        """

        buttonFrame = Tkinter.Frame(rootWindow, name='buttonFrame')

        quitButton = Tkinter.Button(buttonFrame,text='Quit', command=quitCmd)
        quitButton.pack(fill='x',expand=1,side='left')

        helpButton = Tkinter.Button(
            buttonFrame, text='Help',
            command=lambda : self.MakeMainHelpDialog())
        helpButton.pack(fill='x',expand=1,side='left')

        return buttonFrame

    def MakeMainHelpDialog(self):
        "Make dialog showing help message."

        GUIUtils.MakeTextDialog(title="SuperWatch Help",text="""
        SuperWatch GUI

        SuperWatch lets you monitor, spawn, and kill various tasks run
        through superpy. Use the following tabs:

          Config:  Apply configuration settings and load scripts.
          Servers: View and check servers specified in Config tab.
          Tasks:   Load, monitor, kill tasks.
          Scripts: Launch, monitor, kill tasks loaded from Config.

        """ + self.GetExtraHelp())

    def _MakeMainFrame(self, parent):
        """Make main frame for monitor
        
        INPUTS:
        
        -- parent:        Toplevel window to make frame in.
        
        """
        mainFrame = Tkinter.Frame(parent, name='mainFrame')
        nameFrame = self._MakeSuperWatchNameFrame(mainFrame)
        buttonFrame = self._MakeSuperWatchButtonFrame(
            parent, lambda : parent.destroy())
        nameFrame.pack(side='top',expand=0,fill='x')
        mainFrame.pack(fill='both',expand=1,side='top')        
        window = getattr(Pmw,'PanedWidget')(
            mainFrame,orient='vertical',hull_height=500,hull_width=500)
        pane = window.add('Main',min=.6,size=.9)
        self.notebook = getattr(Pmw,'NoteBook')(pane)
        pane = window.add('msgs',min=.1,size=.1)
        msgFrame = Tkinter.Frame(pane)
        self.msgWindow = MsgWindow.MsgWindow(msgFrame)
        self.msgWindow.MakeMsg('Info','''
        This window contains info messages. For each message, click on the
        leftmost button to see the full message. Click on the kill button to
        remove the message from the message queue.
        ''')

        self.notebook.pack(side='top',fill='both',expand=1,padx=10,pady=10)
        msgFrame.pack(fill='both',expand=1,side='bottom')
        window.pack(fill='both',expand=1,side='top')
        buttonFrame.pack(fill='x',expand=0,side='bottom')        
        window.configurepane('msgs',size=.1)
        window.configurepane('Main',size=.8)        
        window.updatelayout()

    @staticmethod
    def _MakeSuperWatchNameFrame(rootWindow):
        """Make frame to list name of applicaiton
        """

        frame = Tkinter.Frame(rootWindow,relief='sunken',bd=2)
        nLabel = Tkinter.Label(
            frame,foreground='blue',background='white',padx=5,pady=5,
            text='SuperWatch')
        nLabel.pack(side='top',fill='x',expand=1)

        return frame
        

    def _MakeHelperFrames(self):
        """Make main frames for the monitor.
        """
        # NOTE: Config page must be created first.
        for name in sorted(self.helpers):
            logging.debug('Creating frame for %s' % name)
            self.helpers[name].MakeFrame(self.notebook)

    def _DoUpdates(self):
        """Do various kinds of background updates.

        The GUI would be more responsive if we put these into seperately
        running threads, but sometimes we actually want to block the user
        while we are doing things so we don't currently do this in threads.
        """
        self.AutoUpdateTaskStatus('Tasks')
        self.AutoUpdateTaskStatus('Scripts')        
        self.helpers['Scripts'].CheckAutoRunScripts()
        self.CheckMajorUpdates()
        self.notebook.after(self.GetParam('pollFrequency'), self._DoUpdates)

    def GetParam(self, argName):
        """Return value of config item with given name.
        """
        return self.helpers['Config'].confItemDict[argName].GetArg()

    def GetExtraHelp(self):
        """Return docs describing extra help on current functions.

        Among other things, this should lookup which tab is currently
        selected and provide help based on that tab.
        """
        curPage = self.notebook.getcurselection()
        return '\nHelp for %s:\n%s' % (curPage, self.helpers[curPage].Help())

    def CheckMajorUpdates(self):
        """Do major updates that happen occassionally.

        Meant to mainly be called by self._DoUpdates
        """
        now = datetime.datetime.now()
        if (now - self._lastMajorUpdates >
            datetime.timedelta(seconds=self.GetParam('majorPollFrequency'))):
            logging.debug('Doing major update at %s' % now)
            SuperInfo.CleanTasks(self.helpers['Servers'].scheduler,
                                 '.','.','.',self.GetParam('autoClean'))
            self._lastMajorUpdates = now
                       
    def AutoUpdateTaskStatus(self, groupName):
        """Update status for all the tasks we know about.
        
        Meant to mainly be called by self._DoUpdates        
        """
        keysToRemove = []
        try:
            taskDict, _msg = SuperInfo.MakeTaskDict(
                self.helpers['Servers'].scheduler,
                idle=self.notebook.update_idletasks)
        except Exception, e:
            self.MakeWarning('get tasks problem','''
            Unable to get all tasks because of exception:\n%s\n\n
            Continuing without cached task info.
            This will slow down the auto-updates.''' % (str(e)))
            taskDict = {}
        commands = self.helpers[groupName].commands
        for taskName, cmdTaskDict in commands.items():
            for serverName, info in cmdTaskDict.items():
                self.notebook.update_idletasks()
                key = (groupName,taskName,serverName)
                now = datetime.datetime.now()
                logging.debug('Auto-updating %s at %s' % (key, now))
                try:
                    cache = taskDict.get(info.name,{}).values()
                    self.helpers['Servers'].ShowTask(info, cache=cache)
                except Exception, e:
                    errTrace = ('Exception of type \'' + `sys.exc_type`
                                + '\':  \'' +  e.__str__() + '\'.\n\n\n' +
                                ''.join(traceback.format_tb(sys.exc_info()[2])),
                                sys.exc_info())
                    self.MakeWarning('autoUpdate error','''
                    Got exception when auto-updating task %s:\n%s\n%s''' % (
                        key, e, errTrace))
                    if (groupName != 'Scripts'):
                        self.MakeWarning(
                            'autoUpdate error','''
                            Will no longer auto-update task %s due to error %s
                            ''' % (key, e))
                        keysToRemove.append(key)
                endTime = datetime.datetime.now()
                logging.debug('Finished auto-updating %s at %s (time = %s)' %
                              (key, endTime, endTime-now))
        for key in keysToRemove:
            del commands[key[1]][key[2]]

    def MakeTaskItems(self, frame, taskName, serverOptions, defaultServer,
                      scriptFile, period=None, row=None):
        """Make item representing the given task in the given frame.
        
        INPUTS:
        
        -- frame:        Frame to create task items in.
        
        -- taskName:     String name of task to create.   
        
        -- serverOptions:  List of strings representing possible values for
                           server.

        -- defaultServer:  String name of default server to use.
        
        -- scriptFile:  Path to file to run script or None if not launchable.
        
        -- period=None:    Period for how often to run via autoRunAt.    
        
        -- row=None:       Integer row number to display for task. This must
                           be not None for things the user can launch.
        
        -------------------------------------------------------
        
        RETURNS:        New TaskInfo instance representing task.
        
        -------------------------------------------------------
        
        PURPOSE:        Create TaskInfo for new task. User may want
                        to grid/pack result.infoList contents.
        
        """
        info = TaskInfo(
            taskName, defaultServer, period=period,
            enable=row is not None and self.GetParam('enableAutoRun'))
        # use getattr to suppress pylint warning
        ballon = getattr(Pmw,'Balloon')(frame)
        if (row):
            enable = Tkinter.Checkbutton(frame, variable=info.enable,text=row)
        status = Tkinter.Label(frame, textvariable=info.status)
        started = Tkinter.Label(frame, textvariable=info.started)
        finished = Tkinter.Label(frame, textvariable=info.finished)
        autoRunAt = Tkinter.Label(frame, textvariable=info.autoRunAt)
        serverMenu = Tkinter.OptionMenu(frame, info.server,*serverOptions)
        itemName = Tkinter.Label(frame, text=taskName)
        menuButtonFrame = Tkinter.Frame(frame,borderwidth=1,relief='raised')
        menuButton = Tkinter.Menubutton(menuButtonFrame)
        menu = Tkinter.Menu(menuButton, tearoff=0)
        menuButton.configure(menu=menu)
        menuButton.configure(text='Actions')
        if (scriptFile):
            ballon.bind(itemName, 'Run script in %s' % scriptFile)
            menu.add_command(
                label='Launch', command = GUIUtils.GenericGUICommand(
                'Launch %s'%taskName,
                self.helpers['Scripts'].Launch, [info, True]))
        menu.add_command(label='Kill', command = GUIUtils.GenericGUICommand(
            'Kill %s'%taskName, self.helpers['Tasks'].Kill, [info]))
        menu.add_command(label='KillAndReset',
                         command = GUIUtils.GenericGUICommand(
            'KillAndReset %s'%taskName, self.helpers['Tasks'].KillAndReset,
            [info]))
        menu.add_command(label='Show', command = GUIUtils.GenericGUICommand(
            'Show %s'%taskName, self.helpers['Servers'].ShowTask, [info]))

        menuButton.pack(fill='x',expand=1,side='left')

        info.itemList = [
            ('status', status), ('server', serverMenu),
            ('name', itemName), ('action', menuButtonFrame),
            ('started', started), ('finished', finished),
            ('autoRunAt', autoRunAt)]
        if (row):
            info.itemList = [('enable', enable)] + info.itemList
        return info


    def ImportTasks(self, hostRE, portRE, taskRE):
        """Import desired tasks into Tasks page.
        
        INPUTS:
        
        -- hostRE:        String regular expression for hosts to search.
        
        -- portRE:        String regular expression for ports to search.
        
        -- taskRE:        String regular expression for tasks to search.
        
        -------------------------------------------------------
        
        RETURNS:        String message describing what we imported.
        
        -------------------------------------------------------
        
        PURPOSE:        Go through all tasks which match the given regular
                        expressions and import them into the Tasks page.
                        This is useful for grabbing tasks that you want to
                        analyze or do something with.
        
        """        
        tasks, msg = SuperInfo.SearchForTasks(
            self.helpers['Servers'].scheduler, hostRE, portRE, taskRE,
            idle=self.notebook.update_idletasks)

        self.helpers['Tasks'].MakeTaskFrameItems(tasks)

        return msg

class ImportTasksCmd(GUIUtils.GenericGUICommand):
    '''
    This command searches all hosts for tasks matching the
    given regular expressions and imports them into the Tasks page.
    '''

    def __init__(self, monitor, hostRE, portRE, taskRE):
        self.monitor = monitor

        GUIUtils.GenericGUICommand.__init__(
            self,'ImportTasks',command=None,argList=[
            ('hostRegexp',GUIValidators.StringValidator(hostRE),'''
            Regular expression for hosts to search.'''),
            ('portRegexp',GUIValidators.StringValidator(portRE),'''
            Regular expression for ports to search.'''),
            ('taskRegexp',GUIValidators.StringValidator(taskRE),'''
            Regular expression for tasks to search.''')])

    def _DoCommand(self):
        """Do the work of the command.
        """

        hostRE = self.argDict['hostRegexp']['value']
        portRE = self.argDict['portRegexp']['value']
        taskRE = self.argDict['taskRegexp']['value']
        result = self.monitor.ImportTasks(hostRE, portRE, taskRE)
        return result

class LaunchTasksCmd(GUIUtils.GenericGUICommand):
    '''This command launches an arbitrary script on a remote server.
    '''

    def __init__(self, monitor, host, port=9287):
        self.monitor = monitor
        
        GUIUtils.GenericGUICommand.__init__(
            self,'LaunchTask',command=None,argList=[
            ('host',GUIValidators.StringValidator(host),'''
            String name of host to launch task on.'''),
            ('port',GUIValidators.IntValidator(port),'''
            Integer port to launch task on.'''),
            ('taskScript',GUIValidators.ExistingFileNameValidator(),'''
            Python script to run remotely.'''),
            ('taskName',GUIValidators.StringValidator('myTask_%s'%time.time()),
             '''String name for task.'''),
            ])

    def _DoCommand(self):
        """Do the work of the command.
        """

        host = self.argDict['host']['value']
        port = self.argDict['port']['value']
        taskScript = self.argDict['taskScript']['value']
        taskName = self.argDict['taskName']['value']
        task = Tasks.ImpersonatingTask(
            targetTask=Tasks.ImportPyTask(
            fileName=taskScript,name=taskName),
            workingDir=os.path.dirname(taskScript),
            domain=self.monitor.GetParam('domain'),
            password=self.monitor.GetParam('password'),
            user=self.monitor.GetParam('user'),name=taskName,
            mode='createProcess')
        _handle = self.monitor.helpers['Servers'].SubmitTask(
            task, '%s:%i'%(host,port))


class CleanTasksCmd(GUIUtils.GenericGUICommand):
    '''
    This command searches all hosts for tasks with a finish
    time that is older than the given threshold and cleans them out.
    '''

    def __init__(self, monitor, hostRE, portRE, taskRE,
                 threshold):
        self.monitor = monitor

        GUIUtils.GenericGUICommand.__init__(
            self,'CleanTasks',command=None,argList=[
            ('hostRegexp',GUIValidators.StringValidator(hostRE),'''
            Regular expression for hosts to search.'''),
            ('portRegexp',GUIValidators.StringValidator(portRE),'''
            Regular expression for ports to search.'''),
            ('taskRegexp',GUIValidators.StringValidator(taskRE),'''
            Regular expression for tasks to search.'''),
            ('threshold',GUIValidators.IntValidator(default=threshold,
                                                    minVal=0),'''
            How many seconds to wait for a finished task before
            cleaning it out.'''),            
            ])

    def _DoCommand(self):
        "Do the work of the command as required by GenericGUICommand"
        
        hostRE = self.argDict['hostRegexp']['value']
        portRE = self.argDict['portRegexp']['value']
        taskRE = self.argDict['taskRegexp']['value']
        threshold = self.argDict['threshold']['value']
        result = SuperInfo.CleanTasks(self.monitor.helpers['Servers'].scheduler,
                                      hostRE, portRE, taskRE, threshold)
        return result

    
class ConfigItem:
    """Generic configuration item for GUI.

    This is meant to be an abstract base class which sub-classes can
    specialize to represent configuration items.
    """

    def __init__(self, frame, name, validator, doc=None):
        """Initializer.
        
        INPUTS:
        
        -- frame:      Frame to create configuration item in.  
        
        -- name:       String name of item. 
        
        -- validator:  Instance of GUIValidators.Validator to use to
                       validate argument. 
        
        -- doc=None:   Optional doc string. If None, we pull from
                       self.__class__.__doc__. 
        """
        if (doc is None): doc = self.__class__.__doc__
        else: doc = 'No documentation provided.'

        self.name = name
        self.validator = validator
        self.doc = doc
        self.menuEntry, self.entry = self.validator.MakeMenuEntry(frame)
        self.label = Tkinter.Label(frame, text=name)
        self.helpButton = Tkinter.Button(
            frame, text='?', command= lambda : GUIUtils.MakeTextDialog(
            title="Help on %s" % self.name,text=self.doc))

        rowNum = len(frame.children)
        self.label.grid(row=rowNum, column=1, sticky='WENS')
        self.menuEntry.grid(row=rowNum, column=2, sticky='WENS')
        self.helpButton.grid(row=rowNum, column=3)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)        
        frame.grid_rowconfigure(rowNum, weight=1)

    def Apply(self, master):
        """Apply configuration to master.
        
        INPUTS:
        
        -- master:        Instance of MasterMonitor to apply config to.
        
        -------------------------------------------------------
        
        PURPOSE:   This method will be called when user loads new
                   configuration. Subclasses may override to do
                   something special.
        """
        _ignore = master, self

    def GetArg(self):
        "Return validated arg"
        return self.validator(self.entry.get())
        

class PollFrequency(ConfigItem):
    '''Int for how often to poll tasks (in milli-seconds) to update status.
    '''

    def __init__(self, argFrame):
        ConfigItem.__init__(self, argFrame, 'pollFrequency',
                            GUIValidators.IntValidator(default=60*1000*1))

class MajorPollFrequency(ConfigItem):
    '''Int indicating how often to poll major tasks in milli-seconds.

    This should be not too often since major tasks may take a while
    and you don't want to be constantly running them.
    '''

    def __init__(self, argFrame):
        ConfigItem.__init__(self, argFrame, 'majorPollFrequency',
                            GUIValidators.IntValidator(default=60*1000*60))

class EnableScripts(ConfigItem):
    '''Boolean indicating whether to enable auto-run scripts by default.
    '''

    def __init__(self, argFrame):
        ConfigItem.__init__(self, argFrame, 'enableAutoRun',
                            GUIValidators.BooleanValidator(default=False))

class ServerConfItem(ConfigItem):
    '''Comma seperated list of superpy servers and ports.

    For example,

    foo:9287,bar:9287

    would indicate that the hosts foo and bar can be contacted on port 9287.
    '''

    def __init__(self, argFrame):
        ConfigItem.__init__(self, argFrame, 'servers',
                            GUIValidators.StringIntListValidator())

    def Apply(self, master):
        """Override ConfigItem.Apply to also reload servers.
        """
        ConfigItem.Apply(self, master)
        master.helpers['Servers'].ReloadServers(self.GetArg())

class SMTPConfItem(ConfigItem):
    '''Name of smtp server to use in sending emails.

    For example, you might provide something like mysmtp.mydomain.com.

    If this is non-empty, emails will be sent based on certain error
    conditions.
    '''

    def __init__(self, argFrame):
        ConfigItem.__init__(self, argFrame, 'smtp',
                            GUIValidators.StringValidator())

    def Apply(self, master):
        """Override ConfigItem.Apply to also reload servers.
        """
        ConfigItem.Apply(self, master)

class ScriptConfItem(ConfigItem):
    '''Path to a CSV file indicating scripts to run.

                        The script file should be a comma separated values
                        file with the following headers in the first row
                        and corresponding values for each subsequent row:

           scriptName:  Name of script.
           scriptFile:  Path to python file representing script. This will
                        be imported when script is run.
           autoRunAt:   String as expected by elements in Periodicity module
                        representing when to automatically run script.
           workingDir:  String representing working directory to run script
                        in. If None, 'None', '', or '<default>', run in
                        directory containing scriptFile.
           server:      Indicates host:port to run task on. If '<best>', run
                        on the best available server.
           page:        String indicating what page of scripts window to
                        show script on. This is useful for organizing
                        similar scripts together.

        Any line (except the first), which begins with a # is
        ignored as a comment.

        Furthermore, one can use python string formatting commands for
        any field with the following variables:

          %(user)s  : Replaced with current username.
          %%        : Escape code for raw % character.
    
    '''

    def __init__(self, argFrame):
        ConfigItem.__init__(
            self, argFrame, 'scripts',
            GUIValidators.ExistingFileNameValidator())
                            
    def Apply(self, master):
        """Override ConfigItem.Apply to also load scripts.
        """
        ConfigItem.Apply(self, master)
        scriptName = self.GetArg()
        if (scriptName in ['None',None,'']):
            master.MakeWarning('no scripts',
                               'No script name given; not loading scripts')
        else:
            logging.debug('Reloading script %s' % scriptName)        
            master.helpers['Scripts'].ReloadScripts(self.GetArg())

class LogConfItem(ConfigItem):
    '''Loglevel to use
    '''

    def __init__(self, argFrame):
        ConfigItem.__init__(self, argFrame, 'logLevel',
                            GUIValidators.LogLevelValidator())

    def Apply(self, master):
        """override ConfigItem.Apply to also set log level.
        """
        ConfigItem.Apply(self, master)
        logging.getLogger('').setLevel(getattr(logging, self.GetArg()))

class AutoCleanConfItem(ConfigItem):
    '''Threshold (in seconds) to allow when auto-cleaning completed tasks.

    Periodically, we will try to call CleanTasks on everything with the
    given threshold. This keeps stale tasks from clogging things up.
    '''

    def __init__(self, argFrame):
        ConfigItem.__init__(self, argFrame, 'autoClean',
                            GUIValidators.IntValidator(default=30000))


class DomainConfItem(ConfigItem):
    '''Domain for user.
    '''

    def __init__(self, argFrame):
        ConfigItem.__init__(self, argFrame, 'domain',
                            GUIValidators.StringValidator())

class UserConfItem(ConfigItem):
    '''Username to run as
    '''

    def __init__(self, argFrame):
        ConfigItem.__init__(self, argFrame, 'user',
                            GUIValidators.StringValidator())

class PasswordConfItem(ConfigItem):
    '''Password to use if necessary.
    '''

    def __init__(self, argFrame):
        ConfigItem.__init__(
            self, argFrame, 'password',GUIValidators.StringValidator(
            meOptions={'show':'*'}))

class TaskInfo:
    """Class to represent information about a task in MasterMonitor class.

    Many of the properties of this class will be Tkinter.StringVar or
    Tkinter.IntVar so the properties can be displayed by various labels
    and automatically get updated by calling self.SetFromHandle.
    """

    def __init__(self,name,defaultServer,status='unknown',started='unknown',
                 finished='unknown',enable=1,period=None,handle=None):
        """Initializer.
        
        INPUTS:
        
        -- name:       String name of task.

        -- defaultServer:  String name of default server to use.
        
        -- status='unknown':        Status of task.
        
        -- started='unknown':       When the task started. 
        
        -- finished='unknown':      When task finished.  
        
        -- enable=1:                Whether to check autoRunAt and start
                                    automatically when necessary.
        
        -- period=None:             How often to try to automatically run.
        
        -- handle=None:             Handle to task on server.
        
        """
        if (period is None):
            period = Periodicity.NoPeriod(None)
        self.name = name
        self.status = Tkinter.StringVar(value=status)
        self.defaultServer = defaultServer
        self.server = Tkinter.StringVar(value=defaultServer)
        self.started = Tkinter.StringVar(value=started)
        self.finished = Tkinter.StringVar(value=finished)
        self.autoRunAt = Tkinter.StringVar(value=period.periodStr)
        self.enable = Tkinter.IntVar(value=enable)
        self.handle = handle
        self.period = period

        self.itemList = []

    def Reset(self):
        """Reset status.

        This is useful for resetting the status of self when we search for
        the task and find nothing for it.
        """
        self.status.set('unknown')
        self.server.set(self.defaultServer)
        self.started.set('unknown')
        self.finished.set('unknown')
        self.handle = None

    def SetFromHandle(self, status=None,server=None,started=None,
                      finished=None,handle=None):
        """Set various properties based on our handle to remote task.
        
        INPUTS:
        
        -- *args:       Things expected by __init__.
        
        -------------------------------------------------------
        
        PURPOSE:        This either takes the handle given as input or
                        tries to update self.handle to get current status
                        of the task and then propagates this to properties.
                        It is useful for updating status fo the task.
        
        """
        if (handle is None):
            if (self.handle is None): #don't know anything about handle so reset
                return self.Reset()
            else:
                handle = self.handle
        else:
            self.handle = handle

        handleInfo = handle.StatusInfo()
        if (server is None):
            server = '%s:%s' % (handleInfo['host'], handleInfo['port'])
            
        started = started if started is not None else handleInfo['starttime']
        finished = finished if finished is not None else handleInfo['endtime']

        self.server.set(server)            
        self.status.set(status if status is not None else handleInfo['mode'])
        self.started.set('-' if started is None
                         else started.strftime('%Y-%m-%d %H:%M:%S'))
        self.finished.set('-' if finished is None
                          else finished.strftime('%Y-%m-%d %H:%M:%S'))

    def __repr__(self):
        params = ['%s=%s' % (name, repr(getattr(self,name)))
                  for name in ['name','status','server','started','finished',
                               'period','handle','enable']]
        return 'TaskInfo(%s)' % ','.join(params)

def Flash(item, times=1, delay=1, color='white'):
    """Make an Tk widget flash.
    
    INPUTS:
    
    -- item:        A Tk widget that has a config method we can use.
    
    -- times=1:     How many times to flash.   
    
    -- delay=1:     How long to stay lit up when doing a flash.   
    
    -- color='white':        Color to flash as.
    
    -------------------------------------------------------
    
    PURPOSE:    Make a TK widget flash.
    
    """
    if (times <= 0):
        return
    
    origColor = item.config()['background'][-1]

    item.config(bg=color)
    t = threading.Timer(
        delay, lambda : (item.config(bg=origColor)
                         and Flash(item, times-1, delay, color)))
    t.start()
    return t

def _test():
    "Test docstrings"
    import doctest
    doctest.testmod()

if __name__ == "__main__":    
    _test()
    print 'Test finished.'
            
