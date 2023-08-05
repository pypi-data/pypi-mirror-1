def trace(self, stack):
    self.reachable = True
    n = self.opname

    if n in ["JUMP_IF_TRUE", "JUMP_IF_FALSE"]:
        # do nothing to stack, conditional jump
        top = stack[0]
        self.use(stack, 1)
        stack.append(top)
        return [(self.next, stack),
                (self.jumpTo, stack[:])]

    if n in ["JUMP_FORWARD", "JUMP_ABSOLUTE",
             "CONTINUE_LOOP"]:
        # do nothing to stack, jump
        return [(self.jumpTo, stack)]

    if n in ["NOP", "PRINT_NEWLINE", "DELETE_FAST",
             "SETUP_LOOP", "POP_BLOCK", "BREAK_LOOP",
             "SETUP_EXCEPT"]:
        # do nothing to stack
        return [(self.next, stack)]
    
    if n in ["POP_TOP"]:
        # pop 1 and use 0
        stack.pop()
        return [(self.next, stack)]

    if n in ["ROT_TWO"]:
        self.use(stack, 2)
        self.push(stack, 2)
        return [(self.next, stack)]

    if n in ["DUP_TOP"]:
        stack.append(self)
        return [(self.next, stack)]


    if n in ["STOP_CODE"]:
        return []
    
    if n in ["RETURN_VALUE"]:
        self.use(stack, 1)
        #assert stack == []
        return []

    if n in ["PRINT_EXPR", "PRINT_ITEM", "PRINT_NEWLINE_TO",
             "STORE_FAST", "STORE_ATTR", "STORE_GLOBAL", "STORE_DEREF", "STORE_NAME"]:
        # use 1 and push 0
        self.use(stack, 1)
        return [(self.next, stack)]

    if n in ["PRINT_ITEM_TO", "LIST_APPEND"]:
        self.use(stack, 1)
        return [(self.next, stack)]

    if n in ["FOR_ITER"]:
        return [
            (self.next, stack + [self]),
            (self.jumpTo, stack[:-1])]
        
    if n in ["LOAD_FAST", "BUILD_MAP", "LOAD_GLOBAL",
             "LOAD_CONST", "LOAD_NAME", "IMPORT_NAME",
             "LOAD_CLOSURE", "LOAD_DEREF"]:
        # push 1
        self.push(stack, 1)
        return [(self.next, stack)]

    if n.startswith("UNARY_") or \
       n.endswith("SLICE+0") or \
       n in ["LOAD_LOCALS", "LOAD_ATTR", "YIELD_VALUE",
             "GET_ITER", "IMPORT_FROM"]:
        # use 1 and push 1
        self.use(stack, 1)
        self.push(stack, 1)
        return [(self.next, stack)]

    if n.startswith("BINARY_") or \
       n.startswith("INPLACE_") or \
       n.endswith("SLICE+1") or \
       n.endswith("SLICE+2") or \
       n in ["DELETE_SUBSCR", "COMPARE_OP"]:
        # use 2 and push 1
        self.use(stack, 2)
        self.push(stack, 1)
        return [(self.next, stack)]
    
    if n.endswith("SLICE+3") or\
       n in []:
        self.use(stack, 3)
        self.push(stack, 1)
        return [(self.next, stack)]

    if n in ["STORE_SUBSCR"]:
        self.use(stack, 3)
        return [(self.next, stack)]
        
    if n in ["BUILD_LIST", "BUILD_TUPLE"]:
        # use n and push 1
        self.use(stack, self.arg)
        self.push(stack, 1)
        return [(self.next, stack)]

    if n in ["CALL_FUNCTION", "CALL_FUNCTION_VAR"]:
        # use h + l * 2 + 1 and push 1
        self.use(stack, self.high + self.low * 2 + 1 )
        self.push(stack, 1)
        return [(self.next, stack)]

    if n in ["DUP_TOPX"]:
        self.push(stack, self.arg)

    if n in ["MAKE_FUNCTION", "MAKE_CLOSURE"]:
        # use 1(code) + arg(default argument)
        self.use(stack, self.arg + 1 )
        self.push(stack, 1)
        return [(self.next, stack)]

    if n in ["RAISE_VARARGS"]:
        self.use(stack, self.arg)
        return []

    if n in ["UNPACK_SEQUENCE"]:
        self.use(stack, 1)
        self.push(stack, self.arg)
        return [(self.next, stack)]

    if n in ["ROT_THREE"]:
        self.use(stack, 3)
        self.push(stack, 3)
        return [(self.next, stack)]
    raise NotImplementedError(self.opname)


testdata = ["STOP_CODE", "POP_TOP", "ROT_TWO", "ROT_THREE", "ROT_FOUR", 
	"DUP_TOP", "UNARY_POSITIVE", "UNARY_NEGATIVE", "UNARY_NOT", 
	"UNARY_CONVERT", "UNARY_INVERT", "GET_ITER", "BINARY_POWER", 
	"BINARY_MULTIPLY", "BINARY_DIVIDE", "BINARY_FLOOR_DIVIDE", 
	"BINARY_TRUE_DIVIDE", "BINARY_MODULO", "BINARY_ADD", "BINARY_SUBTRACT", 
	"BINARY_SUBSCR", "BINARY_LSHIFT", "BINARY_RSHIFT", "BINARY_AND", 
	"BINARY_XOR", "BINARY_OR", "INPLACE_POWER", "INPLACE_MULTIPLY", 
	"INPLACE_DIVIDE", "INPLACE_FLOOR_DIVIDE", "INPLACE_TRUE_DIVIDE", 
	"INPLACE_MODULO", "INPLACE_ADD", "INPLACE_SUBTRACT", "INPLACE_LSHIFT", 
	"INPLACE_RSHIFT", "INPLACE_AND", "INPLACE_XOR", "INPLACE_OR", "SLICE+0", 
	"SLICE+1", "SLICE+2", "SLICE+3", "STORE_SLICE+0", "STORE_SLICE+1", 
	"STORE_SLICE+2", "STORE_SLICE+3", "DELETE_SLICE+0", "DELETE_SLICE+1", 
	"DELETE_SLICE+2", "DELETE_SLICE+3", "STORE_SUBSCR", "DELETE_SUBSCR", 
	"PRINT_EXPR", "PRINT_ITEM", "print", "PRINT_ITEM_TO", "PRINT_NEWLINE", 
	"print", "print", "PRINT_NEWLINE_TO", "BREAK_LOOP", "break", 
	"CONTINUE_LOOP", "continue", "LOAD_LOCALS", "RETURN_VALUE", "YIELD_VALUE", 
	"IMPORT_STAR", "_", "EXEC_STMT", "POP_BLOCK", "END_FINALLY", "finally", 
	"BUILD_CLASS", "STORE_NAME", "DELETE_NAME",
	"UNPACK_SEQUENCE", "DUP_TOPX", "STORE_ATTR", "co_names", "DELETE_ATTR", 
	"co_names", "STORE_GLOBAL", "DELETE_GLOBAL", "LOAD_CONST", 
	"LOAD_NAME", "BUILD_TUPLE", "BUILD_LIST", "BUILD_MAP", "LOAD_ATTR", 
	"COMPARE_OP", "IMPORT_NAME", "IMPORT_FROM", "JUMP_FORWARD", "JUMP_IF_TRUE", 
	"JUMP_IF_FALSE", "JUMP_ABSOLUTE", "FOR_ITER", "next()", "LOAD_GLOBAL", 
	"SETUP_LOOP", "SETUP_EXCEPT", "SETUP_FINALLY", "LOAD_FAST", "STORE_FAST", 
	"DELETE_FAST", "LOAD_CLOSURE", "LOAD_DEREF", "STORE_DEREF", "SET_LINENO", 
	"RAISE_VARARGS", "CALL_FUNCTION", "MAKE_FUNCTION", "MAKE_CLOSURE", 
	"BUILD_SLICE", "EXTENDED_ARG", "CALL_FUNCTION_VAR", "CALL_FUNCTION_KW", 
	"CALL_FUNCTION_VAR_KW"]
