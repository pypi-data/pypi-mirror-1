#!/usr/bin/env python
# $URL: https://pypng.googlecode.com/svn/trunk/code/mkiccp.py $
# $Rev: 157 $
# Make ICC Profile

# References
#
# [ICC 2001] ICC Specification ICC.1:2001-04 (Profile version 2.4.0)
# [ICC 2004] ICC Specification ICC.1:2004-10 (Profile version 4.2.0.0)

import struct

# Local module.
import iccp

def tags(tag):
    """`tag` should be a dictionary of (*signature*, *element*) pairs, where
    *signature* (the key) is a length 4 string, and *element* is the content of
    the tag element (another string).  `tag` can instead, be a list of
    pairs; it is passed to the ``dict`` constructor before using.

    Returns a string.
    """

    tag = dict(tag)
    n = len(tag)
    tablelen = 12*n
    
    # Build the tag table in two parts.  A list of 12-byte tags, and a
    # string of element data.  Offset is the offset from the start of
    # the profile to the start of the element data (so the offset for
    # the next element is this offset plus the length of the element
    # string so far).
    offset = 128 + tablelen + 4
    # The table.  As a string.
    table = ''
    # The element data
    element = ''
    for k,v in tag.items():
        table += struct.pack('>4s2L', k, offset + len(element), len(v))
        element += v
    return struct.pack('>L', n) + table + element

def encode(tsig, *l):
    """Encode a Python value as an ICC type.  `tsig` is the type
    signature to (the first 4 bytes of the encoded value, see [ICC 2004]
    section 10.
    """

    # A number of helper functions.  Each one encodes a particular type
    # (the signature of which matches the last 4 bytes of the functions
    # name).  Each function returns a string comprising the content of
    # the encoded value.  To form the full value, the type sig and the 4
    # zero bytes should be prefixed (8 bytes).

    def ICCdesc(ascii):
        """Return textDescription type [ICC 2001] 6.5.17.  The ASCII part is
        filled in with the string `ascii`, the Unicode and ScriptCode parts
        are empty."""

        ascii += '\x00'
        l = len(ascii)

        return struct.pack('>L%ds2LHB67s' % l,
                           l, ascii, 0, 0, 0, 0, '')

    def ICCtext(ascii):
        """Return textType [ICC 2001] 6.5.18."""

        return ascii + '\x00'

    def ICCcurv(f=None, n=256):
        """Return a curveType, [ICC 2001] 6.5.3.  If no arguments are
        supplied then a TRC for a linear response is generated (no entries).
        If an argument is supplied and it is a number (for *f* to be a
        number it  means that ``float(f)==f``) then a TRC for that
        gamma value is generated.
        Otherwise `f` is assumed to be a function that maps [0.0, 1.0] to
        [0.0, 1.0]; an `n` element table is generated for it.
        """

        if f is None:
            return struct.pack('>L',  0)
        try:
            if float(f) == f:
                return struct.pack('>LH', 1, int(round(f*2**8)))
        except (TypeError, ValueError):
            pass
        assert n >= 2
        table = []
        M = float(n-1)
        for i in range(n):
            x = i/M
            table.append(int(round(f(x) * 65535)))
        return struct.pack('>L%dH' % n, n, *table)

    fun = dict(text=ICCtext, desc=ICCdesc, curv=ICCcurv)
    v = fun[tsig](*l)
    return tsig + '\x00'*4 + v

def black(m):
    """Return a function that maps all values from 0 to m to 0, and maps
    the range [m,1.0] into [0.0, 1.0] linearly.
    """

    m = float(m)

    def f(x):
        if x <= m:
            return 0.0
        return (x-m)/(1.0-m)
    return f

def fs15f16(x):
    """Convert float to ICC s15Fixed16Number (as a Python ``int``)."""

    return int(round(x * 2**16))

def D50():
    """Return D50 illuiminant as an XYZNumber (in a 12 byte string)."""

    # See [ICC 2001] A.1
    return struct.pack('>3l', *map(fs15f16, [0.9642, 1.0000, 0.8249]))

def profile(out, tags):
    """`tags` is a dictionary mapping *sig* to *value*, where *sig* is a
    4 byte signature string, and *value* is the encoded values for the
    tag element.
    """

    it = iccp.Profile().greyInput()
    it.rawtagdict = tags
    it.write(out)

# For monochrome input the required tags are (See [ICC 2001] 6.3.1.1):
# profileDescription [ICC 2001] 6.4.32
# grayTRC [ICC 2001] 6.4.19
# mediaWhitePoint [ICC 2001] 6.4.25
# copyright [ICC 2001] 6.4.13

def agreyprofile(out):
    tags = dict(cprt=encode('text', 'For the use of all mankind.'), 
      desc=encode('desc', 'an ICC profile'),
      wtpt=struct.pack('4sL12s', 'XYZ ', 0, D50()),
      kTRC=encode('curv', black(0.07)),
      )

    return profile(out, tags)

def main():
    import sys
    agreyprofile(sys.stdout)

if __name__ == '__main__':
    main()
