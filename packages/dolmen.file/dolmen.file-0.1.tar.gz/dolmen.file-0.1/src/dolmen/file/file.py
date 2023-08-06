# -*- coding: utf-8 -*-

from zope.schema import TextLine
from zope.schema.fieldproperty import FieldProperty
from zope.interface import implements
from zope.contenttype import guess_content_type
from zope.app.file import File
from zope.app.file.interfaces import IFile


def cleanupFileName(filename):
    return unicode(filename.split('\\')[-1].split('/')[-1])


class INamedFile(IFile):
    """Defines a file that is aware of its filename.
    """
    filename = TextLine(
        title = u"Name of file",
        required = True,
        default = u''
        )


class NamedFile(File):
    """A simple INamedFile implementation that can guess the content type
    from the value and the filename.
    """
    implements(INamedFile)
    filename = FieldProperty(INamedFile['filename'])
    
    def __init__(self, data='', contentType='', filename=None):
        self.data = data
        if filename is not None:
            self.filename = cleanupFileName(filename)
        if not contentType and filename:
            # If we handle large files, we don't want them read just
            # to guess the content type. We provide only the filename.
            self.contentType, enc = guess_content_type(name=filename)
        else:
            self.contentType = contentType
