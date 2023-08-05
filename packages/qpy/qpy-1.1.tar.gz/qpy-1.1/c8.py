"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qpy/c8.py $
$Id: c8.py 27628 2005-10-27 18:55:19Z dbinger $
"""

def html_escape_string(s):
    """(basestring) -> basestring
    Replace characters '&', '<', '>', '"' with HTML entities.
    The type of the result is either str or unicode.
    """
    if not isinstance(s, basestring):
        raise TypeError, 'string object required'
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s

def stringify(obj):
    """(obj) -> basestring
    Return a string version of `obj`.  This is like str(), except
    that it tries to prevent turning str instances into unicode instances.
    The type of the result is either str or unicode.    
    """
    tp = type(obj)
    if issubclass(tp, basestring):
        return obj
    elif hasattr(tp, '__unicode__'):
        s = tp.__unicode__(obj)
        if not isinstance(s, basestring):
            raise TypeError, '__unicode__ did not return a string'
        return s
    elif hasattr(tp, '__str__'):
        s = tp.__str__(obj)
        if not isinstance(s, basestring):
            raise TypeError, '__str__ did not return a string'
        return s
    else:
        return str(obj)


class _quote_wrapper (object):
    """
    Not for outside code.  
    For values that are used as arguments to the % operator, this allows 
    str(value) and repr(value), if called as part of the formatting, to 
    produce quoted results.
    """
    __slots__ = ['value', 'quote']

    def __init__(self, value, quote):
        self.value = value
        self.quote = quote

    def __str__(self):
        return self.quote(self.value)

    def __repr__(self):
        return self.quote(`self.value`)

    def __getitem__(self, key):
        return _quote_wrap(self.value[key], self.quote)
        
def _quote_wrap(x, quote):
    """(x, quote:h8_quote|u8_quote) -> _quote_wrapper | x
    Not for outside code.
    Return a value v for which str(v) and repr(v) will produce quoted strings,
    or, if x is a dict, for which str(v[key]) and repr(v[key]) will produce
    quoted strings.
    """
    if isinstance(x, (int, long, float)):
        return x
    else:
        return _quote_wrapper(x, quote)  


class u8 (unicode):
    """
    This is a subclass of unicode for which the constructor defaults to utf-8 
    encoding and returns the empty instance when the argument is None or not given.
    
    u8.from_list(x) is the same as u8('').join(x).
    """
    __slots__ = []

    def __new__(klass, string='', encoding='utf-8', errors="strict"):
        if (string is None or
            (isinstance(string, basestring) and len(string) == 0)):
            if klass is u8:
                return _u8_empty
            if klass is h8:
                return _h8_empty
        if isinstance(string, unicode):
            return unicode.__new__(klass, string)
        return unicode.__new__(klass, string, encoding, errors)
  
    def __str__(self):
        """() -> str 
        Returns the utf-8 encoding.
        """
        return self.encode('utf-8')

    def __add__(self, other):
        """(other) -> instance of this class
        Like unicode.__add__, except that the argument is quoted and
        the result is an instance of this class.
        """                                
        return self.__class__(unicode.__add__(self, self.quote(other)))

    def __radd__(self, other):
        """(other) -> instance of this class
        Like unicode.__radd__, except that the argument is quoted and
        the result is an instance of this class.
        """                        
        return self.__class__(unicode.__add__(self.quote(other), self))

    def __mul__(self, other):
        """(other) -> instance of this class
        Like unicode.__mul__, except that the result is an instance of this class.
        """                        
        return self.__class__(unicode.__mul__(self, other))

    def __rmul__(self, other):
        """(other) -> instance of this class
        Like unicode.__rmul__, except that the result is an instance of this class.
        """                
        return self.__class__(unicode.__mul__(self, other))

    def __mod__(self, other):
        """(other) -> instance of this class
        Like unicode.__mod__, except that the inserted values are quoted.
        """        
        if isinstance(other, tuple):
            target = tuple(_quote_wrap(item, self.quote) for item in other)
        else:
            target = _quote_wrap(other, self.__class__.quote)
        return self.__class__(unicode.__mod__(self, target))
        
    def __rmod__(self, other):
        """(other) -> instance of this class
        Like unicode.__rmod__, except that the other value is quoted.
        """        
        return self.quote(other) % self

    def join(self, items):
        """(items:list) -> instance of this class
        Like unicode join, except that the items in the list are quoted first.
        """
        quote = self.__class__.quote
        return self.__class__(unicode.join(self, (quote(item) for item in items)))

    @classmethod
    def quote(klass, s):
        """(s:anything) -> instance of this class
        Return an instance of this class, based on s.
        """
        if isinstance(s, klass):
            return s
        if s is None:
            return klass()
        return klass(stringify(s))

_u8_empty = unicode.__new__(u8, '')
u8.from_list = _u8_empty.join


class h8 (u8):
    """
    This subclass of u8 is designated as needing no more html quoting.
    Some operations (the ones with __<op>__ overrides in the u8 class) that 
    combine this with non-h8 instances quote the non-h8 instances and produce 
    h8 instances.

    h8.from_list(x) is the same as h8('').join(x).
    """
    __slots__ = []

    @classmethod
    def quote(klass, s):
        """(s:anything) -> h8
        Return an h8 instance, based on s.  Escape HTML characters as needed.
        """
        if isinstance(s, klass):
            return s
        if s is None:
            return klass()
        return klass(html_escape_string(stringify(s)))

_h8_empty = unicode.__new__(h8, '')
h8.from_list = _h8_empty.join

__all__ = ['u8', 'h8', 'escape_string', 'stringify']

