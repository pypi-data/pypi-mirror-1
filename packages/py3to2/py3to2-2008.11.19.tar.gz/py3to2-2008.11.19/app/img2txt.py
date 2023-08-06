# import img2txt; reload(img2txt); from img2txt import *
from __future__ import py3k_syntax

import functools, itertools, re, subprocess, time, types; from itertools import *

import numpy; from numpy import * ; from scipy import weave

if 1: ######## general
  def echo(x): return x

  def _enumerate(arr, i = None):
    if i: return zip(count(i), arr)
    return enumerate(arr)

  def flatten( * arr): return arr ..walktree() ..tuple()

  def isint(x):
    try: x & 0; return True
    except: return False

  def _profile(exe,n = None,lines = 64):
    import cProfile as profile; import pstats
    if n is not None: exe = 'for i in range({0}): {1}'.format(n,exe)
    x = pstats.Stats(profile.Profile().run(exe)).sort_stats('time'); x.print_stats(lines); return x

  def screensize(): s = system_("stty -a"); row, col = re.search("rows .*?(\d*).*?columns .*?(\d*)", s).groups(); return int(row), int(col)

  def shapes( * arr): return [shape(x) for x in arr]

  def strjoin(s, _ = ""): return _.join(s)

  def system_(exe): exe = subprocess.Popen(exe, shell = 1, stdout = subprocess.PIPE, close_fds = 1).stdout; s = exe.read(); exe.close(); return s

  def walktree(tree, isleaf = lambda x: not hasattr(x, "__iter__"), not_ = None, depth = -1):
    def walk(tree, depth):
      if isleaf(tree) or not depth: yield tree
      else:
        for x in tree:
          for y in walk(x, depth-1): yield y
    if not_: istree = lambda x: not isleaf(x)
    return walk(tree, depth)

######## class
class savestate(object): ## add to subclass to save user-defined states
  def __savestate__(self): state = self.__dict__.copy(); state["__self__"] = self; return state

  @staticmethod
  def __loadstate__(state): state = state.copy(); self = state["__self__"]; del state["__self__"]; self.__dict__ = state; return self

class _asarray(ndarray, savestate): ## array w/ serializable states
  def __new__(self, arr, dtype = None, order = None):
    arr = numpy.asarray(arr, dtype, order)
    self = ndarray.__new__(self, arr.shape, arr.dtype, arr.data)
    if arr.strides: self.strides = arr.strides
    return self

if 1: ######## math
  EPS = MachAr().eps; TINY = MachAr().tiny; HUGE = MachAr().huge
  STD = 0.682689492137085897170465091264075844955825933453208781974788900; STD2 = 0.954499736103641585599434725666933125056447552596643132032668000
  array = numpy.array
  rng = random.random
  stdev = numpy.std
  variance = numpy.var

  def divceil(a, b): return (a + b - 1) // b

  def divround(a, b): return (a + (b >> 1)) // b

  def find2nd(arr, x):
    n = arr.shape[-1]; x = (arr == reshape(x, (-1, 1))) ..asarray(dtype = uint8)
    out = repeat(n, len(x)); out.fill(n); weave.inline("""
    for(int i = 0; i < Nx[0]; i++){
    for(int j = 0; j < Nx[1]; j++){
    if(x[j]) {out[i] = j; break;}
    } x += Nx[1];}""", ("out", "x"), compiler = "gcc"); return arange(len(out)), out

  def histogram_(arr):
    arr = asarray(arr); n = arr.max() + 1; assert n < 0x10000, n; h = zeros(n, int)
    weave.inline("""for(int i = 0; i<Narr[0]; i++){h[ * arr] += 1; arr++;}""", ("arr", "h"), compiler = "gcc")
    return h

  def invzero(x, nan = nan): return 1 / x if x else nan

  def monotonic(arr):
    if all(arr[1:] >= arr[:-1]): return 1
    elif all(arr[1:] <= arr[:-1]): return -1
    return 0

  def popcount(x): # 64 bit population count - O(log)
    x = x - ((x >> 1) & 0x5555555555555555) # count 2 bits
    x = ((x >> 2) & 0x3333333333333333) + (x & 0x3333333333333333) # count 4 bits
    x = ((x >> 4) + x) & 0x0f0f0f0f0f0f0f0f # count 8 bits
    x += x >> 8 # count 16 bits
    x += x >> 16 # count 32 bits
    x += x >> 32 # count 64 bits
    return x & 127

  def rotate3d(x, y, z, t):
    inv = 1 / sqrt(x * x + y * y + z * z); x, y, z = x * inv, y * inv, z * inv; c = cos(t); s = sin(t); d = 1-c
    return [[x * x * d+c,   x * y * d-z * s, z * x * d+y * s],
            [x * y * d+z * s, y * y * d+c,   y * z * d-x * s],
            [z * x * d-y * s, y * z * d+x * s, z * z * d+c  ]] ..asarray()

######## img2txt
class _img2txt(object):
  debug = 0
  _ = ord(" ") # convenience var for blank space
  buf = empty(0, dtype = int64) # internal buffer for outputting text
  fres = r_[10, 6] # row x col resolution of a character block
  lucida = "AAAAAAAAAAAAQRAEARAAAIqiAAAAAAAAAEX5ylcUAACEVxwMRT0EAIBYKQylRgAAAKE4Zpt5AAAE\nQQAAAAAAADBCEARBIDAAA4EgCIIQAwAAsRkKAAAAAAAAEMRHEAAAAAAAAMAwCAEAAAAeAAAAAAAA\nAADAMAAAIAQhDCEIAQCAE0VRFDkAAIBREARBfAAAgANBCCF4AACAB0EMBDkAAADCKMmHIAAAgCcI\nDgQ5AAAAJwTNFDkAAIAHIQQhCAAAgBMlThQ5AACAE0UehBwAAAAAMAzAMAAAAAAwDMAwCAEAAEDM\nwEAAAAAAAD / wAwAAAAAEBmYEAACAJ0EIARAAAIAXdVUfeAAAAMMokieFAADAE0VPFD0AAAAnBEEg\ncAAAwBNFURQ9AACAJwiOIHgAAIAnCI4gCAAAACcEWSRxAABAFEVfFEUAAMBHEARBfAAAgIMgCIIY\nAABAlBRDkUQAAIAgCIIgeAAAQLRtV1VFAABANF1VlkUAAIATRVEUOQAAwBNFTxAEAACAE0VRFDkw\nAMCRJEeRRAAAACcIDAQ5AADARxAEQRAAAEAURVEUOQAAQBhJksIQAABAVFXVoygAAEAoMQgjhQAA\nQKQoBEEQAADAByGEEHwAABxBEARBEBwAgSAQBAJBIAAOgiAIgiAOAABBKIoSAQAAAAAAAAAAPwAE\nAgAAAAAAAAAAOBAn+QAAQRA0UxQ9AAAAAHhBEHgAABAEeVGUWQAAAAA40Rd4AAAYQXgEQRAAAAAA\neFGUWZADQRB0UxRFAAAIADgIgiAAAAgAOAiCIMgBgiBIiqFIAAAHQRAEQRAAAAAAfFVVVQAAAAB0\nUxRFAAAAADhRFDkAAAAANFMUPUEAAAB4UZRZEAQAAGiWIAgAAAAAcAIDOQAAAEF4BEFgAAAAAERR\nlF0AAAAARIqiEAAAAACUbStJAAAAAEQKoUQAAAAAhJLEMMQAAAB8CCF8AAAcQRACQRAcAARBEARB\nEAQADoIgEIIgDgAAAABnDgAAAAAAAAAAAAAA\n" # lucida console 06x10 bitmap font encoded in 64 bits - use str2font to decode

  def printd(self, arr): # print an array in row x col format - for debugging
    if isinstance(arr, int64): arr = [arr & (1 << i) for i in range(self.fres.prod())] ..asarray(dtype = bool).reshape(self.fres)
    for x in arr[:-1]: print( "".join(str(int(x)) if x else "." for x in x) )
    print( "".join(str(int(x)) if x else "_" for x in arr[-1]) )

  def importfont(self, file): # internal fnc for importing font bitmaps
    debug = self.debug; from PIL import Image; fres = self.fres
    font = Image.open(file).getdata() ..asarray(dtype = int64)
    if debug: font = font.reshape(fres * (6, 16)); self.printd(font[:fres[0]])

    font = font.reshape(6, fres[0], 16, fres[1]).transpose(0, 2, 1, 3) .reshape(r_[6 * 16, fres.prod()])
    for i, x in enumerate(font.T): font[:,0] |= x << i
    font = font[:, 0]
    if debug:
      for x in font[1:1+2]: self.printd(x); print()
    return font

  def font2str(self, font): import base64; return base64.encodestring(font.tostring())
  def str2font(self, s): import base64; s = base64.decodestring(s); return ndarray(len(s) // 8, dtype = int64, buffer = s)

  def __init__(self):
    debug = self.debug; fres = self.fres

    arr = self.str2font(self.lucida); arr = arr[..., newaxis].repeat(5, axis = -1) # original
    arr[..., 1] >>= fres[1] # shift up
    arr[..., 2] <<= fres[1] # shift down
    cll = sum(1 << arange(0, fres.prod(), fres[1])) ^ 0xffffffffffffffff # cll left boundary
    x = arr[..., 3]; x &= cll; x >>= 1 # shift left
    x = arr[..., 4]; x <<= 1; x &= cll # shift right
    if 0 and debug:
      for x in arr[17, :5]: self.printd(x)

    fmap = arr
    fidx = r_[32:128]; assert len(fidx) == len(fmap)
    fpop = popcount(fmap[:, 0]); fpop[-1] = fres.prod()

    fmap = (fmap, fmap ^ True) ..concatenate(axis = 0)
    fidx = r_[fidx, fidx + 0x80]; fpop = r_[fpop, fres.prod() - fpop] # include inverted color

    cll = [0] + [i for i, x in enumerate(fpop) if x] # cll blanks
    fmap, fidx, fpop = (x[cll] for x in (fmap, fidx, fpop))

    cll = fpop.argsort() # sort by population count
    fmap, fidx, fpop = (x[cll] for x in (fmap, fidx, fpop))

    hst = histogram_(fpop); hst = [x for x in enumerate(hst) if x[1]] # cll blanks in histogram

    fbin_ = []; pop = 0; a = b = c = 0

    for count, idx in hst:
      c += idx
      while pop < count: pop += 1; fbin_.append((a, c)) # create bins
      a = b; b = c
    fbin_ = asarray(fbin_); fbin_[fres.prod() - 1, 1] = fbin_[-1, 1]; fbin_ = fbin_[:fres.prod()]

    a, b = fbin_.T
    x = 4; b[b < x] = x # low pixel cutoff
    x = len(fpop) - 4; a[a > x] = x # high pixel cutoff

    self.fmap = fmap; self.fidx = fidx; self.fpop = fpop; self.fbin_ = fbin_
    self.fbin = fbin = fbin_.copy(); fbin[fbin_[:, 0] == 0, 0] = 1 # never blank blocks

    chrmap = [chr(x) for x in range(0x80)]
    chrmap += ["\33[7m%s\33[0m" % x for x in chrmap] # invert color
    self.chrmap = chrmap = asarray(chrmap)
    if debug: print( chrmap ..strjoin() ); print( chrmap[fidx] ..strjoin() ) # print chrmap in ascending density

    def method(fname):
      @functools.wraps(getattr(ndarray, fname), assigned = ("__name__", "__doc__"))
      def f(self, *args, **kwds): x = getattr(self.buf, fname); return x(*args, **kwds) if kwds else x(*args)
      return f

    for x in dir(ndarray): # add arr-like methods - from self.buf
      if not hasattr(_img2txt, x) and getattr(ndarray, x) ..callable() and "set" not in x: setattr(_img2txt, x, method(x)) # disallow setters - numpy bug

  def fill(self, arr): # fill buf w/ data
    fres = self.fres; self.res = res = divceil(arr.shape, fres) # res
    if not all(arr.shape // fres == res): x = arr; arr = zeros(res * fres, dtype = bool); arr[:x.shape[0], :x.shape[1]] = x # resize canvas
    if len(self) != res.prod(): self.buf = empty(res.prod(), dtype = int64) # resize buf
    buf = self.buf; buf.fill(0) # clear buf

    arr = asarray(arr, dtype = bool) .reshape(res[0], fres[0], res[1], fres[1]) .transpose(1, 3, 0, 2) .reshape(fres.prod(), -1) # create blocks
    for i, x in enumerate(arr != 0): buf |= x << i # fill buf
    return self

  def itp(self, blank = True, wmatch = 2, wmismatch = 1): # interpolate block -> ascii chr
    buf = self.buf; self.pop = pop = popcount(buf); fbin = self.fbin_ if blank else self.fbin; fhst = [self.fmap[a:b] for a, b in fbin] # fbin, fhst
    for i, (a, b), f in zip(count(1), fbin, fhst):
      cll = pop == i
      if not cll.any(): continue
      x = buf[cll]; f = f.T[..., newaxis]
      y = popcount(x & f) # match
      y[0] *= wmatch # weight original match
      y[0] -= popcount(x ^ f[0]) * wmismatch # subtract mismatch
      y = y.sum(axis = 0); y = y.argsort(axis = 0)[-1] + a; buf[cll] = self.fidx[y] # tally weights & pick highest
    buf[buf == 0] = self._; return self

  def tostr(self): return "\n".join( "".join(self.chrmap[x]) for x in self.reshape(self.res) )

  def from_image(self, file, scale = 1): # must be a file or filename
    from PIL import Image; arr = Image.open(file) # import img
    fres = self.fres[::-1]; res = asarray(arr.size) * scale / fres; res = ceil(res).astype(int) * fres
    if not all(res == arr.size): arr = arr.resize(res) # resize img
    self.img = arr; fres = fres[::-1]; res = res[::-1]; self.res = res // fres # save res
    arr = (arr if arr.mode == "1" else arr.convert("1")).getdata() ..asarray(dtype = bool).reshape(res); self.fill(arr).itp() # itp
    return self

  @staticmethod
  def test():
    self = type(img2txt)
    self.debug = 1
    self = self()
    if 1:
      # font = "lucida console bold 06x10.bmp"
      img = "mario.jpg"
      scale = 0.5
      color = 1
      arr = self.from_image(img, scale = scale)
      print( self.tostr() )
    self.debug = None

# img2txt = _img2txt()

class _img2txtcolor(_img2txt):
  def __init__(self):
    debug = self.debug; _img2txt.__init__(self)

    clrmap = "  ".join( "\33[38;5;231m%c\33[0m" % x for x in range(0x80) )
    clrmap = "  ".join(( clrmap, clrmap.replace("231", "231;7") ))
    i = arange(16, 232); i[0] = 17 # rgb666
    clrmap = "  ".join( clrmap.replace("231", str(x)) for x in i )
    self.clrmap = clrmap = clrmap.split("  ") ..ravel()

    if 1 and debug:
      print( clrmap[:256] ..strjoin() )
      for x in clrmap.reshape(216, -1)[:4]: print( x[self.fidx] ..strjoin() )

  bwrgbcmy = "0x000000 0xFFFFFF 0xFF0000 0x00FF00 0x0000FF 0x00A8EC 0xE3007B 0xF9F400"
  bwrgbcmy = ( eval(x) for x in bwrgbcmy.split(" ") ) ..asarray()
  print( bwrgbcmy )
  rgbi = (36, 6, 1) ..asarray(dtype = uint8) # set color channels to 8bit - numpy defaults to 64 bits, wasting space by order of magnitude
  def from_image(self, file, scale = 1, color = True):
    super().from_image(file, scale); res = self.res; arr = self.img
    if color and arr.mode in ("CYMK", "RGB"):
      color = (arr if arr.mode == "RGB" else arr.convert("RGB")).resize(res[::-1]).getdata() ..asarray(dtype = uint8).reshape(-1, 3)
      color *= 6/256
      self.color = color = dot( color, self.rgbi ) # convert to rgb666
    else: self.color = color = None
    return self

  def tostr(self):
    if self.color is None: return super().tostr()
    buf = self.buf | (self.color ..asarray(dtype = uint16) << 8)
    return "\n".join( "".join(self.clrmap[x]) for x in buf.reshape(self.res) )

img2txt = _img2txtcolor()
