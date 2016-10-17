#!/usr/bin/env python

import sys,os.path
from xml_archangel import *

if __name__ == "__main__":

  if sys.argv[1] == '-h':
    print 'xml_smash file_name'
    print
    print 'build xml file from flat data files'
    sys.exit()

  master={'cal':['zeropoint','scale'],'sky':['sky','skysig','nsky'],'prf':['prf'], \
          'sfb':['sfb','re','se','alpha','mu_o'],'ept':['ept'],'asym':['rad','asym','asym_err']}

  out=xml_write(sys.argv[-1]+'.xml','archangel')

  for x in master.keys():
    if 'prf' == x:
      prf=['INTENS', 'INT_ERR', 'GRAD', 'RAD', 'RMSRES', 'FOURSL', 'ITER', 'NUM', 'RESID_1', 'RESID_2', 'RESID_3', \
           'RESID_4', 'ECC', 'POSANG', 'X0', 'Y0', 'FOUR_2', 'THIRD_2']
      data=[tmp.split() for tmp in open(sys.argv[-1]+'.prf','r').readlines()]
      out.dump('  <array name=\'prf\'>\n')
      for t in prf:
        out.dump('    <axis name=\''+t+'\'>\n')
        for line in data:
          out.dump('      '+line[prf.index(t)]+'\n')
        out.dump('    </axis>\n')
      out.dump('  </array>\n')

    if 'cal' == x:
      data=[tmp.split() for tmp in open(sys.argv[-1]+'.cal','r').readlines()]
      out.dump('  <scale units=\'arcsecs/pixel\'>\n')
      out.dump('    '+data[0][0]+'\n')
      out.dump('  </scale>\n')
      out.dump('  <zeropoint>\n')
      out.dump('    '+data[0][1]+'\n')
      out.dump('  </zeropoint>\n')

    if 'ept' == x:
      try:
        data=[tmp.split() for tmp in open(sys.argv[-1]+'.ept','r').readlines()]
      except:
        continue
      ept=['radius','mag','area']
      out.dump('  <array name=\'ept\'>\n')
      for t in ept:
        out.dump('    <axis name=\''+t+'\'>\n')
        for line in data[1:]:
          out.dump('      '+line[ept.index(t)]+'\n')
        out.dump('    </axis>\n')
      out.dump('  </array>\n')

    if 'sfb' == x:
      try:
        data=[tmp.split() for tmp in open(sys.argv[-1]+'.sfb','r').readlines()]
      except:
        continue
      if float(data[0][0]) != 0:
        out.dump('  <mu_o units=\'mags/arcsecs**2\'>\n')
        out.dump('    '+data[0][0]+'\n')
        out.dump('  </mu_o>\n')
        out.dump('  <alpha units=\'arcsecs\'>\n')
        out.dump('    '+data[0][1]+'\n')
        out.dump('  </alpha>\n')
      if float(data[0][3]) != 0:
        out.dump('  <se units=\'mags/arcsecs**2\'>\n')
        out.dump('    '+data[0][2]+'\n')
        out.dump('  </se>\n')
        out.dump('  <re units=\'arcsecs\'>\n')
        out.dump('    '+data[0][3]+'\n')
        out.dump('  </re>\n')
      out.dump('  <array name=\'sfb\'>\n')
      sfb=['radius','mu','kill']
      for t in sfb:
        out.dump('    <axis name=\''+t+'\'>\n')
        for line in data[1:]:
          if t == 'kill':
            tmp=abs(int(line[sfb.index(t)])-1)
            out.dump('      '+str(tmp)+'\n')
          else:
            out.dump('      '+line[sfb.index(t)]+'\n')
        out.dump('    </axis>\n')
      out.dump('  </array>\n')

    if 'sky' == x:
      cmd='sky_box -f '+sys.argv[-1]+'.clean'
      sky=os.popen(cmd).read()
      if len(sky) < 1 or 'error' in sky:
        print 'error in figuring out sky, aborting'
        sys.exit()
      out.dump('  <sky units=\'DN\'>\n')
      out.dump('    '+sky.split()[2]+'\n')
      out.dump('  </sky>\n')
      out.dump('  <skysig units=\'DN\'>\n')
      out.dump('    '+sky.split()[3]+'\n')
      out.dump('  </skysig>\n')
      out.dump('  <nsky units=\'# of boxes\'>\n')
      out.dump('    '+sky.split()[4]+'\n')
      out.dump('  </nsky>\n')

    if 'asym' == x:
      try:
        data=[tmp.split() for tmp in open(sys.argv[-1]+'.asym','r').readlines()]
      except:
        continue
      try:
        out.dump('  <tot_rad_raw units=\'log arcsecs\'>\n    '+data[0][0]+'\n  </tot_rad_raw>\n')
        out.dump('  <tot_mag_raw units=\'mags\'>\n    '+data[0][1]+'\n  </tot_mag_raw>\n')
        out.dump('  <tot_mag_raw_err units=\'mags\'>\n    '+data[0][2]+'\n  </tot_mag_raw_err>\n')
        out.dump('  <tot_rad_exp units=\'log arcsecs\'>\n    '+data[1][0]+'\n  </tot_rad_exp>\n')
        out.dump('  <tot_mag_exp units=\'mags\'>\n    '+data[1][1]+'\n  </tot_mag_exp>\n')
        out.dump('  <tot_mag_exp_err units=\'mags\'>\n    '+data[1][2]+'\n  </tot_mag_exp_err>\n')
        out.dump('  <tot_mag_asym units=\'mags\'>\n    '+data[3][0]+'\n  </tot_mag_asym>\n')
      except:
        pass

  out.close()
