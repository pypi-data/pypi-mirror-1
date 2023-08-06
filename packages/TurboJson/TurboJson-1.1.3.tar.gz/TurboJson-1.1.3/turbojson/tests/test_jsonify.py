from turbojson import jsonify


class Foo(object):
    def __init__(self, bar):
        self.bar = bar

class Bar(object):
    def __init__(self, bar):
        self.bar = bar
    def __json__(self):
        return 'bar-%s' % self.bar

class Baz(object):
    pass


def jsonify_foo(obj):
    return "foo-%s" % obj.bar
jsonify_foo = jsonify.jsonify.when("isinstance(obj, Foo)")(jsonify_foo)


def test_list():
    d = ['a', 1, 'b', 2]
    encoded = jsonify.encode(d)
    assert encoded == '["a", 1, "b", 2]'

def test_list_iter():
    d = range(3)
    encoded = jsonify.encode_iter(d)
    assert ''.join(jsonify.encode_iter(d)) == jsonify.encode(d)

def test_dictionary():
    d = {'a': 1, 'b': 2}
    encoded = jsonify.encode(d)
    assert encoded == '{"a": 1, "b": 2}'

def test_specificjson():
    a = Foo("baz")
    encoded = jsonify.encode(a)
    assert encoded == '"foo-baz"'

def test_specific_in_list():
    a = Foo("baz")
    d = [a]
    encoded = jsonify.encode(d)
    assert encoded == '["foo-baz"]'

def test_specific_in_dict():
    a = Foo("baz")
    d = {"a": a}
    encoded = jsonify.encode(d)
    assert encoded == '{"a": "foo-baz"}'

def test_nospecificjson():
    b = Baz()
    try:
        encoded = jsonify.encode(b)
    except Exception, e:
        encoded = e.__class__.__name__
    assert encoded == 'NoApplicableMethods'

def test_exlicitjson():
    b = Bar("bq")
    encoded = jsonify.encode(b)
    assert encoded == '"bar-bq"'

def test_exlicitjson_in_list():
    b = Bar("bq")
    d = [b]
    encoded = jsonify.encode(d)
    assert encoded == '["bar-bq"]'

def test_exlicitjson_in_dict():
    b = Bar("bq")
    d = {"b": b}
    encoded = jsonify.encode(d)
    assert encoded == '{"b": "bar-bq"}'
