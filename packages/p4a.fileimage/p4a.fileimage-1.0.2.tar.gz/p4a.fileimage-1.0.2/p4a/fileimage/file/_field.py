from zope import schema
from zope import component

class FileField(schema.Field):

    def __init__(self, **kw):
        super(FileField, self).__init__(**kw)

    def _validate(self, value):
        super(FileField, self)._validate(value)
