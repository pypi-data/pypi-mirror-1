"""
CodeHack --- A tool for hacking code object

* var_warning.py
  a module warns if variable never loaded

* util.py
  utilities. including dis-assembler
  and analyzer of dependecies between op-codes.

* manipulator.py
  extension to hack code objects.



** samples

>>> from codehack.var_warning import checkfunc, checkall
>>> import urllib
>>> checkfunc(urllib.urlopen)
variable 'FancyURLopener' is global
variable '_urlopener' is global
>>> checkall(urllib.__dict__)
* function splitnport
* function getproxies
* function retrieve
variable 'msg' is not used
variable 'garbage' is not used
(snip)
"""


