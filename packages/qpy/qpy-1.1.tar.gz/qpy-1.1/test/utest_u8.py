"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qpy/test/utest_u8.py $
$Id: utest_u8.py 27625 2005-10-26 22:23:20Z dbinger $
"""
from sancho.utest import UTest, raises
from qpy import u8, stringify, html_escape_string

class Test (UTest):

    def test_u8(self):
        u = u8()
        assert str(u) == ''
        assert u == u8('')
        assert u == ''
        assert u == u8(u'')
        assert u == u8.from_list(['', u'', None])
        assert u8('<') == '<'
        u = u8('\xc3\xbc')
        assert u == u'\xfc'
        u = u8('ok')
        x = u.join(['a', u8('a')])
        assert isinstance(x, u8)
        assert x == u'aoka'
        assert 2 * u == 'okok'
        assert u * 2 == 'okok'
        
    def test_utils(self):
        raises(TypeError, stringify, 1)
        class A(object):
            def __unicode__(self):
                return 1
        raises(TypeError, stringify, A())
        A.__unicode__ = lambda x: u''
        raises(TypeError, stringify, A())        
        class B(object):
            def __str__(self):
                return 1
        raises(TypeError, stringify, B())       
        assert stringify(1) == '1'
        raises(TypeError, html_escape_string, 1)
        
    def test_quote_wrapper(self):
        assert u8("%0.2f") % 2 == '2.00'
        assert type(u8("%0.2f") % 2) is u8
        assert u8("%(a)s %(b)0.2f") % dict(a=u'a', b=2) == 'a 2.00'
        assert type(u8("%(a)s %(b)0.2f") % dict(a=u'a', b=2)) is u8
        assert u8("%(a)r %(b)0.2f") % dict(a=u'<', b=2) ==  "u'<' 2.00"
        assert type(u8("%(a)r %(b)0.2f")) is u8

        
        


if __name__ == '__main__':
    Test()
