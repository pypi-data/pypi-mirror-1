"""
################################################################################

AUTHOR:
  kai zhu
  kaizhu@ugcs.caltech.edu

REQUIREMENTS:
- posix/unix os (Windows currently unsupported)
- py3to2 -    http://pypi.python.org/pypi/py3to2
- asciiporn - http://pypi.python.org/pypi/asciiporn

PSEUDOMETHOD:
  Cosine uses ".." syntax notation for pseudomethods
  goto: http://pypi.python.org/pypi/pseudomethod
  for more details about this feature

API:
  Cosine module:

INSTALL:
  python setup.py build
  python setup.py install
  python setup.py dev --quicktest

################################################################################
PLOT USAGE:

start up the py3to2 interpreter by typing "py3to2" in ur terminal &
import Cosine:


  |$ py3to2

  Python 2.6.py3to2 (r26:66714, Nov 18 2008, 00:56:43)
  [GCC 3.4.6 20060404 (Red Hat 3.4.6-10)] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  >>>
  >>> import Cosine
  created...
  py3k server starting...
  >>> ...py3k server started w/...
  >>>

################################################################################
RECENT CHANGELOG:
20081128
  created
"""
__author__ =	"kai zhu"
__author_email__ =	"kaizhu@ugcs.caltech.edu"
__description__ =	"scaleable simd cosine function fitter w/ ~n*log(n) performance"
__download_url__ =	None
__keywords__ =	None
__license__ =	"BSD"
__maintainer__ =	None
__maintainer_email__ =	None
__obsoletes__ =	None
__platforms__ =	None
__provides__ =	None
__requires__ =	["py3to2", "asciiporn"]
__url__ = "http://www-rcf.usc.edu/~kaizhu/work/Cosine"
__version__  = "2009.01.15"
## end setup info

## import Cosine; reload(Cosine); from Cosine import *
from __future__ import py3k_syntax
if "asciiporn" in globals(): reload(asciiporn)
import asciiporn; from asciiporn import *; from asciiporn import _asarray, _profile
if "DEBUG" not in globals(): DEBUG = 0

def quicktest():
  fitpoly.test()
  # Cosine.test()

if 1:
  def fft2nd(arr): return fft.fft(as2d(arr, contiguous = True))

  def ifft2nd(arr): return fft.ifft(as2d(arr, contiguous = True))

class fitpoly(_asarray):
  @staticmethod
  def tt(t, nth): return t[newaxis, :] ** arange(nth + 1)[:, newaxis]

  ## parse y, t datapoints
  @staticmethod
  def yt(**kwds): return dataZYT(parseonly = True, **kwds)

  def __new__(self, nth = None, wgt = None, cff = None, **kwds):
    if cff is not None: return super().__new__(self, cff)
    y, t = self.yt(**kwds); t = self.tt(t, nth)
    if wgt is None: cff, res, rank, sing = linalg.lstsq(t.T, y.T) ## find least squares
    else: assert 1 <= ndim(wgt) <= 2; cff, res, rank, sing = linalg.lstsq((wgt * t).T, (wgt * y).T) ## apply wgt 1st
    self = _asarray.__new__(self, cff.T); return self

  def itp(self, t): return dot(self, self.tt(t, self.shape[1] - 1))

  @staticmethod
  def test():
    n = 256; t = r_[0:1:1j*n]
    w, ph = 3, 4
    y = sin(2*pi*w*t+ph); y = array((y, y + 0.25))
    f = fitpoly(t = t, y = y, nth = 8)
    z = f.itp(t)
    plot(y = [y, z], t = t)

class fft2(fitpoly):
  def __new__(self, y, dtype = complex):
    y = as2d(asarray(y, dtype = dtype), contiguous = True)
    n = y.shape[1]; ln = int(log2(n)); assert 1 << ln == n, (y.shape, y.dtype)
    self = _asarray.__new__(self, y); self.n = n; self.ln = ln; self.n2 = n >> 1; return self

  def fft(self): self[:] = fft.fft(self); return self

  def ifft(self): self[:] = fft.ifft(self); return self

  def abs(self): return abs(self)

  ## inplace bitreverse sort
  def sort(self):
    arr = asarray(self); x = arr.ravel()[:1].copy(); ptr = x.copy(); weave.inline("""
    int i; const int Ni = Narr[0]; int j; const int Nj = Narr[1]; const int n2 = Narr[1] >> 1;

    int pos, step; pos = 0; arr += 1;
    for (j = 1; j < Nj - 1; j++, arr += 1){
    step = n2; while(pos >= step) {pos -= step; step >>= 1;} pos += step; step = pos - j;

    if(step > 0) {
    for (i = 0, ptr = arr; i < Ni; i++, ptr += Nj) {
    *x = *ptr; *ptr = ptr[step]; ptr[step] = *x;
    }}}""", ("arr", "x", "ptr")); return self

  ## decimation in frequency algorithm
  def dif(self, w = None):
    arr = asarray(self); n = arr.shape[1]; w = exp(-2j * pi / n) ** arange(n) if w is None else w.copy()
    x = arr.ravel()[:1].copy(); wptr = x.copy(); e = x.copy(); o = x.copy(); weave.inline("""
    int i; const int Ni = Narr[0]; int j; const int Nj = Narr[1]; int step, step2, wi;

    for (step = Nj; step > 1; step >>= 1) { step2 = step >> 1; // ln loop
    for (wi = 0, wptr = w; wi < step2; *wptr *= *wptr, wi++, wptr++){ // butterfly loop
    for (j = wi; j < Nj; j += step) { // partition loop
    for (i = 0, e = arr + j, o = e + step2; i < Ni; i++, e += Nj, o += Nj) { // simd loop

    *x = *e; *e += *o; *o -= *x; *o *= -*wptr; // butterfly

    }}}}""", ("arr", "w", "wptr", "e", "o", "x")); return self

  def _dtft(self):
    n, ln, n2 = self.n, self.ln, self.n2; N = n * n >> 1
    w0 = exp(-2j * pi / N) ** arange(n)
    frq0 = arange(n2) ..fft2(dtype = float).sort().ravel()

    x = fft2(self.copy()).dif(); y = x[:, 1:2]; frq = r_[n2 + 0.0]; yield y, frq; y = x[:, ::2]; frq = frq0; yield y, frq
    for lfrac, frac in enumerate(1 << arange(1, ln), 1):
      winv = 1 << ln - lfrac - 1; lvl = arange(lfrac - 1)
      wbit = arange(1 << lfrac - 1)[:, newaxis] & (1 << lvl[::-1]); wbit = 1 + dot(wbit.astype(bool), 1 << lvl + 1); wbit *= winv
      frq = 1 / frac + frq0 * (2 / frac); frq = frq.reshape(len(wbit), -1)
      for wbit, frq in zip(wbit, frq): y = fft2(self * w0 ** wbit).dif()[:, ::frac]; yield y, frq

  def _fmax(self, ymax, fmax, y, frq):
    y = asarray(y); weave.inline("""
    int i; const int Ni = Ny[0]; int j; const int Nj = Ny[1];
    for (i = 0; i < Ni; i++, ymax++, fmax++) {
    for (j = 0; j < Nj; j++, y++) {
    if (abs(*y) > *ymax) {*ymax = abs(*y); *fmax = frq[j];}
    }}
    """, ("ymax", "fmax", "y", "frq")); return ymax, fmax

  def fmax(self):
    ymax = zeros(len(self)); fmax = ymax.copy()
    for y, frq in self._dtft(): self._fmax(ymax, fmax, y.copy(), frq)
    return ymax, fmax

  def _frqi(self, frq):
    x = floor(log2(frq)); x[x < 0] = -inf; a = (x + 1) * self.n2; a[a == -inf] = 0
    x = 2 ** x; b = frq - x; x *= 2; x[x == 0] = 2; b *= self.n / x
    frqi = asarray(a + b, dtype = int); return frqi

  def histogram(self):
    yy = empty((len(self), self.ln * self.n2 + 1), dtype = complex); ff = empty(yy.shape[1])
    for y, frq in self._dtft(): frqi = self._frqi(frq); yy[:, frqi] = y; ff[frqi] = frq
    assert all( ff.argsort() == arange(len(ff)) ); return yy, ff

  # finv = [linalg.inv(x ** r_[0, 1, 2][:, newaxis]) for x in ((0, 0.5, 1), (0, 1/3, 1))]
  # finv = asarray(finv)[..., 1:].copy(); finv[..., 1] *= 2
  finv = arange(3.0); finv = (0.5 * finv)[:, newaxis] ** finv; finv = linalg.inv(finv)[:, 1:]; finv[:, 1] *= 2

  def cos(self):
    yy, ff = self.histogram(); yy = abs(yy); nff = len(ff) - 1; yi, fi = find2nd(yy, yy.max(axis = 1))
    yi = yi.repeat(3).reshape(-1, 3); fi[fi == 0] = 1; fi[fi == nff] = nff - 1; fi = fi[:, newaxis] + (-1, 0, 1)

    ff = ff[fi]; f0, f1, f2 = ff.T; df = f2 - f0; cll = (f1 - f0) * 2 != df
    yy = yy[yi, fi]; ab = dot(yy, self.finv[0]); ab[cll] = dot(yy[cll], self.finv[1])
    frq = f0 - df * ab[:, 0] / ab[:, 1]; return frq

  def cos(self):
    ymax, fmax = self.fmax()
    n = self.n; n2 = self.n2; fmax[fmax == 0] = 1 / n2; fmax[fmax == n2] = n2 - 0.5
    df = log2(fmax).astype(int); df[df < 0] = 0; df = (1 << df) / n

    ff = fmax[newaxis] + outer((-1, 0, 1), df)
    yy = exp((-2j * pi / n) * ff)[..., newaxis] ** arange(n)
    yy = [dot2nd(x, self) for x in yy] ..asarray() ..abs()
    print(yy, ff)
    
    print(fmax, df)
    return fmax

if 1:
  n = 32; ln = 2; n2 = n/2

  x = rng(n) - 0.5
  frq = 1.90; t = linspace(0, 2 * pi, n); y0 = cos(frq * t)
  # y0 = [y0 + x * 2.0, rng(n) - 0.5]
  y0 = as2d(y0); y0 -= fitpoly(y = y0, t = t, nth = 1).itp(t)
  # t = arange(n); yt = []; plot(y = y0, t = t)

  y = fft2(y0); yy, tt = y.histogram(); plot(y = abs(yy), t = tt)
  x = y.cos()
  print(frq, x, x / frq)

  if 0:
    plot(y = fft.fft(y0) ..abs())
    y = fft2(y0)
    y.dif().sort()
    plot(y = abs(y), t = t)
    # y = fft2([y0, rng(y0.shape) - 0.5])
    # # y, t = y.histogram(); plot(y = abs(y), t = t)
    # y.freq()
