## import pseudomethod; reload(pseudomethod); from pseudomethod import *
import os, sys, traceback
if os.name != 'posix': sys.stderr.write('\npseudomethod requires linux os\n\n'); exit()
if sys.version_info[:2] != (3, 1): sys.stderr.write('\npseudomethod requires python3.1\n\n'); exit()







if 0: ## __init__ beg
  import pseudomethod, os, pydoc, re, sys, traceback
  if '_SETUP' not in globals(): _SETUP = sys.modules.get('pseudomethod.setup', None)

  def closure(*args, **kwds): return lambda fnc: fnc(*args, **kwds)
  def identity(aa): return aa
  def _import(ss, globals = globals()):
    for aa in ss.split(' '): globals[aa] = __import__(aa)
    return identity
  def dict_append(aa, bb):
    for cc in bb.keys():
      if cc not in aa: aa[cc] = bb[cc]
  class namespace(object):
    def __init__(self, **kwds): vars(self).update(kwds)



  #### pseudomethod compiler
  @_import('ast collections tempfile')
  class pseudomethod_compiler(ast.NodeVisitor):
    ## convenience function
    @staticmethod
    def exec(ss, globals, locals = None, fpath = '<file>'): exec( pseudomethod_compiler().compile(ss, fpath, 'exec'), globals, locals )

    # def exec(ss, globals, locals = None, fpath = '<file>'):
      # print(repr(ss))
      # if 'hello' in ss[:8]: print(repr(ss), '\n')
      # exec( pseudomethod_compiler().compile(ss, fpath, 'exec'), globals, locals )

    ## recursively print nodes in ast object for debugging
    @staticmethod
    def printnode(node, depth = ''):
      ss = '\t'.join('{} {!r}'.format(*aa) for aa in sorted(vars(node).items()))
      print( '{}{}\t{}'.format(depth, str(type(node)), ss) )
      for aa in ast.iter_child_nodes(node): pseudomethod_compiler.printnode(aa, depth = depth + ' ')

    ## parse string into legal python syntax
    @staticmethod
    def parse_string(ss,
                     rgx_pseudomethod1 = re.compile('([^.])\.\.(\w[\w. ]*\()'),
                     rgx_pseudomethod2 = re.compile('([^.])\.\.\.(\w[\w. ]*\()'),
                     rgx_pseudomethod3 = re.compile('([^.])\.\.\.\.(\w[\w. ]*\()'),
                     rgx_print = re.compile('(^|\s)print@@ (\S)'),
                     ):
      ss = rgx_pseudomethod3.sub('\\1.__pseudomethod2__.\\2', ss) ## parse pseudomethod2 syntax
      ss = rgx_pseudomethod2.sub('\\1.__pseudomethod1__.\\2', ss) ## parse pseudomethod1 syntax
      ss = rgx_pseudomethod1.sub('\\1.__pseudomethod0__.\\2', ss) ## parse pseudomethod0 syntax
      ss = rgx_print.sub('\\1lambda __printop__: \\2', ss)
      return ss

    def compile(self, ss, fpath, mode, flags = 0, dont_inherit = 0, parse_string = True, return_ast = None):
      if parse_string: ss = self.parse_string(ss)
      self.ss = ss; self.fpath = fpath; self.mode = mode
      self.node = node = ast.parse(ss, fpath, mode); self.parents = collections.deque(); self.visit(node); assert not self.parents ## parse pseudomethod node
      if return_ast: return node
      return compile(node, fpath, mode, flags, dont_inherit)

    def visit(self, node):
      type = node.__class__
      if type is ast.Attribute: ## ..pseudomethod()
        if node.attr in ('__pseudomethod0__', '__pseudomethod1__', '__pseudomethod2__'):
          name = self.parents.popleft(); name = ast.copy_location(ast.Name(name.attr, ast.Load()), name) ## new name node
          if isinstance(self.parents[0], ast.Call): self.parents[0].func = name ## fnc
          else: self.parents[0].value = name ## meth
          for call in self.parents:
            if isinstance(call, ast.Call): call.args.insert(int(node.attr[-3]), node.value); break ## insert arg
          return self.visit(node.value)
      if type is ast.arg: ## print@@
        if node.arg == '__printop__':
          self.parents.popleft(); lmbd = self.parents.popleft()
          call = ast.copy_location(ast.Call(ast.copy_location(ast.Name('print', ast.Load()), lmbd), [lmbd.body], [], None, None), lmbd)
          if isinstance(self.parents[0], ast.Tuple): call.args += self.parents.popleft().elts[1:] ## print@@ *args
          self.parents[0].value = call
          return self.visit(call)
      self.parents.appendleft(node)
      self.generic_visit(node)
      if self.parents[0] is node: self.parents.popleft()

    @staticmethod
    def test():
      ss0 = 'print( 1 )'; ss1 = '1 ..print()'
      ss0 = 'print( str(1) )'; ss1 = '1 ..str() ..print()'
      ss0 = 'int.__new__(int, 1)'; ss1 = '1 ...int.__new__(int)'
      ss0 = 'print( 1 )'; ss1 = 'print@@ 1'
      ss0 = 'print(1, 2, 3)'; ss1 = 'print@@ 1,2,3'
      ss0 = 'print( str(1), 2 )'; ss1 = 'print@@ 1 ..str(), 2'
      if 0: ## fail
        ss0 = 'list( 1, print(2, 3), 4 )'; ss1 = '(print@@ 2, 3) ...list(1, 3)'
        ss0 = 'list( 1, print(2, 3) )'; ss1 = '1 ..list(print@@ 2, 3)'
      print(ss0); node0 = ast.parse(ss0, '', 'exec'); pseudomethod_compiler.printnode(node0); print()
      print(ss1); node1 = ast.parse(pseudomethod_compiler.parse_string(ss1), '', 'exec'); pseudomethod_compiler.printnode(node1); print()
      print(ss1); node2 = pseudomethod_compiler().compile(ss1, '', 'exec', return_ast = True); pseudomethod_compiler.printnode(node2); print()
  if 0: pseudomethod_compiler.test(); exit()



  #### pseudomethod console interpreter
  @_import('code')
  class pseudomethod_console(code.InteractiveConsole):
    empty = compile('', '', 'exec')
    def runsource(self, ss, filename = '<input>', symbol = 'single'):
      try:
        ss = pseudomethod_compiler.parse_string(ss) ## parse string
        try: cc = code.compile_command(ss, filename, symbol) ## test completed code
        except (OverflowError, SyntaxError, ValueError): self.showsyntaxerror(filename); return False ## syntax error
        if cc:
          if cc.co_code != self.empty.co_code: ## BUG - compile(... 'single') cannot handle empty expression
            self.runcode( pseudomethod_compiler().compile(ss, filename, symbol) ); return False ## compile and run code
        else: return True ## incomplete code
      except: traceback.print_exc(); return False



  #### pseudomethod import hook
  @_import('builtins imp importlib importlib.abc importlib.util')
  @_import('locale') ## PYTHON BUG
  class pseudomethod_importer(importlib.abc.Finder, importlib.abc.PyLoader):
    # magic = '.pseudomethod' ## magic line enabling pseudomethod syntax
    magic = 'pseudomethod.' ## magic line enabling pseudomethod syntax
    maxfilesize = 0x100000

    def add_hook(self):
      if 1: print( 'pseudomethod_importer - adding hook {} to sys.meta_path'.format(self) )
      sys.meta_path[:] = [aa for aa in sys.meta_path if getattr(aa, 'magic', None) != self.magic] + [self] ## reset sys.meta_path
      sys.path_importer_cache = {} ## reset cache
      return self

    # def find_module(self, mname, path = None):
      # if 1: print( 'pseudomethod_importer - find_module(mname = {}, path = {})'.format(mname, path) ) ## DEBUG
      # if mname[-len(self.magic):] != self.magic: return None ## check for magic
      # mname = mname[:-len(self.magic)] ## remove magic
      # fname = os.path.join(*mname.split('.')) + '.py'
      # if not path: path = sys.path
      # for dpath in ['.'] + path:
        # fpath = os.path.join(dpath, fname)
        # if os.path.exists(fpath): self.fpath = fpath; return self

    def find_module(self, mname, path = None):
      if 0: print( 'pseudomethod_importer - find_module(mname = {}, path = {})'.format(mname, path) ) ## DEBUG
      if mname[:len(self.magic)] != self.magic: return None ## check for magic
      mname = mname[len(self.magic):] ## remove magic
      fname = os.path.join(*mname.split('.')) + '.py'
      if not path: path = sys.path
      for dpath in ['.'] + path:
        fpath = os.path.join(dpath, fname)
        if os.path.exists(fpath): self.fpath = fpath; return self

    def get_code(self, fullname = None): return pseudomethod_compiler().compile(self.get_data(self.source_path()), self.source_path(), 'exec', dont_inherit = True)

    def get_data(self, fpath):
      if 0: print( 'pseudomethod_importer - get_data(fpath = {})'.format(fpath) ) ## DEBUG
      if os.path.getsize(fpath) > self.maxfilesize: raise ImportError('pseudomethod_importer - maxfilesize exceeded - {} > {} bytes'.format(fpath, self.maxfilesize))
      return open(fpath).read()

    def is_package(self, fullname = None): return None

    def source_path(self, fullname = None): return self.fpath

  if 'pseudomethod' in sys.modules:
    @closure() #### import pseudomethod.main
    def _():
      builtins.reload = imp.reload
      global IMPORTER; IMPORTER = pseudomethod_importer()
      IMPORTER.find_module('pseudomethod.pseudomethod.main')
      exec( IMPORTER.get_code(), globals() )
## __init__ end







######## UTIL
if 1:
  def depth(arr):
    try: return 1 + depth(arr[0])
    except TypeError: return 0

  @_import('functools')
  @functools.wraps(builtins.enumerate)
  def enumerate(arr, i = None): return count(i) ..zip(arr) if i else builtins.enumerate(arr)

  def getitem2(idx, aa): return aa[idx]

  def lens(*args): return [len(aa) for aa in args]

  ## get current screensize - row x col
  @_import('fcntl struct termios')
  def screensize():
    try: return fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '0123') ...struct.unpack('hh')
    except: return (24, 80)

  def sjoin(arr, _): return _.join(arr)

  @_import('io')
  def stdout2str(fnc):
    with io.StringIO() as ff:
      stdout0 = sys.stdout
      try: sys.stdout = ff; fnc(); return ff.getvalue()
      finally: sys.stdout = stdout0

  ## piped system call
  @_import('subprocess')
  def system(exe, block = True):
    print( exe )
    if block: return subprocess.Popen(exe, shell = 1, stdout = subprocess.PIPE, close_fds = 1).stdout.read().decode('latin')
    return subprocess.check_call(exe, shell = True)

  # ## print test log
  # def test_class(type, fpath):
    # if isinstance(type, types.ModuleType): type = numbyte
    # tt = codetree.src(type, fpath) ...codetree.src(type.test); rgx = re.compile('^' + ' ' * tt[1].depth(), re.M)
    # for aa in tt[1].merge_head():
      # aa = re.sub(rgx, '>>> ', aa.sjoin() if isinstance(aa, Tree) else aa).replace('>>>  ', '...  ')
      # print(aa); pseudomethod_compiler.exec( aa.replace('>>> ', '').replace('...  ', ' '), globals() )

  ## print test log
  def test_class(type, fpath):
    if isinstance(type, types.ModuleType): type = numbyte
    tt = codetree.src(type, fpath) ...codetree.src(type.test); rgx = re.compile('^' + ' ' * tt[1].depth(), re.M)
    tt = [re.sub(rgx, '>>> ', aa.sjoin() if isinstance(aa, Tree) else aa).replace('>>>  ', '...  ').replace('>>> #', '#') for aa in tt[1].merge_head()]; tt[-1] = tt[-1].rstrip()
    for aa in tt:
      aa = re.sub(rgx, '>>> ', aa.sjoin() if isinstance(aa, Tree) else aa).replace('>>>  ', '...  ')
      print(aa); pseudomethod_compiler.exec( aa.replace('>>> ', '').replace('...  ', ' '), globals() )

  ## generate unique alphanumeric string guaranteed not to occur in s
  def uniquestr(s, kwd = 'qjzx'):
    while kwd in s: kwd += hex(id(kwd))
    return kwd



#### pseudomethod test
class pseudomethod(object):
  @staticmethod
  def test():
    ## dynamically bind function calls to objects
    ## bind the function call print() to 'hello'
    print('hello')
    'hello' ..print()
    'hello' ..print('world')
    'hello' ..print('world', '!')
    'hello' ..print('world', '!', file = sys.stdout)

    ## create a string pseudomethod which adds an exclamation or a specified string
    def add_end(self, end = '!'): return self + end
    'hello' ..add_end() ..print()
    'hello'.upper() ..add_end() ..print()
    'hello'.upper() ..add_end(' world') ..print()
    'hello'.upper() ..add_end(' world').lower() ..print()
    'hello'.upper() ..add_end(' world').lower() ..add_end('!') ..print()
    'hello'.upper() ..add_end(' world').lower() ..add_end('!') ..add_end(end = '!') ..print()

    ## OPERATOR PRECEDENCE - 'a..b()' has the same operator precedence as 'a.b()' which precedes <and or not + - * /> but not <= == ,>
    def add(aa, bb): return aa + bb
    print( 2 * 3 ..add(4) + 5 == 2 * (3 + 4) + 5 )
    print( 3 == 1 ..add(2) )
    print( 0, 0 ..add(1), 0 )



    ## the python code object type <class 'code'> cannot be subtyped nor will it accept any method binding.
    ## however, we can extend it by dynamically binding ordinary functions.
    ## here's a pseudomethod, which disassembles an instance of the type to a specified output
    import dis, io, sys
    def disassemble(self, file):
      backup_stdout = sys.stdout ## backup sys.stdout
      try:
        sys.stdout = file
        dis.dis(self) ## disassemble
        return file
      finally:
        sys.stdout = backup_stdout ## restore sys.stdout

    code_source = 'print( "hello" )'; code_object = compile(code_source, '', 'exec'); exec( code_object )
    code_object ..disassemble(file = io.StringIO()).getvalue() ..print()



    ## '...' and '....' syntax
    ## sometimes we instead want the 2nd or 3rd argument of a function bound to an object.
    ## '...' and '....' will do this respectively
    '2nd' ...print(0, 0)
    '3rd' ....print(0, 0)

    ## '....' is useful for chaining re.sub
    ss = 'file = io.StringIO(); print 1, 2, 3 >> file; print file.getvalue()'; print( ss )

    print(
      re.sub('print (.*?)$', 'print( \\1 )',
             re.sub('print (.*) >> (.*?);', 'print( \\1, file = \\2 );', ss)
             )
      )

    ss ....re.sub('print (.*) >> (.*?);', 'print( \\1, file = \\2 );') \
       ....re.sub('print (.*?)$', 'print( \\1 )') \
       ..print()

    ## in fact, another primary use of pseudomethod is to flatten ugly, hard-to-read, lisp-like nested function calls
    print( dict( enumerate( zip( 'abc',  sorted( 'abc bca cab'.split(' '), key = lambda x: x[1] ) ) ) ) )

    'abc bca cab'.split(' ') ..sorted(key = lambda x: x[1]) ...zip('abc') ..enumerate() ..dict() ..print()



    ## import hook
    ## we can also import modules written using pseudoemethod syntax.
    ## in fact, this package makes liberal use of the pseudomethod syntax

    ## enable pseudomethod import hook
    import pseudomethod
    pseudomethod.IMPORTER.add_hook()

    ## test module
    open('test_module.py', 'w').write('"hello" ..print()\n"bye" ..print()\n')

    ## during import, add the magic prefix 'pseudomethod.' to the beginning of the module name
    import pseudomethod.test_module

#### tree
class Tree(list):
  def __init__(self, *args): list.__init__(self, args)

  def walk(self, depth = 0):
    for ii, aa in enumerate(self):
      if not isinstance(aa, Tree): yield aa, depth, ii, self ## return depth, self[ii]
      else:
        for bb in aa.walk(depth + 1): yield bb

  def __str__(self): return '\n'.join('<{} {}> {!r}'.format(depth, ii, aa) for aa, depth, ii, bb in self.walk())

  def blank(line, rgx = re.compile('\s*$')): return True if not line or rgx.match(line) else None

  def find(self, match = None, found = None):
    if match is not None: found = lambda aa: aa[0] == match
    for aa in self.walk():
      if found(aa): return aa

  def __getitem__(self, ii): return list.__getitem__(self, ii) if isinstance(ii, int) else type(self)(Tree(*list.__getitem__(self, ii)))

  def sjoin(self, _ = '\n'): return _.join(str(aa[0]) for aa in self.walk())

  @staticmethod
  def test():
    aa = Tree('1', Tree('2', '3'), '4')
    for bb in aa.walk(): print( bb )



#### tree of lines from braket txt
class tree_from_braket(Tree):
  def _init(self, lines, aa = ''):
    if not aa: aa = next(lines)
    ii = aa.find('{'); jj = aa.find('}')
    if ii == jj == -1: self.append(aa); return self._init(lines)
    if jj == -1 or -1 < ii < jj: ## {
      self.append(aa[:ii])
      self.append(tree_from_braket(Tree(aa[ii])))
      aa = self[-1]._init(lines, aa[ii + 1:])
      return self._init(lines, aa)
    self.append(aa[:jj + 1]); return aa[jj + 1:] ## }

  def __init__(self, lines = None):
    if not lines: return
    if isinstance(lines, Tree): return Tree.__init__(self, *lines)
    if isinstance(lines, str): lines = lines.split('\n')
    lines = iter(lines)
    try: self._init(lines)
    except StopIteration: pass

  @staticmethod
  def test():
    print( __file__ )
    ss = open('pseudomethod/_main.cpp').read()
    tt = tree_from_braket(ss)
    print( tt, '\nlen={}'.format(len(tt)) )



#### tree of lines from indent txt
class tree_from_indent(Tree):
  def depth(self, line = None, rgx = re.compile('\S')): return rgx.search(line if line else self[0]).end() - 1

  def ignore(self, line, rgx = re.compile('\S')): return not rgx.search(line) ## ignore blank line

  def _init(self, lines, ignore, aa, depth0):
    if ignore(self, aa): self.append(''); return self._init(lines, ignore, next(lines), depth0)
    depth = self.depth(aa)
    if depth < depth0: return aa
    if depth == depth0: self.append(aa); return self._init(lines, ignore, next(lines), depth0)
    else:
      Tree(aa) ..tree_from_indent() ..self.append()
      aa = self[-1]._init(lines, ignore, next(lines), depth)
      return self._init(lines, ignore, aa, depth0)

  def __init__(self, lines = None, ignore = ignore):
    if not lines: return
    if isinstance(lines, Tree): return Tree.__init__(self, *lines)
    if isinstance(lines, str): lines = lines.split('\n')
    lines = iter(lines)
    try: self._init(lines, ignore, next(lines), depth0 = 0)
    except StopIteration: pass

  # def merge_head(self):
    # out = type(self)()
    # for aa in self:
      # if isinstance(aa, Tree): aa.insert(0, out[-1]); out[-1] = aa
      # else: out.append(aa)
    # return out

  def merge_head(self):
    out = type(self)()
    for aa in self:
      if isinstance(aa, Tree):
        aa.insert(0, out[-1]); out[-1] = aa
        while not aa[-1]: out.append(aa.pop())
      else: out.append(aa)
    return out

  @staticmethod
  def test():
    print( __file__ )
    ss = open(__file__).read()
    tt = tree_from_indent(ss)
    print( tt, '\nlen={}'.format(len(tt)) )



#### python code object viewer
@_import('dis types')
class codetree(Tree):
  co_args = 'co_argcount co_kwonlyargcount co_nlocals co_stacksize co_flags co_code co_consts co_names co_varnames co_filename co_name co_firstlineno co_lnotab co_freevars co_cellvars'.split(' ')

  def __init__(self, codeobj, **kwds):
    if isinstance(codeobj, list): list.__init__(self, codeobj)
    else:
      for ii, aa in enumerate(self.co_args):
        bb = getattr(codeobj, aa)
        setattr(self, aa, list(bb) if isinstance(bb, tuple) else bb)
      Tree.__init__(self, *(codetree(aa) if isinstance(aa, types.CodeType) else aa for aa in self.co_consts))
      del self.co_consts;
    vars(self).update(kwds)

  ## serializable: codetree(codeobj) == eval( repr( codetree( codeobj ) ) )
  def __repr__(self): return 'codetree({}, **{})'.format(repr(list(self)), vars(self))

  def __str__(self, _ = ''):
    _ += '    '; __ = _ + 18 * ' '
    ss = []
    for aa in self.co_args:
      if aa != 'co_consts': bb = repr(getattr(self, aa))
      else:
        bb = '\n{}'.format(__).join(aa.__str__(__) if isinstance(aa, codetree) else str(aa) for aa in self)
        bb = '\n{}{}'.format(__, bb)
      '{}{:18}{}'.format(_, aa, bb) ..ss.append()
    return 'codetree(\n{})'.format('\n'.join(ss))

  ## codeobj == codetree(codeobj).compile()
  def compile(self):
    args = []
    for aa in self.co_args:
      if aa != 'co_consts': bb = getattr(self, aa)
      else: bb = tuple(aa.compile() if isinstance(aa, codetree) else aa for aa in self) ## recurse
      args.append(tuple(bb) if isinstance(bb, list) else bb)
    return types.CodeType(*args)

  ## recursive disassembler
  def dis(self):
    def recurse(aa, _ = ''):
      if isinstance(aa, types.CodeType):
        yield _ + stdout2str(lambda: dis.dis(aa)).replace('\n', '\n' + _)
        for aa in aa.co_consts:
          for aa in recurse(aa, _ + '  '): yield aa
    return '\n'.join(recurse(self.compile()))

  ## attempt to retrieve source code of object
  @staticmethod
  def src(aa, fpath = ''):
    if isinstance(aa, types.FunctionType): rgx = re.compile('\s*def {}\W'.format(aa.__name__))
    elif isinstance(aa, type): rgx = re.compile('\s*class {}\W'.format(aa.__name__))
    else: raise TypeError('invalid type <{}>'.format(type(aa)))
    if isinstance(fpath, Tree): tt = fpath
    else:
      fpath = '{}/{}'.format(os.path.dirname(sys.modules[aa.__module__].__file__), fpath) if fpath else sys.modules[aa.__module__].__file__
      ss = open(fpath).read(); tt = tree_from_indent(ss.split('\n'))
    for bb, depth, ii, cc in tt.walk():
      if re.match(rgx, bb): return Tree(bb, cc[ii + 1]) ..tree_from_indent()
    raise ValueError('<{}> not found in <{}>'.format(repr(aa)[:256], repr(fpath)[:256]))

  @staticmethod
  def test():
    ## source code
    src = 'def foo(aa):\n def closure():\n  nonlocal aa\n  aa += "!"\n  print(aa)\n return closure()\nfoo("hello")'; print( src )

    ## compile source code
    codeobj = compile(src, '', 'exec')
    exec( codeobj )

    ## convert code object into editable codetree
    tree = codetree(codeobj)
    for item in vars(tree).items(): print( item )

    ## edit / compile / exec codetree
    element, depth, index, subtree = tree.find('hello')
    subtree[index] = 'goodbye'
    exec( tree.compile() )

    ## codetree structure
    print( tree )

    ## disassemble codetree
    print( tree.dis() )







if 1: ######## BUILD
  _import('distutils distutils.core distutils.dist distutils.log')

  _EXTENSION = [
    # distutils.core.Extension('pseudomethod.base', sources = ['pseudomethod/base.cpp'], libraries = ['png']),
    # distutils.core.Extension('pseudomethod._module', sources = ['pseudomethod/_module.cpp'], libraries = ['png'], extra_objects = ['pseudomethod/base.so']),
    distutils.core.Extension('pseudomethod.base', sources = ['pseudomethod/base.cpp']),
    distutils.core.Extension('pseudomethod._module', sources = ['pseudomethod/_module.cpp'], extra_objects = ['pseudomethod/base.so']),
    distutils.core.Extension('pseudomethod._numbyte', sources = ['pseudomethod/_numbyte.cpp'], extra_objects = ['pseudomethod/base.so']),
    distutils.core.Extension('pseudomethod._math_op', sources = ['pseudomethod/_math_op.cpp'], extra_objects = ['pseudomethod/base.so', 'pseudomethod/_numbyte.so']),
    distutils.core.Extension('pseudomethod._image', sources = ['pseudomethod/_image.cpp'], extra_objects = ['pseudomethod/base.so']),
    ] if 'pseudomethod' in 'ascii' 'porn numbyte' else []

  _MANIFEST = '''setup.py
pseudomethod/README
pseudomethod/README
pseudomethod/README
pseudomethod/README
pseudomethod/lucida06x10.bmp
pseudomethod/_main.cpp
pseudomethod/main.py
pseudomethod/mario.png'''
  _README = open(__path__[0] + '/README').read()
  _DESCRIPTION = re.search('DESCRIPTION: (.*)', _README).group(1)
  _README = '''{}

  REQUIRES LINUX OS AND PYTHON3.1

  QUICK TEST: $ python3.1 setup.py build dev --quicktest

  {}
  RECENT CHANGELOG:
  20091231 - added print@@ sugar
  20091224 - added pseudomethod interactive console - revamped pseudomethod import hook
  20091224 - modularized package - fix install issues - added sdist check
  20091209 - improved documentation
  20091205 - moved source code to c++
  20091116 - package integrated

  '''.format(_DESCRIPTION, _README)

  DIST = namespace(
    name = 'pseudomethod',
    version = '2009.12.30.py3k.cpp',
    author = 'kai zhu',
    author_email = 'kaizhu256@gmail.com',
    license = 'gpl',
    url = 'http://pypi.python.org/pypi/pseudomethod',
    description = _DESCRIPTION,
    long_description = _README,
    packages = ['pseudomethod'],
    package_dir = {'pseudomethod': 'pseudomethod'},
    data_files = [
    ('lib/python3.1/site-packages/pseudomethod', ['pseudomethod/mario.png']),
    ('lib/python3.1/site-packages/pseudomethod', ['pseudomethod/README']),
    ],
    ext_modules = _EXTENSION,
    classifiers = [
    'Development Status :: 3 - Alpha',
    # 'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Operating System :: POSIX',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: C',
    'Programming Language :: C++',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.1',
    'Topic :: Multimedia',
    'Topic :: Multimedia :: Graphics',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Software Development',
    'Topic :: Software Development :: Code Generators',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    # 'Topic :: System :: Emulators',
    # 'Topic :: System :: Shells',
    # 'Topic :: System :: System Shells',
    'Topic :: Utilities',
    ])



  ## custom Distribution class
  class Distribution(distutils.dist.Distribution):
    _dist = distutils.dist.Distribution

    class dev(distutils.core.Command):
      def initialize_options(self):
        self.subcommands = []
        for aa in self.user_options: bb = aa[0].replace('=', '').replace('-', '_'); setattr(self, bb, aa[1]); self.subcommands.append(bb)

      def finalize_options(self): pass

      def run(self, **kwds):
        for aa in self.subcommands: setattr(BUILD, aa, getattr(self, aa))
        BUILD.run(**kwds)

      description = 'developer stuff'
      user_options = [('alias=', None, 'alias package'),
                      ('doc', None, 'print doc'),
                      # ('echo', None, 'echo'),
                      ('force', None, 'force'),
                      ('pkginfo', None, 'create pkg-info'),
                      ('quicktest', None, 'run quick tests'),
                      ('sdist-test=', None, 'test sdist package'),
                      ('test=', None, 'test specific functionality'),
                      ('uninstall=', None, 'uninstall'),
                      ]

    def __init__(self, kwds, dev = dev): self._dist.__init__(self, kwds); self.cmdclass['dev'] = dev; global BUILD; BUILD = self

    def run_command(self, command, **kwds):
      if 'rerun' in kwds: self.have_run[command] = not kwds['rerun']
      if self.have_run.get(command): return ## Already been here, done that? then return silently.
      distutils.log.info('\nrunning {}'.format(command)); cmd_obj = self.get_command_obj(command); cmd_obj.ensure_finalized() ## get cmd
      if 0: print( 'DEBUG {}\tcmd_obj={}\tsub_cmd={}\tkwds={}'.format(command, cmd_obj, cmd_obj.get_sub_commands(), kwds) ) ## DEBUG
      if 1: cmd_obj.byte_compile = lambda *args, **kwds: None ## disable byte compile
      if command == 'build_ext': self.pre_build_ext(cmd_obj, **kwds) ## pre build_ext
      elif command == 'register': self.append_pkginfo()
      elif command == 'sdist': self.append_pkginfo(); open('MANIFEST', 'w').write(_MANIFEST)

      cmd_obj.run(); self.have_run[command] = True ## run cmd

      if command == 'install': self.post_install(cmd_obj, **kwds) ## post install

    compiler_so = ['gcc', '-pthread', '-fno-strict-aliasing', '-DNDEBUG', '-g', '-fwrapv', '-O0', '-Wall', '-fPIC']

    def run(self):
      if self.force: self.get_command_obj('build_ext').force = True
      self.run_command('build_ext', compiler_so = self.compiler_so) ## auto build
      if self.alias:
        assert self.alias != 'ascii' 'porn', self.alias
        try: dpath = os.path.abspath(self.alias); assert (os.getcwd() + '/') in dpath, (os.getcwd(), dpath); system( 'rm -r {}/*'.format(dpath) ) ..print()
        except subprocess.CalledProcessError: traceback.print_exc()
        for aa in _MANIFEST.split('\n'):
          bb = 'setup.py' if aa == 'setup.py' else aa.replace('pseudomethod', self.alias)
          if 'README' in aa: system( 'cp pseudomethod/README.{} {}/README'.format(self.alias, self.alias) ) ..print()
          else:
            print( 'aliasing {} -> {}'.format(aa, bb) )
            if aa[-4:] not in '.bmp .png .cpp .hpp': ss = open(aa).read().replace('pseudomethod', self.alias).replace('setup.py', 'setup.py') ....re.sub('README\.\w+', 'README'); open(bb, 'w').write(ss)
            else: system( '  cp -a {} {}'.format(aa, bb) ) ..print()
        system( 'python3.1 setup.py {}'.format(' '.join(sys.argv[3:])), block = None ); exit()
      if self.doc: system( 'python3.1 -c "import pseudomethod; help(pseudomethod)"', block = None )
      if self.pkginfo: self.append_pkginfo()
      if self.quicktest: self.run_test('pseudomethod')
      if self.sdist_test:
        self.run_uninstall(self.sdist_test); self.get_command_obj('install').prefix = self.sdist_test; self.run_command('install')
        system( 'cd /tmp; python3.1 -c "import pseudomethod; pseudomethod.quicktest()"' ) ..print()
        self.run_uninstall(self.sdist_test); self.run_command('sdist'); fpath = self.get_command_obj('sdist').archive_files[0]
        system( 'cp {} index_html/sdist/{}'.format(fpath, os.path.basename(fpath)) ) ..print() ## archive sdist
        system( 'rm -r test/*' ) ..print()
        system( 'cd test; tar -xzf ../{}'.format(fpath) ) ..print()
        system( 'cd test/{}; python3.1 setup.py install'.format(os.path.basename(fpath).replace('.tar.gz', '')), block = None ) ..print()
        system( 'cd /tmp; python3.1 -c "import pseudomethod; pseudomethod.quicktest()"' ) ..print()
      if self.test: self.run_test(self.test)
      if self.uninstall: self.run_uninstall(self.uninstall)

    def run_test(self, type): system( 'python3.1 -c "import pseudomethod; pseudomethod.test_class(pseudomethod.{}, \'main.py\')"'.format(type), block = None)

    def run_uninstall(self, prefix): cmd = self.get_command_obj('install'); cmd.prefix = prefix; cmd.ensure_finalized(); system( 'rm -Ir {}'.format(os.path.join(cmd.install_lib, 'pseudomethod')) ) ..print()

    def append_pkginfo(self): self.metadata.long_description += 'DEMO USAGE:\n\n>>> from pseudomethod import *\n' + ('>>> pseudomethod_console().interact()\n' if 'pseudomethod' == 'pseudomethod' else '') + '\n' + system( 'python3.1 -c "import pseudomethod; pseudomethod.test_class(pseudomethod.pseudomethod, \'main.py\')"' ); self.metadata.write_pkg_file(open('README', 'w')); pydoc.pager(open('README').read())

    def post_install(self, cmd, **kwds): dpath = cmd.install_lib + 'pseudomethod/'; self.get_command_obj('build_ext').force = True; self.run_command('build_ext', rerun = True, install_path = dpath)

    ## generate c header
    def c2h(self, src):
      ss = src.split('\n'); hh = ''; macro = {}
      for ii, aa in enumerate(ss): ## tokenize macro
        if aa and aa[0] == '#': bb = '#{}'.format(ii); macro[bb] = aa; ss[ii] = bb
      tt = Tree(); depth0 = -1; itr = ss ..tree_from_braket().walk()
      def _():
        nonlocal depth0; aa, depth, ii, bb = next(itr)
        if depth0 >= 0:
          if depth > depth0: return _() ## skip lower depth
          depth0 = -1
        if Tree.blank(aa): return _()
        if aa[0] == '#': aa = macro[aa] ## untokenize macro
        elif aa[-2:] == ') ': aa += ';'; depth0 = depth ## prototype fnc
        tt.append(aa); return _()
      try: _()
      except StopIteration: pass
      hh += '\n'.join(aa[0] for aa in tt.walk() if aa[0]); return hh.replace(' inline ', ' ')

    def preprocess(self, src):
      if 'TYPE' not in src: src = '\n#define PYTYPE false\n' + src ## skip type alloc
      for aa in src ...re.finditer(re.compile('\n  namespace (\w+) {(.*?\n)  }', re.S)):
        name, aa = aa.groups(); fpath = 'pseudomethod/{}.cpp'.format(name)
        src += '\nnamespace {} {{ {} }}\n'.format(name, self.METHOD_init(aa))
      src = '\n#define PYMETH_SIZE {}\n'.format(src.count('PYMETH_ADD') // 2 + 1) + src ## optimize method list size
      return src

    def METHOD_init(self, src):
      ss = ''
      for aa in re.finditer('(PYMETH_ADD_\w+) PyObject \*,*py_(\w+)', src): ss += '_{}({});\n'.format(*aa.groups())
      return '\nvoid METHOD_init() {{ int ii; ii = 0; {} }}\n'.format(ss)

    def pre_build_ext(self, cmd, **kwds):
      for aa in open('pseudomethod/_main.cpp').read().replace('\\\n', '') ....re.sub('//+.*', '') ...re.finditer(re.compile('\nnamespace (\w+) {(.*?\n)}', re.S)):
        name, mm = aa.groups(); fpath = 'pseudomethod/{}.cpp'.format(name)

        if name == '_numbyte': ## numbyte
          ss = ''; errs = {'int ': 'ERROR', 'numbyte *': 'NULL', 'PyObject *': 'NULL', 'TT *': 'NULL', 'void ': ''}
          for aa in self.c2h(mm) ...re.finditer('\n      static (.+?)(\w+)\((.*)\)'):
            rtype, fnc, args = aa.groups(); call = re.sub('\w+ \W*', '', args)
            if rtype not in errs: continue
            err = errs[rtype]
            if rtype in 'TT * numbyte *':
              rtype = rtype.replace('numbyte *', 'numbyte<TT> *')
              args = args.replace('numbyte *', 'numbyte<TT> *')
              aa = '{}{}{}({}) {{ return numbyte<TT>::{}({}); }}'.format(rtype, fnc, '' if 'TT' in args else 'TT', args, fnc, call)
              aa = '{}\n{}\n{}\n'.format(aa.replace('TT', 'CC'), aa.replace('TT', 'II'), aa.replace('TT', 'FF'))
              ss += aa
            elif 'numbyte *self' in args: ## method(self)
              args = args.replace('numbyte *', 'PyObject *'); call = call.replace('self', '(numbyte<TT> *)self')
              if rtype == 'PyObject *' and fnc[:3] == 'py_': ## type method
                if args == 'PyObject *self': rtype = 'PYMETH_ADD_NOARGS ' + rtype
                elif args == 'PyObject *self, PyObject *aa': rtype = 'PYMETH_ADD_O ' + rtype
                elif args == 'PyObject *self, PyObject *args': rtype = 'PYMETH_ADD_VARARGS ' + rtype
              aa = 'return numbyte<TT>::{}({});'.format(fnc, call)
              aa = 'NUMBYTE_SWITCH(tcode_self(self), self, \n{},\n{},\n{},\n)'.format(aa.replace('TT', 'CC'), aa.replace('TT', 'II'), aa.replace('TT', 'FF'))
              aa = '{}{}({}) {{ try {{ {} }} catch (...) {{ return {}; }} }}\n'.format(rtype, fnc, args, aa, err)
              ss += aa
            elif 'PyObject *args' in args: ## staticmethod
              if rtype == 'PyObject *' and fnc[:3] == 'py_': rtype = 'PYMETH_ADD_VARARGS_STATIC ' + rtype ## type method
              aa = 'return numbyte<TT>::{}({});'.format(fnc, call)
              aa = 'NUMBYTE_SWITCH(tcode_args(args), NULL, \n{},\n{},\n{},\n)'.format(aa.replace('TT', 'CC'), aa.replace('TT', 'II'), aa.replace('TT', 'FF'))
              aa = '{}{}({}) {{ try {{ {} }} catch (...) {{ return {}; }} }}\n'.format(rtype, fnc, args, aa, err)
              ss += aa
          mm = re.sub('#define NUMBYTE_METHOD', ss, mm)
          open('pseudomethod/numbyte.hpp', 'w').write(self.c2h(mm))

        if name == 'base': open('pseudomethod/base.hpp', 'w').write(self.c2h(mm)) ## base header
        else: mm = self.preprocess(mm)
        if not os.path.exists(fpath) or open(fpath).read() != mm: open(fpath, 'w').write(mm)

      for aa in cmd.extensions:
        name = aa.name.replace('pseudomethod.', '')
        if not os.path.lexists('pseudomethod/{}.so'.format(name)): system( 'ln -s ../{}/pseudomethod/{}.so pseudomethod/{}.so'.format(cmd.build_lib, name, name) ) ..print() ## copy built library

      cmd.build_extension = lambda aa: self.build_extension(cmd, aa, **kwds)

    ## custom extension compiler and linker
    @staticmethod
    def build_extension(self, ext, compiler_so = [], install_path = '', **kwds):
      sources = ext.sources
      ext_path = self.get_ext_fullpath(ext.name)
      depends = sources + ext.depends
      from distutils.dep_util import newer_group
      if not (self.force or newer_group(depends, ext_path, 'newer')): distutils.log.debug('skipping "%s" extension (up-to-date)', ext.name); return
      else: distutils.log.info('building "%s" extension', ext.name)
      macros = ext.define_macros[:]
      for undef in ext.undef_macros: macros.append((undef,))

      if compiler_so: self.compiler.compiler_so = compiler_so
      for aa in '-Wstrict-prototypes'.split(' '): ## remove compiler flag
        if aa in self.compiler.compiler_so: self.compiler.compiler_so.remove(aa)
      if install_path:
        install_path = os.path.abspath(install_path)
        ext_path = os.path.join(install_path, os.path.basename(ext_path))
        ext.extra_objects = [os.path.join(install_path, os.path.basename(aa)) for aa in ext.extra_objects]

      objects = self.compiler.compile(
        sources,
        output_dir=self.build_temp,
        macros=macros,
        include_dirs=ext.include_dirs,
        debug=self.debug,
        extra_postargs=ext.extra_compile_args,
        depends=ext.depends)
      self._built_objects = objects[:] ## cleanup on failed build
      if ext.extra_objects: objects.extend(ext.extra_objects)
      language = ext.language or self.compiler.detect_language(sources)
      self.compiler.link_shared_object(
          objects, ext_path,
          libraries=self.get_libraries(ext),
          library_dirs=ext.library_dirs,
          runtime_library_dirs=ext.runtime_library_dirs,
          extra_postargs=ext.extra_link_args,
          export_symbols=self.get_export_symbols(ext),
          debug=self.debug,
          build_temp=self.build_temp,
          target_lang=language)







if _SETUP: ######## SETUP
  Distribution(vars(DIST))
  distutils.core.setup(distclass = Distribution, **vars(DIST))






if _EXTENSION and not _SETUP: ######## EXTENSION
  for aa in '_module _numbyte _math_op _image'.split(' '): exec('from pseudomethod.{} import *'.format(aa, aa), globals())
  class numbyte(_numbyte._numbyte, _math_op._math_op):
    _numbyte = _numbyte._numbyte; _math_op = _math_op._math_op

    def debug(self): return '{} {} refcnt={} tcode={} tsize={} offset={} shape=<{} {}> stride=<{} {}> transposed={}\n{}'.format(type(self), self.tcode(), refcnt(self), self.tcode(), self.tsize(), self.offset(), self.shape0(), self.shape1(), self.stride0(), self.stride1(), self.transposed(), self)
    def recast(self, tcode): return bytearray(len(self) * self.tsize_from_tcode(tcode)) ....self._numbyte.__new__(type(self), tcode).reshape(self.shape0(), self.shape1()) ..self.copyto()

    def __copy__(self): return self.recast(self.tcode())
    copy = __copy__

    def __new__(type, tcode, arr, shape0 = None, shape1 = -1):
      self = None
      if isinstance(arr, numbyte): self = arr.retype(type).recast(tcode)
      else:
        if isinstance(arr, bytearray): pass
        elif isinstance(arr, bytes): arr = bytearray(bytes)
        elif is_seq(arr):
          self = bytearray(len(arr) * type._numbyte.tsize_from_tcode(tcode))
          self = type._numbyte.__new__(type, tcode, self)
          self.fill_from_itr(iter(arr))
        if self is None: self = type._numbyte.__new__(type, tcode, arr)
      if shape0 is not None: self = self.reshape(shape0, shape1)
      return self

    @staticmethod
    def zeros(tcode, shape0, shape1): return numbyte(tcode, bytearray(shape0 * shape1 * numbyte.tsize_from_tcode(tcode)), shape0, shape1)

    def __getitem__(self, slices):
      if not isinstance(slices, tuple): slices = (slices, slice(None))
      return self._getitem(*slices)

    def __iter__(self): return iter(self.base())

    def rows(self):
      for ii in range(self.shape0()): yield self[ii]

    def __setitem__(self, slices, aa):
      if aa is None: return self._getitem(*slices)
      if not is_numbyte(aa):
        if is_itr(aa): self[slices].fill_from_itr(aa); return
        if is_seq(aa): self[slices].fill_from_itr(iter(aa)); return
      return self._setitem(slices, aa)

    def __str__(self):
      rows, cols = screensize(); ss = []; ll = min(self.shape1(), cols >> 1)
      for ii in min(self.shape0(), rows / 2) ..range():
        aa = '[{}]'.format(self[ii, :ll] ..self._numbyte.__str__()[:-1])
        if not ii: aa = '[' + aa;
        if len(aa) > cols: aa = '{}...]'.format(aa[:cols - 4])
        ss.append(aa)
      if ii + 1 < self.shape0(): ss[-1] += '...'
      ss[-1] += ']'
      if len(ss[-1]) > cols: ss[-1] = ss[-1][:cols - 8] + ss[-1][-8:]
      return '\n'.join(ss)
    __repr__ = __str__

    @staticmethod
    def test():
      ## subclass numbyte
      class numbyte2(numbyte): pass

      ## create bytearray containing 3x4 array of longlong
      integers = numbyte2('i', range(12), shape0 = 3, shape1 = 4)
      print( integers.debug() )

      ## modify underlying bytearray
      integers.bytes()[0] = 0xff; integers.bytes()[1] = 0xff
      print( integers.bytes() )
      print( integers.debug() )

      ## bytearray as sequence
      print( 2 in integers )
      print( integers.count(2) )
      print( integers.index(2) )
      for aa in integers.rows(): print( aa )
      ## slice
      print( integers[1:, 2:].debug() )
      ## transpose
      print( integers.T()[2:, 1:].debug() )
      ## reshape
      print( integers.reshape(2, -1).debug() )
      ## setslice
      integers.T()[2:, 1:] = range(4); print( integers )

      ## almost all arithmetic operations are inplace - use copy to avoid side-effects
      ## recast to double
      floats = integers.recast('f') / 3; print( floats )
      ## copy
      print( floats.copy() + integers[0, :] )
      ## inplace
      print( floats + integers[:, 0] )
      ## inplace
      print( floats - integers[:, 0] )
      ## inplace
      print( floats ** 2 )
      ## inplace
      print( floats.sqrt() )

      ## the only inplace exception are logical comparisons, which return new char arrays
      print( floats )
      ## copy as char
      print( floats == floats[0, :] )
      ## copy as char
      print( floats > 1.5 )

  @closure()
  def _():
    for aa in 'eq ne lt le gt ge'.split(' '): ## logical comparison
      @closure()
      def _(aa = '__{}__'.format(aa)):
        def _(self, bb): cc = self.zeros('c', self.shape0(), self.shape1()); return getattr(cc._math_op, aa)(cc, self, bb)
        setattr(numbyte, aa, _)







  # ## quicktest
  # def quicktest(ipath = ""):
    # ## img2txt
    # # if not ipath: ipath = os.path.join(pseudomethod.__path__[0], "mario.png")
    # # ipath ..print()
    # # png2txt(ipath) ..print()

    # marray.test()

  # class img2txt(object):
      # def _shape(self): return self.barr[0] * 256 + self.barr[1], self.barr[2] * 256 + self.barr[3]
      # shape = property(_shape)
      # def __str__(self): return ansi_str(self.barr)
      # def topng(self, fpath): png_write(fpath, self.barr)

  # def png2txt(fpath, scale = 1, plaintxt = None, wmatch = 2, wmismatch = 4): aa = img2txt(); aa.barr = png_read(fpath, scale, True if plaintxt else False, wmatch, wmismatch); return aa

  if 'test' not in globals(): test = numbyte
if 'test' not in globals(): test = pseudomethod
def quicktest(): test_class(pseudomethod, 'main.py')
