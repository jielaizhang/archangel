#!/usr/bin/env python

# experiment to fit curves of growth

import sys,os,math

if sys.argv[-1] == '-h':
  print '''
Usage: el options cleaned_file
 
script that takes cleaned FITS file and fills in NaN pixels
from efit isophotes, then does elliptical apertures

options: -b = use bulge+disk fit
         -e = use r**1/4 fit
         -s = use sersic fit
       -fit = ignore fits (expm = xsfb)
       -sky = fix sky value
      -fake = make a fake file first
   -no_asym = do not do interactive asym
         -q = quiet'''
  sys.exit()

prefix=sys.argv[-1].split('.')[0]
endfix=sys.argv[-1].split('.')[-1]
if prefix == endfix or len(endfix) == 0:
  file=prefix+'.clean'
else:
  file=sys.argv[-1]

if not os.path.exists(prefix+'.xml'):
  print 'no XML file,',prefix
  sys.exit()

if '-fake' in sys.argv:
  cmd='fake -c -q '+file
  if '-q' not in sys.argv: print cmd
  os.system(cmd)
  file=file.replace('clean','fake')

if '-q' not in sys.argv: print 'xml_archangel -o '+prefix+' prf | lines 2- > tmp.prf'
os.system('xml_archangel -o '+prefix+' prf | lines 2- > tmp.prf')

if '-e' in sys.argv:
  line=['0.','0.']
  tmp=os.popen('xml_archangel -o '+prefix+' re_dev').read().replace('\n','')
  if 'not found' in tmp:
    print 're_dev fit parameter not found'
    sys.exit()
  else:
    line.append(tmp)
  tmp=os.popen('xml_archangel -o '+prefix+' se_dev').read().replace('\n','')
  if 'not found' in tmp:
    print 'se_dev fit parameter not found'
    sys.exit()
  else:
    line.append(tmp)
elif '-s' in sys.argv:
  line=['0.']
  tmp=os.popen('xml_archangel -o '+prefix+' n_sersic').read().replace('\n','')
  if 'not found' in tmp:
    print 'n_sersic fit parameter not found'
    sys.exit()
  else:
    line.append(tmp)
  tmp=os.popen('xml_archangel -o '+prefix+' re_sersic').read().replace('\n','')
  if 'not found' in tmp:
    print 're_sersic fit parameter not found'
    sys.exit()
  else:
    line.append(tmp)
  tmp=os.popen('xml_archangel -o '+prefix+' se_sersic').read().replace('\n','')
  if 'not found' in tmp:
    print 'se_sersic fit parameter not found'
    sys.exit()
  else:
    line.append(tmp)
elif '-b' in sys.argv:
  line=[]
  tmp=os.popen('xml_archangel -o '+prefix+' alpha').read().replace('\n','')
  if 'not found' in tmp:
    print 'alpha fit parameter not found'
    sys.exit()
  else:
    line.append(tmp)
  tmp=os.popen('xml_archangel -o '+prefix+' mu_o').read().replace('\n','')
  if 'not found' in tmp:
    print 'mu_o fit parameter not found'
    sys.exit()
  else:
    line.append(tmp)
  tmp=os.popen('xml_archangel -o '+prefix+' re_bulge').read().replace('\n','')
  if 'not found' in tmp:
    line.append('0.')
  else:
    line.append(tmp)
  tmp=os.popen('xml_archangel -o '+prefix+' se_bulge').read().replace('\n','')
  if 'not found' in tmp:
    line.append('0.')
  else:
    line.append(tmp)
else:
  line=['0.','0.','0.','0.']

if '-sky' in sys.argv:
  line.append(sys.argv[sys.argv.index('-sky')+1])
else:
  tmp=os.popen('xml_archangel -o '+prefix+' prf_sky').read().replace('\n','')
  if 'not found' in tmp:
    tmp=os.popen('xml_archangel -o '+prefix+' sky').read().replace('\n','')
  if 'not found' in tmp:
    print 'no sky value - aborting'
    sys.exit()
  line.append(tmp)

tmp=os.popen('xml_archangel -o '+prefix+' scale').read().replace('\n','')
if 'not found' not in tmp:
  line.append(tmp)
else:
  line.append('1.')

tmp=os.popen('xml_archangel -o '+prefix+' zeropoint').read().replace('\n','')
if 'not found' not in tmp:
  try:
    exptime=float(os.popen('xml_archangel -o '+prefix+' exptime').read())
  except:
    exptime=1.
  if exptime != 0.:
    try:
      filter=os.popen('xml_archangel -o '+prefix+' filter').read().replace('\n','')
      k={'U':0.30,'B':0.20,'V':0.14,'R':0.10,'I':0.05}
      airmass=float(os.popen('xml_archangel -o '+prefix+' airmass').read())
      airmass=k[filter]*airmass
    except:
      airmass=0.
    line.append('%.3f' % (2.5*math.log10(exptime)-airmass+float(tmp)))
  else:
    line.append('%.3f' % float(tmp))
else:
  line.append('0.')

op=''
if '-sky' in sys.argv:
  op=' -sky '+sys.argv[sys.argv.index('-sky')+1]+' '
#  cmd='elapert -sky '+sys.argv[sys.argv.index('-sky')+1]+' '+file+' | grep -v NAN | grep -v nan > el.tmp'
if '-fit' in sys.argv:
  cmd=' -fit '
#  cmd='elapert -fit '+file+' | grep -v NAN | grep -v nan > el.tmp'
cmd='elapert '+op+file+' | grep -v NAN | grep -v nan > el.tmp'
if '-q' not in sys.argv: print cmd
os.system(cmd)

if '-fit' in sys.argv:
  if '-sky' in sys.argv:
    cmd='quick_elapert '+file+' 0. 0. 0. 0. '+sys.argv[sys.argv.index('-sky')+1]+' '+line[-2]+' '+line[-1]
  else:
    cmd='quick_elapert '+file+' 0. 0. 0. 0. '+line[-3]+' '+line[-2]+' '+line[-1]
  cmd=cmd+' | grep -v NAN | grep -v nan >> el.tmp'
else:
  cmd='quick_elapert '+file
  for t in line:
    cmd=cmd+' '+t
  cmd=cmd+' | grep -v NAN | grep -v nan >> el.tmp'

if '-q' not in sys.argv: print cmd
os.system(cmd)

cmd='cat el.tmp | grep -v nan | grep -v NAN | xml_archangel -a '+prefix+' ept'
if '-q' not in sys.argv: print cmd
os.system(cmd)
os.remove('el.tmp')
os.remove('tmp.prf')

if '-fake' in sys.argv and '-no_asym' not in sys.argv:
  cmd='asymptotic '+prefix
  if '-q' not in sys.argv: print cmd
  os.system(cmd)
