from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Acquisition import aq_chain, aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from collective.categorizing.interfaces import ICategoryContainer, ICategory, INavChildren

class CategoryView(BrowserView):
    """Default view of a Category.
    """
    __call__ = ViewPageTemplateFile('category.pt')

    @memoize
    def contents(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = []
        uid = context.getRawContent_categorized()
        for r in catalog(
            UID=uid,
        ):
            results.append(
                dict(
                    title=r.Title,
                    description=r.Description,
                    url=r.getPath(),
                )
            )
        return results

    @memoize
    def categories(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        path = '/'.join(context.getPhysicalPath())
        results = []
        for r in catalog(
            path=dict(query=path, depth=1),
            object_provides=ICategory.__identifier__,
        ):
            results.append(
                dict(
                    title=r.Title,
                    description=r.Description,
                    url=r.getPath(),
                )
            )

        uid = context.getRawSubcategory()
        for r in catalog(
            UID=uid,
        ):
            results.append(
                dict(
                    title=r.Title,
                    description=r.Description,
                    url=r.getPath(),
                )
            )
        return results

class CategoryNavViewlet(BrowserView):
    implements(IViewlet)
    render = ViewPageTemplateFile("category-nav.pt")

    def __init__(self, context, request, view, manager):
        super(CategoryNavViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.manager = manager

    def update(self):
        pass

    @memoize
    def categories(self):
        context = aq_inner(self.context)
        level = 0
        items = INavChildren(context)(level)
        return '<ul>' + ''.join(self.f(items, [])) + '</ul>'

    def f(self, X, results):
        for x in X:
            for k in x.keys():
                tag = '<li><a href="%s" title="%s">%s</a></li>' %(k.getURL(), k.Description, k.Title)
                if len(x[k]) == 0:
                    results.append(tag)
                else:
                    results.append(tag)
                    results.append('<li><ul>')
                    self.f(x[k], results)
                    results.append('</ul></li>')
        return results

class CategoryNavSelectionViewlet(CategoryNavViewlet):
    implements(IViewlet)
    render = ViewPageTemplateFile("category-nav-selection.pt")

    def __init__(self, context, request, view, manager):
        super(CategoryNavViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.manager = manager

    def update(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        form = self.request.form
        update_button = form.get('form.button.Update', None)
        if update_button:
            categories = form.get('category')
            if categories is not None and categories != []:
                for uid in categories:
                    category = catalog(UID=uid)
                    obj = category[0].getObject()
                    content = obj.content_categorized
                    if context not in content:
                        content.append(context)
                        obj.setContent_categorized(content)
        return self.render()

    @memoize
    def categories(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        chain = [obj for obj in aq_chain(context) if hasattr(obj, 'Type')]
        for obj in chain:
            path = '/'.join(obj.getPhysicalPath())
            brains = catalog(
                path=dict(
                    query=path,
                    depth=1,
                ),
                object_provides=ICategoryContainer.__identifier__,
            )
            if len(brains) ==1:
                container = brains[0].getObject()
                break
        level = 0
        items = INavChildren(aq_inner(container))(level)
        return '<ul>' + ''.join(self.f(items, [])) + '</ul>'

    def f(self, X, results):
        context = aq_inner(self.context)
        for x in X:
            for k in x.keys():
                if context in k.getObject().content_categorized:
                    tag = '<li><input id="category_%s" type="checkbox" name="category:list" value="%s" checked /><a href="%s" title="%s">%s</a></li>' %(k.UID, k.UID, k.getURL(), k.Description, k.Title)
                else:
                    tag = '<li><input id="category_%s" type="checkbox" name="category:list" value="%s" /><a href="%s" title="%s">%s</a></li>' %(k.UID, k.UID, k.getURL(), k.Description, k.Title)
                if len(x[k]) == 0:
                    results.append(tag)
                else:
                    results.append(tag)
                    results.append('<ul>')
                    self.f(x[k], results)
                    results.append('</ul>')
        return results

class ActionCondition(BrowserView):
    """Default view of a Category.
    """

    def action_condition(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        context_type = context.portal_type
        chain = aq_chain(context)
        chain = [obj for obj in chain if hasattr(obj, 'Type')]
        parent = chain[1:]
        results = []
        for obj in parent:
            path = '/'.join(obj.getPhysicalPath())
            results.extend(
                catalog(
                    path=dict(query=path, depth=1),
                    object_provides=ICategoryContainer.__identifier__,
                )
            )
        try:
            if context_type in results[0].type_categorized:
                return True
        except IndexError:
            return False
