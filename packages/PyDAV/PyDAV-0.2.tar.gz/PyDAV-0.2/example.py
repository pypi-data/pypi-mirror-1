#!/usr/bin/python

# Simple test 

import getpass
from WebDAV import client

URL = 'http://shuya.ath.cx:443/~neocool/private/dav-test/foo.txt'
USER = 'neocool'
#URL = 'http://chibi/dav/foo.txt'
#USER = 'webdav'

#passwd = getpass.getpass()
passwd = 'killgates'
res = client.Resource(URL, username=USER, password=passwd)
#print res.put(file='Moongoo.')
print res.get()
