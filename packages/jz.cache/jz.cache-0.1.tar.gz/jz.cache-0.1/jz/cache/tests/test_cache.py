# zope modules
from jz.testing.setup import placefulSetUp
from zope.configuration.xmlconfig import XMLConfig
from zope.testing.doctest import DocTestSuite, DocFileSuite
from zope.configuration.xmlconfig import XMLConfig
import zope.app

# python modules
import unittest

# test modules
from jz.cache.tests.sample import Content

# custom modules
import jz.cache


def setUp(test):

	XMLConfig("configure.zcml", zope.app)()
	XMLConfig("configure.zcml", jz.cache)()

	root = placefulSetUp()
	test.globs[u'root'] = root
	test.globs[u'Content'] = Content


def test_suite():
	return unittest.TestSuite((
		DocTestSuite('jz.cache.cache', setUp=setUp),
		DocFileSuite('../readme.txt', setUp=setUp),
	))


if __name__ == '__main__':
	unittest.main(defaultTest='test_suite')