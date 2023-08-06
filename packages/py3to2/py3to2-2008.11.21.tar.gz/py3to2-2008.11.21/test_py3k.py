from __future__ import py3k_syntax
from itertools import *

"""
USAGE:
* make sure u have a patched install of python2.6
* make sure u have a vanilla install of python3.0
* make sure u have py3to2.py somewhere that python2.6 can find
* @ command line type: python2.6 -c "import py3to2; import example_py3k"

the output should look like:

created read/write pipes: (4, 5)
py3k server starting with pipes in/out/err: 7 5 -2
py3k server: Python 3.0rc1 (r30rc1:66499, Oct 15 2008, 15:43:09)
py3k server: [GCC 3.4.6 20060404 (Red Hat 3.4.6-10)] on linux2
py3k server: Type "help", "copyright", "credits" or "license" for more information.
py3k server: >>> ''
testing PEP3102  Keyword-Only Arguments
testing PEP3104  Access to Names in Outer Scopes
testing PEP3105  Make print a function
testing PEP3107  Function Annotations
testing PEP3112  Bytes literals in Python 3000
testing PEP3113  Removal of Tuple Parameter Unpacking
py3k server: Traceback (most recent call last):
py3k server:   File "<stdin>", line 1, in <module>
py3k server:   File "/tmp/tmp753t_X.py", line 1
py3k server:     def foo(a, (b, c)): pass
py3k server:                ^
py3k server: SyntaxError: invalid syntax
testing PEP3114  Renaming iterator.next() to .__next__()
testing PEP3115  Metaclasses in Python 3000
testing PEP3127  Integer Literal Support and Syntax
testing PEP3129  Class Decorators
testing PEP3132  Extended Iterable Unpacking
testing PEP3135  New Super
testing curry example 0
testing curry example 1
testing curry example 2
testing curry example 3
testing numpy example
"""

######## PEP3xxx example
if 1:
  print( "testing PEP3102  Keyword-Only Arguments" )
  def foo(a, *b, c = 0): return a, b, c
  assert foo(1, 2, 3, c = 4) == (1, (2, 3), 4)

if 1:
  print( "testing PEP3104  Access to Names in Outer Scopes" )
  def foo(x):
    def bar(): nonlocal x; x += 1
    bar(); return x
  assert foo(1) == 2

if 1:
  print( "testing PEP3105  Make print a function" )
  from StringIO import StringIO; f = StringIO()
  print("hello", "world", sep = " ", end = "\n", file = f)
  assert f.getvalue() == "hello world\n"

if 1:
  print( "testing PEP3107  Function Annotations" )
  def foo(x:"value", args:tuple, kwds:dict): return x, args, kw
  assert foo.__annotations__ == {"x":"value", "args":tuple, "kwds":dict}

if 0: # fail
  print( "testing PEP3109-3110  Raising/Catching Exceptions in Python 3000" )
  def iter():
    try: 1/0
    except: yield 1; raise
  i = iter(); next(i)
  try: next(i)
  except ZeroDivisionError: pass

if 0: # turned off for batch scripting purpose
  print( "testing PEP3111  Simple input built-in in Python 3000" )
  print( "press 1 and enter")
  assert input() == "1"

if 1:
  print( "testing PEP3112  Bytes literals in Python 3000" )
  assert bytes("hello") == b"hello" == eval(repr(b"hello"))

if 1:
  print( "testing PEP3113  Removal of Tuple Parameter Unpacking" )
  try: exec("def foo(a, (b, c)): pass")
  except SyntaxError: pass
  else: raise Exception

if 1:
  print( "testing PEP3114  Renaming iterator.next() to .__next__()" )
  assert count().__next__() == next(count()) == 0

if 1: #
  print( "testing PEP3115  Metaclasses in Python 3000" )
  class member_table(dict): ## The custom dictionary
    def __init__(self): self.member_names = []
    def __setitem__(self, key, value):
       if key not in self: self.member_names.append(key) # if the key is not already defined, add to the list of keys.
       dict.__setitem__(self, key, value) # Call superclass

  class OrderedClass(type): # The metaclass
    @classmethod
    def __prepare__(metacls, name, bases): return member_table()  # The prepare function - No keywords in this case
    def __new__(cls, name, bases, classdict): # The metaclass invocation
      # Note that we replace the classdict with a regular
      # dict before passing it to the superclass, so that we
      # do not continue to record member names after the class
      # has been created.
      result = type.__new__(cls, name, bases, dict(classdict))
      result.member_names = classdict.member_names; return result

  class MyClass(metaclass = OrderedClass):
    def method1(self): pass # method1 goes in array element 0
    def method2(self): pass # method2 goes in array element 1

  assert MyClass().member_names == ["__module__", "method1", "method2"]

if 0: # not implemented - py3to2 restricted to ascii
  print( "testing PEP3120  Using UTF-8 as the default source encoding" )

if 0: # not implemented - c extension issue
  print( "testing PEP3123  Making PyObject_HEAD conform to standard C" )

if 1:
  print( "testing PEP3127  Integer Literal Support and Syntax" )
  assert -0b10 == -2 and -0o10 == -8 and -0x10 == -16 and eval(bin(-2)) == -2 and eval(oct(-8)) == -8 and eval(hex(-16)) == -16

if 1:
  print( "testing PEP3129  Class Decorators" )
  def foo(cls): cls.foo = 1; return cls
  @foo
  class bar(object): pass
  assert bar.foo == 1

if 0: # not implemented - py3to2 restricted to ascii
  print( "testing PEP3131  Supporting Non-ASCII Identifiers" )

if 1:
  print( "testing PEP3132  Extended Iterable Unpacking" )
  a, *b = 1, 2, 3; assert a == 1 and b == [2, 3]

if 1:
  print( "testing PEP3135  New Super" )
  class Foo(str):
    def __new__(cls, s): return super().__new__(cls, s)
  assert Foo("abc") == "abc"

if 0: # not implemented - py3to2 restricted to ascii
  print( "testing PEP3138  String representation in Python 3000" )

######## curry feature example
if 1:
  print( "testing pseudomethod example 0" )
  x = set(enumerate(["a", "b", "c"]))
  y = ["a", "b", "c"] .__pseudomethod__.enumerate() .__pseudomethod__.set()
  z = ["a", "b", "c"]                 ..enumerate()                 ..set()
  assert x == y == z == { (0, "a"), (1, "b"), (2, "c") }

if 1:
  print( "testing pseudomethod example 1" )
  x = min(len("hello world"), 0, 1 + 2)
  y = "hello world" ..len() ..min(0, 1 + 2)
  assert x == y == 0

if 1:
  print( "testing pseudomethod example 2" )
  def foo(a, b = 0): return a + b
  def bar(c, d = 1): return c * d
  x = bar(foo(1, b = 2), **{"d":3})
  y = 1 ..foo(b = 2) ..bar(**{"d":3})
  assert x == y == 9

  print( "testing pseudomethod example 3" )
  x = eval(compile("oct(16)", "", "eval", 0), globals(), {})
  y = "oct(16)" ..compile("", "eval", 0) ..eval(globals(), {})
  assert x == y == "0o20"

######## numpy example
# numpy must b installed for the following code to run
if 1:
  print( "testing numpy example" )
  try: from numpy import *
  except ImportError: print( "numpy module not found. skipping example" )
  else:
    def sort_a_by_b(a, b):
      return zip(a, b) ..tuple() ..array()[array(b).argsort()]

    a = [ "a", "b", "c", "d"]
    b = [  2 ,  3 ,  1 ,  0 ]
    assert (sort_a_by_b(a, b) ==
            [['d', '0'],
             ['c', '1'],
             ['a', '2'],
             ['b', '3']]
            ).all()
