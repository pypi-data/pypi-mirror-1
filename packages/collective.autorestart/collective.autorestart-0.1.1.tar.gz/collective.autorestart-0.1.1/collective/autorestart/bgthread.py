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

# Zope imports
from OFS.Application import Application
import App.config 
import transaction

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

def reload_plone():
    """ Trigger Plone reload. 
    
    Interact with Plone over normal HTTP interface so that we don't run into any Zope threading mines.
    """

    logger.info("Reloading Plone")


    try:
        
        # TODO: zcml reload seems to break zope.schema.vocabularies 
        f = urllib2.urlopen(plone_reload_url, data=urllib.urlencode({"action" : "code"}))
        
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
    
    def detect_change(self, path):
        """ Monitor event callback, file or folder has changed.
        
        """
        
        if self.reloading:
            return
        
        # Do not allow re-entrant
        self.reloading = True
                
        logger.info("Detected file system change:" + path)
                
        #scanner.mark_files(path)    
            
        # reload_plone()
        # Buffer FS monitor events, since 
        # we might receive many events per file and we want to reload only once
        reload_plone()
        
        self.reloading = False
                                    
    
    def run(self):
        """ Background thread entry point. """
        
        self.reloading = False
        self.need_reload = False
        
        try:
            monitor.set_callback(self.detect_change)
                
            scanner.scan_python_paths(sys.path + product_paths)
            
            logger.debug("Background thread started")
                        
            try:
                
                # Poll loop which flushes inotify buffer
                while True:
                    monitor.do_event_notifications()                                    
                    time.sleep(0.5)
                    
                    if self.need_reload:                
                        self.need_reload = False
                    
            except KeyboardInterrupt:
                # destroy the inotify's instance on this interrupt (stop monitoring)
                pass
            
            # TODO: this is never reached since daemon threads are 
            # forcelly terminated - can we shutdown cleanly?
            
            logger.debug("Closing collective.autorestart")
            
            monitor.close()
        except Exception, e:
            logger.exception(e)
        
        
        
def init():
    """ Initialize monitoring system. """

    global plone_reload_url, product_paths
    
    config = App.config.getConfiguration()
    
    server = config.servers[0] # conf.servers[0]
        
    plone_reload_url = "http://" + server.ip + ":" + str(server.port) + "/autoreload"
    
    logger.info("Calling plone.reload at " + plone_reload_url)
    
    product_paths = config.products

    monitor.init()    
    
def start_monitor():    
    """ Launch the bg thread """
    
    init()

    
    thread = MonitorThread()
    
    # Don't block Zope from dying when CTRL+C is pressed
    thread.daemon = True
    
    thread.start()
        