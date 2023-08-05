from common import CannotResolve

def parent(n):
    def _do(atropine):
        current = atropine.current
        for i in xrange(n+1):
            current = current.parent
        atropine.assimilate(current)
    return _do

def child(n):
    def _do(atropine):
        if len(atropine.current.contents) < n+1:
            raise CannotResolve()
        atropine.assimilate(atropine.current.contents[n])
    return _do

def only(**k):
    def _do(atropine):
        try:
            (tag,) = atropine.find(**k)
        except ValueError:
            raise CannotResolve()
        atropine.assimilate(tag)
    return _do

def nth(n, **k):
    def _do(atropine):
        results = atropine.find(**k)
        if len(results)-1 < n:
            raise CannotResolve()
        atropine.assimilate(results[n])
    return _do

def first(**k):
    def _do(atropine):
        result = atropine.first(**k)
        if result is None:
            raise CannotResolve()
        atropine.assimilate(result)
    return _do

from BeautifulSoup import Null

def prevsib(atropine):
    s = atropine.current.previousSibling
    if s is Null or s is atropine.current:
        raise CannotResolve()
    return atropine.assimilate(s)

def nextsib(atropine):
    s = atropine.current.nextSibling
    if s is Null or s is atropine.current:
        raise CannotResolve()
    atropine.assimilate(s)
