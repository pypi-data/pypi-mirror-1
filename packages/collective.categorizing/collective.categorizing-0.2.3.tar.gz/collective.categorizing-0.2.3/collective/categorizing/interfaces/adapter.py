from zope.interface import Interface

class ICategoryQuery(Interface):
    def content_query():
        """Returns query for content type search of category."""

    def subcategory_query():
        """Returns query for subcategory search."""

class ICategoryChildren(Interface):
    def __call__():
        """Returns list of all the children of category."""

class ICategoryHierarchy(Interface):
    def __call__():
        """Returns list of hierarchy list excluding the top."""

    def direct_children(obj):
        """Returns direct subcategory objects of obj."""

    def list_hierarchy_object(obj):
        """Returns objet list of hierarchy."""

    def hierarchy_list(obj):
        """Returns list of hierarchies."""

class INavChildren(Interface):
    def __call__(level):
        """Returns children categories of CategoryContainer like:
        
        [
            {
                'item':<Products.ZCatalog.Catalog.mybrains object at ...>,
                'depth':1,
                'children':[
                    {
                        'item':<Products.ZCatalog.Catalog.mybrains object at ...>,
                        'depth':2,
                        'children':[
                            ...
                        ]
                    },
                    ...,
                ]
            },
            ...,
        ]
        """

class IAllowedTypes(Interface):
    def __call__():
        """Returns allowed types for categorizing."""

class IStartupDir(Interface):
    def chain():
        """Returns object chain."""
    def content_categorized():
        """Returns start up directory path of content_categorized."""
    def subcategory():
        """Returns start up directory path of subcategory."""

class ICategoryContainerObj(Interface):
    def __call__():
        """Returns CategoryContainer which belongs to the context hierarchy."""
