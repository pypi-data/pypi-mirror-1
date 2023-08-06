chain -- efficient management of strings which are produced and consumed in chunks

trac:

http://tahoe-lafs.org/trac/chain

darcs repository:

http://tahoe-lafs.org/source/chain/trunk

To run tests, do

python ./setup.py test

To run benchmarks, do

python -OOu -c 'from stringchain.bench import bench; bench.quick_bench()'

(The "-O" is important when benchmarking, since chain has extensive
self-tests that are optimized out when -O is included.)


LICENCE

You may use this package under the GNU General Public License, version 2 or, at
your option, any later version.  You may use this package under the Transitive
Grace Period Public Licence, version 1.0, or at your option, any later version.
(You may choose to use this package under the terms of either licence, at your
option.)  See the file COPYING.GPL for the terms of the GNU General Public
License, version 2.  See the file COPYING.TGPPL.html for the terms of the
Transitive Grace Period Public Licence, version 1.0.
