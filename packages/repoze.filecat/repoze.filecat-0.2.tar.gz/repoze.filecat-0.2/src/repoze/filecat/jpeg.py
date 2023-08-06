"""
This module was adapted from Chuck Esterbrook's ``jpeg`` module. Below
is the original license document:


The Gist
========

This Software is open source, but there is no requirement that
products developed with or derivative to it become open source.

This Software is copyrighted, but you can freely use and copy it as
long as you don't change or remove this copyright notice. The license is
a clone of the original OSI-approved Python license.
  OSI licenses: http://www.opensource.org/licenses/

There is no warranty of any kind. Use at your own risk.

Read this entire document for complete, legal details.


Copyright
=========

Copyright (c) 1999-2001 by Chuck Esterbrook
All Rights Reserved


License
=======

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in
supporting documentation, and that the names of the authors not be used
in advertising or publicity pertaining to distribution of the software
without specific, written prior permission.


Disclaimer
==========

THE AUTHORS DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO
EVENT SHALL THE AUTHORS BE LIABLE FOR ANY SPECIAL, INDIRECT OR
CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.


Trademarks
==========

All trademarks referred to in the source code, documentation, sample
files or otherwise, are reserved by their respective owners.
"""

import os
import sys
import struct

reverse = lambda txt: txt[::-1]

#"MM" big endian (Motorola, Mac, Sun), left to right
#"II" little endian (Intel, Windows, Linux), right to left
#JPEG is Big Endian and EXIF may be either one, my Olimpus camera writes EXIF in little endian 
#and many other cameras seem to do that too
if sys.byteorder == "big":
    ENDIAN = "MM"
else:
    ENDIAN = "II"

def endian_padd(val, with_):
    if ENDIAN == "II":
        return val + with_
    return with_ + val

def getNr(nrStr, endian="MM"):
    "given a binary representation of a number in <endian> big or little, return a python int"
    #by default jpeg is MM but we are converting it to ENDIAN and we return an int
    ln = len(nrStr)
    frm = ln > 4 and ('q', 8) or ('i', 4)
    if endian != ENDIAN:  #convert to Intel and padd with NULLs to get <type>
        val = endian_padd(reverse(nrStr), '\x00' * (frm[1]-ln))
    else: 
        val = endian_padd(nrStr, '\x00' * (frm[1]-ln))  
    return struct.unpack(frm[0], val)[0]

def read(file, marker, *headers):
    "return value of <marker> segment if exists, or None otherwise"
    segmentValue=None
    markerSeg, sof, length, im = _process(file, marker, *headers)
    if markerSeg:
        im.seek(-2, 1)  #retract right after marker ID
        segmentValue = im.read(getNr(length))[2:]

    im.close()
    if not markerSeg and not sof:
        raise ValueError, "There is no image in this image file ?"
    return segmentValue

def _process(im, target, *headers):
    """seek target marker in JPEG file, and return tuple:
    (found marker segment boolean, reached image segment boolean, marker segment length, 
    the open file object positioned at the begining of value)
    """
    comment = image = False
    marker = im.read(2)
    if marker != "\xFF\xD8":
        raise ValueError, "Not a JPEG image"
    l=2
    while im.read(1) == "\xFF":
        markerType = im.read(1)
        length = im.read(2)
        l += getNr(length) + 2
        if markerType == "\xC0": #SOF - got to the image, stop
            return (False, True, length, im) 
        if headers and markerType == target:
            magic = im.read(max(map(len, headers)))
            im.seek(-len(magic), os.SEEK_CUR)
            
            for header in headers:
                if magic.startswith(header):
                    break
            else:
                markerType = None

        if markerType == target:
            return (True, False, length, im)
        
        # skip over current segment -2 to move <length> positions
        # starting right after marker
        im.seek(getNr(length) - 2, 1)
        
    return (False, False, length, im) 


