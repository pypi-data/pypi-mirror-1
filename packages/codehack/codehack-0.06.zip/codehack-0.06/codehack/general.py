"""
general
"""

from definition import *

def assertType(x, typ, dontRaise = False):
    def raise_():
        if not dontRaise:
            raise TypeError("%s is not %s" % (x, typ))
    if isinstance(typ, list):
        if not isinstance(x, list):
            raise_()
        for i in x:
            assertType(i, typ[0])
    elif type(x).__name__ == 'classobj':
        if not isinstance(x, typ):
            raise_()
            
def reloadAll():
    import definition
    reload(definition)
    import util
    reload(util)
    import CodeHack
    reload(CodeHack)
    import general
    reload(general)
    import trace
    reload(trace)

