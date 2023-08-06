## import py3k_syntax; reload(py3k_syntax); from py3k_syntax import *
import os, sys
if sys.version_info[1] < 6: raise Exception("py3k_syntax requires Python 2.6 or higher")


__author__ =	"kai zhu"
__author_email__ =	"kaizhu@ugcs.caltech.edu"
__description__ =	"""incomplete py3k syntax emulator"""
__download_url__ =	None
__keywords__ =	None
__license__ =	"BSD"
__maintainer__ =	None
__maintainer_email__ =	None
__name__ = "py3k_syntax"
__obsoletes__ =	None
__platforms__ =	None
__provides__ =	None
__requires__ =	None
__url__ = None
__version__  = "2008.12.20"
## end setup info


if "DEBUG" not in globals(): DEBUG = 0 ## True prints debug info
def quicktest():
  if "py3k_syntax_test" not in sys.modules: import py3k_syntax_test
  else: reload(py3k_syntax_test)


import ast, collections, re ## pseudomethod parser
class parser(ast.NodeTransformer):
  def parse(self, s, fpath, mode):
    s = s.replace("..", ".__pseudomethod__.").replace("__pseudomethod__..", "..").replace("..__pseudomethod__", "..") ## parse pseudomethod syntax
    s = s.replace("\nfrom .__pseudomethod__.", "\nfrom ..").replace(" from .__pseudomethod__.", " from ..") ## ignore .. notation in relative imports

    node = ast.parse(s, fpath, mode); node = self.visit(node); return node ## parse pseudomethod node

  ## recursively print nodes in ast object for debugging
  @staticmethod
  def printnode(node, depth = ""):
    s = node.__dict__.items()
    s = "    ".join("%s %r" % x for x in sorted(node.__dict__.items()))
    print( "%s%s\t%s" % (depth, str(type(node)), s) )
    for x in ast.iter_child_nodes(node): parser.printnode(x, depth = depth + " ")

  ## hack node if it contains __pseudomethod__ attr
  def visit_Call(self, node):
    x = node.func
    if type(x) is ast.Attribute:
      x = x.value
      if type(x) is ast.Attribute and x.attr == "__pseudomethod__": ## a..b(...) -> b(a, ...)
        node.args.insert(0, node.func.value.value)
        node.func = ast.copy_location(
          ast.Name(node.func.attr, ast.Load()), ## new node
          node.func) ## old node
    for x in ast.iter_child_nodes(node): self.visit(x) ## recurse
    return node


import imp ## import hook
class importer(object):
  py3k_syntax = None ## identifier
  magic = "\nfrom __future__ import py3k_syntax\n"

  def __init__(self):
    sys.meta_path[:] = [self] + [x for x in sys.meta_path if not hasattr(x, "py3k_syntax")] ## restore sys.meta_path
    sys.path_importer_cache = {} ## reset cache

  def find_module(self, mname, path = None):
    if DEBUG and 1: print( "py3k_syntax find_module(mname = %s, path = %s)" % (mname, path) )

    if path and len(path) is 1:
      x = path[0] + "."
      if mname[:len(x)] == x: mname = mname[len(x):] ## import from package

    try: file, fpath, desc = imp.find_module(mname, path if path else sys.path); tp = desc[2]
    except ImportError: return

    if tp is imp.PY_SOURCE: pass
    elif tp is imp.PKG_DIRECTORY: fpath += "/__init__.py"; file = open(fpath)
    else: return

    s = "\n" + file.read() + "\n"; file.close()
    if self.magic not in s: return ## no py3k_syntax magic found in file
    s = s.replace(self.magic, "\nfrom __future__ import division, with_statement; from py3k_syntax import *\n", 1)
    s = s[1:-1] ## preserve lineno (for debugging)

    self.found = s, fpath, desc, tp; return self

  def load_module(self, mname):
    s, fpath, desc, tp = self.found
    if DEBUG and 1: print( "py3k_syntax load_module(mname = %s, fpath = %s, desc = %s)" % (mname, fpath, desc) )

    if mname in sys.modules: m = sys.modules[mname]; new = None ## if exist: use existing module
    else: m = sys.modules[mname] = imp.new_module(mname); new = True ## else: new module
    try:
      node = parser().parse(s, fpath, "exec")
      c = compile(node, fpath, "exec"); exec(c, m.__dict__)
      if tp is imp.PKG_DIRECTORY: m.__path__ = [os.path.dirname(fpath)] ## package.__path__
      m.__file__ = fpath; m.__loader__ = self.load_module; return m
    except:
      if new: del sys.modules[mname] ## if new module fails loading, del from sys.modules
      print( "\nFAILED py3k_syntax load_module(mname = %s, fpath = %s, desc = %s)\n" % (mname, fpath, desc) ) ## notify user exception originated from failed py3k_syntax import
      raise
importer()


import __builtin__ as builtins, itertools
if 1: ## builtins
  filter = itertools.ifilter
  filterfalse = itertools.ifilterfalse
  map = itertools.imap
  range = xrange
  zip = itertools.izip
  zip_longest = itertools.izip_longest
  def oct(x): return builtins.oct(x).replace("0", "0o", 1)
