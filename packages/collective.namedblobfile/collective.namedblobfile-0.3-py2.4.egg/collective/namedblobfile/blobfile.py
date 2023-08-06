from z3c.blobfile.file import File
from interfaces import INamedBlobFile
from zope.interface import implements

class NamedBlobFile(File):
    implements(INamedBlobFile)

    def __init__(self, data='', contentType='', filename=None):
        File.__init__(self, data, contentType)
        self.filename=filename