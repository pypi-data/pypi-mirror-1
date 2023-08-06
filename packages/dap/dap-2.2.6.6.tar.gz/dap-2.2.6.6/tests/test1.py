from dap.wsgi.application import SimpleApplication
from dap.util import wsgi_intercept
from dap.dtypes import *
from dap.client import open

from paste.lint import middleware

import httplib
httplib.HTTPConnection = wsgi_intercept.WSGI_HTTPConnection

dataset = DatasetType(name='dataset')
dataset['seq'] = seq = SequenceType(name='seq')
seq['a'] = BaseType(name='a', type='Int32')
seq['b'] = BaseType(name='b', type='Int32')

seq['a'].data = range(5)
seq['b'].data = range(5, 10)

print list(seq.data)

app = SimpleApplication(dataset)
#app = middleware(app)
wsgi_intercept.add_wsgi_intercept('localhost', 8080, lambda: app, script_name='')

dataset = open('http://localhost:8080/', verbose=1)
seq = dataset['seq']

print list(seq.data)

for struct_ in seq:
    print struct_.data

seq2 = (struct_ for struct_ in seq if struct_['a'] > 1 and struct_['b'] < 9)
for struct_ in seq2:
    print struct_.data

seq2 = [struct_ for struct_ in seq if struct_.a > 1 and struct_.b < 9]
for struct_ in seq2:
    print struct_.data

dataset = open('http://localhost:8080/', verbose=1)
seq = dataset.seq
amin = 1
bmax = 9
seq2 = (struct_ for struct_ in seq if struct_.a > amin and struct_.b < bmax)
for struct_ in seq2:
    print struct_.data

dataset = open('http://localhost:8080/', verbose=1)
for struct_ in (s for s in dataset.seq if s.a > 2):
    print struct_

dataset = open('http://localhost:8080/', verbose=1)
for struct_ in dataset.seq:
    if struct_.a > 2:
        print struct_.data
