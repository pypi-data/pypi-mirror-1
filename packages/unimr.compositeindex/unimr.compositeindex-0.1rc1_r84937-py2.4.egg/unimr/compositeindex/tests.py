from Testing import ZopeTestCase as ztc
import unittest

import string, random

from time import time

from Zope2 import DB

from Products.Five import zcml
from Products.Five import fiveconfigure

from OFS.SimpleItem import SimpleItem
from DateTime import DateTime

from Products.ZCatalog import ZCatalog
from Products.ZCatalog.Catalog import Catalog, CatalogError

from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex



import unimr.compositeindex
from unimr.compositeindex.CompositeIndex import CompositeIndex



                        

states = ['published','pending','private','intranet']
types  = ['Document','News','File','Image']
default_pages = [True,False,False,False,False,False]


class TestObject(object):

    def __init__(self, id, portal_type, review_state,is_default_page=False):
        self.id = id
        self.portal_type = portal_type
        self.review_state = review_state
        self.is_default_page = is_default_page

    def getPhysicalPath(self):
        return ['',self.id,]

    def __repr__(self):
        return "< %s, %s, %s, %s >" % (self.id,self.portal_type,self.review_state,self.is_default_page)
        
class RandomTestObject(TestObject):

    def __init__(self, id):
        
        i = random.randint(0,len(types)-1)
        portal_type = types[i]
        
        i = random.randint(0,len(states)-1)
        review_state = states[i]

        i = random.randint(0,len(default_pages)-1)
        is_default_page = default_pages[i]
        
        super(RandomTestObject,self).__init__(id,portal_type,review_state,is_default_page)


class CompositeIndexTests( ztc.ZopeTestCase ):

    def beforeSetUp(self):
        print 
        ztc.installProduct('ZCatalog')

        ztc.installProduct('Five')
        
        fiveconfigure.debug_mode = True
        zcml.load_config('configure.zcml',
                         unimr.compositeindex)
        fiveconfigure.debug_mode = False
        ztc.installPackage('unimr.compositeindex')     

 
    def afterSetUp(self):
        
        catalog = ZCatalog.ZCatalog('portal_catalog')
        self.app._setObject('portal_catalog', catalog)

        self.cat = self.app.portal_catalog

        self.cat.manage_addProperty('unimr.compositeindex',1,'boolean')
        self.cat.manage_addProperty('unimr.catalogqueryplan',0,'boolean')
        
        idx = CompositeIndex('comp01',extra = {'indexed_attrs': 'is_default_page,review_state,portal_type'})
        self.cat._catalog.addIndex('id', idx)
        
        idx = FieldIndex('review_state')
        self.cat._catalog.addIndex('review_state', idx)

        idx = FieldIndex('portal_type')
        self.cat._catalog.addIndex('portal_type', idx)
        
        idx = FieldIndex('is_default_page')
        self.cat._catalog.addIndex('is_default_page', idx)

        self.db = ztc

        
    def _cacheMinimize(self):

        DB.cacheMinimize()


    def _defaultSearch(self, *args, **kw):

        self.cat._updateProperty('unimr.compositeindex',0)
        self._cacheMinimize()
        return self.cat(*args, **kw)

    
    def _compositeSearch(self, *args, **kw):

        self.cat._updateProperty('unimr.compositeindex',1)
        self._cacheMinimize()
        return self.cat(*args, **kw)
    

    def testPerformance(self):

        lengths = [10,100,1000,10000,100000]

        queries = [{  'portal_type' : 'Document' , 'review_state' : 'pending' },\
                   {  'is_default_page': True, 'portal_type' : 'Document' , 'review_state' : 'pending' }]        

        def profileSearch(*args, **kw):


            st = time()
            res1 = self._defaultSearch(*args, **kw)
            print "atomic:    %s hits in %3.2fms" % (len(res1), (time() -st)*1000)

            st = time()
            res2 = self._compositeSearch(*args, **kw)
            print "composite: %s hits in %3.2fms" % (len(res2), (time() -st)*1000)

            self.assertEqual(len(res1),len(res2))

            for i,v in enumerate(res1):
                self.assertEqual(res1[i].getRID(), res2[i].getRID())  



        for l in lengths:
            self.cat.manage_catalogClear()
            print "************************************" 
            print "indexed objects: %s" % l
            for i  in range(l):
                name = 'dummy%s' % i
                obj = RandomTestObject(name)
                self.cat.catalog_object(obj)

            for query in queries:
                profileSearch(**query)


      
        print "************************************"


    def testSearch(self):

        obj = TestObject('obj1','Document','pending')
        self.cat.catalog_object(obj)
        
        obj = TestObject('obj2','News','pending')
        self.cat.catalog_object(obj)
        
        obj = TestObject('obj3','News','visible')
        self.cat.catalog_object(obj)       
        
        queries = [{ 'review_state': 'pending' ,'portal_type' : 'Document'},
                   { 'review_state': ['pending','visible'] ,'portal_type' : 'News'},
                   { 'review_state': ['pending'] ,'portal_type' : ['News','Document']},
                   { 'review_state': ['pending','visible'] ,'portal_type' : ['News','Document']}
                   ]

        for query in queries:
        
            res1 = self._defaultSearch(**query)
            res2 = self._compositeSearch(**query)

            self.assertEqual(len(res1),len(res2))

            for i,v in enumerate(res1):
                self.assertEqual(res1[i].getRID(), res2[i].getRID())
            
        

        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompositeIndexTests))
    return suite

if __name__ == '__main__':
    unittest.main()
