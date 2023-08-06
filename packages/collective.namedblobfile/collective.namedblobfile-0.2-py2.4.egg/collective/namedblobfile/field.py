from zope.interface import implements
from collective.namedfile.field import NamedFile, NamedImage, NamedFileProxy, NamedImageProxy
from interfaces import INamedBlobFile, INamedBlobImage
from blobfile import NamedBlobFile as BlobFileValueType
from blobimage import NamedBlobImage as BlobImageValueType

class NamedBlobFile(NamedFile):
    """A NamedBlobFile field
    """
    implements(INamedBlobFile)

class NamedBlobImage(NamedImage):
    """A NamedBlobImage field
    """
    implements(INamedBlobImage)

class NamedBlobFileProxy(NamedFileProxy):
    implements(INamedBlobFile)
    _valueType = BlobFileValueType
            
class NamedBlobImageProxy(NamedImageProxy):
    implements(INamedBlobImage)
    _valueType = BlobImageValueType
