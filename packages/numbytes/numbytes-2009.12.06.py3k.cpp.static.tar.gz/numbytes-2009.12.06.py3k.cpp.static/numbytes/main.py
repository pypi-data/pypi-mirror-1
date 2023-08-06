## import numbytes; reload(numbytes); from numbytes import *

from __future__ import py3k_sugar
_VERSION = "2009.12.06.py3k.cpp.static"
_MANIFEST = """setup.py
setup.py
README.numbytes
numbytes/_numbytes.cpp
numbytes/_numbytes.hpp
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
20091205 - moved source code to c++
20091116 - package integrated
20081219
- tobias rodaebel points out ".." is used in relative imports as well.
  fixed pseudomethod 2 be compatible w/ this
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

  def getitem2(idx, aa): return aa[idx]

  def lens(*args): return [len(aa) for aa in args]

  re_type = re.compile("")
  re.sub2 = lambda ss, aa, bb, *args, **kwds: re.sub(aa, bb, ss, *args, **kwds)

  ## get current screensize - row x col
  @_import("fcntl struct termios")
  def screensize(): return fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, "0123") ...struct.unpack("hh")

  def sjoin(arr, _): return _.join(arr)

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

  @_import("types")
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



#### tree
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
            if aa[-4:] not in ".bmp .png": ss = open(aa).read().replace("numbytes", self.alias).replace('_MANIFEST = """setup.py', '_MANIFEST = """setup.py'); open(bb, "w").write(ss)
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

          hpp = "" ## numbytes header

          ## numbytes.hpp
          stat = ""; init = ""
          ss = open("numbytes/_numbytes.cpp").read() ..re.sub2("// .*", "") ..re.sub2("#.*", "")

          for aa in "NUMBYTES_METH static PyObject \*(\w+)" ..re.findall(ss): ## numbytes
            if "get_" in aa: ## getset
              stat += "NUMBYTES_METH(PyObject *, %s, NULL, TCODE_SELF(self));\n" % aa
              init += "GETSET.add(\"%s\", %s);\n" % (aa.replace("get_", ""), aa)
            elif "static_" in aa: ## staticmethod
              stat += "NUMBYTES_METH(PyObject *, %s, NULL, TCODE_ARGS(args));\n" % aa
              init += "METHOD.add(\"%s\", %s, METH_VARARGS | METH_STATIC);\n" % (aa.replace("static_", ""), aa)
            else: ## method
              stat += "NUMBYTES_METH(PyObject *, %s, NULL, TCODE_SELF(self));\n" % aa
              init += "METHOD.add(\"%s\", %s, METH_VARARGS);\n" % (aa, aa)

          for aa in "MATH_IOP.\((\w+)" ..re.findall(ss): ## numbytes
            init += "METHOD.add(\"%s\", %s, METH_VARARGS);\n" % (aa.replace("math_", ""), aa)

          # for aa in "MATH_IOP2\((\w+)" ..re.findall(ss): ## numbytes
            # init += "METHOD.add(\"%s\", %s, METH_VARARGS);\n" % (aa, aa)

          # for aa in "MATH_IOP2\((\w+)" ..re.findall(ss): ## numbytes
            # init += "METHOD.add(\"%s\", %s, METH_VARARGS);\n" % (aa, aa)

          hpp = "namespace NUMBYTES {\n%s\nstruct _init {\n_init() {\n%s\n}\n} __init;\n}" % (stat, init)

          open("numbytes/_numbytes.hpp", "w").write(hpp)

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







if _IMPORT_EXTENSION: ######## import extension
  from numbytes import _numbytes; from numbytes._numbytes import *

  class numbytes(_numbytes._numbytes):
    _base = _numbytes._numbytes

    def debug(self): print("%s %s refcnt=%s tsize=%s shape=<%s %s> strides=<%s %s> transposed=%s" % (type(self), self.tcode, refcnt(self), self.tsize, self.shape0, self.shape1, self.strides0, self.strides1, self.transposed))
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

    def __getitem__(self, slices): return self._getitem(*slices)

    def __setitem__(self, slices, aa):
      if aa is None: return self._getitem(*slices)
      if not is_numbytes(aa):
        if is_itr(aa): self[slices].fill_from_itr(aa); return
        if is_seq(aa): self[slices].fill_from_itr(iter(aa)); return
      return self._setitem(slices, aa)

    def __str__(self):
      rows, cols = screensize(); ss = []; ll = min(self.shape1, cols >> 1)
      for ii in min(self.shape0, rows / 2) ..range():
        aa = "[%s]" % self[ii, :ll] ..self._base.__str__()[:-1]
        if not ii: aa = "[" + aa;
        if len(aa) > cols: aa = "%s...]" % aa[:cols - 4]
        ss.append(aa)
      if ii + 1 < self.shape0: ss[-1] += "..."
      ss[-1] += "]"
      if len(ss[-1]) > cols: ss[-1] = ss[-1][:cols - 8] + ss[-1][-8:]
      return "\n" + "\n".join(ss)

    @staticmethod
    def test():
      class numbytes2(numbytes): pass
      ff = numbytes2("f", range(1<<16), 2, -1)
      ff = numbytes2("f", (-1, 0, 1, 2, 3, 4, 5, 6,), 2, -1)
      ii = ff.recast("i"); cc = ff.recast("c"); ff.debug(); ii.debug(); cc.debug()
      print(ff)
      print(ff.copy == ff)
      print(ff.copy.fma(2, 3))
      print(ii.copy + (ff.copy - 0.3))
      print(cc.copy.log2())
      print(ii.copy.log2())
      print(cc.copy.popcount())
      print(ii.copy.popcount())

  @closure()
  def _():
    if "numbytes" not in globals(): global numbytes; numbytes = numbytes

    for aa in "eq ne lt le gt ge".split(" "): ## bool comparison
      @closure()
      def _(aa = "__%s__" % aa):
        def _(self, bb):
          cc = self.zeros(self.tcode, self.shape0, self.shape1)
          return getattr(cc._base, aa)(cc, self, bb)
        setattr(numbytes, aa, _)
