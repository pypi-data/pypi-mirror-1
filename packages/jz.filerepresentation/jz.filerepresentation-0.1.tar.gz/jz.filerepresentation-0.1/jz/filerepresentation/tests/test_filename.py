# zope modules
from unittest import TestCase, main, makeSuite, TestSuite
from zope.testing.doctestunit import DocTestSuite
from zope.testing.doctest import NORMALIZE_WHITESPACE, ELLIPSIS

# jz modules
from jz.testing.setup import placefulSetUp


def setUp(test):
	root = placefulSetUp()
	test.globs['root'] = root


def test_suite():
	return TestSuite((
		DocTestSuite('jz.filerepresentation.filename', setUp=setUp, optionflags=NORMALIZE_WHITESPACE|ELLIPSIS),
		))


if __name__=='__main__':
	main(defaultTest='test_suite')
