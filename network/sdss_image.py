#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import time, sys, os, os.path
import subprocess

def kill_proc(label):
  p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
  out, err = p.communicate()
  for line in out.splitlines():
    if label in line and 'kill' not in line:
      pid = int(line.split(None, 1)[0])
      os.system('kill -9 '+str(pid))
  return

if '-h' in sys.argv:
  print 'sdss_pull_image.py filter gal_name RA Dec'
  print 'or'
  print 'sdss_pull_image.py -f filter master_filename'
  sys.exit()

iboot=0
butt='g'
if '-u' in sys.argv:
  butt='u'
if '-r' in sys.argv:
  butt='r'
if '-i' in sys.argv:
  butt='i'
if '-z' in sys.argv:
  butt='z'

if '-f' in sys.argv:
  files=[tmp.split() for tmp in open(sys.argv[-1],'r').readlines()]
else:
  files=[[sys.argv[-3],sys.argv[-2],sys.argv[-1]]]

# note: user profile varys with computer
profile = webdriver.FirefoxProfile("/Users/js/Library/Application Support/Firefox/Profiles/l40nl96j.default")
driver = webdriver.Firefox(profile)
driver.implicitly_wait(30)
base_url = "http://skyserver.sdss.org/"

for i,file in enumerate(files):
  if os.path.isfile(file[0]+'_'+butt+'.raw'):
    print 'skipping',file[0]+'_'+butt+'.raw'
    continue
  driver.get(base_url + "/dr12/en/tools/search/IQS.aspx")
  driver.find_element_by_name("raCenter").clear()
  driver.find_element_by_name("raCenter").send_keys(file[1])
  driver.find_element_by_name("decCenter").clear()
  driver.find_element_by_name("decCenter").send_keys(file[2])
  driver.find_element_by_xpath("(//input[@id='submit'])[3]").click()
  page=driver.page_source.encode("utf-8")
  if 'No objects have been found' in page:
    print 'fail'
    continue
  else:
    print 'fields found'
  driver.find_element_by_name("submit").click()
  page=driver.page_source.encode("utf-8")

  test_ra=float(file[1])
  test_dec=float(file[2])

  ids=[]
  for line in page.split('\n'):
    if 'fitsdownload' in line:
      ids.append(line.split('id=')[1].split('"')[1])
  n=0
  runs=[]
  for line in page.split('\n'):
    if 'runCamcolField?field' in line and 'run=' in line:
      n=n+1
#    print line
      if n == 4: ra=line.split('>')[1].split('<')[0]
      if n == 5: 
        run=line.split('run=')[1].split("'")[0]
        dec=line.split('>')[1].split('<')[0]
        runs.append([run,ra,dec])
      if n == 6: n=0

  rmin=1.e33
  for x,y,z in runs:
    r=((float(y)-test_ra)**2.+(float(z)-test_dec)**2.)**0.5
    if r < rmin:
      rmin=r
      run=x

  if len(ids) > 1:
    print 'found more than one run, picking',
  else:
    print 'one run found',

  for id in ids:
    if run in id:
      link=id
  print run,link

  z=os.listdir('/Users/js/Desktop/')
  for t in z:
    if t.endswith('.part'): os.system('mv -f /Users/js/Desktop/*.part /Users/js/.Trash')
    if t.endswith('.bz2'): os.system('mv -f /Users/js/Desktop/*.bz2 /Users/js/.Trash')

  driver.find_element_by_id(link).click()
  if butt != 'u': driver.find_element_by_id("filter_u").click()
  if butt != 'g': driver.find_element_by_id("filter_g").click()
  if butt != 'r': driver.find_element_by_id("filter_r").click()
  if butt != 'i': driver.find_element_by_id("filter_i").click()
  if butt != 'z': driver.find_element_by_id("filter_z").click()
  driver.find_element_by_css_selector("button.btn.btn-primary").click()
  restart=True
  print 'starting files search'
  n=0
  while restart:
    time.sleep(1)
    n=n+1
    if n > 100:
      print 'download hung, aborting'
      kill_proc('firefox-bin')
      try:
        driver.close()
      except:
        pass
      print '****** rebooting ******'
      profile = webdriver.FirefoxProfile("/Users/js/Library/Application Support/Firefox/Profiles/l40nl96j.default")
      driver = webdriver.Firefox(profile)
      driver.implicitly_wait(30)
      base_url = "http://skyserver.sdss.org/"
      iboot=1
      break

    print '\r',n,'testing for file',
    sys.stdout.flush()
    for filename in os.listdir('/Users/js/Desktop/'):
      restart=False
      if 'part' in filename:
        restart=True
        break

  if not iboot:
    print 'complete'
    if '-f' in sys.argv:
      print 'sleeping 10'
      time.sleep(10)
    else:
      print 'sleeping 3'
      time.sleep(3)
    for filename in os.listdir('/Users/js/Desktop/'):
      if 'frame' in filename: break
    print 'found file:',filename
    print 'mv ~/Desktop/'+filename+' '+file[0]+'_'+butt+'.raw.bz2'
    os.system('mv ~/Desktop/'+filename+' '+file[0]+'_'+butt+'.raw.bz2')
    print 'bzip2 -d '+file[0]+'_'+butt+'.raw.bz2'
    os.system('bzip2 -d '+file[0]+'_'+butt+'.raw.bz2')
    if '-f' not in sys.argv:
      out=open('marks.tmp','w')
      out.write(file[1]+' '+file[2]+'\n')
      out.close()
      os.system('probe -s '+file[0]+'_'+butt+'.raw')
      print 'done, opening display'
    else:
      print 'done file',i+1,'of',len(files)
  else:
    files.append(file)
    iboot=0

driver.close()
