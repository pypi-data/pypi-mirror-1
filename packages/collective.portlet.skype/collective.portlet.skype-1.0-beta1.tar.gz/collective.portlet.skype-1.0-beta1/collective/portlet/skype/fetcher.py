# Copyright 2007, Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 
#
__author__ = """Jens Klein <jens@bluedynamics.com>"""

from zope.interface import implements
from interfaces import ISkypeNameFetcher
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IUserFactoryPlugin
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin

class SkypeNamesFromUserPropertiesFetcher(object):
    """fetches skype names from user property 'skype'."""
    
    implements(ISkypeNameFetcher)
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self):
        res = []
        pas = getToolByName(self.context, 'acl_users')        
        for user in pas.getUsers():
            if not hasattr(user, 'listPropertysheets'):
                continue
            propsheets = user.listPropertysheets()
            skype = None
            for propsheetid in propsheets:
                propsheet = user.getPropertysheet(propsheetid)
                skype = propsheet.getProperty('skype') or \
                        propsheet.getProperty('skypeid') or \
                        propsheet.getProperty('skype_id') 
                if skype is not None:
                    break
            if skype is None:
                continue
            fullname = None
            for propsheetid in propsheets:
                propsheet = user.getPropertysheet(propsheetid)
                fullname = propsheet.getProperty('fullname') or \
                           propsheet.getProperty('getFullname') # remember
                if fullname is not None:
                    break
            if fullname is None:
                fullname  = 'id'
            res.append({'name': skype, 'fullname': fullname, 'id': user.getId()})
        return  res

    