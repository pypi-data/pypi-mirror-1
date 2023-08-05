import urlparse
from ohm.descriptors import simple_repr
from ohm import validators
from httpencode import GET, PUT, DELETE

class NoDefault(object): pass

class remote(object):

    """
    A descriptor that reads its data from a remote source.  The object
    this is attached to is expected to have a ``base_uri`` attribute.

    It may optionally have an ``environ`` attribute for the current
    WSGI environment (used for subrequests with HTTPEncode).
    """

    default_validator = None
    # For PUTs:
    content_type = 'application/octet-stream'
    unicode = False

    def __init__(self, path, validator=None, unicode=NoDefault,
                 content_type=None):
        self.path = path
        self.validator = validator
        if unicode is not NoDefault:
            if unicode and not isinstance(unicode, basestring):
                unicode = 'utf8'
            self.unicode = unicode
        if content_type is not None:
            self.content_type = content_type

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        uri, environ = self.get_uri(obj)
        value = GET(uri, environ=environ, decode_result=False)
        if self.unicode:
            # @@: Should pick up encoding from headers
            value = value.decode(self.unicode)
        if self.default_validator:
            value = self.default_validator.to_python(value)
        if self.validator:
            value = self.validator.to_python(value)
        return value

    def __set__(self, obj, value):
        if self.validator:
            value = self.validator.from_python(value)
        if self.default_validator:
            value = self.default_validator.from_python(value)
        if self.unicode and not isinstance(value, str):
            if not isinstance(value, unicode):
                value = unicode(value)
            value = value.encode(self.unicode)
        uri, environ = self.get_uri(obj)
        PUT(uri, (self.content_type, value), environ=environ)

    def __delete__(self, obj):
        uri, environ = self.get_uri(obj)
        DELETE(uri, environ=environ)

    def get_uri(self, obj):
        uri = urlparse.urljoin(obj.base_uri, self.path)
        environ = getattr(obj, 'environ', None)
        return uri, environ
        
    def __repr__(self):
        kw = {}
        if self.validator:
            kw['validator'] = validator=self.validator
        if 'unicode' in self.__dict__:
            kw['unicode'] = self.unicode
        if 'content_type' in self.__dict__:
            kw['content_type'] = self.content_type
        return simple_repr('remote', self.path, **kw)

class json_remote(remote):

    default_validator = validators.JSONConverter()
    content_type = 'application/json'
