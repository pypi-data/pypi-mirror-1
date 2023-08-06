#!/usr/bin/env python

from distutils.core import setup

setup(name='OmniFile',
      version='1.0',
      description='Opens files from file names, file objects, or pre-read data',
      author='Leaf',
      author_email='LeafStormRush+py@gmail.com',
      py_modules=['omnifile'],
      classifiers=[
          'Environment :: Plugins',
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Topic :: Software Development'
          ],
      provides=['omnifile'],
      long_description="""
========
OmniFile
========

OmniFile is designed for programmers who write file manipulation functions. In
Python, there are many ways a file can be passed to a function - you can read
the file and pass the read data, you can open the file object, or you can pass
a filename.

OmniFile's job is to handle *any* of these circumstances, based on whichever is
convenient for the user of your function.

Functions
=========

OmniRead
--------
::

 omniread(source)

Used when you only need data, OmniRead can accept file names, pre-read file
data, and file objects. It will return pure string data.

OmniRSIO
--------
::

 omnirsio(source)

Similar to OmniRead, but returns a file-like StringIO instance instead. This is
helpful when you need file-like functionality such as iterating through lines or
manipulating the file in place, but aren't so concerned about whether you have
a physical location on disk.

OmniOpen
--------
::

 omniopen(source, mode)

OmniOpen can handle a file's name or a file that's already been opened. It can
be used when you need a writable file with a physical location.

About
=====
OmniFile is licensed under the terms of the GNU General Public License. Its
mission is to make your life easier as a programmer. It was written by Leaf, who
can be contacted at leafstormrush+py@gmail.com.
      """
      )
