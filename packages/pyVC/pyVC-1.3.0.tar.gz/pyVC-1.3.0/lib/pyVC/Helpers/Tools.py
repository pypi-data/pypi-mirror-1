##
# Module containing tools to assist in Helper generation.
##

__revision__ = "$Revision$"

##
# This function is a generator that will generate a series of Linux interface aliases, like ["", ":0", ":1" ...].
def AliasGenerator():
    
    i = 0

    while i < 256:
        if i == 0:
            yield ""
        else:
            yield ":%d" % (i - 1)
        i += 1

    return
##
# This function converts a CIDR subnet mask into a dotted-quad mask.
#
# @param cidr An integer containing the CIDR prefix, from 0-32.
# @return A string containing the dotted-quad format mask.
def cidr2mask( cidr ):

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

