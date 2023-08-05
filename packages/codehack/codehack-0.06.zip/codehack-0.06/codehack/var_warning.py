"""
check a function

>>> checkfunc(foo)
variable 'botom' is global
variable 'height' is global
variable 'hieght' is not used
variable 'bottom' is not used
"""

# set surpress list
import __builtin__
_default_surpress = __builtin__.__dict__.keys()

def deco_check(surpress = _default_surpress, **kw):
    """checker as decorator
    **usage
    @deco_check()
    def some_func(...):
        ...
        
    """
    def decorator(f):
        checkfunc(f, surpress = surpress, **kw)
        return f
    return decorator

def checkfunc(func,
          print_globals = True,
          print_not_used = True,
          print_func_name = False,
          surpress = _default_surpress):

    import util
    in_vars = set(func.func_code.co_varnames)
    opcodes = util.analyze(func, do_trace=False)

    loaded_vars = set(op.argstr
                for op in opcodes
                if op.opname == "LOAD_FAST")

    loaded_gvars = set(op.argstr
                for op in opcodes
                if op.opname == "LOAD_GLOBAL")

    sn = set(surpress)

    if print_func_name:
        print "* function", func.func_name

    if print_globals:
        for var in loaded_gvars - sn:
            print "variable '%s' is global" % var

    if print_not_used:
        for var in in_vars - loaded_vars - sn:
            print "variable '%s' is not used" % var


def checkall(namespace = None):
    memo = []
    def find_callable(namespace):
        for name in namespace:
            o = namespace[name]
            if callable(o):
                typename = type(o).__name__
                if typename == "classobj":
                    if o not in memo:
                        memo.append(o)
                        find_callable(o.__dict__)
                elif typename == "function":
                    if o not in memo:
                        memo.append(o)
                        checkfunc(o,
                                  print_func_name = True,
                                  print_globals = False)

    if namespace == None:
        namespace = globals()
    find_callable(namespace)


def foo(left, top, right, bottom):
    "function for test"
    width = right - left
    hieght = top - botom
    print height, width


if __name__ == "__main__":
    # reset code for develop phase
    import sys
    [sys.modules.__delitem__(x) for x in sys.modules.keys() if x.startswith("codehack")]
    sys.path.insert(0, "..")

    #    from HTMLParser import HTMLParser
    #    check(HTMLParser.__init__)

    #    import urllib2
    #    checkall(urllib2.__dict__)

    import doctest
    doctest.testmod()
