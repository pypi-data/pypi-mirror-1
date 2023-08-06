from zope.interface import Interface
from zope import schema
from zope.app.container.constraints import contains
from collective.categorizing import CollectiveCategorizingMessageFactory as _

class ICategoryHolder(Interface):
    """Base Interface for ICategoryContainer and ICategory for adaptors."""

#class ICategoryContainer(Interface):
class ICategoryContainer(ICategoryHolder):

    contains(
        'collective.categorizing.interfaces.ICategory',
    )

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.TextLine(
        title=_(u"Description"),
        required=False,
    )

    type_categorized = schema.Choice(
        title=_(u"Content Type"),
        required=True,
        description=_(u'Select Content Types to be categorized.'),
        vocabulary=_(u"Content Types"),
    )

    level = schema.Int(
        title=_(u"Level of Category Child"),
        description=_(u'Level of Category Child to be shown. 0 shows all children and 1 only shows the parent.'),
        required=False,
    )

#class ICategory(Interface):
class ICategory(ICategoryHolder):

    contains(
        'collective.categorizing.interfaces.ICategory',
        )

    title = schema.TextLine(
        title=_(u"Title"),
        required=True
    )

    description = schema.TextLine(
        title=_(u"Description"),
        required=False,
    )

    content_categorized = schema.Choice(
        title=_(u"Content"),
        required=False,
        description=_(u'Select Contents which belongs to this category.'),
        vocabulary=_(u"Contents"),
        )

    subcategory = schema.Choice(
        title=_(u"Subcategory"),
        description=_(u'Select Subcategory which is located not in this category. If the category is located under this category, it becomes subcategory of this category automatically.'),
        required=False,
        vocabulary=_(u"Subcategories"),
    )

