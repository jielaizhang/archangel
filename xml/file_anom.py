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
#          att[attrName]=str(attrValue).replace('&','&amp;') \
#                                      .replace('<','&lt;') \
#                                      .replace('>','&gt;') \
#                                      .replace('"','&quot;') \
#                                      .replace('\'','&apos;')
          att[attrName]=str(attrValue).replace('&amp;','&') \
                                      .replace('&lt;','<') \
                                      .replace('&gt;','>') \
                                      .replace('&quot;','"') \
                                      .replace('&apos;','\'')
          # walk over any text nodes in the current node.
        content = []
        for child in node.childNodes:
          if child.nodeType == Node.TEXT_NODE:
            content.append(child.nodeValue)

        if content:
#        strContent = string.join(content).rstrip().lstrip() \
#          strContent = ' '.join(content).rstrip().lstrip() \
#                                        .replace('&','&amp;') \
#                                        .replace('<','&lt;') \
#                                        .replace('>','&gt;') \
#                                        .replace('"','&quot;') \
#                                        .replace('\'','&apos;')
          strContent = ' '.join(content).rstrip().lstrip() \
                                      .replace('&amp;','&') \
                                      .replace('&lt;','<') \
                                      .replace('&gt;','>') \
                                      .replace('&quot;','"') \
                                      .replace('&apos;','\'')
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

class xml_write:

# open the file and write the header, assign the root name (save for closing)
  def __init__(self, xml_out, root):
    self.root=root
    self.level=0
    self.file=open(xml_out,'w')
    self.file.write('<?xml version = \'1.0\'?>\n')
    self.file.write('<'+self.root+'>\n')
    return

# start off each element and add attributes
  def start_element(self, element, attributes):
    self.level+=2
    self.file.write(self.level*' '+'<'+element)
    if attributes:
      for tmp in attributes.keys():
        self.file.write(' '+tmp+'=\''+attributes[tmp]+'\'')
    self.file.write('>\n')
    return

# end each element
  def end_element(self, element):
    self.file.write(self.level*' '+'</'+element+'>\n')
    self.level-=2
    return

# add the data into each element, replacing bad characters, sorting lists etc.
  def data(self, text):
    if not text: return
    self.level+=2
    if isinstance(text,list):
      for tmp in text:
        tmp = str(tmp).replace('&','&amp;')\
                 .replace('<','&lt;')\
                 .replace('>','&gt;')\
                 .replace('"','&quot;')\
                 .replace('\'','&apos;')
        self.file.write(self.level*' '+tmp+'\n')
    else:
      text = str(text).replace('&','&amp;')\
                 .replace('<','&lt;')\
                 .replace('>','&gt;')\
                 .replace('"','&quot;')\
                 .replace('\'','&apos;')
# if it's a data list with \n delimiters, then slice up by \n and kill leading spaces
      if '\n' in text:
        for t in text.split('\n'): self.file.write(self.level*' '+t.lstrip()+'\n')
      else:
        self.file.write(self.level*' '+text+'\n')
    self.level-=2
    return

# manual dump to XML file
  def dump(self, text):
    self.file.write(text)
    return

# close off and end
  def close(self):
    self.file.write('</'+self.root+'>\n')
    self.file.close()
    return

# short function to recursively loop over elements and children
  def loop(self, elements):
# for elements, iterate over items in dict, level sets spacing
    for el in elements.keys():
# start an element
      for w in elements[el]:
        self.start_element(el,w[0])
# if there are children, write them and loop over their grandkids
        if w[2]:
          for t in w[2].keys():
            for x in w[2][t]:
              self.start_element(t,x[0])
              self.loop(x[2])
              self.data(x[1])
              self.end_element(t)
# write out data
        self.data(w[1])
# end the element, reset spacing
        self.end_element(el)

if __name__ == "__main__":

  def element_print(x,indent,parent):
    print ' '*indent,parent,'('+str(len(x))+')',
    space=1
    indent+=2
    for z in x:
      try:
        if isinstance(z[2],list):
          for t in z[2]:
            print '1'
            for y in t.keys():
              indent=indent+2
              element_print(t[y],indent,y)
              indent=indent-2
        else:
          if z[2].keys() == []:
            if space: print
            space=0
          else:
            if space: print
            space=0
            for y in z[2].keys():
              indent=indent+2
              element_print(z[2][y],indent,y)
              indent=indent-2
      except:
        pass
    return

  def tree_print(x,indent,parent):
    print ' '*indent,'element:',parent
    indent+=2
    for z in x:
      if isinstance(z[0],list):
        print ' '*indent,'attributes:',z[0][0]
        for y in z[1:]: print ' '*indent,'           ',y
      else:
        if z[0] == {}:
          print ' '*indent, 'attributes: None'
        else:
          for t in z[0].keys():
            if indent > 11:
              print ' '*indent,t,'=',z[0][t]
            else:
              print ' '*indent,'attributes:',t,'=',z[0][t]
              indent=indent+12
          indent=indent-12

      try:
        if isinstance(z[2],list):
          for t in z[2]:
            for y in t.keys():
              print '\n'+' '*indent, '  children:',y,'('+parent+')'
              tree_print(t[y],indent+4,y)
        else:
          if z[2].keys() == []:
            pass
#             print ' '*indent, '  children: None','('+parent+')'
          else:
            for y in z[2].keys():
              print '\n'+' '*indent, '  children:',y,'('+parent+')'
              tree_print(z[2][y],indent+4,y)
      except:
        pass
#        print ' '*indent, '  children: None','('+parent+')'
      print
    return

  doc = minidom.parse('hsu_grades.xml')
  rootNode = doc.documentElement
  grades=xml_read(rootNode).walk(rootNode)
  num=0
  for file in os.listdir('.'):
    if '.xml' not in file or file[0] == '.' or file[0] != '9': continue

    try:
      doc = minidom.parse(file)
    except:
      print 'file error'
      sys.exit()
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

    if elements['student'][0][2]['course'][0][0]['name'] != 'Physics 102 Winter 2010': continue
    num=num+1
    print num,file

    id=elements['student'][0][0]['number']
    for n,t in enumerate(grades['courses'][0][2]['course'][0][2]['student']):
      if t[0]['number'] == elements['student'][0][0]['number']:
        grades['courses'][0][2]['course'][0][2]['student'][n][0]['number']=str(num)
        break
    else:
      print 'fail for',elements['student'][0][0]['number']

    elements['student'][0][0]['number']=str(num)
    elements['student'][0][2]['name'][0][1]='None'
    elements['student'][0][2]['email'][0][1]='None'

    out=xml_write(('%3.3i' % num)+'.xml',rootNode.nodeName)
    out.loop(elements)
    out.close()

  for n,t in enumerate(grades['courses'][0][2]['course'][0][2]['student']):
    if int(t[0]['number']) > 100:
      grades['courses'][0][2]['course'][0][2]['student'][n][0]['number']='0'
  doc = minidom.parse('hsu_grades.xml')
  rootNode = doc.documentElement
  out=xml_write('tmp.xml',rootNode.nodeName)
  out.loop(grades)
  out.close()
