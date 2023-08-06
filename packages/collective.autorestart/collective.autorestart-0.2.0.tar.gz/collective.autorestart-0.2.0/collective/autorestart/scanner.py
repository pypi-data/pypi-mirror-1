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

# Don't monitor system files
BAD_PATH_MATCHES = ["/usr/lib", "zope2/lib", ".svn", ".git", ".bzr", "locale/", "locales/", "/var/lib/python-support", "EGG-INFO" ]

#: If these files change, restart Zope
MONITOR_EXTENSIONS = [ ".py", ".zcml" ]

path_count = 0

file_count = 0

def mark_files(path, nested):
    """ Recursive scan for wanted files. 
    
    @param path: File system path as a string
    @param nested: True if the path is potential Python submodule (not a top level folder in PYTHONPATH)
    """
    global path_count, file_count
    #print "Got:" + path
    
    if not type(path) in types.StringTypes:
        raise RuntimeError("Bad path:" + str(path))

    if not os.path.exists(path):
        logger.warn("Path got lost:" + path)
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

        if not "__init__.py" in os.listdir(path) and nested:
            # This path is not a Python module
            logger.debug("Not a Python module")
            return 
        
        path_count += 1
        
        # Recurse to subdir
        files = os.listdir(path)
        for f in files:
            fpath = os.path.join(path, f)
            mark_files(fpath, True)        
            
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
        logger.debug("Scanning root path:" + path)
        mark_files(path, False)
        
    # Scan Zope special folders

        
    logger.info("Monitoring %d paths, %d files for changes" % (path_count, file_count))
        

