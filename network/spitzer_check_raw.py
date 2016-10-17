#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import time, sys, os

# note: user profile varys with computer
profile = webdriver.FirefoxProfile("/Users/js/Library/Application Support/Firefox/Profiles/l40nl96j.default")
driver = webdriver.Firefox(profile)
driver.implicitly_wait(30)

lines=[tmp[:-1] for tmp in open(sys.argv[-1],'r').readlines()]

for gal in lines:

  print gal

  out=open('marks.tmp','w')
  out.write(gal.split()[1]+' '+gal.split()[2]+'\n')
  out.close()

  driver.get('http://sha.ipac.caltech.edu/applications/Spitzer/SHA/#id=SearchByPosition&RequestClass=ServerRequest&DoSearch=true&SearchByPosition.field.radius=0.13888889000000001&UserTargetWorldPt='+gal.split()[1]+';'+gal.split()[2]+';EQ_J2000&TargetPanel.field.targetName='+gal.split()[0]+'&SimpleTargetPanel.field.resolvedBy=nedthensimbad&MoreOptions.field.prodtype=aor,pbcd&shortDesc=Position&isBookmarkAble=true&isDrillDownRoot=true&isSearchResult=true')

  tmp=raw_input()

driver.close()
