# import img2txt; reload(img2txt); from img2txt import *
from __future__ import py3k_syntax
import functools, itertools, re, subprocess, time
import cPickle as pickle

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

  def screensize(): s = system_("stty -a"); row, col = re.search("rows .*?(\d*).*?columns .*?(\d*)", s).groups(); return int(row), int(col)

  def system_(exe): exe = subprocess.Popen(exe, shell = 1, stdout = subprocess.PIPE, close_fds = 1).stdout; s = exe.read(); exe.close(); return s

  def shapes( * arr): return [shape(x) for x in arr]

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

class asarray_(ndarray, savestate): ## array w/ serializable states
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
    cll = sum(1 << arange(0, fres.prod(), fres[1])) ^ 0xffffffffffffffff # culls left boundary
    x = arr[..., 3]; x &= cll; x >>= 1 # shift left
    x = arr[..., 4]; x <<= 1; x &= cll # shift right
    if 0 and debug:
      for x in arr[17, :5]: self.printd(x)

    fmap = arr
    fidx = r_[32:128]; assert len(fidx) == len(fmap)
    fpop = popcount(fmap[:, 0]); fpop[-1] = fres.prod()

    fmap = (fmap, fmap ^ True) ..concatenate(axis = 0)
    fidx = r_[fidx, fidx + 0x80]; fpop = r_[fpop, fres.prod() - fpop] # include inverted color

    # fmap = (fmap, fmap) ..concatenate(axis = 0)
    # fidx = r_[fidx, fidx + 0x100]; fpop = r_[fpop, fpop * 3] # include bold

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
    # pad = fres.prod() - len(fbin_); fbin_ = asarray( fbin_ + [fbin_[-1]] * pad )
    fbin_ = asarray(fbin_); fbin_[fres.prod() - 1, 1] = fbin_[-1, 1]; fbin_ = fbin_[:fres.prod()]

    a, b = fbin_.T
    x = 4; b[b < x] = x # low pixel cutoff
    x = len(fpop) - 4; a[a > x] = x # high pixel cutoff

    self.fmap = fmap; self.fidx = fidx; self.fpop = fpop; self.fbin_ = fbin_
    self.fbin = fbin = fbin_.copy(); fbin[fbin_[:, 0] == 0, 0] = 1 # never blank blocks

    _ = "  "
    chrmap = [_.join( "\33[37;40m%s\33[0m" % chr(i) for i in range(0x80) ).replace("\x7f", " ")]
    chrmap[0] += _ + chrmap[0].replace("40" , "40;7") # invert color
    chrmap[0] += _ + chrmap[0].replace("40", "40;1") # bold

    color = 7, 1, 2, 4, 6, 5, 3, 0; chrmap = [chrmap[0].replace("37", str(i + 30)) for i in color]; self.depth = depth = len(chrmap) # color
    chrmap[-1] = chrmap[-1].replace("40m", "40;1m").replace("40;7", "100") # bold black
    chrmap[0] = chrmap[0].replace("37;40;1;7", "30;107") # bold white

    # self.chrmap = chrmap = asarray(_.join(chrmap).split(_) * 2)
    self.chrmap = chrmap = _.join(chrmap).split(_) ..reshape((-1, 2, 0x100)).transpose(1, 0, 2).ravel()

    x = chrmap.reshape(2, -1, 0x100); x[1, -1] = x[0, -1]

    if debug: print( "".join(chrmap) ); print( "".join(chrmap[fidx]) )

    color = "ff:ff:ff ff:00:00 00:ff:00 00:00:ff 00:a8:ec e3:00:7b f9:f4:00 00:00:00"
    color = [eval("0x%s" % x) for x in color.replace(":", " ").split(" ")] ..asarray()
    regular = color - 0x10; regular[regular < 0] = 0
    bold = color + 0x20; bold[bold > 0xff] = 0xff
    # bold = color + 0x20; bold[bold < 0] = 0xff
    self.color = color = (regular.reshape(-1, 3), bold.reshape(-1, 3)) ..concatenate(axis = 0)

    def method(fname):
      @functools.wraps(getattr(ndarray, fname), assigned = ("__name__", "__doc__"))
      def f(self, *args, **kwds): x = getattr(self.buf, fname); return x(*args, **kwds) if kwds else x(*args)
      return f

    for x in dir(ndarray): # add arr-like methods - from self.buf
      if not hasattr(_img2txt, x) and getattr(ndarray, x) ..callable() and "set" not in x: setattr(_img2txt, x, method(x)) # disallow setters - have bugs
      # if not hasattr(_img2txt, x) and getattr(ndarray, x) ..callable(): setattr(_img2txt, x, method(x))

  def fill(self, arr): # fill buf w/ data
    fres = self.fres; self.res = res = divceil(arr.shape, fres) # res
    if not all(arr.shape // fres == res): x = arr; arr = zeros(res * fres, dtype = bool); arr[:x.shape[0], :x.shape[1]] = x # resize canvas
    if len(self) != res.prod(): self.buf = empty(res.prod(), dtype = int64) # resize buf
    buf = self.buf; buf.fill(0) # clear buf

    arr = asarray(arr, dtype = bool) .reshape(res[0], fres[0], res[1], fres[1]) .transpose(1, 3, 0, 2) .reshape(fres.prod(), -1) # create blocks
    for i, x in enumerate(arr != 0): buf |= x << i # fill buf
    return self

  def itp(self, blank = True, wmatch = 2, wmismatch = 1): # interpolate block -> ascii chr
    buf = self.buf; pop = popcount(buf); fbin = self.fbin_ if blank else self.fbin; fhst = [self.fmap[a:b] for a, b in fbin] # fbin, fhst
    for i, (a, b), f in zip(count(1), fbin, fhst):
      cll = pop == i
      if not cll.any(): continue
      x = buf[cll]; f = f.T[..., newaxis]
      y = popcount(x & f) # match
      y[0] *= wmatch # weight original match
      y[0] -= popcount(x ^ f[0]) * wmismatch # subtract mismatch
      y = y.sum(axis = 0); y = y.argsort(axis = 0)[-1] + a; buf[cll] = self.fidx[y] # tally weights & pick highest
    buf[buf == 0] = self._; return self

  def tostr(self): return "\n".join("".join(self.chrmap[x]) for x in self.reshape(self.res))

  def from_image(self, file, scale = 1, color = True): # must be a file or filename
    from PIL import Image; arr = Image.open(file) # import img
    fres = self.fres[::-1]; res = asarray(arr.size) * scale / fres; res = ceil(res).astype(int) * fres
    if not all(res == arr.size): arr = arr.resize(res) # resize img
    fres = fres[::-1]; res = res[::-1]; self.res = res // fres # save res

    # if color and arr.mode == "RGB":
      # color = arr.resize(self.res[::-1]).getdata() ..asarray()[:, newaxis] - self.color
      # color = sum(color * color, axis = -1).argsort(axis = -1)[:, 0]; color <<= 8
    # else: color = None
    if color:
      # and arr.mode == "RGB":
      color = (arr if arr.mode == "RGB" else arr.convert("RGB"))
      color = arr.resize(self.res[::-1]).getdata() ..asarray()[:, newaxis] - self.color
      color = sum(color * color, axis = -1).argsort(axis = -1)[:, 0]; color <<= 8
    else:
      color = (arr if arr.mode == "L" else arr.convert("L")); i = r_[0, 7, 8, 15]
      color = arr.resize(self.res[::-1]).getdata() ..asarray()[:, [0]] - self.color[i, 0]
      color = color.argsort(axis = -1)[:, 0]; color = i[color] << 8

    arr = (arr if arr.mode == "1" else arr.convert("1")).getdata() ..asarray(dtype = bool).reshape(res); self.fill(arr).itp() # itp
    # if color is not None: self.buf |= color # add extracted color info
    # color = color.resize(self.res[::-1]).getdata() ..asarray()[:, newaxis] - self.color
    # color = sum(color * color, axis = -1).argsort(axis = -1)[:, 0]; self.buf |= color << 8
    self.buf |= color # add extracted color info
    
    return self

  @staticmethod
  def test():
    self = _img2txt
    self.debug = 0
    self = self()
    if 1:
      # font = "lucida console bold 06x10.bmp"
      img = "mario.jpg"
      scale = 0.8
      color = 1
      arr = self.from_image(img, color = color, scale = scale)
      print( self.tostr() )
    self.debug = None

img2txt = _img2txt()

class dataNFT(ndarray):
  def __new__(self, ft = None, f = None, t = None):
    if ft is not None: # zipped ft
      assert f == t == None; ft = asarray(ft, dtype = float); shp = r_[1, ft.shape][-3:]; ft = ft.reshape(shp)

    else: # individual f, t
      assert ft is None; f = asarray(f, dtype = float); fshp = r_[1, f.shape][-2:]; f = f.reshape(fshp)

      if t is None: t = range(fshp[1])
      t = asarray(t, dtype = float); tshp = r_[1, t.shape][-2:]; t = t.reshape(tshp)

      assert fshp[1] == tshp[1]
      nf, nt = fshp[0], tshp[0]; assert (nf % nt) == 0 or (nt % nf) ==0

      if nf > nt: t = t.repeat(nf // nt, axis = 0)
      elif nt > nf: f = f.repeat(nt // nf, axis = 0)
      ft = transpose((f, t), (1, 2, 0))

    self = asarray_.__new__(self, ft.copy())
    self.minmax = minmax = [(x.min(), x.max()) for x in self.T] ..transpose() # self.minmax
    self.origin = origin = [0. if a <= 0 <= b else a if 0 < a else b for a,b in minmax.T] ..asarray() # self.origin
    return self

  def init(self):
    for ft in self:
      t = ft[:, 1]
      if any(t[:-1] > t[1:]): ft[:] = ft[t.argsort()] # sort t-axis

    arr = []; f = self[..., 0] # self.extrema
    for fe in f.min(axis = 1), f.max(axis = 1): cll = find2nd(f, fe); te = self[cll[0], cll[1], 1]; arr.append((fe, te))
    self.extrema = extrema = transpose(arr, (2, 0, 1))

    f = self[..., 0].T; cll = f == 0 # self.roots
    x = f > 0; cll[:-1] |= (x[:-1] ^ x[1:]) & (1 ^ cll[1:]) # record sign change
    self.roots = roots = []
    for t, cll in zip(self[..., 1], cll.T):
      t = t[cll]
      x = (repeat(self.origin[0], len(t)), t) ..transpose()
      roots.append(x)

    return self

  def concat(self, x): return (self, x) ..concatenate(axis = 0) ..dataNFT()

  def norm(self, arr = None): # normalize data points
    a, b = self.minmax; assert not any(a == b)
    if arr is None: arr = self
    arr = arr.reshape(r_[1, 1, arr.shape][-3:]).astype(float); arr -= a; arr *= 1 / (b - a)
    n = linspace(0, 1, len(arr)); n = n[newaxis, :].repeat(arr.shape[1], axis = -1).reshape(r_[arr.shape[:-1], 1])
    arr = concatenate((n, arr), axis = -1); return arr

  @staticmethod
  def test():
    if 1:
      x = dataNFT(f = [ [0,1,2,-1,3], [1, 0, 0, 4, 0] ], t = [4,3,2,7,8]).init()
      print(); print( x, x.minmax, x.origin )
      print(); print( x.roots )
      print(); print( x.norm(x) )

class _tplot3d(_img2txt):

  def __init__(self):
    _img2txt.__init__(self)
    i = self.fres.prod() // 2
    self.fbin[:i] = 1, self.fbin[i, 1]

  def fill(self, arr):
    fres = self.fres; self.res = res = arr.max(axis = 0) // fres + 1 # res

    if len(self) != res.prod(): self.buf = empty(res.prod(), dtype = int64) # resize buffer
    buf = self.buf; buf.fill(0) # clear buf

    row, i = divmod(arr[:, 0], fres[0]); col, j = divmod(arr[:, 1], fres[1]); self.rc = rc = row * res[1] + col
    for i, x in zip(rc, 1 << (i * fres[1] + j)): buf[i] |= x # fill buf
    return self

  def __call__(self, ft = None, f = None, t = None, skew = (0, 0), yres = 1 / 3):#, xres = 1, yres = 1 / 6, tmin = None, tmax = None, ymin = None, ymax = None, idx = 1, txt = None):
    fres = self.fres
    self.data = data = dataNFT(ft, f, t).init(); nn = data.shape[1]; norm = data.norm()
    nline = norm[:, 0, 0].copy(); extra = []
    no, fo, to = origin = data.norm(data.origin)[0, 0]

    arr = asarray((
      [(1, fo, 0), (1, fo, 1)], # origin line
      [(1, 1, 0), (0, 1, 0)], [(1, 1, 1), (0, 1, 1)], # interconnect
      [(1, 0, 0), (1, 0, 1)], [(1, 1, 0), (1, 1, 1)], [(1, 0, 0), (1, 1, 0)], [(1, 0, 1), (1, 1, 1)], # ft plane
      )); extra.append(arr.reshape(-1, 3)) # front plane

    arr = asarray((
      [(0, 1, 0), (0, 1, 1)], [(0, 0, 0), (0, 1, 0)], [(0, 0, 1), (0, 1, 1)], # ft plane
      )); extra.append(arr.reshape(-1, 3)) # back plane

    arr = empty((len(data), 2, 3)); arr[:] = origin; arr.T[0] = nline
    extra.append(arr.reshape(-1, 3)) # origin

    # arr = empty((len(data), 3, 2, 3)); arr[:] = data.norm(data[:, [0, nn // 2, -1]])[:, :, newaxis]; arr[..., 0, 1] = 0
    # extra.append(arr.reshape(-1, 3)) # endpoint
    arr = empty((len(data), 2, 2, 3)); arr[:] = data.norm(data[:, [0, -1]])[:, :, newaxis]; arr[..., 0, 1] = 0
    extra.append(arr.reshape(-1, 3)) # endpoint

    arr = empty((len(data), 2, 2, 2, 3)); arr[:] = data.norm(data.extrema)[:, :, newaxis, newaxis]
    arr[..., 1, 0, 1] = 0
    extra.append(arr[:, 0].reshape(-1, 3)) # min
    extra.append(arr[:, 1].reshape(-1, 3)) # max

    for n, root in zip(nline, data.roots):
      if not len(root): continue
      root = data.norm(root)[0]; root[:, 0] = n
      arr = empty((len(root), 2, 2, 3))
      arr[:] = root[:, newaxis, newaxis]
      # arr[:, 1, :, 0] = 0, 1
      arr[:, 1, 0, 0] = 1
      extra.append(arr.reshape(-1, 3))

    rc = concatenate( [norm.reshape(-1, 3)] + extra )

    rc += outer(rc[:, 0], r_[0, -skew[0], -skew[1]]) # pseudo rotate
    res = screensize() * fres; res[0] *= yres # res
    rc = rc[:, 1:]; rc[:, 0] *= -1 # reverse rows
    rc -= rc.min(axis = 0); rc *= (res - 1) / rc.max(axis = 0) # scale to res
    i = [len(x) for x in extra] ..cumsum(); extra = (rc[-i[-1]:]*(1/fres)).astype(int) # extract extra
    i = r_[0, i]; extra = [extra[a:b].reshape(-1, 2, 2) for a, b in zip(i[:-1], i[1:])]

    for i, x in enumerate(res - 1): arr = rc[:,i]; arr[arr < 0] = 0; arr[arr > x] = x # bound check
    self.fill(rc.astype(int)).itp(blank = None) # img2txt

    self.zbuf = zbuf = zeros(self.buf.shape, dtype = int)
    for i, x in enumerate(self.rc[:len(data) * nn].reshape(-1, nn)): zbuf[x] = (i % 6) + 1

    for i, arr in enumerate(extra): # extra
      point = None; overwrite = None; z = 7; color = (arange(len(data)) % 6) + 1
      if i == 0: point = ord("|"); offset = arr[0, 1, 1] # front plane
      elif i == 1: point = ord("|"); z = 0 # back plane
      elif i == 2: point = ord("O") # origin
      elif i == 3:
        point = ord("|"); z = color # endpoint
        for a, b in arr[-2:]: zbuf.reshape(self.res)[b[0]:a[0] + 1, a[1]] = 0 # overwrite front plane
      elif i == 4: point = ord("U"); z = color # min
      elif i == 5: point = ord("A"); z = color # max
      else: point = ord("+"); overwrite = True # root
      z = repeat(z, len(arr) / size(z)).ravel()
      for (a, b), z in zip(arr, z): self.line(a, b, point = point, z = z) # line

    cll = zbuf == 0; zbuf[zbuf == 7] = 0; zbuf[cll] = 7 # swap gray & white
    self.buf |= zbuf << 8
    print( self.tostr() ) # plot
    # arr = bytearray("'" * (self.res[1] - offset)) # footer w/ box offset
    arr = bytearray("'" * offset) # footer w/ box offset
    fmin, tmin, fmax, tmax = [[ord(x) for x in " %s "%x] for x in data.minmax.ravel()]
    arr[:len(tmin)] = tmin; arr[-len(tmax):] = tmax # t minmax
    n = len(arr) // 2; arr[n - len(fmin):n] = fmin; arr[n:len(fmax) + n] = fmax # f minmax
    print( str(arr) ) # print footer w/ offset

  def line(self, a, b, point = None, z = 0):
    _ = self._; buf = self.buf.reshape(self.res); zbuf = self.zbuf.reshape(self.res)

    a, b = ab = (a, b) ..asarray(dtype = int); r, c = ab.T # a, b
    dr, dc = dx = b - a; a, b = ab = ab.round().astype(int) # dx
    if (abs(dr) > abs(dc) and dr < 0) or (abs(dc) > abs(dr) and dc < 0): a, b = ab = ab[::-1]; r, c = ab.T # sort coord

    if point is not None:
      for i, j in ab:
        buf[i, j] = point; zbuf[i, j] = z % 8
        # if buf[i, j ] == _ or z >= zbuf[i, j]: buf[i, j] = point; zbuf[i, j] = z % 8

    if not all(dx):
      if dr == 0: buf = buf[r[0], c[0]:c[1]]; zbuf = zbuf[r[0], c[0]:c[1]]
      else: buf = buf[r[0]:r[1], c[0]]; zbuf = zbuf[r[0]:r[1], c[0]]
      cll = (buf == _) | (z > zbuf); buf[cll] = ord("|" if dr else "_"); zbuf[cll] = z % 8; return # draw horizontal / vertical line

    if abs(dr) >= abs(dc): f = r_[r[0]:r[1]]; t = ((f - r[0]) * (dc / dr) + c[0]).round().astype(int)
    else:                  t = r_[c[0]:c[1]]; f = ((t - c[0]) * (dr / dc) + r[0]).round().astype(int)

    cll = f * self.res[1] + t; cll = cll[::4]
    cll = cll[(self.buf[cll] == _) | (z > self.zbuf[cll])]
    self.buf[cll] = ord("-"); self.zbuf[cll] = z % 8

  @staticmethod
  def test():
    if 1:
      t = linspace(0, 1, 0xff) - 0.25
      # f = ( t, cos(t * 2 * pi), sin(t * 2 * pi), sin(t * 2 * pi) ) ..array() - 0.5
      f = ( t, t, cos(t * 2 * pi), sin(t * 4 * pi), cos(t * 2 * pi) + 0.25 ) ..array() - 0.5
      f = f[::-1]
      yres = 1 / 3
      skew = 1/4, 1/8
      skew = r_[skew] * 1
      # tplot3d(f = f, t = t, yres = yres, skew = skew * 0)
      tplot3d(f = f, t = t, yres = yres, skew = skew)

tplot3d = _tplot3d()
