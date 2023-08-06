#
# Copyright 2008, BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Jens Klein <jens@bluedynamics.com>"""              
__docformat__ = 'plaintext'

from zope.interface import Interface

class ITimezoneFactory(Interface):
    """Find the current timezone as pytz timezone."""

    def __call__():
        """perform the detection."""
        
