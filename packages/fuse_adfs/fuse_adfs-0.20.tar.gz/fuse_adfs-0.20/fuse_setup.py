#!/usr/bin/env python

"""
fuse_setup.py

A helper script for inserting and removing the fuse kernel module.

Copyright (C) 2005 David Boddie <david@boddie.org.uk>

This software is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public
License along with this library; see the file COPYING
If not, write to the Free Software Foundation, Inc.,
59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""

import popen2, sys

def run(command):

    so, si, se = popen2.popen3(command)
    si.close()
    output = so.read()
    errors = se.read()
    if errors:
    
        sys.stderr.write(errors)
        sys.exit(1)
    
    sys.stdout.write(output)

if __name__ == "__main__":

    if len(sys.argv) != 2:
    
        sys.stderr.write("Usage %s start|stop\n" % sys.argv[0])
        sys.exit(1)
    
    if sys.argv[1] == "start":
    
        run("/sbin/modprobe fuse")
    
    elif sys.argv[1] == "stop":
    
        run("/sbin/rmmod fuse")
    
    else:
    
        sys.stderr.write("Usage %s start|stop\n" % sys.argv[0])
        sys.exit(1)
    
    sys.exit()
