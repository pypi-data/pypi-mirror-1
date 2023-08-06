
""" 
Core classes and functions to load and train on CSV datasets.
"""

try:
    import psyco
    psyco.full()
    print "load psyco optimizer"
except ImportError:
    pass

from pputil import *
from pphisto import *
from ppdataset import *
from ppdist import *

