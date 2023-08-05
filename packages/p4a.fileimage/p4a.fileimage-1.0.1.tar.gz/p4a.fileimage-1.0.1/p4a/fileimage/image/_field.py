from zope import schema
from zope import component
from p4a.fileimage import file

class ImageField(file.FileField):
    """A field for representing an image.
    """

    def __init__(self, preferred_dimensions=None, **kw):
        super(ImageField, self).__init__(**kw)

        self.preferred_dimensions = preferred_dimensions
