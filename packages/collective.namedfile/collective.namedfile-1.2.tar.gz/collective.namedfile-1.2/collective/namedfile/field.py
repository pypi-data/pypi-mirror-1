from interfaces import INamedFile, INamedImage
from file import NamedFile as FileValueType
from image import NamedImage as ImageValueType
from zope.schema import Field
from zope.interface import implements

class NamedFile(Field):
    """A NamedFile field
    """
    implements(INamedFile)

class NamedImage(NamedFile):
    """A NamedImage field
    """
    implements(INamedImage)

class NamedFileProxy(Field):
    """Store a NamedFile across a number of simpler attributes.
    
    Useful for non-zodb content. Example usage:
    
    class IMyFilefo(Interface):
        data = schema.Bytes()
        filename = schema.TextLine()
        file = NamedFileProxy(data=data, filename=filename)
    """
    implements(INamedFile)
    _valueType = FileValueType
    
    def __init__(self, data, contentType=None, filename=None, **kw):
        super(NamedFileProxy, self).__init__(**kw)
        self.data = data
        self.contentType = contentType
        self.filename = filename
    
    def bind(self, onbject):
        clone = super(NamedFileProxy, self).bind(object)
        clone.data = self.data.bind(object)
        if self.contentType is not None:
            clone.contentType = self.contentType.bind(object)
        if self.filename is not None:
            clone.filename = self.filename.bind(object)
        return clone
    
    def _validate(self, value):
        super(NamedFileProxy, self)._validate(value)
        self.data._validate(value.data)
        if self.contentType is not None:
            self.contentType._validate(unicode(value.contentType))
        if self.filename is not None:
            self.filename._validate(unicode(value.filename))
    
    def get(self, object):
        data = self.data.get(object)
        if data is None:
            data = ''
        if self.contentType is not None:
            contentType = self.contentType.get(object)
        else:
            contentType = ''
        if self.filename is not None:
            filename = self.filename.get(object)
        else:
            filename = None
        return self._valueType(str(data), contentType, filename)
    
    def set(self, object, value):
        if self.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.__name__,
                               object.__class__.__module__,
                               object.__class__.__name__))
        self.data.set(object, value.data)
        if self.contentType is not None:
            self.contentType.set(object, value.contentType)
        if self.filename is not None:
            self.filename.set(object, value.filename)
            
class NamedImageProxy(NamedFileProxy):
    """Store a NamedImage across a number of simpler attributes.
    
    Useful for non-zodb content. Example usage:
    
    class IMyFilefo(Interface):
        data = schema.Bytes()
        filename = schema.TextLine()
        file = NamedImageProxy(data=data, filename=filename)
    """
    implements(INamedImage)
    _valueType = ImageValueType
