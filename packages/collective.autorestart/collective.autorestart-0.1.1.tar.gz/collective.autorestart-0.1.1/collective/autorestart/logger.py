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

logger.setLevel(logging.DEBUG)