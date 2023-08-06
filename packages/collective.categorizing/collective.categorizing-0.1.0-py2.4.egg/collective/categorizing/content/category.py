from zope.interface import implements
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from collective.categorizing import PROJECTNAME
from collective.categorizing import CollectiveCategorizingMessageFactory as _
from collective.categorizing.interfaces import ICategory, ICategoryQuery

try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import *

CategorySchema = folder.ATFolderSchema.copy() + Schema((

    ReferenceField(
        name='content',
        required=False,
        searchable=False,
        languageIndependent=False,
        storage=AnnotationStorage(),
        relationship="isContent",
        multiValued=True,
        allowed_types_method='allowed_types',
        widget=ReferenceBrowserWidget(
            label=_(u'Content'),
            description=_(u'Select Contents which belongs to this category.'),
            restrict_browsing_to_startup_directory=True,
            base_query='dynamicQuery',
        ),
    ),

    ReferenceField(
        name='subcategory',
        required=False,
        searchable=False,
        languageIndependent=False,
        storage=AnnotationStorage(),
        relationship="isSubcategory",
        multiValued=True,
        allowed_types=('Category',),
        widget=ReferenceBrowserWidget(
            label=_(u'Subcategory'),
            description=_(u'Select Subcategory which is located not in this category. If the category is located under this category, it becomes subcategory of this category automatically.'),
            restrict_browsing_to_startup_directory=True,
            base_query='dynamicSubQuery',
        ),
    ),

),
)

CategorySchema['title'].storage = AnnotationStorage()
CategorySchema['title'].widget.label = _(u"Title")
CategorySchema['title'].widget.description = _(u"")

CategorySchema['description'].storage = AnnotationStorage()
CategorySchema['description'].widget.label = _(u"Description")
CategorySchema['description'].widget.description = _(u"")

finalizeATCTSchema(CategorySchema, folderish=True, moveDiscussion=False)

class Category(folder.ATFolder):

    implements(ICategory)
    portal_type = "Category"
    _at_rename_after_creation = True
    schema = CategorySchema

    title = ATFieldProperty('title')
    description = ATFieldProperty('description')
    content = ATReferenceFieldProperty('content')
    subcategory = ATReferenceFieldProperty('subcategory')

    def allowed_types(self):
        """Returns allowed content types form parent category container."""
        return self.type_categorized

    def dynamicQuery(self):
        return ICategoryQuery(self).content_query()

    def dynamicSubQuery(self):
        return ICategoryQuery(self).subcategory_query()

registerType(Category, PROJECTNAME)
