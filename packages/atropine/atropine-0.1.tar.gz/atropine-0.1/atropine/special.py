from common import any, all, Collect, CannotResolve

def collect(key, onlytext=False, alltext=False):
    a = (onlytext, alltext)
    assert any(a) and not all(a)

    def _do(atropine):
        tag = atropine.current
        if onlytext:
            try:
                (child,) = tag.contents
            except ValueError:
                raise CannotResolve
            if atropine.istextnode(child):
                raise Collect, {key:child}
            raise CannotResolve()
        if alltext:
            texts = list(t for t in tag.recursiveChildGenerator()
                            if atropine.istextnode(t))
            raise Collect, {key:texts}

    return _do
