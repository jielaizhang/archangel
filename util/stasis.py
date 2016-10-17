#!/usr/bin/env python

import os, commands

os.chdir(os.environ['HOME'])

cmd='find archangel -type f -print | grep -v bin > stasis.log'
print '\n'+cmd
os.system(cmd)
vers=open('archangel/version','r').read().split()[0]
cmd='gnutar -T stasis.log -cf - | gzip -cf > archangel_'+vers+'.tar.gz'
print '\n'+cmd
os.system(cmd)

#if os.environ['USER'] == 'js' and os.path.isdir('/Volumes/CRUCIAL'):
#  cmd='gnutar -T archangel/stasis.log -cf - | gzip -cf > /Volumes/CRUCIAL/archangel.tar.gz'
#  print '\n'+cmd
#  tmp=commands.getstatusoutput(cmd)
#else:
#  cmd='gnutar -T archangel/stasis.log -cf - | gzip -cf > archangel.tar.gz'
#  print '\n'+cmd
#  os.system(cmd)
