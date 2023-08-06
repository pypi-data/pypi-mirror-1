from functools import wraps


def trace(f):
    @wraps(f)
    def wrapper(*args, **kw):
        print "calling %s with args %s, %s" % (f.__name__, args, kw)
        return f(*args, **kw)
    return wrapper


