"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qpy/test/utest_h8.py $
$Id: utest_h8.py 27625 2005-10-26 22:23:20Z dbinger $
"""
from sancho.utest import UTest
from qpy import u8, h8

class Test (UTest):

    def test_h8(self):
        u = h8()
        assert str(u) == ''
        assert u == h8('')
        assert u == u8('')
        assert u == ''
        assert h8('<') == '<'
        assert h8.quote('<') == '&lt;'
        u += 1
        u += None
        assert u == '1'
        assert h8('a%s') % '&' == 'a&amp;'
        assert h8('a%(a)s%(b)s') % dict(a='&', b=h8('<')) == 'a&amp;<'
        assert h8('a%s%s') % ('&', h8('<')) == 'a&amp;<'

    def test_a(self):
        s = h8('<') + '<'
        assert isinstance(s, h8) and s == '<&lt;'
        s = '<' + h8('<')
        assert isinstance(s, h8) and s == '&lt;<', '__radd__ not working.'
        s = h8('%s') % '<'
        assert isinstance(s, h8) and  s == '&lt;'
        s = h8('%s') % h8('<')
        assert isinstance(s, h8) and s == '<'
        s = h8('%(a)s') % dict(a='<')
        assert isinstance(s, h8) and s == '&lt;'
        # mod into str does not produce an h8.
        s = '%s' % h8('a')
        assert isinstance(s, unicode) and not isinstance(s, h8) and s == 'a'
        s = u'%s' % h8('a')
        assert isinstance(s, unicode) and isinstance(s, h8) and s == 'a'
        s = h8('a')
        s += '<'
        assert s == 'a&lt;'
        
    def test_quote_wrapper(self):
        assert h8("%0.2f") % 2 == '2.00'
        assert type(h8("%0.2f") % 2) is h8
        assert h8("%(a)s %(b)0.2f") % dict(a=u'<', b=2) == '&lt; 2.00'
        assert type(h8("%(a)s %(b)0.2f") % dict(a=u'a', b=2)) is h8
        assert h8("%(a)r %(b)0.2f") % dict(a=u'<', b=2) ==  "u'&lt;' 2.00"
        assert type(h8("%(a)r %(b)0.2f")) is h8        

if __name__ == '__main__':
    Test()
