# run this test like so:
# ./bin/instance test -s archetypes.fieldtraverser -t fieldtraverser-tests.txt


__author__ = """Johannes Raggam <johannes@bluedynamics.com>"""
__docformat__ = 'plaintext'

import unittest

from zope.testing import doctest
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

from pprint import pprint
from interact import interact

import os
from Globals import package_home

PACKAGE_HOME = package_home(globals())
def load_file(name):
    """Load a file from testing directory."""
    path = os.path.join(PACKAGE_HOME, name)
    file_desc = open(path, 'rb')
    data = file_desc.read()
    file_desc.close()
    return data

# Grab images for testing
TEST_JPEG = load_file('plone.jpg')
TEST_FILE = load_file('filetest.txt')

OPTION_FLAGS = doctest.REPORT_ONLY_FIRST_FAILURE | \
            doctest.NORMALIZE_WHITESPACE | \
            doctest.ELLIPSIS

@onsetup
def setup_archetypes_fieldtraverser():
    import archetypes.fieldtraverser
    zcml.load_config('configure.zcml', archetypes.fieldtraverser)

setup_archetypes_fieldtraverser()
PloneTestCase.setupPloneSite(products=['archetypes.fieldtraverser'])

def test_suite():

    from Testing import ZopeTestCase as ztc
    suite = ztc.ZopeDocFileSuite(
            'fieldtraverser-tests.txt',
            package='archetypes.fieldtraverser',
            test_class=PloneTestCase.FunctionalTestCase,
            optionflags=OPTION_FLAGS,
            globs={'interact': interact,
                   'pprint': pprint,
                   'test_jpg':TEST_JPEG,
                   'test_file':TEST_FILE,
                   },
    )

    return unittest.TestSuite((suite,))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

