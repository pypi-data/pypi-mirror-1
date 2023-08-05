#!/usr/bin/env python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/code_util.py $
$Id: code_util.py 26358 2005-03-16 15:08:21Z dbinger $
"""
from compiler.ast import Function, Class, AssName, Name
from compiler.ast import Import, From, ListComp, Lambda
from optparse import OptionParser
from os import listdir
from os.path import join, isdir, isfile, realpath, basename
from qpy.compile import parse
from sets import Set
from types import ModuleType
import sys

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
    return realpath(module_file)

def file_tree(module, out):
    if module is None:
        source_file = '<stdin>'
        raw_source = sys.stdin.read()
    else:
        try:
            source_file = get_source_file(module)
            raw_source = open(source_file, 'rU').read()
        except Exception, e:
            raise e
            source_file = '<str>'
            raw_source = module
    try:
        root_node = parse(raw_source, source_file)
    except:
        out.write(source_file + '\n')
        raise
    return source_file, root_node


def check(module, verbose=False, check_imports=True, out=sys.stdout,
          approved_stars=('types')):

    if verbose:
        print "CHECK", module
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

    unresolved = []
    namespace = Set()

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
                    if node.modname in approved_stars:
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

    filename, root_node = file_tree(module, out)
    import __main__
    traverse(root_node,
             [[root_node, [], Set(dir(__main__) +
                                  dir(__main__.__builtins__))]])
    for lineno, prefix, name in unresolved:
        if name=='__path__' and filename.endswith('__init__.py'):
            continue
        if name in namespace:
            if not verbose:
                continue # skip these
            message = "used before definition"
        else:
            message = "not found"
        out.write("%s:%s: %s %s.\n" % (
            filename, lineno, '.'.join(prefix + [name]), message))

    if not check_imports:
        return

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
    walk(root_node)
    for as_name, name in unused_imports.items():
        if as_name == name:
            if name not in ('SitePublisher', 'SiteRootDirectory'):
                out.write("%s: %s\n" % (filename, name))
        if as_name != name:
            if (not as_name.startswith('_') and
                not as_name in ('qpy_h8', 'qpy_u8')):
                # If you want to import something for a side-effect,
                # but you don't want this warning, make the import
                # an 'as' import and make the name start with underscore.
                out.write("%s: %s as %s\n" % (filename, name, as_name))


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--verbose', action='store_true', default=False)
    parser.set_description(
        'Check python source files for unknown name errors '
        'and for unused imports. '
        'The arguments name files to check or '
        'directories to check recursively. '
        'If no arguments are given, the current directory '
        'is checked. '
        'If there is a recursion, it excludes ".svn", "build", '
        'and "dist" directories, and includes files that end '
        'in ".py", ".qpy", or ".ptl".')
    (options, args) = parser.parse_args()
    if args:
        todo = args
    else:
        todo = ['.']
    while todo:
        arg = todo.pop()
        if basename(arg) in ['.svn', 'dist', 'build']:
            continue
        elif (isfile(arg) and
              arg in sys.argv or
              (arg.endswith('.py') or
               arg.endswith('.qpy') or
               arg.endswith('.ptl'))):
            check(arg, verbose=options.verbose)
        elif isdir(arg):
            todo.extend([join(arg, item) for item in listdir(arg)])
