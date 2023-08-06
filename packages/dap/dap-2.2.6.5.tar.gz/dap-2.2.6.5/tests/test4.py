from dap.wsgi.application import SimpleApplication
from dap.util import wsgi_intercept
from dap.dtypes import *
from dap.client import open
from dap.server import SimpleHandler
from dap.helper import escape_dods

from paste.lint import middleware

import httplib
httplib.HTTPConnection = wsgi_intercept.WSGI_HTTPConnection

dataset = DatasetType(name='dataset')
dataset['seq'] = seq = SequenceType(name='seq')
seq['lat'] = BaseType(name='lat', type='Int32')
seq['lon'] = BaseType(name='lon', type='Int32')
seq['profile'] = SequenceType(name='profile')

seq['profile']['depth'] = BaseType(name='depth', type='Int32')
seq['profile']['temp'] = BaseType(name='temp', type='Int32')
seq['profile']['saln'] = BaseType(name='saln', type='Int32')

data = []
data.append([-10, 70, [(100, 24, 35), (200, 23, 36)]])
data.append([-11, 71, [(101, 23, 34), (201, 21, 35)]])
seq.data = data

print list(seq.data)

app = SimpleApplication(dataset)
#app = middleware(app)
wsgi_intercept.add_wsgi_intercept('localhost', 8080, lambda: app, script_name='')

dataset = open('http://localhost:8080/', verbose=1)
seq = dataset['seq']

print list(seq.data)

for position in seq:
    print position.lat.data, position.lon.data
    for cast in position.profile:
        print cast.depth.data, cast.temp.data, cast.saln.data
print

dataset = open('http://localhost:8080/', verbose=1)
seq = dataset['seq']
seq2 = seq.filter('seq.lat<-10', 'seq.profile.depth>150')
for position in seq2:
    print position.lat.data, position.lon.data
    for cast in position.profile:
        print cast.depth.data, cast.temp.data, cast.saln.data
print

dataset = open('http://localhost:8080/', verbose=1)
seq = dataset['seq']
seq2 = (s for s in seq if s.lat < -10 and s.profile.depth > 150)
for position in seq2:
    print position.lat.data, position.lon.data
    for cast in position.profile:
        print cast.depth.data, cast.temp.data, cast.saln.data
print
