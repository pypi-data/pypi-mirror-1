import unittest
from cabig.cabio.service import *

class DefectsTest(unittest.TestCase):
    """ These tests are expected to fail until the defects are fixed, at which 
        point they will be moved to another test suite. 
    """ 
  
    def setUp(self):
        self.cas = CaBioApplicationService()
    
    def testArrayQuery(self):
        
        gene = Gene()
        gene.symbol = "brca1"
        taxon = Taxon()
        taxon.service = self.cas # This shouldn't be necessary
        taxon.geneCollection = (gene,)
        
        resultList = self.cas.queryObject(taxon.className, taxon)
        
        self.failUnless(resultList)
        self.assertEquals(len(resultList),2)
        
    
if __name__ == '__main__':
    unittest.main()
