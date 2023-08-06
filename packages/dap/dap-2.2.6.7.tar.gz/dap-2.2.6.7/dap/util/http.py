import re

import httplib2
from dap.util import socks
httplib2.socks = socks

import dap.lib
from dap.exceptions import ClientError


def openurl(url, cache=None, username=None, password=None):
    h = httplib2.Http(cache=cache,
            timeout=dap.lib.TIMEOUT,
            proxy_info=dap.lib.PROXY)
    if username and password: h.add_credentials(username, password)

    if dap.lib.VERBOSE: print url
    resp, data = h.request(url, "GET", headers={'user-agent': dap.lib.USER_AGENT})

    # Check for errors
    if resp.get("content-description") == "dods_error":
        # Parse response.
        m = re.search('code = (?P<code>\d+);\s*message = "(?P<msg>.*)"', data, re.DOTALL | re.MULTILINE)
        msg =  'Server error %(code)s: "%(msg)s"' % m.groupdict()
        raise ClientError(msg)

    return resp, data
