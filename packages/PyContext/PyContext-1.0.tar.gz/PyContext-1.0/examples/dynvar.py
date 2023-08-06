from __future__ import with_statement
from context import Variable

v = Variable()

with v.set(100):
    print v.get()
    with v.set(200):
        print v.get()
    print v.get()
print v.get()
