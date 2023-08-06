from zope.component import adapts
from zope.interface import implements
from Acquisition import aq_base, aq_inner, aq_chain, aq_parent
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from collective.categorizing.interfaces import (
    ICategoryHolder,
    ICategoryContainer,
    ICategory,
    ICategoryQuery,
    ICategoryChildren,
    ICategoryHierarchy,
    INavChildren,
    IAllowedTypes,
    IStartupDir,
    ICategoryContainerObj,
)
from collective.categorizing.exceptions import SameObjectInHierarchyError

class CategoryQuery(object):
    implements(ICategoryQuery)
    adapts(ICategory)

    def __init__(self, context):
        self.context = context

    def content_query(self):
        context = aq_inner(self.context)
        chain = aq_chain(context)
        obj_index = [chain.index(obj) for obj in chain if hasattr(obj, 'Type') and obj.Type() == u'CategoryContainer']
        index = obj_index[0] + 1
        path = '/'.join(chain[index].getPhysicalPath())
        return {'path':path}

    def subcategory_query(self):
        context = aq_inner(self.context)
        chain = aq_chain(context)
        obj_index = [chain.index(obj) for obj in chain if hasattr(obj, 'Type') and obj.Type() == u'CategoryContainer']
        index = obj_index[0]
        path = '/'.join(chain[index].getPhysicalPath())
        return {'path':path}

class NavChildren(object):
    implements(INavChildren)
    adapts(ICategoryContainer)
    def __init__(self, context):
        self.context = context
    def __call__(self, level=0):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        physical_path = context.getPhysicalPath()
        path_length= len(physical_path)
        path = '/'.join(physical_path)
        brains = catalog(
            path=path,
            object_provides=ICategory.__identifier__,
        )
        reference_catalog = getToolByName(context, 'reference_catalog')
        results = []
        for brain in brains:
            if reference_catalog.getBackReferences(brain.getObject()) != []:
                for i in reference_catalog.getBackReferences(brain.getObject()):
                    results.append(
                        dict(
                            item=brain,
                            path=brain.getPath(),
                            parent_path=catalog(UID=i.sourceUID)[0].getPath(),
                            depth=len(aq_inner(brain.getObject()).getPhysicalPath())+1-path_length,
                            children=[],
                        )
                    )
        results.extend(
            [
                dict(
                    item=brain,
                    path=brain.getPath(),
                    parent_path='/'.join(aq_parent(aq_inner(brain.getObject())).getPhysicalPath()),
                    depth=len(aq_inner(brain.getObject().getPhysicalPath()))-path_length,
                    children=[],
                ) for brain in brains
            ]
        )
        depths = []
        for r in results:
            if r['depth'] not in depths:
                depths.append(r['depth'])
        depths.sort()
        if level != 0:
            depths = [l+1 for l in range(level)]
        depths.reverse()
        for d in depths:
            for r in results:
                if r['depth'] == d:
                    path = r['parent_path']
                    item = r['item']
                    c_children = r['children']
                    for r in results:
                        if r['path'] == path:
                            children = r['children']
                            children.append({item:c_children})
                            r.update({'children':children})
        items = [{r['item']:r['children']} for r in results if r['depth'] == 1]
        return items

class CategoryChildren(object):
    implements(ICategoryChildren)
    adapts(ICategory)
    def __init__(self, context):
        self.context = context
    def __call__ (self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        def f(obj):
            inner_obj = aq_inner(obj)
            path = '/'.join(inner_obj.getPhysicalPath())
            brains = [
                brain for brain in catalog(
                    path=path,
                    object_provides=ICategory.__identifier__,
                )
            ]
            objects = [brain.getObject() for brain in brains]
            refs = []
            for brain in brains:
                subcategory = [category for category in brain.getObject().subcategory if category != '']
                if subcategory is not None and len(subcategory) != 0:
                    refs.extend(subcategory)
                    objects.extend(subcategory)
                    for ref in refs:
                        f(ref)
            return objects
        return f(context)

class CategoryHierarchy(object):
    implements(ICategoryHierarchy)
    adapts(ICategoryHolder)
    def __init__(self, context):
        self.context = context
    def __call__(self):
        context = aq_inner(self.context)
        if len(self.direct_children(context)) == 0:
            return None
        return self.hierarchy_list(context)

    def direct_children(self, obj):
        context = aq_inner(obj)
        catalog = getToolByName(context, 'portal_catalog')
        path = '/'.join(context.getPhysicalPath())
        results = [
            brain.getObject() for brain in catalog(
                path=dict(
                    query=path,
                    depth=1,
                ),
                object_provides=ICategory.__identifier__,
            )
        ]
        if hasattr(context, 'subcategory'):
            results.extend(context.subcategory)
        return results

    def list_hierarchy_object(self, obj):
        direct_children = self.direct_children(obj)
        results = []
        if direct_children:
            results.extend([[obj, child] for child in direct_children])
        else:
            results.append(obj)
        return results

    def hierarchy_list(self, obj, results=[]):
        for category in self.direct_children(obj):
            hierarchy_objects = self.list_hierarchy_object(category)
            for ho in hierarchy_objects:
                results.append(ho)
            self.hierarchy_list(category, results)
        val = []
        for res in results:
            if res not in val:
                val.append(res)
        results = val
        ones = [res for res in results if len(res) == 1]
        others = [res for res in results if len(res) != 1]
        if len(ones) != 0 and len(others) != 0:
            for one in ones:
                for other in others:
                    if one == other[-1]:
                        try:
                            results.remove(one)
                        except ValueError:
                            pass
        ones = [res for res in results if len(res) == 1]
        others = [res for res in results if len(res) != 1]
        top = self.find_top(others)
        if top is None:
            return ones
        return ones + self.connect_list(others, top)

    def find_top(self, L):
        """
        >>> L = [['a', 'i'], ['a', 'b'], ['j', 'k'], ['j', 'l'], ['b', 'd'], ['b', 'e'], ['e', 'g'], ['g', 'h']]
        >>> find_top(L)
        ['a', 'j']
        """
        try:
            zero = [l[0] for l in L]
            one = [l[1] for l in L]
            results = []
            for z in zero:
                if z not in one and z not in results:
                    results.append(z)
            return results
        except AttributeError:
            return None

    def connect_list(self, L, top):
        """"
        >>> L = [['a', 'i'], ['a', 'b'], ['j', 'k'], ['j', 'l'], ['b', 'd'], ['b', 'e'], ['e', 'g'], ['g', 'h']]
        >>> connect_list(L, ['a', 'j'])
        [['a', 'i'], ['a', 'b', 'd'], ['a', 'b', 'e', 'g', 'h'], ['j', 'k'], ['j', 'l']]
        """
        results = L[:]
        for lis in L:
            S = L[:]
            S.remove(lis)
            for s in S:
                if lis[-1] == s[0]:
                    liss = lis+s[1:]
                    for li in liss:
                        LISS = liss[:]
                        LISS.remove(li)
                        for ss in LISS:
                            if li == ss:
                                raise SameObjectInHierarchyError
                    if liss not in L:
                        L.append(liss)
                elif lis not in L:
                        L.append(lis)
        if results == L:
            ends = []
            for lis in L:
                lis_zero = lis[0]
                if lis_zero not in top:
                    results.remove(lis)
                    ends.append(lis_zero)
            resul = [res for res in results if res[-1] not in ends]
            return resul
        return self.connect_list(L, top)

class AllowedTypes(object):
    implements(IAllowedTypes)
    adapts(ICategory)
    def __init__(self, context):
        self.context = context
    def __call__(self):
        base = aq_base(self.context)
        catalog = getToolByName(getSite(), 'portal_catalog')
        category = catalog(UID=base.UID())[0].getObject()
        chain = aq_chain(aq_inner(category))
        container = [obj for obj in chain if hasattr(obj, 'Type') and obj.Type() == u'CategoryContainer'][0]
        return container.type_categorized

class StartupDir(object):
    implements(IStartupDir)
    adapts(ICategory)
    def __init__(self, context):
        self.context = context

    def chain(self):
        base = aq_base(self.context)
        catalog = getToolByName(getSite(), 'portal_catalog')
        category = catalog(UID=base.UID())[0].getObject()
        chain = aq_chain(aq_inner(category))
        return chain

    def content_categorized(self):
        chain = self.chain()
        obj_index = [chain.index(obj) for obj in chain if hasattr(obj, 'Type') and obj.Type() == u'CategoryContainer']
        index = obj_index[0] + 1
        path = '/'.join(chain[index].getPhysicalPath())
        return path

    def subcategory(self):
        chain = self.chain()
        container = [obj for obj in chain if hasattr(obj, 'Type') and obj.Type() == u'CategoryContainer'][0]
        path = '/'.join(container.getPhysicalPath())
        return path

class CategoryContainerObj(object):
    implements(ICategoryContainerObj)
    def __init__(self, context):
        self.context = context
    def __call__(self):
        context = aq_inner(self.context)
        if hasattr(context, 'Type') and context.Type() == u'CategoryContainer':
            return context
        chain = [obj for obj in aq_chain(context) if hasattr(obj, 'Type')]
        if len(chain) > 1:
            chain = chain[1:]
        for obj in chain:
            container = self.find_container(obj)
            if container:
                return container

    def find_container(self, obj):
        path = '/'.join(obj.getPhysicalPath())
        catalog = getToolByName(obj, 'portal_catalog')
        container = catalog(
            path=dict(
                query=path,
                depth=1,
            ),
            object_provides=ICategoryContainer.__identifier__,
        )
        if len(container) == 1:
            return container[0].getObject()
