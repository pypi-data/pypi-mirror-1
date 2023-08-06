import unittest
import doctest

from Testing import ZopeTestCase as ztc

from quintagroup.ploneformgen.readonlystringfield.tests.base import \
    ReadOnlyStringFieldFunctionalTestCase

def test_suite():
    return unittest.TestSuite([
        ztc.FunctionalDocFileSuite(
            'readonlystringfield.txt',
            package='quintagroup.ploneformgen.readonlystringfield.tests',
            test_class=ReadOnlyStringFieldFunctionalTestCase,
            optionflags= doctest.REPORT_ONLY_FIRST_FAILURE | \
                doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
    ])
