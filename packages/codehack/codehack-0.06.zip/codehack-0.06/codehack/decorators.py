"""
decorators
"""

from util import *

def removeUnreachable(func):
    newCode = toBytes(serialize(analyze(func)))
    
    code = CodeHack.getValue(func)
    print len(code[4]) - len(newCode), "bytes removed"
    code[4] = newCode
    CodeHack.CodeHack.setValue(func, code)
