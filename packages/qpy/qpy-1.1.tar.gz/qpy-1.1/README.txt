This is the Qpy package.

Qpy provides a convenient mechanism for generating safely-quoted html
text from python code.  It does this by implementing a quoted-string
data type and a modification of the python compiler.  (This main idea
comes from Quixote's htmltext/PTL.)


The Quoted-String Class: h8
---------------------------

The quoted-string class is named "h8".  The h8 class is a subclass of
unicode, and similarly represents sequences of characters.  The main
distinction is that h8 instances represent strings that need no
further quoting for use in html documents.  When an h8 instance is
combined with an ordinary string with an operator like "+" or "%", an
html-quoting function is applied to make sure that the result is an h8
instance for which no more quoting is needed.

Besides this infectious-quoting behavior, the h8 class differs from
unicode with respect to the default character encoding.  When the
unicode constructor is called without a specified character encoding,
it uses the global character encoding, which is normally 'ascii'.  In
h8, the constructor uses "utf-8" as the default encoding.  Similarly,
the unicode.__str__() method uses the default character encoding, but
h8.__str__() uses "utf-8".

The h8 class has a quote() method that is used by the operators to
produce html-quoted h8 instances for any given argument.  If the
argument is an h8 instance, it is returned without change since it is
known to need no more quoting.  If the argument is None, an empty h8
instance is returned.  Otherwise, the result is formed using standard
html-quoting rules, such as replacing "<' by "&lt;".

The h8 class has another classmethod, from_list() that returns a new h8
instance from the concatenation of the h8.quote()-ed values in a list.


The Qpy Compiler
----------------

The Qpy compiler is a small variation of the Python compiler, and can
best be understood understood as a source-code transformation.  The
transformation is limited to the definitions of certain functions we
call "templates".  An html template is designated in qpy source code
by "[html]" appearing after the function name in the function
definition.  For example, this is an html template:

    def f [html] (x):
        "<div>"
        x
        "</div>"

The Qpy compiler would, in effect, replace this by:

    from qpy import h8 as qpy_h8
    def f(x):
        qpy_output = []
        qpy_append = qpy_output.append
        qpy_append(qpy_h8("<div>"))
        qpy_append(x)
        qpy_append(qpy_h8("</div>"))
        return qpy_h8.from_list(qpy_output)

There are two main things going on here.  One is that every
string-literal in the body of the function is wrapped by the h8
constructor.  The assumption is that a literal string, provided by the
programmer, does not need any more quoting.  The other part of the
conversion is that expression values are accumulated on a local list,
and the default return value is the h8 instance formed by
concatenating these values, after quoting them.

The values returned by f are h8 instances, and here are some samples:

    f(None)         -> u"<div></div>"              # None becomes ''.
    f("<hr />")     -> u"<div>&lt;hr /&gt;</div>"  # Quoting happens.
    f(1)            -> u"<div>1</div>"             # Converted.
    f(h8("<hr />")) -> u"<div><hr /></div>"        # Already quoted.

The nice thing about this is that the expressions appearing in a
template, possibly including values provided from outside sources,
will always be quoted unless they are already instances of the h8
class.  If the programmer makes a mistake with respect to quoting,
it will very likely appear as over-quoting instead of lurking as
a security problem.

Templates can't have normal python docstrings after the arguments: we
just use comments.

A template may also be designated by "[plain]", instead of "[html]"
appearing after the function name.  The difference is that a plain
template will use a different basic string type, "u8" instead of "h8".
The u8 class is exactly the same as the h8 class, except that the
quoting method does *not* do any html quoting.  Plain templates can be
useful when you want to assemble css or other non-html text.

Templates can be nested arbitrarily along with other functions.  A
template's code transformation does not apply inside inner functions.


Using Qpy
---------

Source code files that include templates should be named with a ".qpy"
suffix and placed in a python package directory.  The package
__init__.py should contain the following lines to make sure that the
compiled versions of the qpy modules are up-to-date:

     from qpy.compile import compile_qpy_files
     compile_qpy_files(__path__[0])


The qpcheck.py Utility
----------------------

This package also includes qpcheck.py, a script that looks for unknown
names and unused imports in directories containing python and qpy (and
ptl) source code.


Installation
------------

       python setup.py install

   or

       python setup.py build_ext -i # build extension in place.
       Put this directory on your python path.


Example
-------

An "example" package is included.  To try it, install as described
above, start a python interpreter, and try importing the
"qpy.example.example1" module.  The real purpose of the example is to
provide an example package, __init__.py, and a Qpy module.


Content-in-code instead of code-in-content.
-------------------------------------------

Most "template" systems are designed to embed program-like
value-substitution and control flow into what would otherwise be
static content.  Qpy (like Quixote's PTL templates) uses the opposite
pattern, embedding static content in what would otherwise be an
ordinary program.  This program-centric pattern is especially
attractive when content maintenance team is the same as the
programming team.


Notes for Quixote Users
-----------------------

The basic idea for Qpy comes from Quixote, as does most of the code of
the compiler.

The h8 class is like Quixote's htmltext class.

Unlike htmltext instances, h8 instances can be pickled.

Instead of htmlescape(), use h8.quote().

Instead of TemplateIO, form a list and use h8.from_list().

Most ptl files work without changes with Qpy.

Qpy doesn't use ihooks or any other kind of import hook.


Copyright
---------

Copyright (c) 2005 CNRI.