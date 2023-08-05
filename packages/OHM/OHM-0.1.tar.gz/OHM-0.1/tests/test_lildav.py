import os
import shutil
from paste.fixture import TestApp
from ohm.lildav import LilDAV

base_dir = os.path.join(os.path.dirname(__file__), 'test-dav')

def setup_place():
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.mkdir(base_dir)

def contents(fn):
    fn = os.path.join(base_dir, fn)
    if not os.path.exists(fn):
        return None
    if os.path.isdir(fn):
        return '<dir>'
    f = open(fn, 'rb')
    c = f.read()
    f.close()
    return c

def test_dav():
    setup_place()
    wsgi_app = LilDAV(base_dir)
    app = TestApp(wsgi_app)
    app.get('/foo.html', status=404)
    app.post('/foo.html', 'test this', status=201,
             extra_environ={'REQUEST_METHOD': 'PUT'})
    res = app.get('/foo.html')
    assert res.body == 'test this'
    assert contents('foo.html') == 'test this'
    app.get('/foo.html', status=204,
            extra_environ={'REQUEST_METHOD': 'DELETE'})
    assert contents('foo.html') is None
    app.get('/bar', status=201,
            extra_environ={'REQUEST_METHOD': 'MKCOL'})
    assert contents('bar') == '<dir>'
    app.post('/bar/baz.html', 'test that', status=201,
             extra_environ={'REQUEST_METHOD': 'PUT'})
    res = app.get('/bar/baz.html')
    assert res.body == 'test that'
    assert contents('bar/baz.html') == 'test that'
    app.post('/bar/baz.html', 'test 2', status=204,
             extra_environ={'REQUEST_METHOD': 'PUT'})
    res = app.get('/bar/baz.html')
    assert res.body == 'test 2'
    assert contents('bar/baz.html') == 'test 2'
    app.post('/bar/', '', status=204,
             extra_environ={'REQUEST_METHOD': 'DELETE'})
    assert contents('bar/') is None
    res = app.get('/')
    
