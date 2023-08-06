"""Module containing the Validator class and sub-classes.

See docs on Validator class to start.
"""

import Tkinter
import datetime, os, re

class Validator:
    """A class to validate an argument type.

    The Validator class serves as a basic interface for ways to validate
    user input. Sub-classes can override methods to provide fancier
    input methods and validation.
    """
    
    def __init__(self,default = None, options=None, meOptions=None):
        if(options is None): options = []
        if(default is None): default = ''
        self.default = default
        self.options = options
        self.meOptions = meOptions
        
    def Validate(self,arg):
        """
        Validate(self,arg):
        
        Make sure that arg has the valid type and raise an exception
        otherwise.  If succesful, return (the possibly modified) argument.
        """
        _ignroe = self
        return arg

    def __call__(self,arg):
        return self.Validate(arg)

    def MakeMenuEntry(self,argFrame):
        """
        MakeMenuEntry(self,argFrame):

        argFrame:  A frame to create an entry for the argument in.

        This function will be called by the GUI to create the entry
        for the argument represented by a Validator instance.  This
        function should create an entry object that supports the
        get()/set(...) methods and create a menuEntry object that
        can be gridded into argFrame to allow the user to modify
        the given entry.

        The return value is (menuEntry, entry).
        """
        entry = Tkinter.StringVar()
        menuEntry = Tkinter.Entry(argFrame,textvariable=entry)
        if (self.meOptions is not None and len(self.meOptions)):
            menuEntry.configure(**self.meOptions)
        if (None != self.default):
            entry.set(self.default)
        return (menuEntry,entry)

class BooleanValidator(Validator):
    "Validate a boolean value"
    
    def __init__(self,default=0):
        Validator.__init__(self,default=default)

    def Validate(self,arg):
        "Override validate to handle booleans"
        if (str == type(arg)):
            arg = arg.strip()
        if (None == arg or 0 == arg or '' == arg or '0' == arg or
            False == arg or 'False' == arg):
            return 0
        else:
            return 1

    def MakeMenuEntry(self,argFrame):
        "Override to show as checkbutton"
        entry = Tkinter.StringVar()
        menuEntry = Tkinter.Checkbutton(argFrame,variable=entry)
        entry.set(self.default)
        return (menuEntry,entry)


class DateValidator(Validator):
    """A class to validate a date of the form year-month-day
    """

    def __init__(self,default=None,allowNone=False):
        self.format = '%Y-%m-%d'
        self.allowNone = allowNone
        if (None == default): default = datetime.date.today()
        elif (isinstance(default,(str,unicode))):
            default = datetime.datetime.strptime(default,self.format).date()
            
        Validator.__init__(self,default=default.strftime(self.format))

    def Validate(self,arg):
        "Override to validate date."
        if (self.allowNone and arg == 'None' or arg == "'None'" or arg is None):
            return None
        else:
            return datetime.datetime.strptime(arg,self.format).date()

class DateTimeValidator(Validator):
    """Class to validate a date AND TIME

    Expects a string of the form year-month-day hour:minute:second
    """

    def __init__(self,default=None,allowNone=False):
        self.format = '%Y-%m-%d %H:%M:%S'
        self.allowNone = allowNone
        if (None == default): default = datetime.datetime.now()
        elif (isinstance(default,(str,unicode))):
            default = datetime.datetime.strptime(default,self.format)
            
        Validator.__init__(self,default=default.strftime(self.format))

    def Validate(self,arg):
        "Override to validate datetime."
        
        if (self.allowNone and arg == 'None' or arg == "'None'" or arg is None):
            return None
        else:
            return datetime.datetime.strptime(arg,self.format)

class ChooseOneFromListValidator(Validator):
    """
    A class to validate choosing one type from a set.
    """
    def __init__(self,options, default):
        Validator.__init__(self,default = default, options= options)
        self.myEntry = None
        self.myMenuEntry = None

    def Validate(self,arg):
        "Override to check list membership"
        if (self.options.count(arg)):
            return arg
        else:
            raise Exception, ('Invalid choice %s.  Must be one of %s.' % (
                str(arg), str(self.options)))

    def MakeMenuEntry(self,argFrame):
        "Override to use OptionMenu"
        entry = Tkinter.StringVar()
        menuEntry = Tkinter.OptionMenu(argFrame, entry, *self.options)
        entry.set(self.default)
        self.myEntry = entry
        self.myMenuEntry = menuEntry
        return (menuEntry,entry)

    def ResetMenu(self, newMenu):
        "Reset menu when necessary"
        menu = self.myMenuEntry.children['menu']
        menu.delete(0,Tkinter.END)
        self.options = newMenu
        for val in newMenu:
            def MyCallback(v=self.myEntry, l=val):
                "Simple callback to set value"
                v.set(l)
            menu.add_command(label=val, command=MyCallback)
            

class BooleanPulldownValidator(ChooseOneFromListValidator):
    "Validator for Boolean from pulldown menu"
    def __init__(self,default='False'):
        ChooseOneFromListValidator.__init__(self,options=['True','False'],
                                            default=str(default))

    def Validate(self,arg):
        "Validate boolean"
        if (0 == arg or 'False' == arg):
            return False
        elif (1 == arg or 'True' == arg):
            return True
        else:
            raise Exception, ('Must be one of ["True","False"].')

class LogLevelValidator(ChooseOneFromListValidator):
    "Validator to choose log level"
    def __init__(self,default='WARNING'):
        ChooseOneFromListValidator.__init__(
            self,options=['CRITICAL','ERROR','WARNING','INFO','DEBUG'],
            default=default)

class YesNoValidator(ChooseOneFromListValidator):
    "Validator to choose yes/no"
    def __init__(self,default):
        ChooseOneFromListValidator.__init__(self,options = ['yes','no'],
                                            default = default)

class StringValidator(Validator):
    "Validator for generic string"
    
    def __init__(self, default = '', meOptions=None):
        Validator.__init__(self, default = default, meOptions=meOptions)

class FloatValidator(Validator):
    "Validator for floating point value."
    
    def __init__(self,minVal=None,maxVal=None,default=None):
        self.minVal=minVal
        self.maxVal=maxVal
        Validator.__init__(self,default=default)

    def Validate(self,arg):
        "Validate float"
        if (isinstance(arg,(str,unicode))): arg = arg.replace(',','').strip()
        if ((arg is None) or arg == 'None' or arg == ''): return None
        value = float(arg)
        if (None != self.minVal and value < self.minVal):
            raise Exception, ('Value ' + `value` +
                              ' too small; minimum allowed value = ' +
                              `self.minVal` + '.')
        if (None != self.maxVal and value > self.maxVal):
            raise Exception, ('Value ' + `value` +
                              ' too big; maximum allowed value = ' +
                              `self.maxVal` + '.')
        return value

class StringItemDictValidator(Validator):
    """Validator for dictionary with string keys and user defined values.

    This is meant to be sub-classed by setting _typeConverter_
    """
    _typeConverter_ = lambda x : x #Set to type converter like float or int

    def __init__(self, default=None):
        Validator.__init__(self,default=default)

    def Validate(self, arg):
        "Validate the argument."
        
        if (arg is None or arg == 'None' or arg == ''): arg = {}
        elif (isinstance(arg, dict)): pass
        elif (isinstance(arg,(str,unicode))):
            arg = arg.split(',')
            arg = dict([(s.split(':')[0],self._typeConverter_(s.split(':')[1]))
                        for s in arg])
        else:
            raise Exception('Invalid value %s for %s.' % (
                str(arg), self.__class__.__name__))
        return arg

class PairItemListValidator(Validator):
    """Validator for list of pairs.

    This is meant to be sub-classed by setting _typeConverters_
    """
    _typeConverters_ = [lambda x : x]*2 #Set to type converter like float or int

    def __init__(self, default=None):
        Validator.__init__(self,default=default)

    def Validate(self, arg):
        "Validate the argument."
        
        if (arg is None or arg == 'None' or arg == ''): arg = []
        elif (isinstance(arg, (list, tuple))): pass
        elif (isinstance(arg,(str,unicode))):
            arg = arg.split(',')
            arg = [(self._typeConverters_[0](s.split(':')[0]),
                    self._typeConverters_[1](s.split(':')[1]))
                   for s in arg]
        else:
            raise Exception('Invalid value %s for %s.' % (
                str(arg), self.__class__.__name__))
        return arg

class StringIntListValidator(PairItemListValidator):
    """Sequence of string:int pairs.
    """
    _typeConverters_ = [str, int]

class StringFloatDictValidator(StringItemDictValidator):
    """Validator for dictionary with string keys and float values.

    For example, one could specify a:1,b:2.5 to specify the dictionary
    {'a' : 1, 'b' : 2.5}.
    """
    _typeConverter_ = float

class StringIntDictValidator(StringItemDictValidator):
    """Validator for dictionary with string keys and int values.

    For example, one could specify a:1,b:2 to specify the dictionary
    {'a' : 1, 'b' : 2}.
    """
    _typeConverter_ = int

class StringStringDictValidator(Validator):
    """Validator for dictionary with string keys and string values.

    For example, one could specify a:c,b:d to specify the dictionary
    {'a' : 'c', 'b' : 'd'}.
    """

    def __init__(self, default=None):
        Validator.__init__(self,default=default)

    def Validate(self, arg):
        "Validate the argument."

        stripQuotes = lambda s: s.strip().strip('"').strip("'").strip()
        if (arg is None or arg == 'None' or arg == ''): arg = {}
        elif (isinstance(arg, dict)): pass
        elif (isinstance(arg,(str,unicode))):
            arg = arg.lstrip('{').rstrip('}').split(',')
            arg = dict([(stripQuotes(s.split(':')[0]),
                         stripQuotes(s.split(':')[1])) for s in arg])
        else:
            raise Exception('Invalid value %s for StringStringDict.' % str(arg))
        return arg

class IntegerValidator(Validator):
    "Validator for integer"
    def __init__(self,minVal=None,maxVal=None,default=None):
        self.minVal=minVal
        self.maxVal=maxVal
        Validator.__init__(self,default=default)

    def Validate(self,arg):
        "Validate integer"
        if (isinstance(arg,(str,unicode))): arg = arg.replace(',','').strip()
        if ((arg is None) or arg == 'None' or arg == ''): return None
        value = long(arg)
        if (None != self.minVal and value < self.minVal):
            raise Exception, ('Value ' + `value` +
                              ' too small; minimum allowed value = ' +
                              `self.minVal` + '.')
        if (None != self.maxVal and value > self.maxVal):
            raise Exception, ('Value ' + `value` +
                              ' too big; maximum allowed value = ' +
                              `self.maxVal` + '.')
        return value

IntValidator = IntegerValidator # alias for IntegerValidator

class FileNameValidator(Validator):
    "Validator for file name"
    
    def __init__(self,mustexist,initialDir=None,default=None):
        self.default=default
        Validator.__init__(self,default=default)
        if (None == initialDir):
            initialDir = os.getcwd()
        self.initialDir = initialDir
        self.mustexist = mustexist

    def Validate(self,arg):
        "Validate valid filename"
        if (self.mustexist and None != arg and '' != arg.strip()
            and not os.path.exists(arg)):
            raise Exception, ('No file named ' + `arg` + ' exists.')
        elif ('<' in arg or '>' in arg):
            raise Exception('File name %s has forbidden characters like <,>.'
                            % arg)
        else:
            return arg

    def MakeMenuEntry(self,argFrame):
        "Create menu entry to browse for file"

        browseFrame = Tkinter.Frame(argFrame)
        entry = Tkinter.StringVar()
        menuEntry = Tkinter.Entry(browseFrame,textvariable=entry)
        browseButton = Tkinter.Button(
            browseFrame,text='(Browse)',command=
            lambda :BrowseForFile(browseFrame,entry,self.initialDir,
                                  self.mustexist))
        menuEntry.pack(side='top',expand=1,fill='x')
        browseButton.pack(side='top',expand=1,fill='x')
        entry.set(self.default)

        return (browseFrame,entry)

    
class ExistingFileNameValidator(FileNameValidator):
    "Validator for file that must exist"
    
    def __init__(self,initialDir=None,default=None):
        FileNameValidator.__init__(self,initialDir=initialDir,mustexist=True,
                                   default=default)

class ExistingOrNonExistingFileNameValidator(FileNameValidator):
    "Validator for file that may or may not exist"
    
    def __init__(self,initialDir=None,default=None):
        FileNameValidator.__init__(self,initialDir=initialDir,mustexist=False,
                                   default=default)


def BrowseForFile(parentWindow,stringVarToSet,initialDir,mustexist):
    """
    BrowseForFile(parentWindow,stringVarToSet):

    parentWindow:     Window to open dialog near.
    stringVarToSet:   A StringVar (or anything else with a set method) that
                      is set to the selected file.
    initialDir:       Directory to start dialog in.
    mustexist:        Whether the file must exist or not.

    When this function is invoked, it creates a dialog box that the user
    can use to select a file.
    """
    if (mustexist): command = 'tk_getOpenFile'
    else: command = 'tk_getSaveFile'
    stringVarToSet.set(parentWindow.tk.call(
        command,'-parent',parentWindow,'-initialdir',initialDir))

class DirNameValidator(Validator):
    """Class to validate directory names.
    """
    def __init__(self,initialDir=None,mustExist=False,default=None):
        if (default is not None):
            if (initialDir is None): initialDir = default
            else: raise Exception(
                'default is alias for initialDir; only one should be non-None')
        if (initialDir is None):
            initialDir = os.getcwd()
        Validator.__init__(self,default = initialDir)            
        self.initialDir = initialDir
        self.mustExist = mustExist

    def Validate(self,arg):
        "Validate dir name"
        
        if (self.mustExist and
            None != arg and '' != arg.strip() and not os.path.exists(arg)):
            raise Exception, ('No directory named ' + `arg` + ' exists.')
        else:
            return arg

    def MakeMenuEntry(self,argFrame):
        "Make menu entry to browse"

        browseFrame = Tkinter.Frame(argFrame)
        entry = Tkinter.StringVar()
        if (None != self.default): entry.set(self.default)        
        menuEntry = Tkinter.Entry(browseFrame,textvariable=entry)
        browseButton = Tkinter.Button(
            browseFrame,text='(Browse)',command=
            lambda :BrowseForDir(browseFrame,entry,self.initialDir,
                                 self.mustExist))
        menuEntry.pack(side='top',expand=1,fill='x')
        browseButton.pack(side='top',expand=1,fill='x')

        return (browseFrame,entry)

def BrowseForDir(parentWindow,stringVarToSet,initialDir,mustExist):
    """
    BrowseForExistingDir(parentWindow,stringVarToSet,mustExist):

    parentWindow:     Window to open dialog near.
    stringVarToSet:   A StringVar (or anything else with a set method) that
                      is set to the selected directory.
    initialDir:       Directory to start dialog in.
    mustExist:        Boolean indicating if the directory must already exist.

    When this function is invoked, it creates a dialog box that the user
    can use to select an existing directory.
    """
    stringVarToSet.set(parentWindow.tk.call(
        'tk_chooseDirectory','-parent',parentWindow,'-initialdir',initialDir,
        '-mustexist',mustExist))

class SafeNameValidator(Validator):
    """Forces argument to be a safe string with no strange characters.
    """

    def Validate(self,arg):
        "Validate string is safe"
        regexp = '^[a-zA-Z_]+[a-zA-Z_0-9]*$'
        if (re.compile(regexp).match(arg)):
            return arg
        else:
            raise Exception, """
            Input %s has some strange characteres. It should contain only
            letters, numbers, or _ and cannot start with a number.
            """ % `arg`
        
class EmailValidator(Validator):
    """List of email addresses.
    """

    def __init__(self,default=None):
        if (None == default):
            default = os.getenv('USER',os.getenv('USERNAME'))
        Validator.__init__(self,default=default)

class CSVListValidator(Validator):
    """Comma separated list of strings vaildator.

    This class provides a validator that requires a string containing N
    values separated by commas where N can be in a specified range.
    """

    def __init__(self,default='',allowedValues=set([])):
        self.allowedValues = allowedValues
        Validator.__init__(self,default = default)

    def Validate(self,arg):
        "Validate arg"
        if (isinstance(arg,(tuple,list))): # if it's not a string
            arg = str(arg) # convert back to a string for consistencny        
        if (not isinstance(arg,(str,unicode))):
            raise Exception("Input '%s' is not a string." % arg)
        result = [a.strip() for a in arg.split(',')]
        if (len(result) not in self.allowedValues):
            raise Exception("Got %i values from %s but expected %s." % (
                len(result),arg,self.allowedValues))
        return result
            

            
