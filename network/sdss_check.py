#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re, sys

class Web(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://skyserver.sdss.org/dr12/en/tools/search/IQS.aspx"
#        self.base_url = "http://skyserver.sdss.org/dr7/en/tools/search/IQS.asp"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_tmp(self):
        driver = self.driver
#        lines=[tmp[:-1] for tmp in open('in.tmp','r').readlines()]
#        for line in lines:
#          time.sleep(1)
        driver.get(self.base_url)
        driver.find_element_by_name("raCenter").clear()
        driver.find_element_by_name("raCenter").send_keys(self.RA)
        driver.find_element_by_name("decCenter").clear()
        driver.find_element_by_name("decCenter").send_keys(self.Dec)
        driver.find_element_by_xpath("(//input[@id='submit'])[3]").click()
        page=driver.page_source.encode("utf-8")
        print self.file,
        if 'No objects have been found' in page:
          print 'fail'
        else:
          print 'ok'
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    Web.Dec=sys.argv.pop()
    Web.RA=sys.argv.pop()
    Web.file=sys.argv.pop()
    print Web.file,Web.RA,Web.Dec
    unittest.main()
