"""
This module contains the code to generate interface aliases.

This module contains a single generator, AliasGenerator, which will yield a series of suffixes to an interface name. 

>>> a = AliasGenerator()
>>> a.next()
''
>>> a.next()
':0'
>>> a.next()
':1'
"""
__revision__ = "$Revision$"

def AliasGenerator():
    
    i = 0

    while i < 256:
        if i == 0:
            yield ""
        else:
            yield ":%d" % (i - 1)
        i += 1

    return

def cidr2mask( cidr ):
    """
    Converts a CIDR subnet (/24) to a mask (255.255.255.0).
    """
    one32 = 0xffffffffL
    if ( cidr == "0" ):
        return "0.0.0.0"
    bits = int( cidr )
    n = ( ( one32 << ( 32 - bits ) ) & one32 )
    d3 = "%u" % ( n % 256 )
    n = int( n / 256 )
    d2 = "%u" % ( n % 256 )
    n = int( n / 256 )
    d1 = "%u" % ( n % 256 )
    n = int( n / 256 )
    d0 = "%u" % n
    return "%s.%s.%s.%s" % ( d0, d1, d2, d3 )

