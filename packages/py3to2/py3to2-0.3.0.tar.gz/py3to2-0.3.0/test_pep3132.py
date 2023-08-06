# PEP3132  Extended Iterable Unpacking
# remove comments below & copy to file test_pep3132.py

from __future__ import py3k_syntax

a,*b = 1,2,3
assert a == 1 and b == [2, 3]
print(a, b)
