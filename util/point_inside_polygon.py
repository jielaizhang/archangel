#!/usr/bin/env python

import sys

def point_inside_polygon(x,y,poly):

  n = len(poly)
  inside = False

  p1x,p1y = poly[0]
  for i in range(n+1):
    p2x,p2y = poly[i % n]
    if y > min(p1y,p2y):
      if y <= max(p1y,p2y):
        if x <= max(p1x,p2x):
          if p1y != p2y:
            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
          if p1x == p2x or x <= xinters:
            inside = not inside
    p1x,p1y = p2x,p2y

  return inside

if __name__ == '__main__':

  if '-h' in sys.argv:
    print 'point_inside_polygon polygon_file test_file xcol ycol'
    sys.exit()

  poly=[]
  data=[(map(float, tmp.split())) for tmp in open(sys.argv[1],'r').readlines()]
  for x,y in data: poly.append([x,y])

  data=[tmp.split() for tmp in open(sys.argv[2],'r').readlines()]
  try:
    xcol=int(sys.argv[-2])
    ycol=int(sys.argv[-1])
  except:
    xcol=0 ; ycol=1
  try:
    for z in data:
      try:
#        if point_inside_polygon(float(z[xcol]),float(z[ycol]),poly): print z[xcol],z[ycol]
        if point_inside_polygon(float(z[xcol]),float(z[ycol]),poly): print ' '.join(z)
      except:
        pass
  except:
    pass
