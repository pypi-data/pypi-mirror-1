"""
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

from os.path import isfile
import StringIO

class OmniError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

def omniread(source):
    """
The OmniRead function will return raw string data.

It accepts:

- A pathname.
- A file or file-ish object. (i.e. one with a "read" method)
- String data that's already been read.

It'll read the string data for you and return it.
    """
    if isinstance(source, str):
        if isfile(source):
            return open(source).read()
        else:
            return source
    elif "read" in dir(source):
        return source.read()
    else:
        raise OmniError, "OmniRead wants a STRING or FILE-LIKE object."

def omnirsio(source):
    """
The OmniRSIO (Read StringIO) returns a StringIO object.

This is useful for iteration by lines, or you just want a fake file.

It accepts everything OmniRead does.
    """
    try:
        return StringIO(omniread(source))
    except OmniError:
        raise OmniError, "OmniRSIO needs a STRING or FILE-LIKE object."
    
def omniopen(source, mode="r"):
    """
OmniOpen is designed to return a file object.

It accepts:

- A pathname.
- A file-like object (requires read and write methods).
    """
    if isinstance(source, str):
        if isfile(source):
            return open(source)
        else:
            raise NameError, "OmniOpen only accepts filenames as strings."
    elif ("read" in dir(source)) and ("write" in dir(source)):
        return source
    else:
        raise OmniError, "OmniOpen only accepts file-likes and filenames."
