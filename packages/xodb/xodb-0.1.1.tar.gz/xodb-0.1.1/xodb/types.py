import xapian
import unicodedata

from .exc import (
    AttributeRequired,
    AttributeTypeRequired,
    InvalidTermError,
    )


MAX_TERM_LEN = 240 # compile time xapian limit


def _prefix(name):
    return (u'X' + name.upper()).encode('utf-8')


_default_marker = object()


class BaseType(object):
    """
    A schema type.

    :param sort: If true, this attribute is sortable and will create a
    xapian value.

    :param facet: If true, this attribute is faceted and will generate
    facet terms.

    :param facet_parent: If facet is true, this attributes facet
    parent.  Used to organize facet heirarchies (ie country-> state->
    city etc.)

    :param prefixed: If true, this attribute's value should be prefixed.

    :param getter: A getter function for the value.  If None, the
    value is taken from the object's state.

    :param required: If true, the object is required to provide this
    attribute.

    :param default: The default value for the attribute if one is not
    provided.  Meaningless if required is True.

    :param required_type: If not None, the value of the attribute must
    be an instance of this type.
    """

    def __init__(self, getter=None, sortable=False,
                 facet=False, facet_parent=None, prefixed=True,
                 required=False, translit=None,
                 default=_default_marker, required_type=None):
        self.sortable = sortable
        self.prefixed = prefixed
        self.facet = facet
        self.facet_parent = facet_parent
        self.default = default
        self.getter = getter
        self.required = required
        self.translit = translit
        self.required_type = required_type
        self.valno = None

    @classmethod
    def getter(type_class, *args, **kwargs):
        """
        Decorator for wrapping a schema getter method with a given
        schema type.
        """
        def _decorator(f):
            kwargs['getter'] = f
            t = type_class(*args, **kwargs)
            return t
        return _decorator

    def normalize(self, value, limit=MAX_TERM_LEN):
        value = unicodedata.normalize(
            'NFKC', unicode(value).strip().lower()).encode('utf-8')
        if limit and len(value) > limit:
            raise InvalidTermError('The term %s is too long.' % value)
        return value

    def check_prefix(self, schema, name, boolean=False):
        database = schema.__database__
        prefixes = database.relevance_prefixes.copy()
        prefixes.update(database.boolean_prefixes.copy())
        if name not in prefixes:
            upped = _prefix(name)
            if boolean:
                database.add_boolean_prefix(name, upped)
            else:
                database.add_prefix(name, upped)

    def add_term(self, schema, value, prefix=None, boolean=False):
        value = self.normalize(value)
        if prefix:
            self.check_prefix(schema, prefix, boolean)
            term = _prefix(prefix) + value.lower()
        else:
            term = value.lower()
        schema.__document__.add_term(term)

    def add_value(self, schema, name, value):
        database = schema.__database__
        if name in database.values:
            valno = database.values[name]
        else:
            valno = database.add_value(name, self.__class__.__name__.lower())
        self.valno = valno
        schema.__document__.add_value(valno, value)

    def __call__(self, schema, name, value=None):
        state = schema.__state__
        obj = schema.__object__
        if value is None:
            if self.getter is not None:
                value = self.getter(schema, name)

            elif name in state:
                value = state[name]

            elif self.default is not _default_marker:
                value = self.default

            elif self.required:
                msg = "Attribute %s is required for %s by %s" % (name,
                                                                 repr(obj),
                                                                 self.__class__)
                raise AttributeRequired, msg
            if self.required_type is not None:
                if not isinstance(value, self.required_type):
                    msg = "Attribute %s must be of type %s" % (name,
                                                               self.required_type)
                    raise AttributeTypeRequired, msg
            if self.translit:
                value = value.encode(self.translit)
            if self.facet:
                self.add_term(schema, name, 'facet')
            state[name] = value
        return value


class String(BaseType):
    """A schema type that indexes a string attribute.
    """
    def __call__(self, schema, name, value=None):
        value = BaseType.__call__(self, schema, name, value)
        if value:
            if self.prefixed:
                self.add_term(schema, value, name)
            else:
                self.add_term(schema, value)
            if self.sortable:
                self.add_value(schema, name, value)
        return value


class Numeric(BaseType):
    """A schema type that indexes a numeric attribute.
    """
    def __call__(self, schema, name, value=None):
        value = BaseType.__call__(self, schema, name, value)
        if value:
            if self.prefixed:
                self.add_term(schema, value, name)
            else:
                self.add_term(schema, value)
            if self.sortable:
                self.add_value(schema, name, xapian.sortable_serialise(value))
        return value


class Text(BaseType):
    """A schema type that indexes a textual attribute.
    """
    def __init__(self, getter=None, positions=True,
                 *args, **kwargs):
        BaseType.__init__(self, getter, *args, **kwargs)
        self.positions = positions

    def __call__(self, schema, name, value=None):
        value = BaseType.__call__(self, schema, name, value)
        if value:
            tg = schema.__term_generator__
            if self.positions:
                index_text = tg.index_text
            else:
                index_text = tg.index_text_without_positions
            if self.prefixed:
                self.check_prefix(schema, name)
                index_text(value.encode('utf-8'), 1, _prefix(name))
            else:
                index_text(value.encode('utf-8'))
        return value


class Sequence(BaseType):
    def __init__(self, itemizer=None, *args, **kwargs):
        BaseType.__init__(self, *args, **kwargs)
        self.itemizer = itemizer
    
    def __call__(self, schema, name, value=None):
        value = BaseType.__call__(self, schema, name, value)
        if value:
            for val in value:
                if self.itemizer is not None:
                    self.itemizer(schema, name, val)
                else:
                    if self.prefixed:
                        self.add_term(schema, val, name)
                    else:
                        self.add_term(schema, val)
        return value


class Mapping(BaseType):
    def __init__(self, itemizer=None, *args, **kwargs):
        BaseType.__init__(self, *args, **kwargs)
        self.itemizer = itemizer

    def __call__(self, schema, name, value=None):
        value = BaseType.__call__(self, schema, name, value)
        if value:
            for k, v in value.iteritems():
                if self.itemizer is not None:
                    self.itemizer(schema, (name + '_' + k), v)
                else:
                    if self.prefixed:
                        n = '%s_%s' % (name, k)
                    else:
                        n = k
                    self.add_term(schema, v, n)
                    if self.facet:
                        self.add_term(schema, n, 'facet')
        return value


class BaseDateType(BaseType):
    """A schema type that indexes a mapping attribute.
    """
    def __call__(self, schema, name, value=None):
        value = BaseType.__call__(self, schema, name, value)
        if value:
            term_value = value.strftime(self.term_format)
            if self.prefixed:
                self.add_term(schema, term_value, name)
            else:
                self.add_term(schema, term_value)
            if self.sortable:
                value_value = value.strftime(self.value_format)
                self.add_value(schema, name, value_value)
        return value


class Date(BaseDateType):
    """A schema type that indexes a date attribute.
    """
    term_format = '%Y%m%d'
    value_format = '%Y%m%d'


class Datetime(BaseDateType):
    """A schema type that indexes a datetime attribute.
    """
    term_format = '%Y%m%d'
    value_format = '%Y%m%d%H%M%S'
