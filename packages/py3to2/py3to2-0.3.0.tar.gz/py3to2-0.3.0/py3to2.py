import io, imp, re, os, sys, tempfile, time, traceback, types; from itertools import *

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
  builtins.input = raw_input # PEP3111  Simple input built-in in Python 3000

  def add2builtins(f):
    f.__name__ = fname = f.__name__.replace("py3k_", "")
    f.__doc__ = getattr( getattr(__builtin__, fname, None), "__doc__", None )
    setattr(builtins, fname, f); return f

  @add2builtins
  def py3k_oct(x): return oct(x).replace("0", "0o", 1)



######## py3k server
if ISPY3K:
  import parser; sys.ps1 = ""
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
    try: os.kill(SERVER.pid, signal.SIGTERM) # kill prev server
    except: pass
    try: map(os.close, SERVERIO) # close prev io pipe
    except: pass
    try: del py3to2.SERVER # prevent annoying error upon SystemExit
    except: pass
  if "SERVER" not in globals(): atexit.register(py3k_close) # close server @ exit
  py3k_close() # close existing server if any

  SERVERIO = os.pipe(); print( "created <read/write pipes %i/%i>" % SERVERIO ) # create io pipes

  try: # start up py3k server
    print( "py3k server starting..." ); 
    SERVER = subprocess.Popen(
      "python3.0 -E -i %s" % py3to2.__file__.replace(".pyc", ".py"),
      stdin = subprocess.PIPE,
        stdout = SERVERIO[1],
      stderr = subprocess.STDOUT,
      shell = True)
  except OSError: raise OSERROR("py3to2 could not find or run python3.0.  make sure python3.0 is properly installed & exists in $PATH env variable")

  def py3k_input(s): SERVER.stdin.write(s) # py3k_input

  EOF = "%s\n" % id("eof")
  def py3k_read(): # py3k_read
    n = len(EOF)
    py3k_input("\n" + EOF)
    arr = io.BytesIO()
    while True:
      x = os.read(SERVERIO[0], 4096); arr.write(x)
      if len(x) < len(EOF): x = arr.getvalue()
      if x[-n:] == EOF: break
    return arr.getvalue()[:-n]
  py3k_input("print( '...py3k server started w/ <pid %i> & <i/o pipes %i/%i>' )\n" % (SERVER.pid, SERVERIO[1], SERVERIO[0])); print( py3k_read() )

  def server_compile(*args, **kwds): # server compile
    py3k_input("server_compile(*%s, **%s)" % (args, kwds))
    s = py3k_read()
    return s



######## codetree
import dis, opcode
class codetree(object):
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
    opcode.opname = py2x_opname; reload(dis) # update dis
    for i, x in enumerate(opcode.opname): setattr(opcode, x, i) # populate opcode module w/ opname

    # #### op3to2
    # def op3to2(self):
      # self = codetree(**self.__dict__) # copy self
      # assert 0 <= self.co_argcount < 0x10000; assert 0 <= self.co_kwonlyargcount < 0x100
      # self.co_argcount |= (self.co_kwonlyargcount << 16) | 0x1000000 # bitshift & then piggyback co_kwonlyargcount to co_argcount

      # s = bytearray(self.co_code); skip = 0; HAVE_ARGUMENT = opcode.HAVE_ARGUMENT; opmap_3to2 = self.opmap_3to2
      # for i, x in enumerate(s): # map opcodes from 3k to 2x
        # if skip: skip -= 1; continue
        # if x >= HAVE_ARGUMENT: skip = 2
        # if x in opmap_3to2: s[i] = opmap_3to2[x]
      # self.co_code = bytes(s)
      # self.co_consts = tuple( x.op3to2() if isinstance(x, codetree) else x for x in self.co_consts ) # recurse
      # return self



  #### common
  co_constsi = co_args.index("co_consts") # co_consts index pos

  def __init__(self, code = None, depth = 0, **kwds):
    if code: # code object
      self.__dict__ = dict((x, getattr(code, x)) for x in self.co_args)
      self.co_consts = tuple(codetree(x, depth = depth + 1) if isinstance(x, types.CodeType) else x for x in code.co_consts) # recurse
    self.depth = depth; self.__dict__.update(kwds)

  def __eq__(self, x): return type(self) == type(x) and self.__dict__ == x.__dict__

  def __repr__(self): return "codetree(**%r)" % self.__dict__

  def __str__(self):
    _ =  " " * self.depth
    hsh = sorted(x for x in self.__dict__.items() if x[0] != "co_consts")
    hsh = "".join(_ + k + " =" + " " * (0x10 - len(k)) + repr(x) + ",\n" for k, x in hsh)
    consts = "".join(_ + " " + str(x) + ",\n" for x in self.co_consts)
    return "codetree(\n" + hsh + "%sco_consts = (\n" % _ + consts + "%s )" % _ + ")"

  def compile(self):
    args = [getattr(self, x) for x in self.co_args] # create list of args
    args[self.co_constsi] = tuple(x.compile() if isinstance(x, codetree) else x for x in self.co_consts)  # recurse
    return types.CodeType(*args)

  def dis(self):
    def recurse(x, _ = ""):
      if isinstance(x, types.CodeType):
        dis.dis(x); f.seek(0); yield _ + f.read().replace("\n", "\n" + _); f.seek(0); f.truncate()
        for x in x.co_consts:
          for x in recurse(x, _ + "\t"): yield x

    sys.stdout = f = io.BytesIO()
    try: s = "\n".join(recurse(self.compile()))
    finally: sys.stdout = sys.__stdout__; f.close()
    return s



if not ISPY3K:
  ######## compiler
  import ast, tokenize
  class compiler(object):
    def pre_parse(self, s):
      def printd(tokenized):
        self.tokenized = tokenized = tuple(self.tokenized)
        for x in tokenized: sys.stdout.write( "%s %r, " % (tokenize.tok_name[x[0]], x[1]) )
        print( "" )

      from tokenize import OP, NAME

      src = io.BytesIO(s); src.seek(0); self.tokenized = tokenized = tokenize.generate_tokens(src.readline)
      arr = io.BytesIO(); i0 = tp0 = tk0 = 0
      for tp, tk, beg, end, line in tokenized:
        edit = None
        if tp is OP:
          if tk == "." == tk0: edit = "__pseudomethod__." # pseudomethod

        if edit:
          (brow, bcol), (erow, ecol) = beg, end
          assert brow == erow, (brow, erow)
          i = src.tell() - len(line)
          arr.write(s[i0:i + bcol]); arr.write(edit); i0 = i + ecol
        tp0, tk0 = tp, tk

      arr.write(s[i0:]); return arr.getvalue()

    def tree_parse(self, tree):
      tree = codetree(**tree.__dict__) # copy tree
      co_argcount, co_kwonlyargcount, co_nlocals, co_stacksize, co_flags, co_code, co_consts, co_names, co_varnames, co_filename, co_name, co_firstlineno, co_lnotab, co_freevars, co_cellvars, depth, opmap_3to2 = tree.co_argcount, tree.co_kwonlyargcount, tree.co_nlocals, tree.co_stacksize, tree.co_flags, tree.co_code, tree.co_consts, tree.co_names, tree.co_varnames, tree.co_filename, tree.co_name, tree.co_firstlineno, tree.co_lnotab, tree.co_freevars, tree.co_cellvars, tree.depth, tree.opmap_3to2

      assert 0 <= co_argcount < 0x10000; assert 0 <= co_kwonlyargcount < 0x100
      tree.co_argcount = co_argcount | (co_kwonlyargcount << 16) | 0x1000000 # bitshift & then piggyback co_kwonlyargcount to co_argcount

      from opcode import EXTENDED_ARG, HAVE_ARGUMENT, LOAD_ATTR, LOAD_BUILD_PSEUDOMETHOD, LOAD_FAST, LOAD_GLOBAL, LOAD_LOCALS, LOAD_NAME, LOAD_DEREF, NOP
      code = bytearray(co_code); skip = 0
      for i, x in enumerate(code):
        if skip: skip -= 1; continue
        if x >= HAVE_ARGUMENT: skip = 2
        if x in opmap_3to2: code[i] = x = opmap_3to2[x] # map 3k opcodes -> 2x

      def hack(): # extra opcode hack
        def argi2s(x, _ = chr(EXTENDED_ARG)):
          s = ""
          while True:
            y = x & 0xffff; x >>= 16; s = chr(y & 0xff) + chr( y >> 8) + _ + s
            if not x: break
          return s[:-1]

        _arg = "", 0, None
        freevars = co_cellvars + co_freevars
        op0 = NOP; arg0 = _arg; i0 = -1; skip = 0
        for i, op in enumerate(code):
          if skip: skip -= 1; continue

          arg = 0; j = i
          if op >= HAVE_ARGUMENT:
            skip = 2; arg = code[i + 1] + (code[i + 2] << 8); j += 3 # get arg
            while code[j] is EXTENDED_ARG: skip += 3; arg = (arg << 16) + code[j + 1] + (code[j + 2] << 8); j += 3 # get extended arg
          arg = code[i + 1:j], arg, None

          if op is LOAD_ATTR:
            arg = arg[:2] + (co_names[arg[1]],)
            if op0 is LOAD_ATTR and arg0[2] == "__pseudomethod__":
              x = arg[2]

              # module level
              if depth is 0: op0, arg0 = LOAD_NAME, arg # co_names

              # function / class level
              elif x in co_varnames: # co_varnames
                op0 = LOAD_FAST
                arg0 = co_varnames.index(x)
                arg0 = argi2s(arg0), arg0, arg[2]
              elif x in freevars: # co_cellvars / co_freevars
                op0 = LOAD_DEREF
                arg0 = freevars.index(x)
                arg0 = argi2s(arg0), arg0, arg[2]
              else: op0, arg0 = LOAD_GLOBAL, arg # co_names

              op, arg = LOAD_BUILD_PSEUDOMETHOD, _arg

          if DEBUG and 0: print( opcode.opname[op0], arg0[1] )
          yield chr(op0) + str(arg0[0]); i0, op0, arg0 = i, op, arg
        yield chr(op0) + str(arg0[0])

      tree.co_code = "".join(hack())[1:]
      tree.co_consts = tuple( self.tree_parse(x) if isinstance(x, codetree) else x for x in co_consts ) # recurse
      return tree

    # class ast_parse(ast.NodeTransformer):
      # @classmethod
      # def printd(self, node, depth = ""):
        # s = node.__dict__.items()
        # s = "    ".join("%s %r" % x for x in sorted(node.__dict__.items()))
        # print( "%s%s\t%s" % (depth, str(type(node)), s) )
        # for x in ast.iter_child_nodes(node): self.printd(x, depth = depth + " ")

      # def visit_Call(self, node):
        # x = node.func
        # if type(x) is ast.Attribute:
          # x = x.value
          # if type(x) is ast.Attribute and x.attr == "__pseudomethod__": # a..b(...) -> b(a, ...)
            # node.args.insert(0, node.func.value.value)
            # node.func = ast.copy_location(
              # ast.Name(node.func.attr, ast.Load()), # new node
              # node.func) # old node
        # for x in ast.iter_child_nodes(node): self.visit(x) # recurse
        # return node

    def post_parse(self, s):
      s = s.replace("'__next__'", "'next'") # PEP3114  Renaming iterator.next() to .__next__()
      return s

    def compile(self, s, fpath, mode, flags = 0, dont_inherit = 0):
      s = self.pre_parse(s)
      s = server_compile(s, fpath, mode, flags, dont_inherit)
      s = self.post_parse(s)
      self.t = t = eval(s)
      if isinstance(t, Exception): raise t
      t = self.tree_parse(t); c = t.compile(); return c
  compiler = compiler(); __builtin__._compile = compiler.compile
  


######## debugging...
if DEBUG and ISPY3K and 0:
  self = compiler
  s = "ABC ..echo() ..foo()"
  s = self.pre_parse(s)
  n = ast.parse(s, "", "exec")
  self.ast_parse.printd(n)
  n = self.ast_parse().visit(n)
  self.ast_parse.printd(n)

elif DEBUG and not ISPY3K and 0:
  pass
  # import fail
  # s = "a ..b() ..c()"
  s = "(1,2) ..tuple()"
  s = """
def foo(a, *b, c = 0): return a, b, c
print( foo.__kwdefaults__ )
assert foo(1, 2, 3, c = 4) == (1, (2, 3), 4)
"""
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
  # print( t.dis() ); print( s )
  py3k_exec(c)
