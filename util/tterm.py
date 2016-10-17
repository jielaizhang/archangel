#!/usr/bin/env python

import os, optparse, subprocess

p=optparse.OptionParser(description='open Terminal window',
                        prog='tterm', usage='%prog command')
p.add_option("-x", "--noexit", action="store_true", default=False, help="exit on completion")
p.add_option("-r", "--rows", dest="rows", help="number of rows")
p.add_option("-c", "--columns", dest="columns", help="number of columns")
p.add_option("-f", "--font", dest="font", help="font color")
p.add_option("-p", "--position", dest="position", help="position coords")

(options, args) = p.parse_args()

cmd='tell application "Terminal"\n'
cmd=cmd+'activate\n'
if options.noexit:
  cmd=cmd+'do script with command "'+' '.join(args)+'"\n'
else:
  cmd=cmd+'do script with command "cd '+os.getcwd()+' ; '+' '.join(args)+' ; exit"\n'
cmd=cmd+'tell front window\n'
cmd=cmd+'set cursor color to "white"\n'
#set background color to {15716, 0, 0, -10240}
if options.rows:
  cmd=cmd+'set the number of rows to '+options.rows+'\n'
if options.columns:
  cmd=cmd+'set the number of columns to '+options.columns+'\n'
if options.font:
  cmd=cmd+'set normal text color to "'+options.font+'"\n'
if options.position:
  cmd=cmd+'set position to {'+options.position+'}\n'
cmd=cmd+'end tell\n'
cmd=cmd+'end tell\n'

x=subprocess.Popen('osascript', shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
x.communicate(cmd)
