"""Main product initializer
"""
from zope.i18nmessageid import MessageFactory
CollectiveCategorizingMessageFactory = MessageFactory('collective.categorizing')

PROJECTNAME = "collective.categorizing"
ADD_PERMISSIONS = {
    "CategoryContainer" : "Categorizing: Add CategoryContainer",
    "Category" : "Categorizing: Add Category",
    }

from Products.Archetypes import atapi
from Products.CMFCore import utils

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

#    from collective.categorizing.content import categorycontainer, category

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(PROJECTNAME),
        PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit("%s: %s" % (PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = ADD_PERMISSIONS[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)
