#!/usr/bin/env python

import sys, os.path, string
from xml.dom import minidom, Node

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
    doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
  except:
    print 'file error'
    sys.exit()
  rootNode = doc.documentElement
  elements=xml_read(rootNode).walk(rootNode)

  def extract(list,vars):
    if len(list) == 0:
      return vars[0]
    else:
      for zz in vars[0][2][list[0][0]]:
        try:
          if zz[0][list[0][1]] == list[0][2]:
            return extract(list[1:],[zz])
            break
        except:
          return extract(list[1:],[zz])

  print extract([['quiz','number','1'],['question','number','1']],elements['courses'])
  print extract([['name',None,None]],elements['courses'])
