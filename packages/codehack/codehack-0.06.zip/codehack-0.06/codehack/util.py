# -*- coding: cp932 -*-
import dis 
from opcode import *
from trace import trace
from definition import *
from general import *

def getNum(op):
    if op < HAVE_ARGUMENT:
        return 1
    return 3

def d2h(i):
    return "%02X" % i

def getInst(insts, pos):
    return [self for self in insts if self.pos == pos][0]

def analyze(o, do_trace=True):
    if type(o).__name__ == 'function':
        code = o.func_code.co_code
        cobj = o.func_code
    elif type(o).__name__ == 'code':
        cobj = o
        code = o.co_code
    
    result = []
    resultDict = {}
    code = map(ord, code)
    i = 0
    while code[i:]:
        c = code[i]
        n = getNum(c)
        inst = Instruction(code[i:i+n], cobj)
        result.append(inst)
        resultDict[i] = inst
        inst.pos = i
        if c in hasjrel:
            inst.jumpTo = i + 3 + inst.arg
        elif c in hasjabs:
            inst.jumpTo = inst.arg
        i += n

    for i in result:
        if i.opname not in ["STOP_CODE", "RETURN_VALUE",
                            "JUMP_ABSOLUTE"]:
            next = getInst(result, i.pos + i.length)
            i.next = next
            next.prev = i
        if i.jumpTo != None:
            i.jumpTo = resultDict[i.jumpTo]
    if do_trace:
        start_trace(result[0])
    return result

def dis(o):
    def etc(i):
        if i.jumpTo != None:
            return "-> %s" % i.jumpTo
        return ""

    if isinstance(o, list) and isinstance(o[0], Instruction):
        insts = o
    else:
        insts = analyze(o)

    for i in insts:
        print "%5d %8s %r %s" % (
            i.pos,
            "_".join(map(d2h, i.value)),
            i,
            etc(i))

def start_trace(start):
    stack = []
    visited = []
    next = [(start, stack)]

    while next:
        nn = trace(*next[0])
        visited.append(next[0][0])
        next = [n for n in (nn + next[1:]) if n[0] not in visited]

def serialize(start):
    start_trace(start)
    
    # find blocks
    visited = {}
    blocks = []
    es = [start] # entrypoints
    while es:
        e = es[0]
        es = es[1:]
        if e in visited: continue

        if e.jumpTo: es.append(e.jumpTo)
        
        cur = e
        block = [cur]
        visited[cur] = block
        while cur.next:
            cur = cur.next
            block.append(cur)
            visited[cur] = block
            if cur.jumpTo: es.append(cur.jumpTo)

        cur = e
        while cur.prev:
            cur = cur.prev
            if not cur.reachable: break
            block.insert(0, cur)
            visited[cur] = block
            if cur.jumpTo: es.append(cur.jumpTo)

        blocks.append(tuple(block))

    # topological sort
    ibmap = visited
    edges = dict((b, []) for b in blocks)
    for i in ibmap:
        src = tuple(ibmap[i])
        if i.opcode in hasjrel:
            dst = tuple(ibmap[i.jumpTo])
            if src != dst:
                if dst not in edges[src]: 
                    edges[src].append(dst)

    sortedBlocks = []
    visited = []
    def visit(b):
        if b in visited: return
        visited.append(b)
        for jumpTo in edges[b]:
            visit(jumpTo)
        sortedBlocks.insert(0, b)

    visit(tuple(ibmap[start]))

    # alignment
    result = []
    pos = 0
    for b in sortedBlocks:
        for i in b:
            result.append(i)
            i.pos = pos
            pos += i.length
    
    for i in result:
        if i.jumpTo:
            c = i.opcode
            if c in hasjrel:
                i.setArg(i.jumpTo.pos - 3 - i.pos)
            elif c in hasjabs:
                i.setArg(i.jumpTo.pos)
    return result


def toBytes(insts):
    assertType(insts, [Instruction])
    result = []
    for i in insts:
        result.extend(map(chr, i.value))
    return "".join(result)

mydis = dis # obsolete


def build(opname, arg = None, **kw):
    opcode = opmap[opname]
    if arg == None:
        return Instruction([opcode], **kw)
    i = Instruction([opcode, 0, 0], **kw)
    i.setArg(arg)
    return i

def flatten(args):
    for arg in args:
        if isinstance(arg, list):
            for i in arg:
                yield i
        else:
            yield arg
        
def weave(*args):
    head = None
    prev = None
    for cur in flatten(args):
        if head == None:
            head = cur
        if prev:
            prev.next = cur
            cur.prev = prev
        prev = cur

    return (head, cur)


if __name__ == "__main__":
    def foo(x):
        if x:
            if x:
                print x
                return
            elif x:
                print x
                return

    print dis(foo)
    old = analyze(foo)
    new = serialize(old)
    print len(old), len(new)
    import visualize
    visualize.visualize(new)
    print repr(foo.func_code.co_code)
    print repr(toBytes(new))
    import CodeHack
    code = CodeHack.CodeHack.get_value(foo.func_code)
    print repr(code[4])
    code[4] = toBytes(new)
    print repr(code[4])
    CodeHack.CodeHack.set_value(foo.func_code, code)
