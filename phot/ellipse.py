#!/usr/bin/env python

from math import *

th=-3.07306898512
m=cos(th)
n=sin(th)

r=4.84000015
s=0.523256451*r
#xc=395.884705
#yc=399.782257
xc=0.
yc=0.

a=(s**2)*(m**2)+(r**2)*(n**2)
b=(s**2)*(n**2)+(r**2)*(m**2)
c=-2.*((s**2)*m*xc+(r**2)*n*yc)
d=-2.*((s**2)*n*xc+(r**2)*m*yc)
e=2.*((s**2)*m*n-(r**2)*m*n)
f=(s**2)*(xc**2)+(r**2)*(yc**2)-(r**2)*(s**2)

print a,b,c,d,e,f

#x=396.
x=-4.8847

t1=(d+e*x)
t2=(d+e*x)**2
t3=4.*b*(a*(x**2)+c*x+f)
t4=2.*b
y=(-t1+(t2-t3)**0.5)/t4
print y
y=(-t1-(t2-t3)**0.5)/t4
print y
