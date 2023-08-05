import os
import shutil
from test_persist import VariousStuff
from paste.fixture import TestApp
from ohm import server
from ohm import persist
from ohm import validators
import py.test

class VariousStuffWrapper(server.ApplicationWrapper):

    str_prop = server.Setter()
    uni_prop = server.Setter(unicode=True, content_type='text/plain')
    json_prop = server.JSONSetter(uri_path='json/prop')
    line_prop = server.Setter(validator=validators.LineConverter(), content_type='text/plain', POST={'add': 'add_line', 'delete': 'delete_line'})
    valid_prop = server.Setter(uri_path='valid-place')

def make_obj():
    base_dir = os.path.join(os.path.dirname(__file__),
                            'various-server')
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    obj = VariousStuff(base_dir)
    return obj

def test_wrapper_get():
    obj = make_obj()
    wrapper = VariousStuffWrapper(obj)
    app = TestApp(wrapper)
    obj.str_prop = 'foo'
    res = app.get('/str_prop')
    assert res.body == 'foo'
    assert res.header('content-type') == 'application/octet-stream'
    obj.uni_prop = u'test\u1010this'
    res = app.get('/uni_prop')
    assert res.body == obj.uni_prop.encode('utf8')
    assert res.header('content-type') == 'text/plain; charset=utf8'
    obj.json_prop = [1, 2]
    res = app.get('/json/prop')
    assert res.body == '[1, 2]'
    assert res.header('content-type') == 'application/json; charset=utf8'
    obj.line_prop = ['a', 'b']
    res = app.get('/line_prop')
    assert res.body == 'a\nb\n'
    assert res.header('content-type') == 'text/plain'
    obj.valid_prop = '1'
    res = app.get('/valid-place')
    assert res.body == '1'

def test_wrapper_put():
    obj = make_obj()
    wrapper = VariousStuffWrapper(obj)
    app = TestApp(wrapper)
    obj.str_prop = 'foo'
    res = app.post(
        '/str_prop', 'bar',
        extra_environ=dict(REQUEST_METHOD='PUT'),
        status=204)
    assert obj.str_prop == 'bar'
    res = app.post(
        '/json/prop', '[3, 2, 1]',
        extra_environ=dict(REQUEST_METHOD='PUT'),
        status=204)
    assert obj.json_prop == [3, 2, 1]
    res = app.post(
        '/valid-place', '10',
        extra_environ=dict(REQUEST_METHOD='PUT'),
        status=204)
    assert obj.valid_prop == '10'
    res = app.post(
        '/valid-place', 'x',
        extra_environ=dict(REQUEST_METHOD='PUT'),
        status=400)

def test_wrapper_delete():
    obj = make_obj()
    wrapper = VariousStuffWrapper(obj)
    app = TestApp(wrapper)
    py.test.raises(AttributeError, "obj.str_prop")
    obj.str_prop = 'foo'
    res = app.post(
        '/str_prop', '',
        extra_environ=dict(REQUEST_METHOD='DELETE'),
        status=204)
    py.test.raises(AttributeError, "obj.str_prop")
    
def test_wrapper_post():
    obj = make_obj()
    obj.line_prop = ['a', 'b', 'c']
    wrapper = VariousStuffWrapper(obj)
    app = TestApp(wrapper)
    res = app.post('/line_prop?add', 'foobar', status=204)
    assert obj.line_prop == ['a', 'b', 'c', 'foobar']
    res = app.post('/line_prop?delete', 'b', status=204)
    assert obj.line_prop == ['a', 'c', 'foobar']
    
