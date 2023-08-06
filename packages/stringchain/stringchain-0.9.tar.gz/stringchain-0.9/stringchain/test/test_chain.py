import unittest
from stringchain import stringchain

print "stringchain is ", stringchain
class T(unittest.TestCase):
    def test_al(self):
        c = stringchain.StringChain()
        c.append("ab")
        self.failUnlessEqual(len(c), 2)
        c.append("")
        self.failUnlessEqual(len(c), 2)
        c.append("c")
        self.failUnlessEqual(len(c), 3)

    def test_str(self):
        c = stringchain.StringChain()
        c.append("ab")
        c.append("c")
        self.failUnlessEqual(str(c), "abc")

    def test_trim(self):
        c = stringchain.StringChain()
        c.append("ab")
        c.append("c")
        c.trim(1)
        self.failUnlessEqual(str(c), "bc", (str(c), "bc", c.ig, c.len, c.d))
        c.trim(1)
        self.failUnlessEqual(str(c), "c")
        c.trim(1)
        self.failUnlessEqual(str(c), "")
        c.append("ab")
        c.append("c")
        c.trim(2)
        self.failUnlessEqual(str(c), "c")
        c.trim(1)
        self.failUnlessEqual(str(c), "")
        c.append("a")
        c.append("bc")
        c.trim(2)
        self.failUnlessEqual(str(c), "c")
        c.trim(1)
        self.failUnlessEqual(str(c), "")

        c.append("abc")
        c.trim(4) # We just silently trim all.
        self.failUnlessEqual(str(c), "")

    def test_popleft(self):
        c = stringchain.StringChain()
        c.append("ab")
        s = c.popleft(1)
        self.failUnlessEqual(str(s), "a")
        self.failUnlessEqual(str(c), "b", (str(c), "b", c.ig, c.len, c.d))
        s = c.popleft(1)
        self.failUnlessEqual(str(s), "b")
        self.failUnlessEqual(str(c), "")

        c.append("abc")
        s = c.popleft(1)
        self.failUnlessEqual(str(s), "a")
        self.failUnlessEqual(str(c), "bc")
        s = c.popleft(1)
        self.failUnlessEqual(str(s), "b")
        self.failUnlessEqual(str(c), "c")
        s = c.popleft(1)
        self.failUnlessEqual(str(s), "c")
        self.failUnlessEqual(str(c), "")

        c.append("abc")
        s = c.popleft(2)
        self.failUnlessEqual(str(s), "ab")
        self.failUnlessEqual(str(c), "c")
        s = c.popleft(1)
        self.failUnlessEqual(str(s), "c")
        self.failUnlessEqual(str(c), "")

        c.append("ab")
        c.append("c")
        s = c.popleft(2)
        self.failUnlessEqual(str(s), "ab")
        self.failUnlessEqual(str(c), "c")
        s = c.popleft(1)
        self.failUnlessEqual(str(s), "c")
        self.failUnlessEqual(str(c), "")

        c.append("a")
        c.append("bc")
        s = c.popleft(2)
        self.failUnlessEqual(str(s), "ab")
        self.failUnlessEqual(str(c), "c")
        s = c.popleft(1)
        self.failUnlessEqual(str(s), "c")
        self.failUnlessEqual(str(c), "")

        c.append("abc")
        s = c.popleft(4) # We just silently pop them all.
        self.failUnlessEqual(str(s), "abc")
        self.failUnlessEqual(str(c), "")
