#!/usr/bin/env python

import os,sys,math
import tempfile

# Functions used to filter or massage lines in profile files

def removeLinesWithImaginaryNumbers(filename):
    f = open(filename,'r')
    lines = f.readlines()
    f.close()
    output = []
    for line in lines:
        if (('i' not in line) and ('I' not in line)):
            output.append(line)
    f.close()
    f = open(filename,'w')
    f.writelines(output)
    f.close()
    
def removeLinesWithNAN(filename):
    f = open(filename,'r')
    lines = f.readlines()
    f.close()
    output = []
    for line in lines:
        if (('nan' not in line) and ('NAN' not in line) and ('NaN' not in line)):
            output.append(line)
    f = open(filename,'w')
    f.writelines(output)
    f.close()
    
def replaceNANWithUnity(filename):
    f = open(filename,'r')
    lines = f.readlines()
    f.close()
    output = []
    for line in lines:
        line = line.replace("nan","1.0")
        line = line.replace("NAN","1.0")
        line = line.replace("NaN","1.0")
        output.append(line)
    f = open(filename,'w')
    f.writelines(output)
    f.close()
    
def JoinHeaderToProfileAndSaveToXMLFile(file1,file2,prefix):
    f = open(file1,'r')
    headerlines = f.readlines()
    f.close()
    f = open(file2,'r')
    bodylines = f.readlines()
    f.close()  
    output = headerlines + bodylines
    temporaryFile = tempfile.NamedTemporaryFile(delete=False)
    temporaryFile.writelines(output)
    temporaryFile.close()
    if os.name == 'nt':
        concatenateCommand = 'type'
    else:
        concatenateCommand = 'cat'
    cmd=('%s %s ' % (concatenateCommand, temporaryFile.name)) + ' | xml_archangel -a ' + prefix + ' prf'
    xcmd(cmd,verbose)
    os.unlink(temporaryFile.name)

def xcmd(cmd,verbose):
  global log
  if verbose: print '\n'+cmd
  if log: print >> log,'\n'+cmd
  tmp=os.popen(cmd)
  output=''
  for x in tmp: output+=x
  if 'abort' in output:
    failure=True
  else:
    failure=tmp.close()
  if failure:
    print 'execution of %s failed' % cmd
    print 'error is as follows',output
    sys.exit()
  else:
    return output

#============== MAIN PROGRAM ==============

# main - ellipse fitting script

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print ' '
  print 'Usage: profile file_name options'
  print ' '
  print 'Options: -h = this message'
  print '         -i = inspect ellipses after each fit'
  print '         -l = keep a log in prefix.log'
  print '        -xy = force center xc and yc'
  print '    -center = take center from probe'
  print '        -rx = radius to stop fitting'
  print '        -rs = radius to stop'
  print '        -sg = sigma for prf cleaning (default is 4)'
  print '  -no_clean = no cleaning inside this radius (if 0, no cleaning)'
  print '       -lsb = lsb ims clean, assume no gal'
  print '       -ell = elliptical galaxy, robust cleaning'
  print '       -dsk = sprial galaxy, limited cleaning, smooth for disk'
  print '       -spr = sprial galaxy, limited cleaning, normal smooth'
  print '       -ext = extreme LSB object, force fit'
  print '        -st = change starting radius for fit (default is 4 pixels)'
  print '      -fake = use fake subtraction'
  print '      -nosm = do not smooth final profile'
  print '  -no_probe = do not show fit'
  print '         -q = run quiet'
  sys.exit(0)

# read the data file (.fits?), its endifix and any options

home=os.environ['ARCHANGEL_HOME']

if '.' not in sys.argv[1]:
  prefix=sys.argv[1]
  endfix='fits'
else:
  prefix=sys.argv[1].split('.')[0]
  endfix=sys.argv[1].split('.')[1]
  if endfix == '': endfix='fits'

# determine if in quiet mode and/or keeping a log

s=' '.join(sys.argv[2:])

if '-q' in s:
  verbose=False
else:
  verbose=True

if '-l' in s:
  log=open(prefix+'.log','w')
else:
  log=None

# test for file

if not os.path.isfile(prefix+'.'+endfix):
  if verbose: print prefix+'.'+endfix+' not found, aborting'
  if log: print >> log,prefix+'.'+endfix+' not found, aborting'
  sys.exit(0)

# find the size of the file, nx and ny

cmd='keys -p '+prefix+'.'+endfix+' | grep NAXIS1'
nx=int(xcmd(cmd,False).split()[2])
cmd='keys -p '+prefix+'.'+endfix+' | grep NAXIS2'
ny=int(xcmd(cmd,False).split()[2])

# check if this is 2MASS data, open .xml file and enter calibration

if not os.path.isfile(prefix+'.xml'):
  cmd='xml_archangel -c '+prefix+' archangel'
  xcmd(cmd,verbose)
  first_time=1
else:
  first_time=0

cmd='keys -p '+prefix+'.'+endfix+' | grep ORIGIN'
test=os.popen(cmd).read()

if '2MASS' in test:
  cmd='xml_archangel -e '+prefix+' scale units=\'arcsecs/pixel\' 1.0'
  xcmd(cmd,verbose)
  # find zeropoint, assume last letter on prefix is bandpass
  cmd='keys -p '+prefix+'.'+endfix+' | grep '+prefix[-1].upper()+'MAGZP'
  if verbose: print cmd
  test=os.popen(cmd).read()
  if not test:
    cmd='keys -p '+prefix+'.'+endfix+' | grep MAGZP'
    if verbose: print cmd
    test=os.popen(cmd).read()
  cmd='xml_archangel -e '+prefix+' zeropoint '+test.split()[2]
  xcmd(cmd,verbose)

# start the fitting process, large try/except region

try:
  if verbose: print '\n**** Starting profile fitting for',prefix+'.'+endfix,'('+str(nx)+'x'+str(ny)+') ****'
  if log: print >> log,'\n**** Starting profile fitting for',prefix+'.'+endfix,'****'

# clean file of nonsense pixels (set to NaN) --> .raw, obsolete now just make .clean file

  if endfix != 'clean':
    if os.path.isfile(prefix+'.clean'):
      tmp=raw_input('Overwrite old .clean file? (y)/n: ')
      if tmp != 'n':
        cmd='cp -f '+prefix+'.'+endfix+' '+prefix+'.clean'
        xcmd(cmd,verbose)
    else:
      cmd='imhead '+prefix+'.'+endfix
      tmp=xcmd(cmd,verbose)
      if 'integer' in tmp:
        print 'converting integers to reals in .clean'
        cmd='imarith "'+prefix+'.'+endfix+' * 1. '+prefix+'.clean"'
        xcmd(cmd,verbose)
      else:
        cmd='cp -f '+prefix+'.'+endfix+' '+prefix+'.clean'
        xcmd(cmd,verbose)

#  if os.path.isfile(prefix+'.raw'):
#    print '\n**** using old .raw file ****'
#  else:
#    if '-noraw' in s:
#      cmd='cp -f '+prefix+'.'+endfix+' '+prefix+'.raw'
#      xcmd(cmd,verbose)
#    else:
#      cmd='clean_blanks -c '+prefix+'.'+endfix+' 100'
#      xcmd(cmd,verbose)

# read sky value or do rough border fit using sky_box

  try:
    cmd='xml_archangel -o '+prefix+' sky'
    xsky=xcmd(cmd,verbose).replace('\n','')
    if 'element not found' in xsky:
      if verbose: print 'sky not found in .xml file, will do it manually'
      if log: print >> log,'sky not found in .xml file, will do it manually'
      raise
    cmd='xml_archangel -o '+prefix+' skysig'
    skysig=xcmd(cmd,verbose).replace('\n','')
  except:
    cmd='sky_box -f '+prefix+'.clean'
    sky=xcmd(cmd,verbose)
    if 'error' in sky:
      print 'doing full sky search'
      cmd='sky_box -s '+prefix+'.clean'
      sky=xcmd(cmd,verbose)
    xsky=sky.split()[2]
    skysig=sky.split()[3]
    cmd='xml_archangel -e '+prefix+' sky '+xsky
    xcmd(cmd,verbose)
    cmd='xml_archangel -e '+prefix+' skysig '+skysig
    xcmd(cmd,verbose)

  if verbose:
    print 'sky = %5.1f' % float(xsky)
    print 'sigma = %5.1f' % float(skysig)
  if log:
    print >> log,'sky = %5.1f' % float(xsky)
    print >> log,'sigma = %5.1f' % float(skysig)

# first guess for center is middle of frame or given by user

  if '-xy' in s:
    ixc=s.split()[s.split().index('-xy')+1]
    iyc=s.split()[s.split().index('-xy')+2]
    print 'force using',ixc,iyc,'for center'
    if '-rx' in s:
      tmp=float(s.split()[s.split().index('-rx')+1])/3.
      rstop=str(int(tmp))
      router=int(s.split()[s.split().index('-rx')+1])
    else:
      router=nx/2.
      rstop=str(router/3.)
    eps=1.0
    theta='0.'
  else:
    ixc=str(nx/2)
    iyc=str(ny/2)

# define a high threshold cut for center search

    if '-center' not in s:
      cmd='min_max '+prefix+'.clean '+ixc+' '+iyc+' 4'
      tmp=xcmd(cmd,verbose)
      mx=float(tmp.split()[13])
      print 'tmp: ',tmp
      print 'mx: ',mx
      print 'sky: ',xsky
      cmd='gasp_images -f '+prefix+'.clean '+xsky+' '+str((mx-float(xsky))/3.)+' 10 false '+ \
          ' | grep -v NaN > '+prefix+'.ims'
      xcmd(cmd,verbose)
      if verbose: print '>> '+xcmd('wc '+prefix+'.ims',False).split()[0]+' targets found'
      if log: print >> log,'>> '+xcmd('wc '+prefix+'.ims',False).split()[0]+' targets found'

# find the galaxy target in the .ims file, weighted by area, new centers

      cmd='find_target -q '+prefix+'.ims '+ixc+' '+iyc+' '+str(nx/10)
      tmp=xcmd(cmd,verbose)
      if 'no target' not in tmp:
        ixc=tmp.split()[0]
        iyc=tmp.split()[1]
        rstop=tmp.split()[2]
        eps=float(tmp.split()[3])
        theta=tmp.split()[4]
        cmd='find_target -s '+prefix+'.ims '+ixc+' '+iyc+' '+str(nx/10)+' > s.tmp'
        tmp=xcmd(cmd,verbose)
      else:
        ixc=str(nx/2)
        iyc=str(ny/2)

    if '-no_probe' not in s:
      if endfix != 'clean':
        tmp=os.popen('probe -s -i -v '+prefix+'.'+endfix).read()
        os.system('cp -f '+prefix+'.clean '+prefix+'.backup')
        print 'cp -f '+prefix+'.clean '+prefix+'.backup'
      if tmp:
        if 'abort' in tmp.lower():
          if first_time:
            os.remove(prefix+'.xml')
            os.remove(prefix+'.ims')
          print tmp[:-1]; sys.exit()
        elif '-center' in s:
          ixc=tmp.split()[-2]
          iyc=tmp.split()[-1]
          print 'using',ixc,'and',iyc,'for center from probe'
          try:
            cmd='xml_archangel -o '+prefix+' sky'
            xsky=xcmd(cmd,False).replace('\n','')
            cmd='xml_archangel -o '+prefix+' skysig'
            skysig=xcmd(cmd,False).replace('\n','')
          except:
            pass
        
        if verbose: print '**** added',tmp[:-1],'option'
        s=s+' '+tmp[:-1]
    try:
      os.remove('s.tmp')
    except:
      pass

# locate all the objects for cleaning and outer edge determination of target

  if '-lsb' in s or '-ext' in s:
    search_sig=5.
  else:
    search_sig=25.
  cmd='gasp_images -f '+prefix+'.clean '+xsky+' '+str(search_sig*float(skysig))+' 10 false '+ \
      ' | grep -v NaN > '+prefix+'.ims'
  xcmd(cmd,verbose)
  if verbose: print '>> '+xcmd('wc '+prefix+'.ims',False).split()[0]+' targets found'
  if log: print >> log,'>> '+xcmd('wc '+prefix+'.ims',False).split()[0]+' targets found'
  cmd='find_target -q '+prefix+'.ims '+ixc+' '+iyc+' '+str(nx/10)
  tmp=xcmd(cmd,verbose)
#XXXXXXX
  #cmd='gasp_images -f '+prefix+'.clean '+xsky+' '+str(search_sig*float(skysig))+' 10 false '+ \
  #    ' | grep -v NaN | fltstrm c c r 0 '+str(0.05*nx*nx)+' c c c > '+prefix+'.ims'
  #xcmd(cmd,verbose)

# rstop is place to stop fitting (the 5 sigma level, or above for lsb), or given by user

  if 'no target' in tmp and '-xy' not in s and '-rx' not in s:
    if verbose: print 'cant find the galaxy, use -xy and -rs options'
    if log: print >> log,'cant find the galaxy, use -xy and -rs options'
    for fix in ['.iso_prf','.fake','.ims']:
      if os.path.isfile(prefix+fix): os.remove(prefix+fix)
    sys.exit(0)
  else:
    if '-rx' in s:
      tmp=float(s.split()[s.split().index('-rx')+1])/3.
      rstop=str(int(tmp))
      router=int(s.split()[s.split().index('-rx')+1])
      eps=1.0
      theta='0.'
    elif '-lsb' not in s:
      rstop=tmp.split()[2]
      eps=float(tmp.split()[3])
      theta=tmp.split()[4]

  if float(rstop) > 1200: rstop='1200'
  if verbose: print '\nCenter determined to be',ixc,iyc,' outer fit edge = ',rstop
  if log: print >> log,'\nCenter determined to be',ixc,iyc,' outer edge = ',rstop

# abort is galaxy is too flat, need to brute force it

  if eps < 0.02:
    if verbose: print '\n**** WARNING - this is a very thin galaxy ****',eps
    if log: print >> log,'\n**** WARNING - this is a very thin galaxy ****'
    sys.exit(0)

# router is place to stop calculating all ellipses

  if '-rx' not in s:
    router=int(max((float(rstop)+float(rstop)*0.80),min(nx,ny)/2.))
    if '-lsb' in s: router=int(min(nx,ny)/2.+min(nx,ny)/6.)
  
  if '-rs' in sys.argv:
    router=float(s.split()[s.split().index('-rs')+1])

  if verbose: print '\nOuter stop radius set to','%1.0f' % router
  if log: print >> log,'\nOuter stop radius set to','%1.0f' % router

# set the deleion sigmas depending on what kind of galaxy is being fit, default is elliptical

  if '-sg' in s: 
    sig=s.split()[s.split().index('-sg')+1]
    prof_sig=str(10*int(sig))
  else:
    if '-lsb' in s:
      sig='6'
      prof_sig='0'
    elif '-spr' in s or '-dsk' in s:
      sig='6'
      prof_sig='0'
    else:
      sig='4'
      prof_sig='50'
  if '-no_clean' in s:
    sig='0'
    prof_sig='0'

# clean off all other stuff outside of fitting radius

  if '-no_clean' in s:
    clean_rad=float(s.split()[s.split().index('-no_clean')+1])
  else:
    clean_rad=1.5*float(rstop)
  if clean_rad > 0:
    if '-lsb' in s:
      cmd='ims_clean -q '+prefix+'.clean '+prefix+'.ims 1.5 '+ixc+' '+iyc+' 0'
    elif '-ext' in s:
      cmd='ims_clean -q '+prefix+'.clean '+prefix+'.ims 1.5 '+ixc+' '+iyc+' '+str(clean_rad)+' '+str(eps)+' '+theta
    else:
      cmd='ims_clean -q '+prefix+'.clean '+prefix+'.ims 1.5 '+ixc+' '+iyc+' '+str(clean_rad)+' '+str(eps)+' '+theta
    tmp=xcmd(cmd,verbose)
  if '-i' in s:
    print '\ndisplaying cleaned image',
    xcmd('probe '+prefix+'.clean',verbose)

# cleaning done, if this is an extreme LSB object, do a brute force and exit, good-luck

  if '-ext' in s:
    if clean_rad > 0:
      cmd='extreme_lsb '+prefix+'.clean '+ixc+' '+iyc+' '+str(min(nx,ny))+' '+str(clean_rad)
    else:
      cmd='extreme_lsb -c '+prefix+'.clean '+ixc+' '+iyc+' '+str(min(nx,ny))
    print '\n'+cmd
    os.system(cmd)
    for fix in ['.iso_prf','.fake','.ims']:
      if os.path.isfile(prefix+fix): os.remove(prefix+fix)
    sys.exit(0)

# erase the old jedsub file, cleaned output from ellipse fitting

  if os.path.isfile(prefix+'.jedsub'): os.remove(prefix+'.jedsub')

# ok, the big fitting

  if '-st' in s: 
    tmp=s.split()[s.split().index('-st')+1]
    cmd='efit -q '+prefix+'.clean '+prefix+'.prf -xy '+ixc+' '+iyc+' -sg '+prof_sig+' -rx '+ \
         rstop+' -rs '+str(router/3.)+' -st '+tmp
  else:
    cmd='efit -q '+prefix+'.clean '+prefix+'.prf -xy '+ixc+' '+iyc+' -sg '+prof_sig+' -rx '+rstop+' -rs '+str(router/3.)
  xcmd(cmd,verbose)
  if not os.path.isfile(prefix+'.prf'):
    if verbose: print 'prf file error, aborting'
    if log: print >> log,'prf file error, aborting'
    sys.exit(0)
  tmp=xcmd('wc '+prefix+'.prf',False)
  if verbose: print '>> '+tmp.split()[0]+' ellipses found'
  if log: print >> log,'>> '+tmp.split()[0]+' ellipses found'
  if int(tmp.split()[0]) < 3:
    print '>>>> too few ellipses, aborting <<<<'
    sys.exit()
  if tmp.split()[0] == '0':
      if verbose: print 'efit failure on initial fit - aborting'
      if log: print>> log,'efit failure on initial fit - aborting'
      sys.exit(0)

# mv .jedsub file to .clean, smooth first run of ellipses with prf_smooth, 1st write to xml file

  if os.path.isfile(prefix+'.jedsub'):
    cmd='mv -f '+prefix+'.jedsub '+prefix+'.clean'
    xcmd(cmd,False)
  if '-nosm' not in sys.argv:
    cmd='prf_smooth -q '+prefix+'.prf > tmp.prf'
    xcmd(cmd,verbose)
    replaceNANWithUnity(prefix + '.prf')
    os.remove('tmp.prf')
  if '-i' in s:
    open('tmp.tmp','w').write('INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 '+ \
               'RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n')
    JoinHeaderToProfileAndSaveToXMLFile('tmp.tmp',prefix + '.prf',prefix)
    os.remove('tmp.tmp')
    xcmd('probe -t '+prefix+'.clean',verbose)

# clean along isophotes, 4 sigma

  if sig != '0' and clean_rad > 0:
#    cmd='prf_clean -s '+prefix+'.clean '+prefix+'.prf '+sig+' '+str(clean_rad)
    cmd='prf_clean -s '+prefix+'.clean '+prefix+'.prf '+sig+' 10'
    xcmd(cmd,verbose)
    if os.path.isfile(prefix+'.prf_clean'):
      cmd='mv -f '+prefix+'.prf_clean '+prefix+'.clean'
      xcmd(cmd,False)
    if '-i' in s: xcmd('probe -t '+prefix+'.clean',verbose)

# 2nd fit, with cleaned file, out to far edge, 1st determine mean ecc for sigma deletions

  file=open(prefix+'.prf','r')
  eps=0.
  npts=0
  for line in file:
    if float(line.split()[3]) > 5 and float(line.split()[3]) < 25:
      eps=eps+float(line.split()[12])
      npts+=1
  file.close()
  if npts == 0:
    file=open(prefix+'.prf','r')
    for line in file:
      eps=eps+float(line.split()[12])
      npts+=1
    file.close()
  eps=eps/npts

  if '-st' in s and '-rx' not in s: 
    tmp=s.split()[s.split().index('-st')+1]
    cmd='efit -q '+prefix+'.clean '+prefix+'.prf -xy '+ixc+' '+iyc+' -sg '+prof_sig+' -rx '+ \
         rstop+' -rs -'+str(router)+' -st '+tmp
  if '-st' in s and '-rx' in s: 
    tmp=s.split()[s.split().index('-st')+1]
    cmd='efit -q '+prefix+'.clean '+prefix+'.prf -xy '+ixc+' '+iyc+' -sg '+prof_sig+' -rx '+ \
         rstop+' -rs '+str(router)+' -st '+tmp
  else:
    cmd='efit -q '+prefix+'.clean '+prefix+'.prf -xy '+ixc+' '+iyc+' -sg '+prof_sig+' -rx '+rstop+' -rs '+str(router)
  xcmd(cmd,verbose)
  os.system('grep -v -i I '+prefix+'.prf > tmp.tmp')
  os.system('mv -f tmp.tmp '+prefix+'.prf')
  tmp=os.popen('wc '+prefix+'.prf').read()
  if verbose: print '>> '+tmp.split()[0]+' ellipses found'
  if log: print >> log,'>> '+tmp.split()[0]+' ellipses found'
  if int(tmp.split()[0]) < 3:
    print '>>>> too few ellipses, aborting <<<<'
    sys.exit()
  if os.path.isfile(prefix+'.jedsub'):
    cmd='mv -f '+prefix+'.jedsub '+prefix+'.clean'
    os.system(cmd)

# first smooth ellipses, build a fake model, subtract from file, find new ims_clean, fit again

  if '-nosm' not in sys.argv:
    cmd='prf_smooth -q '+prefix+'.prf > tmp.prf'
    xcmd(cmd,verbose)
    replaceNANWithUnity('tmp.prf')

  if '-fake' in s:
    cmd='iso_prf -q '+prefix+'.clean tmp.prf -sg 0 > '+prefix+'.prf'
    xcmd(cmd,verbose)
    removeLinesWithNAN(prefix+'.prf')

    os.remove('tmp.prf')
    cmd='fake -s '+prefix+'.clean '+prefix+'.prf'
    xcmd(cmd,verbose)
    if '-i' in s: xcmd('probe -t '+prefix+'.fake',verbose)
    cmd='gasp_images -f '+prefix+'.fake 0 '+str(5*float(skysig))+' 10 false > '+ prefix+'.ims'
    
    #  ' | grep -v NaN | fltstrm c c r 0 '+str(0.05*nx*nx)+' c c c > '+prefix+'.ims'
    xcmd(cmd,verbose)
    removeLinesWithNAN(prefix+'.ims')

    if verbose: print '>> '+os.popen('wc '+prefix+'.ims').read().split()[0]+' targets found'
    if log: print >> log,'>> '+os.popen('wc '+prefix+'.ims').read().split()[0]+' targets found'
    if '-lsb' in s:
      cmd='ims_clean -q '+prefix+'.clean '+prefix+'.ims 1.5 '+ixc+' '+iyc+' 0'
    else:
      cmd='ims_clean -q '+prefix+'.clean '+prefix+'.ims 1.5 '+ixc+' '+iyc+' '+str(clean_rad)+' '+str(eps)+' '+theta
    tmp=xcmd(cmd,verbose)
  else:
    cmd='mv -f tmp.prf '+prefix+'.prf'
    xcmd(cmd,verbose)

# 2nd clean along isophotes, 4 sigma

  if sig != '0' and clean_rad > 0:
#    cmd='prf_clean -f '+prefix+'.clean '+prefix+'.prf '+sig+' '+str(clean_rad)
    cmd='prf_clean -f '+prefix+'.clean '+prefix+'.prf '+sig+' 10'
    xcmd(cmd,verbose)
    if os.path.isfile(prefix+'.prf_clean'):
      cmd='mv -f '+prefix+'.prf_clean '+prefix+'.clean'
      xcmd(cmd,False)

  if '-i' in s:
    open('tmp.tmp','w').write('INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 '+ \
               'RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n')
    JoinHeaderToProfileAndSaveToXMLFile('tmp.tmp',prefix + '.prf',prefix)
    os.remove('tmp.tmp')
    xcmd('probe -t '+prefix+'.clean',verbose)

# another fit, larger outer stopping radius

  if '-st' in s and '-rx' not in s: 
    tmp=s.split()[s.split().index('-st')+1]
    cmd='efit -q '+prefix+'.clean '+prefix+'.prf -xy '+ixc+' '+iyc+' -sg '+prof_sig+' -rx '+ \
         rstop+' -rs -'+str(router)+' -st '+tmp
  if '-st' in s and '-rx' in s: 
    tmp=s.split()[s.split().index('-st')+1]
    cmd='efit -q '+prefix+'.clean '+prefix+'.prf -xy '+ixc+' '+iyc+' -sg '+prof_sig+' -rx '+ \
         rstop+' -rs '+str(router)+' -st '+tmp
  else:
    cmd='efit -q '+prefix+'.clean '+prefix+'.prf -xy '+ixc+' '+iyc+' -sg '+prof_sig+' -rx '+rstop+' -rs '+str(router)
  xcmd(cmd,verbose)
  os.system('grep -v I '+prefix+'.prf > tmp.tmp')
  os.system('mv -f tmp.tmp '+prefix+'.prf')
  tmp=os.popen('wc '+prefix+'.prf').read()
  if verbose: print '>> '+tmp.split()[0]+' ellipses found'
  if log: print >> log,'>> '+tmp.split()[0]+' ellipses found'
  if int(tmp.split()[0]) < 3:
    print '>>>> too few ellipses, aborting <<<<'
    sys.exit()
  if os.path.isfile(prefix+'.jedsub'):
    cmd='mv -f '+prefix+'.jedsub '+prefix+'.clean'
    xcmd(cmd,False)

  open('tmp.tmp','w').write('INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 '+ \
             'RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n')
  JoinHeaderToProfileAndSaveToXMLFile('tmp.tmp',prefix + '.prf',prefix)
  os.remove('tmp.tmp')
  if '-i' in s:
    xcmd('probe -t '+prefix+'.clean',verbose)

# final sky determination using boxes - obsolete, assume correct sky at start

#  if nx < 100:
#    if verbose: print 'not doing sky_box -r, file too small'
#    if log: print >> log,'not doing sky_box -r, file too small'
#  else:
#    box='5'
#    if nx > 200: box='10'
#    if nx > 500: box='20'
#    cmd='sky_box -r '+prefix+'.clean '+box
#    sky=xcmd(cmd,verbose)
#    if sky.split()[0] == 'error':
#      if verbose: print 'error in full sky_box, .xml not corrected'
#      if log: print >> log,'error in full sky_box, .xml not corrected'
#    else:
#      cmd='xml_archangel -e '+prefix+' sky '+sky.split()[2]
#      xcmd(cmd,verbose)
#      cmd='xml_archangel -e '+prefix+' skysig '+sky.split()[3]
#      xcmd(cmd,verbose)
#      cmd='xml_archangel -e '+prefix+' nsky '+sky.split()[4]
#      xcmd(cmd,verbose)

# smooth ellipses with prf_smooth, flag #6 set to -1 for cleaned ellipses, 0 for unfixable ones, -n means
# failed to converge to solution after n iterations, n means solution found in n iterations

  if '-nosm' not in s:
    if '-dsk' in s:
      cmd='prf_smooth -s '+prefix+'.prf > tmp.prf'
    else:
      cmd='prf_smooth -d '+prefix+'.prf > tmp.prf'
    xcmd(cmd,verbose)
    replaceNANWithUnity('tmp.prf')
    cmd='iso_prf -q '+prefix+'.clean tmp.prf -sg 0 > '+prefix+'.prf'
    xcmd(cmd,verbose)
    removeLinesWithNAN(prefix+'.prf')
    os.remove('tmp.prf')

    open('tmp.tmp','w').write('INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 '+ \
               'RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n')
    JoinHeaderToProfileAndSaveToXMLFile('tmp.tmp',prefix + '.prf',prefix) 
    os.remove('tmp.tmp')

# final look if not in quiet mode, if changes then probe will run iso_prf

  open('tmp.tmp','w').write('INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 '+ \
                            'RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n')
  JoinHeaderToProfileAndSaveToXMLFile('tmp.tmp',prefix + '.prf',prefix)
  os.remove('tmp.tmp')

  if '-no_probe' not in s:
    cmd='probe -t -y '+prefix+'.fits'
    tmp=xcmd(cmd,verbose)
# obsolete, used to run iso_prf on flag from probe, now probe does it
#    if 'tmp.prf' in tmp:
#      cmd='iso_prf -q '+prefix+'.clean tmp.prf -sg 0 | grep -v -i n | grep -v -i i > '+prefix+'.prf'
#      xcmd(cmd,verbose)
#      os.system('cat '+prefix+'.prf | grep -v -i i | grep -v -i n > tmp.tmp')
#      os.system('mv -f tmp.tmp '+prefix+'.prf')
#      open('tmp.tmp','w').write('INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 '+ \
#               'RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n')
#      cmd='cat tmp.tmp '+prefix+'.prf | xml_archangel -a '+prefix+' prf'
#      xcmd(cmd,verbose)

# clean up files

  for fix in ['.iso_prf','.fake','.ims','.prf']:
    if os.path.isfile(prefix+fix): os.remove(prefix+fix)

#  cmd='fake -x '+prefix
#  tmp=xcmd(cmd,verbose)
 
except SystemExit:
  pass
except:
  if verbose: print '\nsome kind of error has occured'
  if log: print >> log,'\nsome kind of error has occured'
  raise
