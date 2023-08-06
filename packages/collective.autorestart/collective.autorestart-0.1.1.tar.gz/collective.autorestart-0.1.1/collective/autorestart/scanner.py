"""
    Folder tree walking and file matching functions.

"""

__license__ = "GPL"
__author__  = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"
__copyright__ = "2009 Twinapex Research"
__docformat__ = "epytext"

import os, sys
import types

import monitor

from logger import logger

#: Which files/directories are not included in the monitoring, since Plone detects changes in these automatically
#: skins folder contains RestrictedPython scripts which are not normal python though they have .py extension
#: profiles contain only GenericSetup XML which is read from FS every time quick installer is run.
MONITOR_BLACKLIST = [ "skins", "profiles" ]

# Don't monitor system files
BAD_PATH_MATCHES = ["/usr/lib", "zope2/lib", ".svn", ".git", ".bzr", "locale/", "locales/", "/var/lib/python-support", "EGG-INFO" ]

#: If these files change, restart Zope
MONITOR_EXTENSIONS = [ ".py", ".zcml" ]

path_count = 0

file_count = 0

def mark_files(path):
    """ Recursive scan for wanted files. """
    global path_count, file_count
    #print "Got:" + path
    
    if not type(path) in types.StringTypes:
        raise RuntimeError("Bad path:" + str(path))

    if not os.path.exists(path):
        logger.warn("Path got lost:" + path)
        return 
    
    folder, fname = os.path.split(path)
    if fname in MONITOR_BLACKLIST:
        # Don't do restart on blacklisted files        
        logger.debug("Blacklisted path part:" + path)
        return
    
    # Filter out system paths
    for match in BAD_PATH_MATCHES:
        if match in path:
            logger.debug("Blacklisted:" + path)
            return
        
    # We need to resolve links here,
    # or inotify monitors symlink inode
    if os.path.islink(path):
        path = os.path.realpath(path)
        
    
    if os.path.isdir(path):
        
        logger.debug("Found path:" + path)
        
        path_count += 1
        
        # Recurse to subdir
        files = os.listdir(path)
        for f in files:
            fpath = os.path.join(path, f)
            mark_files(fpath)        
            
        # TODO: path itself is not monitored
        # new files are not detected
        
    else:
                
        base, ext = os.path.splitext(path)

        if ext in MONITOR_EXTENSIONS:
            # Match filemask
            #print "Marking " + path
            monitor.monitor(path)

            file_count += 1

def scan_python_paths(paths):
    """ Mark all files in PYTHONPATH to be monitored. 
    
    @param paths: array of paths
    """

    # Scan normal python path
    for path in paths:
        logger.info("Scanning root path:" + path)
        mark_files(path)
        
    # Scan Zope special folders

        
    logger.info("Monitoring %d paths, %d files for changes" % (path_count, file_count))
        

