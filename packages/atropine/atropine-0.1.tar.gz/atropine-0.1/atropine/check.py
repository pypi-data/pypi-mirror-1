from common import CannotResolve, all
from BeautifulSoup import Null

# it is really not useful at all to include the null object pattern
# as an integral part of your external api.

def equal(actual, expected):
    if actual is Null:
        return False

    if hasattr(expected, '__iter__'):
        return actual in expected
    else:
        return actual == expected

def nchildren(atropine, n):
    return len(atropine.current.contents) == n

def tagattributes(atropine, attrs):
    return all(atropine.current._matches(atropine.current.get(k), v)
                    for (k, v) in attrs.iteritems())

def allchildren(atropine, f):
    return all(f(node) for node in atropine.current.contents)

def tagattribute(name):
    def _dotagattribute(atropine, expected):
        try:
            value = atropine.current[name]
        except KeyError:
            raise CannotResolve()
        return equal(value, expected)
    return _dotagattribute

def soupattribute(name):
    def _dosoupattribute(atropine, expected):
        value = getattr(atropine.current, name, None)
        return equal(value, expected)
    return _dosoupattribute

def indexonparent(atropine, n):
    index = atropine.current.parent.contents.index(atropine.current)
    return equal(index, n)

def onlytext(atropine, something):
    return (len(atropine.current.contents) == 1
                and atropine.istextnode(atropine.current.contents[0])
                and atropine.current._matches(atropine.current.contents, something))

def alltext(atropine, something):
    return all(atropine.current._matches([chunk], something)
                for chunk in atropine.current.recursiveChildGenerator()
                    if atropine.istextnode(chunk))

def has(**k):
    def _dohas(atropine):
        for (checkername, constraints) in k.iteritems():
            if not atropine.getchecker(checkername)(atropine, constraints):
                raise CannotResolve()
        return atropine
    return _dohas

def doesnthave(**k):
    def _dodoesnthave(atropine):
        for (checkername, constraints) in k.iteritems():
            if atropine.getchecker(checkername)(atropine, constraints):
                raise CannotResolve()
        return atropine
    return _dodoesnthave
