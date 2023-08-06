from pyutil import benchutil, randutil
import random
from stringchain import stringchain

class Naive(object):
    def __init__(self):
        self.s = ''

    def __len__(self):
        return len(self.s)

    def append(self, s):
        self.s += s

    def trim(self, l):
        self.s = self.s[l:]

    def popleft(self, l):
        n = self.__class__()
        n.s = self.s[:l]
        self.s = self.s[l:]
        return n

    def str(self):
        return self.s

class B(object):
    def __init__(self):
        self.l = []
        self.r = []

    def init(self, N, randstr=randutil.insecurerandstr, rr=random.randrange):
        del self.l[:]
        del self.r[:]
        for i in range(0, N, 4096):
            self.l.append(randstr(4096))

    def init_loaded(self, N):
        self.init(N)
        self._buildup(N)

    def init_naive(self, N):
        self.a = Naive()
        return self.init(N)

    def init_strch(self, N):
        self.a = stringchain.StringChain()
        return self.init(N)

    def init_naive_loaded(self, N):
        self.a = Naive()
        return self.init_loaded(N)

    def init_strch_loaded(self, N):
        self.a = stringchain.StringChain()
        return self.init_loaded(N)

    def _buildup(self, N):
        for s in self.l:
            self.a.append(s)

    def _consume(self, N):
        while len(self.a):
            self.r.append(str(self.a.popleft(4096)))

    def _randomy(self, N, rr=random.randrange):
        i = 0
        while (i < len(self.l)) or (len(self.a) > 0):
            if (rr(2) == 0) or (i == len(self.l)):
                self.r.append(str(self.a.popleft(rr(0, 4096))))
            else:
                self.a.append(self.l[i])
                i += 1

def quick_bench():
    b = B()
    for (m, i) in [
        (b._buildup, b.init_naive), (b._buildup, b.init_strch),
        (b._consume, b.init_naive_loaded), (b._consume, b.init_strch_loaded),
        (b._randomy, b.init_naive), (b._randomy, b.init_strch),
        ]:
        print m.__name__, i.__name__
        for BSIZE in [2**16, 2**17, 2**18, 2**19]:
            benchutil.rep_bench(m, BSIZE, initfunc=i, MAXREPS=5)
