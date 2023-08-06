from OFS import Image as ofsimage
_marker = object()

class FileProperty(object):
    """Stores the given file data in a zodb safe way.
    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        value = inst.__dict__.get(self.__name, _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)

        return value

    def __set__(self, inst, value):
        field = self.__field.bind(inst)
        if field.readonly and inst.__dict__.has_key(self.__name):
            raise ValueError(self.__name, 'field is readonly')

        if inst.__dict__.get(self.__name, None) is None:
            inst.__dict__[self.__name] = ofsimage.File(self.__name, 
                                                       self.__name, '')
        
        obj = inst.__dict__[self.__name]
        obj.manage_upload(file=value)
        inst._p_changed = True

    def __getattr__(self, name):
        return getattr(self.__field, name)


