import sys
from pprint import pprint
print dir(sys.modules[__name__])
try:
    pprint(sec1)
    pprint(sec2)
except NameError:
    pprint(__pyrun_options__)
    for k in __pyrun_options__.keys():
        pprint(globals()[k])
print sys.argv
