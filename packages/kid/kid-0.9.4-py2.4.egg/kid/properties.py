"""Configuration API."""

import release
__revision__ = "$Rev: 421 $"
__date__ = "$Date: 2006-10-22 07:02:46 -0400 (Sun, 22 Oct 2006) $"
__author__ = "David Stanek <dstanek@dstanek.com>"
__copyright__ = "Copyright 2006, David Stanek"
__license__ = release.license

_properties = {
}

def get(name, default=None):
    """Get the property identified by name if it exists or return default.

    name: the name of the property to retrieve
    default: the value returned for non-existing properties, defaults to None

    """
    return _properties.get(name, default)

def set(name, value):
    """The the property identified by name with the value identified by value.

    Returns the value passed in.
    """
    _properties[name] = value
    return value

def isset(name):
    """Returns True if a property exists or False if it doesn't."""
    return _properties.has_key(name)

def remove(name):
    """Remove a property."""
    if name in _properties:
        del _properties[name]
