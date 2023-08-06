import unittest, os

import zope, transaction
import os.path
from zope.testing import doctest, doctestunit, module
from zope.app.testing.functional import FunctionalDocFileSuite, FunctionalDocTestSuite, ZCMLLayer

import bop
import testing

BebopWebDAVLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'BebopWebDAVLayer', allow_teardown=True)


def setUp(test):
    module.setUp(test, 'bebop.webdav.readme_txt')

def tearDown(test):
    module.tearDown(test, 'bebop.webdav.readme_txt')


def test_suite():
    suite = unittest.TestSuite()
    
    globs = {'os': os,
            'os.path': os.path,
            'zope': zope,
            'transaction': transaction,
            'pprint': doctestunit.pprint,
            'printEvent': testing.printEvent,
            'bop': bop}
            
                      
    test = FunctionalDocFileSuite('README.txt',
            package='bebop.webdav',
            globs=globs,
            optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS)

    test.layer = BebopWebDAVLayer
    suite.addTests((test,))
        
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
