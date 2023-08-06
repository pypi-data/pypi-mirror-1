"""Script to start SuperWatch application
"""

import logging
from superpy.SuperWatch import SPGui

if __name__ == "__main__":
    logging.info('Starting SuperWatch GUI.')
    (root, my_tk, myMonitor) = SPGui.StartSuperWatchGUI()
    logging.info('Finished SuperWatch GUI.')

