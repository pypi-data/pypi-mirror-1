import unittest
from Testing import ZopeTestCase as ztc
from collective.contentgenerator.tests import base


def test_suite():
    return unittest.TestSuite([

        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'tests/users.txt', package='collective.contentgenerator',
            test_class=base.BaseFunctionalTestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
