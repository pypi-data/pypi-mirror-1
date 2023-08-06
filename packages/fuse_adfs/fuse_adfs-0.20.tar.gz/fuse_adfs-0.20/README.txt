=========
fuse_adfs
=========

:Author: David Boddie
:Date: 2005-04-29
:Version: 0.20

.. contents::


Introduction
------------

The ``fuse_adfs`` module provides a Filesystem in Userspace (FUSE_) utility
for presenting the contents of ADFS floppy disc images as a mountable
filing system on Linux, relying on the ``ADFSlib`` module for its image
reading facilities.

With this filing system, disc images can be mounted in the same way as floppy
discs and CDROMs, and navigated at the command line or with a file manager.
The filing system translates ADFS-style filenames to Unix-friendly ones and
adds suffixes to filenames to help applications recognize certain types of
files.


Requirements
------------

This utility requires both FUSE_ and the `Python bindings package for FUSE`_.
The Python bindings need to be obtained from the FUSE project site - see the
following Wiki page for more information::

  http://fuse.sourceforge.net/wiki/index.php/FusePython

Follow the instructions given in the package for the Python bindings to install
them. Once this has been done, the ``fuse_adfs`` utility can be installed.


Installing fuse_adfs
--------------------

Enter the ``fuse-adfs`` directory and type::

  python setup.py build

Then, as root, type::

  python setup.py install


Mounting an image
-----------------

Before the ``fuse_adfs.py`` script can be run, the kernel module that provides
the userspace support must be loaded. The ``fuse_setup.py`` script provided
can be run as root to load the ``fuse`` kernel module as required.

Alternatively, you can type the following as root::

  modprobe fuse

As a normal user, you can now mount an ADFS image with the ``fuse_adfs.py``
utility, using the following syntax::

  fuse_adfs.py <mount point> -o image=<image path>

Note that the mount point must refer to an empty directory.


Unmounting an image
-------------------

When you have finished with an image, type::

  fusermount -u <mount point>

or type (possibly as root)::

  umount <mount point>


License
-------

The contents of this package are licensed under the GNU General Public License
(version 3 or later)::

 fuse_adfs, a FUSE filesystem for ADFS disc images.
 Copyright (C) 2008 David Boddie <david@boddie.org.uk>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.



.. _FUSE: http://fuse.sourceforge.net/
.. _`Python bindings package for FUSE`:
   http://cvs.sourceforge.net/viewcvs.py/fuse/python/
