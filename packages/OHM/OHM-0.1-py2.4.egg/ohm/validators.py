from formencode.api import FancyValidator, Invalid, Validator
import simplejson
import cgi
from cStringIO import StringIO
from paste.util.multidict import MultiDict
import xmlrpclib

class JSONConverter(FancyValidator):

    def _to_python(self, value, state):
        # @@: Should catch error:
        try:
            return simplejson.loads(value)
        except ValueError, e:
            raise Invalid('Invalid JSON (%s): %r' % (e, value), value, state)

    def _from_python(self, value, state):
        return simplejson.dumps(value)

class LineConverter(FancyValidator):

    if_empty = ()

    def _to_python(self, value, state):
        value = value.splitlines()
        while value and not value[-1]:
            value.pop()
        return value

    def _from_python(self, value, state):
        return '\n'.join(value) + '\n'

class XMLRPCConverter(FancyValidator):

    object_name = None

    _marshal = xmlrpclib.Marshaller(allow_none=True)
    _marshal_dump = _marshal._Marshaller__dump

    def _from_python(self, value, state):
        if self.object_name is None:
            object_name = 'object'
            if getattr(state, 'object', None):
                object_name = state.object.__class__.__name__.lower()
        else:
            object_name = self.object_name
        body = self._to_xmlrpc(value, state)
        return '<%s>%s</%s>' % (object_name, body, object_name)

    def _to_xmlrpc(self, value, state):
        out = []
        self._marshal_dump(value, out.append)
        return ''.join(out)

    def _to_python(self, value, state):
        value = self._unwrap(value, state)
        value = self._wrap_xmlrpc(value, state)
        parser, unmarshal = xmlrpclib.getparser()
        parser.feed(value)
        parser.close()
        result = unmarshal.close()[0]
        return result

    def _unwrap(self, value, state):
        start = value.find('>')
        if start == -1:
            raise Invalid(
                "Not valid XML: %r" % value,
                value, state)
        value = value[start+1:]
        end = value.rfind('<')
        if end == -1:
            raise Invalid(
                "Not valid XML: %r" % value,
               value, state)
        value = value[:end]
        return value

    def _wrap_xmlrpc(self, value, state):
        return (
            '<methodResponse><params><param>'
            '<value>%s</value>'
            '</param></params></methodResponse>' % value)
        

class ToFrom(Validator):
    """
    Applies one validator when going to_python, another when going
    from_python (for non-symmetrical conversion).
    """

    to_python_validator = None
    from_python_validator = None
    __unpackargs__ = ('to_python_validator', 'from_python_validator')

    def __init__(self, *args, **kw):
        Validator.__init__(self, *args, **kw)
        if not self.to_python_validator:
            raise ValueError(
                "You must give a value for to_python_validator")
        if not self.from_python_validator:
            raise ValueError(
                "You must give a value for from_python_validator")
        if (isinstance(self.to_python_validator, type)
            and issubclass(self.to_python_validator, Validator)):
            self.to_python_validator = self.to_python_validator()
        if (isinstance(self.from_python_validator, type)
            and issubclass(self.from_python_validator, Validator)):
            self.from_python_validator = self.from_python_validator()

    def to_python(self, value, state):
        return self.to_python_validator.to_python(value, state)

    def from_python(self, value, state):
        return self.from_python_validator.from_python(value, state)
        
##################################################
## POST request validators
##################################################

class SimplePostConverter(FancyValidator):

    encoding = None
    content_type = None
    header_validator = True

    def _to_python(self, value, state=None):
        headers, body = value
        if self.encoding is not None:
            body = body.decode(self.encoding)
        return body

    def _from_python(self, value, state=None):
        headers = {}
        if self.content_type is not None:
            headers['Content-Type'] = self.content_type
        if self.encoding:
            if headers.get('Content-Type'):
                headers['Content-Type'] += '; charset=%s' % self.encoding
            if isinstance(value, unicode):
                value = value.encode(self.encoding)
        return (headers, value)
    
class FormPostConverter(FancyValidator):

    header_validator = True
    dict = False

    def _to_python(self, value, state=None):
        headers, body = value
        environ = {}
        for name, value in headers:
            if name.lower() == 'content-type':
                name = 'CONTENT_TYPE'
            else:
                name = 'HTTP_%s' % (name.upper().replace('-', '_'))
            environ[name] = value
        environ['CONTENT_LENGTH'] = str(len(body))
        fs = cgi.FieldStorage(fp=StringIO(body),
                              environ=environ,
                              keep_blank_values=1)
        if not dict:
            return fs
        result = MultiDict()
        for field in fs.list:
            result.add(field.name, field.value)
        return result

    def _from_python(self, value, state=None):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'}
        body = urllib.urlencode(value, doseq=True)
        return headers, body

class SimplePostIdentity(FancyValidator):

    default_encoding = 'utf8'
    encoding = None

    def _to_python(self, value, state):
        if self.encoding and isinstance(value, str):
            value = value.decode(self.encoding)
        return value

    def _from_python(self, value, state):
        if not isinstance(value, basestring):
            if hasattr(value, '__unicode__'):
                value = unicode(value)
            else:
                value = str(value)
        if isinstance(value, unicode):
            value = value.encode(
                self.encoding or self.default_encoding)
        return value

def to_python_headers(validator, header_body, state=None):
    if getattr(validator, 'header_validator', False):
        return validator.to_python(header_body, state)
    else:
        return validator.to_python(header_body[1], state)

def from_python_headers(validator, data, state=None):
    if getattr(validator, 'header_validator', False):
        return ({}, validator.from_python(data, state))
    else:
        return validator.from_python(data, state)

