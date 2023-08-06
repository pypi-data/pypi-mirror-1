from Products.MimetypesRegistry.interfaces import IClassifier
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
from Products.MimetypesRegistry.common import MimeTypeException

from types import InstanceType

class application_docbook(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "DocBook"
    mimetypes  = ('application/docbook+xml',)
    extensions = ('dbk',)
    binary     = 0