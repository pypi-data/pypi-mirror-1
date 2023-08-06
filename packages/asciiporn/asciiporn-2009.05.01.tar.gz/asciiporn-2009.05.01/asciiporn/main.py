## import asciiporn; reload(asciiporn); from asciiporn import *
from __future__ import py3k_syntax
import asciiporn, os, sys, traceback
__readme__ = """
################################################################################
originally ascii art graphics library for ssh terminal,
but expanded to include scientific visualization.

this package has 2 main files:
  asciiporn/__init__.py ## initialize custom import hook to load main.py
  asciiporn/main.py     ## contains EVERYTHING

how to enable 256 color in putty:  http://www.emacswiki.org/emacs/PuTTY#toc2
how to enable 256 color in xterm:  http://www.frexx.de/xterm-256-notes/
how to enable 256 color in screen: http://www.frexx.de/xterm-256-notes/

AUTHOR:
  kai zhu
  kaizhu256@gmail.com

REQUIREMENTS:
  posix os
  Python 2.6
  Python Imaging Library  http://www.pythonware.com/products/pil
  numpy                   http://www.scipy.org/Download

INSTALL:
  python setup.py build
  python setup.py install
  python setup.py dev --quicktest

USAGE:
  $ python setup.py dev --quicktest
    render color image in shell terminal &
    plot scientific functions as well



  >>> from asciiporn import *

  >>> print( img2txt("filename") )
    display color image from gif, jpg, bmp, ... to screen.
    only works if u have Python Imaging Library installed

  >>> help(img2txt.load)
    display img2txt options



  >>> plot(ft = lambda t: cos(t), tmin = 0, tmax = 16)
    plot cos(t) for t = [0, 16]

  >>> plot(ft = [cos, sin], tmin = 0, tmax = 16)
    plot 2 functions, cos & sin

  >>> plot( y = [1.5, 2.5, 3.5], t = [0, 1, 2] )
    plot datapoints (y, t) = (1.5, 0), (2.5, 1), (3.5, 2)

  >>> f = lambda t, z: sin( t*(2*pi + z) ) * (0.5 + z) - z
  >>> plot3d(ftz = ftz, tmin = 0, tmax = 16, zmin = 0, zmax = 1)
    plot f in 3d using specified ranges for t & z

  >>> help(plot.__call__)
  >>> help(dataZYT.__new__)
    display plot options



  >>> fitpoly.test()
    test asciiporn's polynomial fitting routine
    peruse fitpoly.test in asciiporn/main.py for usage

  >>> fft2d.test()
    test asciiporn's cosine fitting routine
    peruse fft2d.test in asciiporn/main.py for usage

################################################################################
RECENT CHANGELOG:
20090407
  fixed installation bugs
  added retro-gif feature
20090328
  removed py3to2 requirement
  update documentation
20090103
  rewrote 3d plotter
  fixed more 64bit issues
20081123
  fixed bug where 64bit gets truncated to 32 on 32bit machine
  256 color support
20081119
  fixed bugs in setup.py
"""
__metadata__ = {
  "name":        "asciiporn",
  "author":      "kai zhu",
  "author_email":"kaizhu256@gmail.com",
  "description":"""
  view color images & 3d scientific plots in ssh terminal
  (screenshots using putty ssh terminal included)
  """,
  "download_url": None,
  "keywords":     None,
  "license":      "gpl",
  "long_description": __readme__,
  "maintainer":   None,
  "maintainer_email":None,
  "obsoletes":    None,
  "platforms":    None,
  "provides":     None,
  "requires":     ["PIL", "numpy"],
  "url":          "http://pypi.python.org/pypi/asciiporn",
  "version":      "2009.05.01",}



import collections, functools, itertools, numpy, re; from itertools import *; from numpy import *; from . import weave
if "DEBUG" not in globals(): DEBUG = 0 ## True prints debug info
if "YRES" not in globals(): YRES = 32

def quicktest():
  print( "test b/w image graphics" )
  img2plaintxt.test(); print()

  print( "test 6*6*6 rgb image graphics" )
  img2txt.test(); print()

  print( "test 3d plot" )
  plot3d.test(); print()

  print( "test cosine fitting algorithm" )
  fft2d.test(); print()



if 1: ######## helper fnc

  ## debug tool
  def dtypes(*args): return [x.dtype for x in args]
  def lens(*args): return [len(x) for x in args]
  def shapes(*args): return [shape(x) for x in args]

  ## state serialization
  def stateload(**state): self = state.pop("__self__"); self.__dict__ = state; return self
  def statesave(self): state = self.__dict__.copy(); state["__self__"] = self; return state
  def stateimport(self, other): self.__dict__ = other.__dict__; return self

  def echo(x): return x

  @functools.wraps(builtins.enumerate)
  def enumerate(arr, i = None): return count(i) ..zip(arr) if i else builtins.enumerate(arr)

  def isint(x):
    try: x & 0; return True
    except: return False

  def readline(fname, _ = None):
    with open(fname) as file:
      line = 1
      while line:
        line = file.readline()
        if not _: line = line.replace("\n", "").replace("\r", "")
        yield line

  ## get current screensize - row x col
  def screensize(): return system("stty -a") ...re.search("rows .*?(\d*).*?columns .*?(\d*)").groups() ...map(int) ..tuple()

  def sjoin(s, _ = ""): return _.join(s)

  ## piped system call
  def system(exe):
    import subprocess
    with subprocess.Popen(exe, shell = 1, stdout = subprocess.PIPE, close_fds = 1).stdout as exe: return exe.read()

  ## generate unique alphanumeric string guaranteed not to occur in s
  def uniquestr(s, kwd = "qjzx"):
    while kwd in s: kwd = kwd + hex(id(kwd))
    return kwd

  def walktree(tree, iterable = iterable, depth = -1):
    if iterable(tree) and depth:
      for x in tree:
        for y in walktree(x, iterable, depth - 1): yield y
    else: yield tree

  flatten = walktree



######## class
import cProfile as profile, time
class _Profile(profile.Profile):

  def __call__(self, exe, lines = 64, sort = 1):
    self.runcall(exe) ## profile
    s = stdout2str(lambda: self.print_stats(sort = sort)) ## catch print output to str
    if lines: s = s.split("\n")[:lines] ..sjoin("\n") ## condense to lines
    return s

  def timing(self, exe, _time = time.time): t0 = _time(); exe(); return _time() - t0

  def timing2d(self, fnc, n, t_transform = echo, status_interval = 2, plot = True):
    tt = collections.deque(); self.timing(lambda: fnc(0)); T0 = time.time()
    for i in range(n):
      t = self.timing(lambda: fnc(i)) ..t_transform(); tt.append(t); T = time.time()
      if T - T0 > status_interval:
        T0 = T; print( "profiling", i, t )
        if plot: asciiporn.plot(y = tt)
    if plot: asciiporn.plot(y = tt)
    return tt

Profile = _Profile()



## my custom arr class
class asarray(ndarray):

  def __new__(self, arr, dtype = None):
    if not isinstance(arr, ndarray): return numpy.array(
      tuple(arr) if hasattr(arr, "__next__") else arr,
      dtype).view(self)
    if dtype and dtype != arr.dtype: return arr.astype(dtype).view(self)
    return arr if isinstance(arr, self) else arr.view(self)

  def fillfrom_(self, arr):
    assert isinstance(arr, ndarray), type(arr)
    assert self.dtype == arr.dtype, dtypes(self, arr)
    assert self.shape == arr.shape, shapes(self, arr)
    "const int N = n; for (int i = 0; i < N; *self = *arr, i++, self++, arr++);" ..inline( n = self.size, self = self, arr = arr ); return self

  def empty(self, shape = None): return empty(shape if shape is not None else self.shape, self.dtype).view(type(self)) ..stateimport(self)



if 1: ######## math

  EPS  = MachAr().eps
  EPS1 = 1 + EPS
  TINY = MachAr().tiny
  HUGE = MachAr().huge
  STD  = 0.682689492137085897170465091264075844955825933453208781974788900
  STD2 = 0.954499736103641585599434725666933125056447552596643132032668000

  array = numpy.array
  randg = random.random
  stdev = numpy.std
  varnc = numpy.var

  ## create arr ptr
  def arrp(x):
    if hasattr(x, "dtype"): x = x.dtype.type()
    return ravel(x)

  def as2d(arr, contiguous = True):
    arr = asarray(arr)
    if contiguous: assert arr.flags.contiguous, arr.flags
    assert arr.size, arr; return arr.reshape(-1, arr.shape[-1])

  def as64(x):
    if iterable(x): return asarray(x, dtype = int64)
    return int64(x)

  def bitshiftl64(a, b): return as64(a) << as64(b)

  def bitshiftr64(a, b): return as64(a) >> as64(b)

  def divceil(a, b): return (a + b - 1) // b

  def divround(a, b): return (a + (b >> 1)) // b

  def inline(code, **kwds):
    for i, x in kwds.items():
      if isinstance(x, ndarray): assert x.flags.contiguous, (i, x.flags); kwds[i] = x.view(ndarray)
    weave.inline( code, arg_names = kwds.keys(), local_dict = kwds ); return kwds

  def roundint(x):
    if iterable(x): return asarray(x).round() ..asarray(dtype = int)
    return int(round(x))

  def ystack(*args): return vstack(as2d(x, contiguous = None) for x in args)

  def assert2d(arr, dtype = None, contiguous = None):
    assert isinstance(arr, ndarray), type(arr)
    assert arr.size, arr
    if arr.ndim <= 1: arr = arr.reshape(-1, arr.shape[-1])
    assert arr.ndim is 2, arr.shape
    if dtype: assert arr.dtype == dtype, (arr.dtype, dtype)
    if contiguous: assert arr.flags.contiguous is True, arr.flags
    return arr



if 1: ######## simd

  def bit2bool(arr):
    assert arr.dtype == uint8, arr.dtype
    out = empty(8 * arr.size, dtype = uint8)
    return """int i; uint x;
    for (const void *N = arr + n; arr != N; arr++)
    for (i = 0, *out = 0, x = *arr; i < 8; i++, out++, x >>= 1) *out = x & 1;""" ..inline(arr = arr, out = out, n = arr.size)["out"]

  ## inplace O(log 64) 64bit bitreverse
  def bitreverse64_(arr):
    assert isinstance(arr, ndarray), type(arr)
    assert arr.dtype == int64, arr.dtype
    return """for (const void *N = x + n; x != N; x++) {
    *x = ((*x & 0xaaaaaaaaaaaaaaaaLLU) >> 1) | ((*x & 0x5555555555555555LLU) << 1); // stride 1
    *x = ((*x & 0xccccccccccccccccLLU) >> 2) | ((*x & 0x3333333333333333LLU) << 2); // stride 2
    *x = ((*x & 0xf0f0f0f0f0f0f0f0LLU) >> 4) | ((*x & 0x0f0f0f0f0f0f0f0fLLU) << 4); // stride 4
    *x = ((*x & 0xff00ff00ff00ff00LLU) >> 8) | ((*x & 0x00ff00ff00ff00ffLLU) << 8); // stride 8
    *x = ((*x & 0xffff0000ffff0000LLU) >> 16) | ((*x & 0x0000ffff0000ffffLLU) << 16); // stride 16
    *x = (*x >> 32) | (*x << 32); // stride 32
    }""" ..inline( x = arr, n = arr.size )["x"]

  ## inplace bitreverse sort
  def brsort2d_(arr): return """int i, j, pos, step;
    const int Ni = Narr[0];
    const int Nj = Narr[1];
    const int Nij = Ni * Nj;
    const int n2 = Nj >> 1;

    pos = 0;
    for (arr++, j = 1; j < Nj - 1; j++, arr++){
      step = n2;
      while(pos >= step) {pos -= step; step >>= 1;}
      pos += step; step = pos - j;

      if(step > 0) {
        for (i = 0; i < Ni; i++, arr += Nj) {
          *tmp = *arr; *arr = arr[step]; arr[step] = *tmp;}
        arr -= Nij;}}""" ..inline( arr = as2d(arr), tmp = arrp(arr) )["arr"]

  ## inplace b/w img dither - floyd steinberg method
  def dither_(arr):
    assert isint(arr), arr.dtype
    assert arr.ndim == 2, arr.shape
    max = arr.max(); assert max >= 0, max
    return """int i, j; unsigned char *x1, *x2, *x3, *x4, old, err;
    const int Ni = Nx0[0];
    const int Nj = Nx0[1];

    x1 = x0 + 1;
    x2 = x0 + Nj - 1;
    x3 = x2 + 1;
    x4 = x3 + 1;
    for (i = 1; i < Ni; i++) {
      x0++; x1++; x2++; x3++; x4++; // skip 1st column - bdd
      for (j = 1; j < Nj; j++, x0++, x1++, x2++, x3++, x4++) {
        old = *x0;
        *x0 = *x0 < cutoff ? 0 : 1;
        err = old - *x0;
        *x0 ^= 1; // BUG - fix pixel inversion                                       - - -
        *x1 += (7 * err + 8) >> 4; *x2 += (3 * err + 8) >> 4; // floyd steinberg cff - - 7
        *x3 += (5 * err + 8) >> 4; *x4 += (    err + 8) >> 4; //                     3 5 1
        }}""" ..inline(x0 = arr, cutoff = int((max >> 1) + 1))["x0"]

  def dot2d(arr, x):
    arr = as2d(arr); x = as2d(x); assert arr.dtype == x.dtype, dtypes(arr, x)
    if len(x) <= 1:               assert arr.shape[1] == x.shape[1], shapes(arr, x); dx = x.shape[1]
    else:                         assert arr.shape == x.shape, shapes(arr, x); dx = 0
    return """int i, j;
    const int Ni = Narr[0];
    const int Nj = Narr[1];
    for (          i = 0; i < Ni; i++, out++, x -= dx)
    for (*out = 0, j = 0; j < Nj; j++, arr++, x++) *out += *arr * *x;""" ..inline( arr = arr, x = x, dx = dx, out = len(arr) ..empty(dtype = arr.dtype) )["out"]

  ## BUG - fails for nan
  def find2d(arr, x):
    arr = as2d(arr); x = ravel(x); assert arr.dtype == x.dtype, dtypes(arr, x)
    narr, nx = lens(arr, x);       assert narr == nx or narr == 1 or nx == 1, shapes(arr, x)
    return len(arr) ..arange(), """int i, j;
    const int Ni = Nout[0];
    const int Nj = Narr[1];
    for (i = 0; i < Ni; i++, *out = j, arr += darr - j, x += dx, out++)
    for (j = 0; j < Nj; j++, arr++) if (*arr == *x) break;""" ..inline(
      arr = arr, darr = 0 if narr == 1 else arr.shape[1],
      x   = x  , dx   = 0 if nx   == 1 else 1,
      out = max(narr, nx) ..empty(dtype = int) )["out"]

  def histogram2d(arr):
    arr = as2d(arr); assert isint(arr), arr.dtype
    n = arr.max() + 1; out = (len(arr), n) ..zeros(dtype = int)
    assert 0 <= arr.min() <= n < 0x10000, (arr.shape, arr.min(), n)
    return """int i,j;
    const int Ni = Narr[0];
    const int Nj = Narr[1];
    const int Nout1 = Nout[1];
    for (i = 0; i < Ni; i++, out += Nout1)
    for (j = 0; j < Nj; j++, out[*arr]++, arr++);""" ..inline( arr = arr, out = out )["out"]

  ## 1st order y-value interpolation
  def itp2d(y0, t0, t):
    assert double == y0.dtype == t0.dtype == t.dtype, dtypes(y0, t0, t) ## check type
    assert all(t0[:-1] < t0[1:]), t0 ## t-axis strictly increasing
    assert t0.min() <= t.min() and t.max() <= t0.max(), (t0, t)
    y0 = as2d(y0); assert y0.shape[1] == t0.size, shapes(y0, t0, t) ## check shape
    return """int i, j; double dt;
    const int Ni = Ny0[0];
    const int Nj = Ny0[1];
    const int Nk = Nt[0];
    const int Nij = Ni * Nj;
    const int Nik = Ni * Nk;
    const void *tff = t + Nk;

    for (; *t0 <= *t; y0++, t0++); // find starting t0 point
    for (j = 1; j < Nj; j++, y0++, t0++) { // t0 loop

      for (i = 0; i < Ni; // df simd loop
        *df = (*y0 - y0[-1]) / (*t0 - t0[-1]), // calculate df
        i++, df++, y0 += Nj);
      df -= Ni; y0 -= Nij; // reset simd

      for (; (t != tff) && (*t <= *t0); y++, t++) { // t loop
        for (dt = *t - *t0, i = 0; i < Ni; // y simd loop
          *y = *y0 + *df * dt, // interpolate y
          i++, df++, y0 += Nj, y += Nk);
        df -= Ni; y0 -= Nij; y -= Nik; // reset simd
      }}""" ..inline( y0 = y0, t0 = t0, y = (len(y0), t.size) ..empty(), t = t, df = len(y0) ..empty() )["y"]

  def map2d(f, arr, binsize, **kwds):
    bin = arange(0, len(arr), step = binsize, dtype = int); bin = r_[bin, len(arr)]; out = collections.deque()
    for i, (a, b) in zip(bin[:-1], bin[1:]) ..enumerate(): print( "map2d %s %i %i-%i" % (f, i, a, b) ); ar = f(arr[a:b], **kwds); out.append(ar)
    return vstack(out)

  def nanmean2d(arr): arr = as2d(arr); return 1 / (arr.shape[1] - isnan(arr).sum(axis = 1)) * nansum(arr, axis = 1)

  ## inplace O(log 64) 64bit population counter
  def popcount64_(arr):
    assert isinstance(arr, ndarray), type(arr)
    assert isint(arr), arr.dtype
    return """for (const void *N = x + n; x != N; x++) {
    *x =  *x - ((*x >> 1) & 0x5555555555555555LLU); // count 2 bits
    *x =       ((*x >> 2) & 0x3333333333333333LLU) + (*x & 0x3333333333333333LLU); // count 4 bits
    *x = ((*x >> 4) + *x) & 0x0f0f0f0f0f0f0f0fLLU ; // count 8 bits
    *x += *x >> 8 ; // count 16 bits
    *x += *x >> 16; // count 32 bits
    *x += *x >> 32; // count 64 bits
    *x &= 127;
    }""" ..inline( x = arr, n = arr.size )["x"]

  ## O(n) integer power arr
  def powrange2d(arr, n):
    assert n >= 1, n; arr = ravel(arr); exp = (len(arr), n) ..empty(dtype = arr.dtype); exp[:, 0] = 1
    if n <= 1: return exp
    return """int i, j;
    const int Ni = Nexp[0];
    const int Nj = Nexp[1];
    const int Nj2 = Nj >> 1;
    const int Nj3 = Nj - Nj2;
    for (i = 0; i < Ni ; i++, arr++, exp += Nj3) // simd loop
    for (j = 0; j < Nj2; j++, exp++) {exp[j] = *exp * *exp; exp[j + 1] = exp[j] * *arr;} // O(n) exp loop
    if (Nj & 1) for (exp -= Nj3, i = 0; i < Ni; i++, exp -= Nj) exp[j] = *exp * *exp; // endpt simd loop""" ..inline( arr = arr, exp = exp )["exp"]

  ## space efficient shallow dot - Nbase.Nx -> Nbase
  def powrangedot2d(base, x):
    x = as2d(x); base = ravel(base)
    assert base.dtype == x.dtype, dtypes(base, x) ## check type
    assert len(base) == len(x) or 1 in lens(base, x) ## check shape
    dx = x.shape[1] if len(base) == len(x) else 0
    exp = empty(x.shape[1], dtype = base.dtype); exp[0] = 1
    return """int i, j;
    const int Ni = Nbase[0];
    const int Nj = Nx[1];
    const int Nj2 = Nj >> 1;
    for (          i = 0; i < Ni ; i++, base++, exp -= Nj2, x += dx - Nj2, dot++) { // simd loop
    for (*dot = 0, j = 0; j < Nj2; j++, exp++, x++) { // O(n) exp & dot loop
    exp[j] =   *exp * *exp ; exp[j + 1] = exp[j] * *base; // exp
    *dot  += exp[j] * x[j] + exp[j + 1] * x[j + 1];} // dot
    if (Nj & 1) *dot += *exp * *exp * x[j];} // endpt""" ..inline( base = base, exp = exp, x = x, dx = dx, dot = len(base) ..empty(dtype = base.dtype) )["dot"]

  ## space efficient full dot - Nbase.Nx -> Nx*Nbase - overwrite target arr if specified
  def powrangedot_(base, x, dot = None):
    assert base.dtype == x.dtype, dtypes(base, x) ## check type
    base = ravel(base); x = as2d(x)
    if dot is None: dot = (len(x), len(base)) ..empty(dtype = base.dtype)
    else:
      assert base.dtype == dot.dtype ## check type
      assert (len(x), len(base)) == dot.shape, shapes(x, base, dot) ## check shape
    exp = empty(x.shape[1], dtype = base.dtype); exp[0] = 1
    return """int i, j, k;
    const int Ni = Nbase[0];
    const int Nj = Nx[0];
    const int Nk = Nx[1];
    const int Nij = Ni * Nj - 1;
    const int Njk = Nj * Nk;
    const int Nk2 = Nk >> 1;
    for (i = 0; i < Ni; i++, base++, x -= Njk, dot -= Nij) { // base loop
    for (k = 0; k < Nk2; k++, exp++) {exp[k] = *exp * *exp; exp[k + 1] = exp[k] * *base;} // exp loop
    if (Nk & 1) exp[k] = *exp * *exp; // endpt
    exp -= Nk2;
    for (          j = 0; j < Nj; j++, dot += Ni, exp -= Nk) // simd loop
    for (*dot = 0, k = 0; k < Nk; k++, x++, exp++) *dot += *x * *exp;} // dot loop""" ..inline(base = base, exp = exp, x = x, dot = dot)["dot"]

  ## inplace reverse sort
  def reverse2d_(arr):
    return """int i, j;
    const int Ni = Narr[0];
    const int Nj = Narr[1];
    const int Nj2 = Nj >> 1;
    for (                    i = 0; i < Ni ; i++, arr += Nj - j)
    for (end = arr + Nj - 1, j = 0; j < Nj2; j++, arr++, end--) {
    *tmp = *arr; *arr = *end; *end = *tmp;}""" ..inline( arr = as2d(arr), end = arr, tmp = arrp(x) )["arr"]



######## img2txt
class _img2txt(object):

  if 1: ## internal vars
    BUFFER = empty(0, dtype = int64) ## internal buffer for outputting txt
    CLRBUF = empty(0, dtype = int64) ## internal color buffer for outputting txt
    LUCIDA = "AAAAAAAAAAAAQRAEARAAAIqiAAAAAAAAAEX5ylcUAACEVxwMRT0EAIBYKQylRgAAAKE4Zpt5AAAE\nQQAAAAAAADBCEARBIDAAA4EgCIIQAwAAsRkKAAAAAAAAEMRHEAAAAAAAAMAwCAEAAAAeAAAAAAAA\nAADAMAAAIAQhDCEIAQCAE0VRFDkAAIBREARBfAAAgANBCCF4AACAB0EMBDkAAADCKMmHIAAAgCcI\nDgQ5AAAAJwTNFDkAAIAHIQQhCAAAgBMlThQ5AACAE0UehBwAAAAAMAzAMAAAAAAwDMAwCAEAAEDM\nwEAAAAAAAD / wAwAAAAAEBmYEAACAJ0EIARAAAIAXdVUfeAAAAMMokieFAADAE0VPFD0AAAAnBEEg\ncAAAwBNFURQ9AACAJwiOIHgAAIAnCI4gCAAAACcEWSRxAABAFEVfFEUAAMBHEARBfAAAgIMgCIIY\nAABAlBRDkUQAAIAgCIIgeAAAQLRtV1VFAABANF1VlkUAAIATRVEUOQAAwBNFTxAEAACAE0VRFDkw\nAMCRJEeRRAAAACcIDAQ5AADARxAEQRAAAEAURVEUOQAAQBhJksIQAABAVFXVoygAAEAoMQgjhQAA\nQKQoBEEQAADAByGEEHwAABxBEARBEBwAgSAQBAJBIAAOgiAIgiAOAABBKIoSAQAAAAAAAAAAPwAE\nAgAAAAAAAAAAOBAn+QAAQRA0UxQ9AAAAAHhBEHgAABAEeVGUWQAAAAA40Rd4AAAYQXgEQRAAAAAA\neFGUWZADQRB0UxRFAAAIADgIgiAAAAgAOAiCIMgBgiBIiqFIAAAHQRAEQRAAAAAAfFVVVQAAAAB0\nUxRFAAAAADhRFDkAAAAANFMUPUEAAAB4UZRZEAQAAGiWIAgAAAAAcAIDOQAAAEF4BEFgAAAAAERR\nlF0AAAAARIqiEAAAAACUbStJAAAAAEQKoUQAAAAAhJLEMMQAAAB8CCF8AAAcQRACQRAcAARBEARB\nEAQADoIgEIIgDgAAAABnDgAAAAAAAAAAAAAA\n" ## lucida console 06x10 bitmap font encoded in 64 bits - use str2font to decode

    _ = ord(" ") ## convenience var for whitespace
    fres = r_[10, 6] ## font block resolution - row * col
    blockff = bitshiftl64(1, fres.prod()) - 1 ## 64bit saturated block mask for various img processing
    blockbit = fres.prod() ..arange() ...bitshiftl64(1) ## 64bit single bit masks for filling blocks w/ data

  if 1: ## ansi 6*6*6 rgb map
    ansi666 = asarray(
      ("\33[38;5;%im%c\33[0m" % (i, c), "\33[38;5;%i;7m%c\33[0m" % (i, c)) ## foreground & background
      for i in range(16, 16 + 6 * 6 * 6) ## 6*6*6 rgb
      for c in range(128) ## 128 character
      ).reshape(6*6*6, 128, 2).transpose(0, 2, 1).ravel()

  if 1: ## gif 6*6*6 rgb palette
    palette666x3 = zeros((6, 6, 6, 3), dtype = uint8); x = linspace(0, 255, 6).astype(uint8)
    palette666x3[..., 0] |= x[:, newaxis, newaxis]
    palette666x3[..., 1] |= x[:, newaxis]
    palette666x3[..., 2] |= x

  if 0 and DEBUG:
    print( ansi666[256:768] ..sjoin() )
    print( sjoin(rgb) )

  ## print block in row, col format - for debugging
  def printd(self, arr):
    if isinstance(arr, int64): arr = (arr & bitshiftl64(1, i) for i in range(self.fres.prod())) ..asarray(dtype = bool).reshape(self.fres) ## convert 64bit word to arr
    for x in arr[:-1]: sjoin(int(x) ..str() if x else "." for x in x) ..print() ## print each line of block
    sjoin(int(x) ..str() if x else "_" for x in arr[-1]) ..print() ## delimit last line w/ "_"

  ## internal fnc for importing font bitmaps
  def importfont(self, fname):
    from PIL import Image; fres = self.fres
    img = Image.open(fname); img = img.tostring() ..fromstring(dtype = uint8).reshape(img.size[::-1])
    font = prod(img.shape // self.fres) ..zeros(dtype = int64) ...self.bmp2block_(img)
    if 1 and DEBUG:
      for x in font[1:1 + 4]: self.printd(x); print()
    return font

  def font2str(self, font): import base64; return font.tostring() ..base64.encodestring()

  def str2font(self, s): import base64; return base64.decodestring(s) ..fromstring(dtype = int64)

  def __init__(self, plaintxt = True):
    self.plaintxt = plaintxt; fres = self.fres

    arr = self.str2font(self.LUCIDA); arr = arr[..., newaxis].repeat(5, axis = -1) ## original
    arr[..., 1] >>= fres[1] ## shift up
    arr[..., 2] <<= fres[1] ## shift down
    cll = 1 ..bitshiftl64(arange(0, fres.prod(), fres[1], dtype = int64)) ..sum() ^ self.blockff ## cll left boundary
    x = arr[..., 3]; x &= cll; x >>= 1 ## shift left
    x = arr[..., 4]; x <<= 1; x &= cll ## shift right
    if 0 and DEBUG:
      for x in arr[17, :5]: self.printd(x)

    self.fbmp0 = fbmp0 = zeros(128, arr.dtype); fbmp0[-len(arr):] = arr[:, 0] ## needed for gif output
    fbmp = arr ## bmp of font
    ford = arange(32, 128); assert len(ford) == len(fbmp) ## bmp -> ord mapping
    fpop = popcount64_(fbmp[:, 0].copy()) ..asarray(dtype = int) ## bmp popcount

    if not plaintxt: ## include inverted color
      fbmp = (fbmp, fbmp ^ self.blockff) ..vstack()
      ford = r_[ford, ford + 128]; fpop = r_[fpop, fres.prod() - fpop]
      fpop[-1] = 0 ## redundant fres.prod()

    cll = fpop.astype(bool); cll[0] = True
    fbmp, ford, fpop = (x[cll] for x in (fbmp, ford, fpop))

    cll = fpop.argsort() ## sort by population count
    fbmp, ford, fpop = (x[cll] for x in (fbmp, ford, fpop))
    self.level = level = 255 / fres.prod() * fpop.mean()

    if 1: ## place font blocks in overlapping bins by popcount
      hst = asarray(list(x) for x in histogram2d(fpop)[0] ..enumerate() if x[1]) ## cll whitespace in histogram

      bin = [0]; i = n = 0
      for a, b in hst[1:]:
        if n < 16: n += b ## binsize
        else: bin.append(a); n = b
      bin = r_[ 0, bin[:-1], [fres.prod() + 1] * 2 ] ## prepend / append endpt

      fbin = (bin[1:-2], bin[2:-1]) ..transpose() ## create bins w/ endpt removed
      fbin[0, 0] = 1 ## ignore whitespace

      a = zip(bin[0::3], bin[3::3])
      b = zip(bin[1::3], bin[4::3])
      c = zip(bin[2::3], bin[5::3])
      fmap = zip_longest(a, b, c) ..flatten() ..tuple() ## overlap
      if None in fmap: fmap = fmap[:fmap.index(None)] ## remove None from zip_longest
      fmap = (-1, 2) ...reshape(fmap).T.ravel() ...find2d(fpop)[1].reshape(2, -1).T ## map font blocks to bin by popcount
      assert len(fmap) == len(fbin)

      if 0 and DEBUG:
        print( "level", level )
        print( "fpop", fpop )
        print( "hst", hst )
        print( "fbin", fbin )
        print( "fmap", fmap )

      fmap = [(a, fbmp[a:b]) for a, b in fmap] ## font blocks grouped by popcount placed in overlapping bins

    chrmap = [chr(x) for x in range(128)] ## chrmap
    self.chrmap = chrmap = asarray(chrmap)
    if 0 and DEBUG: print( chrmap[ford] ..sjoin() ) ## print chrmap in ascending density

    self.fbmp0 = fbmp0; self.fbmp = fbmp; self.ford = ford; self.fpop = fpop; self.fbin = fbin; self.fmap = fmap

  ## take pixel data from 64bit blocks and write to specified bmp
  def block2bmp_(self, block, bmp, rgbi):
    assert isint(bmp), bmp.dtype
    assert block.dtype == int64, block.dtype
    fres = self.fres; res, x = divmod(bmp.shape, fres)
    assert not x.any(), (bmp.shape, fres) ## check bmp shape
    assert res.prod() == block.size, (res, block.size) ## check block shape
    assert bmp.dtype == rgbi.dtype, dtypes(bmp, rgbi)
    assert block.size == rgbi.size, shapes(block, rgbi) ## check rgbi shape
    return """int R, C, i, j, k;
    const int ROW = res[0];
    const int COL = res[1];
    const int FROW = fres[0];
    const int FCOL = fres[1];

    for (R = 0; R < ROW ; R++, bit -= FROW * FCOL, block += COL, rgbi += COL) // BLOCKS row loop
    for (i = 0; i < FROW; i++, bit += FCOL) // font block row loop
    for (C = 0; C < COL ; C++) // BLOCKS col loop
    for (j = 0; j < FCOL; j++, bmp++) // font block col loop
    if (block[C] & bit[j]) *bmp = rgbi[C];""" ..inline(block = block, bmp = bmp, rgbi = rgbi, res = res, fres = fres, bit = self.blockbit)["block"]

  ## group and write pixel data into specified 64bit blocks
  def bmp2block_(self, bmp, block):
    assert block.dtype == int64, block.dtype
    fres = self.fres; res, x = divmod(bmp.shape, fres)
    assert not x.any(), (bmp.shape, fres) ## check bmp shape
    assert res.prod() == block.size, (res, block.size) ## check block shape
    return """int R, C, i, j, k;
    const int ROW = res[0];
    const int COL = res[1];
    const int FROW = fres[0];
    const int FCOL = fres[1];

    for (R = 0; R < ROW ; R++, bit -= FROW * FCOL, block += COL) // BLOCKS row loop
    for (i = 0; i < FROW; i++, bit += FCOL) // font block row loop
    for (C = 0; C < COL ; C++) // BLOCKS col loop
    for (j = 0; j < FCOL; j++, bmp++) // font block col loop
    if (*bmp) block[C] |= bit[j];""" ..inline(bmp = bmp, block = block, res = res, fres = fres, bit = self.blockbit)["block"]

  ## fill BUFFER w/ bmp data - grouped into 64bit blocks
  def fill(self, arr):
    fres = self.fres; self.res = res = divceil(arr.shape, fres) ## res
    if not all(arr.shape // fres == res): x = arr; arr = zeros(res * fres, dtype = arr.dtype); arr[:x.shape[0], :x.shape[1]] = x ## resize canvas
    if len(self.BUFFER) != res.prod(): self.BUFFER = empty(res.prod(), dtype = int64) ## resize BUFFER
    BUFFER = self.BUFFER; BUFFER.fill(0) ## clear BUFFER
    self.bmp2block_(arr, BUFFER) ## BUFFER |= font block bits
    return self

  ## main algorithm - interpolate block -> ascii chr
  def itp(self, wmatch = 1, wmismatch = 2):
    BUFFER = self.BUFFER; self.pop = pop = popcount64_(BUFFER.copy()); wgt = empty(5, dtype = int64)
    for (a, b), (c, f) in zip(self.fbin, self.fmap): """long long *buf, i, j, x, wmax, wmaxi;
      const int Ni = Nf[0];
      const int Nj = Nf[1];
      const int Nij = Ni * Nj;

      for (const void *N = BUFFER + NBUFFER[0]; BUFFER != N; BUFFER++, pop++) // bin loop
      if (a <= *pop && *pop < b) { // popcount within bin limits

      for(i = 0, wmax = -0x8000000000000000LLU; i < Ni; i++) { // font block loop
        for(j = 0; j < Nj; j++, f++, wgt++) { // font shift loop

          x = *BUFFER & *f; // match
          x =  x - ((x >> 1) & 0x5555555555555555LLU); // count 2 bits
          x =      ((x >> 2) & 0x3333333333333333LLU) + (x & 0x3333333333333333LLU); // count 4 bits
          x = ((x >> 4) + x) & 0x0f0f0f0f0f0f0f0fLLU ; // count 8 bits
          x += x >> 8 ; // count 16 bits
          x += x >> 16; // count 32 bits
          x += x >> 32; // count 64 bits
          x &= 127; *wgt = x;} wgt -= Nj;

        *wgt *= wmatch; // weight original match

        x = *BUFFER ^ f[-Nj]; // mismatch
        x =  x - ((x >> 1) & 0x5555555555555555LLU); // count 2 bits
        x =      ((x >> 2) & 0x3333333333333333LLU) + (x & 0x3333333333333333LLU); // count 4 bits
        x = ((x >> 4) + x) & 0x0f0f0f0f0f0f0f0fLLU ; // count 8 bits
        x += x >> 8 ; // count 16 bits
        x += x >> 16; // count 32 bits
        x += x >> 32; // count 64 bits
        x &= 127;

        *wgt -= x * wmismatch; // weight original mismatch

        for (j = 1; j < Nj; j++) *wgt += wgt[j]; // sum weights

        if (*wgt > wmax) {wmax = *wgt; wmaxi = i;} // pick highest weight & corresponding index

        } f -= Nij;

      *BUFFER = ford[wmaxi + c]; // assign optimal font block by weight
      }""" ..inline(
        BUFFER = BUFFER, pop = pop, a = int(a), b = int(b), c = int(c), f = f, ford = self.ford,
        wgt = wgt, wmatch = wmatch, wmismatch = wmismatch,
        )
    BUFFER[BUFFER == 0] = self._; return self

  ## itp -> str
  def tostr(self):
    if self.plaintxt or self.CLRBUF is None: return "\n".join(self.chrmap[x] ..sjoin() for x in self.BUFFER.reshape(self.res))
    BUFFER = self.BUFFER | (self.CLRBUF ..asarray(dtype = uint16) << 8)
    return "\n".join(self.ansi666[x] ..sjoin() for x in BUFFER.reshape(self.res))

  ## autofill s to self.res
  def str2arr(self, s, gray = 172):
    res = self.res; lines = []
    for s in s.replace("\x00\n", "\x00\xff").split("\n"): ## "\x00\n" is possible ansi color code
      if not s: lines.append("") ## empty line
      else:
        s = s.replace("\xff", "\n") ## restore ansi color code
        while s: s[:res[1]] ..lines.append(); s = s[res[1]:] ## break long line into multiple lines

    BUFFER = (len(lines), res[1]) ..empty(dtype = self.BUFFER.dtype); BUFFER.fill(self._) ## resize BUFFER
    CLRBUF = BUFFER.shape         ..empty(dtype = self.CLRBUF.dtype); CLRBUF.fill(gray)   ## resize CLRBUF

    for line, buf, clr in zip(lines, BUFFER, CLRBUF):
      if "\x00" in line: ## color txt - e.g. <white a> is "\x00\xd7a"
        arr = line.split("\x00")
        c, s = asarray((x[0], x[1:]) for x in arr[1:]).T; arr[1:] = s ## extract rgb info from line
        ci = lens(*arr[:-1]) ..cumsum() ## get CLRBUF position
        clr[ci] = [ord(x) for x in c] ## convert chr -> 6*6*6 rgb ord, & write to CLRBUF
        line = sjoin(arr) ## join line sans rgb info
      buf[:len(line)] = [ord(x) for x in line]

    return ravel(BUFFER), ravel(CLRBUF)

  def header(self, s, _footer = None):
    res = self.res
    BUFFER, CLRBUF = self.str2arr(s)
    self.BUFFER = BUFFER = (BUFFER, self.BUFFER)[::-1 if _footer else 1] ..concatenate()
    self.CLRBUF = CLRBUF = (CLRBUF, self.CLRBUF)[::-1 if _footer else 1] ..concatenate()
    self.res = res = r_[len(BUFFER) // res[1], res[1]]
    return self

  def footer(self, s): return self.header(s, _footer = True)

  ## itp -> gif file
  def togif(self, fname):
    if fname[-4:] not in (".gif", ".GIF"): raise ValueError("PIL bug - use filename '%s.gif' instead of %r" % (fname, fname))
    block = self.fbmp0[self.BUFFER & 127]
    block[self.BUFFER > 127] ^= -1 ## background
    bmp = (self.res * self.fres) ..zeros(dtype = uint8)
    self.block2bmp_(block, bmp, self.CLRBUF) ## rasterize font

    from PIL import Image
    img = Image.fromstring("P", bmp.shape[::-1], bmp.tostring()) ## create gif img from bmp
    self.palette666x3.ravel() ..img.putpalette() ## add 6*6*6, 3 channel rgb palette info
    img.save(fname) ## save img to file

  ## img -> itp
  def load(self, fname, invert = None, scale = 1, autolevel = True, togif = "", **kwds): ## must be a file or filename
    from PIL import Image; img = Image.open(fname) ## import img

    if scale != 1: img = img.resize(scale * r_[img.size]) ## scale image
    arr = img if img.mode == "L" else img.convert("L").tostring() ..fromstring(dtype = uint8).reshape(img.size[::-1])
    if invert: arr ^= -1 ## invert gray

    # gray = img.convert("L"); arr = gray.getdata() ..asarray(dtype = uint8) ## auto-level
    # if invert: arr ^= -1
    if autolevel:
      x = arr.mean(); level = self.level

      cll = arr <= x; x = arr[cll]; x -= x.min(); x *= level / (x.max() or 1); arr[cll] = x ## <= mean
      cll = cll ^ True; x = arr[cll]; x -= x.min(); x *= (255 - level) / (x.max() or 1); x += level; arr[cll] = x ## > mean
      # gray.putdata(arr)
    # arr = gray.convert("1").getdata() ..asarray(dtype = bool).reshape(res[::-1]) ## dither


    arr = dither_(arr) ## dither 8bit gray -> 1bit b/w
    self.res = divceil(img.size[::-1], self.fres) ## save res
    self.fill(arr).itp(**kwds) ## itp

    if not self.plaintxt and img.mode in ("CYMK", "P", "RGB"):
      CLRBUF = (img if img.mode == "RGB" else img.convert("RGB")).resize(self.res[::-1]).tostring() ..fromstring(dtype = uint8).reshape(-1, 3) ## rgb img -> rgb arr
      if invert: CLRBUF ^= -1 ## invert rgb
      CLRBUF *= 6 / 256; self.CLRBUF = CLRBUF = r_[36, 6, 1].astype(uint8) ...dot(CLRBUF) ## 24bit rgb -> 6*6*6 rgb
      CLRBUF[(CLRBUF == 0) & (self.BUFFER != self._)] = 1 ## paint darkest non-empty pixel blue instead of invisible black
    else: self.CLRBUF = CLRBUF = None
    if togif: self.togif(togif)
    return self

  ## main fnc
  def __call__(self, *args, **kwds): return self.load(*args, **kwds).tostr()

  def test(self, fname = None, scale = 2.0, **kwds):
    if not fname: fname = imp.find_module("asciiporn")[1] + "/" + "mario.gif"
    txt = self(fname, scale = scale, **kwds)
    print( txt )

img2plaintxt = _img2txt(plaintxt = True) ## creates portable plain txt img

img2txt = _img2txt(plaintxt = None) ## creates colorized txt img for display in terminals (xterm, putty, ...)



######## (z, y, t) datapoint storage object
class dataZYT(asarray):

  def __new__(self, yt = None, z = None, y = None, t = None, zmin = None, zmax = None, ymin = None, ymax = None, tmin = None, tmax = None, zn = 64, yn = 64, tn = 256, ft = None, ftz = None):
    yt = [] if (yt is None or not len(yt)) else [yt] if not ndim(yt[0]) else list(yt) ## yt

    if 1: ## y
      y = [] if (y is None or not len(y)) else [y] if not ndim(y[0]) else list(y)

      if t is None:
        if y: t = len(y[0]) ..arange()
        else: t = linspace(tmin, tmax, tn)

      if ft is not None: ## ft
        if not iterable(ft): ft = [ft]
        y += [[ft(_t) for _t in t] for ft in ft]

      if ftz is not None: ## ftz
        if z is None: z = linspace(0 if zmin is None else zmin, zn - 1 if zmax is None else zmax, zn)
        y += [[ftz(_t, _z) for _t in t] for _z in z]

      if y:
        assert shape(y)[-1] == len(t), shapes(y, t) ## check shape
        yt += [transpose((x, t)) for x in as2d(y)]

    if not len(yt):     raise ValueError("%r cant instantiate empty <%r>" % (self, yt)) ## err - size
    try: ## if yt is arr
      yt = array(yt, dtype = double) ## copy
      yt = r_[1, -1, yt.shape[-2:]][-3:] ..yt.reshape() ## dim = 3
    except: ## else coerce to arr
      yt = [as2d(x) for x in yt]; n = max(len(x) for x in yt) ## 1st order flatten
      for i, x in enumerate(yt): ## make equal lens
        if len(x) < n: yt[i] = len(x) ...divceil(n) ...repeat(x[newaxis], axis = 0) .reshape(-1, 2)[:n]

    self = asarray.__new__(self, yt, dtype = double) ## create self
    if isinf(self).any(): raise ValueError("<%.256r...> contain inf" % self) ## err - inf
    if isnan(self).any(): raise ValueError("<%.256r...> contain nan" % self) ## err - nan

    self.z = z = len(self) ..arange(dtype = double) if z is None else asarray(z, dtype = double)
    self.sorted = None

    if not None is ymin is ymax is tmin is tmax:
      y, t = self.reshape(-1, 2).T
      if tmin is not None: cll = t < tmin; y0 = y[cll ^ True][0]; y[cll] = y0; t[cll] = tmin
      if tmax is not None: cll = t > tmax; y0 = y[cll ^ True][-1]; y[cll] = y0; t[cll] = tmax
      if ymin is not None: y[y < ymin] = ymin
      if ymax is not None: y[y > ymax] = ymax
    return self

  def analyze(self):
    self.minmax = minmax = [(x.min(), x.max()) for x in self.T] ..transpose() ## self.minmax
    if minmax[0, 0] == minmax[1, 0]: raise ValueError("<%.256r...> is horizontal line y = %s" % (self, minmax[0, 0]))
    if minmax[0, 1] == minmax[1, 1]: raise ValueError("<%.256r...> is vertical line t = %s" % (self, minmax[0, 1]))

    for yt in self: ## self.sorted
      y, t = yt.T
      if any(t[:-1] > t[1:]): yt[:] = yt[t.argsort()] ## sort t-axis
    self.sorted = True

    self.origin = origin = [0.0 if a <= 0 <= b else a if 0 < a else b for a, b in minmax.T] ..asarray() ## self.origin

    extrema = []; y = self[..., 0].copy() ## self.extrema
    for ye in y.min(axis = 1), y.max(axis = 1): cll = find2d(y, ye); te = self[cll[0], cll[1], 1]; (ye, te) ..extrema.append() ## find2d global min/max
    self.extrema = extrema = (2, 0, 1) ...transpose(extrema); return self

  ## normalize data points
  def norm(self, arr = None):
    a, b = self.minmax; assert not any(a == b)
    if arr is None: arr = self
    arr = array(arr, dtype = double); assert arr.size, arr ## copy arr for mutation
    arr = r_[1, -1, arr.shape][-3:] ..arr.reshape(); arr -= a; arr *= 1 / (b - a) ## norm
    n = linspace(0, 1, len(arr)).repeat(arr.shape[1]).reshape(r_[arr.shape[:-1], 1])
    return (n, arr) ..concatenate(axis = -1) ## pair y, t -> triplet i, y, t

  ## find y roots
  def roots(self):
    if not self.minmax[0, 0] <= 0 <= self.minmax[1, 0]: return [] ## no zero crossing
    assert self.sorted; roots = []
    for i, yt in enumerate(self):
      y, t  = yt.T; dy, dt = (yt[1:] - yt[:-1]).T; sy = sign(y)
      cll = sy[1:] != sy[:-1]; cll &= dy != 0 ## y sign change
      cll &= dt != 0 ## unique t
      t0 = t[cll] - y[cll] * dt[cll] / dy[cll]; assert not isnan(t0).any(), t0; roots.append(t0) ## newtons method
    return roots



######## general plotter
class _plot(_img2txt):

  redi, greeni, bluei = 36, 6, 1 ## rgbi
  gradienti = [
    (int(a), int(b), int(c)) for a, b, c in """000
001 010 100 011 101 110 111
112 121 211 122 212 221 222
223 232 322 233 323 332 333
334 343 433 344 434 443 444
445 454 544 455 545 554 555""".replace("\n", " ").split(" ")
    ] ..dot((greeni, redi, bluei))

  block = 160 ## plot solid block
  colori0 = gradienti[1:] ## plot color
  boxi = redi + greeni + 5 * bluei ## box color
  gridi = 2 * bluei ## grid color
  rooti = 5 * redi ## root color
  vlinei = 5 * redi + 5 * greeni ## vertical line color

  def __call__(self, replot = None, itp = True, yres = None, xres = None, vline = None, **kwds):
    if replot: data = self.data; norm = self.norm
    else: self.data = data = dataZYT(**kwds).analyze(); self.norm = norm = data.norm()

    if yres is None: yres = YRES ## default to global YRES
    self.res = res = screensize() ..asarray(); res[0] *= yres ## res
    if isint(yres): res[0] = yres ## integer xres
    if isint(xres): res[1] = xres ## integer yres
    if len(self.BUFFER) != res.prod(): self.BUFFER = empty(res.prod(), dtype = int64) ## resize BUFFER
    if len(self.CLRBUF) != res.prod(): self.CLRBUF = empty(res.prod(), dtype = int64) ## resize CLRBUF BUFFER
    BUFFER = self.BUFFER; CLRBUF = self.CLRBUF; BUFFER[:] = CLRBUF[:] = 0 ## reset BUFFER
    self.vline = None if vline is None else ravel(vline) ## plot vertical lines (x = ...)
    s = self.plot().header().tostr(); print( s ) ## plot to stdout

  def ytscale(self, yt, yinvert, res = None):
    yt = self.data.norm(yt).reshape(-1, 3)[:, 1:] ## normalize to 1
    if yinvert: yt[:, 0] = 1 - yt[:, 0] ## y, t -> hline, t
    yt = asarray(yt * ((res if res else self.res) - 1), dtype = int); return yt ## scale to res

  ## plot algorithm
  def plot(self):
    BUFFER = self.BUFFER; CLRBUF = self.CLRBUF; data = self.data; res = self.res; fres = self.fres
    self.colori = colori = self.colori0[linspace(0, len(self.colori0) - 1, len(data) + 1)[1:].astype(int)] ## colori

    ## connect the dots
    arr = self.norm.reshape(-1, 3); arr[..., 1] = 1 - arr[..., 1] ## norm y, t -> hline, t
    for i, yt in (arr[:, 1:] * (res * fres - 1)) .reshape(len(data), -1, 2) ..enumerate():
      if len(yt) == 0: continue
      elif len(yt) == 1: yt = yt.astype(int)
      else:
        y0, t0 = yt.T
        yt = yt[r_[True, t0[:-1] < t0[1:]]] ## t-axis strictly increasing
        y0, t0 = yt.T.copy(); t = linspace(t0[0], t0[-1], t0[-1] - t0[0] + 1)
        y = itp2d(y0, t0, t)[0]; yt = (y, t) ..asarray(dtype = int).T

      a, b = divmod(yt, fres)
      a = r_[res[1], 1] ...dot(a) ## res
      b = r_[fres[1], 1] ...dot(b) ...bitshiftl64(1) ## fres

      "for (const void *N = a + Na[0]; a != N; BUFFER[*a] |= *b, a++, b++);" ..inline( BUFFER = BUFFER, a = a, b = b ) ## draw img BUFFER
      CLRBUF[a] = colori[i] ## colorize
    self.itp(wmatch = 2, wmismatch = 1) ## itp

    o = self.ytscale(data.origin, yinvert = True).ravel(); o = (o, res - 1) ..asarray().min(axis = 0) ## origin
    cll = arange(0, len(BUFFER), res[1]) + o[1]; cll = cll[BUFFER[cll] == self._]; BUFFER[cll] = ord("|"); CLRBUF[cll] = self.rooti ## y axis
    cll = arange(res[1]) + o[0] * res[1]       ; cll = cll[BUFFER[cll] == self._]; BUFFER[cll] = ord("-"); CLRBUF[cll] = self.rooti ## t axis
    cll = arange(res[1]); cll = r_[cll, -1 - cll]; cll = cll[BUFFER[cll] == self._]; BUFFER[cll] = ord("-"); CLRBUF[cll] = self.boxi ## box
    a, b = arr = data.extrema[:, :, 0].T.copy(); x, i = find2d(arr, (a.min(), b.max())); self.mmci = mmci = colori[i] ## extrema
    y, t = self.ytscale( data.extrema[i, [0, 1]], yinvert = True ).T; x = t + o[0] * res[1]; BUFFER[x] = self.block; CLRBUF[x] = mmci

    if self.vline is not None:
      t = self.vline.repeat(2).reshape(-1, 2) ..self.ytscale(yinvert = None)[:, 1].astype(int)
      for t in t: cll = arange(0, len(BUFFER), res[1]) + t; cll = cll[BUFFER[cll] == self._]; BUFFER[cll] = ord("|"); CLRBUF[cll] = self.vlinei

    cll = linspace(0, res[1] - 1, 5)[1:-1] ..roundint()[:, newaxis] + arange(0, len(BUFFER), res[1]); cll = cll.ravel(); cll = cll[BUFFER[cll] == self._]; BUFFER[cll] = ord("|"); CLRBUF[cll] = self.gridi ## t grid
    cll = linspace(0, res[0] - 1, 5)[1:-1] ..roundint()[:, newaxis] * res[1] + arange(res[1])       ; cll = cll.ravel(); cll = cll[BUFFER[cll] == self._]; BUFFER[cll] = ord("-"); CLRBUF[cll] = self.gridi ## y grid

    return self

  ## print header info
  def header(self):
    data = self.data; mm = data.minmax; s = "SIDEVIEW Y:    Z %s to %s %s    Y %s to %s    T %s to %s    MIN MAX %s" % (
      data.z[0], data.z[-1],
      sjoin("\x00%c\xa0" % x for x in self.colori), ## y legend
      mm[0, 0], mm[1, 0], ## y range
      mm[0, 1], mm[1, 1], ## t range
      " ".join("\x00%c\xa0" % x for x in self.mmci), ## global y minmax
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
    res = self.res; BUFFER = self.BUFFER.reshape(res); CLRBUF = self.CLRBUF.reshape(res); data = self.data
    yt = self.norm.reshape(-1, 3)[:, 1:].reshape(len(data), -1, 2); y, t = yt.T; t *= res[1]; t -= 1 ## y, t
    z = linspace(0, res[0], len(yt) + 1).astype(int); z0 = -1 ## z

    for z, yt, root in zip_longest(z, yt, data.roots()):
      if z != z0:
        if z > z0 + 1: BUFFER[z0 + 1:z] = BUFFER[z0]; CLRBUF[z0 + 1:z] = CLRBUF[z0]
        if z == res[0]: break
        y0, t0 = yt.T.copy(); t = linspace(t0[0], t0[-1], t0[-1] - t0[0] + 1); y = itp2d(y0, t0, t)[0]; t = t.astype(int) ## connect the dots
        BUFFER[z, t] = self.ford[roundint(y * (len(self.ford) - 1))]
        CLRBUF[z, t] = self.colori0[roundint(y * (len(self.colori0) - 1))]
        if len(root): root = root.repeat(2).reshape(-1, 2) ..self.ytscale(yinvert = None)[:, 1]; BUFFER[z, root] = self.block; CLRBUF[z, root] = self.rooti ## plot y roots
      z0 = z
    return self

  def header(self):
    data = self.data; mm = data.minmax; s = "TOPVIEW Z:    Z %s to %s (top to bottom)    Y %s to %s %s    T %s to %s    ROOTS %s" % (
      data.z[0], data.z[-1], ## z range
      mm[0, 0], mm[1, 0], ## y range
      sjoin("\x00%c\xa0" % x for x in self.colori0), ## y legend
      mm[0, 1], mm[1, 1], ## x range
      "\x00%c\xa0" % self.rooti, ## roots
      ); _img2txt.header(self, s); return self

plot = _plot(plaintxt = None)
plotsurf = _plotsurf(plaintxt = None)
def plot3d(**kwds):
  plot(**kwds)
  plotsurf.data = plot.data; plotsurf.norm = plot.norm; plotsurf(**kwds)
plot3d.test = lambda: plot.test(plot = plot3d)



######## simd polynomial fitter
class fitpoly2d(asarray):

  def __new__(self, y = None, t = None, nth = None, cff = None):
    if cff is not None: return asarray.__new__(self, cff)
    y = as2d(y); assert y.dtype == double, y.dtype; n = y.shape[1]

    if nth == 0: return y.mean(axis = 1).reshape(-1, 1).view(self) ## nth == 0 optimization

    if t is None: t = arange(n, dtype = double)
    assert y.shape[1] == t.size, shapes(y, t)
    assert t.dtype == double, t.dtype

    if nth == 1: ## nth == 1 optimization
      return """int i; double Y, T, T2, YT, inv; const int n = Nt[0];

      for (T = 0, T2 = 0, i = 0; i < n; T += *t, T2 += *t * *t, i++, t++); // T, T2
      inv = 1 / (n * T2 - T * T); t -= n;

      for (const void *N = y + Ny[0] * Ny[1]; y != N; cff += 2, t -= n) {
      for (Y = 0, YT = 0, i = 0; i < n; Y += *y, YT += *y * *t, i++, y++, t++); // Y, YT
      *cff = inv * (T2 * Y - T * YT); cff[1] = inv * (-T * Y + n * YT); // cff
      }""" ..inline( y = y, t = t.ravel(), cff = (len(y), 2) ..empty() )["cff"].view(self)

    cff, res, rank, sing = powrange2d(t, nth + 1) ..linalg.lstsq(y.T); return cff.T.copy().view(self) ## find least squares

  def itp(self, t): return powrangedot_(t, self)

  @staticmethod
  def test(n = 64, **kwds):
    inv = 1 / n; nn = tt = arange(n, dtype = float)
    y = cos(3 * pi * inv * tt); y = array((y, y + 0.25))
    f = fitpoly2d(y = as2d(y), t = tt, nth = 3)
    z = f.itp(tt); plot(y = [y, z], t = tt, **kwds)



######## simd pwr-of-2 fft tools
class fft2d(asarray):

  def __imul__(self, x): arr = self; ndarray.__imul__(arr, x); return self

  def __new__(self, y, __dict__ = None):
    y = assert2d(y) ..asarray(dtype = complex); self = asarray.__new__(self, y)
    if __dict__: self.__dict__ = __dict__; return self ## import state
    n = y.shape[1]; ln = log2(n) ..int(); assert 1 << ln == n, y.shape ## pwr-of-2
    self.n = n; self.n2 = n >> 1; self.ln = ln; self.w = w = self.exp(); self.idx = arange(n) ..brsort2d_()[0]
    return self

  ## exp(-2j pi / (i nn))
  def exp(self, i = 1): return exp(-2j * pi / (i * self.n)) ..powrange2d(self.n)[0]

  ## failsafe O(n^2) algorithm
  def dot_(self, inv = None, w = None, out = None):
    n = self.n
    if w is None: w = self.w
    if inv: w = w.conjugate()
    if out is None: out = (len(self), len(w)) ..zeros(dtype = complex)
    assert (len(self), len(w)) == out.shape, shapes(self, w, out)
    exp = empty(n, dtype = complex); exp[0] = 1
    """int i, j, k;
    const int Ni = Nself[0];
    const int Nj = Nself[1];
    const int Nk = Nout[1];
    const int Nj2 = Nj >> 1;
    for (k = 0; k < Nk; k++, w++, self -= Ni * Nj, out -= Ni * Nk - 1) { // w loop
    for (j = 0; j < Nj2; j++, exp++) {exp[j] = *exp * *exp; exp[j + 1] = exp[j] * *w;} // exp loop
    if (Nj & 1) exp[j] = *exp * *exp; // endpt
    exp -= Nj2;
    for (          i = 0; i < Ni; i++, out += Nk, exp -= Nj) // simd loop
    for (*out = 0, j = 0; j < Nj; j++, self++, exp++) *out += *self * *exp;} // dot loop""" ..inline(w = w, exp = exp, self = self, out = out)
    if inv: out *= 1 / n
    return out

  ## inplace O(n log n) bitreverse forward fft
  def dif_(self):
    """int PARTS, parti, PARTSIZE, BTFS, btfi, i;
    const int Ni = NEVE0[0];
    const int Nj = NEVE0[1];

    for (                          PARTS = 1,   PARTSIZE = Nj,  BTFS = Nj >> 1;
         PARTSIZE > 1;
         EVE0 -= PARTS * PARTSIZE, PARTS <<= 1, PARTSIZE >>= 1, BTFS >>= 1)

    for (parti = 0;
         parti < PARTS;
         parti++, EVE0 += PARTSIZE,    w -= BTFS * PARTS)

    for (btfi = 0, eve = EVE0;
         btfi < BTFS;
         btfi++,   eve -= Ni * Nj - 1, w += PARTS)

    for (i = 0; i < Ni; i++, eve += Nj) {*odd = eve[BTFS]; eve[BTFS] = (*eve - *odd) * *w; *eve += *odd;}""" ..inline(
      w = self.w, EVE0 = self, eve = self, odd = arrp(self)); return self

  ## inplace O(n log n) un-bitreverse backward fft
  def dit_(self):
    """int PARTS, parti, PARTSIZE, BTFS, btfi, i;
    const int Ni = NTOP0[0];
    const int Nj = NTOP0[1];

    for (                          PARTS = Nj >> 1, PARTSIZE = 2,   BTFS = 1;
         BTFS < Nj;
         TOP0 -= PARTS * PARTSIZE, PARTS >>= 1,     PARTSIZE <<= 1, BTFS <<= 1)

    for (parti = 0;
         parti < PARTS;
         parti++, TOP0 += PARTSIZE,    w -= BTFS * PARTS)

    for (btfi = 0, top = TOP0;
         btfi < BTFS;
         btfi++,   top -= Ni * Nj - 1, w += PARTS)

    for (i = 0; i < Ni; i++, top += Nj) {*bot = top[BTFS] * *w; top[BTFS] = *top - *bot; *top += *bot;}

    const int N = Ni * Nj; for (i = 0; i < N; *TOP0 *= inv, i++, TOP0++);""" ..inline(
      w = self.w.conjugate(), TOP0 = self, top = self, bot = arrp(self), inv = 1 / self.n); return self

  ## i, frqi -> exp( 2j*pi/n * frqi/i)
  def frqi(self):
    n, n2, ln, idx = self.n, self.n2, self.ln, self.idx; lnn = 1 << arange(ln)
    arr = (idx[n2::i] for i in lnn[1:][::-1]); arr = zip(lnn[1:], arr); return arr

  ## frci, frwi, frqi -> exp( 2j*pi/n * frwi/frci)
  def fffti(self):
    yield 1, r_[1], (r_[self.n2 << self.ln], self.idx[::2] << self.ln)
    nn = 1 << arange(self.ln); odd = self.idx[self.n2:]
    for frci, nffi, in zip(nn << 1, reversed(nn)): yield frci, odd[::nffi], (odd * nffi).reshape(-1, nffi) ## frci, frwi, frqi

  ## O(n log^2 n) fast fraction ft - note hires option expands to (n^3)
  def ffft(self, hires = None):
    itr = self.fffti(); frci, frwi, frqi = next(itr)
    hh = self.empty(); hh.fillfrom_(self).dif_(); yield frci, hh[:, 1:2].copy(), frqi[0]; yield frci, hh[:, ::2].copy(), frqi[1] ## O(n log n) fast integer ft

    N = self.n // self.ln
    while frci < N: ## O(n log^2 n) fast fraction ft
      frci, frwi, frqi = next(itr)
      w0 = self.exp(frci)
      for wi, fi in len(frwi) ..frqi.reshape(-1) ...zip(frwi): hh.fillfrom_(self); hh *= w0 ** wi; yield frci, hh.dif_()[:, ::frci].copy(), fi

    if hires: ## O(n^3) dot algorithm
      itr = tuple(itr) ..reversed()
      try: frci, frwi, frqi = next(itr)
      except StopIteration: return
      w = exp(2j * pi / (self.n * frci)) ** self.idx[self.n2:]; yield frci, self.dot_(w = w), frqi
      for frci, frwi, frqi in itr: w *= w; yield frci, self.dot_(w = w), frqi

  ## fractional histogram - period domain
  def histogram(self, plot = None, **kwds):
    hh = collections.deque(); ff = collections.deque()
    for frc, frh, frq in self.ffft(): hh.append(frh); ff.append(frq)
    hh = hstack(hh) ..abs(); ff = flatten(ff) ..asarray()
    TT = 1 / ff; TT *= self.n ** 2
    if plot: asciiporn.plot(y = hh, t = TT, tmin = 1, tmax = self.n, **kwds)
    return hh, TT

  def fmax(self):
    hmax = len(self) ...repeat(-1.0); fmax = len(self) ..empty(dtype = int)
    for frc, frh, frq in self.ffft():
      frh = abs(frh); x = frh.max(axis = 1); frq = frq[ find2d(frh, x)[1] ]; cll = x > hmax
      if cll.any(): hmax[cll] = x[cll]; fmax[cll] = frq[cll]; yield frc, hmax, fmax

  # cosine approx - newtons least squares minimization
  # awp -> a, b, c -> a cos(b i - c)
  def newton(self, awp):
    assert awp.dtype == double ## check type
    awp = as2d(awp); aa, ww, pp = awp.T; assert awp.shape == (len(self), 3), awp.shape ## check shape
    cos = exp(1j * pp)[:, newaxis] * exp(-1j * ww) ..powrange2d(self.n); sin = cos.imag.copy(); cos = cos.real.copy() ## cos, sin
    return """int i; double *a, *b, *c, sa, sb, sc, aa, bb, cc, ab, bc, ca, inv, x, y, z;
    const void *N = awp + Nawp[0] * Nawp[1];
    const int Ni = Nyy[1];

    for (a = awp, b = awp + 1, c = awp + 2; a != N; a += 3, b += 3, c += 3) { // simd loop
      sa = sb = sc = aa = bb = cc = ab = bc = ca = 0; inv = 1 / *a;

      for (i = 0; i < Ni; i++, yy++, cos++, sin++) { // dot loop
        x = *cos - inv * *yy; // x =      cos - yy
        y = *sin * x;         // y = sin (cos - yy)

        sa += *cos * x; // sa =   cos (cos - yy)
        sb +=    i * y; // sb = i sin (cos - yy)
        sc -=        y; // sc =  -sin (cos - yy)

        y = *sin * (*cos + x);      // y = sin (2 cos - yy)
        z = *cos * x - *sin * *sin; // z = cos2 - yy cos

        aa += *cos * *cos; ab +=     i * y; ca -=     y  ; // aa = cos^2    ab =  i sin (2 cos - y)      ca =  -sin (2 cos - y)
                           bb -= i * i * z; bc += i * z  ; //               bb = -i^2 (cos2 - yy cos)    bc = i (cos2 - yy cos)
                                            cc -=     z  ; //                                            cc =  -(cos2 - yy cos)
      }; sa *= inv; aa *= inv * inv; ab *= inv; ca *= inv;

      inv = 1 / (aa * (bc * bc - bb * cc) + bb * ca * ca + cc * ab * ab - 2 * ab * bc * ca); // inv det
      x = cc * ab - bc * ca; y = bb * ca - ab * bc;
                             z = aa * bc - ab * ca;
      *a -= 1 * inv * (sa * (bc * bc - bb * cc) + sb * x                   + sc * y                  ); // inv jacobian . ds
      *b -= 1 * inv * (sa * x                   + sb * (ca * ca - cc * aa) + sc * z                  );
      *c -= 1 * inv * (sa * y                   + sb * z                   + sc * (ab * ab - aa * bb));
    }""" ..inline(awp = awp, yy = self.real.copy(), cos = cos, sin = sin)["awp"]

  def fitcos(self, n = 2):
    for frc, frh, frq in self.fmax(): pass ## O(n log^2 n) frq approx
    awp = (len(self), 3) ..empty(); aa, ww, pp = awp.T
    aa.fill(1 / self.n2); aa *= frh; ww.fill(2 * pi / (self.n * self.n)); ww *= frq; pp[:] = exp(1j * ww) ..powrangedot2d(self) ..log().imag
    for i in log2(self.ln) ..range(): yield i, awp; self.newton(awp) ## newtons method
    i += 1; yield i, awp

  @staticmethod
  def itpatt(att, n): aa, TT, t0 = att.T[:, :, newaxis]; ww = 2 * pi / TT; y = exp(1j * ww) ..powrange2d(n); y *= aa * exp(-1j * ww * t0) ; return y.real

  @staticmethod
  def itpawp(awp, n): aa, ww, pp = awp.T[:, :, newaxis]; y = exp(1j * ww) ..powrange2d(n); y *= aa * exp(-1j * pp); return y.real

  ## awp -> att -> aa TT t0 -> aa cos(2pi/TT (t - t0))
  @staticmethod
  def toatt_(arr): assert arr.flags.contiguous; aa, ww, pp = arr.T; pp /= ww; ww[:] = 2 * pi / ww; return arr

  ## att -> awp -> aa ww pp -> aa cos(ww t - pp)
  @staticmethod
  def toawp_(arr): assert arr.flags.contiguous; aa, TT, t0 = arr.T; TT[:] = 2 * pi / TT; t0 *= TT; return arr

  @staticmethod
  def profile(n = 8, m = 16, **kwds):
    def test(n): (m, 1 << n) ..randg() ..fft2d().fitcos()
    Profile.timing2d(test, n, t_transform = log2, **kwds)

  @staticmethod
  def test(y = None, n = 64, TT = None, t0 = 3.3, **kwds):
    n2 = n >> 1; ln = int(log2(n)); inv = 1 / n; nn = tt = arange(n)
    if TT is None: TT = 0.25 * n + 2.3

    if y is None:
      y = cos(2 * pi / TT * (tt - t0)) ## cos
      if 1: y += 0.5 * sqrt(n) * randg(n) ## randg
      global XX; XX = y = ystack(y, y); y -= y.mean(axis = -1)[:, newaxis]

    y0 = fft2d(y); y1 = y0.empty(); y2 = y0.empty()
    if 0: print("n TT t0", n, TT, t0); plot(y = y0, **kwds)

    if 1 and n <= 256: y0.dot_(out = y1); y1.dot_(inv = True, out = y2); err = (y2 - y0) ..abs().max(); assert err < 4 * n * n * EPS, err ## test failsafe dot
    if 1: y1.fillfrom_(y0); y1.dif_(); y1.dit_(); err = (y1 - y0) ..abs().max(); assert err < 4 * n * ln * EPS, err ## test dif & dit
    if 0: ## fffti
      for frci, TTi, frqi in y0.fffti(): print( "frci frwi frqi", frci, TTi, "\n", frqi, "\n" )
    if 1: print("\nfourier histogram in period (1/frequency) domain"); y1.fillfrom_(y0); y1.histogram(plot = True, **kwds) ## histogram

    if 1: ## fitcos
      y1.fillfrom_(y0)
      for i, awp in y1.fitcos():
        z0 = y1.itpawp(awp, n); chi0 = z0 - y1.real; chi0 = dot2d(chi0, chi0)
        if 0: print(i, "aa ww pp, chi0\n", (awp, chi0[:, newaxis]) ..hstack()[0].round(8))
      att = y1.toatt_(awp.copy()); z1 = y1.itpatt(att, n); chi1 = z1 - y1.real; chi1 = dot2d(chi1, chi1); print( "amp TT t0, chi0\n", (awp, chi0[:, newaxis]) ..hstack()[0].round(8))
      if 1: plot(y = ystack(y1, z0, z1), **kwds)

def foo():
  t0 = arange(8.)
  y0 = array((t0 + 8, t0 + 16))
  t = linspace(0, 7.5, 16)
  print( "y0", y0 )
  print( "t0", t0 )
  print( "t", t )
  print(_itp2d(y0, t0, t))
  print( y0 )
