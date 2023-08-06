SKIP = '.'

class Label:
    def __init__(self, nid, idx, link, skip = False):
        if skip:
            self._t = (nid, SKIP, idx, link)
        else:
            self._t = (nid, idx, link)

    def __getitem__(self, k):
        return self._t[k]

    def __eq__(self, other):
        if id(self) == id(other):
            return True
        return self._t == other._t

    def __neq__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str(self._t)


