from zope.interface import implements
from zope.component import adapts

from plone.namedfile.interfaces import INamedImage

from Products.CMFCore.FSImage import FSImage
from OFS.Image import Image

class NamedFSImage(object):
    """Adapt a filesystem image to a named image.
    """
    implements(INamedImage)
    adapts(FSImage)
    
    def __init__(self, context):
        self.context = context
        self.filename = context.__name__
        self.data = context._data
        self._height = context.height
        self._width = context.width

    def getSize(self):
        return self.context.get_size()

class NamedOFSImage(object):
    """Adapt an OFS image object to a named image.
    """
    implements(INamedImage)
    adapts(Image)

    def __init__(self, context):
        self.context = context
        self.filename = context.__name__
        self.data = context.data
        self._height = context.height
        self._width = context.width

    def getSize(self):
        return self.context.get_size()