import re

from dap.wsgi.application import SimpleApplication
from dap.util import wsgi_intercept
from dap.dtypes import *
from dap.client import open

from paste.lint import middleware

import httplib
httplib.HTTPConnection = wsgi_intercept.WSGI_HTTPConnection

dataset = DatasetType(name='dataset')
dataset['seq'] = seq = SequenceType(name='seq')
dataset['seq']['index'] = BaseType(name='index', type='Int32')
dataset['seq']['index'].data = (i for i in [10, 11, 12, 13])
dataset['seq']['temperature'] = BaseType(name='temperature', type='Float64')
dataset['seq']['temperature'].data = [17.2, 15.1, 15.3, 15.1]
dataset['seq']['site'] = BaseType(name='site', type='String')
dataset['seq']['site'].data = ['Diamond_St', 'Blacktail_Loop', 'Platinum_St', 'Kodiak_Trail']

app = SimpleApplication(dataset)
#app = middleware(app)
wsgi_intercept.add_wsgi_intercept('localhost', 8080, lambda: app, script_name='')

dataset = open('http://localhost:8080/', verbose=1)
seq = dataset['seq']

print list(seq.data)

seq2 = (struct_ for struct_ in seq if struct_.index >= 12)
for index, temperature, site in seq2:
    print index.data, temperature.data, site.data

seq2 = (struct_ for struct_ in seq if struct_.index >= 11 and struct_.temperature < 15.2)
for index, temperature, site in seq2:
    print index.data, temperature.data, site.data

# Currently not working fine.
seq2 = (struct_ for struct_ in seq if re.match(".*_St", struct_.site.data))
for index, temperature, site in seq2:
    print index.data, temperature.data, site.data

