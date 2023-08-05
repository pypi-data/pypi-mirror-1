"""
A set of descriptors for creating the server-side component of a
web-based API.
"""
from paste import httpexceptions
import paste.request
from ohm.validators import JSONConverter, SimplePostConverter, \
     to_python_headers, from_python_headers, SimplePostIdentity
from formencode.api import Invalid
import cgi
from paste.request import EnvironHeaders
from paste.util.template import bunch
import re

class ClassInit(type):
    """
    Metaclass to call __classinit__.
    """
    def __new__(meta, class_name, bases, new_attrs):
        cls = type.__new__(meta, class_name, bases, new_attrs)
        if new_attrs.has_key('__classinit__'):
            cls.__classinit__ = staticmethod(cls.__classinit__.im_func)
        cls.__classinit__(cls, new_attrs)
        return cls

class ApplicationWrapper(object):

    """
    Object that wraps another object with a WSGI application
    interface.

    Primarily provides dispatch to attributes which put themselves in
    ``_attribute_apps`` (particular ``Setter()``).
    """

    __metaclass__ = ClassInit
    _attribute_apps = []

    def __classinit__(cls, new_attrs):
        if not '_attribute_apps' in new_attrs:
            cls._attribute_apps = list(cls._attribute_apps)
        for name, value in new_attrs.items():
            if hasattr(value, '__addtoclass__'):
                value.__addtoclass__(cls, name)

    def __init__(self, obj):
        self.object = obj

    def __repr__(self):
        return '<%s wrapping %s>' % (
            self.__class__.__name__,
            repr(self.object).strip('<>'))
    
    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        for prefix, app in self._attribute_apps:
            if (prefix == path_info
                or path_info.startswith(prefix+'/')):
                environ['SCRIPT_NAME'] = environ.get('SCRIPT_NAME', '')+path_info[:len(prefix)]
                environ['PATH_INFO'] = path_info[len(prefix):]
                break
        else:
            return self.not_found(environ, start_response)
        environ['ohm.object_wrapped'] = self.object
        environ['ohm.wrapper'] = self
        return app(environ, start_response)

    def not_found(self, environ, start_response):
        exc = httpexceptions.HTTPNotFound(
            'No handler for %r (need one of attributes: %s)'
            % (self, ', '.join([repr(path) for path, app in self._attribute_apps])))
        return exc(environ, start_response)

    def add_attribute_app(cls, prefix, app):
        if prefix.endswith('/'):
            prefix = prefix[:-1]
        if not prefix.startswith('/'):
            prefix = '/' + prefix
        cls._attribute_apps.append((prefix, app))
        cls._attribute_apps.sort(
            key=lambda i: -len(i[0]))

    add_attribute_app = classmethod(add_attribute_app)

class Setter(object):

    default_encoding = 'utf8'
    default_validator = None
    content_type = 'application/octet-stream'

    def __init__(self,
                 unicode=False,
                 content_type=None,
                 uri_path=None,
                 parent_app=None,
                 attr=None,
                 validator=None,
                 POST=None,
                 getter=None,
                 setter=None,
                 deleter=None):
        self.unicode = unicode
        if content_type is not None:
            self.content_type = content_type
        self.parent_app = parent_app
        self.attr = attr
        self.validator = validator
        self.uri_path = uri_path
        if POST is None:
            POST = {}
        elif not isinstance(POST, dict):
            POST = {'': POST}
        self.POST = POST
        if getter is not None:
            self.getter = getter
        if setter is not None:
            self.setter = setter
        if deleter is not None:
            self.deleter = deleter

    def __addtoclass__(self, cls, name):
        assert self.parent_app is None and self.attr is None, (
            "Attribute %r bound multiple times to different "
            "classes (first %r as %r, not %r as %r)"
            % (self.parent_app, self.attr, cls, name))
        self.parent_app = cls
        self.attr = name
        if self.uri_path is None:
            self.uri_path = name
        assert self.uri_path not in cls._attribute_apps, (
            "Setter already registered at %r: %r"
            % (self.uri_path, cls._attribute_apps[self.uri_path]))
        cls.add_attribute_app(self.uri_path, self)

    def getter(self, obj):
        try:
            return getattr(obj, self.attr)
        except AttributeError, e:
            raise httpexceptions.HTTPNotFound(
                "You cannot read this resource (attribute %r: %s)"
                % (self.attr, e))

    def setter(self, obj, value):
        try:
            setattr(obj, self.attr, value)
        except AttributeError, e:
            # @@: I don't at this point actually know what is allowed
            # Maybe BadRequest would be more straight-forward?
            # Or Forbidden
            raise httpexceptions.HTTPMethodNotAllowed(
                "You cannot PUT to this resource (attribute %r: %s)"
                % (self.attr, e),
                headers=[('Allow', 'GET,POST')])

    def deleter(self, obj):
        try:
            delattr(obj, self.attr)
        except AttributeError, e:
            raise httpexceptions.HTTPMethodNotAllowed(
                "You cannot DELETE this resource (attribute %r: %s)"
                % (self.attr, e),
                headers=[('Allow', 'GET,PUT,POST')])
        
    def __call__(self, environ, start_response):
        obj = environ['ohm.object_wrapped']
        method = environ['REQUEST_METHOD']
        self_method = getattr(self, 'method_'+method, None)
        if self_method is None:
            exc = httpexceptions.HTTPNotImplemented(
                "The method %r is not implemented" % method)
            return exc(environ, start_response)
        try:
            return self_method(obj, environ, start_response)
        except Invalid, e:
            msg = str(e)
            exc = httpexceptions.HTTPBadRequest(msg)
            return exc(environ, start_response)
        except httpexceptions.HTTPException, exc:
            return exc(environ, start_response)

    def method_GET(self, obj, environ, start_response):
        try:
            data = self.getter(obj)
        except AttributeError, e:
            exc = httpexceptions.HTTPNotFound(
                "Cannot retrieve: %s" % e)
            return exc(environ, start_response)
        state = bunch(object=obj, attr=self.attr)
        if self.validator:
            data = self.validator.from_python(data, state)
        if self.default_validator:
            data = self.default_validator.from_python(data, state)
        extra_ct = ''
        if self.unicode:
            assert isinstance(data, unicode), (
                "Did not get unicode data as expected; got: %r"
                % data)
            data = data.encode(self.default_encoding)
            extra_ct += '; charset=%s' % self.default_encoding
        else:
            assert isinstance(data, str), (
                "Did not get str data as expected; got: %r"
                % data)
        content_type = self.content_type + extra_ct
        length = str(len(data))
        start_response('200 OK',
                       [('Content-Type', content_type),
                        ('Content-Length', length)])
        return [data]

    def method_PUT(self, obj, environ, start_response):
        input = environ['wsgi.input']
        content_length = int(environ.get('CONTENT_LENGTH', '0'))
        data = input.read(content_length)
        if self.unicode:
            # @@: Should at least try to read from environ
            data = data.decode(self.default_encoding)
        state = bunch(object=obj, attr=self.attr)
        if self.default_validator:
            data = self.default_validator.to_python(data, state)
        if self.validator:
            data = self.validator.to_python(data, state)
        self.setter(obj, data)
        start_response('204 No Content', [])
        return []

    def method_DELETE(self, obj, environ, start_response):
        self.deleter(obj)
        start_response('204 No Content', [])
        return []

    def method_POST(self, obj, environ, start_response):
        if not self.POST:
            exc = httpexceptions.HTTPNotImplemented(
                "No POST methods have been defined")
            return exc(environ, start_response)
        qs = cgi.parse_qsl(environ.get('QUERY_STRING', ''),
                           keep_blank_values=True)
        command = ''
        if qs and not qs[0][1]:
            command = qs[0][0]
        for key, value in qs:
            if key == 'command':
                command = value
                break
        if command not in self.POST:
            if not command:
                command_desc = '(empty)'
            else:
                command_desc = repr(command)
            exc = httpexceptions.HTTPBadRequest(
                "No POST method %s defined (need one of %s)"
                % (command_desc,
                   ', '.join([repr(k) for k in self.POST.keys()])))
            return exc(environ, start_response)
        command = self.POST[command]
        headers = EnvironHeaders(environ)
        content_length = int(environ.get('CONTENT_LENGTH', '0'))
        input = environ['wsgi.input']
        body = input.read(content_length)
        response = self.call_POST(obj, command, (headers, body))
        if response is None or response == '':
            start_response('204 No Content', [])
            return ['']
        headers, body = self._coerce_POST_response(response)
        if not body:
            status = '204 No Content'
            body = ''
        else:
            status = '200 OK'
        headers.append(('Content-Length', str(len(body))))
        start_response(status, headers)
        return [body]

    def call_POST(self, obj, command, request):
        if isinstance(command, basestring):
            if self.default_validator:
                command = (self.default_validator, command)
            else:
                command = (SimplePostConverter(), command)
        if (not isinstance(command, (list, tuple))
            or not len(command) == 2):
            raise TypeError(
                "Commands must be in the form (validator, method) not %r"
                % command)
        validator, method = command
        if validator is None:
            validator = SimplePostIdentity()
        state = bunch(object=obj, method=method)
        args = to_python_headers(validator, request, state)
        if isinstance(args, dict):
            posargs, kwargs = (), args
        elif isinstance(args, tuple):
            posargs, kwargs = args, {}
        else:
            posargs, kwargs = (args,), {}
        if isinstance(method, basestring):
            method = getattr(obj, method)
        else:
            posargs = (obj,) + posargs
        response = method(*posargs, **kwargs)
        response = from_python_headers(validator, response, state)
        return response

    _text_re = re.compile(r'^[^\x00-\x1f]+$')
    _mime_re = re.compile(r'^[a-z]+/[a-zA-Z0-9._-]_$')

    def _coerce_POST_response(self, response):
        if isinstance(response, basestring):
            if response.lstrip().startswith('<?xml'):
                content_type = 'application/xml'
            elif response.lstrip()[:5].lower() == '<html':
                content_type = 'text/html'
            elif (isinstance(response, unicode)
                  or self._text_re.search(response)):
                content_type = 'text/plain'
            else:
                content_type = 'application/octet-stream'
            if isinstance(response, unicode):
                content_type += '; charset=utf8'
                response = response.encode('utf8')
            return [('Content-Type', content_type)], response
        if (isinstance(response, tuple)
            and len(response) == 2
            and isinstance(response[0], basestring)
            and self._mime_re.search(response[0])):
            return [('Content-Type', response[0])], response[1]
        if (isinstance(response, tuple)
            and len(response) == 2
            and (hasattr(response[0], 'items')
                 or isinstance(response[0], list))):
            if not isinstance(response[0], list):
                response = (response[0].items(), response[1])
            return response
        raise ValueError(
            "I don't know how to turn %r into a WSGI response"
            % response)
    
class MethodNotAllowed(object):
    """
    Function placeholder that always raises HTTPMethodNotAllowed
    """

    def __init__(self, msg="Method not allowed", allow='GET'):
        self.msg = msg
        self.allow = allow

    def __call__(self, *args, **kw):
        raise httpexceptions.HTTPMethodNotAllowed(
            self.msg,
            headers=[('Allow', self.allow)])


class JSONSetter(Setter):

    default_validator = JSONConverter()
    # simplejson does the encoding:
    content_type = 'application/json; charset=utf8'

def appfactory(uri_path=None):
    """
    Decorator that decorates a function that produces a WSGI
    application
    """
    def decorator(func):
        return FuncFactory(func, uri_path=uri_path)
    return decorator

class FuncFactory(Setter):

    def __init__(self, func, uri_path=None):
        self.func = func
        Setter.__init__(self, uri_path=uri_path)

    def __call__(self, environ, start_response):
        obj = environ['ohm.object_wrapped']
        app = self.func(obj)
        return app(environ, start_response)
