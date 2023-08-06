from __future__ import absolute_import

import xapian

from . import snowball
from . util import lazy_property
from . fields import Text, PrefixedText, Term, PrefixedTerm, Value


_default_marker = object()


class Attribute(object):

    term_field = None
    prefixed_field = None
    value_field = None

    def __init__(self, type=None, required=True,
                 getter=None, volatile=False,
                 prefixed=False, unprefixed=True,
                 value=False, text=False,
                 value_parent=None, sequence=False,
                 mapping=False, sortable=None,
                 translit=None, default=_default_marker):
        self.name = None # set by the schema construction
        self.type = type
        self.required = required
        self.default = default
        self.getter = getter
        self.volatile = volatile
        self.children = []
        self.value_parent = value_parent
        self.sequence = sequence
        self.mapping = mapping
        self.sortable = sortable
        if text:
            if unprefixed:
                self.term_field = Text(self, translit=translit)
            if prefixed:
                self.prefixed_field = PrefixedText(self, prefix=self.name,
                                                   translit=translit)
        else:
            if unprefixed:
                self.term_field = Term(self)
            if prefixed:
                self.prefixed_field = PrefixedTerm(self, prefix=self.name)
        if value or sortable:
            self.value_field = Value(self, parent=value_parent,
                                     sortable=sortable,
                                     prefix=self.name)

    def __call__(self, schema, name, value=None):
        obj = schema.__object__
        state = schema.__state__

        if self.volatile:
            if name in state:
                del state[name]
            return

        if self.getter is not None:
            value = self.getter(name, schema)

        elif name in state:
            value = state[name]

        elif self.default is not _default_marker:
            value = self.default

        elif self.required:
            msg = "Attribute %s is required for %s by %s" % (name,
                                                             repr(obj),
                                                             self.__class__)
            raise TypeError(msg)

        if self.type is not None:
            if not isinstance(value, self.type):
                msg = "Attribute %s must be of type %s" % (name,
                                                           self.type)
                raise TypeError(msg)

        state[name] = value

        for field in [self.term_field, self.prefixed_field, self.value_field]:
            if field:
                field(schema, field.attr.name, obj, state)


class Schema(object):
    """
    Types that define indexing behavior for objects.  Instances of
    these types are used at index-time to add terms, values, and data
    to Xapian documents.
    """
    __slots__ = ['__database__',
                 '__document__',
                 '__object__',
                 '__state__',
                 '__term_generator__',
                 '__language__',
                 ]

    class __metaclass__(type):
        def __new__(cls, cls_name, bases, attrs):
            schema = type.__new__(cls, cls_name, bases, attrs)
            schema.__attributes__ = {}
            for base in reversed(schema.__mro__):
                if base is not schema:
                    if hasattr(base, '__attributes__'):
                        schema.__attributes__.update(base.__attributes__)
            for name, value in attrs.iteritems():
                if not name.startswith("_"):
                    value.name = name
                    schema.__attributes__[name] = value
            return schema

    def __init__(self, database):
        self.__database__ = database
        self.__language__ = None

    def __call__(self, obj):
        if hasattr(self, '__before__'):
            self.__before__(obj)
        state = newargs = None
        if hasattr(obj, '__getstate__'):
            state = obj.__getstate__()
        else:
            state = obj.__dict__.copy()

        for key in state.keys():
            if key not in self.__attributes__:
                state.pop(key)

        if hasattr(obj, '__getnewargs__'):
            newargs = obj.__getnewargs__()
        else:
            newargs = ()

        self.__object__ = obj
        self.__state__ = state
        typ = type(obj)

        if self.__attributes__:
            self.__document__ = doc = xapian.Document()
            self.__term_generator__ = tg = xapian.TermGenerator()
            tg.set_database(self.__database__.backend)
            tg.set_document(doc)
            if self.__database__.spelling:
                tg.set_flags(xapian.TermGenerator.FLAG_SPELLING)
            language = self.__language__
            if language in snowball.stoppers:
                tg.set_stemmer(xapian.Stem(language))
                tg.set_stopper(snowball.stoppers[language])

            for name, attr in self.__attributes__.iteritems():
                attr(self, name)

        data = self.__database__.serialize(typ, newargs, state)
        doc.set_data(data)
        if hasattr(self, '__after__'):
            self.__after__(obj, state, doc)
        return doc
