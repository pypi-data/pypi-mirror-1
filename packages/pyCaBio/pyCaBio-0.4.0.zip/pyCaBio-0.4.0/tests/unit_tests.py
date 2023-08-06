import unittest
from cabig.cabio.service import *

class WSTest(unittest.TestCase):
    
    def setUp(self):
        self.cas = CaBioApplicationService()

    def testGetVersion(self):
        version = self.cas.getVersion()
        self.assertEqual("4.2",version)
    
    def testGetRecordsPerQuery(self):
        num = self.cas.getRecordsPerQuery()
        self.assertEqual(1000,num)
    
    def testGetNumberOfGenes(self):
        gene = Gene()
        num = self.cas.getTotalNumberOfRecords(gene.className, gene)
        self.assertTrue(num > 0);    
    
    def testQueryGeneTaxon(self):
        
        gene = Gene()
        gene.symbol = "br*"
        taxon = Taxon()
        taxon.id = 5
        gene.taxon = taxon
        
        resultList = self.cas.queryObject(gene.className, gene)
        
        self.failUnless(resultList)
        
        for g in resultList:
            self.failUnless(g)
            self.failUnless(g.id)
            self.failUnless(g.symbol)
            self.assertEquals(5,g.taxon.id)
            
    def testQueryGeneOntology(self):
    
        go = GeneOntology()
        go.id = 5125
        gor = GeneOntologyRelationship()
        gor.childGeneOntology = go
    
        resultList = self.cas.queryObject(gor.className, gor)
        
        self.failUnless(resultList)
        
        for g in resultList:
            self.failUnless(g)
            self.failUnless(g.id)
            self.failUnless(g.relationshipType)
            self.assertEqual(go.id,g.childGeneOntology.id)
        
    def testGetAssociation(self):
        
        gene = Gene()
        gene.symbol = "nat*"
        
        go = GeneOntology()
        resultList = self.cas.queryObject(go.className, gene)
        
        self.failUnless(resultList)
        
        for g in resultList:
            
            # when serialization of arrays is fixed, this step can be removed
            go = GeneOntology()
            go.id = g.id
            
            # compare two ways of getting the association
            c1 = g.childGeneOntologyRelationshipCollection
            c2 = self.cas.getAssociation(go, 
                    "childGeneOntologyRelationshipCollection", 0)
            
            ids = [g1.id for g1 in c1]
            for gor in c2:
                self.failUnless(gor.id in ids)
                self.failUnless(gor.id)
                self.failUnless(gor.relationshipType)

    def testAssociations(self):
        
        g = self.cas.queryObject(Gene.className, Gene(symbol='brca2'))[0]
        self.failUnless(g.cytogeneticLocationCollection)
        self.failUnless(g.geneAliasCollection)

    def testGridIdExists(self):
        
        bigId = "hdl://2500.1.PMEUQUCCL5/DXZ7ZIOFOE"
        self.assertTrue(self.cas.exist(bigId))
    
    def testGetDataObject(self):
    
        bigId = "hdl://2500.1.PMEUQUCCL5/DXZ7ZIOFOE"
        gene = self.cas.getDataObject(bigId)
        self.failUnless(gene)
        self.assertEqual(bigId, gene.bigid)
    
    
    
if __name__ == '__main__':
    unittest.main()
