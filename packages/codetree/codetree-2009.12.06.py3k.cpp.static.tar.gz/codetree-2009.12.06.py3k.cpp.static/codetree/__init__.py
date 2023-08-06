import os, sys, traceback
if os.name != "posix": sys.stderr.write("\ncodetree requires linux operating system\n\n"); exit()
if sys.version_info[:2] != (3, 1): sys.stderr.write("\ncodetree requires Python 3.1\n\n"); exit()



if 1: #### helper fnc
  def closure(*args, **kwds): return lambda fnc: fnc(*args, **kwds)
  def identity(aa): return aa
  def _import(ss, globals = globals()):
    for aa in ss.split(" "):
      globals[aa] = __import__(aa, globals)
    return identity



#### pseudomethod parser
@_import("ast")
class parser(ast.NodeVisitor):
  @staticmethod
  def exec(ss, globals, fpath): node = parser().parse(ss, fpath, "exec", sugar_pseudomethod = True); cc = compile(node, fpath, "exec"); exec(cc, globals)

  ## recursively print nodes in ast object for debugging
  @staticmethod
  def printnode(node, depth = ""):
    ss = "\t".join("%s %r" % aa for aa in sorted(node.__dict__.items()))
    print( "%s%s\t%s" % (depth, str(type(node)), ss) )
    for aa in ast.iter_child_nodes(node): parser.printnode(aa, depth = depth + " ")

  @_import("re collections")
  def parse(self, ss, fpath, mode, sugar_pseudomethod = None,
            rgx_pseudomethod2 = re.compile("([^.])\.\.\.(\w[\w. ]*\()"),
            rgx_pseudomethod = re.compile("([^.])\.\.(\w[\w. ]*\()"),
            ):
    self.ss0 = ss0 = ss; self.ss = ss; self.fpath = fpath; self.mode = mode

    if sugar_pseudomethod:
      ss = rgx_pseudomethod2.sub("\\1.__pseudomethod2__.\\2", ss) ## parse pseudomethod2 syntax
      ss = rgx_pseudomethod.sub("\\1.__pseudomethod__.\\2", ss) ## parse pseudomethod syntax

    self.node = node = ast.parse(ss, fpath, mode);
    if sugar_pseudomethod: self.calls = collections.deque(); self.visit(node); assert not self.calls ## parse pseudomethod node
    return node

  class exc_revisit(Exception): pass

  def exc_syntax(self, node): return SyntaxError("dangling pseudomethod", (self.fpath, node.lineno, node.col_offset, self.ss0))

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



#### import hook
class _importer(object):
  sugar = "\nfrom __future__ import py3k_sugar\n" ## magic line enabling py3k_sugar syntax
  maxfilesize = 0x100000

  class ImportError(Exception): pass

  def __init__(self):
    _import("locale")  ## BUG - python 3.1
    sys.meta_path[:] = [self] + [aa for aa in sys.meta_path if not hasattr(aa, "py3k_sugar")] ## reset sys.meta_path
    sys.path_importer_cache = {} ## reset cache

  def find_module(self, mname, path = None):
    if 0: print( "py3k_sugar find_module(mname = %s, path = %s)" % (mname, path) ) ## DEBUG
    fname = os.path.join(*mname.split(".")) + ".py"
    for dpath in path or sys.path:
      fpath = os.path.join(dpath, fname)
      if os.path.exists(fpath):
        if os.path.getsize(fpath) > self.maxfilesize: raise self.ImportError("py3k_sugar - %s > %i bytes" % (fpath, self.maxfilesize))
        with open(fpath, "r") as f:
          ss = f.read(1024)
          if self.sugar in ss:
            ss = ss.replace(self.sugar, "\n#%s" % self.sugar[1:], 1); self.found = fpath, ss + f.read(); return self

  @_import("importlib importlib.util")
  @importlib.util.set_loader
  @importlib.util.set_package
  @importlib.util.module_for_loader
  def load_module(self, mm):
    try:
      fpath, ss = self.found; mm.__file__ = fpath
      if 0: print( "py3k_sugar load_module(mm = %s, fpath = %s)" % (mm, fpath) ) ## DEBUG
      parser.exec(ss, mm.__dict__, fpath); return mm ## parse & load module
    except: print( "\nFAILED py3k_sugar load_module(mm = %s, fpath = %s)\n" % (mm, fpath) ); raise ## notify user exception originated from failed py3k_sugar import

importer = _importer()
_import("builtins imp"); builtins.reload = imp.reload



@closure() ## import codetree.main
def _():
  if "_IMPORT_EXTENSION" not in globals(): global _IMPORT_EXTENSION; _IMPORT_EXTENSION = True
  fpath, ss = importer.find_module("codetree.main").found
  global __path__; __path__ = [os.path.abspath(os.path.dirname(fpath))]
  parser.exec(ss, globals(), fpath)
