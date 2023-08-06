from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
#from Products.Archetypes.mimetype_utils import getAllowableContentTypes
#from Products.Archetypes.mimetype_utils import getAllowedContentTypes
from Products.CMFCore.utils import getToolByName
from plone.app.vocabularies.types import BAD_TYPES

class CategorizingTypesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        ttool = getToolByName(context, 'portal_types', None)
        bad_types = list(BAD_TYPES)
        bad_types.extend(['CategoryContainer', 'Category'])
        if ttool is None:
            return None
        items = [SimpleTerm(t, t, ttool[t].Title())
                  for t in ttool.listContentTypes()
                  if t not in bad_types]
        return SimpleVocabulary(items)

CategorizingTypesVocabularyFactory = CategorizingTypesVocabulary()
