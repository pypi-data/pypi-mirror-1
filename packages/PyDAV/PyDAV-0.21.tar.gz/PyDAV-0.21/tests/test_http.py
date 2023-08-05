#!/usr/bin/python

import unittest

class TestHttps(unittest.TestCase):
	def test1 (self):
		from WebDAV import client
		res = client.Resource('http://chibi/dav/foo.txt', 
			username='webdav', password='killgates')
		data = 'Moongoo.'
		res.put(file=data)
		self.assertEqual(data, str(res.get()).split()[-1])

if __name__ == '__main__':
	unittest.main()
