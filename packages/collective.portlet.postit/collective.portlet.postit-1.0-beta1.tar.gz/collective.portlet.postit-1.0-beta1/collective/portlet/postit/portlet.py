# Copyright 2007, Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 
#
__author__ = """Jens Klein <jens@bluedynamics.com>"""

from zope.interface import implements
from plone.app.portlets.portlets import base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from interfaces import IPostitPortlet
from interfaces import IPostitFetcher

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('collective.portlet.postit')

class Assignment(base.Assignment):
    implements(IPostitPortlet)

    title = _(u'postit', default=u'Post-It')
    
class Renderer(base.Renderer):
    
    render = ViewPageTemplateFile('portlet.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self._available = True

    @property
    def available(self):
        return self._available
    
    def initialize(self):
        fetcher = IPostitFetcher(self.context)
        self.postits = fetcher()
        self._available = bool(self.postits)
    
class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
