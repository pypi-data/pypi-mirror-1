## import codetree; reload(codetree); from codetree import *
from __future__ import py3k_sugar
import os, sys, traceback
if os.name != 'posix': sys.stderr.write('\ncodetree requires linux operating system\n\n'); exit()
if sys.version_info[:2] != (3, 1): sys.stderr.write('\ncodetree requires Python 3.1\n\n'); exit()
__extension__ = 'codetree' in 'ascii' 'porn numbyte'







if 0: ## __init__ beg
  import os, pydoc, re, sys, traceback
  def closure(*args, **kwds): return lambda fnc: fnc(*args, **kwds)
  def identity(aa): return aa
  def _import(ss, globals = globals()):
    for aa in ss.split(' '): globals[aa] = __import__(aa, globals)
    return identity

  #### pseudomethod parser
  @_import('ast collections tempfile')
  class parser(ast.NodeVisitor):
    @staticmethod
    def compile_exec(ss, fpath): node = parser().parse(ss, fpath, 'exec', sugar_pseudomethod = True); return compile(node, fpath, 'exec')

    @staticmethod
    def exec(ss, globals, locals = None, fpath = '<file>'): exec(parser.compile_exec(ss, fpath), globals, locals)

    ## recursively print nodes in ast object for debugging
    @staticmethod
    def printnode(node, depth = ''):
      ss = '\t'.join('{} {!r}'.format(*aa) for aa in sorted(node.__dict__.items()))
      print( '{}{}\t{}'.format(depth, str(type(node)), ss) )
      for aa in ast.iter_child_nodes(node): parser.printnode(aa, depth = depth + ' ')

    def parse(self, ss, fpath, mode, sugar_pseudomethod = None,
              rgx_pseudomethod3 = re.compile('([^.])\.\.\.\.(\w[\w. ]*\()'),
              rgx_pseudomethod2 = re.compile('([^.])\.\.\.(\w[\w. ]*\()'),
              rgx_pseudomethod1 = re.compile('([^.])\.\.(\w[\w. ]*\()'),
              ):
      self.ss0 = ss0 = ss; self.ss = ss; self.fpath = fpath; self.mode = mode

      if sugar_pseudomethod:
        ss = rgx_pseudomethod3.sub('\\1.__pseudomethod2__.\\2', ss) ## parse pseudomethod3 syntax
        ss = rgx_pseudomethod2.sub('\\1.__pseudomethod1__.\\2', ss) ## parse pseudomethod2 syntax
        ss = rgx_pseudomethod1.sub('\\1.__pseudomethod0__.\\2', ss) ## parse pseudomethod syntax

      self.node = node = ast.parse(ss, fpath, mode);
      if sugar_pseudomethod: self.calls = collections.deque(); self.visit(node); assert not self.calls ## parse pseudomethod node
      return node

    class exc_revisit(Exception): pass

    def exc_syntax(self, node): return SyntaxError('dangling pseudomethod', (self.fpath, node.lineno, node.col_offset, self.ss0))

    def visit_Call(self, node):
      node.func.parent = node
      self.calls.append(node)
      try:
        try: self.generic_visit(node)
        except self.exc_revisit: self.generic_visit(node) ## should revisit @ most once
      except self.exc_revisit as node:
        raise self.exc_syntax(node)
      self.calls.pop()

    ## hack node if it contains __pseudomethod0__ attr
    def visit_Attribute(self, node):
      node.value.parent = node
      try:
        if node.value.attr not in ('__pseudomethod0__', '__pseudomethod1__', '__pseudomethod2__'): raise Exception
      except:
        return self.generic_visit(node)

      if not hasattr( node, 'parent' ): raise self.exc_syntax(node) ## pseudomethod node should always have a parent
      self.calls[-1].args.insert(int(node.value.attr[-3]), node.value.value) ## add arg0 to call node
      fnc = ast.copy_location(ast.Name(node.attr, ast.Load()), node) ## create fnc name node
      if isinstance(node.parent, ast.Call): node.parent.func = fnc ## fnc call
      else: node.parent.value = fnc ## method call
      raise self.exc_revisit(node)

    @staticmethod
    def test():
      ss = 'AAAA (BBBB)'
      ss = 'BBBB .__pseudomethod0__ .AAAA()'

      ss = 'AAAA .BBBB (CCCC)'
      ss = 'BBBB .__pseudomethod0__ .AAAA()'

      ss = 'AAAA (BBBB (CCCC))'
      ss = 'CCCC .__pseudomethod0__ .AAAA() .__pseudomethod0__ .BBBB()'

      ss = 'AAAA .BBBB (CCCC)'
      ss = 'CCCC .__pseudomethod0__ .AAAA .BBBB()'

      ss = 'AAAA (BBBB, CCCC (DDDD))'
      ss = 'DDDD .__pseudomethod0__ .CCCC() .__pseudomethod1__ .AAAA(BBBB)'

      node = parser().parse(ss, '', 'exec', sugar_pseudomethod = 1)
      print( ss ); parser.printnode(node)



  #### import hook
  @_import('builtins imp importlib importlib.util')
  @_import('locale subprocess') ## PYTHON BUG
  class _importer(object):
    sugar = '\nfrom __future__ import py3k_sugar\n' ## magic line enabling py3k_sugar syntax
    maxfilesize = 0x100000

    class ImportError(Exception): pass

    def __init__(self):
      sys.meta_path[:] = [self] + [aa for aa in sys.meta_path if not hasattr(aa, 'py3k_sugar')] ## reset sys.meta_path
      sys.path_importer_cache = {} ## reset cache

    def find_module(self, mname, path = None):
      if 0: print( 'py3k_sugar find_module(mname = {}, path = {})'.format(mname, path) ) ## DEBUG
      fname = os.path.join(*mname.split('.')) + '.py'
      for dpath in path or sys.path:
        fpath = os.path.join(dpath, fname)
        if os.path.exists(fpath):
          if os.path.getsize(fpath) > self.maxfilesize: raise self.ImportError('py3k_sugar - {} > {} bytes'.format(fpath, self.maxfilesize))
          with open(fpath, 'r') as ff:
            ss = ff.read(1024)
            if self.sugar in ss:
              ss = ss.replace(self.sugar, '\n#' + self.sugar[1:], 1); self.found = fpath, ss + ff.read(); return self

    @importlib.util.set_loader
    @importlib.util.set_package
    @importlib.util.module_for_loader
    def load_module(self, mm):
      try:
        fpath, ss = self.found; mm.__file__ = fpath
        if 0: print( 'py3k_sugar load_module(mm = {}, fpath = {})'.format(mm, fpath) ) ## DEBUG
        parser.exec(ss, mm.__dict__, fpath = fpath); return mm ## parse & load module
      except: print( '\nFAILED py3k_sugar load_module(mm = {}, fpath = {})\n'.format(mm, fpath) ); raise ## notify user exception originated from failed py3k_sugar import



  @closure() ## import codetree.main
  def _():
    global importer; importer = _importer(); builtins.reload = imp.reload
    if '_IMPORT_EXTENSION' not in globals(): global _IMPORT_EXTENSION; _IMPORT_EXTENSION = __extension__
    fpath, ss = importer.find_module('codetree.main').found
    global __path__; __path__ = [os.path.abspath(os.path.dirname(fpath))]
    parser.exec(ss, globals(), fpath = fpath)
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

  ## print test log
  def test_class(type, fpath):
    tt = codetree.src(type, fpath) ...codetree.src(type.test)
    rgx = re.compile('^' + ' ' * tt[1].depth(), re.M)
    for ii, aa in enumerate(*tt[1:]):
      print( re.sub(rgx, '>>> ', aa) )
      parser.exec( re.sub(rgx, '', aa), globals() )

  ## generate unique alphanumeric string guaranteed not to occur in s
  def uniquestr(s, kwd = 'qjzx'):
    while kwd in s: kwd += hex(id(kwd))
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

  def __getitem__(self, ii):
    return list.__getitem__(self, ii) if isinstance(ii, int) else type(self)(Tree(*list.__getitem__(self, ii)))

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
    ss = open('codetree/_main.cpp').read()
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

  def __init__(self, lines, ignore = ignore):
    if not lines: return
    if isinstance(lines, Tree): return Tree.__init__(self, *lines)
    if isinstance(lines, str): lines = lines.split('\n')
    lines = iter(lines)
    try: self._init(lines, ignore, next(lines), depth0 = 0)
    except StopIteration: pass

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
    self.__dict__.update(kwds)

  ## serializable: codetree(codeobj) == eval( repr( codetree( codeobj ) ) )
  def __repr__(self): return 'codetree({}, **{})'.format(repr(list(self)), self.__dict__)

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
    src = 'def foo():\n def bar(): print("hello")\n return bar()\nfoo()'; print( src )

    ## compile source code
    codeobj = compile(src, '', 'exec')
    exec( codeobj )

    ## convert code object into editable codetree
    tree = codetree(codeobj)

    ## edit / compile / exec codetree
    aa, depth, pos, subtree = tree.find('hello')
    subtree[pos] = 'goodbye'
    exec( tree.compile() )

    ## codetree structure
    print( tree )

    ## disassemble codetree
    print( tree.dis() )







if 1: ######## BUILD
  from distutils import core, dist, log

  _VERSION = '2009.12.24.py3k.cpp'
  _MANIFEST = '''setup.py
codetree/README
codetree/lucida06x10.bmp
codetree/_main.cpp
codetree/main.py
codetree/mario.png'''
  _README = open(__path__[0] + '/README').read()
  _DESCRIPTION = re.search('DESCRIPTION: (.*)', _README).group(1)
  _README = '''{}

  REQUIRES PYTHON3.1

  QUICK TEST: $ python3.1 setup.py build dev --quicktest

  {}
  '''.format(_DESCRIPTION, _README)



  ## custom Distribution class
  class Distribution(dist.Distribution):
    _dist = dist.Distribution

    class dev(core.Command):
      def initialize_options(self):
        self.subcommands = []
        for aa in self.user_options: bb = aa[0].replace('=', '').replace('-', '_'); setattr(self, bb, aa[1]); self.subcommands.append(bb)

      def finalize_options(self): pass

      def run(self, **kwds):
        for aa in self.subcommands: setattr(DISTRIBUTION, aa, getattr(self, aa))
        DISTRIBUTION.run(**kwds)

      description = 'developer stuff'
      user_options = [('alias=', None, 'alias package'),
                      # ('doc', None, 'print doc'),
                      # ('echo', None, 'echo'),
                      ('force', None, 'force'),
                      ('pkginfo', None, 'create pkg-info'),
                      # ('readme', None, 'readme'),
                      ('quicktest', None, 'run quick tests'),
                      ('sdist-test=', None, 'test sdist package'),
                      ('test=', None, 'test specific functionality'),
                      ('uninstall=', None, 'uninstall'),
                      ]

    def __init__(self, *args, dev = dev, **kwds): self._dist.__init__(self, *args, **kwds); self.cmdclass['dev'] = dev; global DISTRIBUTION; DISTRIBUTION = self;

    def run_command(self, command, **kwds):
      if 'rerun' in kwds: self.have_run[command] = not kwds['rerun']
      if self.have_run.get(command): return ## Already been here, done that? then return silently.
      log.info('\nrunning {}'.format(command)); cmd_obj = self.get_command_obj(command); cmd_obj.ensure_finalized() ## get cmd
      if 0: print( 'DEBUG {}\tcmd_obj={}\tsub_cmd={}\tkwds={}'.format(command, cmd_obj, cmd_obj.get_sub_commands(), kwds) ) ## DEBUG
      if 1: cmd_obj.byte_compile = lambda *args, **kwds: None ## disable byte compile
      if command == 'build_ext': self.pre_build_ext(cmd_obj, **kwds) ## pre build_ext
      elif command == 'sdist': self.append_pkginfo(); open('MANIFEST', 'w').write(_MANIFEST)

      cmd_obj.run(); self.have_run[command] = True ## run cmd

      if command == 'install': self.post_install(cmd_obj, **kwds) ## post install

    compiler_so = ['gcc', '-pthread', '-fno-strict-aliasing', '-DNDEBUG', '-g', '-fwrapv', '-O0', '-Wall', '-fPIC']

    def run(self):
      if self.force: self.get_command_obj('build_ext').force = True
      self.run_command('build_ext', compiler_so = self.compiler_so) ## auto build
      if self.alias:
        assert self.alias != 'ascii' + 'porn', self.alias
        try: dpath = os.path.abspath(self.alias); assert (os.getcwd() + '/') in dpath, (os.getcwd(), dpath); system( 'rm -r {}/*'.format(dpath) ) ..print()
        except subprocess.CalledProcessError: traceback.print_exc()
        for aa in _MANIFEST.split('\n'):
          bb = 'setup.py' if aa == 'setup.py' else aa.replace('codetree', self.alias)
          if 'README' in aa: system( 'cp codetree/README.{} {}/README'.format(self.alias, self.alias) ) ..print()
          else:
            print( 'aliasing {} -> {}'.format(aa, bb) )
            if aa[-4:] not in '.bmp .png .cpp .hpp': ss = open(aa).read().replace('README', 'README').replace('codetree', self.alias).replace('setup.py', 'setup.py'); open(bb, 'w').write(ss)
            else: system( '  cp -a {} {}'.format(aa, bb) ) ..print()
        system( 'python3.1 setup.py {}'.format(' '.join(sys.argv[3:])), block = None ); exit()
      if self.pkginfo: self.append_pkginfo()
      if self.quicktest: self.run_test('codetree')
      if self.sdist_test:
        self.run_uninstall(self.sdist_test); self.get_command_obj('install').prefix = self.sdist_test; self.run_command('install')
        system( 'cd /tmp; python3.1 -c "import codetree; codetree.quicktest()"' ) ..print()
        self.run_uninstall(self.sdist_test); self.run_command('sdist'); fpath = self.get_command_obj('sdist').archive_files[0]
        system( 'cp {} index_html/sdist/{}'.format(fpath, os.path.basename(fpath)) ) ..print() ## archive sdist
        system( 'rm -r test/*' ) ..print()
        system( 'cd test; tar -xzf ../{}'.format(fpath) ) ..print()
        system( 'cd test/{}; python3.1 setup.py install'.format(os.path.basename(fpath).replace('.tar.gz', '')), block = None ) ..print()
        system( 'cd /tmp; python3.1 -c "import codetree; codetree.quicktest()"' ) ..print()
      if self.test: self.run_test(self.test)
      if self.uninstall: self.run_uninstall(self.uninstall)

    def run_test(self, type): system( 'python3.1 -c "import codetree; codetree.test_class(codetree.{}, \'main.py\')"'.format(type), block = None)

    def run_uninstall(self, prefix): cmd = self.get_command_obj('install'); cmd.prefix = prefix; cmd.ensure_finalized(); system( 'rm -Ir {}'.format(os.path.join(cmd.install_lib, 'codetree')) ) ..print()

    def append_pkginfo(self): self.metadata.long_description += 'DEMO USAGE:\n\n>>> from codetree import *\n' + system( 'python3.1 -c "import codetree; codetree.test_class(codetree.codetree, \'main.py\')"' ); self.metadata.write_pkg_file(open('README', 'w')); pydoc.pager(open('README').read())

    def post_install(self, cmd, **kwds): dpath = cmd.install_lib + 'codetree/'; self.get_command_obj('build_ext').force = True; self.run_command('build_ext', rerun = True, install_path = dpath)

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
        name, aa = aa.groups(); fpath = 'codetree/{}.cpp'.format(name)
        src += '\nnamespace {} {{ {} }}\n'.format(name, self.METHOD_init(aa))
      src = '\n#define PYMETH_SIZE {}\n'.format(src.count('PYMETH_ADD') // 2 + 1) + src ## optimize method list size
      return src

    def METHOD_init(self, src):
      ss = ''
      for aa in re.finditer('(PYMETH_ADD_\w+) PyObject \*,*py_(\w+)', src): ss += '_{}({});\n'.format(*aa.groups())
      return '\nvoid METHOD_init() {{ int ii; ii = 0; {} }}\n'.format(ss)

    def pre_build_ext(self, cmd, **kwds):
      for aa in open('codetree/_main.cpp').read().replace('\\\n', '') ....re.sub('//+.*', '') ...re.finditer(re.compile('\nnamespace (\w+) {(.*?\n)}', re.S)):
        name, mm = aa.groups(); fpath = 'codetree/{}.cpp'.format(name)

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
          open('codetree/numbyte.hpp', 'w').write(self.c2h(mm))

        if name == 'base': open('codetree/base.hpp', 'w').write(self.c2h(mm)) ## base header
        else: mm = self.preprocess(mm)
        if not os.path.exists(fpath) or open(fpath).read() != mm: open(fpath, 'w').write(mm)

      for aa in cmd.extensions:
        name = aa.name.replace('codetree.', '')
        if not os.path.lexists('codetree/{}.so'.format(name)): system( 'ln -s ../{}/codetree/{}.so codetree/{}.so'.format(cmd.build_lib, name, name) ) ..print() ## copy built library

      cmd.build_extension = lambda aa: self.build_extension(cmd, aa, **kwds)

    ## custom extension compiler and linker
    @staticmethod
    def build_extension(self, ext, compiler_so = [], install_path = '', **kwds):
      sources = ext.sources
      ext_path = self.get_ext_fullpath(ext.name)
      depends = sources + ext.depends
      from distutils.dep_util import newer_group
      if not (self.force or newer_group(depends, ext_path, 'newer')): log.debug('skipping "%s" extension (up-to-date)', ext.name); return
      else: log.info('building "%s" extension', ext.name)
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







if '_SETUP' in globals(): ######## SETUP
  core.setup(
    distclass = Distribution,
    name = 'codetree',
    version = _VERSION,
    author = 'kai zhu',
    author_email = 'kaizhu256@gmail.com',
    license = 'gpl',
    url = 'http://pypi.python.org/pypi/codetree',
    description = _DESCRIPTION,
    long_description = _README,
    packages = ['codetree'],
    package_dir = {'codetree': 'codetree'},
    data_files = [
    ('lib/python3.1/site-packages/codetree', ['codetree/mario.png']),
    ('lib/python3.1/site-packages/codetree', ['codetree/README']),
    ],
    ext_modules = [
    # core.Extension('codetree.base', sources = ['codetree/base.cpp'], libraries = ['png']),
    # core.Extension('codetree._module', sources = ['codetree/_module.cpp'], libraries = ['png'], extra_objects = ['codetree/base.so']),
    core.Extension('codetree.base', sources = ['codetree/base.cpp']),
    core.Extension('codetree._module', sources = ['codetree/_module.cpp'], extra_objects = ['codetree/base.so']),
    core.Extension('codetree._numbyte', sources = ['codetree/_numbyte.cpp'], extra_objects = ['codetree/base.so']),
    core.Extension('codetree._math_op', sources = ['codetree/_math_op.cpp'], extra_objects = ['codetree/base.so', 'codetree/_numbyte.so']),
    ] if __extension__ else [],
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
    # 'Topic :: Utilities',
    ])







if _IMPORT_EXTENSION: ######## EXTENSION
  for aa in '_module _numbyte _math_op'.split(' '): exec('from codetree.{} import *'.format(aa, aa), globals())
  class numbyte(_numbyte._numbyte, _math_op._math_op):
    _base = _numbyte._numbyte
    _math = _math_op._math_op

    def debug(self): return '{} {} refcnt={} tcode={} tsize={} offset={} shape=<{} {}> stride=<{} {}> transposed={}\n{}'.format(type(self), self.tcode(), refcnt(self), self.tcode(), self.tsize(), self.offset(), self.shape0(), self.shape1(), self.stride0(), self.stride1(), self.transposed(), self)
    def recast(self, tcode): return bytearray(len(self) * self.tsize_from_tcode(tcode)) ....self._base.__new__(type(self), tcode).reshape(self.shape0(), self.shape1()) ..self.copyto()

    def __copy__(self): return self.recast(self.tcode())
    copy = __copy__

    def __new__(type, tcode, arr, shape0 = None, shape1 = -1):
      self = None
      if isinstance(arr, numbyte): self = arr.retype(type).recast(tcode)
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
        aa = '[{}]'.format(self[ii, :ll] ..self._base.__str__()[:-1])
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
      print( floats == floats[:, 1] )
      ## copy as char
      print( floats > 1.5 )

  @closure()
  def _():
    for aa in 'eq ne lt le gt ge'.split(' '): ## bool comparison
      @closure()
      def _(aa = '__{}__'.format(aa)):
        def _(self, bb):
          cc = self.zeros('c', self.shape0(), self.shape1())
          # return getattr(cc._base, aa)(cc, self, bb)
          return getattr(cc._math, aa)(cc, self, bb)
        setattr(numbyte, aa, _)

  if 'codetree' not in globals(): codetree = numbyte
  def quicktest(): codetree.test()
