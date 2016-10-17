#!/usr/bin/env python

import sys,os,os.path

def help():
  return '''
Usage: prf_to_xml file_name

take prf file put in or make an xml file
'''

if __name__ == '__main__':

  if sys.argv[1] == '-h':
    print help()
    sys.exit()

  if not os.path.isfile(sys.argv[-1].split('.')[0]+'.xml'):
    cmd='xml_archangel -c '+sys.argv[-1].split('.')[0]+' archangel'
    print cmd
    os.system(cmd)

  open('xml.tmp','w').write('INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 '+ \
                          'RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n')
  cmd='cat xml.tmp '+sys.argv[-1]+' | xml_archangel -a '+sys.argv[-1].split('.')[0]+' prf'
  print cmd
  os.system(cmd)
