from collective.namedfile.widget import NamedFileWidget, NamedImageWidget, NamedFileDisplayWidget, NamedImageDisplayWidget
from blobfile import NamedBlobFile

class NamedBlobFileWidget(NamedFileWidget):
    def _toFieldValue(self, input):
        value=super(NamedFileWidget, self)._toFieldValue(input)
        if value is not self.context.missing_value:
            filename=getattr(input, "filename", None)
            contenttype=input.headers.get("content-type",
                                          "application/octet-stream")
            value=NamedBlobFile(value, contenttype, filename)

        return value


class NamedBlobImageWidget(NamedImageWidget):
    pass


class NamedBlobFileDisplayWidget(NamedFileDisplayWidget):
    pass
    

class NamedBlobImageDisplayWidget(NamedImageDisplayWidget):
    pass
