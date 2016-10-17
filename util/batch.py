#!/usr/bin/env python

import subprocess, sys

cmd=['pick']+sys.argv[1:]
subprocess.Popen(cmd)
