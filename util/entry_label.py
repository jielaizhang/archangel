#!/usr/bin/env python

# ./entry_label.py filename
# generic entryfield tool - needs file that has
# list indices
# header labels
# widths for entryfields
# lines of data
# returns lines to STDOUT

import sys
from Tkinter import *
import Pmw

class entry_label(Frame):
    def __init__(self, parent=None): 
      Frame.__init__(self, parent)
      Pmw.initialise(fontScheme='pmw1',size=16)

      w=Tk()
      self.s_width=w.winfo_screenwidth()
      self.s_height=w.winfo_screenheight()
      w.destroy()

      self.fields=[]
      self.values=[]

      file=open(sys.argv[-1],'r')
      self.index=file.readline().split()
      line=file.readline().split()
      self.header=[]
      for z in self.index:
        if ':' in z:
          if z.split(':')[-1] == '':
            self.header.append(' '.join(line[int(z.split(':')[0]):]))
          else:
            self.header.append(' '.join(line[int(z.split(':')[0]):int(z.split(':')[-1])]))
        else:
          self.header.append(line[int(z)])

      self.widths=map(int,file.readline().split())

      while 1:
        line=file.readline().split()
        if not line: break
        tmp=[]
        for z in self.index:
          if ':' in z:
            if z.split(':')[-1] == '':
              tmp.append(' '.join(line[int(z.split(':')[0]):]))
            else:
              tmp.append(' '.join(line[int(z.split(':')[0]):int(z.split(':')[-1])]))
          else:
            tmp.append(line[int(z)])
        self.values.append(tmp)
      file.close()

      for z in self.values:
        for n,t in enumerate(z):
          if len(t) > self.widths[n]:
            self.widths[n]=len(t)

      if len(self.values) == 0:
        self.values.append(['']*len(self.widths))

      self.tot_wid=0
      for z in self.widths:
        self.tot_wid=self.tot_wid+11*(z+1)
      self.tot_wid=self.tot_wid+10
      master_geo=str(self.tot_wid)+'x'+str(30*(len(self.values)+1)+75)+'+'+str(int(self.s_width/4))+'+200'
      self.master.geometry(master_geo)
#      self.master.geometry('1400x620+800+200')
#      self.master.bind("<Tab>", self.execute)

      self.butt_place=30*(len(self.values)+1)+75-28
      self.box_height=13

      self.frm = Frame()
      self.button=Button(self.frm, text='Add',font='courier',bg='lightblue',command=self.add)
      self.button.place(x=0,y=self.butt_place,width=self.tot_wid/2,height=30)
      self.button=Button(self.frm, text='Execute',font='courier',bg='lightblue',command=self.quit)
      self.button.place(x=self.tot_wid/2,y=self.butt_place,width=self.tot_wid/2,height=30)
      self.frm.pack(side=BOTTOM,expand=YES,fill=BOTH)

      self.text=Text(self.frm)
      self.text.config(fg='white',bg='black',border=0,font='Courier 16',padx=25,pady=25)
      self.text.place(x=0,y=0,width=self.tot_wid,height=self.butt_place)

      self.labels()

    def add(self):
      self.values=[]
      for z in self.fields:
        tmp=[]
        for t in z:
          tmp.append(t.get())
        self.values.append(tmp)
      self.values.append(['']*len(self.widths))
      self.tot_wid=0
      for z in self.widths:
        self.tot_wid=self.tot_wid+11*(z+1)
      self.tot_wid=self.tot_wid+10
      master_geo=str(self.tot_wid)+'x'+str(30*(len(self.values)+1)+75)+'+'+str(int(self.s_width/4))+'+200'
      self.master.geometry(master_geo)

      self.butt_place=30*(len(self.values)+1)+75-28
      self.box_height=13

      self.frm.destroy()

      self.frm = Frame()
      self.button=Button(self.frm, text='Add',font='courier',bg='lightblue',command=self.add)
      self.button.place(x=0,y=self.butt_place,width=self.tot_wid/2,height=30)
      self.button=Button(self.frm, text='Execute',font='courier',bg='lightblue',command=self.quit)
      self.button.place(x=self.tot_wid/2,y=self.butt_place,width=self.tot_wid/2,height=30)
      self.frm.pack(side=BOTTOM,expand=YES,fill=BOTH)

      self.text=Text(self.frm)
      self.text.config(fg='white',bg='black',border=0,font='Courier 16',padx=25,pady=25)
      self.text.place(x=0,y=0,width=self.tot_wid,height=self.butt_place)

      self.labels()

    def labels(self):

      for n,z in zip(self.widths,self.header):
        if len(z) < n:
          self.text.insert(CURRENT, z+' '*(n-len(z)+1))
        else:
          self.text.insert(CURRENT, z+' ')

      self.fields=[]
      pos_y=30
      for n,t in enumerate(self.values):
        self.fields.append(['']*len(self.widths))
        pos_x=28
        pos_y=pos_y+30
        for i,z in enumerate(t):
          self.fields[n][i]= Pmw.EntryField(self.frm,
               value = z,
               validate = None)
          self.fields[n][i].place(x=pos_x,y=pos_y,width=10*self.widths[i]+3)
          pos_x=pos_x+10*(self.widths[i]+1)

    def quit(self):
      for z in self.fields:
        for t in z:
          print t.get(),
        print
      sys.exit(0)

if __name__ == '__main__':
  root=Tk()
  root.option_add('*EntryField.background', 'black')
  root.option_add('*EntryField.foreground', 'white')
  root.title('EntryField Widget')
  root.configure(background='black')
  entry_label().mainloop()
