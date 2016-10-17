#!/usr/bin/env python

import socket,os,time,subprocess,sys

p=subprocess.Popen('rxvt',shell=True)
p.communicate('echo this is a test')
tmp=raw_input()
