from __future__ import absolute_import, unicode_literals

import six
from collections import OrderedDict


def _is_descriptor(obj):
    """Returns True if obj is a descriptor, False otherwise."""
    return (
        hasattr(obj, '__get__') or
        hasattr(obj, '__set__') or
        hasattr(obj, '__delete__'))


def _is_dunder(name):
    """Returns True if a __dunder__ name, False otherwise."""
    return (name[:2] == name[-2:] == '__' and
            name[2:3] != '_' and
            name[-3:-2] != '_' and
            len(name) > 4)


def _is_sunder(name):
    """Returns True if a _sunder_ name, False otherwise."""
    return (name[0] == name[-1] == '_' and
            name[1:2] != '_' and
            name[-2:-1] != '_' and
            len(name) > 2)


class _EnumDict(dict):
    """Track enum member order and ensure member names are not reused.

    EnumMeta will use the names found in self._member_names as the
    enumeration member names.

    """
    @classmethod
    def hack4py2(cls, classdict, allow_types):
        """hacking for python2 to generate an instance from the original classdict
        """
        assert isinstance(classdict, dict)
        res = cls(allow_types=allow_types)
        for key, value in six.iteritems(classdict):
            res[key] = value
        return res

    def _check_value_type(self, v):
        """The value type must be six.integer_types or six.string_types

        In fact, enumeration does not concern about values,
        but just the names of enumeration.

        Value type are restricted for the convenience to be json serializable.

        """
        def _check_basetype(v):
            if not isinstance(v, self._allow_types):
                raise TypeError('Value type must be one of [%s], '
                                'instead of %s' % (', '.join(map(str, self._allow_types)), type(v)))

        if type(v) is tuple:
            if len(v) != 2:
                raise TypeError('Tuple enum definition must be length of 2')
            _check_basetype(v[0])
            if not isinstance(v[1], six.string_types):
                raise TypeError('The second element of tuple enum definition '
                                'must be string, i.e. an explanation of the enum value')
        else:
            _check_basetype(v)

    def __init__(self, allow_types):
        super(_EnumDict, self).__init__()
        self._member_names = []
        self._allow_types = allow_types

    def __setitem__(self, key, value):
        """Changes anything not dundered

        If an enum member name is used twice, an error is raised; duplicate
        values are not checked for.

        Single underscore (sunder) names are reserved.

        """
        if _is_sunder(key):
            raise ValueError('_names_ are reserved for future Enum use')
        elif _is_dunder(key):
            pass
        elif key in self._member_names:
            # descriptor overwriting an enum?
            raise TypeError('Attempted to reuse key: %r' % key)
        elif not _is_descriptor(value):
            if key in self:
                # enum overwriting a descriptor?
                raise TypeError('Key already defined as: %r' % self[key])
            # value must be BASE_TYPE, or tuple of (BASE_TYPE, six.string_types)
            # BASE_TYPE is six.string_types or integer
            self._check_value_type(value)
            self._member_names.append(key)
        super(_EnumDict, self).__setitem__(key, value)


# Dummy value for Enum as EnumMeta explicitly checks for it, but of course
# until EnumMeta finishes running the first time the Enum class doesn't exist.
Enum = None


class EnumMeta(type):
    """Metaclass for Enum"""
    @staticmethod
    def _find_allow_types_(cls, bases):
        all_types = set(six.integer_types) | {six.text_type, str}
        allow_types = set()
        if Enum is None:    # Enum base class
            assert cls == 'Enum'
            return tuple(all_types)
        else:
            for base in bases:
                if not issubclass(base, Enum):
                    allow_types.add(base)
        if allow_types:
            return tuple(all_types & allow_types)
        else:
            return tuple(all_types)

    @classmethod
    def __prepare__(mcs, cls, bases):
        return _EnumDict(EnumMeta._find_allow_types_(cls, bases))

    def __new__(mcs, cls, bases, _dct):
        # hacking to generate an _EnumDict Object
        if six.PY2:
            dct = _EnumDict.hack4py2(_dct, EnumMeta._find_allow_types_(cls, bases))
        else:
            dct = _dct

        # save enum items into separate mapping so they don't get baked into
        # the new class
        members = {k: dct[k] for k in dct._member_names}
        for name in dct._member_names:
            del dct[name]

        # check for illegal enum names (any others?)
        invalid_names = set(members) & {'mro', }
        if invalid_names:
            raise ValueError('Invalid enum member name: {0}'.format(
                ','.join(invalid_names)))

        # create our new Enum type
        enum_class = super(EnumMeta, mcs).__new__(mcs, cls, bases, dct)
        enum_class._member_names_ = []               # names in definition order
        enum_class._member_map_ = OrderedDict()      # name->value map

        # Reverse value->name map for hashable values.
        enum_class._value2member_map_ = {}
        enum_class.choices = []

        # instantiate them, checking for duplicates as we go
        # we instantiate first instead of checking for duplicates first in case
        # a custom __new__ is doing something funky with the values -- such as
        # auto-numbering ;)
        for member_name, value in six.iteritems(members):
            if isinstance(value, tuple):
                real_value = value[0]
                desc = value[1]
            else:
                real_value = value
                desc = ''
            enum_member = enum_class()
            enum_member._name_ = member_name
            enum_member._value_ = real_value
            enum_member._desc_ = desc
            # If another member with the same value was already defined, the
            # new member becomes an alias to the existing one.
            for name, canonical_member in six.iteritems(enum_class._member_map_):
                if canonical_member._value_ == enum_member._value_:
                    enum_member = canonical_member
                    break
            else:
                # Aliases don't appear in member names (only in __members__).
                enum_class._member_names_.append(member_name)
            # now add to _member_map_
            enum_class._member_map_[member_name] = enum_member
            enum_class._value2member_map_[real_value] = enum_member
            enum_class.choices.append([real_value, desc])

        return enum_class

    def __contains__(cls, value):
        return value in cls._value2member_map_

    def __delattr__(cls, attr):
        # nicer error message when someone tries to delete an attribute
        # (see issue19025).
        if attr in cls._member_map_:
            raise AttributeError(
                "%s: cannot delete Enum member." % cls.__name__)
        super(EnumMeta, cls).__delattr__(attr)

    def __getattr__(cls, name):
        """Return the enum member matching `name`

        We use __getattr__ instead of descriptors or inserting into the enum
        class' __dict__ in order to support `name` and `value` being both
        properties for enum members (which live in the class' __dict__) and
        enum members themselves.

        """
        # check if classmethod(bound now)
        if _is_dunder(name):
            raise AttributeError(name)
        try:
            enum_member = cls._member_map_[name]
            return enum_member._value_
        except KeyError:
            six.raise_from(AttributeError(name), None)

    def __desc__(cls, value):
        return cls._value2member_map_[value]._desc_

    @property
    def __members__(cls):
        """Returns a mapping of member name->value.

        This mapping lists all enum members, including aliases. Note that this
        is a read-only view of the internal mapping.

        """
        return cls._member_map_.copy()

    def __getitem__(cls, name):
        return cls._member_map_[name]

    def __iter__(cls):
        """Returns a tuple of tuples(member.value, member.desc) for each member
        """
        return ((
                    cls._member_map_[name]._value_,
                    cls._member_map_[name]._desc_) for name in cls._member_names_)

    def __len__(cls):
        return len(cls._member_names_)

    def __repr__(cls):
        return "<enum %r>" % cls.__name__

    def __reversed__(cls):
        return (cls._member_map_[name] for name in reversed(cls._member_names_))

    def __setattr__(cls, name, value):
        """Block attempts to reassign Enum members.

        A simple assignment to the class namespace only changes one of the
        several possible ways to get an Enum member from the Enum class,
        resulting in an inconsistent Enumeration.

        """
        member_map = cls.__dict__.get('_member_map_', {})
        if name in member_map:
            raise AttributeError('Cannot reassign members.')
        super(EnumMeta, cls).__setattr__(name, value)

    def __dir__(self):
        return list(super(EnumMeta, self).__dir__()) + self._member_names_


class Enum(six.with_metaclass(EnumMeta, object)):
    """Generic enumeration.

    Derive from this class to define new enumerations.

    """

    def __repr__(self):
        return "<%s.%s: %r>" % (
            self.__class__.__name__, self._name_, self._value_)

    def __str__(self):
        if self._desc_:
            return "%s.%s(%s)" % (self.__class__.__name__, self._name_, self._desc_)
        else:
            return "%s.%s" % (self.__class__.__name__, self._name_)

    def __hash__(self):
        return hash(self._name_)

    @classmethod
    def getDesc(cls, key, defaultValue=None):
        """Backport function for gaia.rpc.tool.enumeration.Enumeration
        """
        try:
            return cls.__desc__(key)
        except KeyError:
            return defaultValue


def unique(enumeration):
    """Class decorator for enumerations ensuring unique member values."""
    duplicates = []
    for name, member in six.iteritems(enumeration.__members__):
        if name != member._name_:
            duplicates.append((name, member._name_))
    if duplicates:
        alias_details = ', '.join(
            ["%s -> %s" % (alias, name) for (alias, name) in duplicates])
        raise ValueError('duplicate values found in %r: %s' %
                         (enumeration, alias_details))
    return enumeration
