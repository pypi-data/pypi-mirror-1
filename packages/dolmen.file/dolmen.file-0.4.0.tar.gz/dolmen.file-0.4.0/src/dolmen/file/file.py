# -*- coding: utf-8 -*-

import zope.app.file
from zope.schema import TextLine
from zope.interface import implements
from zope.contenttype import guess_content_type
from zope.schema.fieldproperty import FieldProperty

from dolmen.file import clean_filename


class INamedFile(zope.app.file.interfaces.IFile):
    """Defines a file that is aware of its filename.
    """
    filename = TextLine(
        title = u"Name of file",
        required = True,
        default = u''
        )


class NamedFile(zope.app.file.file.File):
    """A simple INamedFile implementation that can guess the content type
    from the value and the filename.
    """
    implements(INamedFile)
    filename = FieldProperty(INamedFile['filename'])
    
    def __init__(self, data='', contentType='', filename=None):
        self.data = data
        if filename is not None:
            self.filename = clean_filename(filename)
        if not contentType and filename:
            # If we handle large files, we don't want them read just
            # to guess the content type. We provide only the filename.
            self.contentType, enc = guess_content_type(name=filename)
        else:
            self.contentType = contentType
