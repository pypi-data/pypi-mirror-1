"""Module representing configuration parameters.

This module collects together configuration parameters for pyfog applications.
If you are just looking at pyfog to get a sense of how to use superpy, you
can pretty much ignore this module and just look at fogMaker.py.
"""

import logging, os, optparse

def ConfProp(func):
    """Decorator to make a config item property.
    
    INPUTS:
    
    -- func:    Function containing name and docstring for property.
    
    -------------------------------------------------------
    
    RETURNS:    Function representing config property.
    
    -------------------------------------------------------
    
    PURPOSE:    Provide a simple way to make config item properties.

    Example usage is illustrated below:

>>> from config import ConfProp
>>> class foo(object):
...     def __init__(self):
...             self._bar = None     # actual property will refer to this
...     @ConfProp
...     def bar(self):
...             'The bar property is an example property.'
... 
>>> f = foo()
>>> f.bar = 5
>>> f.bar
5
    """

    privateName = '_' + func.__name__
    doc = func.__doc__
    def GenericGet(instance):
        "Return value."
        return getattr(instance, privateName)
    def GenericSet(instance, value):
        "Set value."
        setattr(instance, privateName, value)
    result = property(GenericGet, GenericSet, None, doc)
    return result

class GenericConfig(object):
    """Base class for generic configuration sections.
    """

    # Dictionary of string keys of configuration objects in self
    # and their default values.
    # Sub-classes should override with their own defaults.
    _defaults = {}

    # Dictionary of string keys of configuration objects in self
    # and the action to use for each. The default action 'store'
    # will be provided. Override only if you want special actions
    # (e.g., 'append') used for some items.
    _actions = {}
    
    @classmethod
    def UpdateParser(cls, parser, withDefaults):
        """Update OptionParser to parse args expected by this class.
        
        INPUTS:
        
        -- cls:        Class (usually supplied by python interpreter).
        
        -- parser:     Instance of optparse.OptionParser class.
        
        -- withDefaults:        Whether to include defaults in parser.
        
        -------------------------------------------------------
        
        PURPOSE:        Go through all configuration properties in cls,
                        and add entries for them to parser. If withDefaults,
                        is true, then default values are added to the parser.
        
        """
        for (name, item, default) in cls.GetProperties():
            if (not withDefaults): default = None
            parser.add_option(
                '--%s'%name, dest=name, help=item.__doc__,
                default = default, action=cls._actions.get(name, 'store'))

    @classmethod
    def GetProperties(cls):
        """Return list of configuration properties.
        
        -------------------------------------------------------
        
        RETURNS:        List of tuples of the form (name, item, default)
                        representing the name, property object and default
                        value for all configuration properties in the class.
        
        -------------------------------------------------------
        
        PURPOSE:        Provide a simple way to get config properties.
        
        """

        defaults = cls._defaults
        result = []
        for name in dir(cls):
            item = getattr(cls, name, None)
            if (isinstance(item, property)):
                result.append((name, item, defaults.get(name, None)))
        return result

    def SetFromOptions(self, options):
        """Set configuration properties in self from options.
        
        INPUTS:
        
        -- options:        Options parsed by optparse.OptionParser class.
        
        -------------------------------------------------------
        
        PURPOSE:        Sets the values of all configuration properties in
                        self from the values in options. Any values of None
                        are ignored and the old values are kept.
        
        """
        for (name, _ignore, _junk) in self.GetProperties():
            value = getattr(options, name, None)
            if (value is not None): setattr(self, name, value)

    def Validate(self):
        "Validate args in self; sub-classes should override"
        
        _ignore = self

    

class CountingSessionConfig(GenericConfig):
    """Configuration for test session.
    """

    _defaults = {
        'logLevel' : 'INFO',
        'outputFile' : '',
        'phraseLevel' : 2,
        'maxWords' : 30,
        'killRegexp' : '''(<[^<>]+>)|([()=.><,;:"'!?\[\]{}\\\\])|(&nbsp)''',
        'ignoreFile' : '',
        'webSourceFile' : '',
        'rssSourceFile' : '',
        }

    @ConfProp
    def phraseLevel(self):
        """Integer representing how many words to consider in a phrase.
        """

    @ConfProp
    def webSourceFile(self):
        """String name of file containing web sites to include as source.
        """

    @ConfProp
    def rssSourceFile(self):
        """Name of file containing web sites of rss feeds to use as source.
        """


    @ConfProp
    def ignoreFile(self):
        """String name of file containing patterns to ignore.

        Each line of the file contains a regular expression. Anything matching
        one of these regular expressions in the word counting stage will
        be ignored.
        """


    @ConfProp
    def logLevel(self):
        """String log-level (one of DEBUG, INFO, WARNING, CRITICAL, ERROR).
        """

    @ConfProp
    def killRegexp(self):
        """Regular expression for characters to kill/erase before counting.
        """

    @ConfProp
    def maxWords(self):
        """Maximum number of words to show results for.
        """

    @ConfProp
    def outputFile(self):
        """File to write output to. If not given, output is sent to stdout.
        """


    def __init__(self, *args, **kw):
        self._maxWords = None
        self._phraseLevel = None


        GenericConfig.__init__(self, *args, **kw)
        
    def Validate(self):
        """Validate arguments and raise exceptions if something is wrong.
        """
        self._maxWords = int(self._maxWords)
        self._phraseLevel = int(self._phraseLevel)        

class SuperpyConfig(GenericConfig):
    """Configuration for superpy usage.
    """

    _defaults = {
        'logLevel' : 'INFO',
        'localServers' : 4,
        'serverList' : 'None',        
        'domain' : '', 
        'password' : None,
        'user' : '',
        'remotePyPath' : os.getenv('PYTHONPATH',''),
        'remoteWorkDir' : '',  
        }

    @ConfProp
    def localServers(self):
        """Integer representing number of local superpy servers to spawn.

        In addition to using remove superpy servers, you can specify a
        number of local servers to spawn. The application will spawn that
        many servers, use them in processing, and shut them down when
        finished.

        This is mainly useful to take advantage of multi-processor or
        multi-core machines by running multiple processes in parallel.
        """

    @ConfProp
    def remotePyPath(self):
        """PYTHONPATH to use on remote machines.
        """

    @ConfProp
    def remoteWorkDir(self):
        """Directory to change to for working in.
        """


    @ConfProp
    def serverList(self):
        """Either 'None' or comma separated list of host:port:re triples.

        If present, this represents a list of superpy servers to parallelize
        tests to. For example, if you provide

          'USBODV30:9287,USBODV31:9287'

        then the servers USBODV30 and USBODV31 would be used each with
        port number 9287. Of course, you must make sure a superpy server
        is listening at the appropriate place.
        """

    @ConfProp
    def domain(self):
        """Network domain to use for remote tasks.

        This is used as the network domain when superpy is used to
        spawn tests remotely.
        """

    @ConfProp
    def user(self):
        """Username to use for remote tasks via superpy.

        This is used as the username when superpy is used to
        spawn tests remotely. If nothing is given, we try
        to read the default from the USERNAME or USER environment
        variable.
        """


    @ConfProp
    def password(self):
        """Password used to spawn remote tasks.
        """


    def __init__(self, *args, **kw):
        self._serverList = None
        self._localServers = None
        self._user = None
        self._password = None

        GenericConfig.__init__(self, *args, **kw)
        
    def Validate(self):
        """Validate arguments and raise exceptions if something is wrong.
        """
        self._localServers = int(self._localServers)
        if (self._user in [None, 'None', '']):
            self._user = os.getenv('USERNAME', os.getenv('USER', 'unknown'))
        if (self._serverList is None or self._serverList == 'None' or
            self._serverList == ''):
            self._serverList = None
        elif (isinstance(self._serverList,(str,unicode))): # split into lists
            myList = str(self._serverList)
            self._serverList = []
            for origItem in myList.split(','):
                item = origItem.split(':')
                if (len(item) == 2):
                    self._serverList.append((item[0], int(item[1])))
                else:
                    raise Exception('Could not parse serverList element %s.'
                                    % str(origItem))


def GetHome():
    """Determine and return home directory for user.
    """
    env = os.environ
    result = env.get('HOME',env.get('HOMEDRIVE',None))
    if (result is None):
        logging.warning('Could not determine home drive. Using c:/HOME')
        result = 'c:/HOME'
        if (not os.path.exists(result)): os.mkdir(result)
    if (not os.path.exists(result)):
        raise Exception('Home drive %s does not exists' % result)
    return result

        
class MetaConfig(GenericConfig):
    """Meta-configuration item that holds other config items.

    Sub-classes must define the following class variables:
    
        _subconfigs_:   List of pairs of the form (name, kls) where name is
                        the string name of a GenericConfig instance in self
                        and kls is the corresponding class for that item.
                        For example, if self.files contains a FileConfig
                        instance, subconfigs would be ['files', FileConfig].

        _conf_name_:    String used to determine configuration file name.
    """

    _subconfigs_ = None
    _conf_name_ = None

    def __init__(self, optionArgs=None, configFile = None):
        GenericConfig.__init__(self)

        # First create parser to read config file
        if (configFile is None):
            if (self._conf_name_ is None):
                raise Exception('Could not determine config file name.')
            else:
                configFile = os.path.join(GetHome(),'.pyfog_%s_rc'
                                          % self._conf_name_)

        if (not os.path.exists(configFile)):
            logging.warning('Config file %s does not exist; creating.'
                            % configFile)
            self.CreateDefaultConfigFile(configFile)

        self.SetFromConfigFile(configFile)

        # Next create parser to read the given options
        parser = optparse.OptionParser()
        self.UpdateParser(parser, withDefaults = False)        
        if (optionArgs is None): options, args = parser.parse_args()
        else: options, args = parser.parse_args(args = optionArgs)
        if (args): raise Exception('Invalid positional args: %s.' % str(args))
        self.SetFromOptions(options)

    def Validate(self):
        "Call validate on all children if possible."
        for (name, _kls) in self._subconfigs_:
            subConf = getattr(self, name)
            subConf.Validate()

    def CreateDefaultConfigFile(self, configFile):
        """Create default config file.
        
        INPUTS:
        
        -- configFile:        String name of where config file should go.
        
        -------------------------------------------------------
        
        PURPOSE:        Write out default config file based on default params.
        
        """
        fd = open(configFile, 'w')
        fd.write('# Configuration file for Fogger %s\n\n' % self._conf_name_)
        for (name, kls) in self._subconfigs_:
            fd.write('# Section for %s\n\n' % name)
            fd.write('# ' + '\n# '.join(kls.__doc__.split('\n')) + '\n\n')
            for (name, item, default) in kls.GetProperties():
                fd.write('\n')
                fd.write('# ' + '\n# '.join(item.__doc__.split('\n')) + '\n')
                if (default is None): fd.write('#%s=<value>\n' % name)
                else: fd.write('%s=%s\n' % (name, str(default)))
        fd.close()
        
    def SetFromConfigFile(self, configFile):
        """Set self based on values in given configFile.
        
        INPUTS:
        
        -- configFile:        String path to existing config file.
        
        -------------------------------------------------------
        
        PURPOSE:        Set values in self and child config objects based
                        on values in given config file.
        
        """
        parser = optparse.OptionParser()
        self.UpdateParser(parser, withDefaults = True)        
        fd = open(configFile, 'r')
        data = fd.read().split('\n')
        args = []
        for line in data:
            line = line.strip()
            if (not len(line)): pass
            elif (line[0] == '#'): pass
            else:
                args.append('--'+line)
        options, otherArgs = parser.parse_args(args = args)
        if (otherArgs):
            raise Exception('Invalid positional args: %s.' % str(otherArgs))
        self.SetFromOptions(options)
    
    @classmethod
    def UpdateParser(cls, parser, withDefaults):
        """Override UpdateParser to call UpdateParser for subconfigs.
        """
        for (_name, kls) in cls._subconfigs_:
            kls.UpdateParser(parser, withDefaults)

    def SetFromOptions(self, options):
        """Override SetFromOptions to call SetFromOptions for subconfigs.
        """        
        for (name, _kls) in self._subconfigs_:
            getattr(self, name).SetFromOptions(options)

class FoggerConfig(MetaConfig):
    """MetaConfig object containing configuration for tester.
    """

    _subconfigs_ = [
        ('session', CountingSessionConfig),
        ('superpy', SuperpyConfig),
        ]
    _conf_name_ = 'counter'

    def __init__(self, *args, **kw):
        self.session = CountingSessionConfig()
        self.superpy = SuperpyConfig()
        MetaConfig.__init__(self, *args, **kw)

