import cPickle as pickle
import datetime
from xodb.spies import *
import xodb
from xapian import Document
from xodb import Attribute, Schema

class AS(Schema):
    id = Attribute()
    bone = Attribute(value=True)
    wall = Attribute(value=True)
    seq = Attribute(value=True, sequence=True)


def test_value_spy():
    N = 15
    db = xodb.inmemory()
    ctr = SchemaValueCountMatchSpy(AS, db)

    valnos = dict((a.name, db.add_value(a.name)) for a in (AS.bone, AS.wall, AS.seq))

    words = ('foo', 'bar', 'baz', 'zoom')
    for i in range(N):
        doc = Document()
        doc.add_value(valnos['bone'], pickle.dumps('blong'))
        doc.add_value(valnos['wall'], pickle.dumps(words[i % len(words)]))
        ctr(doc)

    assert 'blong' in ctr.values['bone']
    assert ctr.values['bone']['blong'] == N
    assert ('blong', 15) in ctr.top_values('bone')

    for word in words:
        assert word in ctr.values['wall']

    assert ctr.values['wall']['foo'] == 4
    assert ctr.values['wall']['zoom'] == 3

    assert len(ctr.top_values('wall', 3)) == 3
    assert 'zoom' not in dict(ctr.top_values('wall', 3))

    assert ('zoom', 3) in ctr.top_values('wall')
    assert ('bar', 4) in ctr.top_values('wall')

def test_value_spy_multi():
    db = xodb.inmemory()
    ctr = SchemaValueCountMatchSpy(AS, db)

    valnos = dict((a.name, db.add_value(a.name)) for a in (AS.bone, AS.wall, AS.seq))

    words = ('foo', 'bar', 'baz', 'zoom')
    for i in range(len(words)+1):
        doc = Document()
        value = pickle.dumps(words[:i])
        doc.add_value(valnos['seq'], value)
        ctr(doc)

    for word in words:
        assert word in ctr.values['seq']

    assert ctr.values['seq']['foo'] == 4
    assert ctr.values['seq']['zoom'] == 1

    assert ctr.top_values('seq') == [('foo', 4), ('bar', 3), ('baz', 2), ('zoom', 1)]

def test_category_spy_exact():
    db = xodb.inmemory()
    ctr = SchemaValueCountMatchSpy(AS, db)

    valnos = dict((a.name, db.add_value(a.name)) for a in (AS.bone, AS.wall, AS.seq))

    words = ('foo', 'bar', 'baz', 'zoom')
    for i in range(len(words)):
        doc = Document()
        value = pickle.dumps(words[i])
        doc.add_value(valnos['bone'], value)
        ctr(doc)

    assert ctr.score_categorization('bone') == 0.0
    assert ctr.score_categorization('bone',4) == 0.0
    assert ctr.score_categorization('bone',3) > 0.0

def test_category_spy_approx():
    db = xodb.inmemory()
    ctr = SchemaValueCountMatchSpy(AS, db)

    valnos = dict((a.name, db.add_value(a.name)) for a in (AS.bone, AS.wall, AS.seq))

    words = ('foo', 'bar', 'baz', 'zoom')
    doc = Document()
    value = pickle.dumps(words)
    doc.add_value(valnos['seq'], value)
    ctr(doc)

    assert ctr.score_categorization('seq',4) < ctr.score_categorization('seq',5)
    assert ctr.score_categorization('seq',4) < ctr.score_categorization('seq',3)

def test_category_numeric_ranges():
    db = xodb.inmemory()
    ctr = SchemaValueCountMatchSpy(AS, db)

    valnos = dict((a.name, db.add_value(a.name)) for a in (AS.bone, AS.wall, AS.seq))

    values = (1.0, 2.0, 3.0, 3.3, 3.6, 3.9, 4.0, 5.0)
    for i in range(len(values)):
        doc = Document()
        value = pickle.dumps(unicode(values[i]))
        doc.add_value(valnos['bone'], value)
        ctr(doc)

    assert ctr.build_numeric_ranges('bone', 0) == []

    for N in range(1,len(values)+1):
        buckets = ctr.build_numeric_ranges('bone', N)
        assert len(buckets) == N
        assert buckets[0][0] == values[0]
        assert buckets[-1][1] == values[-1]


def test_quantized_numeric_ranges():
    db = xodb.inmemory()
    ctr = SchemaValueCountMatchSpy(AS, db)

    valnos = dict((a.name, db.add_value(a.name)) for a in (AS.bone, AS.wall, AS.seq))

    values = (10.0, 12.0, 13.0, 15.0, 16.0, 19.0, 23.0, 36.0)
    for i in range(len(values)):
        doc = Document()
        value = pickle.dumps(unicode(values[i]))
        doc.add_value(valnos['bone'], value)
        ctr(doc)

    assert ctr.build_numeric_ranges('bone', 0) == []
    assert ctr.build_numeric_ranges('bone', 2, 5.0) == [(10.0, 25.0), (25.0, 40.0)]
    assert ctr.build_numeric_ranges('bone', 3, 5.0) == [(10.0, 20.0), (20.0, 30.0), (30.0, 40.0)]
    assert ctr.build_numeric_ranges('bone', 7, 5.0) == [
        (10.0, 15.0), (15.0, 20.0), (20.0, 25.0), (25.0, 30.0), (30.0, 35.0), (35.0, 40.0)]

    assert ctr.build_numeric_ranges('bone', 2, 10.0) == [(10.0, 20.0), (20.0, 40.0)]


def test_date_ranges():
    db = xodb.inmemory()
    ctr = SchemaValueCountMatchSpy(AS, db)

    ranges = ctr.build_date_ranges(from_date=datetime.date(2009, 1, 1))
    assert ranges == [
             ('20090101', '20090101', 'today'),
             ('20081231', '20081231', 'yesterday'),
             ('20081230', '20081225', 'past week'),
             ('20090101', '20090131', 'January 2009'),
             ('20081201', '20081231', 'December 2008'),
             ('20081101', '20081130', 'November 2008'),
             ('20081001', '20081031', 'October 2008'),
             ('20080901', '20080930', 'September 2008'),
             ('20080801', '20080831', 'August 2008'),
             ('20080701', '20080731', 'July 2008'),
             ('20080601', '20080630', 'June 2008'),
             ('20080501', '20080531', 'May 2008'),
             ('20080401', '20080430', 'April 2008'),
             ('20080301', '20080331', 'March 2008'),
             ('20080201', '20080229', 'February 2008')]

    ranges = ctr.build_date_ranges(future=True, from_date=datetime.date(2009, 1, 1))
    assert ranges == [
             ('20090101', '20090101', 'today'),
             ('20090102', '20090102', 'tomorrow'),
             ('20090103', '20090108', 'this week'),
             ('20090101', '20090131', 'January 2009'),
             ('20090201', '20090228', 'February 2009'),
             ('20090301', '20090331', 'March 2009'),
             ('20090401', '20090430', 'April 2009'),
             ('20090501', '20090531', 'May 2009'),
             ('20090601', '20090630', 'June 2009'),
             ('20090701', '20090731', 'July 2009'),
             ('20090801', '20090831', 'August 2009'),
             ('20090901', '20090930', 'September 2009'),
             ('20091001', '20091031', 'October 2009'),
             ('20091101', '20091130', 'November 2009'),
             ('20091201', '20091231', 'December 2009')]

