import datetime
import weakref
import gc

from xodb import Schema, Attribute

from nose.tools import assert_raises


class Foo(object): 
    def __init__(self, bar=None):
        self.bar = bar


class Bar(object):
    def __init__(self, ding=None):
        self.ding = ding

    def __len__(self):
        return 42


class Ding(object):
    def __init__(self, bar):
        self.bar = bar
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
        self.slat = 'fuzzy'


class DingSchema(Schema):
    bar  = Attribute(type=Bar)
    zig  = Attribute(required=False)
    blig = Attribute(volatile=True)


class Bling(Foo):
    def __new__(cls, blargh):
        inst = super(Bling, cls).__new__(cls)
        inst.blargh = blargh
        return inst

    def __getstate__(self):
        return dict(value='fuzzy')

    def __setstate__(self, state):
        assert state['value'] == 'fuzzy'
        setattr(self, 'bob', 'dinge')

    def __getnewargs__(self):
        return ('yo',)


class FongSchema(Schema):
    pass


class Fern(object):
    __xodb_schema__ = FongSchema


class _BaseTest(object):
    ding_schema = DingSchema

    fong_schema = FongSchema

    def test_bogus_oid(self):
        s = self.db.new_session()
        assert_raises(KeyError, s.get_oid, "foo")

    def test_unmap(self):
        self.db.mapper.unmap(int)
        assert int not in self.db.mapper.type_map

    def test_clear_mapper(self):
        self.db.mapper.clear()
        assert not self.db.mapper.type_map

    def test_add_and_commit(self):
        """Test adding an object and commiting the transaction.. """
        f = Foo()
        s = self.db.new_session()
        s.add(f)
        s.commit()
        assert len(self.db) == 1
        assert f in s

    def test_delete_and_commit(self):
        f = Foo()
        s = self.db.new_session()
        s.add(f)
        s.commit()
        oid = s.get_oid(f)
        assert len(self.db) == 1
        del self.db.backend[oid]
        assert len(self.db) == 0

    def test_add_and_cancel(self):
        """Test adding an object and cancelling the transaction.. """
        f = Foo()
        s = self.db.new_session()
        s.add(f)
        s.cancel()
        assert len(self.db) == 0
        assert f in s

    def test_query_cache_clear_and_gc(self):
        """Test session, make sure cleared objects do not leak. """
        f = Foo()
        s = self.db.new_session()
        s.add(f)
        s.commit()
        foid = s.get_oid(f)
        assert f in s

        results = list(s.query(foid))
        assert len(results) == 1
        assert results[0] is f

        # make sure when a session is cleared that the objects are not
        # leaked
        d = weakref.WeakValueDictionary()
        d['f'] = f
        s.clear()
        del f, results
        gc.collect()

        # the dict is empty, the object is gone
        assert len(d) == 0

        # requery for it
        results = list(s.query(foid))
        assert len(results) == 1
        assert type(results[0]) is Foo

    def test_cache_reference_and_clear(self):
        """ Test reference resolving, before and after session clear. """
        b = Bar()
        f = Foo(b)
        # f, a Foo, now references b, a Bar

        # let's add it to a db
        s = self.db.new_session()
        s.add(f)
        s.commit()

        # there are two documents, let's get their ids
        assert len(self.db) == 2
        foid = s.get_oid(f)
        boid = s.get_oid(b)

        # get f
        results = list(s.query(foid))
        assert len(results) == 1

        # assert it was cached in session, it's the same object
        assert results[0] is f

        # get b
        results = list(s.query(boid))
        assert len(results) == 1

        # assert it was cached in session
        assert results[0] is b

        # now let's clear this session
        s.clear()

        # get f again, check it's type
        results = list(s.query(foid))
        assert len(results) == 1
        f2 = results[0]
        assert type(f2) is Foo

        # since we cleared the session, the new object is not the same as
        # before
        assert f2 is not f

        # get b again, same story with it
        results = list(s.query(boid))
        assert len(results) == 1
        b2 = results[0]
        assert type(b2) is Bar
        assert b2 is not b

        # f2.bar is a ghost, let's make a local reference to it so we
        # don't loose it.
        d = f2.bar
        # make sure it really is a ghost
        assert type(d) is Ghost
        # ghosts are not in a session
        assert d not in s
        # taking the len loads the real object into f2 (doesn't change d!)
        assert len(f2.bar) == 42
        # now the ghost is not longer f2.bar (still d though)
        assert type(f2.bar) is Bar
        # bar can be traversed
        assert f2.bar.ding is None
        # the object hasn't changed
        assert b2 is f2.bar

        # now let's try to setattr on the ghost
        d.zig = 3
        # make sure it's set
        assert d.zig == 3
        # on the real object too
        assert f2.bar.zig == 3
        # make sure we can del it
        del d.zig
        assert not hasattr(d, 'zig')
        # on the real object too
        assert not hasattr(f2.bar, 'zig')
        # make sure we're still working with a ghost after all that
        assert type(d) is Ghost

    def test_required_attribute(self):
        """ Test an error is raised in a required schema attribute is missing. """
        s = self.db.new_session()
        self.db.mapper.map(Ding, self.ding_schema)
        d = Ding(Bar())
        del d.bar
        s.add(d)
        assert_raises(TypeError, s.commit)

    def test_volatile_attribute(self):
        s = self.db.new_session()
        self.db.mapper.map(Ding, self.ding_schema)
        d = Ding(Bar())
        assert hasattr(d, 'blig')
        s.add(d)
        s.commit()
        doid = s.get_oid(d)
        results = list(s.query(doid))
        assert results[0] is d
        s.clear()
        results = list(s.query(doid))
        assert not hasattr(results[0], 'blig')

    def test_changed_object(self):
        d = Ding(Bar())
        self.db.mapper.map(Ding, self.ding_schema)
        s = self.db.new_session()
        s.add(d)
        s.commit()
        doid = s.get_oid(d)
        s.clear()
        d = s.query(doid).next()

        d.blig = 1
        d.bloog = 1
        s.commit()
        s.clear()
        d = s.query(doid).next()
        assert not hasattr(d, 'blig')
        assert d.bloog == 42

        d.blig = 1
        d.bloog = 1
        s.changed(d)
        d.canary = [] # ewww
        s.commit()
        s.clear()
        d = s.query(doid).next()
        assert not hasattr(d, 'blig')
        assert d.bloog == 1

    def test_pickle_protocol(self):
        """Test __getstate__, __setstate__, and __getnewargs__ """
        d = Bling('flerg')
        assert d.blargh == 'flerg'
        s = self.db.new_session()
        s.add(d)
        s.commit()
        doid = s.get_oid(d)
        s.clear()
        d = s.query(doid).next()
        assert d.bob == 'dinge'
        assert d.blargh == 'yo'

    def test_persistent_add_and_commit(self):
        f = Foop(a="42", b=42, c=Foop(z=1))
        assert f._p_status is persistent.UNSAVED
        s = self.db.new_session()
        s.add(f)
        s.commit()
        assert len(self.db) == 2
        assert f in s
        assert f._p_status is persistent.SAVED
        foid = s.get_oid(f)
        s.clear()
        f = s.query(foid).next()
        assert f._p_status is persistent.GHOST
        assert f.a == "42"
        assert f._p_status is persistent.SAVED

        assert f.c._p_status is persistent.GHOST
        assert f.c.z == 1
        assert f.c._p_status is persistent.SAVED

    def test_persistent_changed(self):
        f = Foop(a="42", b=42, c=Foop(z=1))
        s = self.db.new_session()
        s.add(f)
        s.commit()
        foid = s.get_oid(f)
        s.clear()
        f = s.query(foid).next()
        assert f._p_status is persistent.GHOST
        del f.a
        assert f._p_status is persistent.UNSAVED
        assert not hasattr(f, 'a')
        s.commit()
        s.clear()
        f = s.query(foid).next()
        assert f._p_status is persistent.GHOST
        assert not hasattr(f, 'a')
        assert f._p_status is persistent.SAVED
        s.clear()
        f = s.query(foid).next()
        assert f._p_status is persistent.GHOST
        f.a = 43
        assert f._p_status is persistent.UNSAVED
        s.commit()
        assert f._p_status is persistent.SAVED
        s.clear()
        f = s.query(foid).next()
        assert f._p_status is persistent.GHOST
        assert hasattr(f, 'a')
        assert f.a == 43
        assert f._p_status is persistent.SAVED

    def test_declared_schema(self):
        d = Ding(Bar())
        self.db.mapper.map(Ding, self.declared_ding_schema)
        s = self.db.new_session()
        s.add(d)
        s.commit()
        doid = s.get_oid(d)
        s.clear()
        d = s.query(doid).next()
        assert hasattr(d, 'bar')
        assert type(d.bar) is Ghost
        assert type(d.bloog) is int
        assert d.bloog == 42
        assert not hasattr(d, 'blig')
        
    def test_explicit_class_schema(self):
        canary = []
        fong_schema = self.fong_schema
        def monkey(self, session):
            canary.append(session)
            super(fong_schema, self).__init__(session)
        fong_schema.__init__ = monkey
        Fern.__xodb_schema__ = fong_schema
        f = Fern()
        s = self.db.new_session()
        s.add(f)
        s.commit()
        assert canary[0] is s
