import unittest
from Testing import ZopeTestCase as ztc
from ilrt.contentmigrator.tests import base


def test_suite():
    return unittest.TestSuite([

        ztc.ZopeDocFileSuite(
            'tests/export.txt', package='ilrt.contentmigrator',
            test_class=base.BaseFunctionalTestCase),

        ztc.ZopeDocFileSuite(
            'tests/import.txt', package='ilrt.contentmigrator',
            test_class=base.BaseFunctionalTestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
