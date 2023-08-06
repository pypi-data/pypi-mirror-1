## import asciiporn; reload(asciiporn); from asciiporn import *
from __future__ import py3k_syntax
import os, sys



import functools, itertools, numpy, weave; from itertools import *; from numpy import *
if "DEBUG" not in globals(): DEBUG = 0 ## True prints debug info
if "YRES" not in globals(): YRES = 1 / 3
def quicktest():
  pass
  img2plaintxt.test()
  img2txt.test()
  plot3d.test()



if 1: ######## helper function
  def echo(x): return x

  @functools.wraps(builtins.enumerate)
  def enumerate(arr, i = None):
    if i: return zip(count(i), arr)
    return builtins.enumerate(arr)

  def flatten(*arr): return arr ..walktree()

  def isint(x):
    try: x & 0; return True
    except: return False

  def _profile(exe, n = None, lines = 64):
    import cProfile as profile; import pstats
    if n is not None: exe = 'for i in range({0}): {1}'.format(n, exe)
    x = pstats.Stats(profile.Profile().run(exe)).sort_stats('time'); x.print_stats(lines); return x

  def screensize(): import re; s = system("stty -a"); row, col = re.search("rows .*?(\d*).*?columns .*?(\d*)", s).groups(); return int(row), int(col)

  def shapes(*arr): return [shape(x) for x in arr]

  def strjoin(s, _ = ""): return _.join(s)

  def system(exe): import subprocess; exe = subprocess.Popen(exe, shell = 1, stdout = subprocess.PIPE, close_fds = 1).stdout; s = exe.read(); exe.close(); return s

  def walktree(tree, iterable = iterable, not_ = None, depth = -1):
    def walk(tree, depth):
      if iterable(tree) and depth:
        for x in tree:
          for y in walk(x, depth - 1): yield y
      else: yield tree
    if not_: istree = lambda x: not isleaf(x)
    return walk(tree, depth)



######## class
class savestate(object): ## use when subclassing extensions to allow serialization of self.__dict__
  def __savestate__(self): state = self.__dict__.copy(); state["__self__"] = self; return state

  @staticmethod
  def __loadstate__(state): state = state.copy(); self = state["__self__"]; del state["__self__"]; self.__dict__ = state; return self

class _asarray(ndarray, savestate): ## array w/ serializable states
  def __new__(self, arr, dtype = None, order = None):
    arr = numpy.asarray(arr, dtype, order)
    try: self = ndarray.__new__(self, arr.shape, arr.dtype, arr.data)
    except: return _asarray.__new__(self, arr.copy(), dtype, order)
    if arr.strides: self.strides = arr.strides
    return self



if 1: ######## math
  EPS = MachAr().eps; TINY = MachAr().tiny; HUGE = MachAr().huge
  STD = 0.682689492137085897170465091264075844955825933453208781974788900; STD2 = 0.954499736103641585599434725666933125056447552596643132032668000
  array = numpy.array
  rng = random.random
  stdev = numpy.std
  variance = numpy.var

  @functools.wraps(numpy.asarray)
  def asarray(arr, *args, **kwds): return numpy.asarray(tuple(arr) if hasattr(arr, "next") else arr, *args, **kwds)

  def as2d(arr, dtype = None, transpose = None, contiguous = None):
    arr = asarray(arr, dtype = dtype)
    if arr.size == 0: return arr.reshape(0, 0)
    arr = arr.reshape(-1, arr.shape[-1])
    if transpose: arr = arr.T
    if contiguous and not arr.flags.contiguous: arr = arr.copy()
    return arr

  def as64(x):
    if iterable(x): return asarray(x, dtype = int64)
    return int64(x)

  def bitshift64(a, b): return as64(a) << as64(b)

  def divceil(a, b): return (a + b - 1) // b

  def divround(a, b): return (a + (b >> 1)) // b

  @functools.wraps(numpy.linspace)
  def linspace(*args, **kwds):
    yt = None
    if "yt" in kwds: yt = kwds["yt"]; kwds = kwds.copy(); del kwds["yt"]

    tt = numpy.linspace(*args, **kwds)
    if yt is None: return tt

    yy = tt.copy()
    yt = asarray(yt, dtype = float); y, t = yt.T
    if any(t[1:] < t[:-1]): yt = yt[t.argsort()] # sort t-axis
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

  def orequal_sequential(arr, i, x):
    arr = asarray(arr); i = asarray(i); x = asarray(x)
    assert i.shape == x.shape and arr.dtype == x.dtype and 0 <= i.min() <= i.max() <= len(arr), (i.shape, x.shape, arr.dtype, x.dtype, i.min(), i.max(), len(arr))
    weave.inline("""const int N = Ni[0]; for (int j = 0; j < N; j++){arr[*i] |= *x; i++; x++;}""", ("arr", "i", "x"))
    return arr

  ## efficient 64 bit population count
  def popcount64(x):
    x = x - ((x >> 1) & 0x5555555555555555) ## count 2 bits
    x = ((x >> 2) & 0x3333333333333333) + (x & 0x3333333333333333) ## count 4 bits
    x = ((x >> 4) + x) & 0x0f0f0f0f0f0f0f0f ## count 8 bits
    x += x >> 8 ## count 16 bits
    x += x >> 16 ## count 32 bits
    x += x >> 32 ## count 64 bits
    return x & 127

  def rotate3d(x, y, z, t):
    inv = 1 / sqrt(x * x + y * y + z * z); x, y, z = x * inv, y * inv, z * inv; c = cos(t); s = sin(t); d = 1-c
    return [[x * x * d+c,     x * y * d-z * s, z * x * d+y * s],
            [x * y * d+z * s, y * y * d+c,     y * z * d-x * s],
            [z * x * d-y * s, y * z * d+x * s, z * z * d+c    ]] ..asarray()

  def roundint(x, dtype = int):
    if iterable(x): return asarray(x).round() ..asarray(dtype)
    return dtype(round(x))

  def ystack(*args): return vstack(as2d(x) for x in args)

if 1: ## simd
  def dot2nd(arr, x):
    arr = as2d(arr, contiguous = True); x = as2d(x, contiguous = True); assert arr.dtype == x.dtype, (arr.dtype, x.dtype); out = zeros(len(arr), x.dtype); ptr = x.ravel()[:1].copy()
    if len(x) <= 1: assert arr.shape[1] == x.shape[1], shapes(arr, x); dx = 0
    else: assert arr.shape == x.shape, shapes(arr, x); dx = x.shape[1]
    weave.inline("""
    int i; const int Ni = Narr[0];
    int j; const int Nj = Narr[1];
    for (i = 0; i < Ni; i++, out++, x += dx) {
    for (j = 0, ptr = x; j < Nj; j++, arr++, ptr++) {
    *out += *arr * *ptr;}}""", ("arr", "x", "out", "dx", "ptr")); return out

  def find2nd(arr, x):
    arr = as2d(arr, contiguous = True); x = reshape(x, (-1, 1))
    arr = asarray(arr == x, dtype = uint8); x = repeat(arr.shape[-1], len(arr)); weave.inline("""
    int i; const int Ni = Narr[0];
    int j; const int Nj = Narr[1];
    for (i = 0; i < Ni; i++, arr += Nj) {
    for (j = 0; j < Nj; j++) {
    if (arr[j]) {x[i] = j; break;}}}""", ("arr", "x")); return arange(len(x)), x

  def histogram2nd(arr):
    arr = as2d(arr, dtype = int, contiguous = True); n = arr.max() + 1
    assert 0 <= arr.min() <= n < 0x10000, (arr.shape, arr.dtype, arr.min(), n)
    h = zeros((len(arr), n), int)
    weave.inline("""
    int i; const int Ni = Narr[0];
    int j; const int Nj = Narr[1];
    const int Nh1 = Nh[1];
    for (i = 0; i < Ni; i++, h += Nh1) {
    for (j = 0; j < Nj; j++, arr++) {h[*arr] += 1;}}""", ("arr", "h")); return h



######## img2txt
class _img2txt(object):
  global X
  _ = ord(" ") ## convenience var for whitespace
  buf = empty(0, dtype = int64) ## internal buffer for outputting txt
  color = empty(0, dtype = int64) ## internal color buffer for outputting txt
  fres = r_[10, 6] ## row x col resolution of a character block
  mask = bitshift64(1, fres.prod()) - 1
  lucida = "AAAAAAAAAAAAQRAEARAAAIqiAAAAAAAAAEX5ylcUAACEVxwMRT0EAIBYKQylRgAAAKE4Zpt5AAAE\nQQAAAAAAADBCEARBIDAAA4EgCIIQAwAAsRkKAAAAAAAAEMRHEAAAAAAAAMAwCAEAAAAeAAAAAAAA\nAADAMAAAIAQhDCEIAQCAE0VRFDkAAIBREARBfAAAgANBCCF4AACAB0EMBDkAAADCKMmHIAAAgCcI\nDgQ5AAAAJwTNFDkAAIAHIQQhCAAAgBMlThQ5AACAE0UehBwAAAAAMAzAMAAAAAAwDMAwCAEAAEDM\nwEAAAAAAAD / wAwAAAAAEBmYEAACAJ0EIARAAAIAXdVUfeAAAAMMokieFAADAE0VPFD0AAAAnBEEg\ncAAAwBNFURQ9AACAJwiOIHgAAIAnCI4gCAAAACcEWSRxAABAFEVfFEUAAMBHEARBfAAAgIMgCIIY\nAABAlBRDkUQAAIAgCIIgeAAAQLRtV1VFAABANF1VlkUAAIATRVEUOQAAwBNFTxAEAACAE0VRFDkw\nAMCRJEeRRAAAACcIDAQ5AADARxAEQRAAAEAURVEUOQAAQBhJksIQAABAVFXVoygAAEAoMQgjhQAA\nQKQoBEEQAADAByGEEHwAABxBEARBEBwAgSAQBAJBIAAOgiAIgiAOAABBKIoSAQAAAAAAAAAAPwAE\nAgAAAAAAAAAAOBAn+QAAQRA0UxQ9AAAAAHhBEHgAABAEeVGUWQAAAAA40Rd4AAAYQXgEQRAAAAAA\neFGUWZADQRB0UxRFAAAIADgIgiAAAAgAOAiCIMgBgiBIiqFIAAAHQRAEQRAAAAAAfFVVVQAAAAB0\nUxRFAAAAADhRFDkAAAAANFMUPUEAAAB4UZRZEAQAAGiWIAgAAAAAcAIDOQAAAEF4BEFgAAAAAERR\nlF0AAAAARIqiEAAAAACUbStJAAAAAEQKoUQAAAAAhJLEMMQAAAB8CCF8AAAcQRACQRAcAARBEARB\nEAQADoIgEIIgDgAAAABnDgAAAAAAAAAAAAAA\n" ## lucida console 06x10 bitmap font encoded in 64 bits - use str2font to decode

  ## predefined colors
  bwrgbcmy = "0x000000 0xFFFFFF 0xFF0000 0x00FF00 0x0000FF 0x00A8EC 0xE3007B 0xF9F400"
  bwrgbcmy = ( eval(x) for x in bwrgbcmy.split(" ") ) ..asarray()
  rgbi = (36, 6, 1) ..asarray(dtype = uint8) ## set color channels to 8bit - numpy defaults to 64 bits, wasting space by order of magnitude

  ## color map
  clrmap = "  ".join( "\33[38;5;231m%c\33[0m" % x for x in range(128) )
  clrmap = "  ".join(( clrmap, clrmap.replace("231", "231;7") ))
  i = arange(16, 232) ## rgb666
  X = clrmap; clrmap = "  ".join( X.replace("231", str(x)) for x in i )
  clrmap = clrmap.split("  ") ..ravel()
  if True: clrmap[:256] = " " ## replace null clrmap -> efficient blanks - background must b set to black
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
    if DEBUG: font = font.reshape(fres * (6, 16)); self.printd(font[:fres[0]])

    font = font.reshape(6, fres[0], 16, fres[1]).transpose(0, 2, 1, 3) .reshape(r_[6 * 16, fres.prod()])
    for i, x in enumerate(font.T): font[:, 0] |= bitshift64(x, i)
    font = font[:, 0]
    if DEBUG:
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
    fmap = find2nd(fpop, fmap.T.flat[:])[1].reshape(2, -1).T
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

    self.fbmp = fbmp; self.ford = ford; self.fpop = fpop; self.fbin = fbin; self.fmap = fmap

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

  def tostr(self):
    if self.plaintxt or self.color is None: return "\n".join( "".join(self.chrmap[x]) for x in self.buf.reshape(self.res) )
    buf = self.buf | (self.color ..asarray(dtype = uint16) << 8)
    return "\n".join( "".join(self.clrmap[x]) for x in buf.reshape(self.res) )

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

    if not self.plaintxt and img.mode in ("CYMK", "RGB"):
      color = (img if img.mode == "RGB" else img.convert("RGB")).resize(self.res[::-1]).getdata() ..asarray(dtype = uint8).reshape(-1, 3)
      if invert: color ^= -1
      color *= 6 / 256
      self.color = color = dot( color, self.rgbi ) ## convert to rgb666
      color[(color == 0) & (self.buf != self._)] = 1 ## paint darkest nonempty pixel blud instead of invisible black
    else: self.color = color = None
    return self

  def __call__(self, *args, **kwds): return self.load(*args, **kwds).tostr()

  def test(self):
    img = "mario.jpg"
    txt = self(
      img,
      scale = 0.5, ## scale image size (0.5 = half, 1 = original, 2 = double)
      invert = 0, ## invert colors
      whitespace = True, ## True for optimal algorithm, False to deny a non-empty block from being written as whitespace (e.g. u want to see every datapoint in a plot)
      )
    print( txt )

img2plaintxt = _img2txt(plaintxt = True) ## creates portable plain txt image
img2txt = _img2txt(plaintxt = None) ## creates colorized txt image for display in terminals (xterm, putty, ...)



######## (z, y, t) datapoint storage object
class dataZYT(_asarray):
  def __new__(self, yt = None, z = None, y = None, t = None, zmin = None, zmax = None, ymin = None, ymax = None, tmin = None, tmax = None, zn = 64, yn = 64, tn = 64, ft = None, ftz = None, log2 = None):
    yt = [] if yt is None else [yt] if not ndim(yt[0]) else list(yt)
    y = [] if y is None else [y] if not ndim(y[0]) else list(y)
    if t is None and tmin is not None and tmax is not None: t = linspace(tmin, tmax, tn)
    if z is None and zmin is not None and zmax is not None: z = linspace(zmin, zmax, zn)

    if ft is not None:
      if not iterable(ft): ft = [ft]
      y += [[ft(_t) for _t in t] for ft in ft]
    if ftz is not None:
      y += [[ftz(_t, _z) for _t in t] for _z in z]

    yt += [transpose((x, t)) for x in as2d(y)]
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
    self.log2 = log2
    return self

  def roots(self):
    if not self.minmax[0, 0] <= 0 <= self.minmax[1, 0]: return
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
    if self.log2: arr[..., 1] = log2(1 + arr[..., 1])
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

  block = 160
  colori0 = gradienti[1:] ## plot color
  zeroi = dot( (36, 6, 1), (5, 0, 0) )
  s2rgb = staticmethod(s2rgb)
  printrgb = staticmethod(printrgb)

  def __call__(self, replot = None, itp = True, yres = None, **kwds):
    if replot: data = self.data; norm = self.norm
    else: self.data = data = dataZYT(**kwds).analyze(); self.norm = norm = data.norm()

    if yres is None: yres = YRES
    self.res = res = screensize() ..asarray(); res[0] *= yres ## res
    if len(self.buf) != res.prod(): self.buf = empty(res.prod(), dtype = int64) ## resize buf
    if len(self.color) != res.prod(): self.color = empty(res.prod(), dtype = int64) ## resize color buf
    buf = self.buf; color = self.color; buf[:] = color[:] = 0 ### reset buf
    s = self.plot().tostr(); print( "" ); print( self.header() ); print( s )

  def inverty(self, arr): arr = arr.copy(); arr[..., 1] = 1 - arr[..., 1]; return arr
  def scaleyt(self, yt, inverty, res = None):
    yt = self.data.norm(yt).reshape(-1, 3)[:, 1:]
    if inverty: yt[:, 0] = 1 - yt[:, 0]
    yt = asarray( yt * ((res if res else self.res) - 1), dtype = int ); return yt

  ## plot algorithm
  def plot(self):
    buf = self.buf; color = self.color; data = self.data; fres = self.fres; res = self.res
    self.colori = colori = self.colori0[linspace(0, len(self.colori0) - 1, len(data) + 1)[1:].astype(int)] ## colori

    ## draw lines between points
    arr = self.inverty(self.norm.reshape(-1, 3))
    arr = reshape( arr[:, 1:] * (res * fres - 1), (len(data), -1, 2) ).round()
    for i, yt in enumerate(arr):
      if len(yt) == 0: continue
      if len(yt) == 1: yt = yt.astype(int)
      else: y, t = yt.T; yt = linspace(t[0], t[-1], t[-1] - t[0] + 1, yt = yt).astype(int)
      a, b = divmod(yt, fres); y, t = a.T; a = a[:, 0] * res[1] + a[:, 1]; b = bitshift64(1, b[:, 0] * fres[1] + b[:, 1])
      color[a] = colori[i]
      if len(a) == 1: b[:] = self.mask
      orequal_sequential(buf, a, b)

    # self.itp(wmatch = 7, wmismatch = 1.5, whitespace = 0) ## itp
    self.itp(wmatch = 2, wmismatch = 1, whitespace = True) ## itp
    # cll = color.astype(bool) & (buf == self._); buf[cll] = self.block
    # x = color.astype(bool) & (color.astype(bool) ^ buf.astype(bool)); print(x.sum())

    o = self.scaleyt(data.origin, inverty = True).ravel(); o = asarray((o, res - 1)).min(axis = 0) ## origin
    cll = arange(0, len(buf), res[1]) + o[1]; cll = cll[buf[cll] == self._]; buf[cll] = ord("|"); color[cll] = self.zeroi ## y axis
    cll = arange(res[1]) + o[0] * res[1]; cll = cll[buf[cll] == self._]; buf[cll] = ord("-"); color[cll] = self.zeroi ## t axis
    cll = arange(res[1]); cll = r_[cll, -1 - cll]; cll = cll[ buf[cll] == self._ ]; buf[cll] = ord("-"); color[cll] = 43 ## box

    a, b = arr = data.extrema[:, :, 0].T; x, i = find2nd(arr, (a.min(), b.max())); self.mmci = mmci = colori[i] ## extrema
    y, t = self.scaleyt( data.extrema[i, [0, 1]], inverty = True ).T; x = t + o[0] * res[1]; buf[x] = self.block; color[x] = mmci
    return self

  ## print header info
  def header(self):
    colori = self.colori; data = self.data; c = self.rgb[colori]; mm = data.minmax
    return "SIDEVIEW Y:\t\tZ  %s to %s  %s\t\tY  %s to %s\t\tT  %s to %s\t\tMIN MAX  %s" % (
      data.z[0], data.z[-1], "".join(c),
      mm[0, 0], mm[1, 0],
      mm[0, 1], mm[1, 1],
      " ".join(self.rgb[self.mmci])
      )

  def test(self, plot = None):
    if plot: self = plot
    if 1:
      t = linspace(0, 1, 64) - 0.25
      y = [ t, cos(t * 2 * pi), sin(t * 4 * pi), cos(t * 2 * pi) + 0.25 ]
      yt = None
      yres = 1 / 3
      self(yt = yt, y = y, t = t, yres = yres)

    if 1:
      tmin, tmax = -1, 1
      zmin, zmax = 0, 1
      ftz = lambda t, z: sin( t*(2*pi + z) ) * (0.5 + z) - z
      yres = 1 / 3
      self(ftz = ftz, zmin = zmin, zmax = zmax, tmin = tmin, tmax = tmax, yres = yres)



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
        t0 = self.scaleyt(transpose((t0, t0)), inverty = None)[:, 1]; buf[z, t0] = self.block; color[z, t0] = self.zeroi ## plot y roots
      z0 = z
    return self

  def header(self):
    data = self.data; c = self.rgb[self.colori0]; mm = data.minmax
    return "TOPVIEW Z:\t\tZ  %s to %s  (top to bottom)\t\tY  %s to %s  %s\t\tT  %s to %s\t\tROOTS  %s" % (
      data.z[0], data.z[-1],
      mm[0, 0], mm[1, 0], "".join(c),
      mm[0, 1], mm[1, 1],
      self.rgb[self.zeroi],
      )

plot = _plot(plaintxt = None)
plotsurf = _plotsurf(plaintxt = None)
def plot3d(**kwds):
  plot(**kwds)
  plotsurf.data = plot.data; plotsurf.norm = plot.norm; plotsurf(**kwds)
plot3d.test = lambda: plot.test(plot = plot3d)

# plot3d.test()
