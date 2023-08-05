import os
import shutil
from paste.urlparser import StaticURLParser
from paste.fileapp import FileApp
from paste import httpexceptions
from paste import request
import cgi
import urllib

class LilDAV(object):

    """
    A DAV-like WSGI app that only knows GET, PUT, DELETE, MKCOL.
    PROPLIST is also planned, but probably nothing else.
    """
    
    def __init__(self, directory, root_directory=None):
        if os.path.sep != '/':
            directory = directory.replace(os.path.sep, '/')
        self.directory = directory
        if root_directory is not None:
            root_directory = os.path.normpath(root_directory)
        else:
            root_directory = directory
        self.root_directory = root_directory
        if os.path.sep != '/':
            directory = directory.replace('/', os.path.sep)
            self.root_directory = self.root_directory.replace('/', os.path.sep)

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if not path_info:
            return self.add_slash(environ, start_response)
        filename = request.path_info_pop(environ)
        full = os.path.normpath(os.path.join(self.directory, filename))
        if os.path.sep != '/':
            full = full.replace('/', os.path.sep)
        if self.root_directory is not None and not full.startswith(self.root_directory):
            # Out of bounds
            exc = httpexceptions.HTTPNotFound('The request path is invalid')
            return exc(environ, start_response)
        if os.path.isdir(full) and environ['PATH_INFO']:
            subapp = self.__class__(
                full, root_directory=self.root_directory)
            return subapp(environ, start_response)
        fa = self.make_app(full)
        return fa(environ, start_response)

    def make_app(self, filename):
        return PuttableFileApp(filename)

    def add_slash(self, environ, start_response):
        """
        This happens when you try to get to a directory
        without a trailing /
        """
        url = request.construct_url(environ, with_query_string=False)
        url += '/'
        if environ.get('QUERY_STRING'):
            url += '?' + environ['QUERY_STRING']
        exc = httpexceptions.HTTPMovedPermanently(
            'The resource has moved to %s - you should be redirected '
            'automatically.''' % url,
            headers=[('location', url)])
        return exc.wsgi_application(environ, start_response)
    
    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.directory)

class PuttableFileApp(FileApp):
    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD']
        if method == 'PUT':
            return self.put(environ, start_response)
        elif method == 'DELETE':
            return self.delete(environ, start_response)
        elif method == 'MKCOL':
            return self.mkcol(environ, start_response)
        elif method == 'GET':
            if os.path.isdir(self.filename):
                return self.directory_index(environ, start_response)
            else:
                return FileApp.__call__(self, environ, start_response)
        else:
            exc = httpexceptions.HTTPMethodNotAllowed()
            return exc(environ, start_response)

    def directory_index(self, environ, start_response):
        filenames = os.listdir(self.filename)
        filenames.sort()
        parts = [
            '<html><head><title>Directory Listing</title></head>\n'
            '<body><h1>Directory Listing</h1>\n'
            '<ul>\n']
        for filename in filenames:
            parts.append(
                '<li><a href="%s">%s</a></li>\n'
                % (cgi.escape(urllib.quote(filename), 1),
                   cgi.escape(filename, 1)))
        parts.append(
            '</ul></body></html>')
        body = ''.join(parts)
        start_response(
            '200 OK', [('Content-type', 'text/html'),
                       ('Content-length', str(len(body)))])
        return [body]

    def update(self, force=False):
        try:
            return FileApp.update(self, force=force)
        except OSError:
            pass

    def put(self, environ, start_response):
        exists = os.path.exists(self.filename)
        f = open(self.filename, 'wb')
        size = int(environ['CONTENT_LENGTH'])
        input = environ['wsgi.input']
        while size > 0:
            c = input.read(max(size, 4096))
            size -= len(c)
            f.write(c)
        f.close()
        if exists:
            start_response('204 No Content', [])
        else:
            start_response('201 Created', [])
        return ['']

    def delete(self, environ, start_response):
        if not os.path.exists(self.filename):
            exc = httpexceptions.HTTPPreconditionFailed('File %s does not exists' % self.filename)
            return exc(environ, start_response)
        if os.path.isdir(self.filename):
            shutil.rmtree(self.filename)
        else:
            os.unlink(self.filename)
        start_response('204 No Content', [])
        return ['']
    
    def mkcol(self, environ, start_response):
        if os.path.exists(self.filename):
            exc = httpexceptions.HTTPPreconditionFailed('%s already exists' % self.filename)
            return exc(environ, start_response)
        os.mkdir(self.filename)
        start_response('201 Created', [])
        return ['']
    
