## import numbytes; reload(numbytes); from numbytes import *

from __future__ import py3k_sugar
_VERSION = "2009.12.09.py3k.cpp.static"
_MANIFEST = """setup.py
setup.py
README
numbytes/_numbytes.cpp
numbytes/_numbytes.hpp
numbytes/__init__.py
numbytes/lucida06x10.bmp
numbytes/main.py
numbytes/mario.png"""
# if "_README" not in globals(): global _README; _README = ""
# print(_README)
_README = open("README").read()
_DESCRIPTION = re.search("DESCRIPTION: (.*)", _README).group(1)
_README = """REQUIRES PYTHON3.1

QUICK TEST: $ python3.1 setup.py build dev --quicktest

ASCIIPORN - {}
""".format(_README)



if 1: #### helper fnc
  def depth(arr):
    try: return 1 + depth(arr[0])
    except TypeError: return 0

  @_import("functools")
  @functools.wraps(builtins.enumerate)
  def enumerate(arr, i = None): return count(i) ..zip(arr) if i else builtins.enumerate(arr)

  def getitem2(idx, aa): return aa[idx]

  def lens(*args): return [len(aa) for aa in args]

  ## get current screensize - row x col
  @_import("fcntl struct termios")
  def screensize():
    try: return fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, "0123") ...struct.unpack("hh")
    except: return (24, 80)

  def sjoin(arr, _): return _.join(arr)

  @_import("io")
  def stdout2str(fnc):
    import io
    with io.StringIO() as ff:
      stdout0 = sys.stdout
      try: sys.stdout = ff; fnc(); return f.getvalue()
      finally: sys.stdout = stdout0

  ## piped system call
  @_import("subprocess")
  def system(exe): print( exe ); return subprocess.Popen(exe, shell = 1, stdout = subprocess.PIPE, close_fds = 1).stdout.read().decode("latin")

  ## print test log
  def test_class(type, fpath):
    tt = codetree.src(type, fpath) ...codetree.src(type.test)
    rgx = re.compile("^" + " " * tt.depth(tt[1]), re.M)
    for ii, aa in enumerate(tt[1:]):
      print( re.sub(rgx, ">>> ", aa) )
      parser.exec( re.sub(rgx, "", aa), globals() )

  ## generate unique alphanumeric string guaranteed not to occur in s
  def uniquestr(s, kwd = "qjzx"):
    while kwd in s: kwd = kwd + hex(id(kwd))
    return kwd




#### tree
class tree(list):
  def __init__(self, *args): list.__init__(self, args)

  def walk(self, depth = 0):
    for idx, aa in enumerate(self):
      if not isinstance(aa, tree): yield depth, idx, self ## return depth, self[idx]
      else:
        for bb in aa.walk(depth + 1): yield bb

  def __str__(self): return "\n".join("<{} {}> {!r}".format(depth, idx, aa[idx]) for depth, idx, aa in self.walk())

  def find(self, match = None, found = None):
    if match is not None: found = lambda aa: aa[2][aa[1]] == match
    for aa in self.walk():
      if found(aa): return aa

  @staticmethod
  def test():
    aa = tree("1", tree("2", "3"), "4")
    for bb in aa.walk(): print( bb )



#### tree of lines from indent txt
class tree_from_indent(tree):
  def depth(self, line = None, rgx = re.compile("\S")): return rgx.search(line if line else self[0]).end() - 1

  def ignore(self, line, rgx = re.compile("\S")): return not rgx.search(line) ## ignore blank line

  def _init(self, lines, ignore, aa, depth0):
    if ignore(self, aa): return self._init(lines, ignore, next(lines), depth0)
    depth = self.depth(aa)
    if depth < depth0: return aa
    if depth == depth0: self.append(aa); return self._init(lines, ignore, next(lines), depth0)
    else:
      self[-1] = tree(self[-1]) ..tree_from_indent(); self[-1].append(aa)
      aa = self[-1]._init(lines, ignore, next(lines), depth); return self._init(lines, ignore, aa, depth0)

  def __init__(self, lines, ignore = ignore):
    if isinstance(lines, tree): return tree.__init__(self, *lines)
    lines = iter(lines)
    try: self._init(lines, ignore, next(lines), depth0 = 0)
    except StopIteration: pass

  @staticmethod
  def test():
    print( __file__ )
    ss = open(__file__).readlines()
    tt = tree_from_indent(ss)
    print( tt, "\nlen={}".format(len(tt)) )



#### python compiled code object viewer
@_import("types")
class codetree(tree):
  co_args = "co_argcount co_kwonlyargcount co_nlocals co_stacksize co_flags co_code co_consts co_names co_varnames co_filename co_name co_firstlineno co_lnotab co_freevars co_cellvars".split(" ")

  def __init__(self, codeobj, **kwds):
    if isinstance(codeobj, list): list.__init__(self, codeobj)
    else:
      for ii, aa in enumerate(self.co_args):
        bb = getattr(codeobj, aa)
        setattr(self, aa, list(bb) if isinstance(bb, tuple) else bb)
      tree.__init__(self, *(codetree(aa) if isinstance(aa, types.CodeType) else aa for aa in self.co_consts))
      del self.co_consts;
    self.__dict__.update(kwds)

  ## serializable: codetree(codeobj) == eval( repr( codetree( codeobj ) ) )
  def __repr__(self): return "codetree({}, **{})".format(repr(list(self)), self.__dict__)

  def __str__(self, _ = ""):
    _ = _ + "    "; __ = _ + 18 * " "
    ss = []
    for aa in self.co_args:
      if aa != "co_consts": bb = repr(getattr(self, aa))
      else:
        bb = "\n{}".format(__).join(aa.__str__(__) if isinstance(aa, codetree) else str(aa) for aa in self)
        bb = "\n{}{}".format(__, bb)
      "{}{:18}{}".format(_, aa, bb) ..ss.append()
    return "codetree(\n{})".format("\n".join(ss))

  ## codeobj == codetree(codeobj).compile()
  def compile(self):
    args = []
    for aa in self.co_args:
      if aa != "co_consts": bb = getattr(self, aa)
      else: bb = tuple(aa.compile() if isinstance(aa, codetree) else aa for aa in self) ## recurse
      args.append(tuple(bb) if isinstance(bb, list) else bb)
    return types.CodeType(*args)

  ## recursive disassembler
  def dis(self):
    def recurse(aa, _ = ""):
      if isinstance(aa, types.CodeType):
        yield _ + stdout2str(lambda: dis.dis(aa)).replace("\n", "\n" + _)
        for aa in aa.co_consts:
          for aa in recurse(aa, _ + "  "): yield aa
    import dis; return "\n".join(recurse(self.compile()))

  ## attempt to retrieve source code of object
  @staticmethod
  def src(aa, fpath = ""):
    if isinstance(aa, types.FunctionType): rgx = re.compile("\s*def {}\W".format(aa.__name__))
    elif isinstance(aa, type): rgx = re.compile("\s*class {}\W".format(aa.__name__))
    else: raise TypeError("invalid type <{}>".format(type(aa)))
    if isinstance(fpath, tree): tt = fpath
    else:
      fpath = "{}/{}".format(os.path.dirname(sys.modules[aa.__module__].__file__), fpath) if fpath else sys.modules[aa.__module__].__file__
      ss = open(fpath).read(); tt = tree_from_indent(ss.split("\n"))
    for depth, ii, bb in tt.walk():
      if re.match(rgx, bb[ii]): return bb
    raise ValueError("<{}> not found in <{}>".format(repr(aa)[:256], repr(fpath)[:256]))

  @staticmethod
  def test():
    ss = "def foo():\n def bar(): pass\n return bar()"; print( ss )
    cc = compile(ss, "", "exec")
    tt = codetree(cc); print( tt ); print( tt.dis() )
    codetree.src(codetree, "main.py") ...codetree.src(codetree.test) ..print()







if _IMPORT_EXTENSION: ######## import extension
  from numbytes import _numbytes; from numbytes._numbytes import *

  class numbytes(_numbytes._numbytes):
    _base = _numbytes._numbytes

    def debug(self): print( "{} {} refcnt={} tsize={} shape=<{} {}> strides=<{} {}> transposed={}".format(type(self), self.tcode, refcnt(self), self.tsize, self.shape0, self.shape1, self.strides0, self.strides1, self.transposed) )
    def recast(self, tcode):
      arr = bytearray(len(self) * self.tsize_from_tcode(tcode))
      return self._base.__new__(type(self), tcode, arr).reshape(self.shape0, self.shape1) ..self.copy_to()

    def __copy__(self): return self.recast(self.tcode)
    copy = property(__copy__)

    def __new__(type, tcode, arr, shape0 = None, shape1 = -1):
      self = None
      if isinstance(arr, numbytes): self = arr.retype(type).recast(tcode)
      else:
        if isinstance(arr, bytearray): pass
        elif isinstance(arr, bytes): arr = bytearray(bytes)
        elif is_seq(arr):
          self = bytearray(len(arr) * type._base.tsize_from_tcode(tcode))
          self = type._base.__new__(type, tcode, self)
          self.fill_from_itr(iter(arr))
        if self is None: self = type._base.__new__(type, tcode, arr)
      if shape0 is not None: self = self.reshape(shape0, shape1)
      return self

    @staticmethod
    def zeros(tcode, shape0, shape1): return numbytes(tcode, bytearray(shape0 * shape1 * numbytes.tsize_from_tcode(tcode)), shape0, shape1)

    def __getitem__(self, slices):
      if not isinstance(slices, tuple): slices = (slices, slice(None))
      return self._getitem(*slices)

    def __iter__(self): return iter(self.base)

    def rows(self):
      for ii in range(self.shape0): yield self[ii]

    def __setitem__(self, slices, aa):
      if aa is None: return self._getitem(*slices)
      if not is_numbytes(aa):
        if is_itr(aa): self[slices].fill_from_itr(aa); return
        if is_seq(aa): self[slices].fill_from_itr(iter(aa)); return
      return self._setitem(slices, aa)

    def __str__(self):
      rows, cols = screensize(); ss = []; ll = min(self.shape1, cols >> 1)
      for ii in min(self.shape0, rows / 2) ..range():
        aa = "[{}]".format(self[ii, :ll] ..self._base.__str__()[:-1])
        if not ii: aa = "[" + aa;
        if len(aa) > cols: aa = "{}...]".format(aa[:cols - 4])
        ss.append(aa)
      if ii + 1 < self.shape0: ss[-1] += "..."
      ss[-1] += "]"
      if len(ss[-1]) > cols: ss[-1] = ss[-1][:cols - 8] + ss[-1][-8:]
      return "\n".join(ss) + "\n"

    __repr__ = __str__

    @staticmethod
    def test():
      ## subclass numbytes
      class numbytes2(numbytes): pass

      ## create bytearray of 3x4 matrix of int64
      bytes_integer = numbytes2("i", range(12), shape0=3, shape1=4)
      bytes_integer.debug()
      print( bytes_integer )

      ## underlying bytearray object
      print( bytes_integer.bytes )

      ## slice / transpose / reshape
      print( bytes_integer[0, :] )
      print( bytes_integer[1:, 2:] )
      print( bytes_integer.T[2:, 1:] )
      print( bytes_integer.reshape(2, -1) )

      ## recast into double type
      bytes___float = bytes_integer.recast("f") / 3
      print( bytes___float )

      ## most arithmetic operations are inplace
      ## use copy to avoid side-effects
      print( bytes_integer.copy[1:, 2:] + bytes___float.copy[1:, 2:] )
      print( bytes___float.copy[1:, 2:] + bytes_integer.copy[1:, 2:] )
      print( bytes_integer )
      print( bytes_integer + bytes_integer[:, -1]) ## inplace
      print( bytes_integer + bytes_integer.T[1:, 0]) ## inplace
      print( bytes___float )
      print( bytes___float.sqrt() ) ## inplace
      print( bytes___float ** 2 ) ## inplace

      ## inplace exceptions are logical comparisons,
      ## which return new char-typed arrays
      print( bytes___float )
      print( bytes___float == bytes___float[:, 1] )
      print( bytes___float > 1.5 )

      ## 
      print( bytes_integer )
      for aa in bytes_integer.rows(): print( aa )

  @closure()
  def _():
    if "numbytes" not in globals(): global numbytes; numbytes = numbytes

    for aa in "eq ne lt le gt ge".split(" "): ## bool comparison
      @closure()
      def _(aa = "__{}__".format(aa)):
        def _(self, bb):
          cc = self.zeros("c", self.shape0, self.shape1)
          return getattr(cc._base, aa)(cc, self, bb)
        setattr(numbytes, aa, _)







######## setup
if "_SETUP" in globals():
  from distutils import command, core, dist, log
  def system0(cmd): print( cmd ); return subprocess.check_call(cmd, shell = True)

  class dev(core.Command):
    description = "developer stuff"
    user_options = [("alias=", None, "alias package"),
                    ("doc", None, "print doc"),
                    ("pkginfo", None, "create pkg-info"),
                    ("readme", None, "readme"),
                    ("quicktest", None, "run quick tests"),
                    ("sdist-test=", None, "test sdist package"),
                    ("test=", None, "test specific functionality"),
                    ("uninstall=", None, "uninstall"),
                    ]

    def initialize_options(self):
      for aa in self.user_options: setattr(self, aa[0].replace("=", "").replace("-", "_"), aa[1])

    def finalize_options(self): pass

    @staticmethod
    def update_pkginfo():
      global _README; DISTRIBUTION.metadata.long_description = _README + "DEMO USAGE:\n\n>>> from numbytes import *\n" + system( "python3.1 -c 'import numbytes; numbytes.test_class(numbytes.numbytes, \"main.py\")'" )
      DISTRIBUTION.metadata.write_pkg_file(open("README", "w")); import pydoc; pydoc.pager(open("README").read())

    def run(self):
      DISTRIBUTION.run_command("build") ## auto build
      if self.alias:
        assert self.alias != "ascii" + "porn", self.alias
        try: dpath = os.path.abspath(self.alias); assert (os.getcwd() + "/") in dpath, (os.getcwd(), dpath); system0( "rm -r {}/*".format(dpath) )
        except subprocess.CalledProcessError: traceback.print_exc()
        for aa in _MANIFEST.split("\n"):
          bb = "setup.py" if aa == "_setup.py" else aa.replace("numbytes", self.alias)
          if "README" in aa: system0( "cp README.{} README".format(self.alias) )
          else:
            print( "aliasing {} -> {}".format(aa, bb) )
            if aa[-4:] not in ".bmp .png": ss = open(aa).read().replace("README", "README").replace("numbytes", self.alias).replace('_MANIFEST = """setup.py', '_MANIFEST = """setup.py'); open(bb, "w").write(ss)
            else: system0( "  cp -a {} {}".format(aa, bb) )
        system0( "python3.1 setup.py {}".format(" ".join(sys.argv[3:])) ); exit()
      if self.doc: system0( "python3.1 -c 'import numbytes; help(numbytes)'" )
      if self.pkginfo: self.update_pkginfo()
      if self.quicktest: system0( "python3.1 -c 'import numbytes; numbytes.test_class(numbytes.numbytes, \"main.py\")'" )
      if self.test: system0( "python3.1 -c 'import numbytes; numbytes.test_class(numbytes.{}, \"main.py\")'".format(self.test) )
      if self.uninstall: cmd_obj = DISTRIBUTION.get_command_obj("install"); cmd_obj.prefix = self.uninstall; cmd_obj.ensure_finalized(); system0( "rm -Ir {}".format(os.path.join(cmd_obj.install_lib, "numbytes")) )

  ## custom Distribution class
  class Distribution(dist.Distribution):
    def __init__(self, *args, **kwds): dist.Distribution.__init__(self, *args, **kwds); self.cmdclass["dev"] = dev; global DISTRIBUTION; DISTRIBUTION = self;

    def run_command(self, command):
      if self.have_run.get(command): return # Already been here, done that? then return silently.
      log.info("\nrunning {}".format(command)); cmd_obj = self.get_command_obj(command); cmd_obj.ensure_finalized() ## get cmd
      if 0: print( "DEBUG {}\tcmd_obj={}\tsub_cmd={}".format(command, cmd_obj, cmd_obj.get_sub_commands()) ) ## DEBUG

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

          hpp = "" ## numbytes header

          ## numbytes.hpp
          stat = ""; init = ""
          ss = open("numbytes/_numbytes.cpp").read() ....re.sub("// .*", "") ....re.sub("#.*", "")

          for aa in "NUMBYTES_METH static PyObject \*(\w+)" ..re.findall(ss): ## numbytes
            if "get_" in aa: ## getset
              stat += "NUMBYTES_METH(PyObject *, {}, NULL, TCODE_SELF(self));\n".format(aa)
              init += "GETSET.add(\"{}\", {});\n".format(aa.replace("get_", ""), aa)
            elif "static_" in aa: ## staticmethod
              stat += "NUMBYTES_METH(PyObject *, {}, NULL, TCODE_ARGS(args));\n".format(aa)
              init += "METHOD.add(\"{}\", {}, METH_VARARGS | METH_STATIC);\n".format(aa.replace("static_", ""), aa)
            else: ## method
              stat += "NUMBYTES_METH(PyObject *, {}, NULL, TCODE_SELF(self));\n".format(aa)
              init += "METHOD.add(\"{}\", {}, METH_VARARGS);\n".format(aa, aa)

          for aa in "MATH_IOP.\((\w+)" ..re.findall(ss): ## numbytes
            init += "METHOD.add(\"{}\", {}, METH_VARARGS);\n".format(aa.replace("math_", ""), aa)

          hpp = "namespace NUMBYTES {{\n{}\nstruct _init {{\n_init() {{\n{}\n}}\n}} __init;\n}}".format(stat, init)

          open("numbytes/_numbytes.hpp", "w").write(hpp)

      if command == "sdist": dev.update_pkginfo(); open("MANIFEST", "w").write(_MANIFEST)

      if command == "upload": DISTRIBUTION.run_command("sdist")

      cmd_obj.run(); self.have_run[command] = 1 ## run cmd

      ## post hack
      if command == "build": system0( "cp {}/numbytes/_numbytes.so numbytes".format(cmd_obj.build_lib) ) ## copy built library
      if command == "sdist":
        if os.path.exists("index_html"): system0( "cp {} index_html/sdist/{}".format(cmd_obj.archive_files[0], os.path.basename(cmd_obj.archive_files[0])) ) ## archive sdist

  core.setup(
    distclass = Distribution,
    name = "numbytes",
    version = _VERSION,
    author = "kai zhu",
    author_email = "kaizhu256@gmail.com",
    license = "gpl",
    url = "http://pypi.python.org/pypi/numbytes",
    description = _DESCRIPTION,
    # long_description = _README,
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
    "Operating System :: POSIX",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: C",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.1",
    "Topic :: Multimedia",
    "Topic :: Multimedia :: Graphics",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Scientific/Engineering :: Visualization",
    "Topic :: Software Development",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: Libraries :: Python Modules",
    # "Topic :: System :: Emulators",
    # "Topic :: System :: Shells",
    # "Topic :: System :: System Shells",
    # "Topic :: Utilities",
    ])
