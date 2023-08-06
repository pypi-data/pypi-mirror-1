import imp, os, sys
if "DEBUG" not in globals(): DEBUG = 0 # True enables printing debug info
MAGIC = "\nfrom __future__ import py3k_syntax\n"

######## import hook
class importer(object):
  py3to2 = None # identifier

  def __init__(self):
    sys.meta_path[:] = [self] + [x for x in sys.meta_path if not hasattr(x, "py3to2")] # restore sys.meta_path
    sys.path_importer_cache = {} # reset cache
    # if "py3k_Lib" not in sys.path: sys.path.insert(0, "py3k_Lib")

  def find_module(self, mname, path = None):
    if DEBUG and 1: print( "py3k find_module(%s, path = %s)" % (mname, path) )

    if path and len(path) is 1:
      x = path[0] + "."
      if mname[:len(x)] == x: mname = mname[len(x):] # import from package

    try: f, fpath, desc = imp.find_module(mname, path if path else sys.path); tp = desc[2]
    except ImportError: return

    if tp is imp.PY_SOURCE: pass
    elif tp is imp.PKG_DIRECTORY: fpath += "/__init__.py"; f = open(fpath)
    else: return

    if MAGIC not in "\n" + f.read() + "\n": return # no py3k magic found in f
    f.seek(0); self.found = f, fpath, desc; return self

  # ex: load_module(mname = "img2txt", fpath = "/usr/lib/python2.6/site-packages/img2txt.py")
  def load_module(self, mname, fpath = ""):
    import py3to2

    if fpath:
      f, fpath, desc = imp.find_module(mname, [os.path.dirname(fpath)])
      if desc[2] is not imp.PY_SOURCE: return imp.load_module(mname, f, fpath, desc)
    else: f, fpath, desc = self.found
    s = f.read(); f.close(); tp = desc[2]
    if DEBUG and 1: print( "py3k load_module(%s, fpath = %s, desc = %s)" % (mname, fpath, desc) )


    if mname in sys.modules: m = sys.modules[mname]; new = None # if exist: use existing module
    else: m = sys.modules[mname] = imp.new_module(mname); new = True # else: new module
    try:
      c = py3to2.py3k_compile(s, fpath, "exec")
      py3to2.py3k_exec(c, m.__dict__)

      m.__file__ = fpath
      if tp is imp.PKG_DIRECTORY: m.__path__ = [os.path.dirname(fpath)] # package.__path__
      m.__loader__ = self.load_module
      return m
    except:
      if new: del sys.modules[mname] # if new module fails loading, del from sys.modules
      print( "\nFAILED py3to2 load_module(mname = %s, fpath = %s, desc = %s)\n" % (mname, fpath, desc) ) # notify user exception originated from failed py3to2 import
      raise
load_module = importer().load_module
