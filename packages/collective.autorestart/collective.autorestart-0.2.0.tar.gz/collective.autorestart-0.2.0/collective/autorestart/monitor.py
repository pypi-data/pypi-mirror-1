"""
    Simple abstraction interface over inotify for Linux.
    
    Alternative operating systems can be supported by rewriting this module for them.

"""

__license__ = "GPL"
__author__  = "Mikko Ohtamaa <mikko@redinnovation.com>"
__copyright__ = "2008 Red Innovation Ltd."
__docformat__ = "epytext"

# Python imports
import os

# Dependency imports
import pyinotify

from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent

from logger import logger
#: Callback function which is triggered on fs event. Takes full file path as a string argument.
callback = None

#: Watch manager instance
wm = None

#: Watch handle
wdd = None

#: Notified with hooks
notifier = None

def init():
    global wm, notifier
    wm = WatchManager()
    notifier = ThreadedNotifier(wm, CheckCreateDeleteChanged(), timeout=0.5)    
    notifier.start()
        
def monitor(path):
    """ Start monitoring a file system path """
    #mask = EventsCodes.IN_DELETE | EventsCodes.IN_CREATE | EventsCodes.IN_MODIFY # watched events
    
    
    # Magically broken below
    # EventsCodes.IN_DELETE | EventsCodes.IN_CREATE | EventsCodes.IN_MODIFY # watched events
    mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY|pyinotify.IN_DELETE_SELF # watched events
    wdd = wm.add_watch(path, mask, rec=False, auto_add=False)

def do_event_notifications():
    """ Purge inotify event loop """
    
    if notifier:
        # process the queue of events as explained above    
        notifier.process_events()
        if notifier.check_events():
            # read notified events and enqeue them
            notifier.read_events()
        # you can do some tasks here...

class CheckCreateDeleteChanged(ProcessEvent):
    """ inotify wrapper callback.
    
    Listen to file create, delete and change events.
    
    When something happens, call our custom reload hook.
    """
    
    def process_default(self, event):
        #logger.info("Got event:" + str(pyinotify.EventsCodes.maskname(event.mask)))
        callback(event.path)
        
def set_callback(cb):
    """
    Set callback function which is called when FS change is deteced.
    
    @param cb: Python callable object or function
    """
    global callback
    callback = cb
    
def close():
    """ Stop monitoring fiel system. """
    global notifier
    notifier.stop()
    notifier = None
    wm = None

    
        
