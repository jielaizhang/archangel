#!/usr/bin/env python

import sys, os.path
from xml_archangel import *
from math import *

def interp(x1,x2,y1,y2,z1):
  return y1+(z1-x1)*(y2-y1)/(x2-x1)

if __name__ == '__main__':

  if '-h' in sys.argv:
    print 'Usage: two_sfb_color blue_file_name red_file_name'
    print
    print 'options: -log = output radii in log kpc, noe: this option kills < 2 arcsecs'
    print '         -txt = not using xml files, two ASCII files, r + sfb'
    sys.exit()

  if '-txt' not in sys.argv:
    if os.path.exists(sys.argv[-2].split('.')[0]+'.xml'):
      name=sys.argv[-2]
      root='.'
    else:
      try:
        for root, dirs, files in os.walk('.'):
          for name in files:
            if 'xml' not in name: continue
            if sys.argv[-2] in name:
              raise
        else:
          print file,'no file found'
          sys.exit()
      except:
        pass

  try:
    if '-txt' in sys.argv:
      blue_sfb=[(map(float, tmp.split())) for tmp in open(sys.argv[-2],'r').readlines()] 
      del blue_sfb[-1]
    else:
      if sys.argv[-2] not in name:
        print 'file not found',sys.argv[-2]
        sys.exit()
      doc = minidom.parse(root+'/'+name.split('.')[0]+'.xml')
      rootNode = doc.documentElement
      elements=xml_read(rootNode).walk(rootNode)

      try:
        kpc=float(elements['cosmology_corrected_scale_kpc_arcsec'][0][1])
      except:
        kpc=None

      try:
        blue_ext=float(elements['gal_extinc_'+sys.argv[-2].split('_')[1][0]][0][1])
      except:
        blue_ext=0.

      isfb=0
      for t in elements['array']:
        if t[0]['name'] == 'sfb':
          blue_sfb=[]
          tmp=[]
          head=[]
          for z in t[2]['axis']:
            head.append(z[0]['name'])
            tmp.append(map(float,z[1].split('\n')))
          for z in range(len(tmp[0])):
            kill=int(tmp[head.index('kill')][z])
            try: # if errorbars in sfb area
              blue_sfb.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                           kill,tmp[head.index('error')][z]])
            except:
              blue_sfb.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                           kill,0.])
          break

  except:
    raise
    print sys.argv[-2],'XML error'
    sys.exit()


  if '-txt' not in sys.argv:
    if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
      name=sys.argv[-1]
      root='.'
    else:
      try:
        for root, dirs, files in os.walk('.'):
          for name in files:
            if 'xml' not in name: continue
            if sys.argv[-1] in name:
              raise
        else:
          print file,'no file found'
          sys.exit()
      except:
        pass

  try:
    if '-txt' in sys.argv:
      red_sfb=[(map(float, tmp.split())) for tmp in open(sys.argv[-1],'r').readlines()] 
      del red_sfb[-1]
    else:
      doc = minidom.parse(root+'/'+name.split('.')[0]+'.xml')
      rootNode = doc.documentElement
      elements=xml_read(rootNode).walk(rootNode)

      if not kpc: kpc=float(elements['cosmology_corrected_scale_kpc_arcsec'][0][1])

      try:
        if sys.argv[-1].split('_')[1] == 'ch1':
          red_ext=float(elements['gal_extinc_L'][0][1])
        else:
          red_ext=float(elements['gal_extinc_'+sys.argv[-1].split('_')[1][0]][0][1])
      except:
        red_ext=0.

      isfb=0
      for t in elements['array']:
        if t[0]['name'] == 'sfb':
          red_sfb=[]
          tmp=[]
          head=[]
          for z in t[2]['axis']:
            head.append(z[0]['name'])
            tmp.append(map(float,z[1].split('\n')))
          for z in range(len(tmp[0])):
            kill=int(tmp[head.index('kill')][z])
            try: # if errorbars in sfb area
              red_sfb.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                           kill,tmp[head.index('error')][z]])
            except:
              red_sfb.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                           kill,0.])
          break

  except:
    raise
    print sys.argv[-1],'XML error'
    sys.exit()

xmin=max(blue_sfb[0][0],red_sfb[0][0])
xmax=min(blue_sfb[-1][0],red_sfb[-1][0])

if '-txt' in sys.argv:
  for n,a in enumerate(blue_sfb):
    if a[0] < xmin or a[0] > xmax: continue
    for m,b in enumerate(red_sfb):
      if b[0] > a[0]:
        if '-log' in sys.argv:
          print log10(a[0]),a[1]-interp(red_sfb[m-1][0],red_sfb[m][0],red_sfb[m-1][1],red_sfb[m][1],a[0])
#          print a,b
        else:
          print a[0],a[1]-interp(red_sfb[m-1][0],red_sfb[m][0],red_sfb[m-1][1],red_sfb[m][1],a[0])
        break

else:
  for n,a in enumerate(blue_sfb):
#  print a
    if '-log' in sys.argv and a[0] < 2.: continue
    if a[0] < xmin or a[0] > xmax: continue
    for m,b in enumerate(red_sfb):
      if a[2] and b[2]:
        if b[0] > a[0]:
#        print a,b
          if '-log' in sys.argv:
            print log10(kpc*a[0]),a[1]-interp(red_sfb[m-1][0],red_sfb[m][0],red_sfb[m-1][1],red_sfb[m][1],a[0]),
          else:
            print a[0],a[1]-interp(red_sfb[m-1][0],red_sfb[m][0],red_sfb[m-1][1],red_sfb[m][1],a[0]),
          print ((a[3]**2+interp(red_sfb[m-1][0],red_sfb[m][0], \
                 red_sfb[m-1][3],red_sfb[m][3],a[0])**2)**0.5)/2.,name.split('.')[0]
#        print a[0],a[1],red_sfb[m-1][0],red_sfb[m][0],red_sfb[m-1][1],red_sfb[m][1],a[0]
          break
