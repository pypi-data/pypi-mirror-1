# u must have scipy installed for this script to work
# remove comments below & copy to file test_pep3132_scipy.py

from __future__ import py3k_syntax

import scipy
a,*b = scipy.array([1,2,3])
assert a == 1 and b == [2, 3]
print(a, b)
