"""Graphical User Interface for pyfog.

See instructions at http://code.google.com/p/superpy/wiki/PyFog.
"""

import sys, os
import Tkinter
from superpy.SuperWatch import GUIUtils, GUIValidators
from superpy.demos.pyfog import defaults, fogger



class PyFogCmd(GUIUtils.GenericGUICommand):
    """Class to provide main pyfog gui command.
    """

    def __init__(self, name='PyFog'):
        argList = self._MakeArgList()
        GUIUtils.GenericGUICommand.__init__(
            self, name, self.run, argList=argList)

    @staticmethod
    def _MakeArgList():
        """Make argument list.

        Returns list of triples of the form
          
                            (argName, argValidator, argDoc)

        representing arguments for command.
        """
        return [
            ('phraseLevel', GUIValidators.IntValidator(default=5),'''
            Integer representing how many words to consider in a phrase.
            '''),
            ('maxWords', GUIValidators.IntValidator(default=40),'''
            Integer representing how many words to show results for.
            '''),            
            ('webSourceFile', GUIValidators.ExistingFileNameValidator(
            initialDir=defaults.__path__[0]),'''
            String name of file containing web sites to include as source.
            '''),
            ('rssSourceFile', GUIValidators.ExistingFileNameValidator(
            initialDir=defaults.__path__[0],
            default=os.path.join(defaults.__path__[0],'exampleRSS.txt')),'''
            String name of file containing RSS feeds to include as source.
            '''),
            ('logLevel', GUIValidators.LogLevelValidator('INFO'), '''
            How much logging information to show.
            '''),
            ('localServers', GUIValidators.IntValidator(default=4),'''
            Integer representing number of local superpy servers to spawn.

            In addition to using remove superpy servers, you can specify a
            number of local servers to spawn. The application will spawn that
            many servers, use them in processing, and shut them down when
            finished.

            This is mainly useful to take advantage of multi-processor or
            multi-core machines by running multiple processes in parallel.
            '''),
            ('serverList', GUIValidators.StringValidator(),"""
            Either blank or a comma separated list of host:port tuples.

            If present, this represents a list of superpy servers to parallelize
            tests to. For example, if you provide 'USBODV30:9287,USBODV31:9287'

            then the servers USBODV30 and USBODV31 would be used each with
            port number 9287. Of course, you must make sure a superpy server
            is listening at the appropriate place.
            """),
            ('user', GUIValidators.StringValidator(
            os.getenv('USER', os.getenv('USERNAME', ''))), '''
            Username to use for remote tasks via superpy.

            This is used as the username when superpy is used to
            spawn tests remotely. If nothing is given, we try
            to read the default from the USERNAME or USER environment
            variable.
            '''),
            ('domain', GUIValidators.StringValidator(), '''
            Network domain to use for remote tasks.

            This is used as the network domain when superpy is used to
            spawn tests remotely.
            '''),
            ('password', GUIValidators.StringValidator(), '''
            Password to use for remote superpy tasks.
            '''),
            ]

    def run(self):
        """Do the main work of running the pyfog command.
        """
        argv = []
        for (argName, argDataDict) in self.argDict.items():
            value = argDataDict['value']
            if (value not in ['', 'None', None]):
                argv.append('--%s=%s' % (argName, value))
        result = fogger.Run(argv)
        w = GUIUtils.MakeTextDialog(title='PyFog Results',text=result,grab=1)
        w.wait_window()


if __name__ == "__main__":
    window = Tkinter.Tk()
    while window:
        cmd = PyFogCmd('pyfog')
        window = cmd(window)
        window.tk.call('grab','set',window)
        window.lift()
        window.wait_window()
        window = None
    sys.exit()
