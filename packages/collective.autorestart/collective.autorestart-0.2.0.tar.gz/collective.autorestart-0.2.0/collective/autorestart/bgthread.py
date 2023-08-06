"""
    Background monitoring thread.

"""

__license__ = "GPL"
__author__  = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"
__copyright__ = "2009 Twinapex Research"
__docformat__ = "epytext"

# Python imports
import os, sys
import threading
import urllib
import urllib2
import time
import signal

# Zope imports
from OFS.Application import Application
import App.config 
import transaction

from Signals import Signals
from Signals.SignalHandler import SignalHandler # Zope signal handler
# Local imports
import monitor # file system monitoring interface
import scanner
from logger import logger # terminal output

# Check whether we have pygame + audio support
try:
    import pygame
    import audio
except ImportError:
    logger.warn("No pygame installed - you won't hear bells and whistles when Plone is restarted")
    audio = None

# http address to plone.reload view
plone_reload_url = None

# Zope 2 old style product paths
product_paths = None


def reload_plone(reload_mode):
    """ Trigger Plone reload. 
    
    Interact with Plone over normal HTTP interface so that we don't run into any Zope threading mines.
    
    @param reload_mode: "code" or "zcml"
    """

    logger.info("Reloading Plone")

    try:
        
        # TODO: zcml reload seems to break zope.schema.vocabularies         
        
        f = urllib2.urlopen(plone_reload_url, data=urllib.urlencode({"action" : reload_mode}))
        
        report = f.read()
        
        logger.info("Reloaded done, report:" + report)
        
        succeeded = True
    except Exception, e:        
        succeeded = False
        logger.error("Reload failed")
        logger.exception(e)
            
    if audio:
        # Play sound effect based on the result of reload
        
        if succeeded:
            sound = audio.get_sound("start.wav")
        else:
            sound = audio.get_sound("youfail.wav")
        
        audio.play(sound)
        


class MonitorThread(threading.Thread):
    """        
    Monitor files and if they are changed run plone.reload.
    """
    
    def reload(self):

        # Do not allow re-entrant
        if self.reloading:
            return
        
        
        self.reloading = True                    
        #scanner.mark_files(path)    
            
        # reload_plone()
        # Buffer FS monitor events, since 
        # we might receive many events per file and we want to reload only once
        reload_plone(self.reload_mode)
        
        self.reloading = False
    
    def detect_change(self, path):
        """ Monitor event callback, file or folder has changed.
        
        Monitor should trigger this callback only for real files we are monitoring.
        However, sometimes several events are fired for the same file.
        In that case ignore all but the first one.
        
        Set a thread flag indicating that the background thread
        should trigger plone.reload on succesful file change detect.
        Also, check whether we need to load only the changed .py file
        or all ZCML code (there is no partial ZCML reload).
        """
        logger.info("Detected file system change:" + path)


        # For some reason we get IN_MODIFY event
        # several times.
        # Ignore all except the first event
        # by checking whether the file stats have been changed
        stats = os.stat(path)
        
        old_stats = self.stats_cache.get(path, None)
        if old_stats:
            if stats == old_stats:
                logger.debug("Ignoring double IN_MODIFY events")
                return
        
        self.stats_cache[path] = stats
        
        if path.endswith(".zcml"):
            # For ZCML files, trigger ZCML reload
            self.reload_mode = "zcml"
        else:
            self.reload_mode = "code"

        self.need_reload = True            
        
    def run(self):
        """ Background thread entry point. """
        
        self.reloading = False
        self.need_reload = False # Set by notify callback to tell when we need to call plone.reload
        self.running = True
        self.reload_mode = "code"
        
        # Keep monitored file information to discriminate real .py file changes from notify noise
        self.stats_cache = {}
        
        try:
            #monitor.set_callback(self.detect_change)
                
            scanner.scan_python_paths(sys.path + product_paths)
            
            logger.debug("Background thread started")
                        
            try:
                
                # Poll loop which flushes inotify buffer
                while self.running:
                    #logger.debug("Running happily")
                    
                    # do_event_notifications blocks for a certain timeout
                    monitor.do_event_notifications()                                    
                                                    
                    if self.need_reload:                                
                        self.need_reload = False
                        self.reload()
                        
                print "Not running anymore"
                    
            except KeyboardInterrupt:
                # destroy the inotify's instance on this interrupt (stop monitoring)
                # Should not happen when signal module is available...
                #import thread
                raise RuntimeError("We are not a main thread - we should not receive CTRL+C")
                
            # TODO: this is never reached since daemon threads are 
            # forcelly terminated - can we shutdown cleanly?
            
            logger.info("Closing collective.autorestart")
            
            monitor.close()
        except Exception, e:
           logger.exception(e)
           #raise e
            
    def join(self, timeout=3):
        """ Override join method to try graceful dying. 
        
        Known issue: atexit() hangs to Thread.join(). Guess whether it is our thread.
        """
        self.running = False
        threading.Thread.join(self, timeout)
        
    def signal_callback(self):
        """ Make sure that we die properly on CTRL+C """
        
        # As Iron Maiden cleverly put it
        # ... time to die!
        logger.warn("Received SIGTERM/SIGINT, terminating monitoring loop")
        self.running = False
        
        
def init():
    """ Initialize monitoring system. 
    
    @return: True if we should start background file monitoring
    """

    global plone_reload_url, product_paths
    
    config = App.config.getConfiguration()
    
    
    if not config.debug_mode:
        # Do not start monitoring in production mode
        # Also config.debug_mode = False for unit tests so we cover
        # both non-use cases here
        return False
    
    server = config.servers[0] # conf.servers[0]
        
    plone_reload_url = "http://" + server.ip + ":" + str(server.port) + "/autoreload"
    
    logger.debug("plone.reload callback at " + plone_reload_url)
    
    product_paths = config.products
    
    return True


# Global to hold the background trhead object
background_thread = None

def thread_safe_shutdown_decorator(fn):
    """ Decorator for Zope signal functions.
    
    Make sure that file monitor thread is closed first,
    avoiding potential lock up problem in Py_Finalize() which 
    would wait lock in atexit.py / Thread.join() forever.
    """
    def wrapped(*args, **kws):
        print "Killing bg thread"        
        background_thread.running = False        
        time.sleep(0.6)
        return fn(*args, **kws)
    return wrapped
    
def start_monitor():    
    """ Launch the bg thread """
    global background_thread
    
    if not init():
        # Config has opted out from debugging/autoreload
        logger.warn("Plone not in debug mode - collective.autorestart disabled")
        return

    # Hack around the thread shutdown problem -
    # Make sure that Zope doesn't do anything funny
    # until we can clear pyinotify             
    Signals.shutdownFastHandler = thread_safe_shutdown_decorator(Signals.shutdownFastHandler)
    Signals.shutdownHandler = thread_safe_shutdown_decorator(Signals.shutdownHandler)
    
    thread = MonitorThread()    
    
    # Don't block Zope from dying when CTRL+C is pressed
    thread.daemon = True
    
    # Hacked init order to avoid lock up problems
    background_thread = thread    
    monitor.init()    
    monitor.set_callback(thread.detect_change)
    
    thread.start()
    