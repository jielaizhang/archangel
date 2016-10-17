#!/usr/bin/env python

import sys
from Tkinter import *

def interp(x1,x2,y1,y2,z1):
  return y1+(z1-x1)*(y2-y1)/(x2-x1)

def callback(event):
  global xold, yold, npts, coords, stds
  npts+=1
  if npts == 0:
    coords[0]=event.x
    coords[2]=event.y
    print '1st mark at',event.x,stds[0],event.y,stds[2]
  if npts == 1:
    coords[1]=event.x
    print '2nd mark at',event.x,stds[1]
  if npts == 2:
    coords[3]=event.y
    print '3rd mark at',event.y,stds[3]
  if npts >= 3:
    if npts == 3:
      canvas.create_line(event.x-1, event.y-1, event.x, event.y)             
    else:
      canvas.create_line(xold, yold, event.x, event.y)             
    file.write(str(interp(coords[0],coords[1],stds[0],stds[1],event.x))+' '+ \
               str(interp(coords[2],coords[3],stds[2],stds[3],event.y))+'\n')
    print interp(coords[0],coords[1],stds[0],stds[1],event.x),
    print interp(coords[2],coords[3],stds[2],stds[3],event.y)
    xold=event.x
    yold=event.y

# enter gif file, axis x1, x2, y1, y2

root=Tk()
root.bind("<Button-1>", callback)
root.configure(cursor='cross')
img=PhotoImage(file=sys.argv[1])

stds=[float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])]
coords=[0,0,0,0]
npts=-1

canvas = Canvas(width=img.width(), height=img.height(), bg='white')
canvas.pack(expand=YES, fill=BOTH)                  
canvas.create_image(2,2,image=img,anchor=NW)

file=open('cursor.tmp','w')

xold=0
yold=0

root.mainloop()
