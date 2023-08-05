/*
$Id: c8.c 27630 2005-10-28 13:39:48Z dbinger $
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qpy/c8.c $
*/

#include "Python.h"
#include "structmember.h"
#include "unicodeobject.h"

#define DEFERRED_ADDRESS(ADDR) 0

typedef PyUnicodeObject u8_object;
typedef PyUnicodeObject h8_object;
typedef struct {
	PyObject_HEAD
	PyObject *value;
	PyObject *quote;
} _quote_wrapper_object;

static PyTypeObject u8_type;
static PyTypeObject h8_type;
static PyTypeObject _quote_wrapper_type;

#define is_u8_object(v) ((v)->ob_type == &u8_type)
#define is_h8_object(v) ((v)->ob_type == &h8_type)


static PyUnicodeObject *
_new_empty_unicode(PyTypeObject *type) 
{
    PyUnicodeObject *x = PyObject_New(PyUnicodeObject, type);
    if (x == NULL)
        return NULL;
    x->str = PyMem_NEW(Py_UNICODE, 1);
    if (x->str == NULL) {
        Py_DECREF(x);
        return NULL;
    }
    x->str[0] = 0;
    x->length = 0;
    x->hash = -1;
    x->defenc = NULL;
    return x;
}

static PyUnicodeObject *
_get_empty_instance(PyTypeObject *type) 
{
    static u8_object *u8_empty;
    static h8_object *h8_empty;
    if (type == &h8_type) {
        if (h8_empty == NULL) {
            h8_empty = (h8_object *)_new_empty_unicode(type);
            if (h8_empty == NULL) 
                return NULL;
        }
        Py_INCREF(h8_empty);
        return (PyUnicodeObject *)h8_empty;
    } else if (type == &u8_type) {
        if (u8_empty == NULL) {
            u8_empty = (u8_object *)_new_empty_unicode(type);
            if (u8_empty == NULL) 
                return NULL;
        }
        Py_INCREF(u8_empty);
        return (PyUnicodeObject *)u8_empty;
    }
    return NULL;
}

static PyObject *
_u8_new_from_unicode(PyTypeObject *type, PyObject *x) 
{
    assert (PyUnicode_Check(x));
    if (PyUnicode_GetSize(x) == 0) 
        return (PyObject *)_get_empty_instance(type);
    else {
        PyObject *args = PyTuple_New(1);
        if (args == NULL)
            return NULL;
        Py_INCREF(x);
        PyTuple_SET_ITEM(args, 0, x);
	    PyObject *result = PyUnicode_Type.tp_new(type, args, NULL);        
        Py_DECREF(args);
        return result;
    }
}

static PyObject *
_u8_new_from_object(PyTypeObject *type, PyObject *x, char *errors) 
{
    if (PyUnicode_Check(x)) 
        return _u8_new_from_unicode(type, x);

    /* Decode a new instance of type from x using utf8. */
    static PyObject *utf8_encoding = NULL;
    if (utf8_encoding == NULL) {
        utf8_encoding = PyString_InternFromString("utf-8");
        if (utf8_encoding == NULL) {
            return NULL;
        }
    }
	PyObject *newargs;
    if (errors == NULL) 
	    newargs = PyTuple_New(2);
	else 
	    newargs = PyTuple_New(3);	   
    if (newargs == NULL) 
       return NULL;
    Py_INCREF(x);
    PyTuple_SET_ITEM(newargs, 0, x);
    Py_INCREF(utf8_encoding);
	PyTuple_SET_ITEM(newargs, 1, utf8_encoding); 
	if (errors != NULL) 
   	    PyTuple_SET_ITEM(newargs, 2, PyString_FromString(errors));
	PyObject *result = PyUnicode_Type.tp_new(type, newargs, NULL);
	Py_DECREF(newargs); 
	return result;
}

static PyObject *
u8_new(PyTypeObject *type, PyObject *args, PyObject *kw)
{
	PyObject *x = NULL;
	static char *kwlist[] = {"string", "encoding", "errors", 0};
	char *encoding = NULL;
	char *errors = NULL;   
    /* Parse args using the same format as unicode_new. */
    if (!PyArg_ParseTupleAndKeywords(
        args, kw, "|Oss:u8", kwlist, &x, &encoding, &errors)) 
        return NULL;

    /* Return an empty if the argument is missing or None or empty. */
	if ((x == NULL) || 
	    (x == Py_None) || 
	    (PyString_Check(x) && (PyString_Size(x) == 0))) 
	    return (PyObject *)_get_empty_instance(type);

    /* If the encoding does not need to be changed, do the normal thing. */
    if (PyUnicode_Check(x)) 
        return _u8_new_from_unicode(type, x);

    /* If the encoding is given, let unicode deal with it. */
	if (encoding != NULL)   
	    return PyUnicode_Type.tp_new(type, args, kw);	   

    return _u8_new_from_object(type, x, errors);
}

static PyObject *
stringify(PyObject *obj) 
{
	if (PyUnicode_Check(obj) || PyString_Check(obj)) {
		Py_INCREF(obj);
		return obj;
	}
	static PyObject *unicodestr = NULL;
	if (unicodestr == NULL) {
		unicodestr = PyString_InternFromString("__unicode__");
		if (unicodestr == NULL)
			return NULL;
	}
	PyObject *result;
	PyObject *func = PyObject_GetAttr(obj, unicodestr);
	if (func != NULL) {
		result = PyEval_CallObject(func, (PyObject *)NULL);
		Py_DECREF(func);
	} else {
		PyErr_Clear();
		if (obj->ob_type->tp_str != NULL)
			result = (*obj->ob_type->tp_str)(obj);
		else
			result = PyObject_Repr(obj);
	}
	if (result == NULL)
        return NULL;
	if (!(PyUnicode_Check(result) || PyString_Check(result))) {
		Py_DECREF(result);
	    PyErr_SetString(PyExc_TypeError, "string object expected");
	    return NULL;		
	}
	return result;
}

static PyObject *
_escape_str(PyObject *obj) 
{
	char *s;
	PyObject *newobj;
	size_t i, j, extra_space, size, new_size;
	assert (PyString_Check(obj));
	size = PyString_GET_SIZE(obj);
	extra_space = 0;
	for (i=0; i < size; i++) {
		switch (PyString_AS_STRING(obj)[i]) {
		case '&':
			extra_space += 4;
			break;
		case '<':
		case '>':
			extra_space += 3;
			break;
		case '"':
			extra_space += 5;
			break;
		}
	}
	if (extra_space == 0) {
		Py_INCREF(obj);
		return (PyObject *)obj;
	}
	new_size = size + extra_space;
	newobj = PyString_FromStringAndSize(NULL, new_size);
	if (newobj == NULL)
		return NULL;
	s = PyString_AS_STRING(newobj);
	for (i=0, j=0; i < size; i++) {
		switch (PyString_AS_STRING(obj)[i]) {
		case '&':
			s[j++] = '&';
			s[j++] = 'a';
			s[j++] = 'm';
			s[j++] = 'p';
			s[j++] = ';';
			break;
		case '<':
			s[j++] = '&';
			s[j++] = 'l';
			s[j++] = 't';
			s[j++] = ';';
			break;
		case '>':
			s[j++] = '&';
			s[j++] = 'g';
			s[j++] = 't';
			s[j++] = ';';
			break;
		case '"':
			s[j++] = '&';
			s[j++] = 'q';
			s[j++] = 'u';
			s[j++] = 'o';
			s[j++] = 't';
			s[j++] = ';';
			break;
		default:
			s[j++] = PyString_AS_STRING(obj)[i];
			break;
		}
	}
	assert (j == new_size);
	return (PyObject *)newobj;
}

static PyObject *
_escape_unicode(PyObject *obj) 
{
	Py_UNICODE *u;
	PyObject *newobj;
	size_t i, j, extra_space, size, new_size;
	assert (PyUnicode_Check(obj));
	size = PyUnicode_GET_SIZE(obj);
	extra_space = 0;
	for (i=0; i < size; i++) {
		switch (PyUnicode_AS_UNICODE(obj)[i]) {
		case '&':
			extra_space += 4;
			break;
		case '<':
		case '>':
			extra_space += 3;
			break;
		case '"':
			extra_space += 5;
			break;
		}
	}
	if (extra_space == 0) {
		Py_INCREF(obj);
		return (PyObject *)obj;
	}
	new_size = size + extra_space;
	newobj = PyUnicode_FromUnicode(NULL, new_size);
	if (newobj == NULL) 
		return NULL;

	u = PyUnicode_AS_UNICODE(newobj);
	for (i=0, j=0; i < size; i++) {
		switch (PyUnicode_AS_UNICODE(obj)[i]) {
		case '&':
			u[j++] = '&';
			u[j++] = 'a';
			u[j++] = 'm';
			u[j++] = 'p';
			u[j++] = ';';
			break;
		case '<':
			u[j++] = '&';
			u[j++] = 'l';
			u[j++] = 't';
			u[j++] = ';';
			break;
		case '>':
			u[j++] = '&';
			u[j++] = 'g';
			u[j++] = 't';
			u[j++] = ';';
			break;
		case '"':
			u[j++] = '&';
			u[j++] = 'q';
			u[j++] = 'u';
			u[j++] = 'o';
			u[j++] = 't';
			u[j++] = ';';
			break;
		default:
			u[j++] = PyUnicode_AS_UNICODE(obj)[i];
			break;
		}
	}
	assert (j == new_size);
	return (PyObject *)newobj;
}

static PyObject *
_html_escape_string(PyObject *obj) 
{
	if (PyString_Check(obj)) 
		return _escape_str(obj);
	else if (PyUnicode_Check(obj)) 
		return _escape_unicode(obj);
	else {
	    PyErr_SetString(PyExc_TypeError, "string object required");
	    return NULL;			    
	}
}

static PyObject *
_quote_wrap(PyObject *value, PyObject *quote) 
{
	_quote_wrapper_object *self;
	if (PyInt_Check(value) ||
	    PyFloat_Check(value) ||
	    PyLong_Check(value)) {
		/* no need for wrapper */
		Py_INCREF(value);
		return value;
	}
	self = PyObject_New(_quote_wrapper_object, &_quote_wrapper_type);
	if (self == NULL)
		return NULL;
	Py_INCREF(value);
	self->value = value;
	Py_INCREF(quote);	
	self->quote = quote;
	return (PyObject *)self;
}

static void
_quote_wrapper_dealloc(_quote_wrapper_object *self) 
{
	Py_DECREF(self->value);
	Py_DECREF(self->quote);	
	PyObject_Del(self);
}

static PyObject *
_quote_wrapper_repr(_quote_wrapper_object *self) 
{
	PyObject *s = PyObject_Repr(self->value);
	if (s == NULL)
		return NULL;
	PyObject *qs = PyObject_CallFunction(self->quote, "(O)", s);
	Py_DECREF(s);
	return qs;
}

static PyObject *
_quote_wrapper_str(_quote_wrapper_object *self) 
{
	PyObject *qs = PyObject_CallFunction(self->quote, "(O)", self->value);
	return qs;
}

static PyObject *
_quote_wrapper_subscript(_quote_wrapper_object *self, PyObject *key) 
{
	PyObject *v = PyObject_GetItem(self->value, key);
	if (v == NULL) 
		return NULL;
	PyObject *w = _quote_wrap(v, self->quote); 
	Py_DECREF(v);
	return w;
}

static PyObject *
u8_quote(PyTypeObject *class, PyObject *x) 
{
    if is_u8_object(x) {
        Py_INCREF(x);
        return x;
    }
    if (x == Py_None) 
        return (PyObject *)_get_empty_instance(class);
    if (PyUnicode_Check(x)) 
        return _u8_new_from_unicode(class, x);
    if (PyString_Check(x)) 
        return _u8_new_from_object(class, x, NULL);
    PyObject *s = stringify(x);
    if (s == NULL) 
        return NULL;
    PyObject *result = _u8_new_from_object(class, s, NULL);
    Py_DECREF(s);
    return result;
}

static PyObject *
h8_quote(PyTypeObject *class, PyObject *x) 
{
    if is_h8_object(x) {
        Py_INCREF(x);
        return x;
    }
    if (x == Py_None) 
        return (PyObject *)_get_empty_instance(class);
    PyObject *s = stringify(x);
    if (s == NULL) 
        return NULL;
    PyObject *escaped = _html_escape_string(s);
    Py_DECREF(s);
    if (escaped == NULL) 
        return NULL;
    PyObject *result = _u8_new_from_object(class, escaped, NULL);
    Py_DECREF(escaped);
    return result;
}

static PyObject *
_quoted_list(PyObject *quote, PyObject* args) 
{
    PyObject *quoted_args = PySequence_List(args);
    if (quoted_args == NULL) 
    	return NULL;
    int i;
    int n = PyList_Size(quoted_args);
    for (i=0; i < n; i++) {
    	PyObject *value = PyList_GET_ITEM(quoted_args, i);
    	if (value == NULL) 
    		goto error;
    	PyObject *qvalue = PyObject_CallFunction(quote, "(O)", (PyObject *)value);
        if (qvalue == NULL) 
            goto error;
    	if (PyList_SetItem(quoted_args, i, qvalue) < 0) 
    		goto error;
    }    
    return quoted_args;

    error:  
        Py_DECREF(quoted_args);
        return NULL;
}

static PyObject *
_lookup_quote_method(PyObject *self) 
{
    static PyObject *quote_method_name = NULL;
    if (quote_method_name == NULL) {
        quote_method_name = PyString_InternFromString("quote");
        if (quote_method_name == NULL)
            return NULL;
    }   
    return PyObject_GetAttr(self, quote_method_name);
}

static PyObject *
u8_join(PyObject *self, PyObject *args) 
{
    PyObject *quote = _lookup_quote_method(self);
    if (quote == NULL) 
        return NULL;
    PyObject *quoted_args = _quoted_list(quote, args);
    Py_DECREF(quote);
    if (quoted_args == NULL) 
    	return NULL;
    PyObject *unicode_result = PyUnicode_Join(self, quoted_args);
    Py_DECREF(quoted_args);
    if (unicode_result == NULL)
        return NULL;  
    PyObject *result = _u8_new_from_unicode(self->ob_type, unicode_result);
    Py_DECREF(unicode_result);
    return result;
}

static PyObject *
u8_from_list(PyTypeObject *class, PyObject *args) 
{
    PyObject *quote = _lookup_quote_method((PyObject *)class);
    if (quote == NULL) 
        return NULL;
    PyObject *quoted_args = _quoted_list(quote, args);
    Py_DECREF(quote);
    if (quoted_args == NULL) 
    	return NULL;
    PyObject *empty = (PyObject *)_get_empty_instance(class);
    if (empty == NULL) {
        Py_DECREF(quoted_args);
        return NULL;
    }           
    PyObject *unicode_result = PyUnicode_Join(empty, quoted_args);
    Py_DECREF(empty);
    Py_DECREF(quoted_args);
    if (unicode_result == NULL)
        return NULL;    
    PyObject *result = _u8_new_from_unicode(class, unicode_result);
    Py_DECREF(unicode_result);
    return result;
}

static PyObject *
u8_str(PyObject *self) 
{
  return PyUnicode_AsUTF8String(self);
}

static PyObject *
u8_add(PyObject *self, PyObject *other) 
{
    PyObject *quoted;
    PyObject *unicode_result;
    PyObject *result;
    if (is_h8_object(self) || (is_u8_object(self) && !is_h8_object(other))) {
        quoted = PyObject_CallMethod(self, "quote", "(O)", other);          
        if (quoted == NULL) 
            return NULL;
        unicode_result = PyUnicode_Concat(self, quoted);
        Py_DECREF(quoted);          
        if (unicode_result == NULL) 
            return NULL;    
        result = _u8_new_from_unicode(self->ob_type, unicode_result);
        Py_DECREF(unicode_result);
        return result;
    } else if (is_h8_object(other) || is_u8_object(other)) {
        quoted = PyObject_CallMethod(other, "quote", "(O)", self);          
        if (quoted == NULL) 
            return NULL;
        unicode_result = PyUnicode_Concat(quoted, other);
        Py_DECREF(quoted);  
        if (unicode_result == NULL) 
            return NULL;
        result = _u8_new_from_unicode(other->ob_type, unicode_result);            
        Py_DECREF(unicode_result);
        return result;                                        
    } else {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }
}

static PyObject *
_format_arg_wrap(PyObject *arg, PyObject *quote) 
{
	PyObject *wrapped;
	if (PyTuple_Check(arg)) {
		long i;
		long n = PyTuple_GET_SIZE(arg);
		wrapped = PyTuple_New(n);
		for (i=0; i < n; i++) {
			PyObject *v = PyTuple_GET_ITEM(arg, i);
			v = _quote_wrap(v, quote);
			if (v == NULL) {
				Py_DECREF(wrapped);
				return NULL;
			}
			PyTuple_SetItem(wrapped, i, v);
		}
	}
	else {
		wrapped = _quote_wrap(arg, quote);
		if (wrapped == NULL)
			return NULL;
	}
	return wrapped;
}

static PyObject *
u8_format(PyObject *self, PyObject *other) 
{
    PyObject *quote;   
    PyObject *wrapped;       
    PyObject *unicode_result;
    PyObject *result;
    if (is_h8_object(self) || (is_u8_object(self) && !is_h8_object(other))) {
        quote = _lookup_quote_method(self);
        if (quote == NULL) 
            return NULL;
        wrapped = _format_arg_wrap(other, quote);
        Py_DECREF(quote);
        if (wrapped == NULL) 
            return NULL;
	    unicode_result = PyUnicode_Format(self, wrapped);                    
	    Py_DECREF(wrapped);
        if (unicode_result == NULL) 
            return NULL;
        result = _u8_new_from_unicode(self->ob_type, unicode_result);                    
        Py_DECREF(unicode_result);
        return result;                    
    } else if (is_h8_object(other) || is_u8_object(other)) {
        quote = _lookup_quote_method(other);
        if (quote == NULL) 
            return NULL;        
        wrapped = _format_arg_wrap(self, quote);
        Py_DECREF(quote);
        if (wrapped == NULL) 
            return NULL;
	    unicode_result = PyUnicode_Format(other, wrapped);
	    Py_DECREF(wrapped);
        if (unicode_result == NULL) 
            return NULL;
        result = _u8_new_from_unicode(other->ob_type, unicode_result);
        Py_DECREF(unicode_result);
        return result;                    
    } else {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;    
    }           
}

static PyObject *
u8_repeat(PyObject *self, int other) 
{
    PyObject *unicode_result;   
    PyObject *result;
    unicode_result = PyUnicode_Type.tp_as_sequence->sq_repeat(self, other);
    if (unicode_result == NULL)
        return NULL;
    result = _u8_new_from_unicode(self->ob_type, unicode_result);      
    Py_DECREF(unicode_result);
    return result;
}

static PyNumberMethods u8_as_number = {
    (binaryfunc)u8_add, /* nb_add       */
	0,	/* nb_subtract  */
	0,	/* nb_multiply  */
	0,	/* nb_divide    */
	(binaryfunc) u8_format,	/* nb_remainder */
};

static PySequenceMethods u8_as_sequence = {
    0, /* sq_length */
    (binaryfunc) u8_add,    /* sq_concat */ 
    (intargfunc) u8_repeat, /* sq_repeat */
};

PyDoc_STRVAR(u8_quote_doc,
    "(s:anything) -> instance of this class\n"
    "Return an instance of this class, based on s.");
    
PyDoc_STRVAR(u8_join_doc,
    "(items:list) -> instance of this class\n"
    "Like unicode join, except that the items in the list are quoted first.");
    
PyDoc_STRVAR(u8_from_list_doc,
    "(items:list) -> instance of this class\n"
    "This is the same as the empty instance's join() method.");    

static PyMethodDef u8_methods[] = {
	{"quote", (PyCFunction)u8_quote,
		METH_CLASS, u8_quote_doc},
	{"join", (PyCFunction)u8_join,
		METH_O, u8_join_doc},
	{"from_list", (PyCFunction)u8_from_list,
		METH_CLASS, u8_from_list_doc},
	{NULL,	NULL},
};

PyDoc_STRVAR(u8_doc,
    "This is a subclass of unicode for which the constructor defaults to utf-8\n"
    "encoding and returns the empty instance when the argument is None or not given.\n"
    "u8.from_list(x) is the same as u8('').join(x).");

static PyTypeObject u8_type = {
	PyObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type))
	0,
	"u8",
	sizeof(u8_object),
	0,
	0,	/* tp_dealloc */
	0,	/* tp_print */
	0,	/* tp_getattr */
	0,	/* tp_setattr */
	0,	/* tp_compare */
	0,	/* tp_repr */
	&u8_as_number,		/* tp_as_number */
	&u8_as_sequence,	/* tp_as_sequence */
	0,	/* tp_as_mapping */
	0,	/* tp_hash */
	0,	/* tp_call */
	u8_str,	/* tp_str */
	0,	/* tp_getattro */
	0,	/* tp_setattro */
	0,	/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES, /* tp_flags */
	u8_doc,	/* tp_doc */
	0,	/* tp_traverse */
	0,	/* tp_clear */
	0,	/* tp_richcompare */
	0,	/* tp_weaklistoffset */
	0,	/* tp_iter */
	0,	/* tp_iternext */
	u8_methods,	/* tp_methods */
	0,	/* tp_members */
	0,	/* tp_getset */
	DEFERRED_ADDRESS(&PyUnicode_Type),  /* tp_base */
	0,	/* tp_dict */
	0,	/* tp_descr_get */
	0,	/* tp_descr_set */
	0,	/* tp_dictoffset */
	0,  /* tp_init */
	0,	/* tp_alloc */
	(newfunc)u8_new,	/* tp_new */
};

PyDoc_STRVAR(h8_quote_doc,
    "(s:anything) -> h8\n"
    "Return an h8 instance, based on s.  Escape HTML characters as needed.");
    
static PyMethodDef h8_methods[] = {
	{"quote", (PyCFunction)h8_quote,
		METH_CLASS, h8_quote_doc},
	{NULL,	NULL},
};

PyDoc_STRVAR(h8_doc,
    "This subclass of u8 is designated as needing no more html quoting.\n"
    "Some operations (the ones with __<op>__ overrides in the u8 class) that\n"
    "combine this with non-h8 instances quote the non-h8 instances and produce\n"
    "h8 instances.\n\n"
    "h8.from_list(x) is the same as h8('').join(x).");

static PyTypeObject h8_type = {
	PyObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type))
	0,
	"h8",
	sizeof(h8_object),
	0,
	0,	/* tp_dealloc */
	0,	/* tp_print */
	0,	/* tp_getattr */
	0,	/* tp_setattr */
	0,	/* tp_compare */
	0,	/* tp_repr */
    0,	/* tp_as_number */
	0,	/* tp_as_sequence */
	0,	/* tp_as_mapping */
	0,	/* tp_hash */
	0,	/* tp_call */
	0,	/* tp_str */
	0,	/* tp_getattro */
	0,	/* tp_setattro */
	0,	/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES, /* tp_flags */
	h8_doc, /* tp_doc */
	0,	/* tp_traverse */
	0,	/* tp_clear */
	0,	/* tp_richcompare */
	0,	/* tp_weaklistoffset */
	0,	/* tp_iter */
	0,	/* tp_iternext */
	h8_methods, /* tp_methods */
	0,	/* tp_members */
	0,	/* tp_getset */
	DEFERRED_ADDRESS(&PyUnicode_Type),	/* tp_base */
	0,	/* tp_dict */
	0,	/* tp_descr_get */
	0,	/* tp_descr_set */
	0,	/* tp_dictoffset */
	0,  /* tp_init */
	0,	/* tp_alloc */
	0,	/* tp_new */
};

static PyMappingMethods _quote_wrapper_as_mapping = {
	0, /* mp_length */
	(binaryfunc)_quote_wrapper_subscript, /* mp_subscript */
};

static PyTypeObject _quote_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,	/*ob_size*/
	"QuoteWrapper",	/*tp_name*/
	sizeof(_quote_wrapper_object),	/*tp_basicsize*/
	0,	/*tp_itemsize*/
	(destructor)_quote_wrapper_dealloc, /*tp_dealloc*/
	0,	/*tp_print*/
	0,	/*tp_getattr*/
	0,	/*tp_setattr*/
	0,	/*tp_compare*/
	(unaryfunc)_quote_wrapper_repr, /*tp_repr*/
	0,  /*tp_as_number*/
	0,	/*tp_as_sequence*/
	&_quote_wrapper_as_mapping, /*tp_as_mapping*/
	0,	/*tp_hash*/
	0,	/*tp_call*/
	(unaryfunc)_quote_wrapper_str,  /*tp_str*/
};

static PyObject *
py_html_escape_string(PyObject *self, PyObject *obj) 
{
	return _html_escape_string(obj);
}

static PyObject *
py_stringify(PyObject *self, PyObject *obj) 
{
	return stringify(obj);
}

PyDoc_STRVAR(stringify_doc,
    "(obj) -> basestring\n"
    "Return a string version of `obj`.  This is like str(), except\n"
    "that it tries to prevent turning str instances into unicode instances.\n"
    "The type of the result is either str or unicode.stringify.");

PyDoc_STRVAR(html_escape_string_doc,
	 "(basestring) -> basestring\n"
     "Replace characters '&', '<', '>', '\"' with HTML entities.\n"
     "The type of the result is either str or unicode.html_escape_string.");

static PyMethodDef c8_methods[] = {
    {"stringify", (PyCFunction)py_stringify, 
        METH_O, stringify_doc},
    {"html_escape_string", (PyCFunction)py_html_escape_string, 
        METH_O, html_escape_string_doc},
    {NULL, NULL}
};

PyDoc_STRVAR(c8_doc, "This is the C-implementation of the qpy.c8 module.");

PyMODINIT_FUNC
initc8(void) 
{
	PyObject *m;

	u8_type.tp_base = &PyUnicode_Type;
	if (PyType_Ready(&u8_type) < 0)
		return;
	Py_INCREF(&u8_type);		

	h8_type.tp_base = &u8_type;
	if (PyType_Ready(&h8_type) < 0)
		return;
	Py_INCREF(&h8_type);

	if (PyType_Ready(&_quote_wrapper_type) < 0)
		return;
	Py_INCREF(&_quote_wrapper_type);		
	
	m = Py_InitModule3("c8", c8_methods, c8_doc);
	if (m == NULL)
		return;

	if (PyModule_AddObject(m, "u8", (PyObject *)&u8_type) < 0)
		return;
	if (PyModule_AddObject(m, "h8", (PyObject *)&h8_type) < 0)
		return;		
}
