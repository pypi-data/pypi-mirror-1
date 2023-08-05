from ohm.validators import JSONConverter, LineConverter

def simple_repr(func_name, *args, **kw):
    """
    Helper function for reprs like 'func_name(args, keywords)'
    """
    args = [repr(x) for x in args]
    args.extend(['%s=%r' % (name, value)
                 for name, value in sorted(kw.items())])
    return '%s(%s)' % (func_name, ', '.join(args))

class cache(object):

    """
    A caching descriptor wrapper.  Takes the attribute name and the
    wrapped descriptor as arguments.

    To expire, use ``MyClass.cached_attr.expire(my_object)`` where
    ``my_object`` is an instance of ``MyClass``.
    """

    def __init__(self, name, getter):
        self.name = name
        self._attr_name = '_cache_%s' % name
        self.getter = getter

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        try:
            return getattr(obj, self._attr_name)
        except AttributeError:
            pass
        value = self.getter.__get__(obj, type)
        setattr(obj, self._attr_name, value)
        return value

    def __set__(self, obj, value):
        self.getter.__set__(obj, value)
        setattr(obj, self._attr_name, value)

    def __delete__(self, obj):
        self.getter.__delete__(obj)
        self.expire(obj)

    def expire(self, obj):
        try:
            delattr(obj, self._attr_name)
        except AttributeError:
            pass

    def __repr__(self):
        return simple_repr('cache', self.name, self.getter)

class converter(object):

    """
    Applies a FormEncode validator/converter to a descriptor.
    Supports both a class-level ``default_validator``, and custom
    validators.

    Subclasses (like ``json_converter``) might set
    ``default_validator``.
    """

    default_validator = None

    def __init__(self, getter=None, validator=None):
        self.getter = getter
        # Extra validation, after native validation
        self.validator = validator

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = self.getter.__get__(obj, type)
        if self.validator:
            value = self.validator.to_python(value)
        if self.default_validator:
            value = self.default_validator.to_python(value)
        return value

    def __set__(self, obj, value):
        if self.default_validator:
            value = self.default_validator.from_python(value)
        if self.validator:
            value = self.validator.from_python(value)
        self.getter.__set__(obj, value)

    def __delete__(self, obj):
        self.getter.__delete__(obj)

    def __repr__(self):
        return simple_repr(self.__class__.__name__,
                           self.getter)

    def __getattr__(self, attr):
        # All other attributes are delegated to the getter
        return getattr(self.getter, attr)

class watcher(object):
    """
    Calls a callback function with (obj, old_value, new_value) everytime
    an attribute is set.

    You can listen before or after the value is actually set, with
    before_watcher and after_watcher.  delete_watcher (if given) is
    called with (self, old_value) everytime an attribute is deleted,
    right before the delete.
    """

    def __init__(self, getter, before_watcher=None,
                 after_watcher=None, delete_watcher=None):
        self.getter = getter
        self.before_watcher = before_watcher
        self.after_watcher = after_watcher
        self.delete_watcher = delete_watcher

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = self.getter.__get__(obj, type)
        return value

    def __set__(self, obj, value):
        old_value = self.getter.__get__(obj, None)
        if self.before_watcher is not None:
            self.before_watcher(obj, old_value, value)
        self.getter.__set__(obj, value)
        if self.after_watcher is not None:
            self.after_watcher(obj, old_value, value)

    def __delete__(self, obj):
        if self.delete_watcher is not None:
            old_value = self.getter.__get__(obj, None)
            self.delete_watcher(obj, old_value)
        self.getter.__delete__(obj)

    def __repr__(self):
        kw = {}
        if self.before_watcher:
            kw['before_watcher'] = self.before_watcher
        if self.after_watcher:
            kw['after_watcher'] = self.after_watcher
        if self.delete_watcher:
            kw['delete_watcher'] = self.delete_watcher
        return simple_repr(self.__class__.__name__,
                           self.getter, **kw)
    

class json_converter(converter):
    """
    Wraps a descriptor and does JSON decoding/encoding.

    An underlying string shows up as the JSON it decodes to.
    """

    default_validator = JSONConverter()

class line_converter(converter):
    """
    Wraps a descriptor, and splits/joins text lines.

    An underlying string shows up as a list of strings split by line.
    """
    default_validator = LineConverter()
