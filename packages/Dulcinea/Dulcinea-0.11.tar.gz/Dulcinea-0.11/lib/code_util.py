"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/code_util.py $
$Id: code_util.py 26993 2005-06-29 21:32:39Z dbinger $
"""
from cStringIO import StringIO
from compiler import pycodegen, misc, syntax
from compiler.ast import Function, Class, Name, AssName
from compiler.ast import Import, From, ListComp, Lambda
from sets import Set
from types import ModuleType
import os.path
import sys

try:
    import quixote
    quixote.enable_ptl()
    from quixote.ptl.ptl_compile import parse
except:
    from compiler import parse #n

class ModuleGen(pycodegen.Module):
    """This subclass is here to make sure that quixote's parse
    is used, if it is available.
    """
    def _get_tree(self):
        tree = parse(self.source, self.mode)
        misc.set_filename(self.filename, tree)
        syntax.check(tree)
        self.tree = tree
        return tree

def get_source_file(module):
    """(module:str|ModuleType) -> str
    Identify source file for module.
    """
    if type(module) is str:
        try:
            module_file = __import__(module,{},{},['__file__']).__file__
        except (ImportError, ValueError):
            module_file = module
    else:
        assert type(module) is ModuleType
        module_file = module.__file__
    if module_file[-1] in 'oc':
        module_file = module_file[:-1]
    return os.path.realpath(module_file)

def file_source(module):
    if module is None:
        source_file = '<stdin>'
        raw_source = sys.stdin.read()
    else:
        try:
            source_file = get_source_file(module)
            raw_source = open(source_file, 'rU').read()
        except Exception, e:
            source_file = '<str>'
            raw_source = module
    return source_file, raw_source


def report_unknown_names(module, verbose=False, out=sys.stdout):
    filename, source = file_source(module)
    unresolved = []
    namespace = Set()

    def arg_names (node):
        result = []
        def flatten(item):
            for x in item:
                if type(x) is tuple:
                    flatten(x)
                else:
                    result.append(x)
        flatten(node.argnames)
        return result

    def traverse(node, namestack):
        childNodes = node.getChildNodes()
        if isinstance(node, Lambda):
            for child in node.defaults:
                traverse(child, namestack)
            prevnode, prevprefix, prevspace = namestack[-1]
            namestack = namestack + [[node, prevprefix + ['<lambda>'],
                                      Set(arg_names(node))]]
            childNodes = [node.code]
        if isinstance(node, Function):
            for child in node.defaults:
                traverse(child, namestack)
            childNodes = [node.code]
            prevnode, prevprefix, prevspace = namestack[-1]
            namestack = namestack + [[node, prevprefix + [node.name],
                                      Set([node.name] + arg_names(node))]]
            if isinstance(prevnode, Class):
                namestack[-1][2].add(prevnode.name)
        if isinstance(node, Class):
            prefix = namestack[-1][1]
            namestack = namestack + [[node, prefix + [node.name], Set([])]]
        if isinstance(node, Name):
            name = node.name
            if (name not in namestack[-1][2] and # local
                name not in namestack[0][2]): # global
                # search nested
                for snode, sprefix, space in namestack[1:-1]:
                    if isinstance(snode, Function) and name in space:
                        break
                else:
                    prefix = namestack[-1][1]
                    unresolved.append((node.lineno, prefix, name))
        if isinstance(node, AssName):
            namestack[-1][2].add(node.name)
            if len(namestack) == 1:
                namespace.add(node.name)
        if isinstance(node, Import):
            for name, as_name in node.names:
                namestack[-1][2].add(as_name or name)
                name_split = name.split('.')
                for index in range(len(name_split)):
                    namespace.add('.'.join(name_split[:index+1]))
        if isinstance(node, From):
            for name, as_name in node.names:
                if name == '*':
                    if verbose:
                        prefix = namestack[-1][1]
                        unresolved.append((node.lineno, prefix, name))
                    if node.modname in ('types',):
                        module = __import__(node.modname)
                        names = namestack[-1][2]
                        for name in dir(module):
                            if not name.startswith('_'):
                                names.add(name)
                else:
                    namestack[-1][2].add(as_name or name)
        if isinstance(node, ListComp):
            childNodes = tuple(node.quals +  [node.expr])
        for child in childNodes:
            traverse(child, namestack)
        if isinstance(node, (Function, Class)):
            prevnode, prefix, preset = namestack[-2]
            preset.add(node.name)
            namespace.add('.'.join(prefix + [node.name]))
            if isinstance(node, Class):
                prevnode, prefix, preset = namestack[-1]
                for name in preset:
                    namespace.add('.'.join(prefix + [name]))

    try:
        root_node = parse(source)
    except:
        out.write(filename + '\n')
        raise 
    import __main__
    if type(__builtins__) is dict:
        builtins = __builtins__.keys()
    else:
        builtins = dir(__builtins__) #n
    traverse(root_node,
             [[root_node, [], Set(dir(__main__) + builtins)]])
    for lineno, prefix, name in unresolved:
        if name in namespace:
            if not verbose:
                continue # skip these
            message = "used before definition"
        else:
            message = "not found"
        out.write("%s:%s: %s %s.\n" % (
            filename, lineno, '.'.join(prefix + [name]), message))


def report_unused_imports(module, verbose=False, out=sys.stdout):
    filename, source = file_source(module)
    unused_imports={}
    def walk(ast):
        if isinstance(ast, Import):
            for name, as_name in ast.names:
                if '.' in name:
                    # import a.b
                    # Usage of these names is not currently detected here,
                    # so we won't complain about it.
                    pass
                else:
                    unused_imports[as_name or name] = name
        if isinstance(ast, From):
            for name, as_name in ast.names:
                if '*' != name or verbose:
                    unused_imports[as_name or name] = name
        if isinstance(ast, Name):
            if ast.name in unused_imports:
                del unused_imports[ast.name]
        for child in ast.getChildNodes():
            walk(child)
    walk(parse(source))
    for as_name, name in unused_imports.items():
        if as_name == name:
            out.write("%s: %s\n" % (filename, name))
        if as_name != name:
            if verbose or not as_name.startswith('_'):
                # If you want to import something for a side-effect,
                # but you don't want this warning, make the import
                # an 'as' import and make the name start with underscore.
                out.write("%s: %s as %s\n" % (filename, name, as_name))

def main(report, out=sys.stdout):
    if not sys.argv[1:]:
        out.write("Usage: %s [<file>]+\n" % sys.argv[0])
    for arg in sys.argv[1:]:
        report(arg, out=out)

if __name__ == '__main__':
    def eq(a, b):
        assert a == b, '%r != %r' % (a, b)
    # usage
    sys.argv = ['test']
    s=StringIO()
    main(report_unused_imports, out=s)
    eq(s.getvalue(), 'Usage: test [<file>]+\n')

    # Normal command line.
    sys.argv.append('cgi')
    s=StringIO()
    main(report_unused_imports, out=s)
    eq(s.getvalue(), '')

    # module argument
    import cgi
    s=StringIO()
    report_unused_imports(cgi, out=s)
    eq(s.getvalue(), '')
    # None argument
    s=StringIO()
    input=StringIO('import sys')
    try:
        sys.stdin = input
        report_unused_imports(None, out=s)
    finally:
        sys.stdin = sys.__stdin__
    eq(s.getvalue(), '<stdin>: sys\n')

    # unused import
    s=StringIO()
    report_unused_imports(
        'import sys\n'
        'from types import IntType as num\n'
        'import compiler.ast\n',
        out=s)
    eq(s.getvalue(), '<str>: sys\n<str>: IntType as num\n')

    # unknown names
    s=StringIO()
    report_unknown_names(
        'f(a)\n'
        'def f(x, y=3):\n'
        '    z\n',
        out=s)
    eq(s.getvalue(), '<str>(1): a not found.\n<str>(3): f.z not found.\n')

    # unknown names verbose
    s=StringIO()
    report_unknown_names(
        'f(a)\n'
        'def f(x, y=3):\n'
        '    z\n',
        verbose=True,
        out=s)
    eq(s.getvalue(),
       '<str>(1): f used before definition.\n'
       '<str>(1): a not found.\n'
       '<str>(3): f.z not found.\n')

    # unknown names globals
    s=StringIO()
    report_unknown_names(
        'A=3\n'
        'def f(x, y=3):\n'
        '    return x+A+B+C\n'
        'B=2\n',
        out=s)
    eq(s.getvalue(), '<str>(3): f.C not found.\n')

    # nested
    s=StringIO()
    report_unknown_names(
        'class A:\n'
        '    B=C\n'
        '    def C(self, x=D):\n'
        '        def F(a=x):\n'
        '            return C\n'
        '        return E + B, A\n',
        out=s)
    eq(s.getvalue(),
       '<str>(2): A.C not found.\n'
       '<str>(3): A.D not found.\n'
       '<str>(6): A.C.E not found.\n'
       '<str>(6): A.C.B not found.\n')

    # list comprehensions
    s=StringIO()
    report_unknown_names('[ (x, A) for x in range(3)]', out=s)
    eq(s.getvalue(), '<str>(1): A not found.\n')

    # * imports
    s=StringIO()
    report_unknown_names('from types import *', out=s)
    eq(s.getvalue(), '')
    s=StringIO()
    report_unknown_names('from types import *', verbose=True, out=s)
    eq(s.getvalue(), '<str>(1): * not found.\n')

    # import package
    s=StringIO()
    report_unknown_names('import compiler.ast', out=s)
    eq(s.getvalue(), '')

    # lambda
    s=StringIO()
    report_unknown_names('lambda x, y=a: x+y+z', out=s)
    eq(s.getvalue(),
       '<str>(1): a not found.\n'
       '<str>(1): <lambda>.z not found.\n')

    # unknown names, syntax error
    s=StringIO()
    try:
        report_unknown_names(
            'def f()\n'
            '    x\n',
            out=s)
    except SyntaxError:
        pass

