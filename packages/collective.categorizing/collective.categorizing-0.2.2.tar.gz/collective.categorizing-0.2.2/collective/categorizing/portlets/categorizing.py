from Acquisition import aq_inner
from zope import schema
from zope.formlib import form
from zope.interface import implements
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from collective.categorizing import CollectiveCategorizingMessageFactory as _
from collective.categorizing.interfaces import ICategoryContainerObj, INavChildren,ICategoryHierarchy
from collective.categorizing.browser.category import CategoryNavViewlet

class ICategorizingPortlet(IPortletDataProvider):
    '''A portlet which can render categories.
    '''

#    level = schema.Int(
#            title=_(u"label_category_depth",
#                    default=u"Category Depth"),
#            description=_(u"help_category_depth",
#                          default=u"How many folders should be included "
#                                   "before the category tree stops. 0 "
#                                   "means no limit."
#                                   ),
#            default=2,
#            required=False)


class Assignment(base.Assignment):
    implements(ICategorizingPortlet)

    @property
    def title(self):
        return _(u"Categories")

#    level = 2

#    def __init__(self, level=2):
#        self.level = level

class Renderer(base.Renderer, CategoryNavViewlet):

    render = ViewPageTemplateFile('categorizing.pt')

    def update( self ):
        pass

    @property
    def link_to_category_container(self):
        context = aq_inner(self.context)
        return ICategoryContainerObj(context)().absolute_url()

    @property
    def available(self):
        context = aq_inner(self.context)
        if ICategoryContainerObj(context)():
            return True
        else:
            return False

    @memoize
    def categories(self):
        context = aq_inner(self.context)
        obj = ICategoryContainerObj(context)()
        tags = [self.tag(o) for o in ICategoryHierarchy(obj).direct_children(obj)]
        html = '<ul>' + ''.join(tags) + '</ul>'
        return html

    def tag(self, obj):
        path = '/'.join(obj.getPhysicalPath())
        return '<li><a href="%s" title="%s">%s</a></li>' %(path, obj.Description(), obj.Title())

class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()


#class AddForm(base.AddForm):

#    form_fields = form.Fields(ICategorizingPortlet)
#    label = _(u"Add Categorizing Portlet")
#    description = _(u"This portlet display a category tree.")

#    def create(self, data):
#        return Assignment(level=data.get('level', 2))

#class EditForm(base.EditForm):
#    form_fields = form.Fields(ICategorizingPortlet)
#    label = _(u"Edit Categorizing Portlet")
#    description = _(u"This portlet display a category tree.")
