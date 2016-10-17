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
base_url = "http://irsa.ipac.caltech.edu/"

lines=[tmp[:-1] for tmp in open(sys.argv[-1],'r').readlines()]

for gal in lines:

  print gal,
  driver.get(base_url + "/data/SPITZER/Enhanced/SEIP/")
  window_start = driver.window_handles[0]
  driver.find_element_by_name("locstr").clear()
  driver.find_element_by_name("locstr").send_keys(gal)
  driver.find_element_by_name("region").click()
#  time.sleep(30)
  window_after = driver.window_handles[1]
  driver.switch_to_window(window_after)
  page=driver.page_source.encode("utf-8")
  if 'NOTIFICATION' in page:
    print 'no target'
  else:
    print 'ok'
  driver.close()
  driver.switch_to_window(window_start)

driver.close()
