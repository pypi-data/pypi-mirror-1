from Acquisition import aq_chain, aq_inner, aq_parent
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.app.container.interfaces import IObjectAddedEvent, IObjectMovedEvent, IObjectRemovedEvent
from Products.Archetypes.interfaces import IObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from collective.categorizing import CollectiveCategorizingMessageFactory as _
from collective.categorizing.interfaces import (
    ICategoryContainer,
    ICategory,
    ICategoryHierarchy,
)
from plone.app.vocabularies.types import BAD_TYPES
from collective.categorizing.exceptions import SameObjectInHierarchyError

@adapter(ICategoryContainer, IObjectInitializedEvent)
def category_container_initialized(container, event):
    assert container == event.object
    parent = aq_parent(container)
    path = '/'.join(parent.getPhysicalPath())
    catalog = getToolByName(container, 'portal_catalog')
    results = []
    for r in catalog(
        path=dict(query=path, depth=1),
        object_provides=ICategoryContainer.__identifier__,
    ):
        if r.UID != container.UID():
            results.append(r)
    if len(results) == 1:
        putils = getToolByName(container, 'plone_utils')
        urltool = getToolByName(container, 'portal_url')
        portal = urltool.getPortalObject()
        putils.addPortalMessage(_(u'You cannot add more than one CategoryContainer in the same hierarchy.'), type='warning')
        paths = ['/'.join(container.getPhysicalPath())]
        putils.deleteObjectsByPaths(paths=paths)
        ## Need to fix page rendering after contet deletion.

@adapter(ICategoryContainer, IObjectModifiedEvent)
def category_container_modified(container, event):
    assert container == event.object
    typetool = getToolByName(container, 'portal_types')
    id = container.UID()
    portal_types = [t for t in typetool.portal_types.listContentTypes() if t not in BAD_TYPES]
    for content in portal_types:
        type_info = typetool.getTypeInfo(content)
        ids = [action.id for action in type_info.listActions()]
        if id in ids:
            selection=[ids.index(a) for a in ids if a == id]
            type_info.deleteActions(selection)
    try:
        for content in container.type_categorized:
            type_info = typetool.getTypeInfo(content)
            type_info.addAction(id, container.Title(), 'string:${object_url}/@@categories-view', 'object/@@category-action-condition', 'Modify portal content', 'object')
    except AttributeError:
        pass

@adapter(ICategoryContainer, IObjectRemovedEvent)
def category_container_removed(container, event):
    typetool = getToolByName(container, 'portal_types')
    id = container.UID()
    portal_types = [t for t in typetool.portal_types.listContentTypes() if t not in BAD_TYPES]
    for content in portal_types:
        type_info = typetool.getTypeInfo(content)
        ids = [action.id for action in type_info.listActions()]
        selection=[ids.index(a) for a in ids if a == id]
        type_info.deleteActions(selection)

@adapter(ICategory, IObjectMovedEvent)
def category_chain_loop(content, event):
    if event.newName is None and event.newParent is None:
        return None
    content = aq_inner(content)
    catalog = getToolByName(content, 'portal_catalog')
    parent_obj = aq_parent(content)
    path = u'/'.join(parent_obj.getPhysicalPath())
    brains = [
        brain for brain in catalog(
            path=dict(
                query=path,
                depth=1,
            ),
            object_provides=ICategory.__identifier__,
        ) if brain.Title == content.Title()
    ]
    bs = [brain for brain in brains if brain.Title != '']
    if event.oldName is None and event.oldParent is None:
        if len(bs) == 0:
            return None
        if len(bs) == 1 and brains[0].Title == content.Title():
            container = [obj for obj in aq_chain(aq_inner(content)) if hasattr(obj, 'Type') and obj.Type() == u'CategoryContainer'][0]
            for brain in catalog(
                path='/'.join(aq_inner(container).getPhysicalPath()),
                object_provides=ICategory.__identifier__,
            ):
                if brains[0].Title == brain.Title and brains[0].UID != brain.UID:
                    parent_obj.manage_delObjects([content.getId()])
                    message = _(u"You cannot add ${category} here because category of the same title already exists.", mapping={'category': content.Title()})
                    IStatusMessage(content.REQUEST).addStatusMessage(message, type='warning')
            return None
    else:
        try:
            ICategoryHierarchy(parent_obj)()
            return None
        except SameObjectInHierarchyError:
            parent_obj.manage_delObjects([content.getId()])
#            object_cut = parent_obj.manage_cutObjects([content.getId()])
#            old_parent = event.oldParent
#            old_parent.manage_pasteObjects(object_cut)
            message = _(u"You cannot add ${category} here.", mapping={'category': content.Title()})
            IStatusMessage(content.REQUEST).addStatusMessage(message, type='warning')
            return None
