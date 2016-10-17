#!/usr/bin/env python

# this routine takes a gif image and allows you to mark the
# positions of the cursor into a file, i.e. you can interpolate
# pixel coords on a plot

# still needs to be edited to take out interp

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
    coords[3]=event.y
    print '2nd mark at',event.x,stds[1],event.y,stds[3]
  if npts >= 2:
    if npts == 2:
      canvas.create_line(event.x-1, event.y-1, event.x, event.y)             
    else:
      canvas.create_line(xold, yold, event.x, event.y)             
    file.write(str(interp(coords[0],coords[1],stds[0],stds[1],event.x))+' '+ \
               str(interp(coords[2],coords[3],stds[2],stds[3],event.y))+'\n')
    print event.x,event.y,
    print interp(coords[0],coords[1],stds[0],stds[1],event.x),
    print interp(coords[2],coords[3],stds[2],stds[3],event.y)
    xold=event.x
    yold=event.y

# enter gif file, axis x1, x2, y1, y2

if '-h' in sys.argv:
  print 'cursor_mark gif_file x1,x2,y1,y2'
  print 'first mark is lower left, 2nd is upper right'
  print 'rest of marks to cursor.tmp'
  sys.exit()

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
