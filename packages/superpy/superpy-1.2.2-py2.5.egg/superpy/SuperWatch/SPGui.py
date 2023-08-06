"""SuperWatch is an application to script/launch/watch scripts via superpy
"""

import logging
import Pmw

import SPWidgets



def MakeMainSuperWatchWindow(rootWindow, defaults):
    """Make the main super watch window.
    
    INPUTS:
    
    -- rootWindow:        The main window to create GUI in.
    
    -- defaults:          Dictionary of default parameters for config page.
    
    -------------------------------------------------------
    
    RETURNS:    The pair (rootWindow, monitor) providing the parent window
                used to create everything and the master monitor object
                for SuperWatch.
    
    -------------------------------------------------------
    
    PURPOSE:    Build the GUI. User should call StartSuperWatchGUI which
                will call this.
    
    """

    monitor = SPWidgets.MasterMonitor(rootWindow, defaults)
    return rootWindow, monitor





def StartSuperWatchGUI(defaults=None, doMainLoop=True):
    """Start the GUI for SuperWatch
    
    INPUTS:
    
    -- defaults=None:        Dictionary of default arguments for config page.
    
    -- doMainLoop=True:      Wether to enter tk main loop.
    
    -------------------------------------------------------
    
    RETURNS:  The tuple (root, tk, monitor) representing the root window
              the tk instance, and the master monitor representing the
              super watch gui.
    
    -------------------------------------------------------
    
    PURPOSE:

    This function creates the main SuperWatch GUI window and then enters the
    Tk event loop (if doMainLoop is True).

    NOTE: Tk works weirdly on windows and so this function may never
          return if doMainLoop is True.
    """
    if (defaults is None):
        defaults = {}

    # Use getattr to supperss pylint warning
    myTkWindow = getattr(Pmw,'initialise')()
    myRootWindow, monitor = MakeMainSuperWatchWindow(myTkWindow, defaults)
    myRootWindow.title('SuperWatch')    
    monitor.notebook.selectpage('Config')

    if (doMainLoop):
        myTkWindow.mainloop()
        
    return (myRootWindow, myTkWindow, monitor)

if __name__ == "__main__":
    logging.info('Starting SuperWatch GUI.')
    (root, my_tk, myMonitor) = StartSuperWatchGUI()
    logging.info('Finished SuperWatch GUI.')

