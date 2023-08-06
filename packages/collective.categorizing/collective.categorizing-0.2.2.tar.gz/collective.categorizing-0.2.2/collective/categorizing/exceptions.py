from collective.categorizing import CollectiveCategorizingMessageFactory as _

class SameObjectInHierarchyError(Exception):
    def __str__(self):
        return _(u"The same object already exists on the same hierarchy.")
