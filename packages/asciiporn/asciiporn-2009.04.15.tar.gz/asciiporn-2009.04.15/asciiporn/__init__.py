"""
type\n>>> help(asciiporn.main)\nfor main documentation
"""

from __future__ import division, print_function
import os, sys, traceback
if sys.version_info[0] is not 2: raise Exception("asciiporn requires Python 2.x")
if sys.version_info[1] < 6: raise Exception("asciiporn requires Python 2.6 or higher")
if "DEBUG" not in globals(): DEBUG = 0 ## True prints debug info



def stdout2str(fnc):
  import io
  with io.BytesIO() as f:
    stdout0 = sys.stdout
    try: sys.stdout = f; fnc(); return f.getvalue()
    finally: sys.stdout = stdout0

import collections, types ## codetree
class codetree(object):

  co_args = "co_argcount co_nlocals co_stacksize co_flags co_code co_consts co_names co_varnames co_filename co_name co_firstlineno co_lnotab co_freevars co_cellvars".split(" ")
  co_constsi = co_args.index("co_consts") ## co_consts index pos

  def __init__(self, codeobj = None, **kwds):
    if codeobj: ## codeobj
      self.__dict__ = dict((x, getattr(codeobj, x)) for x in self.co_args)
      self.co_consts = tuple(codetree(x) if isinstance(x, types.CodeType) else x for x in codeobj.co_consts) ## recurse
    self.__dict__.update(kwds)

  def __eq__(self, x): return type(self) == type(x) and self.__dict__ == x.__dict__

  ## serializable: codetree(codeobj) == eval( repr( codetree( codeobj ) ) )
  def __repr__(self): return "codetree(**%r)" % self.__dict__

  def __str__(self, _ = ""):
    arr = collections.deque()
    arr.append("codetree(\n")
    for k, x in sorted(x for x in self.__dict__.iteritems() if x[0] != "co_consts"):
      arr.append("%s%s = %s%r,\n" % ( _, k, " " * (16 - len(k)), x ))
    for x in self.co_consts:
      arr.append("%s  %s,\n" % ( _, x.__str__(_ + "  ") if isinstance(x, codetree) else x ))
    arr.append(_ + ")")
    return "".join(arr)

  ## codeobj == codetree(codeobj).compile()
  def compile(self):
    args = [getattr(self, x) for x in self.co_args] ## create list of args
    args[self.co_constsi] = tuple(x.compile() if isinstance(x, codetree) else x for x in self.co_consts) ## recurse
    return types.CodeType(*args)

  ## recursive disassembler
  def dis(self):

    def recurse(x, _ = ""):
      if isinstance(x, types.CodeType):
        yield _ + stdout2str(lambda: dis.dis(x)).replace("\n", "\n" + _)
        for x in x.co_consts:
          for x in recurse(x, _ + "  "): yield x

    import dis; return "\n".join(recurse(self.compile()))

  @staticmethod
  def test():
    c = compile("def foo():\n def bar(): pass\n return bar()", "", "exec")
    t = codetree(c); print( t ); print( t.dis() )



import ast, re ## pseudomethod parser
class parser(ast.NodeVisitor):

  ## recursively print nodes in ast object for debugging
  @staticmethod
  def printnode(node, depth = ""):
    s = "\t".join("%s %r" % x for x in sorted(node.__dict__.iteritems()))
    print( "%s%s\t%s" % (depth, str(type(node)), s) )
    for x in ast.iter_child_nodes(node): parser.printnode(x, depth = depth + " ")

  def parse(self, s, fpath, mode, rgx_p2 = re.compile("\.\.\.(\w)")):
    self.s0 = s0 = s

    s = s.replace(".items()", ".iteritems()").replace(".keys()", ".iterkeys()").replace(".values()", ".itervalues()")
    s = s.replace("__next__", "next") ## PEP3114  Renaming iterator.next() to iterator.__next__()
    s = rgx_p2.sub(".__pseudomethod2__.\\1", s).replace("__pseudomethod2__...", "...").replace("...__pseudomethod2__", "...") ## parse pseudomethod2 syntax
    s = s.replace("..", ".__pseudomethod__.").replace("__pseudomethod__..", "..").replace("..__pseudomethod__", "..") ## parse pseudomethod syntax
    s = s.replace("\nfrom .__pseudomethod__.", "\nfrom ..").replace(" from .__pseudomethod__.", " from ..") ## ignore .. notation in relative imports

    self.calls = collections.deque()
    try:
      self.s = s; self.fpath = fpath; self.mode = mode
      self.node = node = ast.parse(s, fpath, mode); self.visit(node) ## parse pseudomethod node
      return node
    finally:
      assert not self.calls

  class exc_revisit(Exception): pass

  def exc_syntax(self, node): return SyntaxError("un-called pseudomethod", (self.fpath, node.lineno, node.col_offset, self.s0))

  def visit_Call(self, node):
    node.func.parent = node
    self.calls.append(node)
    try:
      try: self.generic_visit(node)
      except self.exc_revisit: self.generic_visit(node) ## should revisit @ most once
    except self.exc_revisit as (node,):
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
    s = "AAAA (BBBB)"
    s = "BBBB .__pseudomethod__.AAAA()"

    s = "AAAA .BBBB (CCCC)"
    s = "BBBB .__pseudomethod__ .AAAA()"

    s = "AAAA (BBBB (CCCC))"
    s = "CCCC .__pseudomethod__ .AAAA () .__pseudomethod__ .BBBB ()"

    s = "AAAA .BBBB (CCCC)"
    s = "CCCC .__pseudomethod__ .AAAA .BBBB ()"

    s = "AAAA (BBBB, CCCC (DDDD))"
    s = "DDDD .__pseudomethod__ .CCCC() .__pseudomethod2__ .AAAA(BBBB)"

    if 0: node = parser().parse(s, "", "exec")
    else: node = ast.parse(s, "", "exec")
    print( s ); parser.printnode(node)



import imp ## import hook
class _importer(object):

  py3k_syntax = None ## identifier
  magic = "\nfrom __future__ import py3k_syntax\n" ## magic line to enable these syntax sugars

  def __init__(self):
    sys.meta_path[:] = [self] + [x for x in sys.meta_path if not hasattr(x, "py3k_syntax")] ## reset sys.meta_path
    sys.path_importer_cache = {} ## reset cache

  def find_module(self, mname, path = None):
    if 1 and DEBUG: print( "py3k_syntax find_module(mname = %s, path = %s)" % (mname, path) )
    mname = mname.replace("asciiporn.", "") ## BUG - package import

    if path and len(path) is 1:
      x = path[0] + "."
      if mname[:len(x)] == x: mname = mname[len(x):] ## import from package

    try: file, fpath, desc = imp.find_module(mname, path if path else sys.path); tp = desc[2] ## look for modue in path
    except ImportError: return

    if tp is imp.PY_SOURCE: pass
    elif tp is imp.PKG_DIRECTORY: fpath += "/__init__.py"; file = open(fpath) ## use __init__.py for packages
    else: return

    s = "\n" + file.read() + "\n"; file.close()
    if self.magic not in s: return ## no py3k_syntax magic found in file
    s = s.replace(self.magic, "\nfrom __future__ import division, print_function; from asciiporn import *\n", 1)
    s = s[1:-1] ## preserve lineno (for debugging)

    self.found = s, fpath, desc, tp; return self

  def load_module(self, mname):
    s, fpath, desc, tp = self.found
    if 1 and DEBUG: print( "py3k_syntax load_module(mname = %s, fpath = %s, desc = %s)" % (mname, fpath, desc) )

    if mname in sys.modules: m = sys.modules[mname]; new = None ## if exist: use existing module
    else: m = sys.modules[mname] = imp.new_module(mname); new = True ## else: new module
    try:
      node = parser().parse(s, fpath, "exec"); c = compile(node, fpath, "exec"); exec(c, m.__dict__) ## parse & load module
      if tp is imp.PKG_DIRECTORY: m.__path__ = [os.path.dirname(fpath)] ## package.__path__
      m.__file__ = fpath; m.__loader__ = self.load_module; return m
    except:
      if new: del sys.modules[mname] ## if new module fails loading, del from sys.modules
      print( "\nFAILED py3k_syntax load_module(mname = %s, fpath = %s, desc = %s)\n" % (mname, fpath, desc) ) ## notify user exception originated from failed py3k_syntax import
      raise
importer = _importer()



import __builtin__ as builtins, itertools
if 1: ## builtins
  filter = itertools.ifilter
  filterfalse = itertools.ifilterfalse
  map = itertools.imap
  range = xrange
  zip = itertools.izip
  zip_longest = itertools.izip_longest
  def oct(x): return builtins.oct(x).replace("0", "0o", 1)
  def reload(m):
    try:
      if not importer.find_module(m.__name__, path = [os.path.dirname(m.__file__)]): raise ImportError
    except: return builtins.reload(m)
    return importer.load_module(m.__name__)



if "main" in globals(): reload(main)
import main; from main import *
