import os
from ohm.descriptors import simple_repr

class NoDefault(object): pass

class file_property(object):

    def __init__(self, filename, encoding=None,
                 default=NoDefault):
        self.filename = filename
        self.encoding = encoding
        self.default = default

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        fn = self.get_filename(obj)
        if not os.path.exists(fn):
            if self.default is NoDefault:
                raise AttributeError(
                    "Attribute for file %r undefined" % os.path.basename(fn))
            return self.default
        f = open(fn, 'rb')
        c = f.read()
        f.close()
        if self.encoding:
            c = c.decode(self.encoding)
        return c

    def __set__(self, obj, value):
        fn = self.get_filename(obj)
        if self.default is not NoDefault and value == self.default:
            if os.path.exists(fn):
                os.unlink(fn)
            return
        if self.encoding:
            if isinstance(value, str):
                raise ValueError(
                    "Only unicode values allowed in attribute (not str like %r)" % value)
            elif not isinstance(value, unicode):
                raise ValueError(
                    "Only unicode values allowed in attribute (not %r)" % value)
            value = value.encode(self.encoding)
        else:
            if isinstance(value, unicode):
                raise ValueError(
                    "Only str values allowed in attribute (not unicode like %r)" % value)
            elif not isinstance(value, str):
                raise ValueError(
                    "Only str values allowed in attribute (not %r)" % value)
        f = open(fn, 'wb')
        f.write(value)
        f.close()

    def __delete__(self, obj):
        fn = self.get_filename(obj)
        if not os.path.exists(fn):
            raise AttributeError(
                "Attribute undefined")
        os.unlink(fn)
        
    def get_filename(self, obj):
        return os.path.join(obj.base_dir, self.filename)

    def __repr__(self):
        kw = {}
        if self.encoding:
            kw['encoding'] = self.encoding
        if self.default is not NoDefault:
            kw['default'] = self.default
        return simple_repr('file_property', self.filename, **kw)
