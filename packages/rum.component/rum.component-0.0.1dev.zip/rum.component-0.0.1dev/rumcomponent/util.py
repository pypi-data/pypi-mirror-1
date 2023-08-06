from pkg_resources import EntryPoint

class NoDefaultType(type):
    def __repr__(cls):
        """
        This is just so the docs come out more pretty :)

        >>> repr(NoDefault)
        'NoDefault'
        """
        return cls.__name__

class NoDefault(object):
    __metaclass__ = NoDefaultType

def import_string(s):
    """
    Imports the object referenced by ``s`` using ``EntryPoint`` notation.

    Example::

        >>> o = import_string('rumcomponent.util:import_string')
        >>> o.func_name
        'import_string'

    If it is not a string it is returned as-is

        >>> o == import_string(o)
        True
    """
    if not isinstance(s, basestring):
        # Assume we don't need to import anyting
        return s
    return EntryPoint.parse('x='+s).load(False)
