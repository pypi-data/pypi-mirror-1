from __future__ import absolute_import

import xapian
import string

from cStringIO import StringIO
from cPickle import Pickler, Unpickler
from xapian import QueryParser, Query, UnimplementedError, DocNotFoundError

from . import snowball
from .spies import TermCountMatchSpy


RETRY_LIMIT = 3

try:
    # try bz2, fallback to zlib
    from bz2 import compress, decompress

    def _decompress(data):
        if data.startswith('BZ'):
            try:
                data = decompress(data)
            except IOError:
                pass
        return data

except ImportError:
    from zlib import compress, decompress, error as compress_error

    def _decompress(data):
        if data.startswith('x'):
            try:
                data = decompress(data)
            except compress_error:
                pass
        return data


from . schema import Schema


default_parser_flags = (QueryParser.FLAG_PHRASE |
                        QueryParser.FLAG_BOOLEAN |
                        QueryParser.FLAG_LOVEHATE |
                        QueryParser.FLAG_SPELLING_CORRECTION |
                        QueryParser.FLAG_BOOLEAN_ANY_CASE |
                        QueryParser.FLAG_WILDCARD)


class LangDecider(xapian.ExpandDecider):
    """
    A Xapian ExpandDecider that decide which terms to keep and which
    to discard when expanding a query using the "suggest" syntax.  As
    a place to start, we throw out:

      - Terms that don't begin with an uppercase letter or digit.
        This filters prefixed terms and stemmed forms.

      - Terms shorter than min_length chars, which are likely irrelevant

      - Stopwords for the given language.  Default is english, pass
        None for the lang argument if no stopping is desired.
    """

    min_length = 5
    nostart = unicode(string.uppercase + string.digits)

    def __init__(self, lang="en", filter=None, stems=None):
        super(LangDecider, self).__init__()
        if lang in snowball.stoppers:
            self.stopper = snowball.stoppers[lang]
            self.stemmer = xapian.Stem(lang)
        else:
            self.stopper = lambda(term): False
            self.stemmer = xapian.Stem("none")
        self.stems = tuple(self.stemmer(t) for t in stems) if stems else ()

    def __call__(self, term):
        term = term.decode("utf-8")
        if (term[0] in self.nostart or
            len(term) < self.min_length or
            self.stopper(term) or
            '_' in term or
            self.stemmer(term) in self.stems):
            return False
        return True


class PrefixDecider(xapian.ExpandDecider):

    __slots__ = ['prefix']

    def __init__(self, prefix):
        super(PrefixDecider, self).__init__()
        self.prefix = 'X' + prefix.upper()

    def __call__(self, term):
        return term.decode('utf-8').startswith(self.prefix)


class MultipleValueRangeProcessor(xapian.ValueRangeProcessor):
    """Value range processor for multiple prefixes.

    :param map: a dict of prefix to value number pairs.

    :param serializer: optional callable to serialize the arguments into
                       the same form as the corresponding values are stored.
                       Typically xapian.sortable_serialise for floats,
                       str.lower for strings.
    """

    def __init__(self, map, serializer=None):
        self.map = map
        self.serializer = serializer or (lambda x: x)
        xapian.ValueRangeProcessor.__init__(self)

    def __call__(self, begin, end):
        for prefix, value in self.map.items():
            if begin.startswith(prefix + ':'):
                return (value,
                        self.serializer(begin[len(prefix) + 1:]),
                        self.serializer(end))
        return (xapian.BAD_VALUENO, begin, end)


class Record(object):
    """Default dumb record type, names begining with _xodb_ are reserved ."""

    def __init__(self, document, otype, newargs, state):
        # this does not mangle the names
        state.update(__xodb_document=document,
                     __xodb_type=otype,
                     __xodb_newargs=newargs)
        self.__dict__ = state


class BrokenRecord(Record):
    """Type returned when pickled type cannot be found."""
    pass


def instance_factory(document, otype, newargs, state):
    inst = otype.__new__(otype, *newargs)
    inst.__dict__ = state
    return inst


class Database(object):
    """A xodb database.

    :param db_or_path: A path to file, or a xapian.Database object
    that backs this Database instance.

    :param writable: Open database in writable mode.

    :param overwrite: If writable is True, overwrite the existing
    database with a new one.

    :param spelling: If True, write spelling correction data to the
    database.

    :param record_factory: Callable factory to pass stored object
    state when results are instanciated.

    :param persistent_id: Callable to resolve persistent ids for
    pickled object state.

    :param persistent_load: Callable to resolve pickled object state
    for persistent id.
    """
    COMPRESS_OVER = 256 # set to 0 to disable compression

    relevance_prefix = "_XODB_RP_"
    boolean_prefix = "_XODB_BP_"
    value_prefix = "_XODB_VALUE_"
    value_sort_prefix = "_XODB_VALUESORT_"
    value_count_name = "_XODB_COUNT_"

    def __init__(self, db_or_path,
                 writable=True, overwrite=False,
                 spelling=True, record_factory=Record,
                 persistent_id=None, persistent_load=None):
        self._writable = writable
        self.backend = db_or_path
        self.spelling = spelling
        self.record_factory = record_factory
        self.persistent_id = persistent_id
        self.persistent_load = persistent_load

        if isinstance(db_or_path, basestring):
            if writable:
                if overwrite:
                    flags = xapian.DB_CREATE_OR_OVERWRITE
                else:
                    flags = xapian.DB_CREATE_OR_OPEN
                self.backend = xapian.WritableDatabase(db_or_path, flags)
            else:
                self.backend = xapian.Database(db_or_path)
        elif not isinstance(db_or_path, xapian.Database):
            raise TypeError(
                'First argument must be path or xapian.[Writable]Database')

        self.relevance_prefixes = {}
        self.boolean_prefixes = {}
        self.values = {}
        self.value_sorts = {}
        self.type_map = {}

        self.map(object, Schema)
        self.reopen()

    def map(self, otype, schema):
        """Map a type to a schema."""
        self.type_map[otype] = schema

    def unmap(self, otype):
        """Unmap a type."""
        del self.type_map[otype]

    def clear_map(self):
        self.type_map = {}

    def schema_for(self, otype):
        """Get the schema for a given type, or one of its
        superclasses."""
        for base in otype.__mro__:
            if base in self.type_map:
                return self.type_map[base]
        return Schema

    def serialize(self, typ, newargs, state):
        f = StringIO()
        pickler = Pickler(f, -1)
        pickler.dump((typ, newargs))
        if self.persistent_id is not None:
            pickler.persistent_id = self.persistent_id
        pickler.dump(state)
        data = f.getvalue()
        if self.COMPRESS_OVER and len(data) > self.COMPRESS_OVER:
            data = compress(data)
        return data

    def unserialize(self, document, record_factory=None):
        
        data = _decompress(document.get_data())
        file = StringIO(data)
        unpickler = Unpickler(file)
        try:
            otype, newargs = unpickler.load()
        except AttributeError:
            # the type may have gone away ...
            otype, newargs = BrokenRecord, ()
        if self.persistent_load is not None:
            unpickler.persistent_load = self.persistent_load
        state = unpickler.load()
        if record_factory:
            return record_factory(document, otype, newargs, state)
        else:
            return document, otype, newargs, state

    def _get_value_count(self):
        return int(self.backend.get_metadata(self.value_count_name))

    def _set_value_count(self, count):
        self.backend.set_metadata(self.value_count_name, str(count))

    value_count = property(_get_value_count, _set_value_count)

    def add_prefix(self, key, value):
        self.relevance_prefixes[key] = value
        self.backend.set_metadata(self.relevance_prefix + key, value)

    def add_boolean_prefix(self, key, value):
        self.boolean_prefixes[key] = value
        self.backend.set_metadata(self.boolean_prefix + key, value)

    def add_value(self, name, sort=None):
        if name in self.values:
            return self.values[name]
        value_count = self.value_count + 1
        self.value_count = value_count
        self.values[name] = value_count
        self.backend.set_metadata(self.value_prefix + name, str(value_count))
        if sort:
            self.value_sorts[name] = sort
            self.backend.set_metadata(self.value_sort_prefix + name, sort)
        return value_count

    def __len__(self):
        """ Return the number of documents in this database. """
        self.backend.reopen()
        return self.backend.get_doccount()

    def allterms(self, prefix=""):
        for t in self.backend.allterms(prefix):
            yield t.term

    def get(self, docid, default=None):
        """ Get a document with the given docid, or the default value if
        no such document exists.
        """
        try:
            return self[docid]
        except DocNotFoundError:
            return default

    def __getitem__(self, docid):
        document = self.backend.get_document(docid)
        return self.unserialize(document, self.record_factory)

    def __delitem__(self, docid):
        self.backend.delete_document(docid)

    def __setitem__(self, docid, document):
        doc = self.get(docid)
        if doc is None:
            self.backend.add_document(document)
        else:
            self.backend.replace_document(docid, document)

    def add(self, *objs):
        added = []
        for obj in objs:
            if hasattr(obj, '__xodb_schema__'):
                schema_type = obj.__xodb_schema__
            else:
                schema_type = self.schema_for(type(obj))
            schema = schema_type(self)
            added.append(self.backend.add_document(schema(obj)))
        return added

    def reopen(self):
        self.backend.reopen()
        try:
            keys = self.backend.metadata_keys()
        except UnimplementedError:
            # Inmemory backends don't expose this function, so just
            # return since they can't persist anything anyway!
            return

        self.relevance_prefixes.clear()
        self.boolean_prefixes.clear()
        self.values.clear()
        self.value_sorts.clear()

        for k in keys:
            if k.startswith(self.relevance_prefix):
                prefix = k[len(self.relevance_prefix):]
                self.relevance_prefixes[prefix] = self.backend.get_metadata(k)
            elif k.startswith(self.boolean_prefix):
                prefix = k[len(self.boolean_prefix):]
                self.boolean_prefixes[prefix] = self.backend.get_metadata(k)
            elif k.startswith(self.value_prefix):
                value = k[len(self.value_prefix):]
                self.values[value] = int(self.backend.get_metadata(k))
            elif k.startswith(self.value_sort_prefix):
                value = k[len(self.value_sort_prefix):]
                self.value_sorts[value] = self.backend.get_metadata(k)

        # hit the property to refresh this value
        try:
            count = self.value_count
        except ValueError:
            if self._writable:
                self.value_count = 0

    def begin(self):
        if self._writable:
            self.backend.reopen()
            self.backend.begin_transaction()

    def cancel(self):
        if self._writable:
            self.backend.cancel_transaction()

    def commit(self):
        if self._writable:
            self.backend.commit_transaction()

    def prepare_query_parser(self, lang=None, default_op=xapian.Query.OP_AND):
        qp = xapian.QueryParser()
        qp.set_database(self.backend)
        qp.set_default_op(default_op)

        if self.relevance_prefixes:
            for key, value in self.relevance_prefixes.items():
                qp.add_prefix(key, value)
        if self.boolean_prefixes:
            for key, value in self.boolean_prefixes.items():
                qp.add_boolean_prefix(key, value)
        if self.value_sorts:
            # First add numeric values ranges
            qp.add_valuerangeprocessor(MultipleValueRangeProcessor(
                dict(((k, self.values[k])
                      for k, v in self.value_sorts.items() if v == 'numeric')),
                lambda s: xapian.sortable_serialise(float(s)),
            ))
            # Then string and date
            qp.add_valuerangeprocessor(MultipleValueRangeProcessor(
                dict(((k, self.values[k])
                      for k, v in self.value_sorts.items() if v != 'numeric')),
            ))
        if lang in snowball.stoppers:
            qp.set_stemmer(xapian.Stem(lang))
            qp.set_stopper(snowball.stoppers[lang])
            qp.set_stemming_strategy(xapian.QueryParser.STEM_SOME)
        return qp

    def query(self, query, offset=0, limit=None, order=None,
              reverse=False, lang=None, check=0,
              match_decider=None, match_spy=None,
              echo=False, parser_flags=default_parser_flags,
              document=False,
              default_op=xapian.Query.OP_AND):
        """
        Query the database with the provided string or xapian Query
        object.  A string is passed into xapians QueryParser first to
        generate a Query object.
        """
        self.reopen()
        if query == "":
            query = xapian.Query("")
        else:
            qp = self.prepare_query_parser(lang, default_op)
            query = qp.parse_query(query, parser_flags)

        if echo:
            print str(query)
        enq = xapian.Enquire(self.backend)
        enq.set_query(query)

        mset = self._build_mset(enq, offset, limit, order, reverse,
                                check, match_decider, match_spy)
        return self._return_objects(mset, document=document)

    def estimate(self, query, limit=0, lang=None,
                 parser_flags=default_parser_flags):
        """Estimate the number of documents that will be yielded with the
        given query.

        Limit tells the estimator the minimum number of documents to
        consider.  A zero limit means check all documents in the db."""
        self.reopen()
        enq = xapian.Enquire(self.backend)

        if limit == 0:
            limit = self.backend.get_doccount()

        if query == "":
            query = xapian.Query("")
        else:
            qp = self.prepare_query_parser(lang)
            query = qp.parse_query(query, parser_flags)

        enq.set_query(query)
        return enq.get_mset(0, 0, limit).get_matches_estimated()

    def term_freq(self, term):
        """
        Return a count of the number of documents indexed for a given
        term.  Useful for testing.
        """
        self.backend.reopen()
        return self.backend.get_termfreq(term)

    def get_doccount(self):
        """
        Return the number of indexed documents, handy for tests and
        sanity check.
        """
        self.backend.reopen()
        return self.backend.get_doccount()

    def describe_query(self, query, lang=None,
              default_op=xapian.Query.OP_AND):
        """
        Describe the parsed query.
        """
        qp = self.prepare_query_parser(lang, default_op)
        q = qp.parse_query(query, default_parser_flags)
        return str(q)

    def spell(self, query, lang=None):
        """
        Suggest a query string with corrected spelling.
        """
        self.backend.reopen()
        qp = self.prepare_query_parser(lang)
        qp.parse_query(query, xapian.QueryParser.FLAG_SPELLING_CORRECTION)
        return qp.get_corrected_query_string().decode('utf8')

    def suggest(self, query, offset=0, limit=10, moffset=0, mlimit=10,
                lang=None, prefix=None, decider=None, score=False):
        """
        Suggest terms that would possibly yield more relevant results
        for the given query.
        """
        self.reopen()
        enq = xapian.Enquire(self.backend)

        qp = self.prepare_query_parser(lang)

        if mlimit is None:
            mlimit = self.backend.get_doccount()

        enq.set_query(qp.parse_query(query))

        mset = self._build_mset(enq, offset=moffset, limit=mlimit)

        rset = xapian.RSet()
        for m in mset:
            if hasattr(m, 'docid'): # 1.1
                docid = m.docid
            else:
                docid = m[xapian.MSET_DID] # 1.0
            rset.add_document(docid)

        if prefix is not None:
            decider = PrefixDecider(prefix)

        if decider is None:
            decider = LangDecider(lang)
        eset = enq.get_eset(limit, rset, decider)

        for item in eset.items:
            val = item[0].decode('utf8')
            if prefix and val.startswith('X' + prefix.upper()):
                val = "%s:%s" % (prefix, val[len(prefix) + 1:])
            if score:
                yield (val, item[1])
            else:
                yield val

    def similar(self, query=None, offset=0, limit=None, order=None,
                reverse=False, lang=None, check=None,
                match_decider=None, match_spy=None, terms=None,
                default_op=xapian.Query.OP_AND):
        """ Find documents in the database most relevant to the given terms.

        'query' - If *terms*=None, query is passed to xaql.suggest to
        get a list of terms. If *terms* is set, that term list is used
        directly and the *query* is parsed and ANDed with the elite term
        set query.

        'limit' - The number of records to return.

        'lang' - The language stemmer the parser should use.

        'match_decider' - A MatchDecider to apply to the query.

        'terms' - Optional term list from which to derive the
        elite set of terms to match on.
        """
        self.reopen()

        if not terms:
            assert query, 'Query or terms is requred'
            suggested_terms = self.suggest(
                query, lang=lang)
            terms = list(suggested_terms)
            query = None
        elif query:
            qp = self.prepare_query_parser(lang, default_op)
            query = qp.parse_query(query, default_parser_flags)

        enq = xapian.Enquire(self.backend)

        if limit is None:
            limit = self.backend.get_doccount()

        similar_query = Query(Query.OP_ELITE_SET, terms, limit)
        if query:
            similar_query = Query(Query.OP_AND, [similar_query, query])
        enq.set_query(similar_query)

        mset = self._build_mset(enq, offset, limit, order, reverse,
                                check, match_decider, match_spy)
        return self._return_objects(mset)

    def _build_mset(self, enq, offset=0, limit=None, order=None, reverse=False,
                    check=None, match_decider=None, match_spy=None):

        if order is not None:
            if isinstance(order, basestring):
                try:
                    order = self.values[order]
                except KeyError:
                    raise ValueError("There is no sort name %s" % order)
            enq.set_sort_by_value(order, reverse)

        if limit is None:
            limit = self.backend.get_doccount()

        if check is None:
            check = limit + 1

        tries = 0
        while True:
            try:
                mset = enq.get_mset(
                    offset, limit, check, None, match_decider, match_spy)
                break
            except xapian.DatabaseModifiedError:
                if tries > RETRY_LIMIT:
                    raise
                self.reopen()
                tries += 1
        return mset

    def _return_objects(self, mset, document=False):
        for record in mset:
            if hasattr(record, 'document'):  # 1.1
                doc = record.document
            else:
                doc = record[xapian.MSET_DOCUMENT] # 1.0
            if document:
                yield doc
            else:
                obj = self.unserialize(doc, record_factory=self.record_factory)
                yield obj

    def term_counter(self, prefixes):
        """Construct a term count spy with this instance's prefix dict."""
        prefix_map = self.relevance_prefixes.copy()
        prefix_map.update(self.boolean_prefixes)
        return TermCountMatchSpy(prefixes, prefix_map)
