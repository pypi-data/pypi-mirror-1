"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qpy/test/utest_compile.py $
$Id: utest_compile.py 26820 2005-05-19 19:49:46Z dbinger $
"""
from sancho.utest import UTest
from qpy.compile import translate_tokens, TemplateTransformer


class Test (UTest):

    def translation (self):
        src = ('def a [html] ():\n'
               '    "ok"\n')
        translated = translate_tokens(src)
        assert 'def a_h8(' in translated
        src = ('def a [plain] ():\n'
               '    "ok"\n')
        translated = translate_tokens(src)
        assert 'def a_u8(' in translated

    def transform(self):
        src = ('def a_h8 ():\n'
               '    "ok"\n')
        transformer = TemplateTransformer()
        result = transformer.parsesuite(src)

if __name__ == '__main__':
    Test()
