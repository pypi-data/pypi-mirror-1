# -*- coding: utf-8 -*-

from zope.interface import Interface, classImplements, Attribute

    
class IString(Interface):
    """Marker interface for mutable strings.
    """
classImplements(str, IString)


class IUnicode(Interface):
    """Marker interface for mutable unicode strings.
    """
classImplements(unicode, IUnicode)


class INumeric(Interface):
    """Marker interface for a numeric value.
    """
classImplements(int, INumeric)
classImplements(long, INumeric)
classImplements(float, INumeric)


class IBoolean(Interface):
    """Marker interface for a boolean.
    """
classImplements(bool, IBoolean)


class IIterable(Interface):
    """Base interface for iterable types.
    """
    def __iter__():
        """Return an iterator object.
        """


class IList(IIterable):
    """Marker interface for lists
    """
classImplements(list, IList)


class ITuple(IIterable):
    """Marker interface for immutable lists
    """
classImplements(tuple, ITuple)


class IDict(IIterable):
    """Marker interface for dicts
    """
    def items():
        """Returns an iterable list of couples key - value,
        as a list of tuples.
        """
    
    def values():
        """Returns an iterable list of the dict values.
        """

    def keys():
        """Returns an iterable list of the dict keys.
        """

    def has_key(key):
        """Returns a boolean, True if the key exists in the dict,
        False otherwise.
        """
classImplements(dict, IDict)

    
__all__ = ("IString", "IUnicode", "IBoolean", "INumeric",
           "IIterable", "IList", "ITuple", "IDict")
