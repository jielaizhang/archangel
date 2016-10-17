#!/usr/bin/env python

# compile commands for archangel directory

# note: imstat is screwed up with [] from shell, need this
# in your .cshrc
# alias imstat '~/archangel/util/imstat.py "\!*"'

# note: gfortran gasp.f -o gasp -L/usr/local/cfitsio -lcfitsio -fno-range-check -finit-local-zero -fno-automatic 

import os, sys

bin=os.getcwd()+'/bin'
if not os.path.exists(bin):
  try:
    bin=open('bin.archangel','r').read()
  except:
    if sys.argv[-1] in ['./setup.py','basic','build','links']:
      pass
    else:
      print 'options are basic, build, links'
      sys.exit()

top=os.getcwd()
complier='gfortran '
options=''
file=sys.argv[-1].split('.')[0]

if sys.argv[-1] in ['./setup.py','basic','build']:

  print 'Welcome to Archangel v4.3, I\'m going to test your system for'
  print 'correct versions of various packages and then install the tools'
  print 'Hopefully, you have read the README file to understand what is'
  print 'happening.'

  print
  print '--------------------------------------------------------------'
  print 'testing for Python version 2.3 or greater ... ',
  vers=sys.version_info[0]+0.1*sys.version_info[1]
  if vers < 2.3:
    print 'failed'
    print
    print 'You need a version of python that is greater than 2.3.  Sorry, but'
    print 'os.walk (only found in versions greater than 2.3) is used by setup.'
    print
    print 'exiting..........'
    sys.exit()
  else:
    print 'ok'

  print 'testing for numarray or numpy package ... ',
  try:
    import numpy
    print 'ok, numpy'
  except:
    try:
      import numarray
      print 'ok, numarray'
    except:
      print 'failed'
      print
      print 'Your version of python does not include numarray or numpy.  Several'
      print 'important things will fail without numarray.  You will need to goto'
      print 'the PyRAF website and upgrade your python with numarray.'
      print
      print 'exiting..........'
      sys.exit()

  print 'testing for pyfits package ... ',
  try:
    import astropy.io.fits as pyfits
    print 'ok'
  except:
    print 'failed'
    print
    print 'Your version of python does not include pyfits.  Several'
    print 'important things will fail without pyfits.  You will need to goto'
    print 'the PyRAF website and upgrade your version of Python with pyfits.'
    print
    print 'exiting..........'
    sys.exit()

  try:
    print 'testing for gfortran complier ... ',
    test=os.popen('which gfortran').read()
    if 'no gfortran' in test:
      print 'not found'
    else:
      print 'ok, found at',test.replace('/gfortran\n','')
      print 'note: none of the graphic GUI\'s will work with gfortran'
      complier='gfortran '
      raise StopIteration
    print '\n*** no FORTRAN compliers found, aborting ***'
    sys.exit()
  except StopIteration:
    pass

  print 'testing for cfitsio libs ... ',
  try:
    t=os.popen(complier+' util/cfitsio_test.f -o junk -L/opt/local/cfitsio -lcfitsio -fno-range-check -finit-local-zero -fno-automatic').read()
    if 'g' not in t:
      r=os.popen('./junk examples/ned_test.fits').read()
      if '0' in r:
        print 'ok'
      else:
        print 'failed, you need to check your cfitio installation'
        print
        print 'exiting..........'
        sys.exit()
    else:
      print 'failed, you need to install cfitsio'
      print
      print 'exiting..........'
      sys.exit()
    os.system('rm junk')
  except:
    raise
    print
    print 'exiting..........'
    sys.exit()

  print 'testing for pylab/matplotlib package ... ',
  try:
    import pylab
    print 'ok'
  except:
    print 'failed'
    print 'testing for ppgplot package ... ',
    try:
      import ppgplot
      print 'ok'
    except:
      print 'failed'
      print
      print 'Your version of python does not include ppgplot nor matplotlib.  While'
      print 'ppgplot/matplotlib is not needed for the core routines, many of the higher'
      print 'level tools need a graphics interface.  You can install Archangel without'
      print 'the graphics, or you can get ppgplot from the authors website'
      print '(abyss.uoregon.edu/~js) and install it in /usr/local (this is highly'
      print 'recommended as ppgplot is a superior plotting package that interfaces'
      print 'PGPLOT and python).  Or get matplotlib from its website.'
      print
      print 'Note: we are currently migrating to matplotlib to get away from X windows,'
      print 'so all upgrades and additions will be to matplotlib routines (if this influences'
      print 'your decision above).'
      print
      test=raw_input('Do you wish to continue with install? (y)/n: ')
      if test == 'n':
        print 'exiting..........'
        sys.exit()
  print '--------------------------------------------------------------'
  print

  if len(file) == 0 or file == 'setup':
    print 'You did not pick an option!  The options are basic, build, or links.  Or you'
    print 'can give me a file name to re-compile'
    print
    print 'basic - makes a version that requires no graphics, only command line programs'
    print 'build - makes the full graphics version'
    print 'links - re-builds the links (basic and build does this too)'
    print
    print 'Start again and type "python setup.py option" or "./setup.py option'
    sys.exit()

  if not os.path.exists(bin):
    try:
      bin=open('bin.archangel','r').read()
    except:
      print 'Ok, here is the only decision you have to make, where do you want the executables'
      print 'to be placed?  We recommend, -----> '+bin
      print 'so the package is all in one directory.  However, you can place the binaries and'
      print 'links anywhere you want (/usr/local? you running this as su?).  So hit <RETURN> for'
      print 'default directory, or type in your own.'
      print
      test=raw_input('Binaries going to -> '+bin+', Ok?: ')
      if test:
        bin=test
        if not os.path.exists(bin):
          print 'That directory does not exist! Do a mkdir and start again.'
          print
          print 'exiting .........'
          sys.exit()
        tmp=open('bin.archangel','w').write(bin)
      else:
        os.system('mkdir '+bin)
        print
        print 'mkdir',bin
        print

#  bin=(len(os.getcwd().split('/'))-os.getcwd().split('/').index(top)-1)*'../'+'bin/'
#  bin=os.environ['HOME']+'/bin/'

basic_files=['make_fake','ims_clean','iso_prf','prf_clean','efit','gasp_images','sky_box','mask', \
             'quick_elapert','build_norm']
link_files=['profile','offset','offset_imshift','offset_mask','mark','find_target', \
            'quick_scan','brute_prf','prf_smooth','clean_blanks','sky_norm','keys', \
            'extreme_lsb','thres_prf','min_max','cir_apert', \
            'elapert','xml_archangel','el','lines','dss_read','cosmo','DSS_XY','hms','fake', \
            'prf_edit','widgets','ned_xml','scan_target','imarith','imstat','imhead','prf_to_xml', \
            'xits','bdd','residuals','grid_phot','petrosian','ned_photometry','2mass_stitch', \
            'two_color','subtract_stars','grid_dump','extract_isophote','sfb_plot','gen_rad_sfb', \
            'total_colors','asymptotic','hist','pick','probe','aperture','contour','chi_grid', \
            'chi_min','fchisq','auto_fit','compare_sersic','double_exp','imcopy',  \
            'peak','centroid','xy2sky','contour_overlay','peek_image','qphot','blink', \
            'hyper_mongo','polyfit','interp','ned_coords','moving_avg']

# overseer trap background jobs
plot_files=['hist','pick','probe']

move_files=['xml/xml_archangel.pyc','util/matfunc.pyc','util/fltstrm','util/opstrm']
for t in move_files:
  os.system('cp -f '+t+' '+bin)

try:
  if sys.argv[-1] == 'build' or sys.argv[-1] == 'basic':

    print 'Building entire archangel system'
    print 'operating system',os.uname()[0]
    print 'top =',os.getcwd()
    print 'compiler',complier
    print 'bin directory',bin
    for file in basic_files:
      options=''
      try:
        done=0
        for root, dirs, files in os.walk('.'):
          for name in files:
             try:
               if name.split('.')[0] == file and name.split('.')[1] == 'f': 
                 check=open(root+'/'+file+'.f','r').read()
                 options=options+' -L/opt/local/cfitsio -lcfitsio -fno-range-check -finit-local-zero -fno-automatic'

#                 if check.find('pgbegin') > 0: options=options+' -finit-local-zero -L/usr/lib -lpgplot -lX11 -lgcc'
#                 if check.find('ftopen') > 0:
#                   if os.uname()[0] == 'Darwin':
#                     options=options+' -L/usr/local/cfitsio -L/usr/lib -lcfitsio -lm -lgcc'
#                   elif os.uname()[0] == 'Linux':
#                     options=options+' -L/usr/local/cfitsio -lcfitsio -lnsl -lm'
#                   else:
#                     options=options+' -L/usr/local/cfitsio -lcfitsio -lnsl -lm -lsocket'
                 cmd=complier+root+'/'+file+'.f -o '+bin+'/'+file+options
                 print cmd
                 os.system(cmd)
                 done=1
                 break
             except:
               pass
          if done: break
        if not done: print file+'.f','*not* found in the current or lower directories'
      except:
        pass

    for file in plot_files:
      suffix='_overseer'
      try:
        done=0
        for root, dirs, files in os.walk('.'): 
          for name in files:
             try:
               if name.split('.')[0] == file+suffix and name.split('.')[1] == 'py': 
                 cmd='ln -fs '+top+'/'+root.split('/')[-1]+'/'+file+suffix+'.py '+bin+'/'+file
                 print cmd
                 os.system(cmd)
                 done=1
                 break
             except:
               pass
          if done: break
        if not done: print '\n'+file,'*not* found in the current or lower directories\n'
      except:
        pass

    for file in link_files:
      try:
        done=0
        for root, dirs, files in os.walk('.'): 
          for name in files:
             try:
               if name.split('.')[0] == file and name.split('.')[1] == 'py': 
                 cmd='ln -fs '+top+'/'+root.split('/')[-1]+'/'+file+'.py '+bin+'/'+file
                 print cmd
                 os.system(cmd)
                 done=1
                 break
             except:
               pass
          if done: break
        if not done: print '\n'+file,'*not* found in the current or lower directories\n'
      except:
        pass

    print
    print 'Success! Now for things to work you need to add the following lines to your .cshrc'
    print
    print '     set path=($path '+bin+')'
    print '     setenv PYTHONPATH '+bin
    print
    print 'then source your .cshrc and rehash.  Good luck! Email jschombe@uoregon.edu with'
    print 'questions/comments'

  elif sys.argv[-1] == 'links':

    for file in plot_files:
      suffix='_overseer'
      if not os.path.islink(bin+'/'+file):
        try:
          done=0
          for root, dirs, files in os.walk('.'): 
            for name in files:
               try:
                 if name.split('.')[0] == file+suffix and name.split('.')[1] == 'py': 
                   cmd='ln -fs '+top+'/'+root.split('/')[-1]+'/'+file+suffix+'.py '+bin+'/'+file
                   print cmd
                   os.system(cmd)
                   done=1
                   break
               except:
                 pass
            if done: break
          if not done: print '\n'+file,'*not* found in the current or lower directories\n'
        except:
          pass

    for file in link_files:
      if not os.path.islink(bin+'/'+file):
        try:
          done=0
          for root, dirs, files in os.walk('.'): 
            for name in files:
               try:
                 if name.split('.')[0] == file and name.split('.')[1] == 'py': 
                   cmd='ln -fs '+top+'/'+root.split('/')[-1]+'/'+file+'.py '+bin+'/'+file
                   print cmd
                   os.system(cmd)
                   done=1
                   break
               except:
                 pass
            if done: break
          if not done: print '\n'+file,'*not* found in the current or lower directories\n'
        except:
          pass

#  elif sys.argv[-1] == 'chmod':
#    print 'chmod +x bin/*'
#    os.system('chmod +x bin/*')
#    print 'chmod +x */*.py'
#    os.system('chmod +x */*.py')

  else:

    try:
      done=0
      for root, dirs, files in os.walk('.'): 
        for name in files:
           try:
             if name.split('.')[0] == file and name.split('.')[1] == 'f': 
               check=open(root+'/'+file+'.f','r').read()
               options=options+' -L/opt/local/cfitsio -lcfitsio -fno-range-check -finit-local-zero -fno-automatic'

#               if check.find('pgbegin') > 0: 
#                 options=options+' -finit-local-zero -L/usr/lib -lpgplot -lX11 -lgcc'
#               elif check.find('ftopen') > 0:
#                 if os.uname()[0] == 'Darwin':
#                   options=options+' -L/usr/local/cfitsio -L/usr/lib -lcfitsio -lm -lgcc'
#                 elif os.uname()[0] == 'Linux':
#                   options=options+' -L/usr/local/cfitsio -lcfitsio -lnsl -lm'
#                 else:
#                   options=options+' -L/usr/local/cfitsio -lcfitsio -lnsl -lm -lsocket'
#               else:
#                 options=options+' -finit-local-zero -L/usr/lib -lgcc'
               cmd=complier+root+'/'+file+'.f -o '+bin+'/'+file+options
               print cmd
               os.system(cmd)
               done=1
               break
           except:
             pass
        if done: break
      if not done: print '\n'+file,'*not* found in the current or lower directories\n'
    except:
      raise

except SystemExit:
  sys.exit()

except:
  raise

