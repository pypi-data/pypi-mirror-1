## import numbytes; reload(numbytes); from numbytes import *

from __future__ import py3k_sugar
import numbytes; from numbytes import *; from numbytes import _numbytes; from numbytes._numbytes import *
import builtins, os, sys, traceback
import collections, functools, itertools, re

if 1: ######## helper fnc
  def closure(*args, **kwds): return lambda fnc: fnc(*args, **kwds)

  def depth(arr):
    try: return 1 + depth(arr[0])
    except TypeError: return 0

  def echo(aa): return aa

  @functools.wraps(builtins.enumerate)
  def enumerate(arr, i = None): return count(i) ..zip(arr) if i else builtins.enumerate(arr)

  def flatten(tree, iterable = is_itr, depth = -1):
    if iterable(tree) and depth:
      for aa in tree:
        for bb in walktree(aa, iterable, depth - 1): yield bb
    else: yield tree

  def lens(*args): return [len(aa) for aa in args]

  ## get current screensize - row x col
  def screensize(): import fcntl, struct, termios; return fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, "0123") ...struct.unpack("hh")

  ## piped system call
  def system(exe): import subprocess; print( exe ); return subprocess.Popen(exe, shell = 1, stdout = subprocess.PIPE, close_fds = 1).stdout.read()

  ## generate unique alphanumeric string guaranteed not to occur in s
  def uniquestr(s, kwd = "qjzx"):
    while kwd in s: kwd = kwd + hex(id(kwd))
    return kwd

class marray(_numbytes._marray):
  def debug(self): print("%s %s tsize=%s shape=(%s %s) strides=(%s %s) transposed=%s" % (type(self), self.tcode, self.tsize, self.shape0, self.shape1, self.strides0, self.strides1, self.transposed))

  def __new__(self, tcode, arr = None, shape0 = 1, shape1 = -1):
    if isinstance(tcode, _numbytes._marray): return tcode.__copy__(self)
    if not isinstance(tcode, int): tcode = ord(tcode)
    if isinstance(arr, bytearray): assert len(arr) >= 1, "zero size array"; return super().__new__(self, tcode, arr).reshape(shape0, shape1)
    elif isinstance(arr, bytes): arr = bytearray(bytes)
    elif is_seq(arr): arr = self.bytes_from_seq(tcode, arr)
    elif isinstance(arr, int): arr = bytearray(arr * self.tsize_from_tcode(tcode))
    else: raise TypeError("invalid 2nd argument")
    return self.__new__(self, tcode, arr, shape0, shape1)

  def copy_base(self): return self.__copy__(_numbytes._marray)

  def __iter__(self): return self.copy_base() ..iter()

  def __getitem__(self, slices): return self.__callmethod__("__getitem__", slices if isinstance(slices, tuple) else (slices,))

  def __setitem__(self, slices, aa):
    if not isinstance(aa, marray) and is_seq(aa): aa = marray(self.tcode, aa)
    return self.__callmethod__("__setitem__", (slices if isinstance(slices, tuple) else (slices,), aa))

  def rows(self):
    for ii in range(self.shape0): yield self[ii]

  def __str__(self):
    rows, cols = screensize(); ss = []; ll = min(self.shape1, cols / 2)
    for ii in min(self.shape0, rows / 2) ..range():
      aa = "[%s]" % self[ii, :ll].__callmethod__("__str__", ())[:-1]
      if not ii: aa = "[" + aa;
      if len(aa) > cols: aa = "%s.\x2e.]" % aa[:cols - 4]
      ss.append(aa)
    if ii < self.shape0: ss[-1] += ".\x2e."
    ss[-1] += "]"
    if len(ss[-1]) > cols: ss[-1] = ss[-1][:cols - 8] + ss[-1][-8:]
    return "\n".join(ss)

  @staticmethod
  def test():
    # _numbytes._marray.__getattribute__ ..print()
    bb = marray("f", range(64), 4, -1); bb = bb.__copy__(); bb.debug()
    bb[:] = [sqrt(aa) for aa in range(16)]
    bb = bb[1:, 2:]
    print(bb)
    # for aa in bb: print(aa)
    dir(bb) ..print()

@closure()
def _():
  for aa in "bytes shape0 shape1 strides0 strides1 tcode tsize contiguous transposed T".split(" "):
    @closure()
    def _(aa = aa): setattr(marray, aa, property(lambda self: self.__callmethod__("get_" + aa, ())))
  for aa in "__copy__ reshape".split(" "):
    @closure()
    def _(aa = aa): setattr(marray, aa, lambda self, *args: self.__callmethod__(aa, args))

from math import *; from random import *

## quicktest
def quicktest(ipath = ""):
  ## img2txt
  if not ipath: ipath = os.path.join(numbytes.__path__[0], "mario.png")
  ipath ..print()
  png2txt(ipath) ..print()
  marray.test()

class img2txt(object):
    def _shape(self): return self.barr[0] * 256 + self.barr[1], self.barr[2] * 256 + self.barr[3]
    shape = property(_shape)
    def __str__(self): return ansi_str(self.barr)
    def topng(self, fpath): png_write(fpath, self.barr)

def png2txt(fpath, scale = 1, plaintxt = None, wmatch = 2, wmismatch = 4): aa = img2txt(); aa.barr = png_read(fpath, scale, True if plaintxt else False, wmatch, wmismatch); return aa
