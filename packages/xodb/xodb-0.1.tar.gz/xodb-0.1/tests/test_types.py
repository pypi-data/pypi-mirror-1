import datetime
import xodb
from xodb import Schema
from xodb.types import String, Numeric, Date, Datetime, Text, Sequence, Mapping

from nose.tools import assert_raises

# fixtures


class Thinger(object):

    def __init__(self, **args):
        self.__dict__ = args


class Stringer(Thinger):
    pass


class Numericer(Thinger):
    pass


class Dater(Thinger):
    pass


class Datetimer(Thinger):
    pass


class Texter(Thinger):
    pass


class Sequencer(Thinger):
    pass


class Mapper(Thinger):
    pass


class Person(Thinger):
    pass


class Department(Thinger):
    pass

# basic


class StringerSchema(Schema):
    s = String()


class NumericerSchema(Schema):
    n = Numeric()


class DaterSchema(Schema):
    d = Date()


class TexterSchema(Schema):

    def __before__(self, obj):
        self.__language__ = "en"
    
    t = Text(prefixed=False)
    j = Text()


class DatetimerSchema(Schema):
    dt = Datetime()


class SequencerSchema(Schema):
    seq = Sequence()


class MapperSchema(Schema):
    map = Mapping()

# sort


class SortStringerSchema(Schema):
    s = String(sortable=True)


class SortNumericerSchema(Schema):
    n = Numeric(sortable=True)


class SortDaterSchema(Schema):
    d = Date(sortable=True)


class SortDatetimerSchema(Schema):
    dt = Datetime(sortable=True)

# facets


class FacetStringerSchema(Schema):
    s = String(facet=True)


class FacetNumericerSchema(Schema):
    n = Numeric(facet=True)


class FacetDaterSchema(Schema):
    d = Date(facet=True)


class FacetDatetimerSchema(Schema):
    dt = Datetime(facet=True)


class FacetSequencerSchema(Schema):
    seq = Sequence(facet=True)


class FacetMapperSchema(Schema):
    map = Mapping(facet=True)

# containers


class SequencerNumericSchema(Schema):
    seq = Sequence(Numeric())


class SequencerSequencerSchema(Schema):
    seq = Sequence(Sequence())


class MapperNumericSchema(Schema):
    map = Mapping(Numeric())


class MapperMapperSchema(Schema):
    map = Mapping(Mapping())

#chaining


class ChainedStringerNumericerSchema(Schema):
    t = Text(getter=String(sortable=True))

    @Sequence.getter()
    @String.getter(sortable=True)
    def s(self, name):
        return getattr(self.__object__, name)

# modely stuff


class FacetPersonSchema(Schema):
    name = String(facet=True)


class FacetPersonGetterSchema(Schema):

    @String.getter(facet=True)
    def name(self, name):
        return getattr(self.__object__, name) + 'ha'


class FacetPersonRequiredSchema(Schema):
    zoo = String(facet=True, required=True)


class FacetPersonTypeRequiredSchema(Schema):
    name = String(facet=True, required_type=str)


class FacetDepartmentSchema(Schema):
    name = String(facet=True)
    employees = Sequence(facet=True)


class _TestXapianBase(object):
    db_factory = None

    def setup(self):
        self.db = self.db_factory()
        assert self.db.backend.get_doccount() == 0

    def test_string_term(self):
        self.db.map(Stringer, StringerSchema)
        s = Stringer(s="joe")
        self.db.add(s)
        assert self.db.backend.get_doccount() == 1
        assert self.db.query('s:joe').next().s == 'joe'

    def test_string_sort(self):
        self.db.map(Stringer, SortStringerSchema)
        s = Stringer(s="joe")
        s2 = Stringer(s="jane")
        self.db.add(s, s2)
        assert self.db.backend.get_doccount() == 2
        assert self.db.query('s:joe').next().s == 'joe'
        assert self.db.query('s:jane').next().s == 'jane'
        q = list(self.db.query('s:jane..joe', order='s'))
        assert [i.s for i in q] == ['jane', 'joe']
        q = list(self.db.query('s:jane..joe', order='s', reverse=True))
        assert [i.s for i in q] == ['joe', 'jane']

    def test_numeric_term(self):
        self.db.map(Numericer, NumericerSchema)
        n = Numericer(n=5)
        self.db.add(n)
        assert self.db.backend.get_doccount() == 1
        assert self.db.query('n:5').next().n == 5

    def test_numeric_sort(self):
        self.db.map(Numericer, SortNumericerSchema)
        n = Numericer(n=5)
        m = Numericer(n=6)
        self.db.add(n, m)
        assert self.db.backend.get_doccount() == 2
        assert self.db.query('n:5').next().n == 5
        assert self.db.query('n:6').next().n == 6
        q = list(self.db.query('n:4..8', order='n'))
        assert [i.n for i in q] == [5, 6]
        q = list(self.db.query('n:4..8', order='n', reverse=True))
        assert [i.n for i in q] == [6, 5]

    def test_date_term(self):
        self.db.map(Dater, DaterSchema)
        d = Dater(d=datetime.date(1975, 4, 23))
        self.db.add(d)
        assert self.db.backend.get_doccount() == 1
        d = datetime.date(1975, 4, 23)
        query = 'd:19750423'
        assert self.db.query('d:19750423').next().d == d
        for i in range(1, len(query) - 3):
            assert self.db.query(query[:-i] + '*').next().d == d

    def test_date_sort(self):
        self.db.map(Dater, SortDaterSchema)
        d = Dater(d=datetime.date(1975, 4, 23))
        d2 = Dater(d=datetime.date(1975, 5, 23))
        self.db.add(d, d2)
        assert self.db.backend.get_doccount() == 2
        assert (self.db.query('d:19750423').next().d ==
                datetime.date(1975, 4, 23))
        q = list(self.db.query('d:19750423..19750623', order="d"))
        assert len(q) == 2
        assert [i.d for i in q] == [d.d, d2.d]
        q = list(self.db.query('d:19750423..19750623',
                               order="d", reverse=True))
        assert len(q) == 2
        assert [i.d for i in q] == [d2.d, d.d]

    def test_datetime_term(self):
        self.db.map(Datetimer, DatetimerSchema)
        dt = Datetimer(dt=datetime.datetime(1975, 4, 23, 11, 59, 59))
        self.db.add(dt)
        assert self.db.backend.get_doccount() == 1
        dt = datetime.datetime(1975, 4, 23, 11, 59, 59)
        query = 'dt:19750423'
        assert self.db.query(query).next().dt == dt
        for i in range(1, len(query) - 3):
            assert self.db.query(query[:-i] + '*').next().dt == dt

    def test_datetime_sort(self):
        self.db.map(Datetimer, SortDatetimerSchema)
        dt = Datetimer(dt=datetime.datetime(1975, 4, 23, 11, 59, 59))
        dt2 = Datetimer(dt=datetime.datetime(1975, 5, 23, 11, 59, 59))
        self.db.add(dt, dt2)
        assert self.db.backend.get_doccount() == 2
        assert (self.db.query('dt:19750423').next().dt ==
                datetime.datetime(1975, 4, 23, 11, 59, 59))
        q = list(self.db.query('dt:19750423115959..19750623115959',
                               order="dt"))
        assert len(q) == 2
        assert [i.dt for i in q] == [dt.dt, dt2.dt]
        q = list(self.db.query('dt:19750423115959..19750623115959',
                               order="dt", reverse=True))
        assert len(q) == 2
        assert [i.dt for i in q] == [dt2.dt, dt.dt]

    def test_sequence_term(self):
        self.db.map(Sequencer, SequencerSchema)
        data = ['one', 'two', 'three']
        seq = Sequencer(seq=data)
        self.db.add(seq)
        assert self.db.backend.get_doccount() == 1
        for s in data:
            assert self.db.query('seq:%s' % s).next().seq == data

    def test_sequence_numeric_term(self):
        self.db.map(Sequencer, SequencerNumericSchema)
        data = [1, 2, 3]
        seq = Sequencer(seq=data)
        self.db.add(seq)
        assert self.db.backend.get_doccount() == 1
        for s in data:
            assert self.db.query('seq:%s' % s).next().seq == data

    def test_sequence_sequence_term(self):
        self.db.map(Sequencer, SequencerSequencerSchema)
        data = [['one', 'two', 'tree'],
                ['fee', 'fi', 'foo'],
                ['dee', 'doo', 'dum']]
        seq = Sequencer(seq=data)
        self.db.add(seq)
        assert self.db.backend.get_doccount() == 1
        for s in data:
            for j in s:
                assert self.db.query('seq:%s' % j).next().seq == data

    def test_mapping_term(self):
        self.db.map(Mapper, MapperSchema)
        data = {'one': 'ein',
                'two': 'zwei',
                'three': 'drei'}
        map = Mapper(map=data)
        self.db.add(map)
        assert self.db.backend.get_doccount() == 1
        for k, v in data.items():
            assert self.db.query('map_%s:%s' % (k, v)).next().map == data

    def test_mapping_numeric_term(self):
        self.db.map(Mapper, MapperNumericSchema)
        data = {'one': 1,
                'two': 2,
                'three': 3}
        map = Mapper(map=data)
        self.db.add(map)
        assert self.db.backend.get_doccount() == 1
        for k, v in data.items():
            assert self.db.query('map_%s:%s' % (k, v)).next().map == data

    def test_mapping_mapping_term(self):
        self.db.map(Mapper, MapperMapperSchema)
        data = {'one': dict(foo='fum', fin='fom'),
                'two': dict(fee='fi', fuu='fe'),
                'three': dict(dee='dum', duh='der')}
        map = Mapper(map=data)
        self.db.add(map)
        assert self.db.backend.get_doccount() == 1
        for ok, ov in data.items():
            for k, v in ov.items():
                assert self.db.query('map_%s_%s:%s' %
                                     (ok, k, v)).next().map == data

    def test_string_facet(self):
        self.db.map(Stringer, FacetStringerSchema)
        s = Stringer(s="joe")
        self.db.add(s)
        assert self.db.backend.get_doccount() == 1
        assert self.db.query('facet:s').next().s == 'joe'

    def test_numeric_facet(self):
        self.db.map(Numericer, FacetNumericerSchema)
        n = Numericer(n=5)
        self.db.add(n)
        assert self.db.backend.get_doccount() == 1
        assert self.db.query('facet:n').next().n == 5

    def test_text_term(self):
        self.db.map(Texter, TexterSchema)
        s = Texter(t="Joe's House of Running", j="the short and the prefixed.")
        self.db.add(s)
        assert self.db.backend.get_doccount() == 1
        assert (self.db.query('joe', lang="en").next().t
                == "Joe's House of Running")
        assert (self.db.query('house', lang="en").next().t
                == "Joe's House of Running")
        assert (self.db.query('run', lang="en").next().t
                == "Joe's House of Running")
        assert not set(self.db.query('prefix', lang="en"))

        assert (self.db.query('j:short', lang="en").next().j
                == "the short and the prefixed.")
        assert (self.db.query('j:prefix', lang="en").next().j
                == "the short and the prefixed.")
        assert not set(self.db.query('j:house', lang="en"))

    def test_date_facet(self):
        self.db.map(Dater, FacetDaterSchema)
        d = Dater(d=datetime.date(1975, 4, 23))
        self.db.add(d)
        assert self.db.backend.get_doccount() == 1
        assert self.db.query('facet:d').next().d == d.d

    def test_datetime_facet(self):
        self.db.map(Datetimer, FacetDatetimerSchema)
        dt = Datetimer(dt=datetime.datetime(1975, 4, 23))
        self.db.add(dt)
        assert self.db.backend.get_doccount() == 1
        assert self.db.query('facet:dt').next().dt == dt.dt

    def test_sequence_facet(self):
        self.db.map(Sequencer, FacetSequencerSchema)
        data = ['one', 'two', 'three']
        seq = Sequencer(seq=data)
        self.db.add(seq)
        assert self.db.backend.get_doccount() == 1
        assert self.db.query('facet:seq').next().seq == data

    def test_mapping_facet(self):
        self.db.map(Mapper, FacetMapperSchema)
        data = {'one': 1,
                'two': 2,
                'three': 3}
        map = Mapper(map=data)
        self.db.add(map)
        assert self.db.backend.get_doccount() == 1
        for k in data:
            assert self.db.query('facet:map_' + k).next().map == data

    def test_suggest_facet(self):
        self.db.map(Person, FacetPersonSchema)
        self.db.map(Department, FacetDepartmentSchema)
        o = Person(name="joe")
        a = Person(name="jane")
        d = Department(name="housing", employees=[o.name, a.name])
        self.db.add(o, a, d)

        assert self.db.backend.get_doccount() == 3
        assert (set(self.db.suggest('name:housing', prefix='facet')) ==
                set([u'facet:employees', u'facet:name']))
        assert (set(self.db.suggest('name:housing OR name:jane',
                                    prefix='facet')) ==
                set([u'facet:employees', u'facet:name']))
        assert not set(self.db.suggest('name:housing AND name:jane',
                                       prefix='facet'))

        assert (set(self.db.suggest('name:joe', prefix='facet')) ==
                set([u'facet:name']))
        assert (set(self.db.suggest('name:jane', prefix='facet')) ==
                set([u'facet:name']))
        assert (set(self.db.suggest('name:jane OR name:joe',
                                    prefix='facet')) ==
                set([u'facet:name']))
        assert not set(self.db.suggest('name:jane AND name:joe',
                                       prefix='facet'))

        assert (set(self.db.suggest('employees:jane', prefix='facet')) ==
                set([u'facet:employees', u'facet:name']))
        assert (set(self.db.suggest('employees:joe', prefix='facet')) ==
                set([u'facet:employees', u'facet:name']))
        assert (set(self.db.suggest('employees:joe OR employees:jane',
                                    prefix='facet')) ==
                set([u'facet:employees', u'facet:name']))
        assert (set(self.db.suggest('employees:joe AND employees:jane',
                                    prefix='facet')) ==
                set([u'facet:employees', u'facet:name']))
        assert not set(self.db.suggest('employees:joe AND name:jane',
                                       prefix='facet'))

    def test_getter(self):
        self.db.map(Person, FacetPersonGetterSchema)
        self.db.map(Department, FacetDepartmentSchema)
        o = Person(name="joe")
        a = Person(name="jane")
        self.db.add(o, a)
        assert self.db.query("name:joeha").next().name == 'joeha'

    def test_required(self):
        self.db.map(Person, FacetPersonRequiredSchema)
        o = Person(name="joe")
        assert_raises(xodb.exc.AttributeRequired, self.db.add, o)

    def test_type_required(self):
        self.db.map(Person, FacetPersonTypeRequiredSchema)
        o = Person(name=4)
        assert_raises(xodb.exc.AttributeTypeRequired, self.db.add, o)

    def test_chained_string_text(self):
        self.db.map(Stringer, ChainedStringerNumericerSchema)
        s = Stringer(s='abc', t='once upon a lamb')
        self.db.add(s)
        assert self.db.query("s:abc").next().s == 'abc'
        assert self.db.query("s:a").next().s == 'abc'
        assert self.db.query("s:b").next().s == 'abc'
        assert self.db.query("s:c").next().s == 'abc'
        assert self.db.query("t:once").next().t == 'once upon a lamb'
        doc = self.db.query("t:once", document=True).next()
        assert doc.get_value(self.db.values['s']) == 'abc'
        assert doc.get_value(self.db.values['t']) == 'once upon a lamb'


class TestXapianFile(_TestXapianBase):
    db_factory = staticmethod(xodb.temp)


class TestXapianInMem(_TestXapianBase):
    db_factory = staticmethod(xodb.inmemory)
