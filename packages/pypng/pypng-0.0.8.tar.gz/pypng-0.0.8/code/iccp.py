#!/usr/bin/env python
# $URL: https://pypng.googlecode.com/svn/trunk/code/iccp.py $
# $Rev: 158 $

# iccp
#
# International Color Consortium Profile
#
# Tools for manipulating ICC profiles.
#
# An ICC profile can be extracted from a PNG image (iCCP chunk).
#
#
# Non-standard ICCP tags.
#
# Apple use some (widespread but) non-standard tags.  These can be
# displayed in Apple's ColorSync Utility.
# - 'vcgt' (Video Card Gamma Tag).  Table to load into video
#    card LUT to apply gamma.
# - 'ndin' Apple display native information.
# - 'dscm' Apple multi-localized description strings.
# - 'mmod' Apple display make and model information.
# 

# References
#
# [ICC 2001] ICC Specification ICC.1:2001-04 (Profile version 2.4.0)
# [ICC 2004] ICC Specification ICC.1:2004-10 (Profile version 4.2.0.0)

import struct

import png

class FormatError(Exception):
    pass

class Profile:
    """An International Color Consortium Profile (ICC Profile)."""

    def __init__(self):
        self.rawtagtable = None
        self.d = dict()

    def fromFile(self, inp, name='<unknown>'):

        # See [ICC 2004]
        profile = inp.read(128)
        if len(profile) < 128:
            raise FormatError("ICC Profile is too short.")
        size, = struct.unpack('>L', profile[:4])
        profile += inp.read(d['size'] - len(profile))
        return self.fromString(profile, name)

    def fromString(self, profile, name='<unknown>'):
        self.d = dict()
        d = self.d
        if len(profile) < 128:
            raise FormatError("ICC Profile is too short.")
        d.update(
          zip(['size', 'preferredCMM', 'version',
               'profileclass', 'colourspace', 'pcs'],
              struct.unpack('>L4sL4s4s4s', profile[:24])))
        if len(profile) < d['size']:
            warnings.warn(
              'Profile size declared to be %d, but only got %d bytes' %
                (d['size'], len(profile)))
        d['version'] = '%08x' % d['version']
        d['created'] = readICCdatetime(profile[24:36])
        d.update(
          zip(['acsp', 'platform', 'flag', 'manufacturer', 'model'],
              struct.unpack('>4s4s3L', profile[36:56])))
        if d['acsp'] != 'acsp':
            warnings.warn('acsp field not present (not an ICC Profile?).')
        d['deviceattributes'] = profile[56:64]
        d['intent'], = struct.unpack('>L', profile[64:68])
        d['pcsilluminant'] = readICCXYZNumber(profile[68:80])
        d['creator'] = profile[80:84]
        d['id'] = profile[84:100]
        ntags, = struct.unpack('>L', profile[128:132])
        d['ntags'] = ntags
        fmt = '4s2L' * ntags
        # tag table
        tt = struct.unpack('>' + fmt, profile[132:132+12*ntags])
        tt = group(tt, 3)

        # Could (should) detect 2 or more tags having the same sig.  But
        # we don't.  Two or more tags with the same sig is illegal per
        # the ICC spec.
        
        # Convert (sig,offset,size) triples into (sig,value) pairs.
        rawtag = map(lambda x: (x[0], profile[x[1]:x[1]+x[2]]), tt)
        self.rawtagtable = rawtag
        self.rawtagdict = dict(rawtag)
        tag = dict()
        # Interpret the tags whose types we know about
        for sig, v in rawtag:
            if sig in tag:
                warnings.warn("Duplicate tag %r found.  Ignoring." % sig)
                continue
            v = ICCdecode(v)
            if v is not None:
                tag[sig] = v
        self.tag = tag
        return self

    def greyInput(self):
        """Adjust ``self.d`` dictionary for greyscale input device.
        ``profileclass`` is 'scnr', ``colourspace`` is 'GRAY', ``pcs``
        is 'XYZ '.
        """

        self.d.update(dict(profileclass='scnr',
          colourspace='GRAY', pcs='XYZ '))
        return self
    
    def write(self, out):
        """Write ICC Profile to the file."""

        self.writeHeader(out)
        if not self.rawtagtable:
            self.rawtagtable = self.rawtagdict.items()

                

        return self

    def writeHeader(self, out, size=999):
        """Add default values to the instance's `d` dictionary, then
        write a header out onto the file stream.  The size of the
        profile must be specified using the `size` argument.
        """

        def defaultkey(d, key, value):
            """Add ``[key]==value`` to the dictionary `d`, but only if
            it does not have that key already.
            """

            if key in d:
                return
            d[key] = value

        z = '\x00' * 4
        defaults = dict(preferredCMM=z,
                        version='02000000',
                        profileclass=z,
                        colourspace=z,
                        pcs='XYZ ',
                        created=writeICCdatetime(),
                        acsp='acsp',
                        platform=z,
                        flag=0,
                        manufacturer=z,
                        model=0,
                        deviceattributes=0,
                        intent=0,
                        pcsilluminant=D50(),
                        creator=z,
                        )
        for k,v in defaults.items():
            defaultkey(self.d, k, v)

        hl = map(self.d.__getitem__,
                 ['preferredCMM', 'version', 'profileclass', 'colourspace',
                  'pcs', 'created', 'acsp', 'platform', 'flag',
                  'manufacturer', 'model', 'deviceattributes', 'intent',
                  'pcsilluminant', 'creator'])
        # Convert to struct.pack input
        hl[1] = int(hl[1], 16)

        out.write(struct.pack('>L4sL4s4s4s12s4s4sL4sLQL12s4s', size, *hl))
        out.write('\x00' * 44)
        return self

def iccp(out, inp):
    profile = Profile().fromString(*profileFromPNG(inp))
    print >>out, profile.d
    print >>out, map(lambda x: x[0], profile.rawtagtable)
    print >>out, profile.tag

def profileFromPNG(inp):
    """Extract profile from PNG file.  Return (*profile*, *name*)
    pair."""
    r = png.Reader(file=inp)
    _,chunk = r.chunk('iCCP')
    i = chunk.index('\x00')
    name = chunk[:i]
    compression = chunk[i+1]
    assert compression == chr(0)
    profile = chunk[i+2:].decode('zlib')
    return profile, name

def iccpout(out, inp):
    """Extract ICC Profile from PNG file `inp` and write it to
    the file `out`."""

    out.write(profileFromPNG(inp)[0])

def fs15f16(x):
    """Convert float to ICC s15Fixed16Number (as a Python ``int``)."""

    return int(round(x * 2**16))

def D50():
    """Return D50 illuiminant as an XYZNumber (in a 12 byte string)."""

    # See [ICC 2001] A.1
    return struct.pack('>3l', *map(fs15f16, [0.9642, 1.0000, 0.8249]))


def writeICCdatetime(t=None):
    """`t` should be a gmtime tuple (as returned from
    ``time.gmtime()``).  If not supplied, the current time will be used.
    Return an ICC dateTimeNumber in a 12 byte string.
    """

    import time
    if t is None:
        t = time.gmtime()
    return struct.pack('>6H', *t[:6])

def readICCdatetime(s):
    """Convert from 12 byte ICC representation of dateTimeNumber to
    ISO8601 string. See [ICC 2004] 5.1.1"""

    return '%04d-%02d-%02dT%02d:%02d:%02dZ' % struct.unpack('>6H', s)

def readICCXYZNumber(s):
    """Convert from 12 byte ICC representation of XYZNumber to (x,y,z)
    triple of floats.  See [ICC 2004] 5.1.11"""

    return s15f16l(s)

def s15f16l(s):
    """Convert sequence of ICC s15Fixed16 to list of float."""
    # Note: As long as float has at least 32 bits of mantissa, all
    # values are preserved.
    n = len(s)//4
    t = struct.unpack('>%dl' % n, s)
    return map((2**-16).__mul__, t)

# Several types and their byte encodings are defined by [ICC 2004]
# section 10.  When encoded, a value begins with a 4 byte type
# signature.  We use the same 4 byte type signature in the names of the
# Python functions that decode the type into a Pythonic representation.

def ICCdecode(s):
    """Take an ICC encoded tag, and dispatch on its type signature
    (first 4 bytes) to decode it into a Python value.  Pair (*sig*,
    *value*) is returned, where *sig* is a 4 byte string, and *value* is
    some Python value determined by the content and type.
    """

    sig = s[0:4].strip()
    f=dict(text=RDtext,
           XYZ=RDXYZ,
           curv=RDcurv,
           vcgt=RDvcgt,
           sf32=RDsf32,
           )
    if sig not in f:
        return None
    return (sig, f[sig](s))

def RDXYZ(s):
    """Convert ICC XYZType to rank 1 array of trimulus values."""

    # See [ICC 2001] 6.5.26
    assert s[0:4] == 'XYZ '
    return readICCXYZNumber(s[8:])

def RDsf32(s):
    """Convert ICC s15Fixed16ArrayType to list of float."""
    # See [ICC 2004] 10.18
    assert s[0:4] == 'sf32'
    return s15f16l(s[8:])

def RDmluc(s):
    """Convert ICC multiLocalizedUnicodeType.  This types encodes
    several strings together with a language/country code for each
    string.  A list of (*lc*, *string*) pairs is returned where *lc* is
    the 4 byte language/country code, and *string* is the string
    corresponding to that code.  It seems unlikely that the same
    language/country code will appear more than once with different
    strings, but the ICC standard does not prohibit it."""
    # See [ICC 2004] 10.13
    assert s[0:4] == 'mluc'
    n,sz = struct.unpack('>2L', s[8:16])
    assert sz == 12
    record = []
    for i in range(n):
        lc,l,o = struct.unpack('4s2L', s[16+12*n:28+12*n])
        record.append(lc, s[o:o+l])
    # How are strings encoded?
    return record

def RDtext(s):
    """Convert ICC textType to Python string."""
    # Note: type not specified or used in [ICC 2004], only in older
    # [ICC 2001].
    # See [ICC 2001] 6.5.18
    assert s[0:4] == 'text'
    return s[8:-1]

def RDcurv(s):
    """Convert ICC curveType."""
    # See [ICC 2001] 6.5.3
    assert s[0:4] == 'curv'
    count, = struct.unpack('>L', s[8:12])
    if count == 0:
        return dict(gamma=1)
    table = struct.unpack('>%dH' % count, s[12:])
    if count == 1:
        return dict(gamma=table[0]*2**-8)
    return table

def RDvcgt(s):
    """Convert Apple CMVideoCardGammaType."""
    # See
    # http://developer.apple.com/documentation/GraphicsImaging/Reference/ColorSync_Manager/Reference/reference.html#//apple_ref/c/tdef/CMVideoCardGammaType
    assert s[0:4] == 'vcgt'
    tagtype, = struct.unpack('>L', s[8:12])
    if tagtype != 0:
        return s[8:]
    if tagtype == 0:
        # Table.
        channels,count,size = struct.unpack('>3H', s[12:18])
        if size == 1:
            fmt = 'B'
        elif size == 2:
            fmt = 'H'
        else:
            return s[8:]
        l = len(s[18:])//size
        t = struct.unpack('>%d%s' % (l, fmt), s[18:])
        t = group(t, count)
        return size, t
    return s[8:]


def group(s, n):
    # See
    # http://www.python.org/doc/2.6/library/functions.html#zip
    return zip(*[iter(s)]*n)


def main(argv=None):
    import sys
    from getopt import getopt
    if argv is None:
        argv = sys.argv
    argv = argv[1:]
    opt,arg = getopt(argv, 'o:')
    if len(arg) > 0:
        inp = open(arg[0], 'rb')
    else:
        inp = sys.stdin
    for o,v in opt:
        if o == '-o':
            f = open(v, 'wb')
            return iccpout(f, inp)
    return iccp(sys.stdout, inp)

if __name__ == '__main__':
    main()
