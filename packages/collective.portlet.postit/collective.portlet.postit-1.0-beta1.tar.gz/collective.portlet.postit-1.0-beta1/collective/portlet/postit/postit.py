# Copyright 2007, Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 
#
__author__ = """Jens Klein <jens@bluedynamics.com>"""

from AccessControl import ClassSecurityInfo
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import BaseSchema
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import BaseContent
from Products.Archetypes.atapi import registerType
from zope.interface import implements
from zope.component.factory import Factory
from zope.i18nmessageid import MessageFactory
import interfaces

_ = MessageFactory('collective.portlet.postit')

copied_fields = {}
copied_fields['title'] = BaseSchema['title'].copy()
copied_fields['title'].required = 0
copied_fields['title'].mode = "r"
schema = Schema((

    TextField(
        name='postit',
        widget=TextAreaWidget(
            maxlength=150,
            label='Text on Post-It',
            label_msgid='PostIt_label_text',
            i18n_domain='collective.portlet.postit',
        ),
    ),
    copied_fields['title'],

),
)

PostIt_schema = BaseSchema.copy() + \
    schema.copy()
    
class PostIt(BaseContent, BrowserDefaultMixin):
    """Simple type with a text field for usage as a post-it.
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPostIt)

    meta_type = 'PostIt'
    _at_rename_after_creation = True

    schema = PostIt_schema
    
    excludeFromNav = True

    security.declarePublic('Title')
    def Title(self):
        """take the first 10 chars as title - needed for DCMD."""
        return (self.getPostit() or 'empty')[:10]

addPostIt = Factory(PostIt, title=_(u"Add Post-It"))    

registerType(PostIt, 'collective.portlet.postit')


