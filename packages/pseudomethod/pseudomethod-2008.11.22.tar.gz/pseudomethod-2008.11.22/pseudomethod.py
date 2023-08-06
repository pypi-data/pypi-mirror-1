# documentation
"""
################################################################################
this is a pure python3.0 module.
pseudomethod is an extended language feature for python3.0.
it adds the ".." notation for calling regular functions as methods.
this allows u to extend any class or object on-the-fly w/o subclassing
& enhances python's functional programming ability.
pseudomethods r liberally used in the py3to2 application img2txt

a method is normally called by the "." notation:

  class Foo:
    def method(*args, **kwds):
      ...
  Foo().method(*args, **kwds)

pseudomethod allows u to call normal functions on-the-fly as methods
using the ".." notation:

  def function(self, *args, **kwds):
    ...
  class Foo: pass
  Foo()..function(*args, **kwds) # function temporarily bound to Foo

the only requirement for a function to b a pseudomethod is that it must accept
@ least one argument, which is the "self" object its passed to b a method of.

what actually happens is just simple rearrangement of symbols:

  a..b(*args, **kwds)  <==>  b(a, *args, **kwds)
  a..b()..c()..d()     <==>  d( c( b( a ) ) )

in this respect, the ".." notation could b thought of as a "flattener",
removing nesting of the 1st argument, & allowing an elegant style of
functional programming in python

for a real-world application using pseudomethod, check out the py3to2
application img2txt @:

  http://pypi.python.org/pypi/img2txt/

AUTHOR:
  kai zhu
  kaizhu@ugcs.caltech.edu

REQUIREMENTS:
- python3.0 or higher
- for python2.6, see py3to2 (which has pseudomethods enabled by default)

INSTALL:
  python3.0 setup.py install
  python3.0 setup.py dev --quicktest

API:
  type "help(pseudomethod)" for more details
  pseudomethod module:
  - parser - string & ast parser for pseudomethod syntax
  - importer - import hook for handling scripts containing pseudomethod
               syntax

MAGIC
  1 pseudomethod first initializes an import hook
  2 add the MAGIC LINE:

      from __future__ import pseudomethod

    to ur script & the import hook will take care of the rest

USAGE:
  start up the python3.0 interpreter & import pseudomethod:
    $ python3.0

    Python 3.0rc2 (r30rc2:67114, Nov  9 2008, 21:30:06)
    [GCC 3.4.6 20060404 (Red Hat 3.4.6-10)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>>
    >>> import pseudomethod

  try out this simple pseudomethod script:
    ################################################################
    # copy this to file pseudomethod1.py
    from __future__ import pseudomethod

    def add_to_self(self, x): return self + x

    print(
      "ab"             ..add_to_self ( "c"  ),
      bytearray(b"ab") ..add_to_self ( b"c" ),
      1                ..add_to_self ( 2    ),
      [1, 2]           ..add_to_self ( [3]  ),
      )
    ################################################################
    >>>
    >>> import pseudomethod1
    abc bytearray(b'abc') 3 [1, 2, 3]

  for functional-style programming,
  pseudomethods are quite useful for cleaning up ugly nested arguments:
    ################################################################
    # copy this to file pseudomethod2.py
    from __future__ import pseudomethod

    print(
      list(zip(sorted([(2,3), (0,4), (1,5)], key = lambda x: x[0])\\
               , range(2, 5))) # ugly, Ugly, UGLY !!!
      )

    print(
      [(2,3), (0,4), (1,5)] ..sorted(key = lambda x: x[0])\\
                            ..zip(range(2, 5)) ..list() # elegant ^_^
    )
    ################################################################
    >>>
    >>> import pseudomethod2
    [((0, 4), 2), ((1, 5), 3), ((2, 3), 4)]
    [((0, 4), 2), ((1, 5), 3), ((2, 3), 4)]
    >>>

################################################################################
MECHANISM:
  1 this module installs an import hook to detect if a script contains the
    MAGIC LINE:
      from __future__ import pseudomethod
  2 the script is preparsed, replacing the ".." notation w/ ".__pseudomethod__."
    to keep the python parser happy
  3 the script is compiled into an ast object.  the ast is recursively searched
    for the attribute "__pseudomethod__" were some symbol rearrangement occurs.

RECENT CHANGELOG:
current
- removed limitation where parser disallows use of keyword "__pseudomethod__"
  in scripts
20081121 created pseudomethod package
"""

import ast, imp, os, sys; reload = imp.reload
if "DEBUG" not in globals(): DEBUG = 0 # True enables printing debug info
if sys.version_info[0] is not 3: raise Exception("pseudomethod runs on python3.0 or higher")

# pseudomethod parser
class parser(ast.NodeTransformer):
  alphanum = "_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

  # parse str -> ast node w/ pseudomethod support
  def parse(self, s, fpath, mode):
    keyword = "qjzx" # least common alphabets
    for i, x in enumerate(s): # create a unique keyword guaranteed not to occur in s
      if keyword not in s: break
      keyword += alphanum[i % len(alphanum)]
    self.keyword = keyword; self.bkeyword = keyword.encode("ascii")
    s = s.replace("__pseudomethod__", keyword) # temporarily remove "__pseudomethod__" string to prevent collision
    s = s.replace("..", ".__pseudomethod__.").replace("__pseudomethod__..", "..").replace("..__pseudomethod__", "..") # parse pseudomethod syntax
    n = ast.parse(s, fpath, mode)
    n = self.visit(n) # parse pseudomethod node
    return n

  # recursively print nodes in ast object for debugging
  @staticmethod
  def printnode(node, depth = ""):
    s = node.__dict__.items()
    s = "    ".join("%s %r" % x for x in sorted(node.__dict__.items()))
    print( "%s%s\t%s" % (depth, str(type(node)), s) )
    for x in ast.iter_child_nodes(node): parser.printnode(x, depth = depth + " ")

  # hack node if it contains __pseudomethod__ attr
  def visit_Call(self, node):
    x = node.func
    if type(x) is ast.Attribute:
      x = x.value
      if type(x) is ast.Attribute and x.attr in ("__pseudomethod__", self.keyword): # a..b(...) -> b(a, ...)
        node.args.insert(0, node.func.value.value)
        node.func = ast.copy_location(
          ast.Name(node.func.attr, ast.Load()), # new node
          node.func) # old node
    for x in ast.iter_child_nodes(node): self.visit(x) # recurse
    return node

  # tie up loose ends from string replace
  def visit_Str(self, node):
    node.s = node.s.replace(".__pseudomethod__.", "..").replace(self.keyword, "__pseudomethod__")
    return node
  def visit_Bytes(self, node):
    node.s = node.s.replace(b".__pseudomethod__.", b"..").replace(self.bkeyword, b"__pseudomethod__")
    return node

# import hook
class importer(object):
  py3to2 = None # identifier
  magic = "\nfrom __future__ import pseudomethod\n"

  def __init__(self):
    sys.meta_path[:] = [self] + [x for x in sys.meta_path if not hasattr(x, "py3to2")] # restore sys.meta_path
    sys.path_importer_cache = {} # reset cache

  def find_module(self, mname, path = None):
    if DEBUG and 1: print( "pseudomethod find_module(mname = %s, path = %s)" % (mname, path) )

    if path and len(path) is 1:
      x = path[0] + "."
      if mname[:len(x)] == x: mname = mname[len(x):] # import from package

    try: file, fpath, desc = imp.find_module(mname, path if path else sys.path); tp = desc[2]
    except ImportError: return

    if tp is imp.PY_SOURCE: pass
    elif tp is imp.PKG_DIRECTORY: fpath += "/__init__.py"; file = open(fpath)
    else: return

    s = "\n" + file.read() + "\n"; file.close()
    if self.magic not in s: return # no pseudomethod magic found in file
    s = s.replace(self.magic, "\n\n", 1)
    s = s[1:-1] # preserve lineno (for debugging)

    self.found = s, fpath, desc, tp; return self

  def load_module(self, mname):
    s, fpath, desc, tp = self.found
    if DEBUG and 1: print( "pseudomethod load_module(mname = %s, fpath = %s, desc = %s)" % (mname, fpath, desc) )

    if mname in sys.modules: m = sys.modules[mname]; new = None # if exist: use existing module
    else: m = sys.modules[mname] = imp.new_module(mname); new = True # else: new module
    try:
      node = parser().parse(s, fpath, "exec")
      c = compile(node, fpath, "exec"); exec(c, m.__dict__)
      if tp is imp.PKG_DIRECTORY: m.__path__ = [os.path.dirname(fpath)] # package.__path__
      m.__file__ = fpath; m.__loader__ = self.load_module; return m
    except Exception as e:
      if new: del sys.modules[mname] # if new module fails loading, del from sys.modules
      print( "\nFAILED pseudomethod load_module(mname = %s, fpath = %s, desc = %s)\n" % (mname, fpath, desc) ) # notify user exception originated from failed pseudomethod import
      raise
importer()

# debugging...
def quicktest():
  if "pseudomethod_test" not in sys.modules: import pseudomethod_test
  else: reload(pseudomethod_test)

if 0 and DEBUG:
  s = "'a..b'"
  # s = "b'a..b'"
  # s = "bytearray(b'a..b')"
  node = parser.parse(s, "", "exec")
  parser.printnode(node)
  print( s )
