"""
    Listen to SIGUSR1 signal and dump Python threads 
    
    You need to have threaddump egg to run this.

"""

__license__ = "GPL"
__author__  = "Mikko Ohtamaa <mikko@redinnovation.com>"
__copyright__ = "2008 Red Innovation Ltd."
__docformat__ = "epytext"

import sys, traceback
import signal

from logger import logger

OUTFILE = "zope-threaddump.txt"


def dump_threads(file):
    """ Dump Python threads.
    """
    import threadframe       
    
    print >> file, "Dumping Zope threads"
    
    frames = threadframe.dict()
    for thread_id, frame in frames.iteritems():
        print >> file, '-' * 72
        print >> file, '[%s] %d' % (thread_id, sys.getrefcount(frame))
        traceback.print_stack(frame, file=file)

def signal_handler(signum, frame):
    """ Allow external signal to come in and do thread dump. 
    
    
    """
    print "Received SIGUSR1 - trying to a thread dump"
    f = open(OUTFILE, "wt")        
    dump_threads(f)            
    f.close()
    
def start():
    
    try:
        import threadframe       
    except ImportError:
        logger.warn("threadframe module not installed")
        logger.warn("Egg available at http://pypi.python.org/pypi/threadframe/0.2")
        return
        
    logger.info("thread dump handler installed - use killall -SIGUSR1 python2.4 to invoke")
    
    signal.signal(signal.SIGUSR1, signal_handler)
