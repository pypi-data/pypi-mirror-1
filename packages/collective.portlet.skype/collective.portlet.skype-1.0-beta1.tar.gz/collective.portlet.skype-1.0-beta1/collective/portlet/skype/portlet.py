# Copyright 2007, Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 
#
__author__ = """Jens Klein <jens@bluedynamics.com>"""

from zope.interface import implements
from plone.app.portlets.portlets import base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from interfaces import ISkypePortlet
from interfaces import ISkypeNameFetcher

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('collective.portlet.skype')

class Assignment(base.Assignment):
    implements(ISkypePortlet)

    title = _(u'sykpe', default=u'Skype')
    
class Renderer(base.Renderer):
    
    render = ViewPageTemplateFile('skype.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
    
    def initialize(self):
        fetcher = ISkypeNameFetcher(self.context)
        self.skypenames = fetcher()
        self.icontype = 'smallicon' # we might want this configureable in future
        self.actiontype = 'chat' # we might want this configureable in future too
    
class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
