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

  search='+'.join(sys.argv[1].split())

  url='http://nedwww.ipac.caltech.edu/cgi-bin/nph-objsearch?objname='+search+'&extend=no&hconst=73&omegam=0.27&omegav=0.73&corr_z=1&out_csys=Equatorial&out_equinox=J2000.0&obj_sort=RA+or+Longitude&of=pre_text&zv_breaker=30000.0&list_limit=5&img_stamp=YES'
  data=urllib.urlopen(url).read()
  try:
    objid=data.split('objid=')[1].split('&')[0]
  except:
    print 'error in parsing, abort'
    sys.exit()

  url='http://nedwww.ipac.caltech.edu/cgi-bin/nph-datasearch?search_type=Photo_id&objid='+objid+'&of=xml_all'

  data=urllib.urlopen(url).read().replace('<![CDATA[','').replace(']]>','').replace('&amp;','&').replace('&','&amp;')

  if 'Error' in data:
    print 'Object not found, aborting'
    sys.exit()

  junk=[]
  for z in data.split('\n'):
    if '<form' in z:
      junk.append('<TD>N/A</TD>')
    else:
      junk.append(z)
  data=' '.join(junk)

  doc = minidom.parseString(data)
  rootNode = doc.documentElement
  elements=xml_read(rootNode).walk(rootNode)

  for x in elements['RESOURCE'][0][2]['TABLE']:
    for z in x[2]['DATA'][0][2]['TABLEDATA'][0][2]['TR']:
      if 'J_K' in str(z[2]['TD'][1][1]):
        print search,
        for i in [1,2,3,-2]:
          tmp=str(z[2]['TD'][i][1])
          if i == -2:
            print tmp.split()[0],
            print tmp.split()[2],
          else:
            print tmp.replace(' ','_'),
        print
        break
    else:
      print search,'not found'
