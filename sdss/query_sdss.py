#!/usr/bin/env python

import os, sys

if len(sys.argv) < 2:
#?ra=195.07330&dec=27.95535
  ra='195.07330' ; dec='27.95535'
else:
  ra=sys.argv[-2]
  dec=sys.argv[-1]

#cmd='"SELECT TOP 3 p.modelMag_g, \'ugriz\' as filter FROM dbo.fGetNearbyObjEq('+ \
#    ra+','+dec+',0.2) as b,  BESTDR6..Galaxy as p WHERE b.objID = p.objID"'

#cmd='"SELECT TOP 3 p.objid,p.modelMag_u, p.modelMag_g, p.modelMag_r, p.modelMag_i, '+ \
#    '\'ugriz\' as filter FROM dbo.fGetNearbyObjEq('+ \
#    ra+','+dec+',0.2) as b,  BESTDR6..Galaxy as p WHERE b.objID = p.objID"'

cmd='"SELECT TOP 50 p.run,p.rerun,p.camCol,p.field,p.obj '+ \
    'FROM BESTDR7..PhotoObj AS p '+ \
    'JOIN dbo.fGetNearbyObjEq(194.99,28.247389,5.0) AS b ON b.objID = p.objID '+ \
    'WHERE ( p.type = 3 OR p.type = 6)"'
tmp=os.popen('./sqlcl.py -q '+cmd).read()
print tmp
