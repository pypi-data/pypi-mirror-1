# Using PEAK-Rules:

import datetime
import decimal

from peak.rules import abstract, when

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


@abstract()
def jsonify(obj):
    """Generic function for converting objects to JSON.

    Specific functions should return a string or an object that can be
    serialized with JSON, i.e., it is made up of only lists, dictionaries
    (with string keys), and strings, ints, and floats.

    """
    raise NotImplementedError

# This is for easier usage and backward compatibility:
jsonify.when = lambda *args, **kwargs: when(jsonify, *args, **kwargs)


@jsonify.when("isinstance(obj, (datetime.date, datetime.datetime))")
def jsonify_datetime(obj):
    """JSONify datetime and date objects."""
    return str(obj)

@jsonify.when("isinstance(obj, decimal.Decimal)")
def jsonify_decimal(obj):
    """JSONify decimal objects."""
    return float(obj)

@jsonify.when("hasattr(obj, '__json__')")
def jsonify_explicit(obj):
    """JSONify objects with explicit JSONification method."""
    return obj.__json__()


# SQLObject support
try:
    from sqlobject import SQLObject

    def _sqlobject_attrs(obj, descent_bases=[]):
        """Get all attributes of an SQLObject."""
        if not descent_bases:
            descent_bases.append(config.get('turbojson.descent_bases', True))
        descent_bases = descent_bases[0]
        sm = obj.__class__.sqlmeta
        try:
            while sm is not None:
                # we need to exclude the ID-keys, as for some reason
                # this won't work for subclassed items
                for key in sm.columns:
                    if key[-2:] != 'ID':
                        yield key
                sm = descent_bases and sm.__base__ or None
        except AttributeError: # happens if we descent to <type object>
            pass

    def is_sqlobject(obj):
        return (isinstance(obj, SQLObject)
            and hasattr(obj.__class__, 'sqlmeta'))

    @jsonify.when("is_sqlobject(obj)"
        " and not hasattr(obj, '__json__')")
    def jsonify_sqlobject(obj):
        """JSONify SQLObjects."""
        result = {'id': obj.id}
        for name in _sqlobject_attrs(obj):
            result[name] = getattr(obj, name)
        return result

    try:
        SelectResultsClass = SQLObject.SelectResultsClass
    except AttributeError:
        pass
    else:

        @jsonify.when("isinstance(obj, SelectResultsClass)")
        def jsonify_select_results(obj):
            """JSONify SQLObject.SelectResults."""
            return list(obj)

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

        @jsonify.when("is_saobject(obj)"
            " and not hasattr(obj, '__json__')")
        def jsonify_saobject(obj):
            """JSONify SQLAlchemy objects."""
            props = {}
            for key in obj.__dict__:
                if not key.startswith('_sa_'):
                    props[key] = getattr(obj, key)
            return props

    else: # SQLAlchemy < 0.5

        def is_saobject(obj):
            return (hasattr(obj, 'c')
                and isinstance(obj.c, OrderedProperties))

        @jsonify.when("is_saobject(obj)"
            " and not hasattr(obj, '__json__')")
        def jsonify_saobject(obj):
            """JSONify SQLAlchemy objects."""
            props = {}
            for key in obj.c.keys():
                props[key] = getattr(obj, key)
            return props

        try:
            from sqlalchemy.orm.attributes import InstrumentedList
        except ImportError: # SQLAlchemy >= 0.4
            pass # normal lists are used here

        else: # SQLAlchemy < 0.4

            @jsonify.when("isinstance(obj, InstrumentedList)")
            def jsonify_instrumented_list(obj):
                """JSONify SQLAlchemy instrumented lists."""
                return list(obj)

except ImportError:
    pass


class GenericJSON(JSONEncoder):

    def default(self, obj):
        return jsonify(obj)

_instance = GenericJSON()

def encode(obj):
    """Return a JSON string representation of a Python object."""
    return _instance.encode(obj)

def encode_iter(obj):
    """Encode object, yielding each string representation as available."""
    return _instance.iterencode(obj)
