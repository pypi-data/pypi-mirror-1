"""\
Doctests for NestedRecord
"""
import doctest
import logging
logging.basicConfig(level=logging.DEBUG)

import sys; sys.path.append('../')

doctest.testfile('../doc/source/manual.rst', optionflags=doctest.ELLIPSIS)



