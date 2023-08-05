"""Various classes and functions to provide some backwards-compatibility with
previous versions of Python prior to 2.4.

Taken from
http://trac.edgewall.org/browser/trunk/trac/util/compat.py
Thanks.
"""

try:
    sorted = sorted
except NameError:
    def sorted(iterable, cmp=None, key=None, reverse=False):
        """Partial implementation of the "sorted" function from Python 2.4"""
        if key is None:
            lst = list(iterable)
        else:
            lst = [(key(val), idx, val) for idx, val in enumerate(iterable)]
        lst.sort()
        if key is None:
            if reverse:
                return lst[::-1]
            return lst
        if reverse:
            lst = reversed(lst)
        return [i[-1] for i in lst]

try:
    from operator import attrgetter, itemgetter
except ImportError:
    def attrgetter(name):
        def _getattr(obj):
            return getattr(obj, name)
        return _getattr
    def itemgetter(name):
        def _getitem(obj):
            return obj[name]
        return _getitem
