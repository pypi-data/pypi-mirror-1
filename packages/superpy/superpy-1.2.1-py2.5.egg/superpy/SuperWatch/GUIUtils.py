"""Module containing utilities for running commands in GUI.
"""

import sys, logging, traceback, datetime
import Tkinter, tkFont, tkMessageBox

def EmptyP(arg):
    "Return True if arg is an emtpy string or None."
    if (str == type(arg)):
        arg = arg.strip()
    return (None == arg or '' == arg)

def SaveTextToFile(text,parent):
    """Created dialog box in parent window to save text to a file.
    
    INPUTS:
    
    -- text:        Text to save.
    
    -- parent:      Parent window of dialog to create.  
    
    -------------------------------------------------------
    
    PURPOSE:    Provide a simple way for user to save text to a file.
    
    """
    fileName = parent.tk.call(
        'tk_getSaveFile','-parent',parent,'-initialdir','c:')
    if (fileName is not None and fileName != ''):
        open(fileName,'w').write(text)


def MakeHelpDialog(item,helpMsg,parent=None):
    "Make dialog showing help for message"

    logging.debug('ignoring parent argument %s' % str(parent))
    MakeTextDialog('ARCP Help','Help on ' + item + ':\n\n' + helpMsg)



def MakeTextDialog(title,text,grab=0,extraCommands=None,fontArgs=None):
    """
    MakeTextDialog(title,text,grab=0):

    title:  Title of the dialog to create.
    text:   The text that the dialog should contain.
    grab:   Whether or not to execute a 'grab' and force the user
            to click OK before interacting with the rest of the
            application.
    extraCommands: Dictionary of names and callable objects.
    fontArgs: Optional dictionary of arguments to tkFont.Font

    This function creates a new dialog box with the given title and
    displays the given text in a (disabled) text widget. Any name/command
    pairs provided in extraCommands are added as buttons the user can
    click to run the corresponding command.
    """
    if (extraCommands is None): extraCommands = {}
    if (fontArgs is None): fontArgs = {}
    window = Tkinter.Toplevel()
    window.title(title)
    yscroll=Tkinter.Scrollbar(window,orient='vertical')
    message = Tkinter.Text(window,yscrollcommand=yscroll.set)
    yscroll.config(command=message.yview)
    yscroll.pack(side='right',fill='y',expand=0)

    if (len(fontArgs) > 0):
        font = tkFont.Font(**fontArgs)
        message.tag_configure('normal', font=font)
        message.insert(Tkinter.END,str(text),'normal')
    else:
        message.insert(Tkinter.END,str(text))
    
    message.config(state=Tkinter.DISABLED)
    message.pack(side='top',fill='both',expand=1)
    buttonFrame = Tkinter.Frame(window)
    buttonFrame.pack(side='top',fill='both',expand=True)
    button = Tkinter.Button(buttonFrame,text='OK',command = lambda:(
        window.tk.call('grab','release',window),window.destroy()))
    saveMsgButton = Tkinter.Button(buttonFrame,text='Save',command=lambda:(
        SaveTextToFile(message.get(1.0,Tkinter.END),window)))
    saveMsgButton.pack(side='left',fill='both',expand=1)
    button.pack(side='left',fill='both',expand=1)
    for (k,v) in extraCommands.iteritems():
        button = Tkinter.Button(buttonFrame,text=k,command = v)
        button.pack(side='left',fill='both',expand=1)
    if (grab):
        window.tk.call('grab','set',window)
    window.lift()
    return window

class GenericGUICommand:
    """
    The GenericGUICommand class is a class used to create a GUI command.
    It is used to wrap a command into an object which makes running
    the command cleaner.
    """
    
    def __init__(self,name, command=None, fixedArgs=None, argList=None):
        """Initializer.
        
        INPUTS:

          name:           String name of command.
          command=None:   Command to run when invokved. If this is None,
                          then commandMaker will be called to create command.
          fixedArgs=None: Optional list of fixed arguments to provide to
                          command.      
          argList=None:   Optional list of triples of the form
          
                            (argName, argValidator, argDoc)

                          If present, these will be put into a dialog to ask
                          user to fill them out.

        """
        self.name = name
        self.command = command
        self.fixedArgs = [] if fixedArgs is None else fixedArgs
        self.argList = argList
        self.argDict = None    

    def __call__(self, window=None):
        """
        __call__(self):

        Create a window to collect inputs for this command.
        """
        if (self.argList):
            return self.MakeWindow(self.argList, window)
        else:
            self.ProcessCommand(None)

    def _DoCommand(self):
        """Do the actual command. Expected to be called only by ProcessCommand.

        By default this simply calls self.command(*self.fixedArgs), but
        sub-classes can override to do fancier things.
        """
        result = self.command(*self.fixedArgs)
        return result

    def _PrepArgs(self):
        """Prepare args for running command.

        This goes through everything in self.argDict and sets item['value']
        to the validated version of the argument.
        """
        if (self.argDict is not None):
            for (_name, item) in self.argDict.items():
                item['value'] = item['validator'](item['entry'].get())
            
    def ProcessCommand(self, window):
        """Process command including preparing args, running, error reporting.
        
        INPUTS:
        
        -- window:        Parent window for the command. This can be None.
                          If not None, we call window.destroy() if command
                          is successful.
        
        -------------------------------------------------------
        
        PURPOSE:        Prepare arguments for the command via self._PrepArgs,
                        run the command via self._DoCommand, and report results
                        or exceptions. This is what users are exepcted to call
                        to run the actual command.

                        NOTE: This may be called directly if all args are ready
                              or may be called by the window that self.__call__
                              creates to get args and then run the command.
        
        """
        try:
            self._PrepArgs()
            result = self._DoCommand()
            MakeTextDialog(
                title='Command Output',
                text='Command %s completed at %s with result:\n%s\n' % (
                self.name, datetime.datetime.now(), result), grab=1)
            if (window is not None):
                window.destroy()
        except Exception, e:
            logging.debug('Encountered exception %s in GUI.' % e.__str__())
            errTrace = ('Exception of type \'' + `sys.exc_type` + '\':  \'' + 
                         e.__str__() + '\'.\n\n\n' +
                        ''.join(traceback.format_tb(sys.exc_info()[2])),
                        sys.exc_info())
            ComplainAboutException(e,errTrace,window=None)
        except:
            msg = """
            Saw unhandled exception in ProcessCommand : %s.
            Was it a string exception? Please only throw class exceptions.
            """ % (`(sys.exc_type,sys.exc_value,sys.exc_traceback)`)
            logging.critical(msg)
            e = Exception('unhandled Exception')
            raise e

    def MakeWindow(self, argList, window):
        """Make a window to get args from user and then run command.
        
        INPUTS:
        
        -- argList:        List of triples of the form (name, validator, doc)
                           representing string name, GUIValidators.Validator
                           instance, and docstring for arguments.
        
        -- window:         Optional parent window to create stuff in. If None,
                           we create a new top level.     
        
        -------------------------------------------------------
        
        PURPOSE:        This method creates a window to get arguments for
                        a command from the user. Once the user enters the
                        commands and clicks the OK button, we call
                        ProcessCommand to actually run the command.
        
        """
        self.argDict = dict([(n, {'name':n,'validator':v,'doc':d,'entry':None,
                                  'value':None}) for (n,v,d) in argList])
        if (window is None):
            window = Tkinter.Toplevel()

        argFrame = Tkinter.Frame(window,relief='ridge',bd=3)
        for (row, (name, validator, doc)) in enumerate(argList):
            label = Tkinter.Label(argFrame,text=name)
            menuEntry, self.argDict[name]['entry'] = validator.MakeMenuEntry(
                argFrame)
            def HelpInfo():
                "Provide help on command."
                MakeTextDialog(title='Help',text=doc, grab=0)
                
            helpButton = Tkinter.Button(argFrame,text='?',command=HelpInfo)
            label.grid(row=row, column=1)
            menuEntry.grid(row=row, column=2)
            helpButton.grid(row=row, column=3)

        buttonFrame = Tkinter.Frame(window,relief='ridge',bd=6, height =30)
        okButton = Tkinter.Button(buttonFrame,text='OK',command=
            lambda : self.ProcessCommand(window))
        cancelButton = Tkinter.Button(buttonFrame,text='Cancel',command=
            lambda : self.CancelCommand(window))
        helpButton = Tkinter.Button(buttonFrame,text='Help',command=
            lambda : self.HelpCommand(window))
        commandTitle=Tkinter.Label(window,text='Run ' + self.name,
                                   relief='ridge',padx=3,pady=3)
        commandTitle.pack(side='top',fill='x',expand=1)
        argFrame.pack(side='top',fill='both',expand=1)
        buttonFrame.pack(side='top',fill='x',expand=1)
        for button in [okButton, cancelButton, helpButton]:
            button.pack(side='left',fill='x',expand=1)
        return window

    def CancelCommand(self, window):
        "Cancel a command for window created by MakeWindow."
        _ignore = self
        window.destroy()

    def HelpCommand(self, window):
        "Provide help on command"

        _ignore = window
        MakeTextDialog(title='Help on %s' % self.name,
                       text=self.__doc__, grab=1)

def ComplainAboutException(e,errTrace,window=None):
    """
    ComplainAboutException(errTrace,arg,window,e):

    e:         The exception object causing the problem.
    errTrace:  A traceback string describing the error in detail.
    window:    The window representing the command.

    This funciton creates a dialog window describing the error and
    offering to show the user the error traceback if desired.
    """
    errMsg = e.__str__()

    killWindow = False
    if (window is None):
        window = Tkinter.Toplevel()
        killWindow = True
    showTraceBack = window.tk.call('tk_dialog','.showTBOnErrorDialog',
                                   'Error',errMsg,'error',0,'OK',
                                   'Show Traceback','Debug')
    if (killWindow): window.destroy()
    if (1 == showTraceBack or '1' == showTraceBack):
        tkMessageBox.showinfo('Traceback',errTrace[0],parent=window)
    if (2 == showTraceBack or '2' == showTraceBack):
        window.destroy()
        window.quit()
        window.tk.quit()
        print errTrace[0]
        import pdb
        pdb.post_mortem(errTrace[1][2])
