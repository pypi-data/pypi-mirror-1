from turbojson import jsonify


class Foo(object):
    def __init__(self, bar):
        self.bar = bar

def jsonify_foo(obj):
    return "foo-%s" % obj.bar
jsonify_foo = jsonify.jsonify.when("isinstance(obj, Foo)")(jsonify_foo)

def test_dictionary():
    d = {'a':1, 'b':2}
    encoded = jsonify.encode(d)
    print encoded
    assert encoded == '{"a": 1, "b": 2}'

def test_specificjson():
    a = Foo("baz")
    encoded = jsonify.encode(a)
    print encoded
    assert encoded == '"foo-baz"'

def test_specific_in_dict():
    a = Foo("baz")
    d = {"a":a}
    encoded = jsonify.encode(d)
    print encoded
    assert encoded == '{"a": "foo-baz"}'
    

def test_so():
    try:
        import sqlobject as so
        import pysqlite2
        from sqlobject.inheritance import InheritableSQLObject
    except ImportError:
        return
    so.sqlhub.processConnection = so.connectionForURI('sqlite:/:memory:')
    class Person(so.SQLObject):
        fname = so.StringCol()
        mi = so.StringCol(length=1, default=None)
        lname = so.StringCol()
    Person.createTable()
    p = Person(fname="Peter", mi="P", lname="Pasulke")
    pj = jsonify.jsonify(p)
    assert pj == {'fname' : "Peter", 'mi' : "P", 'lname' : "Pasulke", 'id' : 1}
    class A(InheritableSQLObject):
        foo = so.StringCol()

    A.createTable()
    class B(A):
        bar = so.StringCol()

    B.createTable()

    
    b = B(foo="foo", bar="bar")
    bj = jsonify.jsonify(b)
    print bj
    assert bj == {'foo' : "foo", 'bar' : "bar", 'id' : b.id, 'childName' : None}


