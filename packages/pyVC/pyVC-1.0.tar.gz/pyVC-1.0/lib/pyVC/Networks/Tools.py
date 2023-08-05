"""This package contains the function to generate mac addresses """
__revision__ = "$Revision$"
                                         
def MacGenerator(first, last = 0, jump = 1, max = 16777215):
    if not isinstance(first, str):
        raise TypeError, "ERROR: macaddr must be initialized with 3 octets as first, like '52:54:00'"
    
    while last <= max:
        tmplast = "%6.6x" % last
        yield "%s:%0.2s:%0.2s:%0.2s" % (first,
                                        tmplast[0:2],
                                        tmplast[2:4],
                                        tmplast[4:6])
        last += jump
    return
