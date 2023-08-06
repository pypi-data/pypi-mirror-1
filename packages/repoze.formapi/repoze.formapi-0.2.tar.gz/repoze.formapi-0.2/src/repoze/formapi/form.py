from zope import interface

from repoze.formapi import interfaces
from repoze.formapi import marshalling

import types
import re

class Form(object):
    """Base form class. Optionally pass a dictionary as ``data`` and a
    WebOb-like request object as ``request``."""

    interface.implements(interfaces.IForm)
    
    fields = {}
    
    def __init__(self, data=None, context=None, request=None, prefix=None):
        if context is not None:
            if data is not None:
                raise ValueError(
                    "Can't provide both ``data`` and ``context``.")

            # proxy the context object
            data = Proxy(context)

        self.data = Data(data)

        # find action parameters
        if prefix is not None:
            re_prefix = re.compile(r'^%s[._-](?P<name>.*)' % prefix)
            action_params = {}
            for key, value in request.params.items():
                if key == prefix:
                    action_params[None] = value
                else:
                    m = re_prefix.search(key)
                    if m is not None:
                        action_params[m.group('name')] = value

        # initialize form actions
        actions = self.actions = []
        for action in type(self).__dict__.values():
            marker = object()
            name = getattr(action, '__action__', marker)
            if name is not marker:
                actions.append(Action(action, name, name in action_params))                

        # conditionally apply request parameters if:
        # 1. no prefix has been set
        # 2. there is a submitted action
        # 3. there are no defined actions, but a default action was submitted
        if request is not None and (
            prefix is None or \
            filter(None, actions) or \
            len(actions) == 0 and action_params.get(None) is not None):
            params = request.params.items()
        else:
            params = ()
        
        # marshall request parameters
        data, errors = marshalling.marshall(params, self.fields)
        
        self.data.update(data)
        self.errors = errors
        self.prefix = prefix

    def __call__(self):
        """Calls the first submitted action and returns the value."""

        for action in self.actions:
            if action:
                return action(self, self.data)
        
    def validate(self):
        """Validates the request against the form fields. Returns
        ``True`` if all fields validate, else ``False``."""

        if self.errors:
            return False

        # execute custom form validators
        for validator in type(self).__dict__.values():
            if getattr(validator, '__validator__', False):
                for error in validator(self):
                    path = tuple(error.field.split('.'))
                    self.errors[path] = error.msg

        return not self.errors

class ValidationError(Exception):
    """Represents a field validation error."""

    def __init__(self, field, msg):
        if not isinstance(msg, unicode):
            msg = unicode(msg)
        self.field = field
        self.msg = msg

    def __repr__(self):
        return '<%s field="%s" %s>' % (
            type(self).__name__, self.field, repr(self.msg))

    def __str__(self):
        return str(unicode(self))
    
    def __unicode__(self):
        return self.msg
    
class Data(list):
    """Form data object with dictionary-like interface. If initialized
    with a ``data`` object, this will be used to provide default
    values, if not set in the ``request``. Updates to the object are
    transient until the ``save`` method is invoked."""
    
    def __init__(self, data):
        if data is not None:
            self.append(data)
        self.append({})
        
    def __getitem__(self, name):
        for data in reversed(self):
            try:
                value = data[name]
            except KeyError:
                continue

            if value is not None:
                return value
            
    def __setitem__(self, name, value):
        self.tail[name] = value

    @property
    def tail(self):
        return list.__getitem__(self, -1)

    @property
    def head(self):
        return list.__getitem__(self, 0)
        
    def update(self, data):
        """Updates the dictionary by appending ``data`` to the list at
        the position just before the current dictionary."""

        self.insert(-1, data)
        
    def save(self):
        """Flattens the dictionary, saving changes to the data object."""

        while len(self) > 1:
            for name, value in self.pop(1).items():
                self.head[name] = value
        self.append({})

class Action(object):
    """Callable form action."""
    
    def __init__(self, action, name, submitted):
        self.name = name
        self.submitted = submitted
        self.__call__ = action

    def __nonzero__(self):
        return self.submitted

    def __repr__(self):
        return '<%s name="%s" submitted="%s">' % (
            type(self).__name__, self.name or "", str(bool(self.submitted)))

    def __call__(self, *args):
        return self.__call__(*args)
        
class Proxy(object):
    """Proxy object; reads and writes to attributes are forwarded to
    the provided object. Descriptors are supported: they must read and
    write to ``self.context``. Note, that all attribute names are
    supported, including the name 'context'.

    Any object can be the context of a proxy.

    >>> class Content(object):
    ...     pass
    
    >>> from repoze.formapi import Proxy
    
    >>> class ContentProxy(Proxy):
    ...     def get_test_descriptor(self):
    ...         return self.test_descriptor
    ...
    ...     def set_test_descriptor(self, value):
    ...         self.test_descriptor = value + 1
    ...
    ...     def get_get_only(self):
    ...         return self.test_get_only
    ...
    ...     test_descriptor = property(get_test_descriptor, set_test_descriptor)
    ...     test_get_only = property(get_get_only)
    
    >>> context = Content()
    >>> proxy = ContentProxy(context)

    We can read and write to the ``context`` attribute.
    
    >>> proxy.test = 42
    >>> proxy.test
    42

    Descriptors have access to the original context.
    
    >>> proxy.test_descriptor = 41
    >>> proxy.test_descriptor
    42

    Descriptors that only define a getter are supported.
    
    >>> proxy.test_get_only = 41
    >>> proxy.test_get_only
    41

    Proxies provide dictionary-access to attributes.

    >>> proxy['test']
    42

    >>> proxy['test'] = 41
    >>> proxy.test
    41
    """

    def __init__(self, context):
        # instantiate a base proxy object with this context
        serf = object.__new__(Proxy)
        object.__setattr__(serf, '_context', context)
        object.__setattr__(self, '_context', context)
        object.__setattr__(self, '_serf', serf)

    def __getattribute__(self, name):
        prop = object.__getattribute__(type(self), '__dict__').get(name)
        if prop is not None:
            # call getter in the context of the proxy object
            serf = object.__getattribute__(self, '_serf')
            return prop.fget(serf)
        else:
            return getattr(
                object.__getattribute__(self, '_context'), name)
        
    def __setattr__(self, name, value):
        prop = object.__getattribute__(type(self), '__dict__').get(name)
        if prop is not None:
            # property might be read-only (e.g. does not define a
            # setter); in this case we just set attribute on context.
            setter = prop.fset
            if setter is not None:
                # call setter in the context of the proxy object
                serf = object.__getattribute__(self, '_serf')
                return prop.fset(serf, value)
        setattr(
            object.__getattribute__(self, '_context'), name, value)

    __getitem__ = __getattribute__
    __setitem__ = __setattr__

def validator(*fields):
    def decorator(validator):
        def func(self):
            result = validator(self)
            if result is not None:
                if not isinstance(result, (
                    types.TupleType, types.ListType, types.GeneratorType)):
                    result = (result,)
                for field in fields:
                    for msg in result:
                        yield ValidationError(field, msg)
        func.__validator__ = True
        return func
    return decorator

def action(name):
    if isinstance(name, types.FunctionType):
        def func(self, data):
            return name(self, data)
        func.__action__ = None
        return func
    else:
        def decorator(action):
            def func(self, data):
                return action(self, data)
            func.__action__ = name
            return func
        return decorator
