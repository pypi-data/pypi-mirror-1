from zope.interface import implements
#from zope.component import adapts,getUtility
#from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from collective.categorizing import PROJECTNAME
from collective.categorizing import CollectiveCategorizingMessageFactory as _
#from Acquisition import aq_inner, aq_chain
from Products.Archetypes.public import *
#from Products.Archetypes.public import StringField, IntegerField
from collective.categorizing.interfaces import ICategoryContainer

CategoryContainerSchema = folder.ATFolderSchema.copy() + Schema((

    StringField(
        name='type_categorized',
        required=True,
        searchable=False,
        storage=AnnotationStorage(),
        widget=MultiSelectionWidget(
            label=_(u'Content Type'),
            description=_(u'Select Content Types to be categorized.'),
        ),
        vocabulary_factory="collective.categorizing.vocabulary.Types",
        enforceVocabulary=True,
    ),

    IntegerField(
        name='level',
        required=False,
        searchable=False,
        storage=AnnotationStorage(),
        default=2,
        widget=IntegerWidget(
            label=_(u'Level of Category Child'),
            description=_(u'Level of Category Child to be shown. 0 shows all children and 1 only shows the parent.'),
            size=1,
            maxlength=2,
        ),
    ),

),
)

CategoryContainerSchema['title'].storage = AnnotationStorage()
CategoryContainerSchema['title'].widget.label = _(u"Title")
CategoryContainerSchema['title'].widget.description = _(u"")

CategoryContainerSchema['description'].storage = AnnotationStorage()
CategoryContainerSchema['description'].widget.label = _(u"Description")
CategoryContainerSchema['description'].widget.description = _(u"")

finalizeATCTSchema(CategoryContainerSchema, folderish=True, moveDiscussion=False)

class CategoryContainer(folder.ATFolder):

    implements(ICategoryContainer)
    portal_type = "CategoryContainer"
    _at_rename_after_creation = True
    schema = CategoryContainerSchema

    title = ATFieldProperty('title')
    description = ATFieldProperty('description')
    type_categorized = ATFieldProperty('type_categorized')
    level = ATFieldProperty('level')

registerType(CategoryContainer, PROJECTNAME)
