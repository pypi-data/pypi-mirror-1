#!/usr/bin/python
""" Simple PyDAV example. """

__revision__ = '0.1'

from WebDAV import client

# PyDAV supports both http:// and https:// URLs, the latter defaulting
#	to port 443
URL = 'https://foo.bar/blah.txt'
URL = 'http://foo.bar/blah.txt'

# PyDAV also supports HTTP-AUTH over both protocols
USER = 'foobar'
PASS = 'moongoo'

# A connection is initialized by creating a Resource object
res = client.Resource(URL, username=USER, password=PASS)

# You can then write to the specified URL...
response = res.put(file='heh')

# ...and read from there
response = res.get()

# Both methods return a http_response object
print response.get_status(), response.get_headers(), response.get_body()
