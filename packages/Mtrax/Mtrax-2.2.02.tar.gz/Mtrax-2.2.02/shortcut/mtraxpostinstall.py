#!/usr/bin/env python

# mtraxpostinstall.py
import sys
import os.path
import shutil

print "***Running Post-Install Script***"
print "Creating shortcut to mtrax.exe..."
mtraxpath = os.path.join(sys.prefix,'Scripts')
description = 'Mtrax: Multiple Fly Tracking Program'
print 'path = ' + str(sys.path)
iconpath = 'hypnotoad.ico'
for path in sys.path:
    i = path.find(os.path.join('mtrax','shortcut'))
    if i >= 0:
        print 'i = ' + str(i)
        iconpath = os.path.join(path[:i],'mtrax','mtraxicon.ico')
print 'iconpath = ' + iconpath
create_shortcut("mtrax.exe",description,"mtrax.lnk",
                '',mtraxpath,iconpath)
