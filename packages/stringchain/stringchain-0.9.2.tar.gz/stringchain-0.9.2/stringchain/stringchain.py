import copy

from pyutil.assertutil import precondition, _assert

from collections import deque

class StringChain(object):
    def __init__(self):
        self.d = deque()
        self.ig = 0
        self.tailig = 0
        self.len = 0

    def __len__(self):
        assert self._assert_invariants()
        return self.len

    def append(self, s):
        """ Add s to the end of the chain. """
        assert self._assert_invariants()
        if not s:
            return

        # First trim off any ignored tail bytes.
        if self.tailig:
            self.d[-1] = self.d[-1][:-self.tailig]
            self.tailig = 0

        self.d.append(s)
        self.len += len(s)
        assert self._assert_invariants()

    def trim(self, l):
        """ Trim off the leading l bytes. """
        assert self._assert_invariants()
        self.ig += l
        self.len -= l
        while self.d and self.ig >= len(self.d[0]):
            s = self.d.popleft()
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
        if not l or not self.d:
            return self.__class__()

        precondition(l >= 0, l)

        # We need to add at least this many bytes to the new StringChain.
        bytesleft = l + self.ig
        n = self.__class__()
        n.ig = self.ig

        while bytesleft > 0 and self.d:
            s = self.d.popleft()
            self.len -= (len(s) - self.ig)
            n.d.append(s)
            # If adding this string will put more than enough bytes into n, set its .len to only the desired length.
            n.len += len(s)-self.ig
            self.ig = 0
            bytesleft -= len(s)

        overrun = - bytesleft

        if overrun > 0:
            self.d.appendleft(s)
            self.len += overrun
            self.ig = len(s) - overrun
            n.len -= overrun
            n.tailig = overrun
        else:
            self.ig = 0

        # Either you got exactly how many you asked for, or you drained self entirely and you asked for more than you got.
        assert (n.len == l) or ((not self.d) and (l > self.len)), (n.len, l, len(self.d))

        assert self._assert_invariants()
        assert n._assert_invariants()
        return n

    def __str__(self):
        """ Return the entire contents of this chain as a single
        string. (Obviously this requires copying all of the bytes, so don't do
        this unless you need to.) This has a side-effect of collecting all the
        bytes in this StringChain object into a single string which is stored
        in the first element of its internal deque. """
        self._collapse()
        if self.d:
            return self.d[0]
        else:
            return ''

    def copy(self):
        n = self.__class__()
        n.ig = self.ig
        n.len = self.len
        n.d = copy.copy(self.d)
        return n

    def _assert_invariants(self):
        _assert(self.ig >= 0, self.ig)
        _assert(self.tailig >= 0, self.tailig)
        _assert(self.len >= 0, self.len)
        _assert((not self.d) or (self.d[0]), "First element is required to be non-empty.", self.d and self.d[0])
        _assert((not self.d) or (self.ig < len(self.d[0])), self.ig, self.d and len(self.d[0]))
        _assert((not self.d) or (self.tailig < len(self.d[-1])), self.tailig, self.d and len(self.d[-1]))
        _assert(self.ig+self.len+self.tailig == sum([len(x) for x in self.d]), self.ig, self.len, self.tailig, sum([len(x) for x in self.d]))
        return True

    def _collapse(self):
        """ Concatenate all of the strings into one string and make that string
        be the only element of the chain. (Obviously this requires copying all
        of the bytes, so don't do this unless you need to.) """
        assert self._assert_invariants()
        # First trim off any leading ignored bytes.
        if self.ig:
            self.d[0] = self.d[0][self.ig:]
            self.ig = 0
        # Then any tail ignored bytes.
        if self.tailig:
            self.d[-1] = self.d[-1][:-self.tailig]
            self.tailig = 0
        if len(self.d) > 1:
            newstr = ''.join(self.d)
            self.d.clear()
            self.d.append(newstr)
        assert self._assert_invariants()
