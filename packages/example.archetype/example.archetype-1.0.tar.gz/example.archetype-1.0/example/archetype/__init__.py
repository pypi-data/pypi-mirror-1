"""Main product initializer
"""


# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

from zope.i18nmessageid import MessageFactory
exampleMessageFactory = MessageFactory('example.archetype')

# Archetypes & CMF imports
from Products.Archetypes.atapi import process_types
from Products.Archetypes.atapi import listTypes
from Products.CMFCore import utils

# Product imports
import config

# Import the content types modules
from content import message



def initialize(context):
    
    content_types, constructors, ftis = process_types(
             listTypes(config.PROJECTNAME), 
             config.PROJECTNAME)

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (config.PROJECTNAME, atype.portal_type)
        utils.ContentInit(kind,            
                          content_types      = (atype,),
                          permission         = config.ADD_CONTENT_PERMISSIONS[atype.portal_type],
                          extra_constructors = (constructor,),            
                          fti                = ftis,
                          ).initialize(context)
