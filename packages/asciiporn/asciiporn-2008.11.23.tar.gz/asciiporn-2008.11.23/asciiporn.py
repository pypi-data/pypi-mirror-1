"""
################################################################################
this is a moderately sophisticated python3.0 script fully utilizing
extensions, & demonstrated to run under python2.6 via py3to2.
for performance, portions of it have been inlined w/ direct C code using
scipy.weave.  the algorithm also heavily uses bitwise operations.
it takes a jpg, gif... image file & outputs it in colorized ascii art.
also serves dual purpose as a 3-d colorized scientific plotter in text terminals
(screenshots of image conversion & 3d plot in putty terminal included)

if something fails, try updating ur install of py3to2 to the latest version @:
http://pypi.python.org/pypi/py3to2

how to enable 256 color on putty: http://www.emacswiki.org/emacs/PuTTY#toc2
how to enable 256 color on xterm: http://www.frexx.de/xterm-256-notes/

asciiporn is hard-coded to use lucida-console font, but courier looks ok.
the screenshot shows putty w/ lucida-console 5pt.

AUTHOR:
  kai zhu
  kaizhu@ugcs.caltech.edu

REQUIREMENTS:
- posix/unix os (Windows currently unsupported)
- py3to2
- Python Imaging Library
- scipy

PSEUDOMETHOD:
  asciiporn uses ".." syntax notation for pseudomethods
  goto: http://pypi.python.org/pypi/pseudomethod
  for more details about this feature

API:
  asciiporn module:
  - img2plaintxt - converts image file to portable plain txt
                   u can copy & paste in documents
  - img2txt - converts image to high-quality colorized txt
              for display on terminals supporting 256 color (putty, xterm...)
  - tplot3d - 3d color scientific plotter

INSTALL:
  python setup.py build
  python setup.py install
  python setup.py dev --quicktest

################################################################################
IMAGE USAGE:
  start up the py3to2 interpreter by typing "py3to2" in ur terminal &
  import asciiporn:
    $ py3to2

    Python 2.6.py3to2 (r26:66714, Nov 18 2008, 00:56:43)
    [GCC 3.4.6 20060404 (Red Hat 3.4.6-10)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>>
    >>> import asciiporn
    created...
    py3k server starting...
    >>> ...py3k server started w/...
    >>>

  in this example, u'll b loading the image file included w/ this distribution,
  "mario.jpg".  its a fairly large image, so u probably want to scale it down
  to 0.5 (or less):
    >>> colortxt = asciiporn.img2txt("mario.jpg", scale = 0.5)
    >>> print( colortxt )

    ... beautiful image appears ^_-

    >>> plaintxt = asciiporn.img2plaintxt("mario.jpg", scale = 0.5)
    >>> print( plaintxt )

    ... rather plain b/w img -_-, but u can copy & paste in documents

  actually, the plaintxt prolly won't look well when pasted,
  b/c most document readers invert the color:
    >>> plaintxt = asciiporn.img2plaintxt('mario.jpg', scale = 0.5, invert = True)
    >>> print( plaintxt )

    ... b/w img w/ colors inverted.  may look funny now :/
        but it'll b normal when pasted document

################################################################################
PLOT USAGE:

################################################################################
RECENT CHANGELOG:
  rewrote 3d plotter
  fixed more 64bit issues
20081123
  fixed bug where 64bit  gets truncated to 32 on 32bit machine
  256 color support
20081119
  fixed bugs in setup.py
"""
__author__ =	"kai zhu"
__author_email__ =	"kaizhu@ugcs.caltech.edu"
__description__ =	"""
takes a jpeg, gif, etc... image file & outputs it as colorized ascii art.
also does 3d-plots (screenshots of image conversion & 3d plots in putty terminal
included)
"""
__download_url__ =	None
__keywords__ =	None
__license__ =	"BSD"
__maintainer__ =	None
__maintainer_email__ =	None
__obsoletes__ =	None
__platforms__ =	None
__provides__ =	None
__requires__ =	["py3to2", "pil", "scipy"]
__url__ = "http://www-rcf.usc.edu/~kaizhu/work/asciiporn"
__version__  = "2008.11.23"
## end setup info

## import asciiporn; reload(asciiporn); from asciiporn import *
from __future__ import py3k_syntax
import functools, itertools, re, subprocess, time, types; from itertools import *
print("asciiporn importing scipy which may take awhile...")
import numpy, scipy.weave; from numpy import *
if "DEBUG" not in globals(): DEBUG = 0

if 1: ######## general
  def echo(x): return x

  def _enumerate(arr, i = None):
    if i: return zip(count(i), arr)
    return enumerate(arr)

  def flatten(*arr): return arr ..walktree() ..tuple()

  def isint(x):
    try: x & 0; return True
    except: return False

  def iterable(x): return hasattr(x, "__iter__")

  def _profile(exe, n = None, lines = 64):
    import cProfile as profile; import pstats
    if n is not None: exe = 'for i in range({0}): {1}'.format(n, exe)
    x = pstats.Stats(profile.Profile().run(exe)).sort_stats('time'); x.print_stats(lines); return x

  def screensize(): s = system_("stty -a"); row, col = re.search("rows .*?(\d*).*?columns .*?(\d*)", s).groups(); return int(row), int(col)

  def shapes(*arr): return [shape(x) for x in arr]

  def strjoin(s, _ = ""): return _.join(s)

  def system_(exe): exe = subprocess.Popen(exe, shell = 1, stdout = subprocess.PIPE, close_fds = 1).stdout; s = exe.read(); exe.close(); return s

  def walktree(tree, iterable = iterable, not_ = None, depth = -1):
    def walk(tree, depth):
      if iterable(tree) and depth:
        for x in tree:
          for y in walk(x, depth - 1): yield y
      else: yield tree
    if not_: istree = lambda x: not isleaf(x)
    return walk(tree, depth)

######## class
class savestate(object): ## use when subclassing extensions to allow serialization of  self.__dict__
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

  def bitshift64(a, b): return int64(a) << int64(b)

  def divceil(a, b): return (a + b - 1) // b

  def divround(a, b): return (a + (b >> 1)) // b

  def find2nd(arr, x):
    n = arr.shape[-1]; x = (arr == reshape(x, (-1, 1))) ..asarray(dtype = uint8)
    out = repeat(n, len(x)); out.fill(n); scipy.weave.inline("""
    for(int i = 0; i < Nx[0]; i++){
    for(int j = 0; j < Nx[1]; j++){
    if(x[j]) {out[i] = j; break;}
    } x += Nx[1];}""", ("out", "x"), compiler = "gcc"); return arange(len(out)), out

  def _histogram(arr):
    arr = asarray(arr); n = arr.max() + 1; assert n < 0x10000, n; h = zeros(n, int)
    scipy.weave.inline("""for(int i = 0; i < Narr[0]; i++){h[*arr] += 1; arr++;}""", ("arr", "h"), compiler = "gcc")
    return h

  def invzero(x, nan = nan): return 1 / x if x else nan

  def monotonic(arr):
    if all(arr[1:] >= arr[:-1]): return 1
    elif all(arr[1:] <= arr[:-1]): return -1
    return 0

  def orequal(arr, i, x):
    arr = asarray(arr); i = asarray(i); x = asarray(x); assert i.shape == x.shape
    scipy.weave.inline("""for(int j = 0; j < Ni[0]; j++){arr[*i] |= *x; i++; x++;}""", ("arr", "i", "x"), compiler = "gcc")
    return arr

  def popcount(x): ## 64 bit population count - O(log)
    x = x - ((x >> 1) & 0x5555555555555555) ## count 2 bits
    x = ((x >> 2) & 0x3333333333333333) + (x & 0x3333333333333333) ## count 4 bits
    x = ((x >> 4) + x) & 0x0f0f0f0f0f0f0f0f ## count 8 bits
    x += x >> 8 ## count 16 bits
    x += x >> 16 ## count 32 bits
    x += x >> 32 ## count 64 bits
    return x & 127

  def roundint(x, dtype = int):
    if iterable(x): return asarray(x).round() ..asarray(dtype)
    return dtype(round(x))

  def rotate3d(x, y, z, t):
    inv = 1 / sqrt(x * x + y * y + z * z); x, y, z = x * inv, y * inv, z * inv; c = cos(t); s = sin(t); d = 1-c
    return [[x * x * d+c,   x * y * d-z * s, z * x * d+y * s],
            [x * y * d+z * s, y * y * d+c,   y * z * d-x * s],
            [z * x * d-y * s, y * z * d+x * s, z * z * d+c  ]] ..asarray()

######## img2txt
# def foo(self, arr): print( arr.reshape(self.res)[0] )
class _img2txt(object):
  global X
  _ = ord(" ") ## convenience var for whitespace
  buf = empty(0, dtype = int64) ## internal buffer for outputting text
  color = empty(0, dtype = int64) ## internal color buffer for outputting text
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
    cll = sum(1 ..bitshift64(arange(0, fres.prod(), fres[1]))) ^ self.mask ## cll left boundary
    x = arr[..., 3]; x &= cll; x >>= 1 ## shift left
    x = arr[..., 4]; x <<= 1; x &= cll ## shift right
    if 0 and DEBUG:
      for x in arr[17, :5]: self.printd(x)

    fbmp = arr ## bmp of font
    ford = r_[32:128]; assert len(ford) == len(fbmp) ## maps fbmp -> ord
    fpop = popcount(fbmp[:, 0])

    if not plaintxt: ## include inverted color
      fbmp = (fbmp, fbmp ^ self.mask) ..concatenate(axis = 0)
      ford = r_[ford, ford + 128]; fpop = r_[fpop, fres.prod() - fpop]
      fpop[-1] = 0 ## redundant fres.prod()

    cll = [0] + [i for i, x in enumerate(fpop) if x] ## cll whitespace
    fbmp, ford, fpop = (x[cll] for x in (fbmp, ford, fpop))

    cll = fpop.argsort() ## sort by population count
    fbmp, ford, fpop = (x[cll] for x in (fbmp, ford, fpop))
    self.level = level = fpop.mean() * 255 / fres.prod()

    hst = _histogram(fpop)
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
    fmap = flatten(zip_longest(a, b, c))
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
    buf = self.buf; self.pop = pop = popcount(buf)
    for (a, b), (c, f) in zip(self.fbin, self.fmap):
      cll = (a <= pop) & (pop < b)
      if not cll.any(): continue
      x = buf[cll]; f = f.T[..., newaxis]
      y = popcount(x & f) ## match
      y[0] *= wmatch ## weight original match
      y[0] -= popcount(x ^ f[0]) * wmismatch ## subtract mismatch
      y = y.sum(axis = 0); y = y.argsort(axis = 0)[-1] + c; ## tally weights & pick highest
      if not whitespace: y[y == 0] = 1
      buf[cll] = self.ford[y]
    buf[buf == 0] = self._; return self

  def tostr(self):
    if self.plaintxt or self.color is None: return "\n".join( "".join(self.chrmap[x]) for x in self.buf.reshape(self.res) )
    # print( self.buf.reshape(self.res)[0] )
    # print( self.color.reshape(self.res)[0] )
    buf = self.buf | (self.color ..asarray(dtype = uint16) << 8)
    return "\n".join( "".join(self.clrmap[x]) for x in buf.reshape(self.res) )

  # def load(self, file, scale = 1, invert = None, **kwds): ## must be a file or filename
    # from PIL import Image; img = Image.open(file) ## import img
    # fres = self.fres[::-1]; res = asarray(img.size) * scale / fres; res = ceil(res).astype(int) * fres ## make res multiple of fres
    # if not all(res == img.size): img = img.resize(res) ## resize img

    # if self.plaintxt: ## auto-level
      # gray = (img if img.mode == "L" else img.convert("L"))
      # arr = gray.getdata() ..asarray(dtype = uint8)
      # if invert: arr ^= -1
      # x = arr.mean()
      # if x > self.level:
        # arr *= self.level / x; img = gray
        # img.putdata(arr)

    # self.res = res[::-1] // fres[::-1] ## save res
    # arr = (img if img.mode == "1" else img.convert("1")).getdata() ..asarray(dtype = bool).reshape(res[::-1])
    # if invert and not self.plaintxt: arr ^= True
    # self.fill(arr).itp(**kwds) ## itp

    # if not self.plaintxt and img.mode in ("CYMK", "RGB"):
      # color = (img if img.mode == "RGB" else img.convert("RGB")).resize(self.res[::-1]).getdata() ..asarray(dtype = uint8).reshape(-1, 3)
      # if invert: color ^= -1
      # color *= 6 / 256
      # self.color = color = dot( color, self.rgbi ) ## convert to rgb666
      # color[(color == 0) & (self.buf != self._)] = 1 ## paint darkest nonempty pixel blud instead of invisible black
    # else: self.color = color = None
    # return self

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

def quicktest():
  img2plaintxt.test()
  img2txt.test()
  plot3d.test()





######## (z, y, t) datapoint storage object
class dataZYT(ndarray):
  def __new__(self, yt = None, y = None, t = None, trange = None, z = None, zrange = None):
    if trange is not None: assert t is None; t = linspace(trange[0], trange[1], 256)
    # if yrange is not None: assert y is None; y = linspace(yrange[0], yrange[1], 64)
    if zrange is not None: assert z is None; z = linspace(zrange[0], zrange[1], 64)

    # if callable(yt): ## z fnc
      # assert ndim(y) == ndim(t) == 1
      # if len(y) * len(t) > 0x10000: raise ValuError("too many datapoints to calculate")
      # yt = [ [(yt(a, b), b) for b in t] for a in y ]

    if z is not None: ## z fnc
      assert yt is None and callable(y) and ndim(t) == ndim(z) == 1
      if len(t) * len(z) > 0x10000: raise ValuError("too many datapoints to calculate")
      yt = [ [(y(_t, _z), _t) for _t in t] for _z in z ]

    elif yt is not None: ## zipped yt
      assert y is None and t is None; yt = asarray(yt, dtype = float); shp = r_[1, yt.shape][-3:]; yt = yt.reshape(shp)

    else: ## individual y, t
      assert yt is None

      if not iterable(y): y = [y]
      for i, f in enumerate(y):
        if callable(f): assert ndim(t) == 1; y[i] = [f(x) for x in t] # eval y(t)
        elif not iterable(f): y[i] = [f] * len(t) # constant

      y = asarray(y, dtype = float); yshp = r_[1, y.shape][-2:]; y = y.reshape(yshp)

      if t is None: t = range(yshp[1])
      t = asarray(t, dtype = float); tshp = r_[1, t.shape][-2:]; t = t.reshape(tshp)

      assert yshp[1] == tshp[1]
      zy, nt = yshp[0], tshp[0]; assert (zy % nt) == 0 or (nt % zy) ==0

      if zy > nt: t = t.repeat(zy // nt, axis = 0)
      elif nt > zy: y = y.repeat(nt // zy, axis = 0)
      yt = transpose((y, t), (1, 2, 0))

    self = _asarray.__new__(self, array(yt)); self.z = z = arange(len(self)) if z is None else asarray(z)
    self.minmax = minmax = [(x.min(), x.max()) for x in self.T] ..transpose() ## self.minmax
    if any(minmax[0] == minmax[1]):
      if minmax[0, 1] == minmax[1, 1]: raise ValueError("datapoints all lie on vertical line t = %s" % minmax[0, 1])
      else: raise ValueError("datapoints all lie on horizontal line y = %s" % minmax[0, 0])
    self.origin = origin = [0.0 if a <= 0 <= b else a if 0 < a else b for a, b in minmax.T] ..asarray() ## self.origin
    return self

  def roots(self):
    if not self.minmax[0, 0] <= 0 <= self.minmax[1, 0]: return
    assert self.sorted; roots = []
    for i, (y, t) in enumerate(self.transpose(0, 2, 1)):
      y = y.copy(); y[y < 0] = -1; y[y > 0] = 1; y = y[:-1] != y[1:]
      roots.append(t[y])
    return roots

  def analyze(self):
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
    arr = asarray(arr); arr = arr.reshape(r_[1, 1, arr.shape][-3:]).astype(float); arr -= a; arr *= 1 / (b - a) # norm
    n = linspace(0, 1, len(arr)); n = n[newaxis, :].repeat(arr.shape[1], axis = -1).reshape(r_[arr.shape[:-1], 1])
    arr = concatenate((n, arr), axis = -1)
    return arr

  @staticmethod
  def test():
    if 1:
      x = dataZYT(y = [ [0,1,2,-1,3], [1, 0, 0, 4, 0] ], t = [4,3,2,7,8]).init()
      print(); print( x, x.minmax, x.origin )
      print(); print( x.norm(x) )
# dataZYT.test()



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

  # colori = greeni[1:] # plot color
  colori = rainbowi[4:] # plot color
  # colori = bluei[1:] # plot color
  zeroi = dot( (36, 6, 1), (5, 0, 0) )
  s2rgb = staticmethod(s2rgb)
  printrgb = staticmethod(printrgb)

  def __call__(self, yt = None, y = None, colori = rainbowi[5:], yres = 1 / 3, **kwds):
    if yt is None and y is None: data = self.data; norm = self.norm
    else: self.data = data = dataZYT(yt = yt, y = y, **kwds).analyze(); self.norm = norm = data.norm()

    self.colori = colori ## colori
    self.res = res = screensize() ..asarray(); res[0] *= yres ## res
    if isinstance(self, _plotsurf): res[0] = min(res[0], len(data))
    if len(self.buf) != res.prod(): self.buf = empty(res.prod(), dtype = int64) ## resize buf
    if len(self.color) != res.prod(): self.color = empty(res.prod(), dtype = int64) ## resize color buf
    buf = self.buf; color = self.color; buf[:] = color[:] = 0 ### reset buf
    s = self.plot().tostr(); print( "" ); print( self.header() ); print( s )

  def inverty(self, arr): arr = arr.copy(); arr[..., 1] = 1 - arr[..., 1]; return arr
  def scaleyt(self, yt, inverty, res = None):
    yt = self.data.norm(yt).reshape(-1, 3)[:, 1:]
    if inverty: yt[:, 0] = 1 - yt[:, 0]
    yt = roundint( yt * ((res if res else self.res) - 1) ); return yt

  ## plot algorithm
  def plot(self):
    buf = self.buf; color = self.color; colori = self.colori; data = self.data; fres = self.fres; res = self.res; arr = self.inverty(self.norm.reshape(-1, 3))

    c = colori[ roundint( arr[:, 0] * (len(colori) - 1) ) ]
    arr = roundint( arr[:, 1:] * (res * fres - 1) )
    a, b = divmod(arr, fres) ..transpose((0, 2, 1))
    a = a[0] * res[1] + a[1]; b = 1 ..bitshift64(b[0] * fres[1] + b[1])
    color[a] = c ## fill color buf
    orequal(buf, a, b) ## fill buf
    self.itp(wmatch = 7, wmismatch = 1.5, whitespace = 0) ## itp
    if len(arr) < 64: buf[buf != self._] = 160 ## cutoff to use block datapoints for better visibility

    # o = self.inverty(data.norm(data.origin)); o = roundint( o.ravel()[1:] * res ); o = asarray((o, res - 1)).min(axis = 0) ## origin
    o = self.scaleyt(data.origin, inverty = True).ravel(); o = asarray((o, res - 1)).min(axis = 0) ## origin
    cll = arange(0, len(buf), res[1]) + o[1]; cll = cll[buf[cll] == self._]; buf[cll] = ord("|"); color[cll] = self.zeroi ## y axis
    cll = arange(res[1]) + o[0] * res[1]; cll = cll[buf[cll] == self._]; buf[cll] = ord("-"); color[cll] = self.zeroi ## t axis
    cll = r_[ r_[:res[1]], -1 - r_[:res[1]] ]; cll = cll[ buf[cll] == self._ ]; buf[cll] = ord("-"); color[cll] = 43 ## box

    a, b = arr = data.extrema[:, :, 0].T; x, i = find2nd(arr, (a.min(), b.max())) ## extrema
    self.mmi = mmi = colori[roundint( i * (len(colori) - 1) / (len(data) - 1) )]
    y, t = self.scaleyt( data.extrema[i, [0, 1]], inverty = True ).T; x = t + o[0] * res[1]
    buf[x] = 160; color[x] = mmi
    return self

  ## print header info
  def header(self):
    colori = self.colori; data = self.data
    c = linspace(0, len(colori) - 1, min(len(data), len(colori))) ..roundint(); c = self.rgb[colori[c]]; mm = data.minmax
    return "SIDEVIEW Y:\t\tZ  %s to %s  %s\t\tY  %s to %s\t\tT  %s to %s\t\tORIGIN  %s\t\tMIN MAX  %s" % (
      # 0, len(self.data) - 1, "".join(c),
      data.z[0], data.z[-1], "".join(c),
      mm[0, 0], mm[1, 0],
      mm[0, 1], mm[1, 1],
      self.rgb[self.zeroi],
      " ".join(self.rgb[self.mmi])
      )

  def test(self, plot = None):
    if plot: self = plot
    if 1:
      t = linspace(0, 1, 256) - 0.25
      y = [ echo, cos(t * 2 * pi), sin(t * 4 * pi), cos(t * 2 * pi) + 0.25 ]
      yt = None
      yres = 1 / 3
      self(yt = yt, y = y, t = t, yres = yres)

    if 1:
      trange = -1, 1
      zrange = 0, 1
      y = lambda t, z: sin( t*(2*pi + z) ) * (0.5 + z) - z
      yres = 1 / 3
      self(y = y, trange = trange, zrange = zrange, yres = yres)

## surface plot
class _plotsurf(_plot):
  colori = _plot.gradienti[1:] # plot color
  # colori = _plot.blueredi[1:-1] # plot color

  def plot(self):
    res = self.res; buf = self.buf.reshape(res); color = self.color.reshape(res); data = self.data; arr = self.norm.reshape(-1, 3)

    arr = arr[arr[:, 1].argsort()]; z, t = roundint( arr.T[[0, 2]] * (res[:, newaxis] - 1) ); y = arr[:, 1]
    buf[z, t] = self.ford[roundint( y * (len(self.ford) - 1) )]
    color[z, t] = self.colori[roundint( y * (len(self.colori) - 1) )]

    roots = data.roots(); i = linspace(0, res[0] - 1, len(roots)) ..roundint() ## plot y roots
    for i, t in zip(i, roots): t = self.scaleyt(transpose((t, t)), inverty = None)[:, 1]; buf[i, t] = 160; color[i, t] = self.zeroi
    return self

  def header(self):
    colori = self.colori; data = self.data; c = self.rgb[colori]; mm = data.minmax
    return "TOPVIEW Z:\t\tZ  %s to %s  (top to bottom)\t\tY  %s to %s  %s\t\tT  %s to %s\t\tY ROOTS  %s" % (
      # 0, len(self.data) - 1,
      data.z[0], data.z[-1],
      mm[0, 0], mm[1, 0], "".join(c),
      mm[0, 1], mm[1, 1],
      self.rgb[self.zeroi],
      )

plot = _plot(plaintxt = None)
plotsurf = _plotsurf(plaintxt = None)
def plot3d(**kwds):
  plot(colori = _plot.bluei[1:], **kwds)
  plotsurf.data = plot.data; plotsurf.norm = plot.norm; plotsurf(colori = _plot.gradienti[1:], **kwds)

plot3d.test = lambda: plot.test(plot = plot3d)
# quicktest()
# plot.test(plot = plot3d)
