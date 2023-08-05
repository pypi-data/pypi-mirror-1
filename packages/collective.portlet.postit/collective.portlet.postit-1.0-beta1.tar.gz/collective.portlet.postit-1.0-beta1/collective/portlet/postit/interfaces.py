# Copyright 2007, Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 
#
__author__ = """Jens Klein <jens@bluedynamics.com>"""

from zope.interface import Interface
from plone.portlets.interfaces import IPortletDataProvider

class IPostIt(Interface):
    """Marker interface for .postit.PostIt
    """

class IPostitFetcher(Interface):
    """An class implementing this interface is supposed to know how to collect
    postits.
    """
    
    def __call__():
        """A sorted list of dicts with at least 'text' and 'creator' as keys.
        """    

class IPostitPortlet(IPortletDataProvider):
    """A portlet rendering the postits.
    """    