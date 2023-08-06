# Copyright (C) 2004-2010 Barry A. Warsaw
#
# This file is part of munepy.
#
# munepy is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# munepy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with munepy.  If not, see <http://www.gnu.org/licenses/>.

"""Python enumerations.

See docs/pep-xxxx.txt for detailed documentation.
"""

__all__ = [
    'Enum',
    ]


COMMASPACE = ', '



class EnumMetaclass(type):
    def __init__(cls, name, bases, dict):
        # cls == the class being defined
        # name == the name of the class
        # bases == the class's bases
        # dict == the class attributes
        super(EnumMetaclass, cls).__init__(name, bases, dict)
        # Store EnumValues here for easy access.
        cls._enums = {}
        # Figure out the set of enum values on the base classes, to ensure
        # that we don't get any duplicate values (which would screw up
        # conversion from integer).
        for basecls in cls.__mro__:
            if hasattr(basecls, '_enums'):
                cls._enums.update(basecls._enums)
        # For each class attribute, create an EnumValue and store that back on
        # the class instead of the int.  Skip Python reserved names.  Also add
        # a mapping from the integer to the instance so we can return the same
        # object on conversion.
        for attr in dict:
            if not (attr.startswith('__') and attr.endswith('__')):
                intval  = dict[attr]
                enumval = EnumValue(cls, intval, attr)
                if intval in cls._enums:
                    raise TypeError('Multiple enum values: %s' % intval)
                # Store as an attribute on the class, and save the attr name
                setattr(cls, attr, enumval)
                cls._enums[intval] = attr

    def __getattr__(cls, name):
        if name == '__members__':
            return cls._enums.values()
        raise AttributeError(name)

    def __repr__(cls):
        enums = ['%s: %d' % (cls._enums[k], k) for k in sorted(cls._enums)]
        return '<%s {%s}>' % (cls.__name__, COMMASPACE.join(enums))

    def __iter__(cls):
        for i in sorted(cls._enums):
            yield getattr(cls, cls._enums[i])

    def __getitem__(cls, i):
        # i can be an integer or a string
        attr = cls._enums.get(i)
        if attr is None:
            # It wasn't an integer -- try attribute name
            try:
                return getattr(cls, i)
            except (AttributeError, TypeError):
                raise ValueError(i)
        return getattr(cls, attr)

    # Support both MyEnum[i] and MyEnum(i)
    __call__ = __getitem__



class EnumValue(object):
    """Class to represent an enumeration value.

    EnumValue('Color', 'red', 12) prints as 'Color.red' and can be converted
    to the integer 12.
    """
    def __init__(self, cls, value, enumname):
        self._class     = cls
        self._value     = value
        self._enumname  = enumname

    def __repr__(self):
        return '<EnumValue: %s.%s [int=%d]>' % (
            self._class.__name__, self._enumname, self._value)

    def __str__(self):
        return '%s.%s' % (self._class.__name__, self._enumname)

    def __int__(self):
        return self._value

    @property
    def enumclass(self):
        return self._class

    @property
    def enumname(self):
        return self._enumname

    # Support only comparison by identity and equality.  Ordered comparisions
    # are not supported.
    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    def __lt__(self, other):
        raise NotImplementedError

    __gt__ = __lt__
    __le__ = __lt__
    __ge__ = __lt__
    __hash__ = object.__hash__



class Enum:
    __metaclass__ = EnumMetaclass
