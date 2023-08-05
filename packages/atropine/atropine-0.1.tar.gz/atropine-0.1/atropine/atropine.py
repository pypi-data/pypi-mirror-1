from BeautifulSoup import BeautifulSoup, Null, NavigableText
import check, go
from common import CannotResolve, Collect

class WhitespaceIsntDataSoup(BeautifulSoup):
    def handle_data(self, data):
        if not data.isspace():
            BeautifulSoup.handle_data(self, data)

def mergeclass(cls, attrs):
    if cls is not None:
        attrs['class'] = cls
    return attrs

class AtropineBase(object):
    current = None
    collection = None

    def __init__(self, checkers, html, ignorewhitespace):
        self.checkers = checkers
        if html is not None:
            if ignorewhitespace:
                cls = WhitespaceIsntDataSoup
            else:
                cls = BeautifulSoup
            self.soup = cls(html)

    def registerchecker(self, name, f):
        self.checkers[name] = f

    def getchecker(self, name):
        return self.checkers[name]

    @staticmethod
    def istextnode(t):
        return isinstance(t, NavigableText)

    @classmethod
    def onlytext(cls, t):
        (contents,) = t.contents
        assert cls.istextnode(contents)
        return contents

    def find(self, tag=None, cls=None, attrs=None):
        if attrs is None:
            attrs = dict()
        return self.soup.fetch(name=tag, attrs=mergeclass(cls, attrs))

    def first(self, tag=None, cls=None, attrs=None):
        if attrs is None:
            attrs = dict()
        return self.soup.first(name=tag, attrs=mergeclass(cls, attrs))

    def resolve(self, *things):
        self.collection = None
        self.current = self.soup
        collection = dict()

        for thing in things:
            try:
                thing(self)
            except Collect, val:
                (cdict,) = val.args
                collection.update(cdict)

        new = self.__class__(None)
        new.checkers.update(self.checkers)
        (new.soup, self.current) = (self.current, None)
        new.collection = collection
        return new

    def assimilate(self, soup):
        assert soup is not Null or soup is not None
        self.current = soup



class Atropine(AtropineBase):
    def __init__(self, html=None, ignorewhitespace=True):
        checkers = dict(indexonparent = check.indexonparent,
                        nchildren     = check.nchildren,
                        tag           = check.soupattribute('name'),
                        id            = check.tagattribute('id'),
                        cls           = check.tagattribute('class'),
                        attrs         = check.tagattributes,
                        onlytext      = check.onlytext,
                        alltext       = check.alltext)

        AtropineBase.__init__(self, checkers, html, ignorewhitespace)
