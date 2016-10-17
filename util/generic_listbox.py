#!/usr/bin/env python

# ./generic_listbox.py filename
# generic listbox tool - needs file that has

import sys
from Tkinter import *
import Pmw

class generic_listbox(Frame):
    def __init__(self, parent=None): 
      Frame.__init__(self, parent)
      Pmw.initialise(fontScheme='pmw1',size=16)

      w=Tk()
      self.s_width=w.winfo_screenwidth()
      self.s_height=w.winfo_screenheight()
      w.destroy()

      self.titles=[]
      while 1:
        try:
          self.titles.append(raw_input())
        except:
          break

      self.tot_wid=0
      self.box_height=min(len(self.titles),30)
      for z in self.titles:
        if len(z) > self.tot_wid: self.tot_wid=len(z)
      if self.tot_wid > 50:
        self.tot_wid=50
        self.tot_height=int((515-45)*self.box_height/30.)+46
      else:
        self.tot_height=int((495-45)*self.box_height/30.)+46
      self.tot_wid=int(9.*(self.tot_wid+2))

      master_geo=str(self.tot_wid+10)+'x'+str(self.tot_height)+'+100+100'
      self.master.geometry(master_geo)
      self.butt_place=self.tot_height-(495-452)

      self.master.bind("<Up>", self.up_title)
      self.master.bind("<Down>", self.down_title)
      self.master.bind("<Return>", self.quit)

      self.frm = Frame()
      self.button=Button(self.frm, text='Cancel',font='courier',bg='lightblue',command=self.cancel)
      self.button.place(x=0,y=self.butt_place,width=self.tot_wid/3,height=35)
      self.button=Button(self.frm, text='Open',font='courier',bg='lightblue',command=self.open_file)
      self.button.place(x=self.tot_wid/3,y=self.butt_place,width=self.tot_wid/3,height=35)
      self.button=Button(self.frm, text='Execute',font='courier',bg='lightblue',command=self.execute)
      self.button.place(x=2*self.tot_wid/3,y=self.butt_place,width=self.tot_wid/3,height=35)
      self.frm.pack(side=BOTTOM,expand=YES,fill=BOTH,padx=5,pady=5)

      self.line=0
      self.box()

    def box(self):
      self.listBox = Pmw.ScrolledListBox(self.frm,
        items=self.titles,
        listbox_height = self.box_height,
        vscrollmode = "static",
        selectioncommand = self.select_line)
      self.listBox.component('listbox').configure(background='black',foreground='white',font='Courier 14')
      self.listBox.activate(self.line)
      self.listBox.select_set(ACTIVE)
      top, bottom = self.listBox.yview()
      size = bottom - top
#      self.listBox.yview('moveto', (self.line-6)*size)
      self.listBox.yview('moveto', float(self.line)/(1.5*len(self.titles)))
      self.listBox.place(x=0,y=0,width=self.tot_wid)

    def select_line(self):
      self.line=int(self.listBox.curselection()[0])
      self.box()

    def down_title(self, event):
      self.line=min(self.line+1,len(self.titles)-1)
      self.box()

    def up_title(self, event):
      self.line=max(self.line-1,0)
      self.box()

    def open_file(self):
      pass

    def labels(self):
      pass

    def cancel(self):
      print '>>>aborting<<<'
      sys.exit(0)

    def execute(self):
      print self.titles[int(self.listBox.curselection()[0])]
      sys.exit(0)

    def quit(self, event):
      print self.titles[int(self.listBox.curselection()[0])]
      sys.exit(0)

if __name__ == '__main__':
  root=Tk()
  root.option_add('*EntryField.background', 'black')
  root.option_add('*EntryField.foreground', 'white')
  root.title('ListBox Widget')
  root.configure(background='black')
  generic_listbox().mainloop()
