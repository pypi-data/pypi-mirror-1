from pyutil.assertutil import precondition, _assert

from collections import deque

class StringChain(object):
    def __init__(self):
        self.d = deque()
        self.ig = 0
        self.len = 0

    def __len__(self):
        assert self._assert_invariants()
        return self.len

    def _assert_invariants(self):
        _assert(self.ig >= 0, self.ig)
        _assert(self.len >= 0, self.len)
        _assert((not self.d) or (self.d[0]), "First element is required to be non-empty.", self.d and self.d[0])
        _assert((not self.d) or (self.ig <= len(self.d[0])), self.ig, self.d and len(self.d[0]))
        _assert(self.ig+self.len == sum([len(x) for x in self.d]), self.ig, self.len, sum([len(x) for x in self.d]))
        return True
        
    def append(self, s):
        """ Add s to the end of the chain. """
        assert self._assert_invariants()
        self.d.append(s)
        self.len += len(s)
        assert self._assert_invariants()

    def trim(self, l):
        """ Trim off the leading l bytes. """
        assert self._assert_invariants()
        self.ig += l
        self.len -= l
        while self.d and l >= len(self.d[0]):
            s = self.d.popleft()
            l -= len(s)
            self.ig -= len(s)
        if self.len < 0:
            self.len = 0
        if not self.d:
            self.ig = 0
        assert self._assert_invariants()

    def popleft(self, l):
        """ Remove the leading l bytes of the chain and return them as a new
        Chain object. """
        assert self._assert_invariants()
        precondition(l >= 0, l)

        n = self.__class__()
        n.ig = self.ig
        while l > 0 and self.d:
            s = self.d.popleft()
            self.len -= len(s)
            n.d.append(s)
            n.len += len(s)
            l -= len(s)
        if l < 0:
            n.d[-1] = n.d[-1][:l]
            n.len += l
            self.d.appendleft(s)
            self.ig = len(s) + l
            self.len += (- l)
        else:
            self.ig = 0

        assert self._assert_invariants()
        assert n._assert_invariants()
        return n

    def _collapse(self):
        """ Concatenate all of the strings into one string and make that string
        be the only element of the chain. (Obviously this requires copying all
        of the bytes, so don't do this unless you need to.) """
        assert self._assert_invariants()
        if self.ig:
            self.d[0] = self.d[0][self.ig:]
            self.ig = 0
        if len(self.d) > 1:
            newstr = ''.join(self.d)
            self.d.clear()
            self.d.append(newstr)
        assert self._assert_invariants()

    def __str__(self):
        """ Return the entire contents of this chain as a single string. (This
        calls self._collapse() first then just returns a reference to the single
        element of the chain.) """
        self._collapse()
        if self.d:
            return self.d[0]
        else:
            return ''
