from __future__ import print_function
import io, imp, itertools, re, os, sys, tempfile, time, traceback, types; from itertools import *

ISPY3K = True if sys.version_info[0] == 3 else None
if "DEBUG" not in globals(): DEBUG = 0 # set to 0 to suppress printing debug info
def echo(x): return x



######## builtins
if ISPY3K:
  import builtins; builtins.reload = imp.reload
  
else:
  import __builtin__, _py3to2, py3to2, py3to2_init, cStringIO as StringIO; reload(py3to2_init)
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
  def server_compile(*args, **kwds):
    try:
      c = builtins.compile(*args, **kwds)
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
import dis, opcode
class codetree(object):
  """
  ################################################################
  mutable, serializable codeobj-like obj which u can edit,
  disassemble, debug, & recompile into a full-fledged codeobj

  >>> codeobj = compile("def foo(x): return x", "", "exec")
  >>> tree = codetree(codeobj)
  >>> print( t )
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
  co_names =        ('foo',),
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
   co_name =         'foo',
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
    1           0 LOAD_CONST               0 (<code object foo...
                3 MAKE_FUNCTION            0
                6 STORE_NAME               0 (foo)
                9 LOAD_CONST               1 (None)
               12 RETURN_VALUE

        1           0 LOAD_FAST                0 (x)
                    3 RETURN_VALUE
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
    "LOAD_BUILD_PSEUDOMETHOD":37,
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

  def __repr__(self):
    "serializable: codetree(codeobj) == eval(repr(codetree(codeobj)))"
    return "codetree(**%r)" % self.__dict__

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

  def dis(self):
    def recurse(x, _ = ""):
      if isinstance(x, types.CodeType):
        dis.dis(x); f.seek(0); yield _ + f.read().replace("\n", "\n" + _); f.seek(0); f.truncate()
        for x in x.co_consts:
          for x in recurse(x, _ + "    "): yield x

    # sys.stdout = f = io.BytesIO()
    sys.stdout = f = tempfile.TemporaryFile(mode = "w+")
    try: s = "\n".join(recurse(self.compile()))
    finally: sys.stdout = sys.__stdout__; f.close()
    return s



if not ISPY3K:
  ######## compiler
  import ast, tokenize
  class compiler(object):
    magic = py3to2_init.importer.magic

    def pre_parse(self, s):
      def printd(tokenized):
        self.tokenized = tokenized = tuple(self.tokenized)
        for x in tokenized: sys.stdout.write( "%s %r, " % (tokenize.tok_name[x[0]], x[1]) )
        print( "" )

      from tokenize import OP, NAME

      s = s.replace("...", "<ellipses>")
      src = io.BytesIO(s); src.seek(0); self.tokenized = tokenized = tokenize.generate_tokens(src.readline)
      arr = io.BytesIO(); i0 = tp0 = tk0 = 0
      for tp, tk, beg, end, line in tokenized:
        edit = None
        if tp is OP:
          if tk == "." == tk0: edit = tk = "__pseudomethod__." # pseudomethod

        if edit:
          (brow, bcol), (erow, ecol) = beg, end
          assert brow == erow, (brow, erow)
          i = src.tell() - len(line)
          arr.write(s[i0:i + bcol]); arr.write(tk); i0 = i + ecol
        tp0, tk0 = tp, tk

      arr.write(s[i0:])
      s = arr.getvalue()
      s = s.replace("<ellipses>", "...")
      return s

    def pre_parse(self, s, _ = "\x00"):
      s = "\n" + s + "\n"
      s = s.replace(self.magic, "\n\n", 1)
      s = s.replace("..", ".__pseudomethod__.").replace("__pseudomethod__..", "..")
      return s[1:-1] # preserve lineno (for debugging)

    def tree_parse(self, tree):
      tree = codetree(**tree.__dict__) # copy tree
      co_argcount, co_kwonlyargcount, co_nlocals, co_stacksize, co_flags, co_code, co_consts, co_names, co_varnames, co_filename, co_name, co_firstlineno, co_lnotab, co_freevars, co_cellvars, depth, opmap_3to2 = tree.co_argcount, tree.co_kwonlyargcount, tree.co_nlocals, tree.co_stacksize, tree.co_flags, tree.co_code, tree.co_consts, tree.co_names, tree.co_varnames, tree.co_filename, tree.co_name, tree.co_firstlineno, tree.co_lnotab, tree.co_freevars, tree.co_cellvars, tree.depth, tree.opmap_3to2

      assert 0 <= co_argcount < 0x10000; assert 0 <= co_kwonlyargcount < 0x100
      tree.co_argcount = co_argcount | (co_kwonlyargcount << 16) | 0x1000000 # bitshift & then piggyback co_kwonlyargcount to co_argcount

      from opcode import EXTENDED_ARG, HAVE_ARGUMENT, LOAD_ATTR, LOAD_BUILD_PSEUDOMETHOD, LOAD_FAST, LOAD_GLOBAL, LOAD_LOCALS, LOAD_NAME, LOAD_DEREF, NOP
      code = bytearray(co_code); pseudomethod = skip = 0
      for i, x in enumerate(code):
        if skip: skip -= 1; continue
        if x >= HAVE_ARGUMENT: skip = 2
        if x in opmap_3to2: code[i] = x = opmap_3to2[x] # map 3k opcodes -> 2x
        if x is LOAD_ATTR: # pseudomethod hack
          assert code[i + 3] is not EXTENDED_ARG
          arg = code[i + 1] + (code[i + 2] << 8); name = co_names[arg]
          if pseudomethod:
            freevars = co_cellvars + co_freevars
            # module level
            if depth is 0: x, arg = LOAD_NAME, arg # co_names
            # function / class level
            elif name in co_varnames: x, arg = LOAD_FAST, co_varnames.index(name) # co_varnames
            elif name in freevars: x, arg = LOAD_DEREF, freevars.index(name) # co_cellvars / co_freevars
            else: x, arg = LOAD_GLOBAL, arg # co_names
            code[i - 3:i + 3] = x, arg & 0xff, arg >> 8, LOAD_BUILD_PSEUDOMETHOD, NOP, NOP; pseudomethod = 0
          elif name == "__pseudomethod__": pseudomethod = i
      tree.co_code = bytes(code)

      def recurse():
        for x in co_consts:
          tp = type(x)
          if tp is codetree: yield self.tree_parse(x)
          elif tp is str: yield x.replace(".__pseudomethod__.", "..")
          else: yield x
      tree.co_consts = tuple(recurse()); return tree

    def post_parse(self, s):
      s = s.replace("'__next__'", "'next'") # PEP3114  Renaming iterator.next() to .__next__()
      return s

    def compile(self, s, fpath, mode, flags = 0, dont_inherit = 0):
      s = self.pre_parse(s)
      s = server_compile(s, fpath, mode, flags, dont_inherit)
      s = self.post_parse(s)
      self.t = t = __builtin__.eval(s)
      if isinstance(t, Exception): raise t
      t = self.tree_parse(t); c = t.compile(); return c
  compiler = compiler(); __builtin__._compile = compiler.compile
  


######## debugging...
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
  # s = """
# 1 ..abs()
# # abs(1)
# for x in (1,2): pass
# """
  # s = """
# def foo():
  # a; b = 1; b
  # def bar():
    # nonlocal b
    # b = 2; b
# """
  c = py3k_compile(s, "", "exec"); t = codetree(c)
  print( t )
  # print( compiler.t.dis() )
  print( t.dis() ); print( s )
  py3k_exec(c)
