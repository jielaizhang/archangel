#!/usr/bin/env python

import sys, os, re, smtplib
import urllib2
from mechanize import Browser
from mechanize import UserAgent
from BeautifulSoup import BeautifulSoup

def allText(tag):
    """Converts a tag into text by walking all the text-owning subtags."""
    text = ''.join([text for text in tag.findAll(text=re.compile(r'.+'))])
    text = text.replace('&nbsp;', ' ')
    return text.strip()

def parse(html):
    # First remove some HTML constructs that BeautifulSoup doesn't like.
    html = re.sub('<!--.*?-->', '', html)
    html = re.sub(r'(onclick|onmouseover)="[^"]*"', '', html)
   
    # Now get BeautifulSoup to do the heavy lifting.
    soup = BeautifulSoup(html)
    back=''
    for tr in soup('tr')[1:]:   # Ignore the first row
        back=back+'\n'+'|'.join([allText(cell) for cell in tr('td')])
    return back

if __name__ == '__main__':
  b = Browser()
  b.addheaders=[('User-Agent', 'Mozilla/5.0')]
  b.open('https://website.com')

  userid=''
  password=''
  b.select_form(name='LoginForm')
  b['userId']=userid
  b.submit()

  for form in b.forms():
    print form

  b.select_form(name='LoginForm')
  try:
    b.submit()
  except:
    b['challengeAnswer']=chall[b['challengeQuesion']]
    b.submit()
