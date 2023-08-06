"""Module providing MsgWindow class.
"""

import Tkinter
import Pmw
import GUIUtils

class MsgWindow:
    """Class to provide a message window to display application messages.

    This is useful to be able to show messages in a way that does not
    annoy the user but lets the messages persist until user has read
    them and then allow user to kill the message. See the MakeMsg method
    for details.
    """

    def __init__(self, rootWindow):
        """Initializer.
        
        INPUTS:
        
        -- rootWindow:        Parent window to create widget inside.
        """
        
        self.root = rootWindow
        self.frame = self._MakeMsgFrame(rootWindow)

    @classmethod
    def KillWindowAndChildren(cls, window):
        """Kill window and all its children.
        
        INPUTS:
        
        -- window:        Window to kill.n
        
        -------------------------------------------------------
        
        PURPOSE:        Kill a window and all its children. This is mainly
                        meant to be used internally to clean up old messages.
        
        """
        for (_name, child) in window.children.items():
            cls.KillWindowAndChildren(child)
        window.destroy()

    @staticmethod
    def _MakeMsgFrame(rootWindow):
        "Main main frame to hold messages."
        

        sframe = getattr(Pmw,'ScrolledFrame')(
            rootWindow, labelpos='n', horizflex='expand', vertflex='expand')
        _frame = sframe.interior()
        sframe.pack(fill='both',expand=True)
        return sframe

    def MakeMsg(self, title, msg):
        """Make a message and display it.
        
        INPUTS:
        
        -- title:        Short title for the message.
        
        -- msg:          Longer info about the message.
        
        -------------------------------------------------------
        
        PURPOSE:        Create an entry in the message frame showing
                        the given message.
        
        """
        frame = Tkinter.Frame(self.frame.interior(),relief='raised',bd=2,
                              padx=1,pady=1)
        show = Tkinter.Button(
            frame, text=title, padx=2, pady=2,
            command=lambda : GUIUtils.MakeTextDialog(
            title="Details on %s" % title,text=msg))
        kill = Tkinter.Button(
            frame, text='Kill', padx=2, pady=2,
            command=lambda : self.KillWindowAndChildren(frame))
        
        frame.pack(side='top',fill='x',expand=True)
        kill.pack(side='left',expand=False)        
        show.pack(side='left',fill='x',expand=True)
        
        return frame
        

