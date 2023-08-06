from __future__ import division, print_function
import builtins, os, sys, traceback; DEBUG = 0
if sys.version_info[:2] != (3, 1): raise Exception("numbytes requires Python 3.1")



def stdout2str(fnc):
  import io
  with io.StringIO() as f:
    stdout0 = sys.stdout
    try: sys.stdout = f; fnc(); return f.getvalue()
    finally: sys.stdout = stdout0

import collections, types ## codetree
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



import ast
class asttree(object):
  def __init__(self):
    pass

import ast, re ## pseudomethod parser
class parser(ast.NodeVisitor):

  ## recursively print nodes in ast object for debugging
  @staticmethod
  def printnode(node, depth = ""):
    ss = "\t".join("%s %r" % aa for aa in sorted(node.__dict__.items()))
    print( "%s%s\t%s" % (depth, str(type(node)), ss) )
    for aa in ast.iter_child_nodes(node): parser.printnode(aa, depth = depth + " ")

  def parse(self, ss, fpath, mode, sugar_pseudomethod = None, rgx_pseudomethod2 = re.compile("\.\.\.(\w)")):
    self.ss0 = ss0 = ss; self.ss = ss; self.fpath = fpath; self.mode = mode

    if sugar_pseudomethod:
      ss = rgx_pseudomethod2.sub(".__pseudomethod2__.\\1", ss).replace("__pseudomethod2__...", "...").replace("...__pseudomethod2__", "...") ## parse pseudomethod2 syntax
      ss = ss.replace("..", ".__pseudomethod__.").replace("__pseudomethod__..", "..").replace("..__pseudomethod__", "..") ## parse pseudomethod syntax
      ss = ss.replace("\nfrom .__pseudomethod__.", "\nfrom ..").replace(" from .__pseudomethod__.", " from ..") ## ignore .. notation in relative imports

    self.node = node = ast.parse(ss, fpath, mode);

    if sugar_pseudomethod: self.calls = collections.deque(); self.visit(node); assert not self.calls ## parse pseudomethod node

    return node

  class exc_revisit(Exception): pass

  def exc_syntax(self, node): return SyntaxError("un-called pseudomethod", (self.fpath, node.lineno, node.col_offset, self.ss0))

  def visit_Call(self, node):
    node.func.parent = node
    self.calls.append(node)
    try:
      try: self.generic_visit(node)
      except self.exc_revisit: self.generic_visit(node) ## should revisit @ most once
    except self.exc_revisit as node:
      raise self.exc_syntax(node)
    self.calls.pop()

  ## hack node if it contains __pseudomethod__ attr
  def visit_Attribute(self, node):
    node.value.parent = node
    try:
      if node.value.attr not in ("__pseudomethod__", "__pseudomethod2__"): raise Exception
    except:
      return self.generic_visit(node)

    if not hasattr( node, "parent" ): raise self.exc_syntax(node) ## pseudomethod node should always have a parent
    self.calls[-1].args.insert(0 if node.value.attr is "__pseudomethod__" else 1, node.value.value) ## add arg0 to call node
    fnc = ast.copy_location(ast.Name(node.attr, ast.Load()), node) ## create fnc name node
    if isinstance(node.parent, ast.Call): node.parent.func = fnc ## fnc call
    else: node.parent.value = fnc ## method call
    raise self.exc_revisit(node)

  @staticmethod
  def test():
    ss = "AAAA (BBBB)"
    ss = "BBBB .__pseudomethod__.AAAA()"

    ss = "AAAA .BBBB (CCCC)"
    ss = "BBBB .__pseudomethod__ .AAAA()"

    ss = "AAAA (BBBB (CCCC))"
    ss = "CCCC .__pseudomethod__ .AAAA () .__pseudomethod__ .BBBB ()"

    ss = "AAAA .BBBB (CCCC)"
    ss = "CCCC .__pseudomethod__ .AAAA .BBBB ()"

    ss = "AAAA (BBBB, CCCC (DDDD))"
    ss = "DDDD .__pseudomethod__ .CCCC() .__pseudomethod2__ .AAAA(BBBB)"

    if 1: node = parser().parse(ss, "", "exec")
    else: node = ast.parse(ss, "", "exec")
    print( ss ); parser.printnode(node)



import imp, importlib.util ## import hook
class _importer(object):

  sugar = "from __future__ import py3k_sugar\n" ## magic line enabling py3k_sugar syntax
  maxfilesize = 0x100000
  class ImportError(Exception): pass

  def __init__(self):
    import locale  ## BUG - python 3.1
    sys.meta_path[:] = [self] + [aa for aa in sys.meta_path if not hasattr(aa, "py3k_sugar")] ## reset sys.meta_path
    sys.path_importer_cache = {} ## reset cache

  def find_module(self, mname, path = None):
    if 1 and DEBUG: print( "py3k_sugar find_module(mname = %s, path = %s)" % (mname, path) )
    fname = mname.split(".")[-1] + ".py"
    for dpath in path or sys.path:
      fpath = os.path.join(dpath, fname)
      if os.path.exists(fpath):
        if os.path.getsize(fpath) > self.maxfilesize: raise self.ImportError("py3k_sugar - %s > %i bytes" % (fpath, self.maxfilesize))
        with open(fpath, "r") as f:
          ss = f.read(1024)
          if self.sugar in ss: ss = ss.replace(self.sugar, "#" + self.sugar, 1)
          self.found = fpath, ss + f.read(); return self

  @importlib.util.set_loader
  @importlib.util.set_package
  @importlib.util.module_for_loader
  def load_module(self, m):
    try:
      fpath, ss = self.found; m.__file__ = fpath
      if 1 and DEBUG: print( "py3k_sugar load_module(m = %s, fpath = %s)" % (m, fpath) )
      node = parser().parse(ss, fpath, "exec", sugar_pseudomethod = True); cc = compile(node, fpath, "exec"); exec(cc, m.__dict__); return m ## parse & load module
    except: print( "\nFAILED py3k_sugar load_module(m = %s, fpath = %s)\n" % (m, fpath) ); raise ## notify user exception originated from failed py3k_sugar import
importer = _importer()



builtins.reload = imp.reload
if "main" in globals(): reload(main)
import numbytes.main; globals().update(main.__dict__); __name__ = "numbytes"
