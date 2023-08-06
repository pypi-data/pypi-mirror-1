import xapian
import unicodedata
import translitcodec
from cPickle import dumps, loads

from . import snowball

MAX_TERM_LEN = 240 # compile time xapian limit


def _prefix(name):
    return (u'X'+ name.upper()).encode('utf-8')


_novalue = object()


class Field(object):
    __slots__ = ['attr', 'prefix']

    def __init__(self, attr, prefix=None):
        self.attr = attr
        self.prefix = prefix

    def check_prefix(self, schema, prefix, boolean=False):
        """
        Check the database in the current session for the given
        prefix.  If it doesn't exist, add it.
        """
        database = schema.__database__
        prefixes = database.relevance_prefixes.copy()
        prefixes.update(database.boolean_prefixes.copy())
        if prefix not in prefixes:
            upped = _prefix(prefix)
            if boolean:
                database.add_boolean_prefix(prefix, upped)
            else:
                database.add_prefix(prefix, upped)

    def __call__(self, schema, name, obj, state):
        self.check_prefix(schema, (self.prefix or self.attr.name))
        self.index(schema, name, obj, state)

    def normalize(self, value):
        value = unicodedata.normalize('NFKC', unicode(value).strip().lower()).encode('utf-8')
        if len(value) > MAX_TERM_LEN:
            return ''
        return value

    def add_term(self, schema, value, prefix=None):
        value = self.normalize(value)
        if value:
            if prefix is None:
                schema.__document__.add_term(value)
            else:
                term = _prefix(prefix) + value.lower()
                schema.__document__.add_term(term)

    def index(self, schema, name, obj, state):
        raise NotImplementedError


class Term(Field):
    """Field that adds a single term into a schema document. """

    def index(self, schema, name, obj, state):
        value = state.get(self.attr.name)
        if value:
            prefix = self.prefix or self.attr.name
            if self.attr.sequence:
                for val in value:
                    self.add_term(schema, val)
            elif self.attr.mapping:
                for key, val in value.items():
                    if not val:
                        continue
                    pre = prefix + "_" + key
                    self.check_prefix(schema, pre)
                    self.add_term(schema, val, prefix=pre)
            else:
                self.add_term(schema, value)


class PrefixedTerm(Field):
    """Field that adds a single prefixed term into a schema document."""

    def index(self, schema, name, obj, state):
        value = state.get(self.attr.name)
        if value:
            prefix = self.prefix or self.attr.name
            if self.attr.sequence:
                for val in value:
                    self.add_term(schema, val, prefix=prefix)
            elif self.attr.mapping:
                for key, val in value.items():
                    if not val:
                        continue
                    pre = prefix + "_" + key
                    self.check_prefix(schema, pre)
                    self.add_term(schema, val, prefix=pre)
            else:
                self.add_term(schema, value, prefix=prefix)


class Text(Field):
    """A field that indexes text into a schema document."""

    __slots__ = ['translit']

    def __init__(self, attr, translit=None):
        Field.__init__(self, attr)
        self.translit = translit

    def index(self, schema, name, obj, state):
        value = state.get(self.attr.name)
        if value:
            tg = schema.__term_generator__
            language = schema.__language__
            if language in snowball.stoppers:
                tg.set_stemmer(xapian.Stem(language))
                tg.set_stopper(snowball.stoppers[language])
            prefix = self.prefix or self.attr.name
            if self.attr.sequence:
                for val in value:
                    if not val:
                        continue
                    if self.translit:
                        val = val.encode(self.translit)
                    tg.index_text(val.encode('utf-8'))
            elif self.attr.mapping:
                for key, val in value.items():
                    if not val:
                        continue
                    if self.translit:
                        val = val.encode(self.translit)
                    pre = prefix + "_" + key
                    self.check_prefix(schema, pre)
                    tg.index_text(val.encode('utf-8'), 1, _prefix(pre))
            else:
                if self.translit:
                    value = value.encode(self.translit)
                tg.index_text(value.encode('utf-8'))


class PrefixedText(Field):
    """A field that indexes prefixed text into a schema document."""

    __slots__ = ['translit']

    def __init__(self, attr, prefix=None, translit=None):
        Field.__init__(self, attr, prefix)
        self.translit = translit

    def index(self, schema, name, obj, state):
        value = state.get(self.attr.name)
        if value:
            prefix = self.prefix or self.attr.name
            tg = schema.__term_generator__
            language = schema.__language__
            if language in snowball.stoppers:
                tg.set_stemmer(xapian.Stem(language))
                tg.set_stopper(snowball.stoppers[language])
            if self.attr.sequence:
                for val in value:
                    if not val:
                        continue
                    if self.translit:
                        val = val.encode(self.translit)
                    tg.index_text(val.encode('utf-8'), 1, _prefix(prefix))
            elif self.attr.mapping:
                for key, val in value.items():
                    if not val:
                        continue
                    if self.translit:
                        val = val.encode(self.translit)
                    pre = prefix + "_" + key
                    self.check_prefix(schema, pre)
                    tg.index_text(val.encode('utf-8'), 1, _prefix(pre))
            else:
                if self.translit:
                    value = value.encode(self.translit)
                tg.index_text(value.encode('utf-8'), 1, _prefix(prefix))


class Value(Field):
    """A document value used for matching and sorting."""

    __slots__ = ['attr', 'filter', 'valno', 'parent', 'sortable']

    def __init__(self, attr, parent=None, filter=None, sortable=None, prefix=None):
        Field.__init__(self, attr, prefix)
        self.attr = attr
        self.filter = filter
        self.parent = parent

        if sortable not in (None, 'numeric', 'date', 'datetime', 'string'):
            raise TypeError("Unkown sortable type: %s" % sortable)
        self.sortable = sortable
        if parent:
            # sw: attr.name is net yet known here
            parent.children.append(attr)

    def __call__(self, schema, name, obj, state):
        self.check_value(schema)
        if self.filter:
            self.attr.value = self.filter(self.attr.value)
        self.index(schema, name, obj, state)

    def check_value(self, schema):
        """Check the database in the current session for the given
        value name.  If it doesn't exist, add it."""
        database = schema.__database__
        if self.attr.name in database.values:
            self.valno = database.values[self.attr.name]
        else:
            self.valno = database.add_value(self.attr.name, self.sortable)

    def index(self, schema, name, obj, state):
        value = state.get(self.attr.name)
        prefix = self.prefix or self.attr.name
        if value:
            if self.sortable:
                if self.sortable == 'numeric':
                    value = xapian.sortable_serialise(float(value))
                if self.sortable == 'date':
                    value = value.strftime("%Y%m%d")
                    pre = prefix+'_date'
                    self.check_prefix(schema, prefix=pre)
                    self.add_term(schema, value, prefix=pre)
                if self.sortable == 'datetime':
                    value = value.strftime("%Y%m%d%H%M%S")
                    pre = prefix+'_datetime'
                    self.check_prefix(schema, prefix=pre)
                    self.add_term(schema, value, prefix=pre)
                if self.sortable == 'string':
                    value = str(value)
            else:
                value = dumps(value)
            schema.__document__.add_value(self.valno, value)

