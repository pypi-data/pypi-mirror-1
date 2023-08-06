from dap.wsgi.application import SimpleApplication
from dap.util import wsgi_intercept
from dap.dtypes import *
from dap.client import open

from paste.lint import middleware

from numpy import *

import httplib
httplib.HTTPConnection = wsgi_intercept.WSGI_HTTPConnection

dataset = DatasetType(name='dataset')
data = arange(16)
data.shape = (4, 4)
a = dataset['a'] = ArrayType(name='a', data=data, shape=data.shape, type=data.dtype.char)

app = SimpleApplication(dataset)
app = middleware(app)
wsgi_intercept.add_wsgi_intercept('localhost', 8080, lambda: app, script_name='')

dataset = open('http://localhost:8080/', verbose=1)
print dataset
print dataset.a.shape, dataset.a.type
print dataset.a[:]
print dataset.a[0]
print dataset.a[:,0]
print dataset.a[::2]
