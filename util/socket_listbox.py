#!/usr/bin/env python

import sys,os
from Tkinter import *
import Pmw
import socket,time

class entry_field(Frame):
    def __init__(self, lines, parent=None): 
      Frame.__init__(self, parent)
      Pmw.initialise(fontScheme='pmw1',size=16)

      w=Tk()
      try:
        self.tk.call('console','hide')
      except:
        pass
      self.s_width=w.winfo_screenwidth()
      self.s_height=w.winfo_screenheight()
      w.destroy()

      self.fields=[]
      self.values=[]
      self.header=[]

      if '-f' in lines:
        junk=[tmp[:-1] for tmp in open(lines[-1],'r').readlines()]
        os.system('mv -f '+lines[-1]+' ~/.Trash')
        self.index=junk[0].split()
        line=junk[1].split()
        for z in self.index:
          if ':' in z:
            if z.split(':')[-1] == '':
              self.header.append(' '.join(line[int(z.split(':')[0]):]))
            else:
              self.header.append(' '.join(line[int(z.split(':')[0]):int(z.split(':')[-1])]))
          else:
            self.header.append(line[int(z)])

        self.widths=map(int,junk[2].split())

        for t in junk[3:]:
          line=t.split()
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
      else:
        self.index=lines.split('\n')[0].split()
        line=lines.split('\n')[1].split()
        for z in self.index:
          if ':' in z:
            if z.split(':')[-1] == '':
              self.header.append(' '.join(line[int(z.split(':')[0]):]))
            else:
              self.header.append(' '.join(line[int(z.split(':')[0]):int(z.split(':')[-1])]))
          else:
            self.header.append(line[int(z)])

        self.widths=map(int,lines.split('\n')[2].split())

        for t in lines.split('\n')[3:]:
          line=t.split()
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

      for z in self.values:
        for n,t in enumerate(z):
          if len(t) > self.widths[n]:
            self.widths[n]=len(t)

      if len(self.values) == 0:
        self.values.append(['']*len(self.widths))

      self.tot_wid=0
      for z in self.widths:
        self.tot_wid=self.tot_wid+10*(z+1)+10
      self.tot_wid=self.tot_wid+10
      master_geo=str(self.tot_wid)+'x'+str(30*(len(self.values)+1)+75)+'+'+str(int(self.s_width/10))+'+200'
      self.master.geometry(master_geo)
      self.butt_place=30*(len(self.values)+1)+75-28
      self.box_height=13

      self.frm = Frame()
      if '-noadd' in lines:
        self.button=Button(self.frm, text='Cancel',font='courier',bg='lightblue',command=self.cancel)
        self.button.place(x=0,y=self.butt_place,width=self.tot_wid/2,height=30)
        self.button=Button(self.frm, text='Execute',font='courier',bg='lightblue',command=self.quit)
        self.button.place(x=self.tot_wid/2,y=self.butt_place,width=self.tot_wid/2,height=30)
      else:
        self.button=Button(self.frm, text='Cancel',font='courier',bg='lightblue',command=self.cancel)
        self.button.place(x=0,y=self.butt_place,width=self.tot_wid/3,height=30)
        self.button=Button(self.frm, text='Add',font='courier',bg='lightblue',command=self.add)
        self.button.place(x=self.tot_wid/3,y=self.butt_place,width=self.tot_wid/3,height=30)
        self.button=Button(self.frm, text='Execute',font='courier',bg='lightblue',command=self.quit)
        self.button.place(x=2*self.tot_wid/3,y=self.butt_place,width=self.tot_wid/3,height=30)
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
        self.tot_wid=self.tot_wid+10*(z+1)+10
      self.tot_wid=self.tot_wid+10
      master_geo=str(self.tot_wid)+'x'+str(30*(len(self.values)+1)+75)+'+'+str(int(self.s_width/10))+'+200'
      self.master.geometry(master_geo)
      self.butt_place=30*(len(self.values)+1)+75-28
      self.box_height=13

      self.frm.destroy()

      self.frm = Frame()
      self.button=Button(self.frm, text='Cancel',font='courier',bg='lightblue',command=self.cancel)
      self.button.place(x=0,y=self.butt_place,width=self.tot_wid/3,height=30)
      self.button=Button(self.frm, text='Add',font='courier',bg='lightblue',command=self.add)
      self.button.place(x=self.tot_wid/3,y=self.butt_place,width=self.tot_wid/3,height=30)
      self.button=Button(self.frm, text='Execute',font='courier',bg='lightblue',command=self.quit)
      self.button.place(x=2*self.tot_wid/3,y=self.butt_place,width=self.tot_wid/3,height=30)
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
          if ':' in self.header[0] and i == 0:
            self.fields[n][i]= Pmw.EntryField(self.frm,
                 label_font = 'Courier 16',
                 labelpos = 'w',
                 label_text = t[0].ljust(self.widths[0])+':',
                 label_foreground = 'white',
                 label_background = 'black',
                 validate = None)
          else:
            self.fields[n][i]= Pmw.EntryField(self.frm,
                 value = z,
                 validate = None)
#                 validate = {'max' : 5})
          self.fields[n][i].place(x=pos_x,y=pos_y,width=10*self.widths[i]+3)
          pos_x=pos_x+10*(self.widths[i]+1)

    def cancel(self):
      self.out='>>>aborting<<<'
      print self.out
      self.master.destroy()

    def quit(self):
      self.out=''
      for z in self.fields:
        for t in z:
          self.out=self.out+t.get()
        self.out=self.out+'\n'
      self.out=self.out[:-1]
      print self.out
      self.master.destroy()

class listbox(Frame):
    def __init__(self, lines, parent=None): 
      Frame.__init__(self, parent)
      Pmw.initialise(fontScheme='pmw1',size=16)

      w=Tk()
      try:
        self.tk.call('console','hide')
      except:
        pass
      self.s_width=w.winfo_screenwidth()
      self.s_height=w.winfo_screenheight()
      w.destroy()

      self.titles=[]

      if '-f' in lines:
        self.titles=[tmp[:-1] for tmp in open(lines[-1],'r').readlines()]
        if '-x' in lines: os.system('mv -f '+lines[-1]+' ~/.Trash')
      else:
        while 1:
          try:
            self.titles.append(raw_input())
          except:
            break

      self.dir=os.getcwd()
      self.tot_wid=len(self.dir)
      self.box_height=min(len(self.titles),30)
      self.box_height=30
      for z in self.titles:
        if len(z) > self.tot_wid: self.tot_wid=len(z)
      self.tot_height=int(15*self.box_height)+50
      self.tot_height=500
      self.tot_wid=int(9.*(self.tot_wid+4))

      master_geo=str(self.tot_wid+20)+'x'+str(self.tot_height+10)+'+100+100'
      self.master.geometry(master_geo)

      self.frm = Frame()
      self.frm.configure(background='black')
      self.frm.pack(side=BOTTOM,expand=YES,fill=BOTH,padx=10,pady=10)

      self.text=Text(self.frm)
      self.text.config(fg='white',bg='black',border=0,font='Courier 14',padx=5,pady=5)
      self.text.place(x=0,y=self.tot_height-39,width=self.tot_wid-25,height=30)
      self.text.insert(CURRENT,self.dir)

      self.line=0
      self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      self.sock.bind(('',2727))
      print 'starting'
      self.sock.listen(1)
      print 'listening'
      self.channel,details=self.sock.accept()

      while 1:
        try:
          print 'reading'
          tmp=self.channel.recv(100)
          print 'got',tmp
          self.titles.append(tmp)
          if tmp == 'quit':
            time.sleep(0.1)
            self.sock.close()
            self.master.destroy()
            sys.exit()
#          self.line=self.titles.index(tmp)
#          print self.line
        except:
          time.sleep(0.1)
          self.sock.close()
#          self.master.destroy()
          sys.exit()
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
      self.listBox.yview('moveto', float(self.line)/(1.5*len(self.titles)))
      self.listBox.place(x=0,y=0,width=self.tot_wid)
      self.frm.update()

    def select_line(self):
      self.line=int(self.listBox.curselection()[0])
      self.box()

    def down_title(self, event):
      self.line=min(self.line+1,len(self.titles)-1)
      self.box()

    def up_title(self, event):
      self.line=max(self.line-1,0)
      self.box()

    def cancel(self):
      self.sock.close()
      self.master.destroy()

    def send(self, event):
#      self.sock.send(self.titles[int(self.listBox.curselection()[0])])
      self.box()

    def quit(self, event):
      self.out=self.titles[int(self.listBox.curselection()[0])]
#      print self.out
      self.sock.close()
      self.master.destroy()

if __name__ == '__main__':
  root=Tk()
  if sys.argv[1] in ['-listbox']:
    root.title('')
    root.configure(background='black')
    listbox(sys.argv).mainloop()
  elif sys.argv[1] == '-entry_field':
    root.title('EntryField Widget')
    root.configure(background='black')
    entry_field(sys.argv).mainloop()
