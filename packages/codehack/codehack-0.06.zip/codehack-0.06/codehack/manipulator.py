import codehack_bin
from general import *
from definition import *

def getValue(o):
    if type(o) == type(getValue):
        return CodeObject(codehack_bin.get_value(o.func_code))
    raise NotImplementedError(type(o))

def setValue(o, c):
    if isinstance(c, CodeObject):
        c = c.getList()
    if type(o) == type(getValue):
        codehack_bin.set_value(o.func_code, c)
    else:
        raise NotImplementedError(type(o))
