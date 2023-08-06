VERSION = "2009.11.16.py3k.cpp"
MANIFEST = """setup.py
README.numbytes
numbytes/_numbytes.cpp
numbytes/__init__.py
numbytes/lucida06x10.bmp
numbytes/main.py
numbytes/mario.png"""
README = open("README.numbytes").read()
DESCRIPTION = README.split("\n")[0]
README = """REQUIRES PYTHON3.1
test usage: python3.1 setup.py build dev --quicktest
""" + README

import os, shutil, sys, traceback; from distutils import command, core, dist, log
def closure(*args, **kwds): return lambda fnc: fnc(*args, **kwds)
def quicktest(): system("python3.1 -c 'import numbytes; numbytes.quicktest()'")
def system(cmd): print( cmd ); import subprocess; return subprocess.check_call(cmd, shell = True)

class dev(core.Command):
  description = "developer stuff"
  user_options = [
    ("alias=", None, "alias package"),
    ("doc", None, "print doc"),
    ("pkginfo", None, "create pkg-info"),
    ("quicktest", None, "run quick tests"),
    ("sdist-test=", None, "test sdist package"),
    ("uninstall=", None, "uninstall"),
    ]
  def initialize_options(self):
    for aa in self.user_options: setattr(self, aa[0].replace("=", "").replace("-", "_"), aa[1])
  def finalize_options(self): pass
  def run(self):
    if self.alias:
      for aa in MANIFEST.split("\n"):
        if aa == "setup.py": bb = aa; aa = "_setup.py"
        else: bb = aa.replace("numbytes", self.alias)
        print( "aliasing %s -> %s" % (aa, bb) ); ss = open(aa, "rb").read().replace(b"numbytes", self.alias.encode("latin")); open(bb, "wb").write(ss)
      system("python3.1 setup.py %s" % " ".join(sys.argv[3:]))
      exit()
    if self.doc: system("python3.1 -c 'import numbytes; help(numbytes)'")
    if self.pkginfo: DISTRIBUTION.metadata.write_pkg_file(open("PKG-INFO", "w"))
    if self.quicktest: quicktest()
    if self.sdist_test:
      DISTRIBUTION.run_command("sdist")
      system("rm -r test; mkdir test"); os.chdir("test"); print()
      fpath = "numbytes-%s" % VERSION; print(fpath); system("tar -xzf ../index_html/sdist/%s.tar.gz; lndir %s;" % (fpath, fpath)); print()
      system("python3.1 setup.py install --prefix=%s" % self.sdist_test); print()
      try: system("python3.1 setup.py dev --uninstall=%s", self.sdist_test); print()
      except: pass
      system("python3.1 -c 'import numbytes; numbytes.quicktest()'"); print()

    if self.uninstall:
      cmd_obj = DISTRIBUTION.get_command_obj("install"); cmd_obj.prefix = self.uninstall; cmd_obj.ensure_finalized()
      fpath = os.path.join(cmd_obj.install_lib, "numbytes"); print( "uninstalling %s" % fpath); shutil.rmtree(fpath)

## custom Distribution class
class Distribution(dist.Distribution):
  def __init__(self, *args, **kwds): dist.Distribution.__init__(self, *args, **kwds); self.cmdclass["dev"] = dev; global DISTRIBUTION; DISTRIBUTION = self;

  def run_command(self, command):
    if self.have_run.get(command): return # Already been here, done that? then return silently.
    log.info("running %s", command); cmd_obj = self.get_command_obj(command); cmd_obj.ensure_finalized() ## get cmd
    if 0: print( "DEBUG %s\tcmd_obj=%s\tsub_cmd=%s" % (command, cmd_obj, cmd_obj.get_sub_commands()) ) ## DEBUG

    ## pre hack
    if 1: cmd_obj.byte_compile = lambda *args, **kwds: None ## disable byte compile
    if command == "build":
      print( """numbytes requires:
      Python 3.1
      make sure these packages are installed before building""" )
      if sys.version_info[:2] != (3, 1): raise Exception("numbytes requires Python 3.1")
    if command == "build_ext":
      def closure(self = cmd_obj, build_extension = cmd_obj.build_extension):
        def fnc(*args):
          self.compiler.compiler_so += "-O0".split(" ") ## add compiler flag
          for aa in "-Wstrict-prototypes -O3".split(" "): ## remove compiler flag
            if aa in self.compiler.compiler_so: self.compiler.compiler_so.remove(aa)
          return build_extension(*args)
        self.build_extension = fnc
      closure()
    if command == "sdist": open("MANIFEST", "w").write(MANIFEST)

    cmd_obj.run(); self.have_run[command] = 1 ## run cmd

    ## post hack
    if command == "build": shutil.copy2("%s/numbytes/_numbytes.so" % cmd_obj.build_lib, "numbytes") ## copy built library
    if command == "sdist": shutil.copy2(cmd_obj.archive_files[0], "index_html/sdist/%s" % os.path.basename(cmd_obj.archive_files[0])) ## archive sdist

core.setup(
  distclass = Distribution,
  name = "numbytes",
  version = VERSION,
  author = "kai zhu",
  author_email = "kaizhu256@gmail.com",
  url = "http://pypi.python.org/pypi/numbytes",
  description = DESCRIPTION,
  long_description = README,
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
