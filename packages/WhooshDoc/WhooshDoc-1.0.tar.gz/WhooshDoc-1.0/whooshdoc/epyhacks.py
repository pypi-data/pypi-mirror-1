""" Hacks for to help epydoc read certain packages.
"""

from epydoc import docintrospecter


def type_name_predicate(type_module, type_name):
    """ Return a predicate function that returns True if an object is a strict
    instance of a type given by its module and name.

    Instances of subclasses are not considered.
    """
    def f(obj):
        typ = type(obj)
        return (getattr(typ, '__module__', None) == type_module and 
            getattr(typ, '__name__', None) == type_name)
    return f

def register_hacks():
    """ Register hacks for special cases.
    """
    docintrospecter.register_introspecter(
        type_name_predicate('numpy', 'ufunc'),
        docintrospecter.introspect_routine)
    docintrospecter.register_introspecter(
        type_name_predicate('__builtin__', 'fortran'),
        docintrospecter.introspect_routine)
