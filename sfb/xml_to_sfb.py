#!/usr/bin/env python

import sys,os,subprocess,numpy,math
from xml_archangel import *

def help():
  return '''
Usage: xml_to_sfb option file_name

take xml file and make sfb data, or reverse

options: -v = output, do not alter xml file
         -x = make an xml file from sfb file (radius,sfb)
         -e = make an xml file from ept file (radius,sfb)
'''

if __name__ == '__main__':

  if sys.argv[1] == '-h':
    print help()
    sys.exit()

  if '-x' in sys.argv or '-e' in sys.argv:
    print "<?xml version = '1.0'?>"
    print "<archangel>"
    print "  <array name='sfb'>"
    data=[tmp.split() for tmp in open(sys.argv[-1],'r').readlines()]
    print "    <axis name='radius'>"
    for z in data:
      print '     ',z[0]
    print "    </axis>"
    print "    <axis name='mu'>"
    for z in data:
      if '-x' in sys.argv:
        print '     ',z[1]
      else:
        print '     ',z[3]
    print "    </axis>"
    print "    <axis name='kill'>"
    for z in data:
      print '     1'
    print "    </axis>"
    print "    <axis name='error'>"
    for z in data:
      if '-x' in sys.argv:
#        err=1./(abs(26.-float(z[1])))
#        print '     '+str(err)
        print '     0.000'
      else:
        print '    ',z[4]
    print "    </axis>"
    print "  </array>"
    print "  <array name='prf'>"
    print "    <axis name='INTENS'>"
    for z in data: print '     0.000'
    print "    </axis>"
    print "    <axis name='INT_ERR'>"
    for z in data: print '     1.000'
    print "    </axis>"
    print "    <axis name='GRAD'>"
    for z in data: print '     0.000'
    print "    </axis>"
    print "    <axis name='RAD'>"
    for z in data: print '     ',z[0]
    print "    </axis>"
    print "    <axis name='RMSRES'>"
    for z in data: print '     1.000'
    print "    </axis>"
    print "    <axis name='FOURSL'>"
    for z in data: print '     0.000'
    print "    </axis>"
    print "    <axis name='ITER'>"
    for z in data: print '     0.000'
    print "    </axis>"
    print "    <axis name='NUM'>"
    for z in data: print '     0.000'
    print "    </axis>"
    print "    <axis name='RESID_1'>"
    for z in data: print '     0.000'
    print "    </axis>"
    print "    <axis name='RESID_2'>"
    for z in data: print '     0.000'
    print "    </axis>"
    print "    <axis name='RESID_3'>"
    for z in data: print '     0.000'
    print "    </axis>"
    print "    <axis name='RESID_4'>"
    for z in data: print '     0.000'
    print "    </axis>"
    print "    <axis name='ECC'>"
    for z in data: print '     0.000'
    print "    </axis>"
    print "    <axis name='POSANG'>"
    for z in data: print '     0.000'
    print "    </axis>"
    print "    <axis name='X0'>"
    for z in data: print '     1.000'
    print "    </axis>"
    print "    <axis name='Y0'>"
    for z in data: print '     1.000'
    print "    </axis>"
    print "    <axis name='FOUR_2'>"
    for z in data: print '     0.000'
    print "    </axis>"
    print "    <axis name='THIRD_2'>"
    for z in data: print '     0.000'
    print "    </axis>"
    print "  </array>"
    print "</archangel>"

  else:
    filename=sys.argv[-1].split('.')[0]

    if os.path.exists(filename+'.xml'):
      doc = minidom.parse(filename+'.xml')
      rootNode = doc.documentElement
      elements=xml_read(rootNode).walk(rootNode)
    else:
      print 'file error'
      sys.exit()

    try:
      sky=float(elements['sky'][0][1])
    except:
      print 'sky value not found, setting to zero'
      sky=0.
    try:
      skysig=float(elements['skysig'][0][1])
    except:
      print 'skysig not found, setting to one'
      skysig=1.

    try:
      xscale=float(elements['scale'][0][1])
    except:
      print 'pixel scale value not found, setting to one'
      xscale=1.
    try:
      cons=float(elements['zeropoint'][0][1])
    except:
      print 'zeropoint not found, setting to 25.'
      cons=25.

    for t in elements['array']:
      if t[0]['name'] == 'prf':
        prf=[]
        data=[]
        head=[]
        for z in t[2]['axis']:
          prf.append(map(float,z[1].split('\n')))
          head.append(z[0]['name'])
        for z in range(len(prf[0])):
          err1=prf[head.index('RMSRES')][z]/(prf[head.index('NUM')][z])**0.5
          err2=skysig/(2.)**0.5 # note sqrt(2) kluge
          data.append([prf[head.index('RAD')][z],prf[head.index('INTENS')][z],1,(err1**2+err2**2)**0.5])
        tmp=numpy.array(prf)
        prf=numpy.swapaxes(tmp,1,0)

    line='radius mu kill error\n'
    for t in data:
      if t[1] - sky > 0: 
        err=abs(-2.5*math.log10((t[1]-sky)/(xscale**2))+cons- \
            (-2.5*math.log10((t[1]+t[3]-sky)/(xscale**2))+cons))
        line=line+'%.2f' % (t[0]*xscale)+' '+'%.3f' % (-2.5*math.log10((t[1]-sky)/(xscale**2))+cons)+' 1 '+'%.3f' % err+'\n'

    if '-v' not in sys.argv:
      p=subprocess.Popen('xml_archangel -a '+filename+' sfb ', \
                          shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
      p.communicate(line[:-1])
    else:
      print line
