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
