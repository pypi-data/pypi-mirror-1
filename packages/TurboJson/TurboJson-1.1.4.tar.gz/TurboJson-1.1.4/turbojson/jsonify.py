"""JSON encoding functions using RuleDispatch."""

import datetime

try:
    import decimal
except ImportError: # Python 2.3
    decimal = None

import dispatch
from simplejson import JSONEncoder
from turbojson.prioritized_methods import PriorityDisambiguated

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


# Global options

descent_bases = True


# Specific encoding functions

def jsonify(obj):
    """Generic function for converting objects to JSON.

    Specific functions should return a string or an object that can be
    serialized with JSON, i.e., it is made up of only lists, dictionaries
    (with string keys), and strings, ints, and floats.

    """
    raise NotImplementedError
jsonify = dispatch.generic(PriorityDisambiguated)(jsonify)


def jsonify_datetime(obj):
    """JSONify datetime and date objects."""
    return str(obj)
jsonify_datetime = jsonify.when(
        "isinstance(obj, (datetime.datetime, datetime.date))", prio=-1)(
    jsonify_datetime)


def jsonify_decimal(obj):
    """JSONify decimal objects."""
    return float(obj)
if decimal:
    jsonify_decimal = jsonify.when(
        "isinstance(obj, decimal.Decimal)", prio=-1)(jsonify_decimal)


def jsonify_explicit(obj):
    """JSONify objects with explicit JSONification method."""
    return obj.__json__()
jsonify_explicit = jsonify.when(
    "hasattr(obj, '__json__')", prio=-1)(jsonify_explicit)


# SQLObject support

try:
    from sqlobject import SQLObject

    def is_sqlobject(obj):
        return (isinstance(obj, SQLObject)
            and hasattr(obj.__class__, 'sqlmeta'))

    def jsonify_sqlobject(obj):
        """JSONify SQLObjects."""
        result = {}
        result['id'] = obj.id
        keys = []
        sm = obj.__class__.sqlmeta
        try:
            while sm is not None:
                # we need to exclude the ID-keys, as for some reason
                # this won't work for subclassed items
                keys.extend([key
                    for key in sm.columns.keys() if key[-2:] != 'ID'])
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
            "is_sqlobject(obj) and not hasattr(obj, '__json__')", prio=-1)(
        jsonify_sqlobject)

    try:
        SelectResultsClass = SQLObject.SelectResultsClass
    except AttributeError:
        pass
    else:

        def jsonify_select_results(obj):
            """JSONify SQLObject.SelectResults."""
            return list(obj)
        jsonify_select_results = jsonify.when(
                "isinstance(obj, SelectResultsClass)", prio=-1)(
            jsonify_select_results)

except ImportError:
    pass


# SQLAlchemy support

try:
    import sqlalchemy

    try:
        import sqlalchemy.ext.selectresults
        from sqlalchemy.util import OrderedProperties
    except ImportError: # SQLAlchemy >= 0.5

        def is_saobject(obj):
            return hasattr(obj, '_sa_class_manager')

        def jsonify_saobject(obj):
            """JSONify SQLAlchemy objects."""
            props = {}
            for key in obj.__dict__:
                if not key.startswith('_sa_'):
                    props[key] = getattr(obj, key)
            return props
        jsonify_saobject = jsonify.when(
                "is_saobject(obj) and not hasattr(obj, '__json__')", prio=-1)(
            jsonify_saobject)

    else: # SQLAlchemy < 0.5

        def is_saobject(obj):
            return (hasattr(obj, 'c')
                and isinstance(obj.c, OrderedProperties))

        def jsonify_saobject(obj):
            """JSONify SQLAlchemy objects."""
            props = {}
            for key in obj.c.keys():
                props[key] = getattr(obj, key)
            return props
        jsonify_saobject = jsonify.when(
                "is_saobject(obj) and not hasattr(obj, '__json__')", prio=-1)(
            jsonify_saobject)

        try:
            from sqlalchemy.orm.attributes import InstrumentedList
        except ImportError: # SQLAlchemy >= 0.4
            pass # normal lists are used here

        else: # SQLAlchemy < 0.4

            def jsonify_instrumented_list(obj):
                """JSONify SQLAlchemy instrumented lists."""
                return list(obj)
            jsonify_instrumented_list = jsonify.when(
                    "isinstance(obj, InstrumentedList)", prio=-1)(
                jsonify_instrumented_list)

except ImportError:
    pass


# JSON Encoder class

class GenericJSON(JSONEncoder):

    def __init__(self, **opts):
        opt = opts.pop('descent_bases', None)
        if opt is not None:
            global descent_bases
            descent_bases = opt
        super(GenericJSON, self).__init__(**opts)

    def default(self, obj):
        return jsonify(obj)

_instance = GenericJSON()


# General encoding functions

def encode(obj):
    """Return a JSON string representation of a Python object."""
    return _instance.encode(obj)

def encode_iter(obj):
    """Encode object, yielding each string representation as available."""
    return _instance.iterencode(obj)
