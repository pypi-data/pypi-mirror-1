#!/usr/bin/python

from setuptools import setup

setup(
    name = "PyDAV",
    version = "0.21",
    packages = ['WebDAV'],
    test_suite = 'tests',

    author = "Boris Buegling",
    author_email = "boris@icculus.org",
    description = "Python WebDAV client library",
    license = "ZPL 2.0",
    keywords = "webdav",
	url = "https://shuya.ath.cx/~neocool/code/pydav/",
	long_description = "Simple Python WebDAV client library, basically taken from Zope 2.8.0. Unlike Zope's version, this one is stand-alone and works with Python 2.4.x.",
	download_url = "https://shuya.ath.cx/~neocool/code/pydav/pydav-latest.tar.bz2",
)
