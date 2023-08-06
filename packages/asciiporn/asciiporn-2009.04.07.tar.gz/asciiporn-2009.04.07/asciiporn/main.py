## import asciiporn; reload(asciiporn); from asciiporn import *
from __future__ import py3k_syntax
import asciiporn, os, sys, traceback



import collections, functools, itertools, numpy; from itertools import *; from numpy import *; from . import weave
if "DEBUG" not in globals(): DEBUG = 0 ## True prints debug info
if "YRES" not in globals(): YRES = 16
def quicktest():
  try:
    img2plaintxt.test()
    img2txt.test()
  except: traceback.print_exc()
  plot3d.test()
  cosfit2nd.test()



if 1: ######## helper function
  def echo(x): return x

  @functools.wraps(builtins.enumerate)
  def enumerate(arr, i = None):
    if i: return zip(count(i), arr)
    return builtins.enumerate(arr)

  def isint(x):
    try: x & 0; return True
    except: return False

  def lens(*arr): return [len(x) for x in arr]

  def readline(fname, _ = None):
    with open(fname) as file:
      while True:
        line = file.readline()
        if not line: break
        if not _: line = line.replace("\n", "").replace("\r", "")
        yield line

  def screensize(): import re; s = system("stty -a"); row, col = re.search("rows .*?(\d*).*?columns .*?(\d*)", s).groups(); return int(row), int(col)

  def shapes(*arr): return [shape(x) for x in arr]

  def strjoin(s, _ = ""): return _.join(s)

  def system(exe): import subprocess; exe = subprocess.Popen(exe, shell = 1, stdout = subprocess.PIPE, close_fds = 1).stdout; s = exe.read(); exe.close(); return s

  def uniquestr(s, alphanum = "_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"): ## create a unique string guaranteed not to occur in s
    keyword = "qjzx" ## least common alphabets
    for i, x in enumerate(s):
      if keyword not in s: break
      keyword += alphanum[i % len(alphanum)]
    return keyword

  def walktree(tree, iterable = iterable, not_ = None, depth = -1):
    def walk(tree, depth):
      if iterable(tree) and depth:
        for x in tree:
          for y in walk(x, depth - 1): yield y
      else: yield tree
    if not_: istree = lambda x: not isleaf(x)
    return walk(tree, depth)
  flatten = walktree



# ######## class
import cProfile as profile, pstats, time
class _Profile(profile.Profile):
  super = profile.Profile

  def __call__(self, exe, lines = 64):
    self.runcall(exe)
    if lines: self.print_stats(sort = 1)
    return self

  def timing(self, exe, fasttime = time.time): t0 = fasttime(); exe(); t1 = fasttime(); return t1 - t0

  def timing2nd(self, fnc, n, dt = 2, plot = True):
    tt = collections.deque(); self.timing(lambda: fnc(0))
    T0 = time.time()
    for i in range(n):
      t = self.timing(lambda: fnc(i)); tt.append(t)
      T = time.time()
      if T - T0 > dt:
        T0 = T; print( i, t )
        if plot:
          try: asciiporn.plot(y = tt)
          except: traceback.print_exc()
    if plot:
      try: asciiporn.plot(y = tt)
      except: traceback.print_exc()
    return tt

Profile = _Profile()

import cPickle as pickle
class savestate(object): ## use when subclassing extensions to allow serialization of self.__dict__
  def __savestate__(self): state = self.__dict__.copy(); state["__self__"] = self; return state

  @staticmethod
  def __loadstate__(state): state = state.copy(); self = state["__self__"]; del state["__self__"]; self.__dict__ = state; return self

class _asarray(ndarray, savestate): ## array w/ serializable states
  def __new__(self, arr, dtype = None, order = None):
    arr = asarray(arr, dtype, order)
    try: self = ndarray.__new__(self, arr.shape, arr.dtype, arr.data)
    except AttributeError: arr = array(arr); self = ndarray.__new__(self, arr.shape, arr.dtype, arr.data)
    if arr.strides: self.strides = arr.strides
    return self



if 1: ######## math
  EPS = MachAr().eps; TINY = MachAr().tiny; HUGE = MachAr().huge
  PI2 = 2 * pi
  STD = 0.682689492137085897170465091264075844955825933453208781974788900; STD2 = 0.954499736103641585599434725666933125056447552596643132032668000
  array = numpy.array
  rng = random.random
  stdev = numpy.std
  variance = numpy.var

  def arrptr(x):
    if hasattr(x, "dtype"): x = x.dtype.type()
    return ravel(x)

  @functools.wraps(numpy.asarray)
  def asarray(arr, *args, **kwds): return numpy.asarray(tuple(arr) if hasattr(arr, "next") else arr, *args, **kwds)

  def as2d(arr, dtype = None, transpose = None, contiguous = None, nonempty = None):
    arr = asarray(arr, dtype = dtype); assert not nonempty or arr.size, (arr.shape, arr.dtype)
    if arr.size == 0: return arr.reshape(0, 0)
    arr = arr.reshape(-1, arr.shape[-1])
    if transpose: arr = arr.T
    if contiguous and not arr.flags.contiguous: arr = arr.copy()
    return arr

  def as64(x):
    if iterable(x): return asarray(x, dtype = int64)
    return int64(x)

  def bitreverse64(x):
    x = as64(x)
    x = ((x & 0xaaaaaaaaaaaaaaaa) >> 1) | ((x & 0x5555555555555555) << 1) ## stride 1
    x = ((x & 0xcccccccccccccccc) >> 2) | ((x & 0x3333333333333333) << 2) ## stride 2
    x = ((x & 0xf0f0f0f0f0f0f0f0) >> 4) | ((x & 0x0f0f0f0f0f0f0f0f) << 4) ## stride 4
    x = ((x & 0xff00ff00ff00ff00) >> 8) | ((x & 0x00ff00ff00ff00ff) << 8) ## stride 8
    x = ((x & 0xffff0000ffff0000) >> 16) | ((x & 0x0000ffff0000ffff) << 16) ## stride 16
    x = (x >> 32) | (x << 32) ## stride 32
    return x

  def bitshift64(a, b): return as64(a) << as64(b)

  def divceil(a, b): return (a + b - 1) // b

  def divround(a, b): return (a + (b >> 1)) // b

  def inline(code, **vars): weave.inline(code = code, arg_names = vars.keys(), local_dict = vars); return vars

  @functools.wraps(numpy.linspace)
  def linspace(*args, **kwds):
    yt = None
    if "yt" in kwds: yt = kwds["yt"]; kwds = kwds.copy(); del kwds["yt"]

    tt = numpy.linspace(*args, **kwds)
    if yt is None: return tt

    yy = tt.copy()
    yt = asarray(yt, dtype = float); y, t = yt.T
    if any(t[1:] < t[:-1]): yt = yt[t.argsort()] ## sort t-axis
    y, t = yt.T; yt = ystack((y[0], tt[0]), yt, (y[-1], tt[-1]))

    dyt = (yt[1:] - yt[:-1]); cll = dyt[:, 1] == 0
    if any(cll): cll ^= True; yt = yt[1:][cll]; dyt = dyt[cll]

    y, t = yt.T; dy, dt = dyt.T; df = dy / dt; tab = zip(t, y, df); t, a, b = next(tab)
    for i, x in enumerate(yy):
      if x > t: t, a, b = next(tab)
      yy[i] = a if x == t else a + b * (x - t)
    yt = transpose((yy, tt))
    return yt

  def monotonic(arr):
    if all(arr[1:] >= arr[:-1]): return 1
    elif all(arr[1:] <= arr[:-1]): return -1
    return 0

  ## efficient 64 bit population count
  def popcount64(x):
    x = x - ((x >> 1) & 0x5555555555555555) ## count 2 bits
    x = ((x >> 2) & 0x3333333333333333) + (x & 0x3333333333333333) ## count 4 bits
    x = ((x >> 4) + x) & 0x0f0f0f0f0f0f0f0f ## count 8 bits
    x += x >> 8 ## count 16 bits
    x += x >> 16 ## count 32 bits
    x += x >> 32 ## count 64 bits
    x &= 127
    return asarray(x, dtype = int) if isinstance(x, ndarray) else int(x)

  def rotate3d(x, y, z, t):
    inv = 1 / sqrt(x * x + y * y + z * z); x, y, z = x * inv, y * inv, z * inv; c = cos(t); s = sin(t); d = 1-c
    return [[x * x * d+c,     x * y * d-z * s, z * x * d+y * s],
            [x * y * d+z * s, y * y * d+c,     y * z * d-x * s],
            [z * x * d-y * s, y * z * d+x * s, z * z * d+c    ]] ..asarray()

  def roundint(x, dtype = int):
    if iterable(x): return asarray(x).round() ..asarray(dtype)
    return dtype(round(x))

  def ystack(*args): return vstack(as2d(x) for x in args)



if 1: ######## simd
  def dot2nd(arr, x):
    arr = as2d(arr, contiguous = True); x = as2d(x, contiguous = True); assert arr.dtype == x.dtype, (arr.dtype, x.dtype); out = zeros(len(arr), dtype = arr.dtype)
    if len(x) <= 1: assert arr.shape[1] == x.shape[1], shapes(arr, x); dx = 0
    else: assert arr.shape == x.shape, shapes(arr, x); dx = x.shape[1]
    code = """int i; const int Ni = Narr[0]; int j; const int Nj = Narr[1];
    for (i = 0; i < Ni; i ++, out ++, x += dx) {xptr = x;
    for (j = 0; j < Nj; j ++, arr ++, xptr ++) {*out += *arr * *xptr;}}"""; inline(
      code = code, arr = arr,
      x = x, xptr = arrptr(x), dx = dx, out = out); return out

  def fft2nd(arr): return fft.fft(as2d(arr, contiguous = True))
  def ifft2nd(arr): return fft.ifft(as2d(arr, contiguous = True))

  def find2nd(arr, x):
    arr = as2d(arr, contiguous = True); x = ravel(x); assert arr.dtype == x.dtype, (arr.dtype, x.dtype)
    n = len(arr); darr = arr.shape[1]; dx = 1
    if len(arr) == 1: n = len(x); darr = 0
    if len(x) == 1: dx = 0
    out = empty(n, dtype = int)
    code = """int i; const int Ni = Nout[0]; int j; const int Nj = Narr[1];
    for (i = 0; i < Ni; i ++, *out = j, arr += darr, x += dx, out ++) {ptr = arr;
    for (j = 0; j < Nj; j ++, ptr ++) {
    if (*ptr == *x) break;}}"""; inline(
      code = code, arr = arr, ptr = arrptr(arr), darr = darr,
      x = x, dx = dx, out = out); return arange(len(arr)), out

  def histogram2nd(arr):
    arr = as2d(arr, dtype = int, contiguous = True); n = arr.max() + 1; out = zeros((len(arr), n), int)
    assert 0 <= arr.min() <= n < 0x10000, (arr.shape, arr.dtype, arr.min(), n)
    code = """int i; const int Ni = Narr[0]; int j; const int Nj = Narr[1]; const int Nout1 = Nout[1];
    for (i = 0; i < Ni; i ++, out += Nout1) {
    for (j = 0; j < Nj; j ++, arr ++) {out[*arr] += 1;}}"""; inline(code = code, arr = arr, out = out); return out

  ## up-sample n = pwr-of-2 datapoints
  def itp2nd(arr):
    arr = as2d(arr, dtype = float); n = 1 << arr.shape[1] ..log2() ..ceil() ..int()
    if n == arr.shape[1]: return n, arr

    a, b = linspace(0, arr.shape[1] - 1, n) ..divmod(1); a = a.astype(int); out = arr[:, a]
    out[:, 1:] += b[1:] * (arr[:, 1:] - arr[:, :-1])[:, a[:-1]]
    return arr.shape[1], out

  def map2nd(f, arr, binsize, **kwds):
    bin = arange(0, len(arr), step = binsize, dtype = int); bin = r_[bin, len(arr)]; out = collections.deque()
    for i, (a, b) in zip(bin[:-1], bin[1:]) ..enumerate(): print( "map2nd %s %i %i-%i" % (f, i, a, b) ); ar = f(arr[a:b], **kwds); out.append(ar)
    return concatenate(out, axis = 0)



######## img2txt
class _img2txt(object):
  global X
  _ = ord(" ") ## convenience var for whitespace
  buf = empty(0, dtype = int64) ## internal buffer for outputting txt
  color = empty(0, dtype = int64) ## internal color buffer for outputting txt
  fres = r_[10, 6] ## row x col resolution of a character block
  mask = bitshift64(1, fres.prod()) - 1
  lucida = "AAAAAAAAAAAAQRAEARAAAIqiAAAAAAAAAEX5ylcUAACEVxwMRT0EAIBYKQylRgAAAKE4Zpt5AAAE\nQQAAAAAAADBCEARBIDAAA4EgCIIQAwAAsRkKAAAAAAAAEMRHEAAAAAAAAMAwCAEAAAAeAAAAAAAA\nAADAMAAAIAQhDCEIAQCAE0VRFDkAAIBREARBfAAAgANBCCF4AACAB0EMBDkAAADCKMmHIAAAgCcI\nDgQ5AAAAJwTNFDkAAIAHIQQhCAAAgBMlThQ5AACAE0UehBwAAAAAMAzAMAAAAAAwDMAwCAEAAEDM\nwEAAAAAAAD / wAwAAAAAEBmYEAACAJ0EIARAAAIAXdVUfeAAAAMMokieFAADAE0VPFD0AAAAnBEEg\ncAAAwBNFURQ9AACAJwiOIHgAAIAnCI4gCAAAACcEWSRxAABAFEVfFEUAAMBHEARBfAAAgIMgCIIY\nAABAlBRDkUQAAIAgCIIgeAAAQLRtV1VFAABANF1VlkUAAIATRVEUOQAAwBNFTxAEAACAE0VRFDkw\nAMCRJEeRRAAAACcIDAQ5AADARxAEQRAAAEAURVEUOQAAQBhJksIQAABAVFXVoygAAEAoMQgjhQAA\nQKQoBEEQAADAByGEEHwAABxBEARBEBwAgSAQBAJBIAAOgiAIgiAOAABBKIoSAQAAAAAAAAAAPwAE\nAgAAAAAAAAAAOBAn+QAAQRA0UxQ9AAAAAHhBEHgAABAEeVGUWQAAAAA40Rd4AAAYQXgEQRAAAAAA\neFGUWZADQRB0UxRFAAAIADgIgiAAAAgAOAiCIMgBgiBIiqFIAAAHQRAEQRAAAAAAfFVVVQAAAAB0\nUxRFAAAAADhRFDkAAAAANFMUPUEAAAB4UZRZEAQAAGiWIAgAAAAAcAIDOQAAAEF4BEFgAAAAAERR\nlF0AAAAARIqiEAAAAACUbStJAAAAAEQKoUQAAAAAhJLEMMQAAAB8CCF8AAAcQRACQRAcAARBEARB\nEAQADoIgEIIgDgAAAABnDgAAAAAAAAAAAAAA\n" ## lucida console 06x10 bitmap font encoded in 64 bits - use str2font to decode

  ## pre-defined colors
  bwrgbcmy = "0x000000 0xFFFFFF 0xFF0000 0x00FF00 0x0000FF 0x00A8EC 0xE3007B 0xF9F400"; bwrgbcmy = ( eval(x) for x in bwrgbcmy.split(" ") ) ..asarray()
  rgbi = (36, 6, 1) ..asarray(dtype = uint8) ## set color channels to 8bit - numpy defaults to 64 bits, wasting space by order of magnitude
  x = arange(0, 256, 51); rgb666 = zeros((6, 6, 6, 3), dtype = uint8); rgb666[..., 0] |= x[:, newaxis, newaxis]; rgb666[..., 1] |= x[:, newaxis]; rgb666[..., 2] |= x; rgb666 = ravel(rgb666)

  ## color map
  clrmap = "  ".join( "\33[38;5;foom%c\33[0m" % x for x in range(128) ); clrmap += "  " + clrmap.replace("foo", "foo;7")
  i = range(16, 232); X = clrmap; clrmap = "  ".join( X.replace("foo", str(x)) for x in i ).split("  ") ..ravel() ## rgb666
  rgb = clrmap[ord(" ") + 128::256] ..asarray()

  if 0 and DEBUG:
    print( clrmap[256:768] ..strjoin() )
    print( "".join(rgb) )

  ## print an array in row, col format - for debugging
  def printd(self, arr):
    if isinstance(arr, int64): arr = [arr & bitshift64(1, i) for i in range(self.fres.prod())] ..asarray(dtype = bool).reshape(self.fres)
    for x in arr[:-1]: print( "".join(str(int(x)) if x else "." for x in x) )
    print( "".join(str(int(x)) if x else "_" for x in arr[-1]) )

  ## internal fnc for importing font bitmaps
  def importfont(self, file):
    DEBUG = self.DEBUG; from PIL import Image; fres = self.fres
    font = Image.open(file).getdata() ..asarray(dtype = int64)
    if 0 and DEBUG: font = font.reshape(fres * (6, 16)); self.printd(font[:fres[0]])

    font = font.reshape(6, fres[0], 16, fres[1]).transpose(0, 2, 1, 3) .reshape(r_[6 * 16, fres.prod()])
    for i, x in enumerate(font.T): font[:, 0] |= bitshift64(x, i)
    font = font[:, 0]
    if 0 and DEBUG:
      for x in font[1:1 + 2]: self.printd(x); print()
    return font

  def font2str(self, font): import base64; return base64.encodestring(font.tostring())
  def str2font(self, s): import base64; s = base64.decodestring(s); return ndarray(len(s) // 8, dtype = int64, buffer = s)

  def __init__(self, plaintxt = True):
    self.plaintxt = plaintxt; fres = self.fres

    arr = self.str2font(self.lucida); arr = arr[..., newaxis].repeat(5, axis = -1) ## original
    arr[..., 1] >>= fres[1] ## shift up
    arr[..., 2] <<= fres[1] ## shift down
    cll = 1 ..bitshift64(arange(0, fres.prod(), fres[1], dtype = int64)) ..sum() ^ self.mask ## cll left boundary
    x = arr[..., 3]; x &= cll; x >>= 1 ## shift left
    x = arr[..., 4]; x <<= 1; x &= cll ## shift right
    if 0 and DEBUG:
      for x in arr[17, :5]: self.printd(x)

    fbmp0 = zeros(128, arr.dtype); fbmp0[-len(arr):] = arr[:, 0]; fbmp0 = [fbmp0 & bitshift64(1, i) for i in range(self.fres.prod())] ..asarray(dtype = bool).T.copy()
    fbmp = arr ## bmp of font
    ford = arange(32, 128); assert len(ford) == len(fbmp) ## maps fbmp -> ord
    fpop = popcount64(fbmp[:, 0])

    if not plaintxt: ## include inverted color
      fbmp = (fbmp, fbmp ^ self.mask) ..concatenate(axis = 0)
      ford = r_[ford, ford + 128]; fpop = r_[fpop, fres.prod() - fpop]
      fpop[-1] = 0 ## redundant fres.prod()

    cll = [0] + [i for i, x in enumerate(fpop) if x] ## cll whitespace
    fbmp, ford, fpop = (x[cll] for x in (fbmp, ford, fpop))

    cll = fpop.argsort() ## sort by population count
    fbmp, ford, fpop = (x[cll] for x in (fbmp, ford, fpop))
    self.level = level = fpop.mean() * 255 / fres.prod()

    hst = histogram2nd(fpop)[0]
    hst = [list(x) for x in enumerate(hst) if x[1]] ..array() ## cll whitespace in histogram

    bin = [0]; i = n = 0
    for a, b in hst[1:]:
      if n < 16: n += b ## binsize
      else: bin.append(a); n = b
    bin = asarray( [0] + bin[:-1] + [fres.prod() + 1] * 2 )
    a = zip(bin[0::3], bin[3::3])
    b = zip(bin[1::3], bin[4::3])
    c = zip(bin[2::3], bin[5::3])

    fbin = transpose((bin[1:-2], bin[2:-1])); fbin[0, 0] = 1 ## ignore whitespace
    fmap = zip_longest(a, b, c) ..flatten() ..tuple()
    if None in fmap: fmap = fmap[:fmap.index(None)]
    fmap = fmap ..reshape((-1, 2))
    fmap = find2nd(fpop, fmap.T.ravel())[1].reshape(2, -1).T
    assert len(fmap) == len(fbin)

    if 0 and DEBUG:
      print( "level", level )
      print( "fpop", fpop )
      print( "hst", hst )
      print( "fbin", fbin )
      print( "fmap", fmap )

    fmap = [(a, fbmp[a:b]) for a, b in fmap]
    chrmap = [chr(x) for x in range(128)] ## chrmap
    if not plaintxt: chrmap += ["\33[7m%s\33[0m" % x for x in chrmap] ## include inverted color
    self.chrmap = chrmap = asarray(chrmap)
    if 0 and DEBUG: print( chrmap[ford] ..strjoin() ) ## print chrmap in ascending density

    self.fbmp0 = fbmp0; self.fbmp = fbmp; self.ford = ford; self.fpop = fpop; self.fbin = fbin; self.fmap = fmap

  ## fill buf w/ data
  def fill(self, arr):
    fres = self.fres; self.res = res = divceil(arr.shape, fres) ## res
    if not all(arr.shape // fres == res): x = arr; arr = zeros(res * fres, dtype = bool); arr[:x.shape[0], :x.shape[1]] = x ## resize canvas
    if len(self.buf) != res.prod(): self.buf = empty(res.prod(), dtype = int64) ## resize buf
    buf = self.buf; buf.fill(0) ## clear buf
    arr = asarray(arr, dtype = bool) .reshape(res[0], fres[0], res[1], fres[1]) .transpose(1, 3, 0, 2) .reshape(fres.prod(), -1) ## create blocks
    for i, x in enumerate(arr != 0): buf |= bitshift64(x, i) ## fill buf
    return self

  ## draw algorithm - interpolates block -> ascii chr
  def itp(self, wmatch = 1, wmismatch = 2, whitespace = True):
    buf = self.buf; self.pop = pop = popcount64(buf)
    for (a, b), (c, f) in zip(self.fbin, self.fmap):
      cll = (a <= pop) & (pop < b)
      if not cll.any(): continue
      x = buf[cll]; f = f.T[..., newaxis]
      y = popcount64(x & f) ## match
      y[0] *= wmatch ## weight original match
      y[0] -= popcount64(x ^ f[0]) * wmismatch ## subtract mismatch
      y = y.sum(axis = 0); y = y.argsort(axis = 0)[-1] + c; ## tally weights & pick highest
      if not whitespace: y[y == 0] = 1
      buf[cll] = self.ford[y]
    buf[buf == 0] = self._; return self

  ## itp -> txt
  def tostr(self):
    if self.plaintxt or self.color is None: return "\n".join( "".join(self.chrmap[x]) for x in self.buf.reshape(self.res) )
    buf = self.buf | (self.color ..asarray(dtype = uint16) << 8)
    return "\n".join( "".join(self.clrmap[x]) for x in buf.reshape(self.res) )

  # ## autofill s to self.res
  # def str2arr(self, s, gray = 172):
    # res = self.res; lines = []
    # for s in s.split("\n"):
      # if not s: lines.append("")
      # else:
        # while s: lines.append(s[:res[1]]); s = s[res[1]:]

    # buf = empty((len(lines), res[1]), self.buf.dtype); buf.fill(self._); color = empty(buf.shape, self.color.dtype); color.fill(gray)
    # for s, b, c in zip(lines, buf, color):
      # if "\x00" in s: ## color txt - white a - "\x00\xd7a"
        # s = s.split("\x00"); clr = [ord(x[0]) for x in s[1:]]; s[1:] = [x[1:] for x in s[1:]]; clri = cumsum(lens(*s[:-1])); c[clri] = clr; s = "".join(s)
      # b[:len(s)] = [ord(x) for x in s]

    # return ravel(buf), ravel(color)

  ## autofill s to self.res
  def str2arr(self, s, gray = 172):
    res = self.res; lines = []
    for s in s.replace("\x00\n", "\x00\xff").split("\n"):
      if not s: lines.append("")
      else:
        s = s.replace("\xff", "\n")
        while s: lines.append(s[:res[1]]); s = s[res[1]:]

    buf = empty((len(lines), res[1]), self.buf.dtype); buf.fill(self._); color = empty(buf.shape, self.color.dtype); color.fill(gray)
    for s, b, c in zip(lines, buf, color):
      if "\x00" in s: ## color txt - white a - "\x00\xd7a"
        s = s.split("\x00"); clr = [ord(x[0]) for x in s[1:]]; s[1:] = [x[1:] for x in s[1:]]; clri = cumsum(lens(*s[:-1])); c[clri] = clr; s = "".join(s)
      b[:len(s)] = [ord(x) for x in s]

    # print( buf.shape, self.res )
    # print( repr(buf.tostring()) )
    return ravel(buf), ravel(color)

  def header(self, s): res = self.res; buf, color = self.str2arr(s); self.buf = buf = concatenate((buf, self.buf)); self.color = color = concatenate((color, self.color)); self.res = res = r_[len(buf) // res[1], res[1]]; return self
  def footer(self, s): res = self.res; buf, color = self.str2arr(s); self.buf = buf = concatenate((self.buf, buf)); self.color = color = concatenate((self.color, color)); self.res = res = r_[len(buf) // res[1], res[1]]; return self

  ## itp -> gif
  def togif(self, fname):
    fres = self.fres; res = self.res
    front = self.color.copy(); back = zeros(len(front), front.dtype) ## foreground / background
    cll = self.buf > 127; back[cll] = front[cll]; front[cll] = 0 ## invert foreground / background
    buf = self.fbmp0[self.buf & 127] ## draw
    buf = (buf * front[:, newaxis]) | ((buf ^ True) * back[:, newaxis]) ## paint
    buf = buf.reshape(res[0], res[1], fres[0], fres[1]).transpose(0, 2, 1, 3) ## rearrange blocks
    assert buf.dtype == uint8; buf = buf.tostring()
    from PIL import Image; img = Image.fromstring("P", (res * fres)[::-1], buf); img.putpalette(self.rgb666); img.save(fname)

  ## img -> itp
  def load(self, file, scale = 1, invert = None, **kwds): ## must be a file or filename
    from PIL import Image; img = Image.open(file) ## import img
    fres = self.fres[::-1]; res = asarray(img.size) * scale / fres; res = ceil(res).astype(int) * fres ## make res multiple of fres
    if not all(res == img.size): img = img.resize(res) ## resize img

    gray = img.convert("L"); arr = gray.getdata() ..asarray(dtype = uint8) ## auto-level
    if invert: arr ^= -1
    x = arr.mean(); level = self.level
    if x and x != level:
      cll = arr <= x; x = arr[cll]; x -= x.min(); x *= level / (x.max() or 1); arr[cll] = x ## <= mean
      cll = cll ^ True; x = arr[cll]; x -= x.min(); x *= (255 - level) / (x.max() or 1); x += level; arr[cll] = x ## > mean
      gray.putdata(arr)
    arr = gray.convert("1").getdata() ..asarray(dtype = bool).reshape(res[::-1]) ## dither

    self.res = res[::-1] // fres[::-1] ## save res
    self.fill(arr).itp(**kwds) ## itp

    if not self.plaintxt and img.mode in ("CYMK", "P", "RGB"):
      color = (img if img.mode == "RGB" else img.convert("RGB")).resize(self.res[::-1]).getdata() ..asarray(dtype = uint8).reshape(-1, 3)
      if invert: color ^= -1
      color *= 6 / 256
      self.color = color = dot( color, self.rgbi ) ## convert to rgb666
      color[(color == 0) & (self.buf != self._)] = 1 ## paint darkest non-empty pixel blud instead of invisible black
    else: self.color = color = None
    return self

  def __call__(self, *args, **kwds): return self.load(*args, **kwds).tostr()

  def test(self):
    img = imp.find_module("asciiporn")[1] + "/" + "mario.gif"
    txt = self(
      img,
      scale = 1.0, ## scale image size (0.5 = half, 1 = original, 2 = double)
      invert = 0, ## invert colors
      whitespace = True, ## True for optimal algorithm, False to deny a non-empty block from being written as whitespace (e.g. u want to see every datapoint in a plot)
      )
    print( txt )
    # htm = self.tohtm( txt ); open("index_html/a00.html", "w").write(htm)

img2plaintxt = _img2txt(plaintxt = True) ## creates portable plain txt image
img2txt = _img2txt(plaintxt = None) ## creates colorized txt image for display in terminals (xterm, putty, ...)



######## (z, y, t) datapoint storage object
class dataZYT(_asarray):
  def __new__(self, yt = None, z = None, y = None, t = None, zmin = None, zmax = None, ymin = None, ymax = None, tmin = None, tmax = None, zn = 64, yn = 64, tn = 64, ft = None, ftz = None):
    yt = [] if yt is None else [yt] if not ndim(yt[0]) else list(yt)
    y = [] if y is None else [y] if not ndim(y[0]) else list(y)
    if not (y is None and ft is None) and t is None:
      if y: tn = len(y[0])
      t = linspace(0 if tmin is None else tmin, tn - 1 if tmax is None else tmax, tn)

    if ft is not None:
      if not iterable(ft): ft = [ft]
      y += [[ft(_t) for _t in t] for ft in ft]
    if ftz is not None:
      if z is None: z = linspace(0 if zmin is None else zmin, zn - 1 if zmax is None else zmax, zn)
      y += [[ftz(_t, _z) for _t in t] for _z in z]

    if y: yt += [transpose((x, t)) for x in as2d(y)]
    try:
      yt = array(yt, dtype = float) ## copy yt
      yt = yt.reshape(r_[1, -1, yt.shape[-2:]][-3:])
    except:
      yt = [as2d(x) for x in yt]; n = max(len(x) for x in yt)
      for i, x in enumerate(yt):
        if len(x) < n: yt[i] = x[newaxis].repeat(divceil(n, len(x)), 0).reshape(-1, 2)[:n]
      yt = asarray(yt)

    self = _asarray.__new__(self, yt, dtype = float)
    if not None is ymin is ymax is tmin is tmax:
      y, t = self.reshape(-1, 2).T
      if tmin is not None: cll = t < tmin; y0 = y[cll ^ True][0]; y[cll] = y0; t[cll] = tmin
      if tmax is not None: cll = t > tmax; y0 = y[cll ^ True][-1]; y[cll] = y0; t[cll] = tmax
      if ymin is not None: y[y < ymin] = ymin
      if ymax is not None: y[y > ymax] = ymax
    self.z = z = arange(len(self)) if z is None else asarray(z, dtype = float)
    return self

  def roots(self):
    if not self.minmax[0, 0] <= 0 <= self.minmax[1, 0]: return []
    assert self.sorted; roots = []
    for i, yt in enumerate(self):
      y, t = yt.T; sgn = sign(y); cll = (sgn[:-1] != sgn[1:]) & (t[:-1] != t[1:]); root = t[cll] ## roots
      x = (sgn[:-1] + sgn[1:]) == 0; a = cll & x; b = x[cll] ## itp crossover
      dyt = (yt[1:]- yt[:-1])[a]; inv = -dyt[:, 1] / dyt[:, 0]; root[b] = t[a] + y[a] * inv
      roots.append(root)
    return roots

  def analyze(self):
    self.minmax = minmax = [(x.min(), x.max()) for x in self.T] ..transpose() ## self.minmax
    if any(minmax[0] == minmax[1]):
      if minmax[0, 1] == minmax[1, 1]: raise ValueError("datapoints all lie on vertical line t = %s" % minmax[0, 1])
      else: raise ValueError("datapoints all lie on horizontal line y = %s" % minmax[0, 0])
    self.origin = origin = [0.0 if a <= 0 <= b else a if 0 < a else b for a, b in minmax.T] ..asarray() ## self.origin

    for yt in self:
      t = yt[:, 1]
      if any(t[:-1] > t[1:]): yt[:] = yt[t.argsort()] ## sort t-axis
    self.sorted = True
    arr = []; y = self[..., 0] ## self.extrema
    for ye in y.min(axis = 1), y.max(axis = 1): cll = find2nd(y, ye); te = self[cll[0], cll[1], 1]; arr.append((ye, te))
    self.extrema = extrema = transpose(arr, (2, 0, 1)); return self

  def concat(self, x): return (self, x) ..concatenate(axis = 0) ..dataZYT()

  def norm(self, arr = None): ## normalize data points
    a, b = self.minmax; assert not any(a == b)
    if arr is None: arr = self
    arr = asarray(arr); arr = arr.reshape(r_[1, 1, arr.shape][-3:]).astype(float); arr -= a; arr *= 1 / (b - a) ## norm
    n = linspace(0, 1, len(arr)); n = n[newaxis, :].repeat(arr.shape[1], axis = -1).reshape(r_[arr.shape[:-1], 1])
    arr = concatenate((n, arr), axis = -1)
    return arr



######## general plotter
class _plot(_img2txt):
  def s2rgb(s, rgb): return [(int(a), int(b), int(c)) for a,b,c in s] ..dot(rgb) ## convert array of string triplets -> rgb666
  def printrgb(rgbi = None): print( len(rgbi), "".join(img2txt.rgb[rgbi]) )

  rgb = img2txt.rgb; rgbi = img2txt.rgbi
  monoi = """
000
001 002 003 004 005
015 025 035 045 045
055 155 255 355 455
555
""".replace("\n", " ").split(" ")[1:-1]
  bluei = s2rgb(monoi, (36, 6, 1))
  greeni = s2rgb(monoi, (1, 36, 6))
  redi = s2rgb(monoi, (6, 1, 36))
  gradienti = """
000
001 010 100 011 101 110 111
112 121 211 122 212 221 222
223 232 322 233 323 332 333
334 343 433 344 434 443 444
445 454 544 455 545 554 555
""".replace("\n", " ").split(" ")[1:-1] ..s2rgb((6, 36, 1))
  rainbowi = """
000
001 002 003 004 005
015 025 035 045 055
054 053 052 051 050
150 250 350 450 550
540 530 520 510 500
501 502 503 504 505
515 525 535 545 555
""".replace("\n", " ").split(" ")[1:-1] ..s2rgb((1, 6, 36))
  blueredi = """
000
001 002 003 004 005
015 025 035 045 055
155 255 355 455 555
554 553 552 551 550
540 530 520 510 500
400 300 200 100 000
""".replace("\n", " ").split(" ")[1:-1] ..s2rgb((36, 6, 1))

  if 0 and DEBUG:
    printrgb(arange(216))
    printrgb(greeni)
    printrgb(gradienti)
    printrgb(rainbowi)

  block = 160 ## plot solid block
  colori0 = gradienti[1:] ## plot color
  boxi = 1 * 36 + 1 * 6 + 1 ## box color
  gridi = 2 ## grid color
  rooti = 5 * 36 ## root color
  vlinei = 5 * 36 + 5 * 6 ## vertical line color
  s2rgb = staticmethod(s2rgb)
  printrgb = staticmethod(printrgb)

  def __call__(self, replot = None, itp = True, yres = None, xres = None, vline = None, **kwds):
    if replot: data = self.data; norm = self.norm
    else: self.data = data = dataZYT(**kwds).analyze(); self.norm = norm = data.norm()

    if yres is None: yres = YRES
    self.res = res = screensize() ..asarray(); res[0] *= yres ## res
    if isint(yres): res[0] = yres
    if isint(xres): res[1] = xres
    if len(self.buf) != res.prod(): self.buf = empty(res.prod(), dtype = int64) ## resize buf
    if len(self.color) != res.prod(): self.color = empty(res.prod(), dtype = int64) ## resize color buf
    buf = self.buf; color = self.color; buf[:] = color[:] = 0 ## reset buf
    self.vline = vline
    # s = self.plot().tostr(); s = self.header() + "\n" + s
    # print( s )
    s = self.plot().header().tostr(); print( s )

  def inverty(self, arr): arr = arr.copy(); arr[..., 1] = 1 - arr[..., 1]; return arr
  def scaleyt(self, yt, inverty, res = None):
    yt = self.data.norm(yt).reshape(-1, 3)[:, 1:]
    if inverty: yt[:, 0] = 1 - yt[:, 0]
    yt = asarray( yt * ((res if res else self.res) - 1), dtype = int ); return yt

  ## plot algorithm
  def plot(self):
    buf = self.buf; color = self.color; data = self.data; fres = self.fres; res = self.res
    self.colori = colori = self.colori0[linspace(0, len(self.colori0) - 1, len(data) + 1)[1:].astype(int)] ## colori

    ## connect the dots w/ lines
    arr = self.inverty(self.norm.reshape(-1, 3))
    arr = reshape( arr[:, 1:] * (res * fres - 1), (len(data), -1, 2) ).round()
    for i, yt in enumerate(arr):
      if len(yt) == 0: continue
      if len(yt) == 1: yt = yt.astype(int)
      else: y, t = yt.T; yt = linspace(t[0], t[-1], t[-1] - t[0] + 1, yt = yt).astype(int)
      a, b = divmod(yt, fres); y, t = a.T; a = a[:, 0] * res[1] + a[:, 1]; b = bitshift64(1, b[:, 0] * fres[1] + b[:, 1])
      color[a] = colori[i]
      if len(a) == 1: b[:] = self.mask
      inline("int i; const int Ni = Na[0]; for (i = 0; i < Ni; buf[*a] |= *b, i ++, a ++, b ++);", buf = buf, a = a, b = b)
    self.itp(wmatch = 2, wmismatch = 1, whitespace = True) ## itp

    o = self.scaleyt(data.origin, inverty = True).ravel(); o = asarray((o, res - 1)).min(axis = 0) ## origin
    cll = arange(0, len(buf), res[1]) + o[1]; cll = cll[buf[cll] == self._]; buf[cll] = ord("|"); color[cll] = self.rooti ## y axis
    cll = arange(res[1]) + o[0] * res[1]; cll = cll[buf[cll] == self._]; buf[cll] = ord("-"); color[cll] = self.rooti ## t axis
    cll = arange(res[1]); cll = r_[cll, -1 - cll]; cll = cll[ buf[cll] == self._ ]; buf[cll] = ord("-"); color[cll] = self.boxi ## box
    a, b = arr = data.extrema[:, :, 0].T; x, i = find2nd(arr, (a.min(), b.max())); self.mmci = mmci = colori[i] ## extrema
    y, t = self.scaleyt( data.extrema[i, [0, 1]], inverty = True ).T; x = t + o[0] * res[1]; buf[x] = self.block; color[x] = mmci

    if self.vline is not None:
      vline = self.vline; yt = transpose((zeros(len(vline)), vline)); t = self.scaleyt(yt, inverty = True)[:, 1] ..roundint()
      for t in t: cll = arange(0, len(buf), res[1]) + t; cll = cll[buf[cll] == self._]; buf[cll] = ord("|"); color[cll] = self.vlinei

    cll = linspace(0, res[1] - 1, 5)[1:-1] ..roundint()[:, newaxis] + arange(0, len(buf), res[1]); cll = cll.ravel(); cll = cll[buf[cll] == self._]; buf[cll] = ord("|"); color[cll] = self.gridi ## t grid
    cll = linspace(0, res[0] - 1, 5)[1:-1] ..roundint()[:, newaxis] * res[1] + arange(res[1]); cll = cll.ravel(); cll = cll[buf[cll] == self._]; buf[cll] = ord("-"); color[cll] = self.gridi ## y grid

    return self

  ## print header info
  def header(self):
    data = self.data; mm = data.minmax; s = "SIDEVIEW Y:    Z %s to %s %s    Y %s to %s    T %s to %s    MIN MAX %s" % (
      data.z[0], data.z[-1],
      "".join("\x00%c\xa0" % x for x in self.colori),
      mm[0, 0], mm[1, 0],
      mm[0, 1], mm[1, 1],
      " ".join("\x00%c\xa0" % x for x in self.mmci),
      ); _img2txt.header(self, s); return self

  def test(self, plot = None):
    if plot: self = plot
    if 1:
      t = linspace(0, 1, 64) - 0.25
      y = [ t, cos(2 * pi * t), sin(t * 4 * pi), cos(2 * pi * t) + 0.25 ]
      yt = None
      self(yt = yt, y = y, t = t, vline = [0.5])
    if 1:
      tmin, tmax = -1, 1
      zmin, zmax = 0, 1
      ftz = lambda t, z: sin( t*(2*pi + z) ) * (0.5 + z) - z
      self(ftz = ftz, zmin = zmin, zmax = zmax, tmin = tmin, tmax = tmax)



######## surface plotter
class _plotsurf(_plot):
  def plot(self, **kwds):
    res = self.res; buf = self.buf.reshape(res); color = self.color.reshape(res); data = self.data; arr = self.norm.reshape(-1, 3)

    yt = reshape( arr[:, 1:], (len(data), -1, 2) ); y, t = yt.T; t[:] = (t * res[1] - 1).round()
    z = linspace(0, res[0], len(yt) + 1).astype(int); z0 = -1

    for z, yt, t0 in zip_longest(z, yt, data.roots()):
      if z != z0:
        if z > z0 + 1: buf[z0 + 1:z] = buf[z0]; color[z0 + 1:z] = color[z0]
        if z == res[0]: break
        y, t = yt.T
        yt = linspace(t[0], t[-1], t[-1] - t[0] + 1, yt = yt)
        y, t = yt.T; t = t.astype(int)
        buf[z, t] = self.ford[roundint( y * (len(self.ford) - 1) )]
        color[z, t] = self.colori0[roundint( y * (len(self.colori0) - 1) )]
        if t0 is not None: t0 = self.scaleyt(transpose((t0, t0)), inverty = None)[:, 1]; buf[z, t0] = self.block; color[z, t0] = self.rooti ## plot y roots
      z0 = z
    return self

  def header(self):
    data = self.data; mm = data.minmax; s = "TOPVIEW Z:    Z %s to %s (top to bottom)    Y %s to %s %s    T %s to %s    ROOTS %s" % (
      data.z[0], data.z[-1],
      mm[0, 0], mm[1, 0],
      "".join("\x00%c\xa0" % x for x in self.colori0),
      mm[0, 1], mm[1, 1],
      "\x00%c\xa0" % self.rooti,
      ); _img2txt.header(self, s); return self

plot = _plot(plaintxt = None)
plotsurf = _plotsurf(plaintxt = None)
def plot3d(**kwds):
  plot(**kwds)
  plotsurf.data = plot.data; plotsurf.norm = plot.norm; plotsurf(**kwds)
plot3d.test = lambda: plot.test(plot = plot3d)



######## simd polynomial fitter
class polyfit2nd(_asarray):
  def __new__(self, y = None, t = None, nth = None, wgt = None, cff = None):
    if cff is not None: return _asarray.__new__(self, cff)

    if wgt is not None: wgt = asarray(wgt, dtype = float)

    if nth == 0: ## nth == 0 optimization
      if wgt is None: cff = as2d(y).mean(axis = 1)[:, newaxis]
      else: cff = 1 / sum(wgt) * dot2nd(y, wgt)[:, newaxis]
      return _asarray.__new__(self, cff)

    elif nth == 1: ## nth == 1 optimization
      y = as2d(y); N = y.shape[1]
      if t is None: t = arange(N, dtype = float)
      if wgt is None:
        Y = y.sum(axis = 1); T = t.sum(); T2 = dot(t, t); YT = dot2nd(y, t)
        inv = 1 / (N * T2 - T * T); a = T2 * Y - T * YT; b = -T * Y + N * YT
      else:
        W2 = dot(wgt, wgt); WY = dot2nd(y, wgt)
        wt = wgt * t; W2T = dot(wt, t); W2T2 = dot(wt, wt); WYT = dot2nd(y, wt)
        inv = 1 / (W2 * W2T2 - W2T * W2T); a = W2T2 * WY - W2T * WYT; b = -W2T * WY + W2 * WYT
      cff = inv * transpose((a, b)); return _asarray.__new__(self, cff)

    y = as2d(y, transpose = True, nonempty = True)
    if t is None: t = arange(len(y), dtype = float)
    t = t[:, newaxis] ** arange(nth + 1)[newaxis]

    if wgt is None: cff, res, rank, sing = linalg.lstsq(t, y) ## find least squares
    else: cff, res, rank, sing = linalg.lstsq((wgt * t).T, (wgt * y).T) ## apply wgt 1st
    self = _asarray.__new__(self, cff.T); return self

  def itp(self, t): return dot(self, t[newaxis] ** arange(self.shape[1])[:, newaxis])

  @staticmethod
  def test():
    n = 256; t = r_[0:1:1j*n]; w, phi = 1.2 * 2 * pi, 0.1 * 2 * pi
    y = sin(w * t + phi); y = array((y, y + 0.25))
    f = polyfit2nd(y = y, t = t, nth = 4); z = f.itp(t); plot(y = [y, z], t = t)



######## simd pwr-of-2 fft utilities
class fft2(_asarray):
  def __new__(self, y, dtype = complex):
    y = as2d(asarray(y, dtype = dtype), contiguous = True, nonempty = True)
    n = y.shape[1]; ln = int(log2(n)); assert 1 << ln == n, (y.shape, y.dtype)
    self = _asarray.__new__(self, y); self.n = n; self.ln = ln; self.n2 = n >> 1; return self

  def abs(self): return abs(self)

  def dot(self, w):
    arr = asarray(self); w = ravel(w); assert w.dtype == arr.dtype, (arr.dtype, w.dtype)
    out = zeros((len(arr), len(w)), dtype = arr.dtype); wx = arrptr(arr); arrx = wx.copy(); arry = wx.copy(); outx = wx.copy(); weave.inline("""
    int i; const int Ni = Narr[0]; int j; const int Nj = Narr[1]; int k; const int Nk = Nw[0];
    for (k = 0; k < Nk; k ++, w ++, out ++){
    for (j = 0, arrx = arr, *wx = *w; j < Nj; j ++, arrx ++, *wx *= *w){
    for (i = 0, arry = arrx, outx = out; i < Ni; *outx += *arry * *wx, i ++, arry += Nj, outx += Nk);
    }}""", ("arr", "w", "out", "wx", "arrx", "arry", "outx")); return out

  ## inplace bitreverse sort
  def sort(self):
    arr = asarray(self); ptr = arrptr(arr); x = ptr.copy(); weave.inline("""
    int i; const int Ni = Narr[0]; int j; const int Nj = Narr[1]; const int n2 = Narr[1] >> 1;

    int pos, step; pos = 0; arr ++;
    for (j = 1; j < Nj - 1; j ++, arr ++){
    step = n2; while(pos >= step) {pos -= step; step >>= 1;} pos += step; step = pos - j;

    if(step > 0) {
    for (i = 0, ptr = arr; i < Ni; i ++, ptr += Nj) {
    *x = *ptr; *ptr = ptr[step]; ptr[step] = *x;
    }}}""", ("arr", "ptr", "x")); return self

  ## decimation in frequency algorithm
  def dif(self, w = None):
    arr = asarray(self); n = arr.shape[1]; w = exp(-2j * pi / n) ** arange(n) if w is None else w.copy()
    wptr = arrptr(arr); x = wptr.copy(); e = x.copy(); o = x.copy(); weave.inline("""
    int i; const int Ni = Narr[0]; int j; const int Nj = Narr[1]; int step, step2, wi;

    for (step = Nj; step > 1; step >>= 1) { step2 = step >> 1; // ln loop
    for (wi = 0, wptr = w; wi < step2; *wptr *= *wptr, wi ++, wptr ++){ // butterfly loop
    for (j = wi; j < Nj; j += step) { // partition loop
    for (i = 0, e = arr + j, o = e + step2; i < Ni; i ++, e += Nj, o += Nj) { // simd loop

    *x = *e; *e += *o; *o -= *x; *o *= -*wptr; // butterfly
    }}}}""", ("arr", "w", "wptr", "e", "o", "x")); return self

  ## yield fractional dft
  def _dtft(self):
    n, ln, n2 = self.n, self.ln, self.n2; nn = arange(n); N = n * n >> 1
    if n == 1: yield self, zeros(1); return
    w0 = exp(-2j * pi / N) ** arange(n)
    frq0 = arange(n2) ..fft2(dtype = float).sort().ravel()

    self.fft = fft = fft2(self.copy()).dif(); y = fft[:, 1:2]; frq = r_[n2 + 0.0]; yield y, frq; y = fft[:, ::2]; frq = frq0; yield y, frq
    for lfrac, frac in enumerate(1 << arange(1, ln), 1):

      if ln * frac < n: ## fft only if more efficient
        winv = 1 << ln - lfrac - 1; lvl = arange(lfrac - 1)
        wbit = arange(1 << lfrac - 1)[:, newaxis] & (1 << lvl[::-1]); wbit = 1 + dot(wbit.astype(bool), 1 << lvl + 1); wbit *= winv
        frq = 1 / frac + frq0 * (2 / frac); frq = frq.reshape(len(wbit), -1)
        for wbit, frq in zip(wbit, frq): y = fft2(self * w0 ** wbit).dif()[:, ::frac]; yield y, frq

      else: ## else dot product
        if 0: print( ln * frac >> 1, frac >> 1, n >> 1 )
        wbit = n >> lfrac; w = w0[wbit >> 1] * w0[:n2] ** wbit; y = self.dot(w) ## O(n) memory efficiency
        frq = 1 / frac + nn[:n2] * (2 / frac); yield y, frq

  @staticmethod
  def _fmax(ymax, fmax, y, frq):
    y = as2d(y, contiguous = True); x = zeros(1, dtype = float); weave.inline("""
    int i; const int Ni = Ny[0]; int j; const int Nj = Ny[1];
    for (i = 0; i < Ni; i ++, ymax ++, fmax ++) {
    for (j = 0, *x = abs(*ymax); j < Nj; j ++, y ++) {
    if (abs(*y) > *x) {*x = abs(*y); *ymax = *y; *fmax = frq[j];}
    }}""", ("ymax", "fmax", "y", "frq", "x")); return ymax, fmax

  def fmax(self, y = None, frq = None):
    ymax = zeros(len(self), dtype = self.dtype); fmax = ymax.astype(float)
    if y is None:
      for y, frq in self._dtft(): self._fmax(ymax, fmax, y, frq)
    else: self._fmax(ymax, fmax, y, frq)
    return ymax, fmax

  ## deduce histogram sort order from frq
  def _frqi(self, frq):
    x = floor(log2(frq)); x[x < 0] = -inf; a = (x + 1) * self.n2; a[a == -inf] = 0
    x = 2 ** x; b = frq - x; x *= 2; x[x == 0] = 2; b *= self.n / x
    frqi = asarray(a + b, dtype = int); return frqi

  def histogram(self):
    yy = empty((len(self), self.ln * self.n2 + 1), dtype = complex); ff = empty(yy.shape[1])
    for y, frq in self._dtft(): frqi = self._frqi(frq); yy[:, frqi] = y; ff[frqi] = frq
    assert all( ff.argsort() == arange(len(ff)) ); return yy, ff

  @staticmethod
  def test():
    n = 32
    frq = 1.90; phi = -2.3; t = linspace(0, 2 * pi, n); y0 = cos(frq * t + phi)
    y0 = [y0 + rng(n) - 0.5]
    y0 += [rng(n) - 0.5]
    plot(y = y0, t = t)
    y = fft2(y0); yy, tt = y.histogram(); plot(y = abs(yy), t = tt)



######## simd cosine fitter
class cosfit2nd(_asarray):
  def __new__(self, y = None, cff = None, histogram = None):
    if cff is not None: return _asarray.__new__(self, cff)
    n0, y = y ..array() ..itp2nd(); n = y.shape[1] ## up-sample pwr-of-2
    y1 = polyfit2nd(y, nth = 1); y -= y1.itp(arange(y.shape[1])); y1[:, 1] *= n / n0 ## linear regression baseline

    y = fft2(y)
    if histogram: yh, fh = histogram = y.histogram(); ymax, fmax = y.fmax(yh, fh); fh *= n0 / n
    else: ymax, fmax = y.fmax()

    amp = 2 / n * abs(ymax); frq = 1 / n0 * fmax; t0 = -1 / (2 * pi) / frq * log(ymax).imag; t0[amp == 0] = 0 ## amp, frq, t0
    self = _asarray.__new__(self, transpose((y1[:, 0], y1[:, 1], amp, frq, t0)))
    if histogram: self.histogram = histogram
    return self

  def itp(self, t): y0, y1, amp, frq, t0 = self.T[..., newaxis]; return y0 + y1 * t + amp * cos(2 * pi * frq * (t - t0))

  @staticmethod
  def test():
    n = 60; t = arange(n); t0 = 3.2
    frq = 0.5; y0 = 2 / n * t + cos(frq * (t + t0))
    y0 += rng(n) * 2
    y0 = [y0]
    y0 = [rng(n) - 0.5] + y0
    y = cosfit2nd(y0, histogram = True); y1 = y.itp(t); yy = ystack(y0, y1); plot(y = yy, t = t) ## plot
    yh, th = y.histogram; plot(y = abs(yh), t = th) ## plot histogram

if 0:
  def foo(i):
    y = empty((16, 1 << i))
    # y = empty((16, i + 1))
    polyfit2nd(y, nth = 1)
    # y = itp2nd(y)[1]
    # fft2(y).fmax()
    # cosfit2nd(y)

  def bar(n): return Profile.timing2nd(foo, n = n)
