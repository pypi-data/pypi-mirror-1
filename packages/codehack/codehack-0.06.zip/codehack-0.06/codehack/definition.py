"""
definition of objects
"""
from opcode import *
from general import *

class Instruction():
    def __init__(self, value, cobj = None, **kw):
        self.cobj = cobj
        self.value = value
        self.opcode = value[0]
        self.opname = opname[self.opcode]
        self.length = len(value)
        if self.opcode >= HAVE_ARGUMENT:
            self.arg = value[1] + value[2] * 256
            self.high = value[1]
            self.low = value[2]
        self.updateArgstr()
        self.relyOn = []
        self.reachable = False
        self.jumpTo = None
        self.next = None
        self.prev = None
        self.pos = "UNDEF"
        for k in kw:
            self.__dict__[k] = kw[k]

    def setArg(self, v):
        self.arg = v
        self.high = v % 256
        self.low = v / 256
        self.value[1] = self.high
        self.value[2] = self.low
        self.updateArgstr()
        
    def updateArgstr(self):
        if self.opcode >= HAVE_ARGUMENT:
            if self.cobj == None:
                self.argstr = str(self.arg)
            elif self.opcode in hasconst:
                self.argstr = str(self.cobj.co_consts[self.arg])
            elif self.opcode in hasname:
                self.argstr = self.cobj.co_names[self.arg]
            elif self.opcode in haslocal:
                self.argstr = self.cobj.co_varnames[self.arg]
            elif self.opcode in hascompare:
                self.argstr = cmp_op[self.arg]
            elif self.opname == "CALL_FUNCTION":
                self.argstr = "%d, %d" % (self.high, self.low)
            else:
                self.argstr = str(self.arg)
        else:
            self.argstr = None
        
    def get_arg(self):
        return self.arg

    def use(self, stack, num):
        assert isinstance(num, int)
        for i in range(num):
            self.relyOn.append(stack.pop())

    def push(self, stack, num):
        for i in range(num):
            stack.append(self)        

    def __repr__(self):
        if self.argstr != None:
            return "%s(%s)@%s" % (self.opname, self.argstr, self.pos)
        else:
            return "%s@%s" % (self.opname, self.pos)
    
    def __str__(self):
        result = repr(self)
        if self.relyOn:
            result += " rely on %r" % self.relyOn
        return result



_fieldname = 'argcount nlocals stacksize flags \
code consts names varnames cellvars cellvars \
filename name firstlineno lnotab'.split()

class CodeObject():
    def __init__(self, cobj):
        map(
            self.__dict__.__setitem__,
            _fieldname,
            cobj)
        self.cobj = cobj

    def getList(self):
        return [self.__dict__.__getitem__(name) for name in _fieldname]

    def append(self, xsname, x):
        assertType(xsname, str)
        xs = self.__dict__[xsname]
        i = len(xs)
        self.__dict__[xsname] = tuple(list(xs) + [x])
        return i

    def addIfNotExist(self, xsname, x):
        assertType(xsname, str)
        xs = self.__dict__[xsname]
        if x in xs:
            return list(xs).index(x)
        return self.append(xsname, x)
