from httpencode import HTTP
http = HTTP()
from httpencode import BadRequestError
import py.test
from test_server import make_obj, VariousStuffWrapper
from ohm.client import remote, json_remote
from ohm.validators import LineConverter

class RemoteVarious(object):

    def __init__(self, base_uri):
        self.base_uri = base_uri
    
    str_prop = remote('str_prop')
    uni_prop = remote('uni_prop', unicode=True)
    json_prop = json_remote('json_prop')
    line_prop = remote('line_prop', validator=LineConverter())
    valid_prop = remote('valid-place')

def test_client():
    obj = make_obj()
    wsgi_app = VariousStuffWrapper(obj)
    # Install mock
    http.mock_wsgi_app = wsgi_app
    robj = RemoteVarious(base_uri='http://localhost/')
    obj.str_prop = 'foo'
    assert robj.str_prop == 'foo'
    # 404:
    py.test.raises(BadRequestError, 'robj.uni_prop')
    t = obj.uni_prop = u'foo\u1010bar'
    assert robj.uni_prop == t
    t = obj.json_prop = [1, 2, 3]
    assert robj.json_prop == t
    t = robj.json_prop = [3, 2, 1]
    assert obj.json_prop == t
    py.test.raises(BadRequestError, "robj.valid_prop = 'x'")
    robj.valid_prop = '10'
    assert obj.valid_prop == '10'
