#!/usr/bin/env python

# ./entry_titles.py filename
# generic entryfield tool - needs file that has
# lines of headers and data separated by :
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
      self.widths=[]

      file=open(sys.argv[-1],'r')
      while 1:
        line=file.readline()
        if not line: break
        self.values.append([line.split(':')[0],line.split(':')[-1][:-1].lstrip()])
      file.close()

      self.widths=[0,25]
      for z in self.values:
        for n,t in enumerate(z):
          if len(t) > self.widths[n]:
            self.widths[n]=len(t)

      self.tot_wid=0
      for z in self.widths:
        self.tot_wid=self.tot_wid+10*(z+1)
      self.tot_wid=self.tot_wid
      master_geo=str(self.tot_wid)+'x'+str(30*(len(self.values)+1)+30)+'+'+str(int(self.s_width/4))+'+200'
      self.master.geometry(master_geo)
#      self.master.geometry('1400x620+800+200')
#      self.master.bind("<Tab>", self.execute)

      self.butt_place=30*(len(self.values)+1)+30-28
      self.box_height=13

      self.frm = Frame()
      self.button=Button(self.frm, text='Execute',font='courier',bg='lightblue',command=self.quit)
      self.button.place(x=0,y=self.butt_place,width=self.tot_wid,height=30)
      self.frm.pack(side=BOTTOM,expand=YES,fill=BOTH)

      self.text=Text(self.frm)
      self.text.config(fg='white',bg='black',border=0,font='Courier 16',padx=25,pady=25)
      self.text.place(x=0,y=0,width=self.tot_wid,height=self.butt_place)

      self.labels()

    def labels(self):

      pos_y=-10
      self.fields=[]
      for i in self.values: self.fields.append('')
      for n,t in enumerate(self.values):
        pos_x=28
        pos_y=pos_y+30
        self.fields[n]= Pmw.EntryField(self.frm,
               label_font = 'Courier 16',
               labelpos = 'w',
               label_text = t[0].rjust(self.widths[0])+':',
               label_foreground = 'white',
               label_background = 'black',
               value = t[1],
               validate = None)
        self.fields[n].place(x=pos_x,y=pos_y,width=10*self.widths[1]+3)

    def quit(self):
      for t,z in zip(self.values,self.fields):
          print t[0]+':',z.get()
      sys.exit(0)

if __name__ == '__main__':
  root=Tk()
  root.option_add('*EntryField.background', 'black')
  root.option_add('*EntryField.foreground', 'white')
  root.title('EntryField Widget')
  root.configure(background='black')
  entry_label().mainloop()
