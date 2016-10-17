#!/usr/bin/env python3

# series of notes from python cookbook

# unpack_a_fixed_number_of_elements_from_iterables_of_arbitrary_length.py
# keeping_the_last_n_items.py
# finding_the_largest_or_smallest_n_items.py
# calculating_with_dictionaries.py
# removing_duplicates_from_a_sequence_while_maintaining_order.py

# using slices

x='abcdefghijk'

print('example of slice: x=',x,': x[slice(4,8)]=',x[slice(4,8)])
# example of slice: x= abcdefghijk : x[slice(4,8)]= efgh

items=[1,2,3,4,5,6]
a=slice(2,4)
print(items[2:4])
# [3, 4]
print(items[a])
# [3, 4]
items[a]=[10,11]
print(items)
# [1, 2, 10, 11, 5, 6]
del items[a]
print(items)
# [1, 2, 5, 6]
a=slice(1,6,2)
print(x[a])
# bdf

# determine_the_top_n_items_occurring_in_a_list.py
# grouping_records_together_based_on_a_field.py

# reverse list

a=['a','b','c','d']
for x in reversed(a): print(x,end='')

# filtering sequences

print('\nfilters\n')
mylist=[1,4,-5,10,-7,2,3,-1]
print([n for n in mylist if n > 0])
# [1, 4, 10, 2, 3]
print([n for n in mylist if n < 0])
# [-5, -7, -1]

pos = (n for n in mylist if n < 0)
for x in pos: print(x)

values = ['1','2','-3','-','N/A','5']

def is_int(val):
  try:
    x=int(val)
    return True
  except:
    return False

print(list(filter(is_int, values)))
# ['1', '2', '-3', '5']

import math
print([math.sqrt(n) for n in mylist if n > 0])
# [1.0, 2.0, 3.1622776601683795, 1.4142135623730951, 1.7320508075688772]

print([n if n > 0 else 0 for n in mylist])
# [1, 4, 0, 10, 0, 2, 3, 0]

print([n > 5 for n in mylist])
# [False, False, False, True, False, False, False, False]

addresses=['a','b','c','d','e','f','g','h']
from itertools import compress
print(list(compress(addresses, [n > 5 for n in mylist])))
# ['d']

# namedtuple's

import collections

Stock = collections.namedtuple('Stock', ['name','shares','price'])
s=Stock('ACME',100,123.4)
print(s)
# Stock(name='ACME', shares=100, price=123.4)
print(s.shares)
# 100

# strings and text

# split a line by delimiters

import re

line = 'asdf fjdk; afed, fjek,asdf,      foo'

# (a) Splitting on space, comma, and semicolon
parts = re.split(r'[;,\s]\s*', line)
print(parts)
# ['asdf', 'fjdk', 'afed', 'fjek', 'asdf', 'foo']

# (b) Splitting with a capture group
fields = re.split(r'(;|,|\s)\s*', line)
print(fields)
# ['asdf', ' ', 'fjdk', ';', 'afed', ',', 'fjek', ',', 'asdf', ',', 'foo']

# (c) Rebuilding a string using fields above
values = fields[::2]
delimiters = fields[1::2]
delimiters.append('')
print('value =', values)
# value = ['asdf', 'fjdk', 'afed', 'fjek', 'asdf', 'foo']
print('delimiters =', delimiters)
# delimiters = [' ', ';', ',', ',', ',', '']
newline = ''.join(v+d for v,d in zip(values, delimiters))
print('newline =', newline)
# newline = asdf fjdk;afed,fjek,asdf,foo

# (d) Splitting using a non-capture group
parts = re.split(r'(?:,|;|\s)\s*', line)
print(parts)
# ['asdf', 'fjdk', 'afed', 'fjek', 'asdf', 'foo']

# start or ending strings

import os
#print([name for name in os.listdir('.') if name.endswith(('.py','.pyc'))])
print([name for name in os.listdir('.') if name.startswith(('mat','writ'))])

# aligning text

text='hello'
print(text.rjust(20,'='))
# ===============hello
print(format(text,'>20'))
#                hello
print(format(text,'<20'))
# hello               
print(format(text,'^20'))
#        hello        
print(format(text,'#^20s'))
# #######hello########

# handling HTML to XML files

s='Elements are written as "<tag>text</tag>".'
import html
print(s)
# Elements are written as "<tag>text</tag>".

print(html.escape(s))
# Elements are written as &quot;&lt;tag&gt;text&lt;/tag&gt;&quot;.

from html.parser import HTMLParser
p = HTMLParser()
x=html.escape(s)
print(p.unescape(s))
# Elements are written as "<tag>text</tag>".

import html

def make_element(name,value,**attrs):
    keyvals = [' %s="%s"' % item for item in attrs.items()]
    attr_str = ''.join(keyvals)
    element = '<{name}{attrs}>{value}</{name}>'.format(
                  name=name,
                  attrs=attr_str,
                  value=html.escape(value))
    return element

# Example
# Creates '<item size="large" quantity="6">Albatross</item>'
print("make_element('item', 'Albatross', size='large', quantity=6)")
print(make_element('item', 'Albatross', size='large', quantity=6))
print("make_element('p','<spam>')")
print(make_element('p','<spam>'))

# writing_a_simple_recursive_descent_parser.py

# formating

x=1234.56789
print(format(x,'0.2f'))
# 1234.57
print(format(x,'>10.2f'))
#   1234.57
print(format(x,'<10.2f'))
# 1234.57   
print(format(x,'^10.2f'))
#  1234.57  
print(format(x,'^0,.1f'))
# 1,234.6
print(format(x,'0.1e'))
# 1.2e+03

a=float('inf')
b=float('nan')
print(math.isinf(a))
print(math.isnan(b))
c=float('nan')
print(b == c)
print(b is c)

# date and time

# determining_last_fridays_date.py
# finding_the_date_range_for_the_current_month.py

# iterators

out=open('tmp.tmp','w')
out.write('#1\n@2\n@3\n')
out.close()
with open('tmp.tmp') as f:
  try:
    while True:
      line=next(f)
      print(line,end='')
  except StopIteration:
    pass

from itertools import dropwhile
with open('tmp.tmp') as f:
  for line in dropwhile(lambda line: line.startswith('#'),f):
    print(line,end='')

# permutations and combinations

a=['a','b','c','d']
from itertools import permutations
print('\npermutations\n')
for p in permutations(a):
  print(p)
print('\npermutations in 2s\n')
for p in permutations(a,2):
  print(p)
from itertools import combinations
print('\ncombinations in 2s\n')
for c in combinations(a,2):
  print(c)

# Example of iterating over two sequences as one

from itertools import chain
a = [1, 2, 3, 4]
b = ['x', 'y', 'z','zz']
for x in chain(a, b):
    print(x)

a = [1, 2, 3]
print(dict(zip(a,b)))
from itertools import zip_longest
print(dict(zip_longest(a,b)))

# how_to_flatten_a_nested_sequence.py

# functions

# Examples of *args and **kwargs functions

def avg(first, *rest):
    return (first + sum(rest)) / (1 + len(rest))

print('\naverage')
print(avg(1, 2))
print(avg(1,2,3,4))

# sort last names with build-in functions

names = ['Brian Jones', 'David Beazley', 'John Cleese', 'Big Jones']
print()
print(names)
print("sorted(names, key=lambda name: name.split()[-1].lower())")
print(sorted(names, key=lambda name: name.split()[-1].lower()))
