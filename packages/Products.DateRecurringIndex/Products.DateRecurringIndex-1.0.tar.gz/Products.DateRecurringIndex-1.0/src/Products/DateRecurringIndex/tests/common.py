# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD derivative License 

import os, sys, code
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.ZCatalog.Catalog import Catalog
from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
from Products.DateRecurringIndex.index import DateRecurringIndex
from datetime import datetime

ZopeTestCase.installProduct('DateRecurringIndex')

class DummyEvent(object):
    """some dummy with a start, delta and until to index"""
    
    def __init__(self, id, start, delta, until):
        self.id = id
        self.start = start
        self.delta = delta
        self.until = until
        
        
class DRITestcase(ZopeTestCase.ZopeTestCase):
    """Base TestCase for DateRecurringIndex."""
    
    def afterSetUp(self):
        """set up a base scenario"""
        self.app.catalog = Catalog()
        extra = object()
        # abuse:
        extra = DummyEvent(None, 'start', 'delta', 'until') # abuse, but works
        extra.dst = 'adjust'
        dri = DateRecurringIndex('recurr', extra=extra)
        self.app.catalog.addIndex('recurr', dri)
        self.app.catalog.addColumn('id')
        
    def buildDummies(self, cases):
        """setup dummies, cases is a list of tuples (start, delta, until)."""
        dummies = {}
        for id in cases:
            dummy = DummyEvent(id, datetime(*(cases[id][0])), 
                                   cases[id][1],
                                   cases[id][2] is not None and \
                                   datetime(*(cases[id][2])) or None
                    )
            dummies[id] = dummy
        return dummies
    
    def catalogDummies(self, dummies):
        for id in dummies:
            self.app.catalog.catalogObject(dummies[id], id)
            
    def idsOfBrainsSorted(self, brains):
        ids = [brain.id for brain in brains]
        ids.sort()
        return ids


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(DRIRITestcase))
    return suite

if __name__ == '__main__':
    framework()


