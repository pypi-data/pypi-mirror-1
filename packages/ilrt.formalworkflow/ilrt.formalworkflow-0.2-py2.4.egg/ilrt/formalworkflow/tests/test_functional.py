import unittest
from Testing import ZopeTestCase as ztc
from ilrt.formalworkflow.tests import base


def test_suite():
    return unittest.TestSuite([

        ztc.ZopeDocFileSuite(
            'tests/functional.txt', package='ilrt.formalworkflow',
            test_class=base.BaseFunctionalTestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
