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

  if sys.argv[1] == '-h':
    print 'xml_quiz_maker op file_name element data'
    sys.exit()

  try:
    doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
  except:
    print 'file error'
    sys.exit()
  rootNode = doc.documentElement
  elements=xml_read(rootNode).walk(rootNode)

# each element list, 0th is attributes (dictionary), 1st is data, 2nd is children (dictionary)

#  print elements.keys()                            # list all the elements
#  print elements['courses']                        # array for element courses, list of N courses
#  print len(elements['courses'])                   # number of courses
#  for z in elements['courses']:                    # element names in courses
#    print z[2].keys()
#  for z in elements['courses']:                     # names of courses, note: each element is a list,
#    print z[2]['name'][0][1]                        # even is list is one element, access 0th, then 1 is
#  for z in elements['courses']:
#    if z[2]['name'][0][1] == 'AST123 Spring 2009':   # found course we want
#      for t in z[2]['quiz']:                         # show me quizzes
#        print t
#        print
#  for z in elements['courses']:
#    if z[2]['name'][0][1] == 'AST123 Spring 2009':   # found course we want
#      for t in z[2]['quiz']:                         # what quiz number is it?
#        print t[0]['number']

  for z in elements['courses']:
    if z[2]['name'][0][1] == 'AST123 Spring 2009':                            # course ID
      for t in z[2]['quiz']:
        if int(t[0]['number']) == 2:                                          # quiz number
          print 'number of questions =',len(t[2]['question'])
          print
          for w in t[2]['question']:                                          # iterate through questions and answers
            print 'Question #'+w[0]['number']+':',
            strng=w[1].replace('&lt;','<').replace('&gt;','>').replace('&quot;','"')+' (number of answers = '+str(len(w[2]['answer']))
            try:
              strng=strng+', correct one is '+w[2]['correct'][0][1]+')'
            except:
              strng=strng+')'
            print strng
            for x in w[2]['answer']:
              print '  '+x[0]['value']+')',
              print x[1].replace('&lt;','<').replace('&gt;','>').replace('&quot;','"')
            print
          print

  out=xml_write('tmp.xml',rootNode.nodeName)
  out.loop(elements)
  out.close()
