# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD derivative License 

import os, sys
import interlude

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.DateRecurringIndex.tests.common import DRITestcase

def test_suite():
    from unittest import TestSuite
    from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite

    return TestSuite((
        ZopeDocFileSuite('recurring.txt',
                         package='Products.DateRecurringIndex',
                         test_class=DRITestcase,
                         globs=dict(interact=interlude.interact)),
    ))

if __name__ == '__main__':
    framework()
