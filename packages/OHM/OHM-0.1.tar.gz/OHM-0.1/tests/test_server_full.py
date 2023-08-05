from paste.fixture import TestApp
from ohm import server
from ohm import validators
import py.test
import md5

class Person(object):
    def __init__(self, first_name, last_name, email,
                 password_hashed):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hashed = password_hashed

    def check_password(self, password):
        hashed = md5.new(password).hexdigest()
        return hashed == self.password_hashed

    @property
    def html(self):
        return '%s %s &gt;<a href="mailto:%s">%s</a>' % (
            self.first_name, self.last_name,
            self.email, self.email)


class PersonApplication(server.ApplicationWrapper):

    first_name = server.Setter(content_type='text/plain')
    last_name = server.Setter(content_type='text/plain')
    email = server.Setter(content_type='text/plain')
    password_hashed = server.Setter(content_type='text/plain')
    html = server.Setter(uri_path='summary.html', content_type='text/html')

    check_password = server.JSONSetter(
        POST=(validators.ToFrom(validators.SimplePostIdentity(), validators.JSONConverter()),
              'check_password'),
        getter=server.MethodNotAllowed(),
        setter=server.MethodNotAllowed())

    def get_state(obj):
        return obj.__dict__

    def set_state(obj, d):
        for name, value in d.items():
            setattr(obj, name, value)

    full = server.Setter(
        uri_path='',
        getter=get_state,
        setter=set_state,
        validator=validators.XMLRPCConverter())
    
def put(app, uri, data, **kw):
    kw.setdefault('status', (200, 201, 204))
    return app.post(uri, data, extra_environ={'REQUEST_METHOD': 'PUT'},
                    **kw)

def test_wrapper_post():
    obj = Person('Ian', 'Bicking', 'ianb@example.com',
                 md5.new('password').hexdigest())
    wsgi_app = PersonApplication(obj)
    app = TestApp(wsgi_app)
    assert app.get('/first_name').body == 'Ian'
    put(app, '/first_name', 'Monica')
    assert app.get('/first_name').body == 'Monica'
    assert obj.first_name == 'Monica'
    res = app.post('/check_password', 'foo')
    assert res.body == 'false'
    res = app.post('/check_password', 'password')
    assert res.body == 'true'
    res = app.get('/summary.html')
    res.mustcontain(
        'Monica', 'Bicking',
        'mailto:ianb@example.com')
    # 405 Method Not Allowed:
    put(app, '/summary.html', 'foo', status=405)
    res = app.get('/')
    data = validators.XMLRPCConverter().to_python(res.body)
    data['email'] = 'monica@example.com'
    put(app, '/', validators.XMLRPCConverter().from_python(data))
    assert obj.email == data['email']
    assert obj.first_name == 'Monica'
    
