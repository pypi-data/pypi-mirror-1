from zope.interface import implements
from blobfile import NamedBlobFile
from interfaces import INamedBlobImage

class NamedBlobImage(NamedBlobFile):
    implements(INamedBlobImage)