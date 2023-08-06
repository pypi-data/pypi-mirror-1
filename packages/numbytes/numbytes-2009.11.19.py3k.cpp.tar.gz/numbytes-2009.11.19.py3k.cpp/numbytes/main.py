## import numbytes; reload(numbytes); from numbytes import *

from __future__ import py3k_sugar
_VERSION = "2009.11.19.py3k.cpp"
_MANIFEST = """_setup.py
setup.py
README.numbytes
numbytes/_numbytes.cpp
numbytes/__init__.py
numbytes/lucida06x10.bmp
numbytes/main.py
numbytes/mario.png"""
if "_README" not in globals(): global _README; _README = ""
_DESCRIPTION = _README.split("\n")[0]
_README = """REQUIRES PYTHON3.1
test usage: python3.1 setup.py build dev --quicktest
""" + _README
_README += """
RECENT CHANGE:
20091116 - package integrated
20081219
- tobias rodaebel points out ".." is used in relative imports as well.
  fixed pseudomethod 2 b compatible w/ this
- removed limitation where parser disallows use of keyword "__pseudomethod__"
  in scripts
"""



if 1: #### helper fnc
  def depth(arr):
    try: return 1 + depth(arr[0])
    except TypeError: return 0

  @_import("functools")
  @functools.wraps(builtins.enumerate)
  def enumerate(arr, i = None): return count(i) ..zip(arr) if i else builtins.enumerate(arr)

  def lens(*args): return [len(aa) for aa in args]

  re_type = re.compile("")
  re.sub2 = lambda ss, aa, bb, *args, **kwds: re.sub(aa, bb, ss, *args, **kwds)

  ## get current screensize - row x col
  @_import("fcntl struct termios")
  def screensize(): return fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, "0123") ...struct.unpack("hh")

  @_import("io")
  def stdout2str(fnc):
    import io
    with io.StringIO() as f:
      stdout0 = sys.stdout
      try: sys.stdout = f; fnc(); return f.getvalue()
      finally: sys.stdout = stdout0

  ## piped system call
  @_import("subprocess")
  def system(exe): print( exe ); return subprocess.Popen(exe, shell = 1, stdout = subprocess.PIPE, close_fds = 1).stdout.read()

  ## generate unique alphanumeric string guaranteed not to occur in s
  def uniquestr(s, kwd = "qjzx"):
    while kwd in s: kwd = kwd + hex(id(kwd))
    return kwd



#### python compiled code object viewer
class codetree(object):
  co_args = "co_argcount co_kwonlyargcount co_nlocals co_stacksize co_flags co_code co_consts co_names co_varnames co_filename co_name co_firstlineno co_lnotab co_freevars co_cellvars".split(" ")
  co_constsi = co_args.index("co_consts") ## co_consts index pos

  def __init__(self, codeobj = None, **kwds):
    if codeobj: ## codeobj
      self.__dict__ = dict((aa, getattr(codeobj, aa)) for aa in self.co_args)
      self.co_consts = tuple(codetree(aa) if isinstance(aa, types.CodeType) else aa for aa in codeobj.co_consts) ## recurse
    self.__dict__.update(kwds)

  def __eq__(self, aa): return isinstance(aa, codetree) and self.__dict__ == aa.__dict__

  ## serializable: codetree(codeobj) == eval( repr( codetree( codeobj ) ) )
  def __repr__(self): return "codetree(**%r)" % self.__dict__

  def __str__(self, _ = ""):
    arr = collections.deque()
    arr.append("codetree(\n")
    for kk, aa in sorted(aa for aa in self.__dict__.items() if aa[0] != "co_consts"):
      arr.append("%s%s = %s%r,\n" % ( _, kk, " " * (16 - len(kk)), aa ))
    for aa in self.co_consts:
      arr.append("%s  %s,\n" % ( _, aa.__str__(_ + "  ") if isinstance(aa, codetree) else aa ))
    arr.append(_ + ")")
    return "".join(arr)

  ## codeobj == codetree(codeobj).compile()
  def compile(self):
    args = [getattr(self, aa) for aa in self.co_args] ## create list of args
    args[self.co_constsi] = tuple(aa.compile() if isinstance(aa, codetree) else aa for aa in self.co_consts) ## recurse
    return types.CodeType(*args)

  ## recursive disassembler
  def dis(self):

    def recurse(aa, _ = ""):
      if isinstance(aa, types.CodeType):
        yield _ + stdout2str(lambda: dis.dis(aa)).replace("\n", "\n" + _)
        for aa in aa.co_consts:
          for aa in recurse(aa, _ + "  "): yield aa

    import dis; return "\n".join(recurse(self.compile()))

  @staticmethod
  def test():
    ss = "def foo():\n def bar(): pass\n return bar()"; print( ss )
    cc = compile(ss, "", "exec")
    tt = codetree(cc); print( tt ); print( tt.dis() )



####
class tree(list):
  def __init__(self, *args): list.__init__(self, args)
  def __iter__(self, depth = 0):
    for idx, aa in list.__iter__(self) ..enumerate():
      if not isinstance(aa, tree): yield depth, idx, self ## return depth, self[idx]
      else:
        for bb in aa.__iter__(depth + 1): yield bb
  def __str__(self): return "\n".join("<%i %i> %r" % (depth, idx, aa[idx]) for depth, idx, aa in self)
  def find(self, match = None, found = None):
    if match is not None: found = lambda aa: aa[2][aa[1]] == match
    for aa in self:
      if found(aa): return aa
  @staticmethod
  def test():
    aa = tree("1", tree("2", "3"), "4")
    for bb in aa: print(bb)



#### tree of lines from indent txt
class tree_from_indent(tree):
  def depth(self, line = None, rgx = re.compile("\S")): return rgx.search(line if line else self[0]).end() - 1
  def ignore(self, line, rgx = re.compile("\S")): return not rgx.search(line) ## ignore blank line
  def _init(self, lines, ignore, aa, depth0):
    if ignore(self, aa): return self._init(lines, ignore, next(lines), depth0)
    depth = self.depth(aa)
    if depth < depth0: return aa
    if depth == depth0:
      self.append(aa)
      return self._init(lines, ignore, next(lines), depth0)
    else:
      # tree.__new__(tree_from_indent) ..self.append(); self[-1].append(aa)
      tree(aa) ..tree_from_indent() ..self.append()
      aa = self[-1]._init(lines, ignore, next(lines), depth)
      return self._init(lines, ignore, aa, depth0)
  def __init__(self, lines, ignore = ignore):
    if isinstance(lines, tree): return tree.__init__(self, *lines)
    lines = iter(lines)
    try: self._init(lines, ignore, next(lines), depth0 = 0)
    except StopIteration: pass
  @staticmethod
  def test():
    print(__file__)
    ss = open(__file__).readlines()
    tt = tree_from_indent(ss)
    print(tt, "\nlen=%i" %len(tt))







######## setup
if "_SETUP" in globals():
  from distutils import command, core, dist, log
  def system(cmd): print( cmd ); return subprocess.check_call(cmd, shell = True)

  class dev(core.Command):
    description = "developer stuff"
    user_options = [("alias=", None, "alias package"),
                    ("doc", None, "print doc"),
                    ("pkginfo", None, "create pkg-info"),
                    ("readme", None, "readme"),
                    ("quicktest", None, "run quick tests"),
                    ("sdist-test=", None, "test sdist package"),
                    ("uninstall=", None, "uninstall"),
                    ]

    def initialize_options(self):
      for aa in self.user_options: setattr(self, aa[0].replace("=", "").replace("-", "_"), aa[1])

    def finalize_options(self): pass

    def run(self):
      DISTRIBUTION.run_command("build") ## auto build
      if self.alias:
        assert self.alias != "ascii" + "porn", self.alias
        try: dpath = os.path.abspath(self.alias); assert (os.getcwd() + "/") in dpath, (os.getcwd(), dpath); system("rm -r %s/*" % dpath)
        except subprocess.CalledProcessError: traceback.print_exc()
        for aa in _MANIFEST.split("\n"):
          bb = "setup.py" if aa == "_setup.py" else aa.replace("numbytes", self.alias)
          if "README" not in aa:
            print( "aliasing %s -> %s" % (aa, bb) )
            if aa[-4:] not in ".bmp .png": ss = open(aa).read().replace("numbytes", self.alias); open(bb, "w").write(ss)
            else: system("  cp -a %s %s" % (aa, bb))
        system("python3.1 setup.py %s" % " ".join(sys.argv[3:])); exit()
      if self.doc: system("python3.1 -c 'import numbytes; help(numbytes)'")
      if self.pkginfo: DISTRIBUTION.metadata.write_pkg_file(open("PKG-INFO", "w"))
      if self.readme: import pydoc; pydoc.pager(_README)
      if self.quicktest: system("python3.1 -c 'import numbytes; numbytes.numbytes.test()'")
      if self.uninstall: cmd_obj = DISTRIBUTION.get_command_obj("install"); cmd_obj.prefix = self.uninstall; cmd_obj.ensure_finalized(); system("rm -Ir %s" % os.path.join(cmd_obj.install_lib, "numbytes"))

  ## custom Distribution class
  class Distribution(dist.Distribution):
    def __init__(self, *args, **kwds): dist.Distribution.__init__(self, *args, **kwds); self.cmdclass["dev"] = dev; global DISTRIBUTION; DISTRIBUTION = self;

    def run_command(self, command):
      if self.have_run.get(command): return # Already been here, done that? then return silently.
      log.info("\nrunning %s", command); cmd_obj = self.get_command_obj(command); cmd_obj.ensure_finalized() ## get cmd
      if 0: print( "DEBUG %s\tcmd_obj=%s\tsub_cmd=%s" % (command, cmd_obj, cmd_obj.get_sub_commands()) ) ## DEBUG

      ## pre hack
      if 1: cmd_obj.byte_compile = lambda *args, **kwds: None ## disable byte compile
      if command == "build_ext":
        @closure()
        def _(self = cmd_obj, build_extension = cmd_obj.build_extension):
          def fnc(*args):
            self.compiler.compiler_so += "-O0".split(" ") ## add compiler flag
            for aa in "-Wstrict-prototypes -O3".split(" "): ## remove compiler flag
              if aa in self.compiler.compiler_so: self.compiler.compiler_so.remove(aa)
            return build_extension(*args)
          self.build_extension = fnc



          ss = ""; aa = open("numbytes/_numbytes.cpp").read();

          # def ignore(self, line): return tree_from_indent.ignore(self, line) or line[0] == "#"
          # bb = aa.split("\n") ..tree_from_indent(ignore = ignore);
          # depth, idx, node = bb.find("  template <typename TT> class view {")
          # print(node[idx+2])

          bb = re.match(".*?\*pyerr\(.*?\n", aa, re.S).group(); ss += "\n#ifndef ASCIIPORN\n%s\n#undef ASCIIPORN\n#endif\n" % bb ## header

          ss += "\n#ifndef ASCIIPORN\nnamespace NUMBYTES {\n#endif\n" ## namespace - beg
          bb = re.search("namespace NUMBYTES {.*?\n  };", aa, re.S).group()
          ss += ";".join(re.findall("\n  inline .*?\)", bb)) + ";\n" ## header

          bb = "".join(re.findall("\n    \w.*", bb)); bb = re.sub("\).*", ");", bb)
          ss += "\n#ifndef ASCIIPORN\ntemplate <typename TT> class tview { public:\n%s\n};\n#endif\n" % bb ## template

          bb = "\n".join(re.findall(" PROTOTYPE .*", bb)).replace("(", "(PyObject *self, ").replace(", )", ")").replace("PyObject *self, PyTypeObject", "PyTypeObject").replace(" static " , " ").replace(" inline ", " "); ss += bb ## prototype

          ss += "\n#ifdef ASCIIPORN\n"
          bb = "\n".join(re.findall(".*PyObject \*self, PyObject \*args.*", bb)) ## filter (self, args) methods
          cc = re.sub("((\w+)\(.*\))", "\\1 { METH_TT(\\2(args), NULL); }", bb).replace("METH_TT(static_", "STATMETH_TT(static_"); ss += cc ## flesh
          pygetset = ""; pymethod = ""
          for cc in (aa.group()[:-1] for aa in re.finditer("\w+\(", bb)):
            if "get_" in cc: pygetset += "{(char *) \"%s\", (getter) %s},\n" % (cc[4:], cc)
            elif "static_" in cc: pymethod += "{\"%s\", %s, METH_STATIC | METH_VARARGS},\n" % (cc[7:], cc)
            else: pymethod += "{\"%s\", %s, METH_VARARGS},\n" % (cc, cc)
          ss += "\nPyGetSetDef PYGETSET[] = {\n%s\n{NULL}};\n" % pygetset
          ss += "\nPyMethodDef PYMETHOD[] = {\n%s\n{NULL}};\n" % pymethod
          ss += "\n#endif\n"
          ss += "\n#ifndef ASCIIPORN\n}\n#endif\n" ## namespace - end

          ss += "\n#ifdef ASCIIPORN\nnamespace numbytes {\n"
          bb = re.search("namespace numbytes {.*?\n}", aa, re.S).group() ## template
          ss += ";\n".join(re.findall(" PROTOTYPE .*?\)", bb)) + ";\n"
          ss += "\n}\n#endif\n"

          ss = ss.replace(" PROTOTYPE ", " ")

          open("numbytes/_numbytes.hpp", "w").write(ss)



      if command == "sdist": open("MANIFEST", "w").write(_MANIFEST)

      cmd_obj.run(); self.have_run[command] = 1 ## run cmd

      ## post hack
      if command == "build": system("cp %s/numbytes/_numbytes.so numbytes" % cmd_obj.build_lib) ## copy built library
      if command == "sdist":
        if os.path.exists("index_html"): system("cp %s index_html/sdist/%s" % (cmd_obj.archive_files[0], os.path.basename(cmd_obj.archive_files[0]))) ## archive sdist

  core.setup(
    distclass = Distribution,
    name = "numbytes",
    version = _VERSION,
    author = "kai zhu",
    author_email = "kaizhu256@gmail.com",
    url = "http://pypi.python.org/pypi/numbytes",
    description = _DESCRIPTION,
    long_description = _README,
    packages = ["numbytes"],
    ext_modules = [core.Extension("numbytes._numbytes", sources = ["numbytes/_numbytes.cpp"], libraries = ["png"])],
    data_files = [("lib/python3.1/site-packages/numbytes", ["numbytes/mario.png"])],

    classifiers = [
    "Development Status :: 3 - Alpha",
    # "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    # "Operating System :: POSIX",
    "Operating System :: POSIX :: Linux",
    # "Operating System :: Unix",
    "Programming Language :: C",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.1",
    "Topic :: Multimedia",
    "Topic :: Multimedia :: Graphics",
    # "Topic :: Multimedia :: Graphics :: 3D Modeling",
    # "Topic :: Multimedia :: Graphics :: 3D Rendering",
    # "Topic :: Multimedia :: Graphics :: Capture",
    # "Topic :: Multimedia :: Graphics :: Capture :: Digital Camera",
    # "Topic :: Multimedia :: Graphics :: Capture :: Scanners",
    # "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
    # "Topic :: Multimedia :: Graphics :: Editors",
    # "Topic :: Multimedia :: Graphics :: Editors :: Raster-Based",
    # "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
    "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    # "Topic :: Multimedia :: Graphics :: Presentation",
    # "Topic :: Multimedia :: Graphics :: Viewers",
    # "Topic :: Scientific/Engineering",
    # "Topic :: Scientific/Engineering :: Artificial Intelligence",
    # "Topic :: Scientific/Engineering :: Astronomy",
    # "Topic :: Scientific/Engineering :: Atmospheric Science",
    # "Topic :: Scientific/Engineering :: Bio-Informatics",
    # "Topic :: Scientific/Engineering :: Chemistry",
    # "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    # "Topic :: Scientific/Engineering :: GIS",
    # "Topic :: Scientific/Engineering :: Human Machine Interfaces",
    "Topic :: Scientific/Engineering :: Image Recognition",
    # "Topic :: Scientific/Engineering :: Information Analysis",
    # "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
    "Topic :: Scientific/Engineering :: Mathematics",
    # "Topic :: Scientific/Engineering :: Medical Science Apps.",
    # "Topic :: Scientific/Engineering :: Physics",
    "Topic :: Scientific/Engineering :: Visualization",
    # "Topic :: Software Development",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: Libraries :: Python Modules",
    # "Topic :: System :: Emulators",
    # "Topic :: System :: Shells",
    # "Topic :: System :: System Shells",
    # "Topic :: Utilities",
    ])







if _IMPORT_EXTENSION: ######## import extension
  import numbytes; from numbytes import _numbytes; from numbytes._numbytes import *
  class numbytes(_numbytes._numbytes):
    def recast(self, tcode, force = None):
      if not force and tcode == self.tcode: return self
      return bytearray(len(self) * self.tsize_from_tcode(tcode)) ...self.base.recast(tcode).reshape(self.shape0, self.shape1).retype(type(self))

    def __copy__(self): return self.recast(self.tcode, force = True)

    def debug(self): print("%s %s tsize=%s shape=<%s %s> strides=<%s %s> transposed=%s" % (type(self), self.tcode, self.tsize, self.shape0, self.shape1, self.strides0, self.strides1, self.transposed))

    def __new__(type, tcode, arr, shape0 = 1, shape1 = -1):
      if 0: print( tcode, arr, shape0, shape1) ## DEBUG
      if is_numbytes(arr): return arr.recast(tcode, force = None).reshape(shape0, shape1)
      if isinstance(arr, bytearray): assert len(arr) >= 1, "array cannot be zero"; return _numbytes._numbytes.__new__(type, tcode, arr).reshape(shape0, shape1) ## bytearray
      elif isinstance(arr, bytes): arr = bytearray(arr) ## bytes
      elif is_seq(arr): arr = type.bytes_from_itr(tcode, len(arr), iter(arr)) ## seq
      elif is_itr(arr): arr = type.bytes_from_itr(tcode, shape0 * (shape1 if shape1 > 0 else 1), arr) ## itr
      else: ## number
        if shape1 == -1: shape1 = 1
        self = bytearray(shape0 * shape1 * type.tsize_from_tcode(tcode))
        self = numbytes.__new__(type, tcode, self, shape0, shape1)
        self[:, :] = arr; return self
      return numbytes.__new__(type, tcode, arr, shape0, shape1)

    def __iter__(self): return iter(self.base)

    def __getitem__(self, slices): return getattr(self, "__getitem")(*slices)

    def __setitem__(self, slices, aa):
      if not isinstance(aa, numbytes) and is_seq(aa): aa = numbytes(aa, self.tcode)
      self.base.__setitem__(slices, aa); return self

    def rows(self):
      for ii in range(self.shape0): yield self[ii, :]

    def __str__(self):
      rows, cols = screensize(); ss = []; ll = min(self.shape1, cols / 2)
      for ii in min(self.shape0, rows / 2) ..range():
        aa = "[%s]" % self[ii, :ll].base ..str()[:-1]
        if not ii: aa = "[" + aa;
        if len(aa) > cols: aa = "%s...]" % aa[:cols - 4]
        ss.append(aa)
      if ii + 1 < self.shape0: ss[-1] += "..."
      ss[-1] += "]"
      if len(ss[-1]) > cols: ss[-1] = ss[-1][:cols - 8] + ss[-1][-8:]
      return "\n" + "\n".join(ss)

    def math_iop3(self, op, aa, bb): self.base.math_iop3(op, aa if is_numbytes(aa) else numbytes(self.tcode, aa), bb if is_numbytes(bb) else numbytes(self.tcode, bb)); return self

    @staticmethod
    def test():
      bb = numbytes(numbytes.II, range(64), 4, -1)
      bb.recast(numbytes.CC) ..print()
      bb = bb.__copy__(); bb.debug()
      # bb[1:, 1:] = 1
      print(bb)
      bb += 2
      print(bb)
      # numbytes(numbytes.CC, 8)
      # bb ^= 0xfffffff
      # bb %= 44
      # print(bb)
      # # print(bb + bb.recast(numbytes.FF))
      # print(bb * 2)
      # print(is_itr(bb))
      # bb.recast("f").debug()

  @closure()
  def _():
    global test; test = numbytes.test ## default test = numbytes.test
    ss = os.path.join(__path__[0], "_numbytes.cpp") ..open().read()
    aa = re.search("enum code_TT {(.*?)}", ss, re.S).group(1).replace("=", "=ord(").replace(",", ");").replace("code_", "numbytes."); exec(aa)
    aa = re.search("enum MATH_OP {(.*?)}", ss, re.S).group(1).replace("'", "").replace("MATH_", "")
    for aa in re.finditer("\w.*?,", aa):
      fname, op = aa.group()[:-1].split('='); ll = int(fname[-1]); op = ord(op); fname = fname[:-1].lower()
      @closure()
      def _(fname = fname, op = op, ll = ll):
        def _(self, aa = 0, bb = 0): return self.math_iop3(op, aa, bb)
        def __(self, aa = 0, bb = 0): return _(self.__copy__(), aa, bb)
        if fname in "abs add and bool ceil divmod eq floor floordiv ge gt invert le lshift lt mod mul ne neg or pos pow radd rand rdivmod rfloordiv rlshift rmod rmul ror round rpow rrshift rshift rsub rtruediv rxor sub truediv trunc xor":
          setattr(numbytes, "__i%s__" % fname, _); setattr(numbytes, "__%s__" % fname, __)
        else: setattr(numbytes, "i%s" % fname, _); setattr(numbytes, "%s" % fname, __)

  class img2txt(object):
      def _shape(self): return self.barr[0] * 256 + self.barr[1], self.barr[2] * 256 + self.barr[3]
      shape = property(_shape)
      def __str__(self): return ansi_str(self.barr)
      def topng(self, fpath): png_write(fpath, self.barr)

      @staticmethod
      def test():
        ipath = os.path.join(__path__[0], "mario.png")
        ipath ..print()
        png2txt(ipath) ..print()
        # numbytes.test()
        # codetree.test()

  def png2txt(fpath, scale = 1, plaintxt = None, wmatch = 2, wmismatch = 4): aa = img2txt(); aa.barr = png_read(fpath, scale, True if plaintxt else False, wmatch, wmismatch); return aa

  # if "numbytes" not in globals(): numbytes = img2txt
  # ## quicktest
  # def quicktest(ipath = ""):
    # ## img2txt
    # if not ipath: ipath = os.path.join(__path__[0], "mario.png")
    # ipath ..print()
    # png2txt(ipath) ..print()
    # numbytes.test()
    # codetree.test()
