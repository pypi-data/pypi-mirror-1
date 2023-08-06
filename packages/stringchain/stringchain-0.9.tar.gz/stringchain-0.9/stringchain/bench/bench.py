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

    def init(self, N, randstr=randutil.insecurerandstr, rr=random.randrange):
        del self.l[:]
        for i in range(N):
            self.l.append(randstr(rr(0, 4096)))

    def _benchit(self, ch, rr=random.randrange):
        i = 0
        while i < len(self.l):
            if rr(10) == 0:
                ch.popleft(rr(0, 2048))
            else:
                ch.append(self.l[i])
                i += 1

    def bench_naive(self, N):
        return self._benchit(Naive())

    def bench_strch(self, N):
        return self._benchit(stringchain.StringChain())


def quick_bench():
    b = B()
    for m in (b.bench_naive, b.bench_strch):
        print m
        benchutil.bench(m, initfunc=b.init, TOPXP=8)
