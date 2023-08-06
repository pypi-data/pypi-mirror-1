namespace NUMBYTES {
NUMBYTES_METH(PyObject *, static_tsize_from_tcode, NULL, TCODE_ARGS(args));
NUMBYTES_METH(PyObject *, _getitem, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, _setitem, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, get_base, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, get_bytes, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, get_contiguous, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, get_shape0, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, get_shape1, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, get_strides0, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, get_strides1, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, get_T, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, get_tcode, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, get_transposed, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, get_tsize, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, copy_to, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, fill_from_itr, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, reshape, NULL, TCODE_SELF(self));
NUMBYTES_METH(PyObject *, retype, NULL, TCODE_SELF(self));
MATH_METH1(__neg__)
MATH_METH1(__pos__)
MATH_METH1(__abs__)
MATH_METH1(__invert__)
MATH_METH1(cos)
MATH_METH1(sin)
MATH_METH1(tan)
MATH_METH1(acos)
MATH_METH1(asin)
MATH_METH1(atan)
MATH_METH1(cosh)
MATH_METH1(sinh)
MATH_METH1(tanh)
MATH_METH1(exp)
MATH_METH1(log)
MATH_METH1(log2)
MATH_METH1(log10)
MATH_METH1(sqrt)
MATH_METH1(ceil)
MATH_METH1(floor)
MATH_METH1(popcount)
MATH_METH1(round)
MATH_METH2(__add__)
MATH_METH2(__sub__)
MATH_METH2(__mul__)
MATH_METH2(__truediv__)
MATH_METH2(__mod__)
MATH_METH2(__pow__)
MATH_METH2(__lshift__)
MATH_METH2(__rshift__)
MATH_METH2(__and__)
MATH_METH2(__or__)
MATH_METH2(__xor__)
MATH_METH2(atan2)

struct _init {
_init() {
METHOD.add("tsize_from_tcode", static_tsize_from_tcode, METH_VARARGS | METH_STATIC);
METHOD.add("_getitem", _getitem, METH_VARARGS);
METHOD.add("_setitem", _setitem, METH_VARARGS);
GETSET.add("base", get_base);
GETSET.add("bytes", get_bytes);
GETSET.add("contiguous", get_contiguous);
GETSET.add("shape0", get_shape0);
GETSET.add("shape1", get_shape1);
GETSET.add("strides0", get_strides0);
GETSET.add("strides1", get_strides1);
GETSET.add("T", get_T);
GETSET.add("tcode", get_tcode);
GETSET.add("transposed", get_transposed);
GETSET.add("tsize", get_tsize);
METHOD.add("copy_to", copy_to, METH_VARARGS);
METHOD.add("fill_from_itr", fill_from_itr, METH_VARARGS);
METHOD.add("reshape", reshape, METH_VARARGS);
METHOD.add("retype", retype, METH_VARARGS);
METHOD.add("__neg__", __neg__, METH_VARARGS);
METHOD.add("__pos__", __pos__, METH_VARARGS);
METHOD.add("__abs__", __abs__, METH_VARARGS);
METHOD.add("__invert__", __invert__, METH_VARARGS);
METHOD.add("cos", cos, METH_VARARGS);
METHOD.add("sin", sin, METH_VARARGS);
METHOD.add("tan", tan, METH_VARARGS);
METHOD.add("acos", acos, METH_VARARGS);
METHOD.add("asin", asin, METH_VARARGS);
METHOD.add("atan", atan, METH_VARARGS);
METHOD.add("cosh", cosh, METH_VARARGS);
METHOD.add("sinh", sinh, METH_VARARGS);
METHOD.add("tanh", tanh, METH_VARARGS);
METHOD.add("exp", exp, METH_VARARGS);
METHOD.add("log", log, METH_VARARGS);
METHOD.add("log2", log2, METH_VARARGS);
METHOD.add("log10", log10, METH_VARARGS);
METHOD.add("sqrt", sqrt, METH_VARARGS);
METHOD.add("ceil", ceil, METH_VARARGS);
METHOD.add("floor", floor, METH_VARARGS);
METHOD.add("popcount", popcount, METH_VARARGS);
METHOD.add("round", round, METH_VARARGS);
METHOD.add("__add__", __add__, METH_VARARGS);
METHOD.add("__sub__", __sub__, METH_VARARGS);
METHOD.add("__mul__", __mul__, METH_VARARGS);
METHOD.add("__truediv__", __truediv__, METH_VARARGS);
METHOD.add("__mod__", __mod__, METH_VARARGS);
METHOD.add("__pow__", __pow__, METH_VARARGS);
METHOD.add("__lshift__", __lshift__, METH_VARARGS);
METHOD.add("__rshift__", __rshift__, METH_VARARGS);
METHOD.add("__and__", __and__, METH_VARARGS);
METHOD.add("__or__", __or__, METH_VARARGS);
METHOD.add("__xor__", __xor__, METH_VARARGS);
METHOD.add("atan2", atan2, METH_VARARGS);

}
} __init;
}