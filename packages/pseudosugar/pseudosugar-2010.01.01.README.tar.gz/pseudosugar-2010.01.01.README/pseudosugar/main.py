## import pseudosugar; reload(pseudosugar); from pseudosugar import *
import os, sys
if os.name != 'posix': sys.stderr.write('\npseudosugar requires linux os\n\n'); exit()
if sys.version_info[:2] != (3, 1): sys.stderr.write('\npseudosugar requires python3.1\n\n'); exit()

if 0: ######## INIT
  import pseudosugar as _MODULE
  if '_SETUP' not in globals(): _SETUP = sys.modules.get('pseudosugar.setup', None)

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

  #### pseudosugar compiler
  @_import('ast collections re')
  class pseudo_compiler(ast.NodeVisitor):
    ## convenience function
    @staticmethod
    def exec(ss, globals, locals = None, fpath = '<file>'): exec( pseudo_compiler().compile(ss, fpath, 'exec'), globals, locals )

    ## recursively print nodes in ast object for debugging
    @staticmethod
    def debugnode(node, depth = ''):
      ss = '\t'.join('{} {!r}'.format(*aa) for aa in sorted(vars(node).items()))
      ss = '{}{}\t{}\n'.format(depth, str(type(node)), ss)
      for aa in ast.iter_child_nodes(node): ss += pseudo_compiler.debugnode(aa, depth = depth + ' ')
      return ss

    ## parse string into legal python syntax
    @staticmethod
    def parse_string(ss,
                     rgx_pseudometh2 = re.compile(' \.\.(\w[\w. ]*\()'),
                     rgx_pseudometh3 = re.compile(' \.\.\.(\w[\w. ]*\()'),
                     rgx_pseudometh4 = re.compile(' \.\.\.\.(\w[\w. ]*\()'),
                     rgx_prefixop_print = re.compile('(^|\W)print@ '),
                     rgx_prefixop = re.compile('(\w)<<<< '),
                     rgx_postfixop = re.compile(' >>>>(\w)'),
                     ):
      ss = rgx_pseudometh2.sub(' .__pseudometh2__.\\1', ss) ## parse pseudometh2 syntax
      ss = rgx_pseudometh3.sub(' .__pseudometh3__.\\1', ss) ## parse pseudometh3 syntax
      ss = rgx_pseudometh4.sub(' .__pseudometh4__.\\1', ss) ## parse pseudometh4 syntax
      ss = rgx_prefixop_print.sub('\\1print<<<< ', ss)
      ss = rgx_prefixop.sub('\\1.__prefixop4__(), ', ss)
      ss = rgx_postfixop.sub(' ,__postfixop4__().\\1', ss)
      return ss

    @staticmethod
    def unparse_string(ss): return ss.replace(',__postfixop4__().', '>>>>').replace('.__prefixop4__(),', '<<<<').replace('print<<<<', 'print@').replace('.__pseudometh4__.', '....').replace('.__pseudometh3__.', '...').replace('.__pseudometh2__.', '..')

    def compile(self, ss, fpath, mode, flags = 0, dont_inherit = 0, parse_string = True, return_ast = None):
      if parse_string: self.ss = ss; ss = self.parse_string(ss)
      else: self.ss = self.unparse(ss)
      self.fpath = fpath; self.mode = mode; self.node = node = ast.parse(ss, fpath, mode); self.parents = collections.deque()
      try: self.visit(node)
      except:
        for aa in self.parents:
          if hasattr(aa, 'lineno'): raise self.syntaxerr('invalid sugar syntax', aa.lineno, aa.col_offset)

      assert not self.parents ## parse pseudosugar node
      if return_ast: return node
      return compile(node, fpath, mode, flags, dont_inherit)

    def syntaxerr(self, ss, lineno, col_offset): return SyntaxError(ss, (self.fpath, lineno, col_offset, '\n'.join(self.ss.split('\n')[lineno - 4: lineno])))

    @staticmethod
    def setitem(node, aa, bb):
      for cc, dd in vars(node).items():
        if dd == aa: setattr(node, cc, bb); return
        elif isinstance(dd, list) and aa in dd: dd[dd.index(aa)] = bb; return
      raise ValueError('{!r} not found in node {}'.format(aa, node))

    def visit(self, node):
      self.node = node
      if 1:
        type = node.__class__

        if type is ast.Str: node.s = self.unparse_string(node.s); return

        elif type is ast.Attribute:
          # if node.attr == '__prefixop4__': return self.prefixop(self.parents.popleft()) ## prefixop
          if node.attr == '__prefixop4__':
            call = self.parents.popleft(); call.func = call.func.value; child = call ## pop call
            for depth, parent in enumerate(self.parents): ## get args
              assert depth <= 1; args = getattr(parent, 'elts', getattr(parent, 'args', None))
              if args:
                ii = args.index(child); call.args = args[ii + 1:]; args[ii + 1:] = [] ## update args
                if ii == 0 and isinstance(parent, ast.Tuple): self.parents.rotate(-depth); self.parents.popleft(); self.setitem(self.parents[0], parent, child); self.parents.rotate(depth) ## (prefixop, ...) - delete tuple
                return self.visit(call) ## visit call
              child = parent

          elif node.attr in ('__pseudometh2__', '__pseudometh3__', '__pseudometh4__'): ## pseudometh
            for call in self.parents:
              if isinstance(call, ast.Call):
                call.args.insert(int(node.attr[12]) - 2, node.value) ## insert arg
                name = self.parents.popleft(); name = ast.copy_location(ast.Name(name.attr, ast.Load()), node) ## new name node - pop attr
                if isinstance(self.parents[0], ast.Call): self.parents[0].func = name ## fnc
                else: self.parents[0].value = name ## meth
                return self.visit(node.value) ## visit inserted arg
              else: assert isinstance(call, ast.Attribute)

        elif type is ast.Name:
          if node.id == '__postfixop4__': ## postfixop
            call = self.parents.popleft(); child = self.parents.popleft(); node.id = child.attr ## pop call, pop attr
            while True:
              parent  = self.parents.popleft() ## pop parent
              if isinstance(parent, ast.Attribute): parent.value = call.func; call.func = parent ## move call up tree
              else:
                if isinstance(child, ast.Attribute): self.setitem(parent, child, call); child = call ## bind call to 1st non-attr
                args = getattr(parent, 'elts', getattr(parent, 'args', None))
                if args:
                  ll = len(args) - 1; ii = args.index(child); call.args = args[:ii]; args[:ii] = [] ## update args
                  if ii == ll and isinstance(parent, ast.Tuple): self.setitem(self.parents[0], parent, child); parent = child ## (..., postfixop) - remove enclosing tuple
                  return self.visit(parent) ## visit parent
              child = parent

        self.parents.appendleft(node); self.generic_visit(node)
        if self.parents[0] is node: self.parents.popleft()

    def prefixop(self, call):
      call.func = call.func.value; child = call
      for depth, parent in enumerate(self.parents): ## get args
        assert depth <= 1; args = getattr(parent, 'elts', getattr(parent, 'args', None))
        if args:
          ii = args.index(child); call.args = args[ii + 1:]; args[ii + 1:] = [] ## update args
          if ii == 0 and isinstance(parent, ast.Tuple): self.parents.rotate(-depth); self.parents.popleft(); self.setitem(self.parents[0], parent, child); self.parents.rotate(depth) ## (prefixop, ...) - delete tuple
          return self.visit(call)
        child = parent

    @staticmethod
    def index(node, aa):
      for bb, cc in vars(node).items():
        if cc == aa: return bb
      raise ValueError('{!r} not found in node {}'.format(aa, node))

    @staticmethod
    def test():
      ss0, ss1 = 'aa(1)', '1 ..aa()'
      ss0, ss1 = 'bb(aa(1))', '1 ..aa() ..bb()'
      ss0, ss1 = 'bb.aa(1, 2)', '2 ...bb.aa(1)'

      ss0, ss1 = 'aa(1, 2)', 'aa<<<< 1, 2'
      ss0, ss1 = '{ aa(1, 2) }', '{ aa<<<< 1, 2 }'
      ss0, ss1 = '0, dd( 0, 0 + cc.bb(aa(1, 2)) )', '0, dd<<<< 0, 0 + cc.bb<<<< aa<<<< 1, 2'

      ss0, ss1 = 'aa(1, 2)', '1, 2 >>>>aa'
      ss0, ss1 = '{aa(1, 2)}', '{1, 2 >>>>aa}'
      ss0, ss1 = 'dd(cc.bb(aa(1, 2)) + 0, 0), 0', '1, 2 >>>>aa >>>>cc.bb + 0, 0 >>>>dd, 0'

      # ss0, ss1 = 'print(1) + 0', '1 >>>>print + 0'
      # ss0 = 'a.b.c.d()'
      # ss0, ss1 = 'list( 1, print(2, 3), 4 )', '(print<<<< 2, 3) ...list(1, 4)'
      # ss0, ss1 = 'print(None is print(1))', 'print( None is print<<<< 1 )'
      if 0: ## fail
        ss0, ss1 = 'call(*print( 1 ) )', 'call(*print<<<< 1 )'
      ss = ss0; print(ss); node = ast.parse(pseudo_compiler.parse_string(ss), '', 'exec'); print( pseudo_compiler.debugnode(node), '\n' )
      ss = ss1; print(ss); node = pseudo_compiler().compile(ss, '', 'exec', return_ast = True); print( pseudo_compiler.debugnode(node), '\n' )
  if 0: pseudo_compiler.test(); exit()

  #### pseudosugar console interpreter
  @_import('code codeop')
  class pseudo_console(code.InteractiveConsole, codeop.Compile):
    ## convenience function
    def exec(self, ss, globals = None, locals = None): self.runsource(ss, symbol = 'single')

    ## hacked codeop.Compile.call
    def __call__(self, source, filename, symbol):
      codeob = pseudo_compiler().compile(source, filename, symbol, self.flags, 1)
      for feature in codeop._features:
        if codeob.co_flags & feature.compiler_flag: self.flags |= feature.compiler_flag
      return codeob

    def __init__(self, *args, **kwds): code.InteractiveConsole.__init__(self, *args, **kwds); codeop.Compile.__init__(self, *args, **kwds); self.compile.compiler = self

  #### pseudosugar import hook
  @_import('builtins imp importlib importlib.abc importlib.util')
  @_import('locale') ## PYTHON BUG
  class pseudo_importer(importlib.abc.Finder, importlib.abc.PyLoader):
    magic = 'pseudosugar'; maxfilesize = 0x100000

    def add_hook(self):
      if 1: print( 'pseudo_importer - adding hook {} to sys.meta_path'.format(self) )
      sys.meta_path[:] = [aa for aa in sys.meta_path if getattr(aa, 'magic', None) != self.magic] + [self]; sys.path_importer_cache = {}; return self

    def find_module(self, fullname, path = None):
      if 0: print( 'pseudo_importer - find_module(fullname = {}, path = {})'.format(fullname, path) ) ## DEBUG
      fullname = fullname.split('.')
      if fullname[-1] == self.magic:
        if len(fullname) >= 2: return self ## dummy module
        fullname = ['pseudosugar'] ## alias pseudosugar -> pseudosugar
      if len(fullname) >= 2 and fullname[-2] == self.magic: del fullname[-2] ## check for magic
      else: return
      if path:
        fpath = os.path.join(path[0], fullname[-1], '.py')
        if os.path.exists(fpath): self.fpath = fpath; return self
      rpath = os.path.join(*fullname) + '.py'
      for dpath in ['.'] + sys.path:
        fpath = os.path.join(dpath, rpath)
        if os.path.exists(fpath): self.fpath = fpath; return self

    def load_module(self, fullname):
      if 0: print( 'pseudo_importer - load_module(fullname = {})'.format(fullname) ) ## DEBUG
      fullname = fullname.split('.')
      if len(fullname) >= 2 and fullname[-1] == self.magic: mm0 = sys.modules['.'.join(fullname[:-1])]; mm = imp.new_module('.'.join(fullname)); mm.__file__ = mm0.__file__; mm.__path__ = mm0.__path__;  mm.__package__ = mm0.__package__;  mm.__loader__ = self; return mm ## dummy module
      return super().load_module('')

    def get_code(self, fullname = None): return pseudo_compiler().compile(self.get_data(self.source_path()), self.source_path(), 'exec', dont_inherit = True)

    def get_data(self, fpath):
      if 0: print( 'pseudo_importer - get_data(fpath = {})'.format(fpath) ) ## DEBUG
      if os.path.getsize(fpath) > self.maxfilesize: raise ImportError('pseudo_importer - maxfilesize exceeded - {} > {} bytes'.format(fpath, self.maxfilesize))
      return open(fpath).read()

    def is_package(self, fullname = None): return None

    def source_path(self, fullname = None): return self.fpath
  if 'pseudosugar' in sys.modules: builtins.reload = imp.reload; _MODULE.IMPORTER = pseudo_importer(); IMPORTER.add_hook(); IMPORTER.find_module('pseudosugar.pseudosugar.main'); exec( IMPORTER.get_code(), globals() ); _MODULE.__fpath__ = IMPORTER.fpath
## END















######## UTIL
if 1:
  def depth(arr):
    try: return 1 + depth(arr[0])
    except TypeError: return 0

  @_import('functools itertools')
  @functools.wraps(builtins.enumerate)
  def enumerate(arr, ii = None): return itertools.count(ii) ..zip(arr) if ii else builtins.enumerate(arr)

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

  ## generate unique alphanumeric string guaranteed not to occur in ss
  @_import('random')
  def uniquestr(ss, kwd = 'qjzx', alphanum = '_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'):
    while kwd in ss: kwd += random.choice(alphanum)
    return kwd



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
    ss = open('pseudosugar/_main.cpp').read()
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

  def merge_head(self):
    out = type(self)()
    for aa in self:
      if isinstance(aa, Tree):
        aa.insert(0, out[-1]); out[-1] = aa
        while not aa[-1]: out.append(aa.pop()) ## create separate entry for trailing newlines
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
    if isinstance(aa, type): rgx = re.compile('\s*class {}\W'.format(aa.__name__))
    elif isinstance(aa, types.FunctionType): rgx = re.compile('\s*def {}\W'.format(aa.__name__))
    else: raise TypeError('invalid type <{}>'.format(type(aa)))
    if not fpath: fpath = sys.modules[aa.__module__].__file__
    if isinstance(fpath, Tree): tt = fpath
    else: ss = open(fpath).read(); tt = tree_from_indent(ss.split('\n'))
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
## END















if 1: ######## BUILD
  _import('distutils distutils.core distutils.dist distutils.log pydoc')
  import pseudosugar.pseudosugar._README as _README
  _EXTENSION = [
    distutils.core.Extension('pseudosugar.base', sources = ['pseudosugar/base.cpp']),
    distutils.core.Extension('pseudosugar._module', sources = ['pseudosugar/_module.cpp'], extra_objects = ['pseudosugar/base.so']),
    distutils.core.Extension('pseudosugar._numbyte', sources = ['pseudosugar/_numbyte.cpp'], extra_objects = ['pseudosugar/base.so']),
    distutils.core.Extension('pseudosugar._math_op', sources = ['pseudosugar/_math_op.cpp'], extra_objects = ['pseudosugar/base.so', 'pseudosugar/_numbyte.so']),
    distutils.core.Extension('pseudosugar._image', sources = ['pseudosugar/_image.cpp'], extra_objects = ['pseudosugar/base.so']),
    ] if 'pseudosugar' in 'ascii' 'porn numbyte' else []
  _MANIFEST = '''README
  setup.py
  pseudosugar/lucida06x10.bmp
  pseudosugar/_main.cpp
  pseudosugar/main.py
  pseudosugar/mario.png
  pseudosugar/_README.py'''.replace(' ', '')
  _DIST = namespace(
    name = 'pseudosugar',
    version = '2010.01.01.README',
    author = 'kai zhu',
    author_email = 'kaizhu256@gmail.com',
    license = 'gpl',
    url = 'http://pypi.python.org/pypi/pseudosugar',
    description = _README.pseudosugar.description,
    long_description = '{pseudosugar.description}\n{HEADER}{pseudosugar.body}{FOOTER}{pseudosugar.footer}'.format(**vars(_README)),
    packages = ['pseudosugar'],
    package_dir = {'pseudosugar': 'pseudosugar'},
    data_files = [
    ('lib/python3.1/site-packages/pseudosugar', ['pseudosugar/mario.png']),
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



  #### hacked distutils.dist.Distribution
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
                      ('force', None, 'force'),
                      ('pkginfo', None, 'create pkg-info'),
                      ('quicktest', None, 'run quick tests'),
                      ('sdist-test=', None, 'test sdist package'),
                      ('test=', None, 'test specific functionality'),
                      ('uninstall=', None, 'uninstall'),
                      ]

    def __init__(self, kwds, dev = dev): self._dist.__init__(self, kwds); self.cmdclass['dev'] = dev; _MODULE.BUILD = self

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
        assert self.alias != 'ascii' 'porn', self.alias ## do not overwrite master distribution
        try: dpath = os.path.abspath(self.alias); assert (os.getcwd() + '/') in dpath, (os.getcwd(), dpath); system( 'rm -r {}/*'.format(dpath) ) ..print()
        except subprocess.CalledProcessError: traceback.print_exc()
        for aa in _MANIFEST.split('\n'):
          bb = 'setup.py' if aa == 'setup.py' else aa.replace('pseudosugar', self.alias); print( 'aliasing {} -> {}'.format(aa, bb) )
          if aa[-3:] == '.py': open(bb, 'w').write( open(aa).read().replace('pseudosugar', self.alias).replace('setup.py', 'setup.py') ) ## edit and copy
          else: system( '  cp -a {} {}'.format(aa, bb) ) ..print() ## direct copy
        system( 'python3.1 setup.py {}'.format(' '.join(sys.argv[3:])), block = None ); exit()
      if self.doc: system( 'python3.1 -c "import pseudosugar; help(pseudosugar)"', block = None )
      if self.pkginfo: self.append_pkginfo()
      if self.quicktest: _MODULE._SETUP = None; reload(_MODULE); print(_MODULE); quicktest()
      if self.sdist_test:
        self.run_uninstall(self.sdist_test); self.get_command_obj('install').prefix = self.sdist_test; self.run_command('install')
        system( 'cd /tmp; python3.1 -c "import pseudosugar; pseudosugar.quicktest()"' ) ..print()
        self.run_uninstall(self.sdist_test); self.run_command('sdist'); fpath = self.get_command_obj('sdist').archive_files[0]
        system( 'cp {} index_html/sdist/{}'.format(fpath, os.path.basename(fpath)) ) ..print() ## archive sdist
        system( 'rm -r test/*' ) ..print()
        system( 'cd test; tar -xzf ../{}'.format(fpath) ) ..print()
        system( 'cd test/{}; python3.1 setup.py install'.format(os.path.basename(fpath).replace('.tar.gz', '')), block = None ) ..print()
        system( 'cd /tmp; python3.1 -c "import pseudosugar; pseudosugar.quicktest()"' ) ..print()
      if self.test: _MODULE._SETUP = None; reload(_MODULE); quicktest(self.test)
      if self.uninstall: self.run_uninstall(self.uninstall)

    def run_uninstall(self, prefix): cmd = self.get_command_obj('install'); cmd.prefix = prefix; cmd.ensure_finalized(); system( 'rm -Ir {}'.format(os.path.join(cmd.install_lib, 'pseudosugar')) ) ..print()

    def append_pkginfo(self): self.metadata.long_description += system( 'python3.1 -c "import pseudosugar; pseudosugar.quicktest()"' ); self.metadata.write_pkg_file(open('README', 'w')); pydoc.pager(open('README').read())

    def post_install(self, cmd, **kwds): dpath = cmd.install_lib + 'pseudosugar/'; self.get_command_obj('build_ext').force = True; self.run_command('build_ext', rerun = True, install_path = dpath)

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
        name, aa = aa.groups(); fpath = 'pseudosugar/{}.cpp'.format(name)
        src += '\nnamespace {} {{ {} }}\n'.format(name, self.METHOD_init(aa))
      src = '\n#define PYMETH_SIZE {}\n'.format(src.count('PYMETH_ADD') // 2 + 1) + src ## optimize method list size
      return src

    def METHOD_init(self, src):
      ss = ''
      for aa in re.finditer('(PYMETH_ADD_\w+) PyObject \*,*py_(\w+)', src): ss += '_{}({});\n'.format(*aa.groups())
      return '\nvoid METHOD_init() {{ int ii; ii = 0; {} }}\n'.format(ss)

    def pre_build_ext(self, cmd, **kwds):
      for aa in open('pseudosugar/_main.cpp').read().replace('\\\n', '') ....re.sub('//+.*', '') ...re.finditer(re.compile('\nnamespace (\w+) {(.*?\n)}', re.S)):
        name, mm = aa.groups(); fpath = 'pseudosugar/{}.cpp'.format(name)

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
          open('pseudosugar/numbyte.hpp', 'w').write(self.c2h(mm))

        if name == 'base': open('pseudosugar/base.hpp', 'w').write(self.c2h(mm)) ## base header
        else: mm = self.preprocess(mm)
        if not os.path.exists(fpath) or open(fpath).read() != mm: open(fpath, 'w').write(mm)

      for aa in cmd.extensions:
        name = aa.name.replace('pseudosugar.', '')
        if not os.path.lexists('pseudosugar/{}.so'.format(name)): system( 'ln -s ../{}/pseudosugar/{}.so pseudosugar/{}.so'.format(cmd.build_lib, name, name) ) ..print() ## copy built library

      cmd.build_extension = lambda aa: self.build_extension(cmd, aa, **kwds)

    ## hacked distutils.command.build_ext.build_ext.build_extension
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

  Distribution(vars(_DIST))
  if _SETUP: distutils.core.setup(distclass = Distribution, **vars(_DIST)) ######## SETUP
## END















if _EXTENSION and not _SETUP: ######## EXTENSION
  for aa in '_module _numbyte _math_op _image'.split(' '): exec('from pseudosugar.{} import *'.format(aa, aa), globals())
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
  @closure()
  def _():
    for aa in 'eq ne lt le gt ge'.split(' '): ## logical comparison
      @closure()
      def _(aa = '__{}__'.format(aa)):
        def _(self, bb): cc = self.zeros('c', self.shape0(), self.shape1()); return getattr(cc._math_op, aa)(cc, self, bb)
        setattr(numbyte, aa, _)

## print test log
def quicktest(type = None):
  if not type: type = 'pseudosugar' if hasattr(_README, 'pseudosugar') else 'numbyte'
  type = getattr(_README, type)
  tt = codetree.src(type.test, codetree.src(type)); rgx = re.compile('^' + ' ' * tt[1].depth(), re.M)
  tt = [re.sub(rgx, '>>> ', aa.sjoin() if isinstance(aa, Tree) else aa).replace('>>>  ', '...  ') for aa in tt[1].merge_head()]; tt[-1] = tt[-1].rstrip()
  tt.insert(0, '>>> from pseudosugar import *\n')
  mm = imp.new_module('test'); console = pseudo_console(); console.locals = vars(mm)
  for aa in tt: print(aa); console.exec( aa.replace('>>> ', '').replace('...  ', ' ') + '\n' )
