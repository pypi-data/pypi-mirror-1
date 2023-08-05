from Testing.ZopeTestCase import FunctionalDocFileSuite
from Globals import package_home
from base import CommentingFunctionalTestCase
from unittest import TestSuite
from os.path import join, split
from os import walk
from re import compile
from sys import argv

# first we determine the pattern when searching doctests:
# no limitations apply when a test pattern was explicitely specified, so
# that tests in failing/ or elsewhere can be run as well;  otherwise only
# files named 'test*' and files contained in directories named this way
# are considered to build the test suite...
if '-t' in argv:
    pattern = compile('.*\.(txt|rst)$')
else:
    pattern = compile('(^test.*|/test[^/]*)\.(txt|rst)$')

# we collect all matching doctests in docs/
tests = []
docs = join(package_home(globals()), '../docs/')
for path, dirs, files in walk(docs, topdown=False):
    for name in files:
        relative = join(path, name)[len(docs):]
        if not '.svn' in split(path) and pattern.search(relative):
            tests.append(relative)

def test_suite():
    suite = TestSuite()
    for test in tests:
        suite.addTest(FunctionalDocFileSuite(test,
            package="iqpp.plone.commenting.docs",
            test_class=CommentingFunctionalTestCase))
    return suite

