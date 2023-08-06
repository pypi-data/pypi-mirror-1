import unittest
from Testing import ZopeTestCase as ztc
from ilrt.migrationtool.tests import base
from Products.CMFPlone.tests.testMigrationTool import TestMigrationTool

def test_suite():
    return unittest.TestSuite([
        ztc.ZopeDocFileSuite(
            'tests/browsertool.txt', package='ilrt.migrationtool',
            test_class=base.BaseFunctionalTestCase),

        ztc.ZopeDocFileSuite(
            'tests/workflowtool.txt', package='ilrt.migrationtool',
            test_class=base.BaseFunctionalTestCase),

        unittest.makeSuite(TestMigrationTool), 

        ztc.ZopeDocFileSuite(
            'tests/migrationtool.txt', package='ilrt.migrationtool',
            test_class=base.BaseFunctionalTestCase),

        ztc.ZopeDocFileSuite(
            'tests/utils.txt', package='ilrt.migrationtool',
            test_class=base.BaseFunctionalTestCase),

        ztc.ZopeDocFileSuite(
            'tests/atfitool.txt', package='ilrt.migrationtool',
            test_class=base.BaseFunctionalTestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
