"""
################################################################################
py3to2 is a python2.6 interpreter w/ extended python3.0 opcodes, allowing it to
natively run python3.0 scripts. it should b fully backwards-compatible w/
cpython2.6 & its extensions.

the intended purpose is to allow developers to migrate python2.6 scripts to
python3.0 while retaining backwards compatibility w/ existing extension modules.

AUTHOR:
  kai zhu
  kaizhu@ugcs.caltech.edu

REQUIREMENTS:
  - posix/unix os (Windows currently unsupported)
  - w/ python2.6 & python3.0 installed

INSTALL
  $ python2.6 setup.py build
  $ python2.6 setup.py install
  $ python2.6 setup.py dev --quicktest

  the above will build & install 3 files:
  - extended python2.6 interpreter: bin/py3to2
  - initialization script:          lib/python2.6/site-packages/py3to2_init.py
  - python3.0 bytecode compiler:    lib/python2.6/site-packages/py3to2.py

MAGIC
  simply add the MAGIC LINE:

    from __future__ import py3k_syntax

  to make py3to2 aware that a script is using python3.0 syntax

PSEUDOMETHOD:
  py3to2 supports ".." syntax notation
  please goto: http://pypi.python.org/pypi/pseudomethod
  for more details about this feature

API:
  try help(py3to2)  ^_-

  py3to2 module:
  - class codetree - mutable codeobj & disassembler/assembler/debugger
  - class compiler - compiling tools
  - python3.0 wrappers:
    - py3k_compile() - compile python3.0 src
    - py3k_eval() - eval py3thon3.0 src
    - py3k_exec() - exec python3.0 src

USAGE:
  start up the py3to2 interpreter by typing "py3to2" in ur shell:
    $ py3to2

    Python 2.6.py3to2 (r26:66714, Nov 18 2008, 00:56:43)
    [GCC 3.4.6 20060404 (Red Hat 3.4.6-10)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

  try out this simple python3.0 script:
    ################################################################
    # PEP3132  Extended Iterable Unpacking
    # copy this to file test_pep3132.py

    from __future__ import py3k_syntax

    a,*b = 1,2,3
    assert a == 1 and b == [2,3]
    print(a,b)
    ################################################################
    >>>
    >>> import test_pep3132
    created...
    py3k server starting...
    ...py3k server started w/...

    1 [2, 3]

  here's another python3.0 script using scipy (python2.6) extension module:
    ################################################################
    # u must have scipy installed for this script to work
    # copy this to file test_pep3132_scipy.py

    from __future__ import py3k_syntax

    import scipy
    a,*b = scipy.array([1,2,3])
    assert a == 1 and b == [2,3]
    print(a,b)
    ################################################################
    >>>
    >>> import test_pep3132_scipy
    1 [2, 3]

  another simple, but more thorough test script, test_py3k,
  is included w/ this distribution:
    >>>
    >>> import test_py3k
    testing PEP3102  Keyword-Only Arguments
    testing PEP3104  Access to Names in Outer Scopes
    testing PEP3105  Make print a function
    testing PEP3107  Function Annotations
    testing PEP3112  Bytes literals in Python 3000
    testing PEP3113  Removal of Tuple Parameter Unpacking
    testing PEP3114  Renaming iterator.next() to .__next__()
    testing PEP3115  Metaclasses in Python 3000
    testing PEP3127  Integer Literal Support and Syntax
    testing PEP3129  Class Decorators
    testing PEP3132  Extended Iterable Unpacking
    testing PEP3135  New Super
    testing pseudomethod example 0
    testing pseudomethod example 1
    testing pseudomethod example 2
    testing pseudomethod example 3
    testing numpy example

FEATURES:
  PEP3102  Keyword-Only Arguments
  PEP3104  Access to Names in Outer Scopes
  PEP3105  Make print a function
  PEP3107  Function Annotations
  PEP3111  Simple input built-in in Python 3000
  PEP3112  Bytes literals in Python 3000
  PEP3113  Removal of Tuple Parameter Unpacking
  PEP3114  Renaming iterator.next() to .__next__()
  PEP3115  Metaclasses in Python 3000
  PEP3127  Integer Literal Support and Syntax
  PEP3129  Class Decorators
  PEP3132  Extended Iterable Unpacking
  PEP3135  New Super

LIMITATIONS (FEATURES NOT FULLY SUPPORTED):
  from a migration standpoint, py3to2 is almost feature complete in terms of
  python3.0's language syntax, except for:
  - unicode support (str vs bytes). future support for utf8 is pending...

  language issue aside, python3.0 scripts will still behave differently b/c of
  internal differences between python2.6 & python3.0:
  - exception handling.  py3to2 implements python3.0 syntax for raising &
    catching exceptions.  but the underlying behavior is still python2.6
  - builtin functions / types.  a few of these have become different beasts
    under python3.0

################################################################################
MECHANISM

py3to2 has 3 components:
- py3to2
  python interpreter. can evaluate python2.6 bytecode containing additional
  python3.0 opcode instructions

- py3to2_init.py
  initialization script.  sets up import hook for recognizing python3.0 scripts

- py3to2.py
  bytecode compiler. the compile process takes 2 steps:
  - a persistent python3.0 process is created for compiling scripts into
    python3.0 code
  - py3to2.py then converts the code from python3.0 to python2.6 format

################################################################################
MANIFEST
  ./patch/ - patched files
  ./py3to2.diff - summary of patches (maybe out-of-date)

PYTHON2.6 COMPATIBILITY TEST
  output from amd opteron x86_64 machine on redhat linux (3.4.6-10):
    $ python setup.py dev --maketest
    ...
    324 tests OK.
    36 tests skipped:
        test_aepack test_al test_applesingle test_bsddb185 test_bsddb3
        test_cd test_cl test_codecmaps_cn test_codecmaps_hk
        test_codecmaps_jp test_codecmaps_kr test_codecmaps_tw test_curses
        test_dl test_gdbm test_gl test_imageop test_imgfile test_kqueue
        test_linuxaudiodev test_macos test_macostools test_normalization
        test_ossaudiodev test_pep277 test_py3kwarn test_scriptpackages
        test_socketserver test_startfile test_sunaudiodev test_timeout
        test_urllib2net test_urllibnet test_winreg test_winsound
        test_zipfile64
    1 skip unexpected on linux2:
        test_gdbm

RECENT CHANGES:
  moved pseudomethod syntax handling to py3k server
  added more checks during setup
  added more documentation
  backported patch r67299 fixing an issue w/ super()
  cleaned up py3to2.compiler class
20081120
  fixed package importing bug - py3to2 failed to import foo.bar
20081119
  created self-installing distutils distribution
20081019
  ported to python-2.6
  consolidate & simplify patches to 1 file: ceval.c
  created extension module builtins_py3k
  revamped import hook again
  removed unicode support & restrict source code to ascii-only
20080727
  revampled import hook
20080911
  consolidate patches to 2 files: bltinmodule.c & ceval.c
20080828
  add kwonlyargcount 'attr' to codeobj
  add __annotations__ & __kwdefaults__ attr to funcobj
  add __pseudomethod__ feature to baseobj
20080819
  pure python import hook - removed magic comment & use magic path instead
  revamped str & bytes handling
  revamped py3k .pyc file handling
20080802
  pep3135  New Super
20080717
  pep3107  Function Annotations
  pep3120  Using UTF-8 as the default source encoding
  pep3131  Supporting Non-ASCII Identifiers
20080713
  import / reload works transparently on py3k scripts using a magic comment
  added pep3102  Keyword-Only Arguments
20080709 added a py3k preparser
20080702
  rewrote py3k server's pipe io.  implemented partial bytearray & bytes class.
  wrote a few simple tests
20080630
  __build_class__ function to bltmodule.c.  tested class decorators to b working.
################################################################################
"""

from __future__ import print_function
import io, imp, itertools, os, sys; from itertools import *
__author__ =	"kai zhu"
__author_email__ =	"kaizhu@ugcs.caltech.edu"
__description__ =	"backport 3.0 opcodes to Python-2.6 so it can natively run 3.0 scripts w/ 2.6 extension modules"
__download_url__ =	None
__keywords__ =	None
__license__ =	"BSD"
__maintainer__ =	None
__maintainer_email__ =	None
__obsoletes__ =	None
__platforms__ =	None
__provides__ =	None
__requires__ =	None
__url__ = "http://www-rcf.usc.edu/~kaizhu/work/py3to2"
__version__  = "2008.11.22"
# end info

ISPY3K = True if sys.version_info[0] == 3 else None
if "DEBUG" not in globals(): DEBUG = 0 # set to 0 to suppress printing debug info
def echo(x): return x # useful debug function



######## builtins
if ISPY3K:
  import builtins; builtins.reload = imp.reload

else: # emulate py3k builtins
  import __builtin__, _py3to2, py3to2, py3to2_init; reload(py3to2_init)
  sys.modules["builtins"] = builtins = _py3to2
  __builtin__.__build_class__ = builtins.__build_class__
  py3k_compile = builtins.compile
  py3k_eval = builtins.eval
  py3k_exec = builtins.__dict__["exec"]

  builtins.filter = itertools.filter = ifilter
  itertools.filterfalse = ifilterfalse
  builtins.input = raw_input # PEP3111  Simple input built-in in Python 3000
  builtins.range = xrange
  builtins.map = itertools.map = imap
  builtins.zip = itertools.zip = izip
  itertools.zip_longest = izip_longest

  def add2builtins(f):
    fname = f.__name__.replace("py3k_", "")
    f.__doc__ = getattr( getattr(__builtin__, fname, None), "__doc__", None )
    setattr(builtins, fname, f); return f
  @add2builtins
  def py3k_oct(x): return __builtin__.oct(x).replace("0", "0o", 1)
  @add2builtins
  def printiter(*args, **kwds): print( *tuple(tuple(x) if hasattr(x, "next")  else x for x in args), **kwds )

  from builtins import *; del compile, eval, globals()["exec"]



######## py3k server
if ISPY3K:
  import parser
  def server_compile(s, fpath, mode, flags, dont_inherit):
    try:
      node = parser().parse(s, fpath, mode)
      c = builtins.compile(node, fpath, mode, flags, dont_inherit)
      t = codetree(c)
      s = ascii(t)
    except Exception as e: s = ascii(e)
    sys.stdout.write(s)

else:
  import atexit, signal, subprocess
  def py3k_close():
    "kill & cleanup py3k server process"
    try: os.kill(SERVER.pid, signal.SIGTERM) # kill prev server
    except: pass
    try: map(os.close, SERVERIO) # close prev io pipe
    except: pass
    try: del py3to2.SERVER # prevent annoying error upon SystemExit
    except: pass
  if "SERVER" not in globals(): atexit.register(py3k_close) # close server @ exit
  py3k_close() # close existing server if any

  SERVERIO = os.pipe()[::-1]

  try: # start up py3k server
    print( "py3k server starting..." );
    SERVER = subprocess.Popen(
      "python3.0 -E -i %s" % py3to2.__file__.replace(".pyc", ".py"),
      stdin = subprocess.PIPE,
        stdout = SERVERIO[0],
      stderr = subprocess.STDOUT,
      shell = True)
  except OSError: raise OSERROR("py3to2 could not find or run python3.0.  make sure python3.0 is properly installed & exists in $PATH env variable")

  def py3k_input(s):
    "input command to py3k server's stdin"
    SERVER.stdin.write(s)
  py3k_input("sys.ps1 = ''\n")

  EOF = "%s\n" % id("eof")
  def py3k_read():
    "read from py3k server's stdout"
    n = len(EOF)
    py3k_input("\n" + EOF)
    arr = io.BytesIO()
    while True:
      x = os.read(SERVERIO[1], 4096); arr.write(x)
      if len(x) < len(EOF): x = arr.getvalue()
      if x[-n:] == EOF: break
    return arr.getvalue()[:-n]
  py3k_input("print( '...py3k server started w/ <pid %i> & <i/o pipes %i/%i>' )\n" % (SERVER.pid, SERVERIO[0], SERVERIO[1])); print( py3k_read() )

  def server_compile(*args, **kwds): # server compile
    """
    tell py3k server to compile(*args, **kwds) &
    return the resultant py3k codeobj back to u
    """
    py3k_input("server_compile(*%s, **%s)" % (args, kwds))
    s = py3k_read()
    return s



######## codetree
import dis, opcode, types
class codetree(object):
  """
  ################################################################
  mutable, serializable pseudo-codeobj which u can edit,
  disassemble, debug, & recompile into a real codeobj

  >>> codeobj = compile( "def echo(x): return x", "", "exec" )
  >>> tree = codetree( codeobj )
  >>> print( tree )
  codetree(
  co_argcount =     0,
  co_cellvars =     (),
  co_code =         'd\\x00\\x00\\x84\\x00\\x00Z\\x00\\x00d\\x01\\x00S',
  co_filename =     '',
  co_firstlineno =  1,
  co_flags =        64,
  co_freevars =     (),
  co_lnotab =       '',
  co_name =         '<module>',
  co_names =        ('echo',),
  co_nlocals =      0,
  co_stacksize =    1,
  co_varnames =     (),
  depth =           0,
  co_consts = (
   codetree(
   co_argcount =     1,
   co_cellvars =     (),
   co_code =         '|\\x00\\x00S',
   co_filename =     '',
   co_firstlineno =  1,
   co_flags =        67,
   co_freevars =     (),
   co_lnotab =       '',
   co_name =         'echo',
   co_names =        (),
   co_nlocals =      1,
   co_stacksize =    1,
   co_varnames =     ('x',),
   depth =           1,
   co_consts = (
    None,
    )),
   None,
   ))

  >>> print( tree.dis() )
    1           0 LOAD_CONST               0 (<code object echo...
                3 MAKE_FUNCTION            0
                6 STORE_NAME               0 (echo)
                9 LOAD_CONST               1 (None)
               12 RETURN_VALUE

        1           0 LOAD_FAST                0 (x)
                    3 RETURN_VALUE

  >>> exec( tree.compile() )
  >>> echo( "hello world" )
  hello world
  
  """
  py2x_opname = "STOP_CODE POP_TOP ROT_TWO ROT_THREE DUP_TOP ROT_FOUR <6> <7> <8> NOP UNARY_POSITIVE UNARY_NEGATIVE UNARY_NOT UNARY_CONVERT <14> UNARY_INVERT <16> <17> LIST_APPEND BINARY_POWER BINARY_MULTIPLY BINARY_DIVIDE BINARY_MODULO BINARY_ADD BINARY_SUBTRACT BINARY_SUBSCR BINARY_FLOOR_DIVIDE BINARY_TRUE_DIVIDE INPLACE_FLOOR_DIVIDE INPLACE_TRUE_DIVIDE SLICE+0 SLICE+1 SLICE+2 SLICE+3 <34> <35> <36> <37> <38> <39> STORE_SLICE+0 STORE_SLICE+1 STORE_SLICE+2 STORE_SLICE+3 <44> <45> <46> <47> <48> <49> DELETE_SLICE+0 DELETE_SLICE+1 DELETE_SLICE+2 DELETE_SLICE+3 STORE_MAP INPLACE_ADD INPLACE_SUBTRACT INPLACE_MULTIPLY INPLACE_DIVIDE INPLACE_MODULO STORE_SUBSCR DELETE_SUBSCR BINARY_LSHIFT BINARY_RSHIFT BINARY_AND BINARY_XOR BINARY_OR INPLACE_POWER GET_ITER <69> PRINT_EXPR PRINT_ITEM PRINT_NEWLINE PRINT_ITEM_TO PRINT_NEWLINE_TO INPLACE_LSHIFT INPLACE_RSHIFT INPLACE_AND INPLACE_XOR INPLACE_OR BREAK_LOOP WITH_CLEANUP LOAD_LOCALS RETURN_VALUE IMPORT_STAR EXEC_STMT YIELD_VALUE POP_BLOCK END_FINALLY BUILD_CLASS STORE_NAME DELETE_NAME UNPACK_SEQUENCE FOR_ITER <94> STORE_ATTR DELETE_ATTR STORE_GLOBAL DELETE_GLOBAL DUP_TOPX LOAD_CONST LOAD_NAME BUILD_TUPLE BUILD_LIST BUILD_MAP LOAD_ATTR COMPARE_OP IMPORT_NAME IMPORT_FROM <109> JUMP_FORWARD JUMP_IF_FALSE JUMP_IF_TRUE JUMP_ABSOLUTE <114> <115> LOAD_GLOBAL <117> <118> CONTINUE_LOOP SETUP_LOOP SETUP_EXCEPT SETUP_FINALLY <123> LOAD_FAST STORE_FAST DELETE_FAST <127> <128> <129> RAISE_VARARGS CALL_FUNCTION MAKE_FUNCTION BUILD_SLICE MAKE_CLOSURE LOAD_CLOSURE LOAD_DEREF STORE_DEREF <138> <139> CALL_FUNCTION_VAR CALL_FUNCTION_KW CALL_FUNCTION_VAR_KW EXTENDED_ARG <144> <145> <146> <147> <148> <149> <150> <151> <152> <153> <154> <155> <156> <157> <158> <159> <160> <161> <162> <163> <164> <165> <166> <167> <168> <169> <170> <171> <172> <173> <174> <175> <176> <177> <178> <179> <180> <181> <182> <183> <184> <185> <186> <187> <188> <189> <190> <191> <192> <193> <194> <195> <196> <197> <198> <199> <200> <201> <202> <203> <204> <205> <206> <207> <208> <209> <210> <211> <212> <213> <214> <215> <216> <217> <218> <219> <220> <221> <222> <223> <224> <225> <226> <227> <228> <229> <230> <231> <232> <233> <234> <235> <236> <237> <238> <239> <240> <241> <242> <243> <244> <245> <246> <247> <248> <249> <250> <251> <252> <253> <254> <255>".split(" ")
  py3k_opname = "STOP_CODE POP_TOP ROT_TWO ROT_THREE DUP_TOP ROT_FOUR <6> <7> <8> NOP UNARY_POSITIVE UNARY_NEGATIVE UNARY_NOT <13> <14> UNARY_INVERT <16> SET_ADD LIST_APPEND BINARY_POWER BINARY_MULTIPLY <21> BINARY_MODULO BINARY_ADD BINARY_SUBTRACT BINARY_SUBSCR BINARY_FLOOR_DIVIDE BINARY_TRUE_DIVIDE INPLACE_FLOOR_DIVIDE INPLACE_TRUE_DIVIDE <30> <31> <32> <33> <34> <35> <36> <37> <38> <39> <40> <41> <42> <43> <44> <45> <46> <47> <48> <49> <50> <51> <52> <53> STORE_MAP INPLACE_ADD INPLACE_SUBTRACT INPLACE_MULTIPLY <58> INPLACE_MODULO STORE_SUBSCR DELETE_SUBSCR BINARY_LSHIFT BINARY_RSHIFT BINARY_AND BINARY_XOR BINARY_OR INPLACE_POWER GET_ITER STORE_LOCALS PRINT_EXPR LOAD_BUILD_CLASS <72> <73> <74> INPLACE_LSHIFT INPLACE_RSHIFT INPLACE_AND INPLACE_XOR INPLACE_OR BREAK_LOOP WITH_CLEANUP <82> RETURN_VALUE IMPORT_STAR <85> YIELD_VALUE POP_BLOCK END_FINALLY POP_EXCEPT STORE_NAME DELETE_NAME UNPACK_SEQUENCE FOR_ITER UNPACK_EX STORE_ATTR DELETE_ATTR STORE_GLOBAL DELETE_GLOBAL DUP_TOPX LOAD_CONST LOAD_NAME BUILD_TUPLE BUILD_LIST BUILD_SET BUILD_MAP LOAD_ATTR COMPARE_OP IMPORT_NAME IMPORT_FROM JUMP_FORWARD JUMP_IF_FALSE JUMP_IF_TRUE JUMP_ABSOLUTE <114> <115> LOAD_GLOBAL <117> <118> CONTINUE_LOOP SETUP_LOOP SETUP_EXCEPT SETUP_FINALLY <123> LOAD_FAST STORE_FAST DELETE_FAST <127> <128> <129> RAISE_VARARGS CALL_FUNCTION MAKE_FUNCTION BUILD_SLICE MAKE_CLOSURE LOAD_CLOSURE LOAD_DEREF STORE_DEREF <138> <139> CALL_FUNCTION_VAR CALL_FUNCTION_KW CALL_FUNCTION_VAR_KW EXTENDED_ARG <144> <145> <146> <147> <148> <149> <150> <151> <152> <153> <154> <155> <156> <157> <158> <159> <160> <161> <162> <163> <164> <165> <166> <167> <168> <169> <170> <171> <172> <173> <174> <175> <176> <177> <178> <179> <180> <181> <182> <183> <184> <185> <186> <187> <188> <189> <190> <191> <192> <193> <194> <195> <196> <197> <198> <199> <200> <201> <202> <203> <204> <205> <206> <207> <208> <209> <210> <211> <212> <213> <214> <215> <216> <217> <218> <219> <220> <221> <222> <223> <224> <225> <226> <227> <228> <229> <230> <231> <232> <233> <234> <235> <236> <237> <238> <239> <240> <241> <242> <243> <244> <245> <246> <247> <248> <249> <250> <251> <252> <253> <254> <255>".split(" ")
  diff_opname = []
  for i, a, b in zip(count(), py2x_opname, py3k_opname):
    if a != b: diff_opname.append([i, a, b])

  #	enum	py2x_opcode	py3k_opcode
  #	13	UNARY_CONVERT	<13>
  #	17	<17>	SET_ADD
  #	21	BINARY_DIVIDE	<21>
  #	30	SLICE+0	<30>
  #	31	SLICE+1	<31>
  #	32	SLICE+2	<32>
  #	33	SLICE+3	<33>
  #	40	STORE_SLICE+0	<40>
  #	41	STORE_SLICE+1	<41>
  #	42	STORE_SLICE+2	<42>
  #	43	STORE_SLICE+3	<43>
  #	50	DELETE_SLICE+0	<50>
  #	51	DELETE_SLICE+1	<51>
  #	52	DELETE_SLICE+2	<52>
  #	53	DELETE_SLICE+3	<53>
  #	58	INPLACE_DIVIDE	<58>
  #	69	<69>	STORE_LOCALS
  #	71	PRINT_ITEM	LOAD_BUILD_CLASS
  #	72	PRINT_NEWLINE	<72>
  #	73	PRINT_ITEM_TO	<73>
  #	74	PRINT_NEWLINE_TO	<74>
  #	82	LOAD_LOCALS	<82>
  #	85	EXEC_STMT	<85>
  #	89	BUILD_CLASS	POP_EXCEPT
  #	94	<94>	UNPACK_EX
  #	104	BUILD_MAP	BUILD_SET
  #	105	LOAD_ATTR	BUILD_MAP
  #	106	COMPARE_OP	LOAD_ATTR
  #	107	IMPORT_NAME	COMPARE_OP
  #	108	IMPORT_FROM	IMPORT_NAME
  #	109	<109>	IMPORT_FROM

  NOP = py2x_opname.index("NOP")
  opmap_new = {
    "SET_ADD":17,
    "STORE_LOCALS":69,
    "LOAD_BUILD_CLASS":34,
    # "MAKE_BYTES":35,
    "POP_EXCEPT":NOP, # 36
    "UNPACK_EX":94,
    "BUILD_SET":192,
    "MAKE_FUNCTION":193,
    }

  for i, a, b in diff_opname:
    if b[0] != "<" and b not in opmap_new: opmap_new[b] = py2x_opname.index(b)
  opmap_3to2 = {}
  for x, i in opmap_new.items():
    j = py3k_opname.index(x) if x in py3k_opname else i
    if j != i: opmap_3to2[j] = i

  if ISPY3K:
    co_args = "co_argcount co_kwonlyargcount co_nlocals co_stacksize co_flags co_code co_consts co_names co_varnames co_filename co_name co_firstlineno co_lnotab co_freevars co_cellvars".split(" ")

  else:
    co_args = "co_argcount co_nlocals co_stacksize co_flags co_code co_consts co_names co_varnames co_filename co_name co_firstlineno co_lnotab co_freevars co_cellvars".split(" ")

    for x, i in opmap_new.items():
      if i is not NOP: py2x_opname[i] = x; setattr(opcode, x, i) # update opname
    opcode.opname = py2x_opname; opcode.opmap.update(opmap_new); reload(dis) # update dis
    for i, x in enumerate(opcode.opname): setattr(opcode, x, i) # populate opcode module w/ opname

  co_constsi = co_args.index("co_consts") # co_consts index pos

  def __init__(self, codeobj = None, depth = 0, **kwds):
    if codeobj: # codeobj
      self.__dict__ = dict((x, getattr(codeobj, x)) for x in self.co_args)
      self.co_consts = tuple(codetree(x, depth = depth + 1) if isinstance(x, types.CodeType) else x for x in codeobj.co_consts) # recurse
    self.depth = depth; self.__dict__.update(kwds)

  def __eq__(self, x): return type(self) == type(x) and self.__dict__ == x.__dict__

  # serializable: codetree(codeobj) == eval( repr( codetree( codeobj ) ) )
  def __repr__(self): return "codetree(**%r)" % self.__dict__

  def __str__(self):
    _ =  " " * self.depth
    hsh = sorted(x for x in self.__dict__.items() if x[0] != "co_consts")
    hsh = "".join(_ + k + " =" + " " * (0x10 - len(k)) + repr(x) + ",\n" for k, x in hsh)
    consts = "".join(_ + " " + str(x) + ",\n" for x in self.co_consts)
    return "codetree(\n" + hsh + "%sco_consts = (\n" % _ + consts + "%s )" % _ + ")"

  def compile(self):
    "codeobj == codetree(codeobj).compile()"
    args = [getattr(self, x) for x in self.co_args] # create list of args
    args[self.co_constsi] = tuple(x.compile() if isinstance(x, codetree) else x for x in self.co_consts)  # recurse
    return types.CodeType(*args)

  # recursive disassembler
  def dis(self):
    def recurse(x, _ = ""):
      if isinstance(x, types.CodeType):
        dis.dis(x); f.seek(0); yield _ + f.read().replace("\n", "\n" + _); f.seek(0); f.truncate()
        for x in x.co_consts:
          for x in recurse(x, _ + "    "): yield x
    sys.stdout = f = io.StringIO() if ISPY3K else io.BytesIO()
    try: s = "\n".join(recurse(self.compile()))
    finally: sys.stdout = sys.__stdout__; f.close()
    return s



if ISPY3K:
  import ast
  # pseudomethod parser
  class parser(ast.NodeTransformer):
    alphanum = "_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    # parse str -> ast node w/ pseudomethod support
    def parse(self, s, fpath, mode):
      keyword = "qjzx" # least common alphabets
      for i, x in enumerate(s): # create a unique keyword guaranteed not to occur in s
        if keyword not in s: break
        keyword += alphanum[i % len(alphanum)]
      self.keyword = keyword; self.bkeyword = keyword.encode("ascii")
      s = s.replace("__pseudomethod__", keyword) # temporarily remove "__pseudomethod__" string to prevent collision
      s = s.replace("..", ".__pseudomethod__.").replace("__pseudomethod__..", "..").replace("..__pseudomethod__", "..") # parse pseudomethod syntax
      n = ast.parse(s, fpath, mode)
      n = self.visit(n) # parse pseudomethod node
      return n

    # recursively print nodes in ast object for debugging
    @staticmethod
    def printnode(node, depth = ""):
      s = node.__dict__.items()
      s = "    ".join("%s %r" % x for x in sorted(node.__dict__.items()))
      print( "%s%s\t%s" % (depth, str(type(node)), s) )
      for x in ast.iter_child_nodes(node): parser.printnode(x, depth = depth + " ")

    # hack node if it contains __pseudomethod__ attr
    def visit_Call(self, node):
      x = node.func
      if type(x) is ast.Attribute:
        x = x.value
        if type(x) is ast.Attribute and x.attr in ("__pseudomethod__", self.keyword): # a..b(...) -> b(a, ...)
          node.args.insert(0, node.func.value.value)
          node.func = ast.copy_location(
            ast.Name(node.func.attr, ast.Load()), # new node
            node.func) # old node
      for x in ast.iter_child_nodes(node): self.visit(x) # recurse
      return node

    # tie up loose ends from string replace
    def visit_Str(self, node):
      node.s = node.s.replace(".__pseudomethod__.", "..").replace(self.keyword, "__pseudomethod__")
      return node
    def visit_Bytes(self, node):
      node.s = node.s.replace(b".__pseudomethod__.", b"..").replace(self.bkeyword, b"__pseudomethod__")
      return node



if not ISPY3K:
  ######## compiler tools
  class compiler(object):
    magic = py3to2_init.importer.magic

    def pre_parse(self, s, _ = "\x00"):
      s = "\n" + s + "\n"; s = s.replace(self.magic, "\n\n", 1)
      return s[1:-1] # preserve lineno (for debugging)

    def tree_parse(self, tree):
      tree = codetree(**tree.__dict__) # copy tree
      assert 0 <= tree.co_argcount < 0x10000; assert 0 <= tree.co_kwonlyargcount < 0x100
      tree.co_argcount |= (tree.co_kwonlyargcount << 16) | 0x1000000 # bitshift & then piggyback co_kwonlyargcount to co_argcount

      s = bytearray(tree.co_code); skip = 0; HAVE_ARGUMENT = opcode.HAVE_ARGUMENT; opmap_3to2 = tree.opmap_3to2
      for i, x in enumerate(s): # map opcodes from 3k to 2x
        if skip: skip -= 1; continue
        if x >= HAVE_ARGUMENT: skip = 2
        if x in opmap_3to2: s[i] = opmap_3to2[x]
      tree.co_code = bytes(s)
      tree.co_consts = tuple( self.tree_parse(x) if isinstance(x, codetree) else x for x in tree.co_consts ) # recurse
      return tree

    def post_parse(self, s):
      s = s.replace("'__next__'", "'next'") # PEP3114  Renaming iterator.next() to .__next__()
      return s

    def compile(self, s, fpath, mode, flags = 0, dont_inherit = 0):
      if not isinstance(s, str): raise TypeError("py3to2 can only compile <str obj> not <%s obj>" % type(s))
      s = self.pre_parse(s)
      s = server_compile(s, fpath, mode, flags, dont_inherit)
      s = self.post_parse(s)
      self.t = t = __builtin__.eval(s)
      if isinstance(t, Exception): raise t
      t = self.tree_parse(t); c = t.compile(); return c
  __builtin__._compile = compiler().compile



######## debugging...
def quicktest():
  if "py3to2_test" not in sys.modules: import py3to2_test
  else: reload(py3to2_test)

if 0 and DEBUG and ISPY3K:
  self = compiler
  s = "ABC ..echo() ..foo()"
  s = self.pre_parse(s)
  n = ast.parse(s, "", "exec")
  self.ast_parse.printd(n)
  n = self.ast_parse().visit(n)
  self.ast_parse.printd(n)

elif 1 and DEBUG and not ISPY3K:
  pass
  s = """
class A:
  def foo(self): pass
class B(A):
  def foo(self): return super().foo()
B().foo()
"""
  c = py3k_compile(s, "", "exec"); t = codetree(c)
  print( t ); print( t.dis() ); print( s )
  py3k_exec(c)
