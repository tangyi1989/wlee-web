
import json
import inspect
import itertools
import datetime
import xmlrpclib
import traceback

def help():
    content = "If you are the first time use this, please modify"
    "settings in this project and good luck!"
    
    print content


def to_primitive(value, convert_instances=False, level=0):
    """Convert a complex object into primitives.

    Handy for JSON serialization. We can optionally handle instances,
    but since this is a recursive function, we could have cyclical
    data structures.

    To handle cyclical data structures we could track the actual objects
    visited in a set, but not all objects are hashable. Instead we just
    track the depth of the object inspections and don't go too deep.

    Therefore, convert_instances=True is lossy ... be aware.

    """
    nasty = [inspect.ismodule, inspect.isclass, inspect.ismethod,
             inspect.isfunction, inspect.isgeneratorfunction,
             inspect.isgenerator, inspect.istraceback, inspect.isframe,
             inspect.iscode, inspect.isbuiltin, inspect.isroutine,
             inspect.isabstract]
    for test in nasty:
        if test(value):
            return unicode(value)

    # value of itertools.count doesn't get caught by inspects
    # above and results in infinite loop when list(value) is called.
    if type(value) == itertools.count:
        return unicode(value)

    # FIXME(vish): Workaround for LP bug 852095. Without this workaround,
    #              tests that raise an exception in a mocked method that
    #              has a @wrap_exception with a notifier will fail. If
    #              we up the dependency to 0.5.4 (when it is released) we
    #              can remove this workaround.
    if getattr(value, '__module__', None) == 'mox':
        return 'mock'

    if level > 3:
        return '?'

    # The try block may not be necessary after the class check above,
    # but just in case ...
    try:
        # It's not clear why xmlrpclib created their own DateTime type, but
        # for our purposes, make it a datetime type which is explicitly
        # handled
        if isinstance(value, xmlrpclib.DateTime):
            value = datetime.datetime(*tuple(value.timetuple())[:6])

        if isinstance(value, (list, tuple)):
            o = []
            for v in value:
                o.append(to_primitive(v, convert_instances=convert_instances,
                                      level=level))
            return o
        elif isinstance(value, dict):
            o = {}
            for k, v in value.iteritems():
                o[k] = to_primitive(v, convert_instances=convert_instances,
                                    level=level)
            return o
        elif isinstance(value, datetime.datetime):
            return timeutils.strtime(value)
        elif hasattr(value, 'iteritems'):
            return to_primitive(dict(value.iteritems()),
                                convert_instances=convert_instances,
                                level=level + 1)
        elif hasattr(value, '__iter__'):
            return to_primitive(list(value),
                                convert_instances=convert_instances,
                                level=level)
        elif convert_instances and hasattr(value, '__dict__'):
            # Likely an instance of something. Watch for cycles.
            # Ignore class member vars.
            return to_primitive(value.__dict__,
                                convert_instances=convert_instances,
                                level=level + 1)
        else:
            return value
    except TypeError:
        # Class objects are tricky since they may define something like
        # __iter__ defined but it isn't callable as list().
        return unicode(value)
    
def json_dumps(value, default=to_primitive, **kwargs):
    return json.dumps(value, default=default, **kwargs)

def json_loads(s):
    return json.loads(s)

def debug(func):
    """
    A decorator used to debug a function
    """
    def invoke_with_debug(*args, **kargs):
        
        print ""
        print "Invoking Function : %s.%s" % (func.__module__, func.__name__) 
        print "With args : %s kargs : %s" % (to_primitive(args), 
                                             to_primitive(kargs))
        try:
            ret = func(*args, **kargs)
        except Exception as e:
            print "Caught exception : %s" % str(e)
            print traceback.format_exc()
            raise e
        print "Function returns : %s" % to_primitive(ret)
        print ""
        return ret
    
    return invoke_with_debug
