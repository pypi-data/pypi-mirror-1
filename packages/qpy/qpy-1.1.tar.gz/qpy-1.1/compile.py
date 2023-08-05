"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qpy/compile.py $
$Id: compile.py 27629 2005-10-27 22:14:32Z dbinger $
"""
from compiler import misc, syntax
from compiler import pycodegen
from compiler.ast import AssName, Assign, Return, AugAssign, List, Getattr
from compiler.ast import Function, From, Module, Stmt, Name, CallFunc, Discard
from compiler.consts import OP_ASSIGN
from compiler.transformer import Transformer
from imp import get_magic
from marshal import dump
from os import unlink, stat, listdir
from os.path import splitext, join
from struct import pack
from token import ENDMARKER, NEWLINE, EQUAL
import re
import symbol
import sys

assert sys.hexversion >= 0x20300b1, 'requires Python 2.3 or newer'

source_suffix = '.qpy'

_template_re = re.compile(
    r"^(?P<indent>[ \t]*) def (?:[ \t]+)"
    r" (?P<name>[a-zA-Z_][a-zA-Z_0-9]*)"
    r" (?:[ \t]*) \[(?P<type>plain|html)\] (?:[ \t]*)"
    r" (?:[ \t]*[\(\\])",
    re.MULTILINE|re.VERBOSE)

def translate_tokens(buf):
    """
    def foo [plain] (...): -> def foo_u8(...):
    def foo [html] (...): -> def foo_h8(...):
    """
    def replacement(match):
        if match.group('type') == 'html':
            template_type = 'h8'
        else:
            template_type = 'u8'
        return '%sdef %s_%s(' % (match.group('indent'),
                                 match.group('name'),
                                 template_type)
    return  _template_re.sub(replacement, buf)


class TemplateTransformer(Transformer):

    def __init__(self, *args, **kwargs):
        Transformer.__init__(self, *args, **kwargs)
        # __template_type is a stack whose values are
        # "html", "plain", or None
        self.__template_type = []

    def _get_template_type(self):
        """Return the type of the function being compiled (
        "html", "plain", or None)
        """
        if self.__template_type:
            return self.__template_type[-1]
        else:
            return None

    def file_input(self, nodelist):
        doc = None # self.get_docstring(nodelist, symbol.file_input)
        html_imp = From('qpy', [('u8', 'qpy_u8'), ('h8', 'qpy_h8')])
        stmts = [html_imp]
        for node in nodelist:
            if node[0] != ENDMARKER and node[0] != NEWLINE:
                self.com_append_stmt(stmts, node)
        return Module(doc, Stmt(stmts))

    def funcdef(self, nodelist):
        if len(nodelist) == 6:
            assert nodelist[0][0] == symbol.decorators
            decorators = self.decorators(nodelist[0][1:])
        else:
            assert len(nodelist) == 5
            decorators = None

        lineno = nodelist[-4][2]
        name = nodelist[-4][1]
        args = nodelist[-3][2]

        if name.endswith('_h8'):
            template_type = 'html'
            name = name[:-3]
        elif name.endswith('_u8'):
            template_type = 'plain'
            name = name[:-3]
        else:
            template_type = None
        self.__template_type.append(template_type)

        if template_type is None:
            n = Transformer.funcdef(self, nodelist)
        else:
            if args[0] == symbol.varargslist:
                names, defaults, flags = self.com_arglist(args[1:])
            else:
                names = defaults = ()
                flags = 0

            # qpy_accumulation = []
            assign_qpy_accumulation = Assign(
                [AssName('qpy_accumulation', OP_ASSIGN)], List([]))
            # qpy_append = qpy_accumulation.append
            assign_qpy_append = Assign(
                [AssName('qpy_append', OP_ASSIGN)],
                Getattr(Name('qpy_accumulation'), 'append'))

            # code for function
            code = self.com_node(nodelist[-1])

            if template_type == 'html':
                closer = 'qpy_h8'
            else:
                closer = 'qpy_u8'
            ret = Return(CallFunc(Getattr(Name(closer), 'from_list'),
                                  [Name('qpy_accumulation')]))

            # wrap original function code
            new_code = Stmt([
                assign_qpy_accumulation,
                assign_qpy_append,
                code,
                ret
                ])
            doc = None
            if sys.hexversion >= 0x20400a2:
                n = Function(decorators, name, names, defaults, flags, doc,
                             new_code)
            else:
                n = Function(name, names, defaults, flags, doc, new_code)
            n.lineno = lineno

        self.__template_type.pop()
        return n

    def expr_stmt(self, nodelist):
        if self._get_template_type() is None:
            return Transformer.expr_stmt(self, nodelist)
        # Instead of discarding objects on the stack, call
        # qpy_append(obj)
        exprNode = self.com_node(nodelist[-1])
        if len(nodelist) == 1:
            n = CallFunc(Name('qpy_append'), [exprNode])
            if hasattr(exprNode, 'lineno'):
                n.lineno = exprNode.lineno
            n = Discard(n)
        elif nodelist[1][0] == EQUAL:
            nodes = [ ]
            for i in range(0, len(nodelist) - 2, 2):
                nodes.append(self.com_assign(nodelist[i], OP_ASSIGN))
            n = Assign(nodes, exprNode)
            n.lineno = nodelist[1][2]
        else:
            lval = self.com_augassign(nodelist[0])
            op = self.com_augassign_op(nodelist[1])
            n = AugAssign(lval, op[1], exprNode)
            n.lineno = op[2]
        return n

    def atom_string(self, nodelist):
        const_node = Transformer.atom_string(self, nodelist)
        template_type = self._get_template_type()
        if template_type == "html":
            return CallFunc(Name('qpy_h8'), [const_node])
        elif template_type == "plain":
            return CallFunc(Name('qpy_u8'), [const_node])
        else:
            return const_node

def parse(buf, filename):
    try:
        return TemplateTransformer().parsesuite(translate_tokens(buf))
    except SyntaxError, e:
        raise SyntaxError(str(e), (filename, e.lineno, e.offset, e.text))


class Template(pycodegen.Module):

    def _get_tree(self):
        tree = parse(self.source, self.filename)
        misc.set_filename(self.filename, tree)
        syntax.check(tree)
        return tree

    def dump(self, fp):
        mtime = timestamp(self.filename)
        fp.write('\0\0\0\0')
        fp.write(pack('<I', mtime))
        dump(self.code, fp)
        fp.flush()
        fp.seek(0)
        fp.write(get_magic())
        fp.flush()

def compile(source_name):
    base, ext = splitext(source_name)

    source_file = open(source_name)
    source = source_file.read()
    source_file.close()
    output_name = base + '.pyc'
    output = open(output_name, 'wb')
    try:
        template = Template(source, source_name)
        template.compile()
        template.dump(output)
    except:
        output.close()
        unlink(output_name)
        raise
    else:
        output.close()
        return template.code

def timestamp(filename):
    try:
        s = stat(filename)
    except OSError:
        return None
    return s.st_mtime

def compile_qpy_file(source):
    """(source:str)
    Compile the given filename if it is a .qpy file and if it does not already
    have an up-to-date .pyc file.
    """
    if source[-4:] == '.qpy':
        compile_time = timestamp(source[:-4] + '.pyc')
        if compile_time is not None:
            source_time = timestamp(source)
            if compile_time >= source_time:
                return # already up-to-date
        compile(source)

def compile_qpy_files(path):
    """(path:str)
    Compile the .qpy files in the given directory.
    """
    for name in listdir(path):
        if name[-4:] == '.qpy':
            compile_qpy_file(join(path, name))

def main():
    args = sys.argv[1:]
    if not args:
        print "no files to compile"
    else:
        for filename in args:
            compile(filename)

if __name__ == "__main__":
    main()
