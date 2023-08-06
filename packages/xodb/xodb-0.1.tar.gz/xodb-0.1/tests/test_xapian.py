import datetime
import xodb
import tempfile
import xapian
from xodb import Schema, Attribute, MultipleValueRangeProcessor

from nose.tools import assert_raises


# These tests and the Attribute description syntax the use is
# deprecated, these will be removed when Attribute style schemas go
# away completely


class Ding(object):
    def __init__(self):
        self.blig = 41
        self.bloog = 42
        self.sez = set([])
        self.canary = []

        self.language = 'en'
        self.name = 'ding'
        self.direction = 'north'
        self.title = 'The young and the database.'
        self.instructions = 'Under the walker'
        self.zig = 3
        self.zag = 6
        self.zork = ['zap', 'zop', 'zern']
        self.zirk = {'jib': 'zoop', 'jab': 'zeep'}
        self.bing = ['boop', 'berp', 'barp']
        self.bang = {'plop': 'This is a borp of a time', 'plip': 'Textual birpism'}
        self.slap = 3
        self.slag = datetime.date(2009, 01, 20)
        self.slup = datetime.datetime(2009, 01, 20, 11, 58, 59)
        self.slat = 'fuzzy'


class DingSchema(Schema):

    def __before__(self, obj):
        obj.canary.append(self)

    name          = Attribute(text=True)
    direction     = Attribute(prefixed=True)
    title         = Attribute(text=True)
    instructions  = Attribute(prefixed=True, text=True)
    zig           = Attribute(value=True)
    zag           = Attribute(value=True, value_parent=zig)
    zork          = Attribute(value=True, sequence=True)
    zirk          = Attribute(value=True, prefixed=True, mapping=True)
    bing          = Attribute(value=True, sequence=True, prefixed=True)
    bang          = Attribute(value=True, prefixed=True, text=True, mapping=True)
    slap          = Attribute(prefixed=True, sortable='numeric')
    slag          = Attribute(prefixed=True, sortable='date')
    slup          = Attribute(prefixed=True, sortable='datetime')
    slat          = Attribute(prefixed=True, sortable='string')
    schlip        = Attribute(required=False, getter=lambda sc, na: "booring")
    canary        = Attribute(volatile=True)
    hipster       = Attribute(default="look")

    def __after__(self, obj, state, doc):
        obj.canary.append(self)


class Dang(object):
    zig = None


class DangSchema(Schema):
    zig = Attribute(prefixed=True, text=True)


class _TestXapianBase(object):

    db_factory = None

    def setup(self):
        self.db = self.db_factory()
        assert self.db.backend.get_doccount() == 0

    def test_no_bogus_db(self):
        assert_raises(TypeError, xodb.Database, None)
        assert_raises(TypeError, xodb.Database, 1)
        assert_raises(TypeError, xodb.Database, True)

    def test_stored_prefixes(self):
        t = tempfile.mkdtemp()
        x = xapian.WritableDatabase(t, xapian.DB_CREATE_OR_OVERWRITE)
        x.set_metadata("_XODB_RP_Foo", "bar")
        x.set_metadata("_XODB_BP_Ding", "dong")
        x.flush()
        xdb = xodb.Database(x)
        assert xdb.relevance_prefixes['Foo'] == 'bar'
        assert xdb.boolean_prefixes['Ding'] == 'dong'

    def test_stored_values(self):
        db = self.db
        assert db.value_count == 0
        assert db.add_value('foo')
        assert db.value_count == 1
        assert db.add_value('foo')
        assert db.value_count == 1
        assert db.add_value('bar')
        assert db.value_count == 2

    def test_values(self):
        d = Ding()
        d.zig = 1
        d.zag = 9
        e = Ding()
        e.zig = 2
        e.zag = 8
        f = Ding()
        f.zig = 3
        e.zag = 7
        self.db.map(Ding, DingSchema)
        for i in [d, e, f]:
            self.db.add(i)

        forwardzig = [d.zig, e.zig, f.zig]
        reversezig = [f.zig, e.zig, d.zig]
        forwardzag = [f.zag, e.zag, d.zag]
        reversezag = [d.zag, e.zag, f.zag]

        results = list(self.db.query('ding', order="zig"))
        assert len(results) == 3
        assert [t.zig for t in results] == forwardzig
        results = list(self.db.query('ding', order="zig", reverse=False))
        assert len(results) == 3
        assert [t.zig for t in results] == forwardzig
        results = list(self.db.query('ding', order="zig", reverse=True))
        assert len(results) == 3
        assert [t.zig for t in results] == reversezig
        results = list(self.db.query('ding', order="zag"))
        assert len(results) == 3
        assert [t.zag for t in results] == forwardzag
        results = list(self.db.query('ding', order="zag", reverse=False))
        assert len(results) == 3
        assert [t.zag for t in results] == forwardzag
        results = list(self.db.query('ding', order="zag", reverse=True))
        assert len(results) == 3
        assert [t.zag for t in results] == reversezag

    def test_schema_text_search(self):
        """ Text searching with unprefixed terms. """
        d = Ding()
        self.db.map(Ding, DingSchema)
        self.db.add(d)
        results = list(self.db.query("young"))
        assert len(results) == 1
        results = list(self.db.query("database"))
        assert len(results) == 1
        results = list(self.db.query("foobar"))
        assert len(results) == 0
        assert self.db.term_freq("young") == 1

    def test_default_value(self):
        d = Ding()
        self.db.map(Ding, DingSchema)
        self.db.add(d)
        results = list(self.db.query("young"))
        assert results[0].hipster == "look"

    def test_required_missing(self):
        class foo(object): pass

        class fooschema(Schema):
            bar = Attribute()

        self.db.map(foo, fooschema)
        d = foo()
        assert_raises(TypeError, self.db.add, d)

    def test_attribute_type(self):
        class foo(object): 
            def __init__(self):
                self.z = 5

        class fooschema(Schema):
            z = Attribute(type=str)

        self.db.map(foo, fooschema)
        d = foo()
        assert_raises(TypeError, self.db.add, d)

    def test_prefixed_text_search(self):
        """ Text searching with prefixed terms. """
        d = Ding()
        self.db.map(Ding, DingSchema)
        self.db.add(d)
        results = list(self.db.query("instructions:walker"))
        assert len(results) == 1
        results = list(self.db.query("instructions:bug"))
        assert len(results) == 0

    def test_prefixed_term_search(self):
        """ Term searching with prefix. """
        d = Ding()
        self.db.map(Ding, DingSchema)
        self.db.add(d)
        results = list(self.db.query("direction:north"))
        assert len(results) == 1
        results = list(self.db.query("direction:south"))
        assert len(results) == 0

    def test_schema_term_search(self):
        """ Term searching without prefix. """
        self.db.map(Ding, DingSchema)
        d = Ding()
        self.db.add(d)
        results = list(self.db.query("ding"))
        assert len(results) == 1
        results = list(self.db.query("dong"))
        assert len(results) == 0

    def test_sequence_terms(self):
        self.db.map(Ding, DingSchema)
        d = Ding()
        self.db.add(d)
        results = list(self.db.query("zap"))
        assert len(results) == 1
        results = list(self.db.query("zop"))
        assert len(results) == 1
        results = list(self.db.query("zern"))
        assert len(results) == 1
        results = list(self.db.query("zowwie"))
        assert len(results) == 0

    def test_sequence_prefixed_terms(self):
        self.db.map(Ding, DingSchema)
        d = Ding()
        self.db.add(d)
        results = list(self.db.query("bing:boop"))
        assert len(results) == 1
        results = list(self.db.query("bing:berp"))
        assert len(results) == 1
        results = list(self.db.query("bing:barp"))
        assert len(results) == 1
        results = list(self.db.query("bing:zowwie"))
        assert len(results) == 0

    def test_mapping_terms(self):
        self.db.map(Ding, DingSchema)
        d = Ding()
        self.db.add(d)
        results = list(self.db.query("zirk_jib:zoop"))
        assert len(results) == 1
        results = list(self.db.query("zirk_jab:zeep"))
        assert len(results) == 1
        results = list(self.db.query("zirk_jib:nono"))
        assert len(results) == 0

    def test_mapping_prefixed_text(self):
        self.db.map(Ding, DingSchema)
        d = Ding()
        self.db.add(d)
        results = list(self.db.query("bang_plop:borp"))
        assert len(results) == 1
        results = list(self.db.query("bang_plip:birpism"))
        assert len(results) == 1
        results = list(self.db.query("bang_plop:nono"))
        assert len(results) == 0

    def test_numeric_sort_value(self):
        self.db.map(Ding, DingSchema)
        d = Ding()
        d.slap = 3
        e = Ding()
        e.slap = 2
        self.db.add(d)
        self.db.add(e)
        results = list(self.db.query("slap:3"))
        assert len(results) == 1
        results = list(self.db.query("slap:3..4"))
        assert len(results) == 1
        results = list(self.db.query("slap:2..4"))
        assert len(results) == 2

    def test_date_and_datetime_sort_value(self):
        self.db.map(Ding, DingSchema)
        d = Ding()
        d.slag = datetime.date(2009, 1, 10)
        d.slup = datetime.datetime(2009, 01, 20, 1, 2, 3)
        e = Ding()
        e.slag = datetime.date(2009, 4, 20)
        e.slup = datetime.datetime(2009, 4, 20, 11, 58, 59)
        self.db.add(d)
        self.db.add(e)
        assert len(list(self.db.query("slag_date:20090420"))) == 1
        assert len(list(self.db.query("slag_date:20090421"))) == 0
        assert len(list(self.db.query("slag_date:200904*"))) == 1
        assert len(list(self.db.query("slag_date:2009*"))) == 2
        results = list(self.db.query("slag:20090201..20090501"))
        assert len(results) == 1
        results = list(self.db.query("slag:20090101..20090501"))
        assert len(results) == 2
        results = list(self.db.query("slag:19700101..20080501"))
        assert len(results) == 0

        assert len(list(self.db.query("slup_datetime:20090420115859"))) == 1
        assert len(list(self.db.query("slup_datetime:20090421115959"))) == 0
        assert len(list(self.db.query("slup_datetime:200904*"))) == 1
        assert len(list(self.db.query("slup_datetime:2009*"))) == 2

        results = list(self.db.query("slup:20090201..20090501"))
        assert len(results) == 1
        results = list(self.db.query("slup:20090101..20090501"))
        assert len(results) == 2
        results = list(self.db.query("slup:19700101..20080501"))
        assert len(results) == 0

    def test_string_sort_value(self):
        self.db.map(Ding, DingSchema)
        d = Ding()
        d.slat = "fuzzybear"
        e = Ding()
        e.slat = "fuzzybunny"
        self.db.add(d)
        self.db.add(e)
        results = list(self.db.query("slat:fuzzybear"))
        assert len(results) == 1
        results = list(self.db.query("slat:fuzzy..fuzzybrine"))
        assert len(results) == 1
        results = list(self.db.query("slat:fuzzy..gump"))
        assert len(results) == 2
        results = list(self.db.query("slat:gump..zed"))
        assert len(results) == 0

    def test_estimate(self):
        self.db.map(Ding, DingSchema)
        d = Ding()
        self.db.add(d)
        assert self.db.estimate("bang_plop:borp") == 1
        assert self.db.backend.get_doccount() == 1

    def test_empty_query(self):
        assert not len(list(self.db.query('')))

    def test_describe_query(self):
        assert self.db.describe_query('foo') == 'Xapian::Query(foo:(pos=1))'

    def test_before_after(self):
        self.db.map(Ding, DingSchema)
        d = Ding()
        self.db.add(d)
        assert len(d.canary) == 2

    def test_before_after_terms(self):
        self.db.map(Ding, DingSchema)
        d = Ding()
        self.db.add(d)
        r = list(self.db.query("booring"))
        assert len(r) == 1

    def test_instance_factory(self):
        self.db = xodb.temp(record_factory=xodb.instance_factory)
        d = Ding()
        self.db.map(Ding, DingSchema)
        i = self.db.add(d)[0]
        e = self.db.get(i)
        assert isinstance(e, Ding)
        assert not hasattr(e, 'blig')
        assert not hasattr(e, 'canary')
        assert e.zig == 3
        assert e.zork == ['zap', 'zop', 'zern']
        assert e.zirk == {'jib': 'zoop', 'jab': 'zeep'}
        assert e.slag == datetime.date(2009, 01, 20)


class TestXapianFile(_TestXapianBase):
    db_factory = staticmethod(xodb.temp)


class TestXapianInMem(_TestXapianBase):
    db_factory = staticmethod(xodb.inmemory)


def test_value_range_processor():
    vp = MultipleValueRangeProcessor(dict(foo=1, bar=2), str.upper)
    assert vp('foo:abc', 'def') == (1, 'ABC', 'DEF')
    assert vp('bar:news', 'def') == (2, 'NEWS', 'DEF')
    assert vp('bar:', 'def') == (2, '', 'DEF')
    assert vp('bar', 'def') == (xapian.BAD_VALUENO, 'bar', 'def')
    assert vp('baz:foo', 'def') == (xapian.BAD_VALUENO, 'baz:foo', 'def')

    qp = xapian.QueryParser()
    db = xodb.temp()
    qp.set_database(db.backend)
    qp.add_valuerangeprocessor(vp)

    query = qp.parse_query('foo:abc..def')
    assert str(query) == 'Xapian::Query(VALUE_RANGE 1 ABC DEF)'

    query = qp.parse_query('bar:abc..def')
    assert str(query) == 'Xapian::Query(VALUE_RANGE 2 ABC DEF)'

    query = qp.parse_query('bar:3..4')
    assert str(query) == 'Xapian::Query(VALUE_RANGE 2 3 4)'

    assert_raises(xapian.QueryParserError, qp.parse_query, 'baz:abc..def')


class TestXapianSuggest(object):

    def setup(self):
        self.db = xodb.temp()
        self.db.map(Dang, DangSchema)
        self.dangs = []
        for value in ('food bar', 'food foo', 'food baz', 'fee fum'):
            d = Dang()
            d.zig = value
            self.db.add(d)
            self.dangs.append(d)

#     def test_suggest(self):
#         result = self.db.suggest('zig:bar')
#         assert result.next()

    def test_similar(self):
        result = self.db.similar(terms=['food', 'spice'])
        dangs = [d.zig for d in result]
        assert len(dangs) == 3
        assert 'fee fum' not in dangs

#     def test_similar_query(self):
#         import pdb; pdb.set_trace()
#         result = self.db.similar('bar')
#         dangs = [d.zig for d in result]
#         assert len(dangs) == 3
#         assert 'fee fum' not in dangs

    def test_similar_query_with_terms(self):
        result = self.db.similar('zig:food', terms=['bar', 'baz'])
        dangs = [d.zig for d in result]
        assert len(dangs) == 2 
        assert 'fee fum' not in dangs
        assert 'food foo' not in dangs

