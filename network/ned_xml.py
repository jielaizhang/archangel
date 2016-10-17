#!/usr/bin/env python

import sys, os.path
from xml.dom import minidom, Node
import urllib

class xml_read:

  def __init__(self, parent):
    self.parent=parent
    return

  def walk(self, node):
    self.parent=node
    elements={}
    for node in self.parent.childNodes:
      if node.nodeType == Node.ELEMENT_NODE:
        # get attributes
        att={}
        attrs = node.attributes
        for attrName in attrs.keys():
          attrNode = attrs.get(attrName)
          attrValue = attrNode.nodeValue
          att[attrName]=str(attrValue).replace('&','&amp;') \
                                      .replace('<','&lt;') \
                                      .replace('>','&gt;') \
                                      .replace('"','&quot;') \
                                      .replace('\'','&apos;')
          # walk over any text nodes in the current node.
        content = []
        for child in node.childNodes:
          if child.nodeType == Node.TEXT_NODE:
            content.append(child.nodeValue)

        if content:
#        strContent = string.join(content).rstrip().lstrip() \
          strContent = ' '.join(content).rstrip().lstrip() \
                                        .replace('&','&amp;') \
                                        .replace('<','&lt;') \
                                        .replace('>','&gt;') \
                                        .replace('"','&quot;') \
                                        .replace('\'','&apos;')
            # walk the child nodes.
          if len(strContent) == 0: strContent=None
        else:
          strContent=None
        kids=self.walk(node)
        if node.nodeName in elements.keys():
          elements[node.nodeName].append([att,strContent,kids])
        else:
          elements[node.nodeName]=[[att,strContent,kids]]
    return elements

if __name__ == "__main__":

  try:
    if sys.argv[1] == '-h':
      raise
  except:
    print '''
Usage: ned_xml galaxy_ID (put ID in quotes) variables

routine to pull full XML results from NED, print variables

options: -a = list all variables
         -p = photometry
         -d = and descriptions
'''
    sys.exit()

  if '-a' in sys.argv or '-d' in sys.argv or '-p' in sys.argv:
    search='+'.join(sys.argv[2].split())
  else:
    search='+'.join(sys.argv[1].split())

  if search[0] in ['D','F'] and 'DDO' not in search:
    search='LSB'+search

  if search[:2] == 'KK':
    search='[KK'+search.split('KK')[1].split('-')[0]+'] '+search.split('-')[-1]

  if '-p' in sys.argv:
    url='http://nedwww.ipac.caltech.edu/cgi-bin/nph-datasearch?objname='+search+'&meas_type=bot&ebars_spec=ebars&'+ \
        'label_spec=no&x_spec=freq&y_spec=Fnu_jy&xr=-1&of=xml_main&search_type=Photometry'
  else:
    url='http://nedwww.ipac.caltech.edu/cgi-bin/nph-objsearch?objname='+search+'&extend=no&out_csys=Equatorial'+ \
        '&out_equinox=J2000.0&obj_sort=RA+or+Longitude&of=xml_all&zv_breaker=30000.0&list_limit=5&img_stamp=YES'

  data=urllib.urlopen(url).read().replace('<![CDATA[','').replace(']]>','').replace('&amp;','&').replace('&','&amp;')

  if 'Error' in data:
    print search,'Object not found, aborting'
    sys.exit()

  junk=[]
  for z in data.split('\n'):
#    if '<form' in z:
    if 'NED_ExternalLinksTable' in z:

      junk.append('</RESOURCE>')
      junk.append('</VOTABLE>')
      break
#      junk.append('<TD>N/A</TD>')
    else:
      junk.append(z)
  data=' '.join(junk)

  try:
    doc = minidom.parseString(data)
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)
  except:
    print search,'XML fail'
    sys.exit()

  if '-p' in sys.argv:
    for x in elements['RESOURCE'][0][2]['TABLE']:
      for z in x[2]['DATA'][0][2]['TABLEDATA'][0][2]['TR']:
        print search,z[2]['TD'][1][1].replace(' ',''),
        print z[2]['TD'][2][1],
        try:
          print z[2]['TD'][3][1].replace('+/-',''),
        except:
          print z[2]['TD'][3][1],
        print z[2]['TD'][15][1]
#        try:
#          for i in range(19):
#            print i,z[2]['TD'][i][1]
#        except:
#          pass
    sys.exit()

# look at tree to see how this shakes out
# w[0]['name']              = variable name
# v[1]                      = value
# w[2]['DESCRIPTION'][0][1] = description of variable

  if '-a' in sys.argv or '-d' in sys.argv:
    for x in elements['RESOURCE'][0][2]['TABLE']:
      if len(x[2]['FIELD']) == len(x[2]['DATA'][0][2]['TABLEDATA'][0][2]['TR'][0][2]['TD']):
        for w,v in zip(x[2]['FIELD'], \
                       x[2]['DATA'][0][2]['TABLEDATA'][0][2]['TR'][0][2]['TD']):
          if '-a' in sys.argv:
            print search.replace('+',''),w[0]['name'].ljust(65),v[1]
          else:
            print search.replace('+',''),w[0]['name'],v[1],w[2]['DESCRIPTION'][0][1]

  else:
    for var in sys.argv[2:]:
      for x in elements['RESOURCE'][0][2]['TABLE']:
        try:
          if len(x[2]['FIELD']) == len(x[2]['DATA'][0][2]['TABLEDATA'][0][2]['TR'][0][2]['TD']):
            for w,v in zip(x[2]['FIELD'], \
                           x[2]['DATA'][0][2]['TABLEDATA'][0][2]['TR'][0][2]['TD']):
              if w[0]['name'] == var:
                print search.replace('+',''),w[0]['name'],v[1]
                raise
        except:
          break
      else:
        print search.replace('+',''),var,'not found'
