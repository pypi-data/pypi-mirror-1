# zope modules
from zope.testing.doctest import NORMALIZE_WHITESPACE, ELLIPSIS
from zope.configuration.xmlconfig import XMLConfig
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import placelesssetup
from zope.publisher.browser import TestRequest
import transaction, zope.app

# zc modules
import zc.resourcelibrary

# jz modules
from jz.testing.setup import placefulSetUp
import jz.magic, jz.common

# python modules
import unittest


def setUp(test):
	"""Set Up Zope 3 test environment."""

	placelesssetup.setUp()

	XMLConfig("configure.zcml", zope.app)()
	XMLConfig("meta.zcml", zc.resourcelibrary)()
	XMLConfig("configure.zcml", jz.common)()
	XMLConfig("meta.zcml", jz.magic)()
	XMLConfig("configure.zcml", jz.magic)()

	test.globs['TestRequest'] = TestRequest


def test_suite():
	return unittest.TestSuite((
		DocFileSuite('../readme.txt', setUp=setUp, optionflags=NORMALIZE_WHITESPACE|ELLIPSIS),
	))


if __name__ == '__main__':
	unittest.main(defaultTest='test_suite')