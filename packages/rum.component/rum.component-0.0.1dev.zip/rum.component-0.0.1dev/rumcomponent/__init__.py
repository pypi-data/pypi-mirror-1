from pkg_resources import iter_entry_points
import rumcomponent.util as util
from rumcomponent.exceptions import NoComponentFound, NoComponentRegistered

__all__ = ['Component']


class Component(object):
    """
    An attribute of a class that can is resolved at runtime based on some kind
    of configuration.

    **Parameters:**

    ``key``
       The key that uniquevocally identifies this :class:`Component`

    ``doc``
       Optional docstring for the :class:`Component`

    ``default``
        Optional callable that provides a default value for this attribute
        if the key cannot be found in the config.
    
    ``cache``
        If True then the initialized attribute will be cached in the instance

    Subclasses will probably want to override the :attr:`config` property
    to control where the config dict is loaded from. The :class:`Component` will
    load from the contextual :attr:`rum.app.config` by default.

    Example::

        >>> class SomeClass(object):
        ...     bar = Component('some.key', 'This is a bar')

        >>> SomeClass.bar # doctest: +ELLIPSIS
        <rumcomponent.Component object at ...>
    """
  
    def __init__(self, key, doc=None, default=util.NoDefault, cache=True):
        self.key = key
        self.__doc__ = "Component(%r)" % self.key
        if doc is not None:
            self.__doc__ += ': ' + doc
        self.default = default
        self.do_cache = cache

    def config(self):
        raise NotImplementedError, "You have to adapt the component architecture to your own configuration scheme, return a dictionary here"

    config = property(
        fget=config,
        doc="The configuration mapping where implementators and their arguments"
            " are declared"
        )

    def initialize_component(self, config):
        try:
            config = config[self.key]
        except KeyError:
            config = {}
        if 'use' not in config:
            if self.default is util.NoDefault:
                raise NoComponentRegistered(self.key)
            if isinstance(self.default, basestring):
                # Assume a ep name or object path
                use = self.default
            else:
                use = self.default()
            config['use'] = use
        component = self.load_component(config['use'])
        if component is not None:
            args = config.copy()
            args.pop('use')
            return component(**args)

    def load_component(self, key):
        if isinstance(key, basestring):
            if ':' in key:
                try:
                    return util.import_string(key)
                except ImportError, e:
                    raise NoComponentFound(`(self.key, key, e)`)
            else:
                for ep in iter_entry_points(self.key):
                    if ep.name == key:
                        return ep.load()
            raise NoComponentFound(`(self.key, key)`)
        # Assume key is a component class
        return key

    def _get_attributes(self, obj):
        return obj.__dict__.setdefault('__injected_attributes__', {})

    #
    # The descriptor interface
    #
    def __get__(self, obj, typ=None):
        if obj is None:
            return self
        attributes = self._get_attributes(obj)
        if self.key not in attributes:
            # try to get config from the object we're atteched to
            try:
                config = obj.config
            except AttributeError:
                config = self.config
            attr = self.initialize_component(config)
            if self.do_cache:
                self.__set__(obj, attr)
        else:
            attr = attributes[self.key]
        return attr

    def __set__(self, obj, attr):
        self._get_attributes(obj)[self.key] = attr

    def __delete__(self, obj):
        del self._get_attributes(obj)[self.key]
