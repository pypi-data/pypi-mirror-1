import os
import shutil
from ohm import persist
from ohm import descriptors
import py.test
from formencode.api import FancyValidator, Invalid

class IntableValidator(FancyValidator):

    def validate(self, value, state):
        try:
            int(value)
        except:
            raise Invalid('Not a valid int: %r' % value, value, state)

    def _to_python(self, value, state):
        self.validate(value, state)
        return value

    _from_python = _to_python

class VariousStuff(object):

    def __init__(self, base_dir):
        # The basic contract for file_property:
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)

    str_prop = persist.file_property('str.txt')
    uni_prop = persist.file_property('unicode.txt', encoding='utf8')
    cache_prop = descriptors.cache(
        'cache_prop',
        persist.file_property('cached.txt'))

    json_prop = descriptors.json_converter(
        persist.file_property('json.txt'))
    line_prop = descriptors.line_converter(
        persist.file_property('lines.txt'))
    valid_prop = descriptors.converter(
        persist.file_property('valid.txt'),
        validator=IntableValidator())

    def add_line(self, value):
        self.line_prop = self.line_prop + [value]

    def delete_line(self, value):
        current = self.line_prop
        if value not in current:
            raise ValueError(
                'You cannot remove %r because it isn\'t in the current values'
                % value)
        current.remove(value)
        self.line_prop = current

def test_stuff():
    base_dir = os.path.join(os.path.dirname(__file__),
                            'various-stuff')
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    def contents(filename):
        filename = os.path.join(base_dir, filename)
        if not os.path.exists(filename):
            return None
        f = open(filename, 'rb')
        c = f.read()
        f.close()
        return c
    def write_file(filename, value):
        filename = os.path.join(base_dir, filename)
        f = open(filename, 'wb')
        f.write(value)
        f.close()
    obj = VariousStuff(base_dir)
    t = obj.str_prop = 'this is a test\x00'
    assert contents('str.txt') == t
    assert obj.str_prop == t
    write_file('str.txt', 'test2')
    assert obj.str_prop == 'test2'
    py.test.raises(ValueError,
                   "obj.str_prop = 10")
    py.test.raises(ValueError,
                   "obj.str_prop = u'test'")
    assert obj.str_prop == 'test2'
    t = obj.uni_prop = u'this\u1010 test'
    assert contents('unicode.txt') == t.encode('utf8')
    assert t == obj.uni_prop
    assert isinstance(obj.uni_prop, unicode)
    py.test.raises(ValueError,
                   "obj.uni_prop = 'test'")
    assert obj.uni_prop == t
    t = obj.cache_prop = 'test1'
    assert contents('cached.txt') == t
    write_file('cached.txt', 'test2')
    assert obj.cache_prop == 'test1'
    VariousStuff.cache_prop.expire(obj)
    assert obj.cache_prop == 'test2'
    v = obj.json_prop = {'a': 1, 'b': 2, 'c': ['a b c']}
    assert obj.json_prop == v
    assert contents('json.txt') == '{"a": 1, "c": ["a b c"], "b": 2}'
    v = obj.line_prop = ['a', 'b', 'cde']
    assert v == obj.line_prop
    assert contents('lines.txt') == 'a\nb\ncde\n'
    v = obj.valid_prop = '10'
    assert v == obj.valid_prop
    py.test.raises(Invalid,
                   "obj.valid_prop = 'x'")
    py.test.raises(ValueError,
                   "obj.valid_prop = 10")
    
