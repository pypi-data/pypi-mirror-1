#!/usr/bin/env python
#
# How to connect to an alternative service endpoint (caBIO staging server)
#

from cabig.cabio.service import *

STAGE_URL = "http://cabioapi-stage.nci.nih.gov/cabio40/services/caBIOService"

gene = Gene()
gene.symbol = 'EGFR'

cr = CaBioApplicationService().queryObject(Gene.className, gene)
sr = CaBioApplicationService(url=STAGE_URL).queryObject(Gene.className, gene)

print gene.symbol, "has the following big ids:"
print "Production %s" % cr[0].bigid
print "Stage      %s" % sr[0].bigid
