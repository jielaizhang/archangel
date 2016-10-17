#!/usr/bin/env python

# general g77 compile commands, searches for setup.py, if not
# found in upper directories, finds correct platform and options

import os, sys

if len(sys.argv) <= 1:
  print 'generic compile parser'
  print 'Usage: q file_to_be_compiled'
  sys.exit()

# look for a setup.py file in current and top directories

try:
  back=os.getcwd()
  files=os.listdir('.')
  if 'setup.py' in files: 
    root='.'
  else:
    if os.getcwd() != os.environ['HOME']:
      while 1:
        os.chdir('..')
        if os.getcwd() == os.environ['HOME']: break
        files=os.listdir('.')
        if 'setup.py' in files: root=os.getcwd()

except:
  print 'error in directory structure (?)'
  sys.exit()

try:
  cmd=root+'/setup.py '+sys.argv[1] 
  os.system('cd '+root+' ; '+cmd)
  sys.exit()
except SystemExit:
  sys.exit()
except:
  pass

# setup.py not found, do standard compile

try:
  os.chdir(back)  # return to original directory
  complier='g77 '
  options=''
  file=sys.argv[-1].split('.')[0]

# open file and search for commands that indicate options needed

  check=open(file+'.f','r').read()
  if 'finit-local-zero' in check: options=options+' -finit-local-zero'
  if check.find('pgbegin') > 0: options=options+' -finit-local-zero -lpgplot -L/usr/X11R6/lib -lX11 -L/usr/lib -lgcc'
  if check.find('ftopen') > 0:
    if os.uname()[0] == 'Darwin': # platform check
      options=options+' -L/usr/local/cfitsio -L/usr/lib -lcfitsio -lm -lgcc'
    elif os.uname()[0] == 'SunOS':
      options=options+' -L/usr/local/cfitsio -lcfitsio -lnsl -lm -lsocket'

  cmd=complier+file+'.f -o '+file+options
  print cmd
  os.system(cmd)

except:
  print 'file',file+'.f','not found'
