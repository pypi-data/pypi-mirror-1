## import ast2src; reload(ast2src); from ast2src import *
import os, sys
if os.name != 'posix': sys.stderr.write('\nast2src requires linux os\n\n'); exit()
if sys.version_info[:2] != (3, 1): sys.stderr.write('\nast2src requires python3.1\n\n'); exit()















if 0: ######## INIT
  import ast2src as _MODULE
  if '_SETUP' not in globals(): _SETUP = sys.modules.get('ast2src.setup', None)
  def closure(*args, **kwds): return lambda fnc: fnc(*args, **kwds)
  def identity(aa): return aa
  def _import(ss, globals = globals()):
    for aa in ss.split(' '): globals[aa] = __import__(aa)
    return identity
  class Namespace(object):
    def __init__(self, **kwds): vars(self).update(kwds)



  @_import('ast builtins collections re ' #### pseudosugar compiler
           'imp importlib importlib.abc importlib.util ' #### import hook
           'locale') ## PYTHON BUG
  class PseudoSugar(ast.NodeVisitor, importlib.abc.Finder, importlib.abc.PyLoader):
    ## convenience function
    @staticmethod
    def exec(ss, globals, locals = None, fpath = '<file>'): exec( PseudoSugar().compile(ss, fpath, 'exec'), globals, locals )

    ## recursively print nodes in ast object for debugging
    @staticmethod
    def debugnode(node, depth = ''):
      ss = '\t'.join('{} {!r}'.format(*aa) for aa in sorted(vars(node).items()))
      ss = '{}{}\t{}\n'.format(depth, str(type(node)), ss)
      for aa in ast.iter_child_nodes(node): ss += PseudoSugar.debugnode(aa, depth = depth + ' ')
      return ss

    ## parse string into legal python syntax
    @staticmethod
    def parse_str(ss,
                  rgx_pseudometh2 = re.compile(' \.\.(\w[\w. ]*\()'),
                  rgx_pseudometh3 = re.compile(' \.\.\.(\w[\w. ]*\()'),
                  rgx_pseudometh4 = re.compile(' \.\.\.\.(\w[\w. ]*\()'),
                  rgx_prefixop_print = re.compile('(^|\W)print@@ '),
                  rgx_prefixop = re.compile('(\))<<<< '),
                  rgx_postfixop = re.compile(' >>>>(\w[\w. ]*\()'),
                  ):
      ss = PseudoSugar.magic.sub('#\\1', ss, 1)
      ss = rgx_pseudometh2.sub(' .__pseudometh2__.\\1', ss) ## parse pseudometh2 syntax
      ss = rgx_pseudometh3.sub(' .__pseudometh3__.\\1', ss) ## parse pseudometh3 syntax
      ss = rgx_pseudometh4.sub(' .__pseudometh4__.\\1', ss) ## parse pseudometh4 syntax
      ss = rgx_prefixop_print.sub('\\1print()<<<< ', ss)
      ss = rgx_prefixop.sub('\\1.__prefixop4__, ', ss)
      ss = rgx_postfixop.sub(' ,__postfixop4__.\\1', ss)
      return ss

    @staticmethod
    def unparse_str(ss): return ss.replace(',__postfixop4__.', '>>>>').replace('.__prefixop4__,', '<<<<').replace('print()<<<<', 'print@@').replace('.__pseudometh4__.', '....').replace('.__pseudometh3__.', '...').replace('.__pseudometh2__.', '..')

    def parse_ast(self, ss, fpath, mode):
      node = builtins.__pseudocompile__(self.parse_str(ss), fpath, mode, ast.PyCF_ONLY_AST); self.parents = collections.deque()
      try: self.visit(node) ## parse pseudosugar node
      except: lineno, col_offset = self.visit_lineno(self.node); raise SyntaxError('invalid pseudosugar syntax', (fpath, lineno, col_offset, '\n'.join(self.unparse_str(ss).split('\n')[max(lineno - 4, 0): lineno])))
      assert not self.parents, self.parents; return node

    @staticmethod
    def compile(ss, fpath, mode, flags = 0, dont_inherit = 0):
      try: return builtins.__pseudocompile__(ss, fpath, mode, flags, dont_inherit)
      except SyntaxError: pass
      node = PseudoSugar().parse_ast(ss, fpath, mode)
      if flags & ast.PyCF_ONLY_AST: return node
      return builtins.__pseudocompile__(node, fpath, mode, flags, dont_inherit)
    if not hasattr(builtins, '__pseudocompile__'): builtins.__pseudocompile__ = builtins.compile

    @staticmethod
    def setitem(node, aa, bb):
      for cc, dd in vars(node).items():
        if dd == aa: setattr(node, cc, bb); return
        elif isinstance(dd, list) and aa in dd: dd[dd.index(aa)] = bb; return
      raise ValueError('{!r} not found in node {}'.format(aa, node))

    @staticmethod
    def visit_lineno(node):
      if hasattr(node, 'lineno'): return node.lineno, node.col_offset
      for aa in ast.iter_child_nodes(node):
        if hasattr(aa, 'lineno'): return  aa.lineno, aa.col_offset
      return 0, 0

    def visit(self, node):
      self.node = node; type = node.__class__
      if type is ast.Str: node.s = self.unparse_str(node.s); return

      elif type is ast.Attribute:
        if node.attr == '__prefixop4__': ## prefixop
          call = child = node.value; self.setitem(self.parents[0], node, child) ## call
          for depth, parent in enumerate(self.parents): ## get args
            assert depth <= 1; args = getattr(parent, 'elts', getattr(parent, 'args', None))
            if args:
              ii = args.index(child); call.args = args[ii + 1:] + call.args; args[ii + 1:] = [] ## update args
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
          call = child = self.parents.popleft(); node.id = child.attr; self.setitem(self.parents[0], child, node) ## name
          while not isinstance(child, ast.Call): call = child = self.parents.popleft() ## pop call
          while True:
            parent  = self.parents.popleft(); args = getattr(parent, 'elts', getattr(parent, 'args', None)) ## args
            if args:
              ll = len(args) - 1; ii = args.index(child); call.args = args[:ii] + call.args; args[:ii] = [] ## update args
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



    #### import hook
    magic = re.compile('(?m)^(from __future__ import pseudosugar)$'); maxfilesize = 0x100000

    def add_hook(self):
      if 1: print( 'PseudoSugar - adding hook {} to sys.meta_path'.format(self) )
      builtins.compile = PseudoSugar.compile
      sys.meta_path[:] = [self] + [aa for aa in sys.meta_path if getattr(aa, 'magic', None) != self.magic]; sys.path_importer_cache = {}; return self

    def find_module(self, fullname, path = None):
      fullname = fullname.split('.')[-1]
      if 0: print( 'PseudoSugar - find_module(fullname = {}, path = {})'.format(fullname, path) ) ## DEBUG
      try: _, fpath, (_, _, tp) = imp.find_module(fullname, path)
      except ImportError: return
      if tp == imp.PY_SOURCE: package = None
      elif tp == imp.PKG_DIRECTORY: package = True; fpath = fpath + '/__init__.py'
      else: return
      if not self.magic.search(open(fpath).read(1024)): return ## look for magic
      self.fpath = fpath; self.package = package; return self

    def get_code(self, fullname = None): return PseudoSugar.compile(self.get_data(self.source_path()), self.source_path(), 'exec', dont_inherit = True)

    def get_data(self, fpath):
      if 0: print( 'PseudoSugar - get_data(fpath = {})'.format(fpath) ) ## DEBUG
      if os.path.getsize(fpath) > self.maxfilesize: raise ImportError('PseudoSugar - maxfilesize exceeded - {} > {} bytes'.format(fpath, self.maxfilesize))
      return open(fpath).read()

    def is_package(self, fullname = None): return self.package

    def source_path(self, fullname = None): return self.fpath

    @staticmethod
    def test():
      self = PseudoSugar()
      ss0, ss1 = 'aa(1)', '1 ..aa()'
      ss0, ss1 = 'bb(aa(1))', '1 ..aa() ..bb()'
      ss0, ss1 = 'bb.aa(1, 2)', '2 ...bb.aa(1)'

      ss0, ss1 = 'aa(1, 2)', 'aa()<<<< 1, 2'
      ss0, ss1 = '{ aa(1, 2, 3, *args) }', '{ aa(3, *args)<<<< 1, 2 }'
      ss0, ss1 = '0, dd( 0, 0 + cc.bb(aa(1, 2)) )', '0, dd()<<<< 0, 0 + cc.bb()<<<< aa()<<<< 1, 2'

      ss0, ss1 = 'aa(1, 2)', '1, 2 >>>>aa()'
      ss0, ss1 = '{aa(1, 2, 3, *args)}', '{1, 2 >>>>aa(3, *args)}'
      ss0, ss1 = 'dd(cc.bb(aa(1, 2)) + 0, 0), 0', '1, 2 >>>>aa() >>>>cc.bb() + 0, 0 >>>>dd(), 0'

      ss0, ss1 = 'aa(bb(1))', 'aa()<<<< 1 >>>>bb()'
      if 0: ## fail
        ss0, ss1 = 'call(*print( 1 ) )', 'call(*print<<<< 1 )'
      ss = ss0; print(ss); node = ast.parse(self.parse_str(ss), '', 'exec'); print( self.debugnode(node), '\n' )
      ss = ss1; print(ss); node = ast.parse(self.parse_str(ss), '', 'exec'); print( self.debugnode(node), '\n' )
      ss = ss1; print(self.parse_str(ss)); node = self.compile(ss, '', 'exec', flags = ast.PyCF_ONLY_AST); print( self.debugnode(node), '\n' )
  if 0: PseudoSugar.test(); exit()
  if 'ast2src' in sys.modules: builtins.reload = imp.reload; _MODULE.IMPORTER = PseudoSugar(); IMPORTER.add_hook(); __fpath__ = os.path.join(os.path.dirname(__file__), 'main.py'); PseudoSugar.exec(open(__fpath__).read(), globals(), fpath = __fpath__)
## END















if 1: ######## UTIL
  def depth(arr):
    try: return depth(arr[0]) + 1
    except TypeError: return 0

  def dict_append(aa, bb):
    for cc in bb.keys():
      if cc not in aa: aa[cc] = bb[cc]

  @_import('itertools')
  def enumerate(arr, ii = None): return zip(itertools.count(ii), arr) if ii else builtins.enumerate(arr)

  def getitem2(idx, aa): return aa[idx]

  def lens(*args): return [len(aa) for aa in args]

  ## get current screensize - row x col
  @_import('fcntl struct termios')
  def screensize():
    try: return 'hh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '0123') >>>>struct.unpack()
    except: return (24, 80)

  def sjoin(arr, _): return _.join(str(aa) for aa in arr)

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
  class TreeBraket(Tree):
    def _init(self, lines, aa = ''):
      if not aa: aa = next(lines)
      ii = aa.find('{'); jj = aa.find('}')
      if ii == jj == -1: self.append(aa); return self._init(lines)
      if jj == -1 or -1 < ii < jj: ## {
        self.append(aa[:ii])
        self.append(TreeBraket(Tree(aa[ii])))
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
      ss = open('ast2src/_main.cpp').read()
      tt = TreeBraket(ss)
      print( tt, '\nlen={}'.format(len(tt)) )



  #### tree of lines from indent txt
  class TreeIndent(Tree):
    def depth(self, line = None, rgx = re.compile('\S')): return rgx.search(line if line else self[0]).end() - 1

    def ignore(self, line, rgx = re.compile('\S')): return not rgx.search(line) ## ignore blank line

    def _init(self, lines, ignore, aa, depth0):
      if ignore(self, aa): self.append(''); return self._init(lines, ignore, next(lines), depth0)
      depth = self.depth(aa)
      if depth < depth0: return aa
      if depth == depth0: self.append(aa); return self._init(lines, ignore, next(lines), depth0)
      else:
        Tree(aa) ..TreeIndent() ..self.append()
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
      tt = TreeIndent(ss)
      print( tt, '\nlen={}'.format(len(tt)) )



  #### python code object viewer
  @_import('dis types')
  class CodeTree(Tree):
    co_args = 'co_argcount co_kwonlyargcount co_nlocals co_stacksize co_flags co_code co_consts co_names co_varnames co_filename co_name co_firstlineno co_lnotab co_freevars co_cellvars'.split(' ')

    def __init__(self, codeobj, **kwds):
      if isinstance(codeobj, list): list.__init__(self, codeobj)
      else:
        for ii, aa in enumerate(self.co_args):
          bb = getattr(codeobj, aa)
          setattr(self, aa, list(bb) if isinstance(bb, tuple) else bb)
        Tree.__init__(self, *(CodeTree(aa) if isinstance(aa, types.CodeType) else aa for aa in self.co_consts))
        del self.co_consts;
      vars(self).update(kwds)

    ## serializable: CodeTree(codeobj) == eval( repr( CodeTree( codeobj ) ) )
    def __repr__(self): return 'CodeTree({}, **{})'.format(repr(list(self)), vars(self))

    def __str__(self, _ = ''):
      _ += '    '; __ = _ + 18 * ' '
      ss = []
      for aa in self.co_args:
        if aa != 'co_consts': bb = repr(getattr(self, aa))
        else:
          bb = '\n{}'.format(__).join(aa.__str__(__) if isinstance(aa, CodeTree) else str(aa) for aa in self)
          bb = '\n{}{}'.format(__, bb)
        '{}{:18}{}'.format(_, aa, bb) ..ss.append()
      return 'CodeTree(\n{})'.format('\n'.join(ss))

    ## codeobj == CodeTree(codeobj).compile()
    def compile(self):
      args = []
      for aa in self.co_args:
        if aa != 'co_consts': bb = getattr(self, aa)
        else: bb = tuple(aa.compile() if isinstance(aa, CodeTree) else aa for aa in self) ## recurse
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
      else: ss = open(fpath).read(); tt = TreeIndent(ss.split('\n'))
      for bb, depth, ii, cc in tt.walk():
        if re.match(rgx, bb): return Tree(bb, cc[ii + 1]) ..TreeIndent()
      raise ValueError('<{}> not found in <{}>'.format(repr(aa)[:256], repr(fpath)[:256]))



  #### reverse compiler
  class Ast2Src(PseudoSugar):
    @staticmethod
    def unparse(node): return Ast2Src().unparse_ast(node)

    def unparse_ast(self, node): self.indent = 0; self.lineno = 1; self.parents = collections.deque(); assert not self.parents, self.parents; return self.visit(node) ## parse pseudosugar node

    def format(self, fmt, *args, **kwds):
      if 'indent' in kwds: self.indent += kwds['indent']
      ss = fmt.format(*(self.visit(aa) if isinstance(aa, ast.AST) else kwds.get('join', '').join(self.visit(aa) if isinstance(aa, ast.AST) else aa for aa in aa) if isinstance(aa, (list, types.GeneratorType)) else aa for aa in args), **kwds)
      if 'indent' in kwds: self.indent -= kwds['indent']
      return ss

    def generic_visit2(self, nodes):
      for aa in ast.iter_child_nodes(nodes) if isinstance(nodes, ast.AST) else nodes: yield self.visit(aa)

    def generic_visit(self, nodes, _ = None): return (identity if _ is None else _.join)(self.visit(aa) for aa in (ast.iter_child_nodes(nodes) if isinstance(nodes, ast.AST) else nodes))

    def indent_str(self, ii = 0): return (self.indent + ii) * ' '

    const = {getattr(ast, aa): bb for aa, bb in
             (aa.replace('_', ' ').split(':') for aa in
              'And:and Or:or ' ## boolop
              'Eq:== Gt:> GtE:>= In:in Is:is IsNot:is_not Lt:< LtE:<= NotEq:!= NotIn:not_in ' ## cmpop
              'Add:+ BitAnd:& BitOr:| BitXor:^ Div:/ FloorDiv:// LShift:<< Mod:% Mult:* Pow:** RShift:>> Sub:- ' ## operator
              'Invert:~ Not:not UAdd:+ USub:- ' ## unaryop
              'Break:break; Continue:continue; Del:del Ellipsis:... Pass:pass;'.split(' '))} ## misc

    rgx_whitespace = re.compile('(\s*)')

    def visit(self, node):
      def decorator():
        nonlocal ss, newline
        if node.decorator_list:
          for aa in node.decorator_list: ss += self.format('{}@{}\n', self.indent_str(), aa); self.lineno += 1
          ss = ss[self.indent:] + self.indent_str()

      ss = ''; self.parents.appendleft(node); type = node.__class__; newline = 0;
      lineno = self.visit_lineno(node)[0]
      if lineno > self.lineno: newline = lineno - self.lineno; self.lineno = lineno

      if type in self.const: ss = self.const[type] ## const
      elif hasattr(node, 'elts'): ## seq
        if type is ast.Tuple: ss = self.format('({})', node.elts, join = ',')
        elif type is ast.List: ss = self.format('[{}]', node.elts, join = ',')
        elif type is ast.Set: ss = self.format('{{{}}}', node.elts, join = ',')
        else: raise Exception(node)
      elif issubclass(type, ast.alias): ss = '{} as {}', node.name, node.asname >>>>self.format() if node.asname else node.name
      elif issubclass(type, ast.arg): ss = self.format('{}{}', node.arg, ':' + self.visit(node.annotation) if node.annotation else '')
      elif issubclass(type, ast.arguments):
        args = list(self.generic_visit(node.args))
        if node.defaults:
          for ii, aa in enumerate(node.defaults, len(args) - len(node.defaults)): args[ii] = args[ii] + '=' + self.visit(aa)
        if node.vararg: args.append('*' + node.vararg)
        if node.kwonlyargs: args += [aa.arg + '=' + self.visit(bb) for aa, bb in zip(node.kwonlyargs, node.kw_defaults)]
        if node.kwarg: args.append('**' + node.kwarg)
        ss = ','.join(args)
      ## elif issubclass(type, ast.boolop): pass ## const
      ## elif issubclass(type, ast.cmpop): pass ## const
      elif issubclass(type, ast.comprehension): ss = self.format('for {} in {}{}', node.target, node.iter, self.format(' if {}', node.ifs) if node.ifs else '')
      elif issubclass(type, ast.excepthandler):
        if type is ast.ExceptHandler: ss = self.format('except {}{}:{}', node.type if node.type else '', ' as ' + node.name if node.name else '', node.body, indent = 1)
      elif issubclass(type, ast.expr):
        if type is ast.Attribute: ss = self.format('{}.{}', node.value, node.attr)
        elif type is ast.BinOp: ss = self.format('({})', self.generic_visit(node, ' '))
        elif type is ast.BoolOp: ss = self.format('({})', [node.values[0], node.op, node.values[1]], join = ' ')
        elif type is ast.Bytes: ss = repr(node.s)
        elif type is ast.Call:
          args = list(self.generic_visit(node.args + node.keywords))
          if node.starargs: args.append('*' + self.visit(node.starargs))
          if node.kwargs: args.append('**' + self.visit(node.kwargs))
          ss = self.format('{}({})', node.func, args, join = ',')
        elif type is ast.Compare: ss = self.format('({})', self.generic_visit(node, ' '))
        elif type is ast.Dict: ss = self.format('{{{}}}',  (self.visit(aa) + ':' + self.visit(bb) for aa, bb in zip(node.keys, node.values)))
        elif type is ast.DictComp: ss = self.format('{{{}:{} {}}}', node.key, node.value, node.generators)
        ## elif type is ast.Ellipsis: pass ## const
        ## elif type is ast.GeneratorExp: pass ## node.elt + node.generators
        elif type is ast.IfExp: ss = self.format('{} if {} else {}', node.body, node.test, node.orelse)
        elif type is ast.Lambda: ss = self.format('lambda {}:{}', node.args, node.body)
        ## elif type is ast.List: pass ## seq
        elif type is ast.ListComp: ss = self.format('[{}]', self.generic_visit(node, ' '))
        elif type is ast.Name: ss = self.visit(node.ctx); ss = self.format('{} {};', ss, node.id) if (ss and ss in 'del') else node.id
        elif type is ast.Num: ss = str(node.n)
        ## elif type is ast.Set: pass ## seq
        elif type is ast.SetComp:  ss = self.format('{{{}}}', self.generic_visit(node, ' '))
        elif type is ast.Starred: ss = '* ' + self.visit(node.value)
        elif type is ast.Str: ss = repr(node.s)
        elif type is ast.Subscript: ss = self.format('{}[{}]', node.value, node.slice)
        ## elif type is ast.Tuple: pass ## seq
        elif type is ast.UnaryOp: ss = self.format('({})', self.generic_visit(node, ' '))
        elif type is ast.Yield: ss = self.format('yield {};', self.visit(node.value))
      elif issubclass(type, ast.expr_context):
        if type is ast.AugLoad: raise NotImplementedError(node)
        elif type is ast.AugStore: raise NotImplementedError(node)
        ## elif type is ast.Del: pass ## const
        ## elif type is ast.Load: pass ## load name
        elif type is ast.Param: raise NotImplementedError(node)
        ## elif type is ast.Store: pass ## store name
      elif issubclass(type, ast.keyword): ss = self.format('{}={}', node.arg, node.value)
      elif issubclass(type, ast.mod):
        if type is ast.Expression: raise NotImplementedError(node)
        elif type is ast.Interactive: raise NotImplementedError(node)
        ## elif type is ast.Module: pass ## module
        elif type is ast.Suite: raise NotImplementedError(node)
      ## elif issubclass(type, ast.operator): pass ## const
      elif issubclass(type, ast.slice):
        if type is ast.ExtSlice: ss = self.format('{}', node.dims, join = ',')
        elif type is ast.Index: pass
        elif type is ast.Slice: ss = self.format('{}:{}:{}', node.lower, node.upper, node.step)
      elif issubclass(type, ast.stmt):
        if type is ast.Assert: ss = self.format('assert {}{};', node.test, (',' + self.visit(node.msg) if node.msg else ''))
        elif type is ast.Assign: ss = self.format('{}=({});', node.targets, node.value)
        elif type is ast.AugAssign: ss = self.format('{}{}={};', node.target, node.op, node.value)
        ## elif type is ast.Break: pass ## const
        elif type is ast.ClassDef:
          decorator()
          self.indent += 1
          args = list(self.generic_visit(node.bases))
          if node.keywords: args += [aa.arg + '=' + self.visit(aa.value) for aa in node.keywords]
          if node.starargs: args.append('*' + self.visit(node.starargs))
          if node.kwargs: args.append('**' + self.visit(node.kwargs))
          ss += self.format('class {}({}):{}', node.name, ','.join(args), node.body)
          self.indent -= 1
        ## elif type is ast.Continue: pass ## const
        elif type is ast.Delete: raise NotImplementedError(node)
        elif type is ast.Expr: ss = self.format('({});', node.value)
        elif type is ast.For: assert not node.orelse; ss = self.format('for {} in {}:{}', node.target, node.iter, node.body, indent = 1)
        elif type is ast.FunctionDef: decorator(); ss += self.format('def {}({}):{}', node.name, node.args, node.body, indent = 1)
        elif type is ast.Global: ss = self.format('global {};' + node.names)
        elif type is ast.If:
          ss = self.format('if {}:{}', node.test, node.body, indent = 1)
          if node.orelse:
            if len(node.orelse) == 1: aa = node.orelse[0]; ss += self.visit(aa).replace('if', 'elif', 1) if isinstance(aa, ast.If) else self.rgx_whitespace.sub('\\1else:', self.visit(aa), 1)
            else: self.lineno += 1; ss += self.format('\n{}else:{}', self.indent_str(), node.orelse, indent = 1)
        elif type is ast.Import: ss = self.format('import {}', self.generic_visit(node, ','))
        elif type is ast.ImportFrom: ss = self.format('from {} import {}', node.module, node.names, join = ',')
        elif type is ast.Nonlocal: ss = self.format('nonlocal ();', node.names, join = ',')
        ## elif type is ast.Pass: pass ## const
        elif type is ast.Raise: ss = self.format('raise {};', (node.exc if node.exc else ''))
        elif type is ast.Return: ss = self.format('return {};', (node.value if node.value else ''))
        elif type is ast.TryExcept: ss = self.format('try:{}', node.body, indent = 1); ss += self.generic_visit(node.handlers, '')
        elif type is ast.TryFinally: ss = self.format('try:{}', node.body, indent = 1); tt = self.format('{}', node.finalbody, indent = 1); ss += self.format('\n{}finally:{}', self.indent_str(), tt[1:])
        elif type is ast.While: assert not node.orelse; ss = self.format('while {}:{}', node.test, node.body, indent = 1)
        elif type is ast.With: ss = self.format(
          '{}{}{}{}{}',
          '' if isinstance(self.parents[1], ast.With) and not newline else 'with ',
          node.context_expr,
          [' as ', node.optional_vars] if node.optional_vars else '',
          ',' if isinstance(node.body[0], ast.With) and self.visit_lineno(node.body[0])[0] == self.lineno else ':',
          node.body, indent = 1)
      ## elif issubclass(type, ast.unaryop): pass ## const
      if not ss: ss = self.generic_visit(node, ' ')
      if self.parents[0] is node: self.parents.popleft()
      return (newline * '\n' + self.indent_str() + ss) if newline else ss

    ## compare two ast trees
    @staticmethod
    def compare(aa, bb):
      try:
        for ii, (aa, bb) in enumerate(itertools.zip_longest(ast.walk(aa), ast.walk(bb))):
          # pass
        # print( ii )
        # raise Exception
          assert type(aa) is type(bb), (type(aa), type(bb))
      except: raise Exception(ii, aa, bb, Ast2Src.visit_lineno(aa), Ast2Src.visit_lineno(bb))

    @staticmethod
    def test():
      self = Ast2Src()
      if 1:
        ss = '''aa += 1'''
        node = compile(ss, '', 'exec', ast.PyCF_ONLY_AST); tt = self.unparse_ast( node ); print( self.debugnode(node) ); ii = 0
      else: ii = 2 * 32; ss = open('ast2src/_README.py').read(); node = compile(ss, '', 'exec', ast.PyCF_ONLY_AST); tt = self.unparse_ast( node )
      '################################################################\n' + ss.split('\n')[ii:ii + 32] ..sjoin('\n') >>>>print()
      '################################################################\n' + tt.split('\n')[ii:ii + 32] ..sjoin('\n') >>>>print()
      open('a00.py', 'w').write(tt); compile(tt, 'a00.py', 'exec')
  if 0: Ast2Src.test(); exit()
## END















if 1: ######## BUILD
  _import('distutils distutils.core distutils.dist distutils.log pydoc')
  import ast2src._README as _README
  _EXTENSION = [
    distutils.core.Extension('ast2src.base', sources = ['ast2src/base.cpp']),
    distutils.core.Extension('ast2src._module', sources = ['ast2src/_module.cpp'], extra_objects = ['ast2src/base.so']),
    distutils.core.Extension('ast2src._numbyte', sources = ['ast2src/_numbyte.cpp'], extra_objects = ['ast2src/base.so']),
    distutils.core.Extension('ast2src._math_op', sources = ['ast2src/_math_op.cpp'], extra_objects = ['ast2src/base.so', 'ast2src/_numbyte.so']),
    distutils.core.Extension('ast2src._sort', sources = ['ast2src/_sort.cpp'], extra_objects = ['ast2src/base.so', 'ast2src/_numbyte.so']),
    distutils.core.Extension('ast2src._image', sources = ['ast2src/_image.cpp'], extra_objects = ['ast2src/base.so']),
    ] if 'ast2src' in 'ascii' 'porn numbyte' else []
  _MANIFEST = '''README
  setup.py
  ast2src/lucida06x10.bmp
  ast2src/_main.cpp
  ast2src/main.py
  ast2src/mario.png
  ast2src/_README.py'''.replace(' ', '')
  _DIST = Namespace(
    name = 'ast2src',
    version = '2010.01.21.ast2src',
    author = 'kai zhu',
    author_email = 'kaizhu256@gmail.com',
    license = 'gpl',
    url = 'http://pypi.python.org/pypi/ast2src',
    description = _README.ast2src.description,
    long_description = '{ast2src.description}\n{HEADER}{ast2src.body}{FOOTER}{ast2src.footer}'.format(**vars(_README)),
    packages = ['ast2src'],
    package_dir = {'ast2src': 'ast2src'},
    data_files = [
    ('lib/python3.1/site-packages/ast2src', ['ast2src/mario.png']),
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

    class Dev(distutils.core.Command):
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

    def __init__(self, kwds, dev = Dev): self._dist.__init__(self, kwds); self.cmdclass['dev'] = dev; _MODULE.BUILD = self

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
          bb = 'setup.py' if aa == 'setup.py' else aa.replace('ast2src', self.alias); print( 'aliasing {} -> {}'.format(aa, bb) )
          if aa[-3:] == '.py': open(bb, 'w').write( open(aa).read().replace('ast2src', self.alias).replace('setup.py', 'setup.py') ) ## edit and copy
          else: system( '  cp -a {} {}'.format(aa, bb) ) ..print() ## direct copy
        system( 'python3.1 setup.py {}'.format(' '.join(sys.argv[3:])), block = None ); exit()
      if self.doc: system( 'python3.1 -c "import ast2src; help(ast2src)"', block = None )
      if self.pkginfo: self.append_pkginfo()
      if self.quicktest: _MODULE._SETUP = None; reload(_MODULE); print(_MODULE); quicktest()
      if self.sdist_test:
        self.run_uninstall(self.sdist_test); self.get_command_obj('install').prefix = self.sdist_test; self.run_command('install')
        system( 'cd /tmp; python3.1 -c "import ast2src; ast2src.quicktest()"' ) ..print()
        self.run_uninstall(self.sdist_test); self.run_command('sdist'); fpath = self.get_command_obj('sdist').archive_files[0]
        system( 'cp {} index_html/sdist/{}'.format(fpath, os.path.basename(fpath)) ) ..print() ## archive sdist
        system( 'rm -r test/*' ) ..print()
        system( 'cd test; tar -xzf ../{}'.format(fpath) ) ..print()
        system( 'cd test/{}; python3.1 setup.py install'.format(os.path.basename(fpath).replace('.tar.gz', '')), block = None ) ..print()
        system( 'cd /tmp; python3.1 -c "import ast2src; ast2src.quicktest()"' ) ..print()
      if self.test: _MODULE._SETUP = None; reload(_MODULE); quicktest(self.test)
      if self.uninstall: self.run_uninstall(self.uninstall)

    def run_uninstall(self, prefix): cmd = self.get_command_obj('install'); cmd.prefix = prefix; cmd.ensure_finalized(); system( 'rm -Ir {}'.format(os.path.join(cmd.install_lib, 'ast2src')) ) ..print()

    def append_pkginfo(self): self.metadata.long_description += system( 'python3.1 -c "import ast2src; ast2src.quicktest()"' ); self.metadata.write_pkg_file(open('README', 'w')); pydoc.pager(open('README').read())

    def post_install(self, cmd, **kwds): dpath = cmd.install_lib + 'ast2src/'; self.get_command_obj('build_ext').force = True; self.run_command('build_ext', rerun = True, install_path = dpath)

    ## generate c header
    def c2h(self, src):
      ss = src.split('\n'); hh = ''; macro = {}
      for ii, aa in enumerate(ss): ## tokenize macro
        if aa and aa[0] == '#': bb = '#{}'.format(ii); macro[bb] = aa; ss[ii] = bb
      tt = Tree(); depth0 = -1; itr = ss ..TreeBraket().walk()
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
      for aa in re.finditer('(?s)\n  namespace (\w+) {(.*?\n)  }', src):
        name, aa = aa.groups(); fpath = 'ast2src/{}.cpp'.format(name)
        src += '\nnamespace {} {{ {} }}\n'.format(name, self.METHOD_init(aa))
      src = '\n#define PYMETH_SIZE {}\n'.format(src.count('PYMETH_ADD') // 2 + 1) + src ## optimize method list size
      return src

    def METHOD_init(self, src):
      ss = ''
      for aa in re.finditer('(PYMETH_ADD_\w+) PyObject \*,*py_(\w+)', src): ss += '_{}({});\n'.format(*aa.groups())
      return '\nvoid METHOD_init() {{ int ii; ii = 0; {} }}\n'.format(ss)

    def pre_build_ext(self, cmd, **kwds):
      for aa in open('ast2src/_main.cpp').read().replace('\\\n', '') ....re.sub('//+.*', '') ...re.finditer(re.compile('\nnamespace (\w+) {(.*?\n)}', re.S)):
        name, mm = aa.groups(); fpath = 'ast2src/{}.cpp'.format(name)

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
          open('ast2src/numbyte.hpp', 'w').write(self.c2h(mm))

        if name == 'base': open('ast2src/base.hpp', 'w').write(self.c2h(mm)) ## base header
        else: mm = self.preprocess(mm)
        if not os.path.exists(fpath) or open(fpath).read() != mm: open(fpath, 'w').write(mm)

      for aa in cmd.extensions:
        name = aa.name.replace('ast2src.', '')
        if not os.path.lexists('ast2src/{}.so'.format(name)): system( 'ln -s ../{}/ast2src/{}.so ast2src/{}.so'.format(cmd.build_lib, name, name) ) ..print() ## copy built library

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
  for aa in '_module _numbyte _math_op _sort _image'.split(' '): exec('from ast2src.{} import *'.format(aa, aa), globals())

  class Numbyte(_numbyte._numbyte, _math_op._math_op):
    _numbyte = _numbyte._numbyte; _math_op = _math_op._math_op

    def debug(self): return '{} {} refcnt={} tcode={} tsize={} offset={} shape=<{} {}> stride=<{} {}> transposed={}\n{}'.format(type(self), self.tcode(), refcnt(self), self.tcode(), self.tsize(), self.offset(), self.shape0(), self.shape1(), self.stride0(), self.stride1(), self.transposed(), self)
    def recast(self, tcode): return bytearray(len(self) * self.tsize_from_tcode(tcode)) ....self._numbyte.__new__(type(self), tcode).reshape(self.shape0(), self.shape1()) ..self.copyto()

    def __copy__(self): return self.recast(self.tcode())
    copy = __copy__

    def __new__(type, tcode, arr, shape0 = None, shape1 = -1):
      self = None
      if isinstance(arr, Numbyte): self = arr.retype(type).recast(tcode)
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
    def zeros(tcode, shape0, shape1): return Numbyte(tcode, bytearray(shape0 * shape1 * Numbyte.tsize_from_tcode(tcode)), shape0, shape1)

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
        setattr(Numbyte, aa, _)



## print test log
@_import('code')
def quicktest(type = None):
  if not type: type = 'ast2src' if hasattr(_README, 'ast2src') else 'numbyte'
  type = getattr(_README, type)
  tt = CodeTree.src(type.test, CodeTree.src(type)); rgx = re.compile('^' + ' ' * tt[1].depth(), re.M)
  tt = [re.sub(rgx, '>>> ', aa.sjoin() if isinstance(aa, Tree) else aa).replace('>>>  ', '...  ') for aa in tt[1].merge_head()]; tt[-1] = tt[-1].rstrip()
  tt.insert(0, '>>> from ast2src import *\n')
  mm = imp.new_module('test'); console = code.InteractiveConsole(vars(mm))
  for aa in tt: print(aa); console.runsource( aa.replace('>>> ', '').replace('...  ', ' ') + '\n' )
