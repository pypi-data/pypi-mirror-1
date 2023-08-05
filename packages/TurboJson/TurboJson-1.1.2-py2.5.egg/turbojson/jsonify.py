# Using RuleDispatch:

import datetime

import dispatch
from simplejson import JSONEncoder

try:
    from turbogears import config
except ImportError:
    class config(object):
        _default = object()
        def get(cls, key, default=_default):
            if default is cls._default:
                raise KeyError(key)
            return default
        get = classmethod(get)

try:
    import decimal
except ImportError:
    # Python 2.3
    decimal = None

def jsonify(obj):
    """
    Return an object that can be serialized with JSON, i.e., it
    is made up of only lists, dictionaries (with string keys),
    and strings, ints, and floats.
    """
    raise NotImplementedError
jsonify = dispatch.generic()(jsonify)

def jsonify_datetime(obj):
	return str(obj)
jsonify_datetime = jsonify.when(
        'isinstance(obj, datetime.datetime) or '
        'isinstance(obj, datetime.date)')(jsonify_datetime)

def jsonify_decimal(obj):
    return float(obj)
if decimal is not None:
    jsonify_decimal = jsonify.when('isinstance(obj, decimal.Decimal)')(
        jsonify_decimal)

def jsonify_explicit(obj):
    return obj.__json__()
jsonify_explicit = jsonify.when('hasattr(obj, "__json__")')(jsonify_explicit)

# SQLObject support
try:
    import sqlobject

    def jsonify_sqlobject(obj, descent_bases=[]):
        if not descent_bases:
            descent_bases.append(config.get('turbojson.descent_bases', True))
        descent_bases = descent_bases[0]
        result = {}
        result['id'] = obj.id
        keys = []
        sm = obj.__class__.sqlmeta
        try:
            while sm is not None:
                # we need to exclude the ID-keys, as for some reason
                # this won't work for subclassed items
                keys.extend([key for key in sm.columns.keys() if key[-2:] != 'ID'])
                if descent_bases:
                    sm = sm.__base__
                else:
                    sm = None
        except AttributeError:
            # this happens if we descent to <type object>
            pass
        for name in keys:
            result[name] = getattr(obj, name)
        return result
    jsonify_sqlobject = jsonify.when(
            'isinstance(obj, sqlobject.SQLObject)')(jsonify_sqlobject)

    def jsonify_select_results(obj):
        return list(obj)
    jsonify_select_results = jsonify.when(
            'isinstance(obj, sqlobject.SQLObject.SelectResultsClass)')(
                    jsonify_select_results)
except ImportError:
    pass

# SQLAlchemy support
try:
    import sqlalchemy

    def jsonify_saobject(obj):
       props = {}
       for key in obj.c.keys():
           props[key] = getattr(obj, key)
       return props
    jsonify_saobject = jsonify.when(
            "hasattr(obj, 'c') and isinstance(obj.c,sqlalchemy.util.OrderedProperties)")(jsonify_saobject)

except ImportError:
    pass


class GenericJSON(JSONEncoder):

    def default(self, obj):
        return jsonify(obj)

_instance = GenericJSON()

def encode_iter(obj):
    return _instance.iterencode(obj)

def encode(obj):
    return _instance.encode(obj)
