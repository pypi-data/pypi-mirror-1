from zope.interface import implements
from zope.component import adapts
from Acquisition import aq_inner, aq_chain
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IObjectPostValidation
from collective.categorizing import CollectiveCategorizingMessageFactory as _
from collective.categorizing.interfaces import ICategory, ICategoryChildren, INavChildren

class ValidateTitleUniqueness(object):
    """Validate uniqueness of title under same CategoryContainer"""
    implements(IObjectPostValidation)
    adapts(ICategory)
    field_name = 'title'

    def __init__(self, context):
        self.context = context

    def __call__(self, request):
        context = aq_inner(self.context)
        value = request.form.get(self.field_name, request.get(self.field_name, None))
        if value is not None:
            if value == context.Title:
                return None
            catalog = getToolByName(context, 'portal_catalog')
            chain = aq_chain(context)
            container = [obj for obj in chain if hasattr(obj, 'Type') and obj.Type() == u'CategoryContainer']
            path = '/'.join(container[0].getPhysicalPath())
            results = catalog(
                path=path,
                object_provides=ICategory.__identifier__,
                Title=value,
            )
            if len(results) == 0:
                return None
            elif len(results) == 1 and results[0].UID == context.UID():
                return None
            else:
                return {self.field_name: _(u'The Title is already in use under the CategoryContainer.')}
        return None

class ValidateSubcategory(object):
    """Validate subcategory not to categorize its parent hierarchy."""
    implements(IObjectPostValidation)
    adapts(ICategory)
    field_name = 'subcategory'

    def __init__(self, context):
        self.context = context

    def __call__(self, request):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        value = request.form.get(self.field_name, request.get(self.field_name, None))
        if value is not None and value != ['']:
            if '' in value:
                value.remove('')
            value_brains = catalog(UID=value)
            container = [obj for obj in aq_chain(context) if hasattr(obj, 'Type') and obj.Type() == u'CategoryContainer'][0]
            container_path = '/'.join(container.getPhysicalPath())
            for val in value:
                uids = [
                    brain.UID for brain in catalog(
                        path=container_path,
                        object_provides=ICategory.__identifier__,
                    )
                ]
                if val not in uids:
                    return {self.field_name: _(u'subcategory-from-different-hierarchy-validation', u'You cannot use ${category} as subcategory here since it is located in a different hierarchy.', mapping={'category':catalog(UID=val)[0].Title})}
            titles = []
            path = u'/'.join(context.getPhysicalPath())
            subfolders = [
                brain.getObject() for brain in catalog(
                    path=dict(
                        query=path,
                        depth=1,
                    ),
                    object_provides=ICategory.__identifier__,
                )
            ]
            chain = [obj for obj in aq_chain(context) if hasattr(obj, 'Type') and obj.Type() == u'Category']
            values = [aq_inner(brain.getObject()) for brain in value_brains]
            for v_obj in values:
                ## Check if subcategory is one of subfolders.
                if v_obj in subfolders:
                    titles.append(v_obj.Title())
                items = ICategoryChildren(v_obj)()
                for obj in chain:
                    if obj in items:
                        titles.append(v_obj.Title())
            ts = []
            for title in titles:
                if title not in ts:
                    ts.append(title)
            titles = ts
            if len(titles) > 1:
                categories = u', '.join(titles)
                return {self.field_name: _(u'subcategories-validation', u'You cannot use ${categories} as subcategories since they are located on top of this category or they are already the direct subcategory of this category.', mapping={'categories':categories})}
            elif len(titles) == 1:
                return {self.field_name: _(u'subcategory-validation', u'You cannot use ${category} as subcategory since it is located on top of this category or they are already the direct subcategory of this category.', mapping={'category':titles[0]})}
        return None

    def f(self, X, results):
        context = aq_inner(self.context)
        for x in X:
            for k in x.keys():
                if len(x[k]) == 0:
                    results.append(k)
                else:
                    results.append(k)
                    self.f(x[k], results)
        return results
