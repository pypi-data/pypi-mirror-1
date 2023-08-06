"""

    Simple hardcoded logger configuration

"""

__license__ = "GPL"
__author__  = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"
__copyright__ = "2009 Twinapex Research"
__docformat__ = "epytext"

# Python imports
import logging

logger = logging.getLogger("collective.autorestart")

logger.propagate = False # Do not pass messages to the parent loggers
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

logger.addHandler(handler)
logger.setLevel(logging.INFO)

