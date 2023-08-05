# Copyright 2007, Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 
#
__author__ = """Jens Klein <jens@bluedynamics.com>"""

from zope.interface import Interface
from plone.portlets.interfaces import IPortletDataProvider

class ISkypeNameFetcher(Interface):
    """An class implementing this interface is supposed to know how to collect
    skype usernames."""
    
    def __call__():
        """A sorted list with dicts of skype userinfo. The dict has at least one
        wntry with key 'name'."""
    

class ISkypePortlet(IPortletDataProvider):
    """A portlet rendering the skype contacts.
    """    