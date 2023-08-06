import xodb
from xodb import Schema, Attribute


class A(object):
    def __init__(self, **kw):
        for k,v in kw.items():
            setattr(self, k, v)


class B(A):
    pass


class AS(Schema):
    id = Attribute()
    bone = Attribute(required=False)
    slow = Attribute()


class BS(AS):
    fod = Attribute()
    bone = Attribute()


def test_basic_inheritance():
    assert issubclass(BS, AS)
    assert not issubclass(AS, BS)
    assert AS.__attributes__['bone'].required is False
    assert AS.bone.required is False
    assert BS.__attributes__['bone'].required is True
    assert BS.bone.required is True
    assert 'id' in BS.__attributes__
    assert hasattr(BS, 'id')
    assert 'fod' not in AS.__attributes__
    assert not hasattr(AS, 'fod')

