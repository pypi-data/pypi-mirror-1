# -*- coding: utf-8 -*-

from zope import schema, interface


class IFileField(interface.Interface):
    """A field storing binary datas.
    """


class FileField(schema.Field):
    interface.implements(IFileField)

    def __init__(self, **kw):
        super(FileField, self).__init__(**kw)

    def _validate(self, value):
        super(FileField, self)._validate(value)
