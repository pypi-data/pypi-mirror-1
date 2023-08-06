#!/usr/bin/env python
#
# How to browse the PID pathway interaction data
#

from cabig.cabio.service import *

get_class = lambda c: c.className.split('.')[-1];

cas = CaBioApplicationService()
pathway = cas.queryObject(Pathway.className, Pathway(name='h_cdc42racPathway'))[0]

print pathway.name
print pathway.displayValue
print pathway.source

for i in pathway.interactionCollection:
    icls = get_class(i)
    print "\n%s"%icls

    if icls == 'Macroprocess':
        print "Name: %s"%(i.name)

    for p in i.participantCollection:
        pcls = get_class(p)

        if pcls == 'Condition':
            print "    %s "%(pcls)
            print "      Name: %s"%(p.name)
        else:
            entities = ','.join([e.name for e in p.physicalEntity.entityNameCollection])
            print "    %s (%s) "%(pcls,entities)
            if p.activityState:
                print "      Activity State: %s"%(p.activityState)
            if p.location:
                print "      Location: %s"%(p.location)
            if p.postTranslationalMod:
                print "      Post-Translational Modification : %s"%(p.postTranslationalMod)


