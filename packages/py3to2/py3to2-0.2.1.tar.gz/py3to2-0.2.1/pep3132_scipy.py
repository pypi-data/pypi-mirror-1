# u must have scipy installed for this script to work
# remove comments below & copy to file pep3132_scipy.py
# PEP3132  Extended Iterable Unpacking

from __future__ import py3k_syntax

import scipy
a,*b = scipy.array([1,2,3])
assert a == 1 and b == [2, 3]
print(a, b)
