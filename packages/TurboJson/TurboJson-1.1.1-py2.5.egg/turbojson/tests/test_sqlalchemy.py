from turbojson import jsonify

try:
    from sqlalchemy import *
    from sqlalchemy.orm import *
    gotsa = True
    
    metadata = MetaData('sqlite:///:memory:')
    test1 = Table('test1', metadata, 
            Column('id', Integer, primary_key=True),
            Column('val', String))

    test2 = Table('test2', metadata, 
            Column('id', Integer, primary_key=True),
            Column('test1id', Integer, ForeignKey('test1.id')),
            Column('val', String))
    metadata.create_all()
    
    class Test2(object):
        pass
    mapper(Test2, test2)

    class Test1(object):
        pass
    mapper(Test1, test1, properties={'test2s':relation(Test2)})

    test1.insert().execute({'id':1, 'val':'bob'})    
    test2.insert().execute({'id':1, 'test1id':1, 'val':'fred'})
    test2.insert().execute({'id':2, 'test1id':1, 'val':'alice'})
    
except ImportError:
    gotsa = False


def test_saobj():
    if not gotsa:
        return    
    s = create_session()
    t = s.query(Test1).get(1)
    encoded = jsonify.encode(t)
    assert encoded == '{"id": 1, "val": "bob"}'
    
def test_salist():
    if not gotsa:
        return    
    s = create_session()
    t = s.query(Test1).get(1)
    encoded = jsonify.encode(t.test2s)
    print encoded
    assert encoded == '[{"test1id": 1, "id": 1, "val": "fred"}, {"test1id": 1, "id": 2, "val": "alice"}]'
    
    