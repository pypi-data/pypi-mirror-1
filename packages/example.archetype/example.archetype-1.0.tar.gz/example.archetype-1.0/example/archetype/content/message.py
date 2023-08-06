# Zope3 imports
from zope.interface import implements

# CMF imports
from Products.CMFCore import permissions

# Archetypes & ATCT imports
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# Product imports
from example.archetype import config
from example.archetype.interfaces import IInstantMessage
from example.archetype import exampleMessageFactory as _

# Schema definition
schema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

  atapi.StringField('priority',
              vocabulary = config.MESSAGE_PRIORITIES,
              default = 'normal',
              widget = atapi.SelectionWidget(label = _(u'Priority')),
             ),

  atapi.TextField('body',
            searchable = 1,
            required = 1,
            allowable_content_types = ('text/plain',
                                       'text/structured',
                                       'text/html',),
            default_output_type = 'text/x-html-safe',
            widget = atapi.RichWidget(label = _(u'Message Body')),
           ),

))


class InstantMessage(base.ATCTContent):
    """An Archetype for an InstantMessage application"""

    implements(IInstantMessage)

    schema = schema
    
# Content type registration for the Archetypes machinery
atapi.registerType(InstantMessage, config.PROJECTNAME)
