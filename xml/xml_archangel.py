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

  def z_print(x,indent,parent):
    for z in x:
      if parent != 'axis' and parent != 'array': print parent,z[1]
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

      if sys.argv[1] == '-z' and parent != 'axis': print ' '*indent,'      data:',z[1]

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

  if '-h' in sys.argv or len(sys.argv) <= 1:
    print 'xml_archangel op file_name element data'
    print
    print 'add or delete data into xml format'
    print
    print '  -o = output element value or array'
    print '  -d = delete element or array'
    print '  -a = replace or add array, array header and data is cat\'ed into routine'
    print '  -e = replace or add element (attributes by varaiable=\'value\')'
    print '  -c = create xml file with root element'
    print '  -n = list elements and children names'
    print '  -k = list elements, attributes, children (no data)'
    print '  -z = list elements, attributes, children and data'
    print '  -f = output element value or array for list of files giving by file_name,'
    print '       list of variables allowed'
    print
    sys.exit()

  if '-' not in sys.argv[1]:
    print 'no option selected - aborting'
    sys.exit()

  if sys.argv[1] == '-c':
    out=xml_write(sys.argv[2].split('.')[0]+'.xml',sys.argv[3])
    out.close()
    sys.exit()

  if sys.argv[1] != '-f':
    name=sys.argv[2].split('.')[0]+'.xml'
    files=[]
    try:
      for root, dirs, filex in os.walk('.'):
        for file in filex:
          if name == file:
            files.append(root+'/'+file)
#            print name,file,files
      if len(files) == 0:
        print name,'no xml file found - aborting'
        sys.exit()
    except:
      pass

    if len(files) > 1:
      print 'multiple files',files
      sys.exit()
    else:
      if files[0].count('/') == 1:
        root='.'
      else:
        root=files[0].split('/')[1]

  if '-f' not in sys.argv:

    try:
      doc = minidom.parse(root+'/'+name)
    except:
      print 'file error in xml_archangel - line 262',root+'/'+name
      sys.exit()
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

  else:

    try:
      files=[tmp[:-1]+'.xml' for tmp in open(sys.argv[2],'r').readlines()]
    except:
      print 'file',sys.argv[2],'not found -- aborting'

    for file in files:

      try:
        for root, dirs, filex in os.walk('.'):
          for name in filex:
            if file in name:
              raise
        else:
          print sys.argv[-1],'no xml file found'
          continue
      except:
        pass

      doc = minidom.parse(root+'/'+file)
      rootNode = doc.documentElement
      elements=xml_read(rootNode).walk(rootNode)

      try:
        print file.split('/')[-1].replace('.xml',''),
        for t in sys.argv[3:]:
          print elements[t][0][1],
        print
      except:
        print 'element not found'

    sys.exit()

  if sys.argv[1] == '-o':

    doc = minidom.parse(root+'/'+name)
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

    try:
      print elements[sys.argv[3]][0][1]
      raise SystemExit
    except SystemExit:
      sys.exit()
    except:
      pass

    try:
      max_len=[]
      for t in elements['array']:
        if t[0]['name'] == sys.argv[3]:
          all=[]
          for z in t[2]['axis']:
            tmp=map(string.strip,z[1].split('\n'))
            xlen=0
            for w in tmp:
              if len(w) > xlen: xlen=len(w)
            max_len.append([z[0]['name'],xlen])
            all.append(map(string.strip,z[1].split('\n')))
          for y in range(len(all)):
            print max_len[y][0].ljust(max_len[y][1]),
          print
          for z in range(len(all[0])):
            for i,y in enumerate(all):
              print y[z].ljust(max_len[i][1]),
            print
      if not max_len: print 'element not found'
    except:
      print 'element not found'
    sys.exit()

  if sys.argv[1] == '-z':
    for x in elements.keys():
      z_print(elements[x],0,x)
    sys.exit()

  if sys.argv[1] == '-k':
    for x in elements.keys():
      tree_print(elements[x],0,x)
    sys.exit()

  if sys.argv[1] == '-n':
    for x in elements.keys():
      element_print(elements[x],0,x)
    sys.exit()

#  out=xml_write(sys.argv[2].split('.')[0]+'.xml',rootNode.nodeName)
  out=xml_write(root+'/'+name.split('.')[0]+'.xml',rootNode.nodeName)

  if sys.argv[1] == '-e':

    try:
      del elements[sys.argv[3]]
    except:
      pass
    attr={}
    for t in sys.argv[4:-1]:
      if '=' in t: attr[t.split('=')[0]]=t.split('=')[1]
    out.loop({sys.argv[3]:[[attr,sys.argv[-1],{}]]})
    out.loop(elements)

  if sys.argv[1] == '-d':
    try:
      del elements[sys.argv[3]]
    except:
      try:
        for i,t in enumerate(elements['array']):
          if t[0]['name'] == sys.argv[3]:
            try:
              del elements['array'][i]
            except:
              pass
        if not elements['array']: del elements['array']
      except:
        pass

    out.loop(elements)

  if sys.argv[1] == '-a':
    try:
      for i,t in enumerate(elements['array']):
        if t[0]['name'] == sys.argv[3]:
          try:
            del elements['array'][i]
          except:
            pass
      if not elements['array']: del elements['array']
    except:
      pass

    data=[]
    while 1:
      try:
        data.append(raw_input())
      except:
        break

    out.loop(elements)
    out.dump('  <array name=\''+sys.argv[3]+'\'>\n')
    for i,t in enumerate(data[0].split()):
      out.dump('    <axis name=\''+t+'\'>\n')
      for line in data[1:]:
        out.dump('      '+line.split()[i]+'\n')
      out.dump('    </axis>\n')
    out.dump('  </array>\n')

  out.close()
