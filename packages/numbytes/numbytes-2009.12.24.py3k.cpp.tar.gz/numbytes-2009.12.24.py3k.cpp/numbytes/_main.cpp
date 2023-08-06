
namespace base {
#ifndef PYBASE_HPP
#define PYBASE_HPP
#include "Python.h" // must be included first
#include "structmember.h" // python struct
#include "png.h" // png
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <vector>
  using namespace std;
  typedef long long i64; typedef ssize_t ssz; typedef unsigned char uch; typedef unsigned int uint; typedef unsigned long long u64; const int ERROR = -1;



  namespace MY {
#define CAST(TT, aa) ((TT)aa)
#define CLOSURE(rtype, name, args, body) struct _##name { static rtype name args body; }; rtype (*name) args = &_##name::name;
#define DIVCEIL(aa, bb) (((aa) + (bb) - 1) / (bb))
#define DIVROUND(aa, bb) ((aa + ((bb) / 2)) / (bb))
#define MAX(aa, bb) ((aa) > (bb) ? (aa) : (bb))
#define MIN(aa, bb) ((aa) < (bb) ? (aa) : (bb))
#define SIGN(aa) ((aa) < 0 ? -1 : (aa) > 0 ? 1 : 0)
#define SWAP(aa, bb, cc) cc = aa; aa = bb; bb = cc;
#define VSNPRINTF(ss, ll, fmt) char ss[ll]; va_list args; va_start(args, fmt); vsnprintf(ss, ll, fmt, args); va_end(args);
    const char *sformat(const char *fmt, ...) { static VSNPRINTF(ss, 1024, fmt); return ss; }

    //// math
    const double INVLOG2 = 1.0 / log(2.0);
    u64 popcount64(u64 aa) {
      aa -= ((aa >> 1) & 0x5555555555555555LLU); // count 2 bit
      aa = (((aa >> 2) & 0x3333333333333333LLU) + (aa & 0x3333333333333333LLU)); // count 4 bit
      aa = (((aa >> 4) + aa) & 0x0f0f0f0f0f0f0f0fLLU); // count 8 bit
      aa += (aa >> 8); aa += (aa >> 16); aa += (aa >> 32); return aa & 0x7f; // count 16/32/64 bit
    }
    u64 log64(u64 aa) { aa |= (aa >> 1); aa |= (aa >> 2); aa |= (aa >> 4); aa |= (aa >> 16); aa |= (aa >> 32); return popcount64(aa) - 1; }
    double roundeven(double aa) {
      if (aa < 0) return -roundeven(-aa);
      double bb = floor(aa + 0.5);
      if (bb == aa + 0.5) return floor(bb * 0.5) * 2; // round even
      return bb;
    }
  }



  namespace PY {
    PyObject *err(PyObject *err, const char *fmt = "", ...) { VSNPRINTF(ss, 1024, fmt); PyErr_SetString(err, ss); return err; }
    void print(const char *fmt, ...) { VSNPRINTF(ss, 1024, fmt); PyFile_WriteString(ss, PySys_GetObject("stdout")); }
    const char *tpname(PyObject *aa) { return Py_TYPE(aa) ->tp_name; }
    const char *tostr(PyObject *aa) {
      static char ss[1024]; PyObject *bb = PyObject_Str(aa), *cc = NULL; if (not bb) throw ERROR;
      try {
        cc = PyUnicode_AsEncodedString(PyObject_Str(bb), "latin", NULL); if (not cc) throw ERROR;
        strncpy(ss, PyBytes_AS_STRING(cc), sizeof(ss)); ss[sizeof(ss) - 1] = 0;
        Py_XDECREF(bb); Py_XDECREF(cc); return ss;
      } catch (...) { Py_XDECREF(bb); Py_XDECREF(cc); throw; }
    }
#ifndef PYMETH_SIZE
#define PYMETH_SIZE 256
#endif
#define PYMETH_ADD(fnc, flags) if (ii + 1 >= PYMETH_SIZE) throw PY::err(PyExc_MemoryError, "too many methods (> %i) in module", PYMETH_SIZE - 1); METHOD[ii].ml_name = (char *)#fnc; METHOD[ii].ml_meth = (PyCFunction)py_##fnc; METHOD[ii].ml_flags = flags; METHOD[ii].ml_doc = NULL; ii ++;
#define PYMETH_ADD_NOARGS
#define _PYMETH_ADD_NOARGS(fnc) PYMETH_ADD(fnc, METH_NOARGS)
#define PYMETH_ADD_NOARGS_STATIC
#define _PYMETH_ADD_NOARGS_STATIC(fnc) PYMETH_ADD(fnc, METH_NOARGS | METH_STATIC)
#define PYMETH_ADD_O
#define _PYMETH_ADD_O(fnc) PYMETH_ADD(fnc, METH_O)
#define PYMETH_ADD_O_STATIC
#define _PYMETH_ADD_O_STATIC(fnc) PYMETH_ADD(fnc, METH_O | METH_STATIC)
#define PYMETH_ADD_VARARGS
#define _PYMETH_ADD_VARARGS(fnc) PYMETH_ADD(fnc, METH_VARARGS)
#define PYMETH_ADD_VARARGS_STATIC
#define _PYMETH_ADD_VARARGS_STATIC(fnc) PYMETH_ADD(fnc, METH_VARARGS | METH_STATIC)
  }



#ifndef PYTYPE
#define PYTYPE true
#endif
#if PYTYPE
  namespace TYPE {
    PyMethodDef METHOD[PYMETH_SIZE] = {{NULL}}; void METHOD_init() {}; void init() {}
    PyTypeObject TYPE = {
      PyVarObject_HEAD_INIT(NULL, 0)
      "mytype", // tp_name
      sizeof(PyObject), // tp_basicsize
      NULL, // tp_itemsize
      NULL, // tp_dealloc
      NULL, // tp_print
      NULL, // tp_getattr
      NULL, // tp_setattr
      NULL, // tp_reserved
      NULL, // tp_repr
      NULL, // tp_as_number
      NULL, // tp_as_sequence
      NULL, // tp_as_mapping
      NULL, // tp_hash
      NULL, // tp_call
      NULL, // tp_str
      NULL, // tp_getattro
      NULL, // tp_setattro
      NULL, // tp_as_buffer
      Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, // tp_flags
      NULL, // tp_doc
      NULL, // tp_traverse
      NULL, // tp_clear
      NULL, // tp_richcompare
      NULL, // tp_weaklistoffset
      NULL, // tp_iter
      NULL, // tp_iternext
      METHOD, // tp_methods
      NULL, // tp_members
      NULL, // tp_getset
      NULL, // tp_base
      NULL, // tp_dict
      NULL, // tp_descr_get
      NULL, // tp_descr_set
      NULL, // tp_dictoffset
      NULL, // tp_init
      NULL, // tp_alloc
      NULL, // tp_new
      NULL, // tp_free
      NULL, // tp_is_gc
      NULL, // tp_bases
      NULL, // tp_mro
      NULL, // tp_cache
      NULL, // tp_subclasses
      NULL, // tp_weaklist
      NULL, // tp_del
      NULL, // tp_version_tag
    };
  }
#endif



  namespace MODULE {
    PyMethodDef METHOD[PYMETH_SIZE] = {{NULL}}; void METHOD_init() {};
    struct PyModuleDef MODULE = {
      PyModuleDef_HEAD_INIT, // m_base
      "mymodule", // m_name
      NULL, // m_doc
      -1, // m_size
      METHOD, // m_methods
      NULL, // m_reload
      NULL, // m_traverse
      NULL, // m_clear
      NULL, // m_free
    };
#if PYTYPE
#define PyInit_module(name, body)                                       \
    extern "C" { PyObject *PyInit_##name() { try {                      \
          MODULE.m_name = #name; METHOD_init(); body; PyObject *mm = PyModule_Create(&MODULE); if (not mm) throw ERROR; \
          TYPE::TYPE.tp_name = #name; TYPE::METHOD_init(); TYPE::init(); if (PyType_Ready(&TYPE::TYPE) == ERROR) throw ERROR; Py_INCREF(&TYPE::TYPE); PyModule_AddObject(mm, TYPE::TYPE.tp_name, (PyObject *)&TYPE::TYPE); \
          return mm; } catch (...) { return NULL; } } }
#else
#define PyInit_module(name, body)                                       \
    extern "C" { PyObject *PyInit_##name() { try {                      \
          MODULE.m_name = #name; METHOD_init(); body; PyObject *mm = PyModule_Create(&MODULE); if (not mm) throw ERROR; \
          return mm; } catch (...) { return NULL; } } }
#endif
    PyInit_module(base, {});
  }
#endif
}







namespace _module {
#include "base.hpp"
  namespace MODULE {
    PYMETH_ADD_O PyObject *py_is_itr(PyObject *self, PyObject *aa) { return PyLong_FromLong(    PyIter_Check(aa)); }
    PYMETH_ADD_O PyObject *py_is_map(PyObject *self, PyObject *aa) { return PyLong_FromLong( PyMapping_Check(aa)); }
    PYMETH_ADD_O PyObject *py_is_num(PyObject *self, PyObject *aa) { return PyLong_FromLong(  PyNumber_Check(aa)); }
    PYMETH_ADD_O PyObject *py_is_seq(PyObject *self, PyObject *aa) { return PyLong_FromLong(PySequence_Check(aa)); }
    PYMETH_ADD_O PyObject *py_refcnt(PyObject *self, PyObject *aa) { return PyLong_FromSsize_t(Py_REFCNT(aa)); }
    PyInit_module(_module, {});
  }
}







namespace _numbytes {
#include "base.hpp"
  namespace TYPE {
    //// typedef
    int is_type(PyTypeObject *type) { return type == &TYPE or PyType_IsSubtype(type, &TYPE); }
    PyTypeObject *check_type(PyTypeObject *type) { if (not is_type(type)) throw PY::err(PyExc_TypeError, "not numbytes type <%s>", type ->tp_name); return type; }
    typedef char CC; typedef i64 II; typedef double FF; const int tcode_CC='c',tcode_II='i',tcode_FF='f';
    int tcode_TT(const CC *tt) { return tcode_CC; }; int tcode_TT(const II *tt) { return tcode_II; }; int tcode_TT(const FF *tt) { return tcode_FF; };
    void as_TT(CC *tt, PyObject *oo) { *tt = PyLong_AsLong    (oo); if (*tt == ERROR and PyErr_Occurred()) throw ERROR; }
    void as_TT(II *tt, PyObject *oo) { *tt = PyLong_AsLongLong(oo); if (*tt == ERROR and PyErr_Occurred()) throw ERROR; }
    void as_TT(FF *tt, PyObject *oo) { *tt = PyFloat_AsDouble (oo); if (*tt == ERROR and PyErr_Occurred()) throw ERROR; }
    PyObject *from_TT(const CC *tt) { return PyLong_FromLong    (*tt); }
    PyObject *from_TT(const II *tt) { return PyLong_FromLongLong(*tt); }
    PyObject *from_TT(const FF *tt) { return PyFloat_FromDouble (*tt); }
    void str_TT(const CC *tt, char *&ss) { *ss = *tt < 0 ? '-' : ' '; ss ++; ss += sprintf(ss, "%.2x ", abs(*tt)); }
    void str_TT(const II *tt, char *&ss) { static const int ll = 10 + 2; static const i64 mm = pow(10, ll - 2); ss += abs(*tt) < mm ? sprintf(ss, "%*lli ", ll - 1, *tt) : sprintf(ss, "%*.*e ", ll - 1, ll - 8, (double)*tt); }
    void str_TT(const FF *tt, char *&ss) { static const int ll = 6 + 8; ss += sprintf(ss, "%*.*g ", ll - 1, ll - 8, *tt); }

    //// struct
#define NUMBYTES_LOOP1(self) for (int i0 = 0, j0 = 0; i0 < (self) ->shape0; i0 ++) for (j0 = 0; j0 < (self) ->shape1; j0 ++)
#define NUMBYTES_LOOP2(self, them1) check_shape(self, them1); for (int i0 = 0, j0 = 0, i1 = 0, j1 = 0, di1 = (them1) ->shape0 == 1 ? 0 : 1, dj1 = (them1) ->shape1 == 1 ? 0 : 1; i0 < (self) ->shape0; i0 ++, i1 += di1) for (j0 = j1 = 0; j0 < (self) ->shape1; j0 ++, j1 += dj1)
#define NUMBYTES_LOOP3(self, them1, them2) check_shape(self, them1); check_shape(self, them2); for (int i0 = 0, j0 = 0, i1 = 0, j1 = 0, i2 = 0, j2 = 0, di1 = (them1) ->shape0 == 1 ? 0 : 1, dj1 = (them1) ->shape1 == 1 ? 0 : 1, di2 = (them2) ->shape0 == 1 ? 0 : 1, dj2 = (them2) ->shape1 == 1 ? 0 : 1; i0 < (self) ->shape0; i0 ++, i1 += di1, i2 += di2) for (j0 = j1 = j2 = 0; j0 < (self) ->shape1; j0 ++, j1 += dj1, j2 += dj2)
#define NUMBYTES_SWITCH(tcode, check, cc, ii, ff, _) switch (tcode) {    \
      case tcode_CC: if (check) { numbytes<CC>::check_mem((numbytes<CC> *)check); } cc; break; \
      case tcode_II: if (check) { numbytes<II>::check_mem((numbytes<II> *)check); } ii; break; \
      case tcode_FF: if (check) { numbytes<FF>::check_mem((numbytes<FF> *)check); } ff; break; \
      default: throw PY::err(PyExc_ValueError, "invalid tcode <%c>", tcode); }
    template<typename TT> struct numbytes: PyObject { int tcode; PyObject *bytes; TT *offset; int shape0, shape1, stride0, stride1;
      static int check_idx0(numbytes *self, int idx) { if ((idx < 0 ? idx += self ->shape0 : idx) < 0 or self ->shape0 <= idx) throw PY::err(PyExc_IndexError, "index0 <%i> out of range", idx); return idx; }
      static int check_idx1(numbytes *self, int idx) { if ((idx < 0 ? idx += self ->shape1 : idx) < 0 or self ->shape1 <= idx) throw PY::err(PyExc_IndexError, "index1 <%i> out of range", idx); return idx; }
      static numbytes *check_mem(numbytes *self) { if (self ->offset < frombytes(self ->bytes) or PyObject_Size(self ->bytes) < (self ->offset - frombytes(self ->bytes)) + self ->shape0 * self ->shape1) throw PY::err(PyExc_MemoryError, "numbytes memory invalidated"); return self; }
      static void check_shape(numbytes *self, PyObject *aa) { numbytes *them = (numbytes *)aa; if ((them ->shape0 != 1 and them ->shape0 != self ->shape0) or (them ->shape1 != 1 and them ->shape1 != self ->shape1)) throw PY::err(PyExc_IndexError, "incompatible shape0 - self <%i %i> vs them <%i %i>", self ->shape0, self ->shape1, them ->shape0, them ->shape1); }
      static void check_tcode(numbytes *self, PyObject *aa) { numbytes *them = (numbytes *)aa; if (them ->tcode != self ->tcode) throw PY::err(PyExc_TypeError, "incompatible tcode self <%c> vs them <%c>", self ->tcode, them ->tcode); }
      static TT *frombytes(PyObject *bytes) { return (TT *)PyByteArray_AS_STRING(bytes); }
      static int contiguous(numbytes *self) { return self ->stride1 == 1 and frombytes(self ->bytes) == self ->offset; }
      static TT *getoffset(numbytes *self, int ii, int jj) { return self ->offset + ii * self ->stride0 + jj * self ->stride1; }
      static int length(numbytes *self) { return self ->shape0 * self ->shape1; }
      static int transposed(numbytes *self) { return self ->stride1 != 1; }
      static int tsize() { return sizeof(TT); }

      //// constructor
      static void numbytes_dealloc(numbytes *self) { Py_DECREF(self ->bytes); Py_TYPE(self) ->tp_free(self); }
      static numbytes *numbytes_new(PyTypeObject *type, int tcode, PyObject *bytes, TT *offset, int shape0, int shape1, int stride0, int stride1) { numbytes *self = (numbytes *)type ->tp_alloc(type, 0); if (not self) throw ERROR; self ->tcode = tcode; self ->bytes = bytes; self ->offset = offset; self ->shape0 = shape0; self ->shape1 = shape1; self ->stride0 = stride0; self ->stride1 = stride1; Py_INCREF(bytes); return self; }
      static PyObject *numbytes_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
        static const TT *tt; PyObject *tcode, *bytes; if (not PyArg_ParseTuple(args, "OO:numbytes_new", &tcode, &bytes)) throw ERROR;
        if (not PyByteArray_Check(bytes)) throw PY::err(PyExc_TypeError, "not bytearray type <%s>", PY::tpname(bytes));
        int ll = PyObject_Size(bytes); if (ll % tsize()) throw PY::err(PyExc_IndexError, "bytearray size <%i> not multiple of tsize <%i>", ll, tsize());
        ll /= tsize(); return numbytes_new(type, tcode_TT(tt), bytes, frombytes(bytes), 1, ll, ll, 1);
      }
      template <typename UU> static void copyto(numbytes *self, numbytes<UU> *them) { NUMBYTES_LOOP2(self, them) *numbytes<UU>::getoffset(them, i1, j1) = (UU)*getoffset(self, i0, j0); }
      static PyObject *py_copyto(numbytes *self, PyObject *aa) { check_type(Py_TYPE(aa)); NUMBYTES_SWITCH(CAST(numbytes *, aa) ->tcode, aa, copyto(self, (numbytes<CC> *)aa), copyto(self, (numbytes<II> *)aa), copyto(self, (numbytes<FF> *)aa),); Py_INCREF(aa); return aa; }
      static PyObject *py_fill_from_itr(numbytes *self, PyObject *aa) {
        PyObject *bb;
        try {
          if (not PyIter_Check(aa)) throw PY::err(PyExc_TypeError, "invalid fill type <%s>", PY::tpname(aa));
          NUMBYTES_LOOP1(self) {
            if (not (bb = PyIter_Next(aa))) Py_RETURN_NONE;
            as_TT(getoffset(self, i0, j0), bb); Py_DECREF(bb);
          }
          Py_INCREF(self); return self;
        } catch (...) { Py_XDECREF(bb); throw; }
      }
      static PyObject *py_reshape(numbytes *self, PyObject *args) {
        int ll, mm; if (not PyArg_ParseTuple(args, "ii:reshape", &ll, &mm)) throw ERROR;
        if (not contiguous(self)) throw PY::err(PyExc_IndexError, "cannot reshape non-contiguous array");
        if (ll == -1) ll = length(self) / mm; else if (mm == -1) mm = length(self) / ll;
        if (ll < 0 or ll * mm != length(self)) throw PY::err(PyExc_IndexError, "invalid reshape <%i %i> -> <%i %i>", self ->shape0, self ->shape1, ll, mm);
        return numbytes_new(Py_TYPE(self), self ->tcode, self ->bytes, self ->offset, ll, mm, mm, self ->stride1);
      }
      static PyObject *py_base(numbytes *self) { return numbytes_new(&TYPE, self ->tcode, self ->bytes, self ->offset, self ->shape0, self ->shape1, self ->stride0, self ->stride1); }
      static PyObject *py_bytes(numbytes *self) { Py_INCREF(self ->bytes); return self ->bytes; }
      static PyObject *py_contiguous(numbytes *self) { return PyLong_FromLong(contiguous(self)); }
      static PyObject *py_offset(numbytes *self) { return PyLong_FromLong(self ->offset - frombytes(self ->bytes)); }
      static PyObject *py_retype(numbytes *self, PyObject *aa) { return numbytes_new(check_type((PyTypeObject *)aa), self ->tcode, self ->bytes, self ->offset, self ->shape0, self ->shape1, self ->stride0, self ->stride1); }
      static PyObject *py_shape0(numbytes *self) { return PyLong_FromLong(self ->shape0); }
      static PyObject *py_shape1(numbytes *self) { return PyLong_FromLong(self ->shape1); }
      static PyObject *py___str__(numbytes *self) { char ss[length(self) * 16 + 1]; char *tt = ss; NUMBYTES_LOOP1(self) str_TT(getoffset(self, i0, j0), tt); return PyUnicode_FromStringAndSize(ss, tt - ss); }
      static PyObject *py_stride0(numbytes *self) { return PyLong_FromLong(self ->stride0); }
      static PyObject *py_stride1(numbytes *self) { return PyLong_FromLong(self ->stride1); }
      static PyObject *py_T(numbytes *self) { return numbytes_new(Py_TYPE(self), self ->tcode, self ->bytes, self ->offset, self ->shape1, self ->shape0, self ->stride1, self ->stride0); }
      static PyObject *py_tcode(numbytes *self) { return PyUnicode_FromFormat("%c", self ->tcode); }
      static PyObject *py_transposed(numbytes *self) { return PyLong_FromLong(transposed(self)); }
      static PyObject *py_tsize(numbytes *self) { return PyLong_FromLong(tsize()); }
      static PyObject *py_tsize_from_tcode(PyObject *_, PyObject *args) { return PyLong_FromLong(tsize()); }

      //// sequence
      static int sq_length(numbytes *self, PyObject *_) { return length(self); }
      static int sq_contains(numbytes *self, PyObject *aa) { TT bb; as_TT(&bb, aa); NUMBYTES_LOOP1(self) if (*getoffset(self, i0, j0) == bb) return true; return false; }
      static PyObject *sq_item(numbytes *self, PyObject *aa) { ssz ii = (ssz)aa; if (ii >= length(self)) throw ERROR; return from_TT(getoffset(self, ii / self ->shape1, ii % self ->shape1)); }
      static void parse_slice(numbytes *self, int ii, PyObject *slice, ssz *start, ssz *stop, ssz *step, ssz *slicelength) {
        if (PyLong_Check(slice)) { *start = ii ? check_idx1(self, PyLong_AsLong(slice)) : check_idx0(self, PyLong_AsLong(slice)); *stop = *start + 1; *step = 1; *slicelength = 1; }
        else if (PySlice_Check(slice)) { if (PySlice_GetIndicesEx((PySliceObject *)slice, ii ? self ->shape1 : self ->shape0, start, stop, step, slicelength) == ERROR) throw ERROR; }
        else throw PY::err(PyExc_TypeError, "invalid index%i type <%s>", ii, PY::tpname(slice));
      }
      static PyObject *py__getitem(numbytes *self, PyObject *args) {
        int ii, jj; if (PyArg_ParseTuple(args, "ii:_getitem", &ii, &jj)) { return from_TT(getoffset(self, check_idx0(self, ii), check_idx1(self, jj))); } else { PyErr_Clear(); }
        PyObject *slice0 = NULL, *slice1 = NULL; if (not PyArg_ParseTuple(args, "OO:_getitem", &slice0, &slice1)) throw ERROR;
        ssz start0, stop0, step0, slicelength0; parse_slice(self, 0, slice0, &start0, &stop0, &step0, &slicelength0);
        ssz start1, stop1, step1, slicelength1; parse_slice(self, 1, slice1, &start1, &stop1, &step1, &slicelength1);
        return numbytes_new(Py_TYPE(self), self ->tcode, self ->bytes, getoffset(self, start0, start1), slicelength0, slicelength1, step0 * self ->stride0, step1 * self ->stride1);
      }
      template<typename UU> static void set_slice(numbytes *self, numbytes<UU> *them) { NUMBYTES_LOOP2(self, them) *getoffset(self, i0, j0) = (TT)*numbytes<UU>::getoffset(them, i1, j1); }
      static PyObject *py__setitem(numbytes *self, PyObject *args) {
        PyObject *slices; numbytes<TT> *them; if (not PyArg_ParseTuple(args, "OO:_setitem", &slices, &them)) throw ERROR;
        int ii, jj; if (PyArg_ParseTuple(slices, "ii:_setitem", &ii, &jj)) { as_TT(getoffset(self, ii, jj), them); Py_RETURN_NONE; } else { PyErr_Clear(); }
        self = (numbytes *)py__getitem(self, slices);
        try {
          if (PyNumber_Check(them)) { TT bb; as_TT(&bb, them); NUMBYTES_LOOP1(self) *getoffset(self, i0, j0) = bb; } // number
          else { check_type(Py_TYPE(them)); NUMBYTES_SWITCH(them ->tcode, them, set_slice(self, (numbytes<CC> *)them), set_slice(self, (numbytes<II> *)them), set_slice(self, (numbytes<FF> *)them),); }
          Py_DECREF(self); Py_RETURN_NONE;
        } catch (...) { Py_DECREF(self); throw; }
      }
      static PyObject *py_count(numbytes *self, PyObject *aa) { TT bb; as_TT(&bb, aa); int ii = 0; NUMBYTES_LOOP1(self) if (*getoffset(self, i0, j0) == bb) ii ++; return PyLong_FromLong(ii); }
      static PyObject *py_index(numbytes *self, PyObject *aa) { TT bb; as_TT(&bb, aa); NUMBYTES_LOOP1(self) if (*getoffset(self, i0, j0) == bb) return PyLong_FromLong(i0 * self ->shape1 + j0); return PyLong_FromLong(-1); }
    };

    //// untemplate
    int tcode_args(PyObject *args) { char *tcode; PyObject *_; if (not PyArg_ParseTuple(args, "s|OOOO:tcode_args", &tcode, &_, &_, &_, &_)) throw ERROR; if (not tcode[0] or tcode[1]) throw PY::err(PyExc_ValueError, "tcode <%s> must be single character", tcode); return tcode[0]; }
    int tcode_self(PyObject *self) { check_type(Py_TYPE(self)); return CAST(numbytes<CC> *, self) ->tcode; }
#define NUMBYTES_METHOD

    //// sequence
    PySequenceMethods SEQUENCE = {
      (lenfunc)sq_length, // sq_length
      NULL, // sq_concat
      NULL, // sq_repeat
      (ssizeargfunc)sq_item, // sq_item
      NULL, // sq_slice
      NULL,	// sq_ass_item
      NULL, // sq_ass_slice
      (objobjproc)sq_contains, // sq_contains
      NULL, // sq_inplace_concat */
      NULL,	// sq_inplace_repeat
    };

    //// init
    void init() {
      TYPE.tp_basicsize = sizeof(numbytes<CC>);
      TYPE.tp_dealloc = (destructor)numbytes_dealloc;
      TYPE.tp_new = numbytes_new;
      TYPE.tp_as_sequence = &SEQUENCE;
    }
  }

  namespace MODULE {
    PYMETH_ADD_O PyObject *py_is_numbytes(PyObject *self, PyObject *aa) { return PyLong_FromLong(TYPE::is_type(Py_TYPE(aa))); }
    PyInit_module(_numbytes, {});
  }
}







namespace _math_op {
#include "numbytes.hpp"
  namespace TYPE {
#define MATH_OP1(rtype, fnc, cc, ii, ff, _) void fnc(CC *aa) { cc; }; void fnc(II *aa) { ii; }; void fnc(FF *aa) { ff; }; \
    PyObject *fnc(PyObject *self, PyObject *_) { try {                  \
        NUMBYTES_SWITCH(tcode_self(self), self,                         \
                        NUMBYTES_LOOP1((numbytes<CC> *)self) fnc(getoffset((numbytes<CC> *)self, i0, j0));, \
                        NUMBYTES_LOOP1((numbytes<II> *)self) fnc(getoffset((numbytes<II> *)self, i0, j0));, \
                        NUMBYTES_LOOP1((numbytes<FF> *)self) fnc(getoffset((numbytes<FF> *)self, i0, j0));, \
                        ); } catch (...) { return NULL; } Py_INCREF(self); return self; }
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py___neg__, *aa = -*aa, *aa = -*aa, *aa = -*aa,);
    PYMETH_ADD_NOARGS PyObject *py___pos__(PyObject *self, PyObject *_) { return self; }
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py___abs__, *aa = abs(*aa), *aa = abs(*aa), *aa = abs(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py___invert__, *aa = *aa ^ -1, *aa = *aa ^ -1LL, throw PY::err(PyExc_ArithmeticError, "cannot <~double>"),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_cos, throw PY::err(PyExc_ArithmeticError, "cannot <cos(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <cos(int64)>"), *aa = cos(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_sin, throw PY::err(PyExc_ArithmeticError, "cannot <sin(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <sin(int64)>"), *aa = sin(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_tan, throw PY::err(PyExc_ArithmeticError, "cannot <tan(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <tan(int64)>"), *aa = tan(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_acos, throw PY::err(PyExc_ArithmeticError, "cannot <acos(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <acos(int64)>"), *aa = acos(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_asin, throw PY::err(PyExc_ArithmeticError, "cannot <asin(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <asin(int64)>"), *aa = asin(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_atan, throw PY::err(PyExc_ArithmeticError, "cannot <atan(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <atan(int64)>"), *aa = atan(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_cosh, throw PY::err(PyExc_ArithmeticError, "cannot <cosh(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <cosh(int64)>"), *aa = cosh(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_sinh, throw PY::err(PyExc_ArithmeticError, "cannot <sinh(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <sinh(int64)>"), *aa = sinh(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_tanh, throw PY::err(PyExc_ArithmeticError, "cannot <tanh(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <tanh(int64)>"), *aa = tanh(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_exp, throw PY::err(PyExc_ArithmeticError, "cannot <exp(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <exp(int64)>"), *aa = exp(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_log, throw PY::err(PyExc_ArithmeticError, "cannot <log(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <log(int64)>"), *aa = log(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_log10, throw PY::err(PyExc_ArithmeticError, "cannot <log10(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <log10(int64)>"), *aa = log10(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_sqrt, throw PY::err(PyExc_ArithmeticError, "cannot <sqrt(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <sqrt(int64)>"), *aa = sqrt(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_ceil, throw PY::err(PyExc_ArithmeticError, "cannot <ceil(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <ceil(int64)>"), *aa = ceil(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_floor, throw PY::err(PyExc_ArithmeticError, "cannot <floor(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <floor(int64)>"), *aa = floor(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_log2, *aa = *aa <= 0 ? -1 : MY::log64((uch)*aa), *aa = *aa <= 0 ? -1 : MY::log64(*aa), *aa = log(*aa) * MY::INVLOG2, );
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_popcount, *aa = MY::popcount64((uch)*aa), *aa = MY::popcount64(*aa), throw PY::err(PyExc_ArithmeticError, "cannot <popcount(double)>"),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_roundeven, throw PY::err(PyExc_ArithmeticError, "cannot <roundeven(char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <roundeven(int64)>"), *aa = MY::roundeven(*aa),);
    MATH_OP1(PYMETH_ADD_NOARGS PyObject *,py_sign, *aa = SIGN(*aa), *aa = SIGN(*aa), *aa = SIGN(*aa),);
#define _MATH_OP2(TT, fnc) if (PyNumber_Check(them)) { TT tt; as_TT(&tt, them); NUMBYTES_LOOP1((numbytes<TT> *)self) fnc(getoffset((numbytes<TT> *)self, i0, j0), &tt); } \
    else { NUMBYTES_SWITCH(tcode_self(them), them,                      \
                           NUMBYTES_LOOP2((numbytes<TT> *)self, (numbytes<CC> *)them) fnc(getoffset((numbytes<TT> *)self, i0, j0), getoffset((numbytes<CC> *)them, i1, j1)), \
                           NUMBYTES_LOOP2((numbytes<TT> *)self, (numbytes<II> *)them) fnc(getoffset((numbytes<TT> *)self, i0, j0), getoffset((numbytes<II> *)them, i1, j1)), \
                           NUMBYTES_LOOP2((numbytes<TT> *)self, (numbytes<FF> *)them) fnc(getoffset((numbytes<TT> *)self, i0, j0), getoffset((numbytes<FF> *)them, i1, j1)), \
                           ); }

#define MATH_OP2(rtype, fnc, cc, ii, ff, _) template<typename UU> void fnc(CC *aa, UU *bb) { cc; }; template<typename UU> void fnc(II *aa, UU *bb) { ii; }; template<typename UU> void fnc(FF *aa, UU *bb) { ff; }; \
    PyObject *fnc(PyObject *self, PyObject *them) { try {               \
        NUMBYTES_SWITCH(tcode_self(self), self, _MATH_OP2(CC, fnc), _MATH_OP2(II, fnc), _MATH_OP2(FF, fnc),); \
        Py_INCREF(self); return self; } catch (...) { return NULL; } }
    MATH_OP2(PYMETH_ADD_O PyObject *,py___add__, *aa += (CC)*bb, *aa += (II)*bb, *aa += (FF)*bb,);
    MATH_OP2(PYMETH_ADD_O PyObject *,py___sub__, *aa -= (CC)*bb, *aa -= (II)*bb, *aa -= (FF)*bb,);
    MATH_OP2(PYMETH_ADD_O PyObject *,py___mul__, *aa *= (CC)*bb, *aa *= (II)*bb, *aa *= (FF)*bb,);
    MATH_OP2(PYMETH_ADD_O PyObject *,py___truediv__, *aa /= (CC)*bb, *aa /= (II)*bb, *aa /= (FF)*bb,);
    MATH_OP2(PYMETH_ADD_O PyObject *,py___mod__, *aa %= (CC)*bb, *aa %= (II)*bb, fmod(*aa, (FF)*bb),);
    MATH_OP2(PYMETH_ADD_O PyObject *,py___pow__, *aa = pow(*aa, (CC)*bb), *aa = pow(*aa, (II)*bb), *aa = pow(*aa, (FF)*bb),);
    MATH_OP2(PYMETH_ADD_O PyObject *,py___lshift__, *aa <<= (CC)*bb, *aa <<= (II)*bb, throw PY::err(PyExc_ArithmeticError, "cannot <double <<= double>"),);
    MATH_OP2(PYMETH_ADD_O PyObject *,py___rshift__, *aa >>= (CC)*bb, *aa >>= (II)*bb, throw PY::err(PyExc_ArithmeticError, "cannot <double >>= double>"),);
    MATH_OP2(PYMETH_ADD_O PyObject *,py___and__, *aa &= (CC)*bb, *aa &= (II)*bb, throw PY::err(PyExc_ArithmeticError, "cannot <double &= double>"),);
    MATH_OP2(PYMETH_ADD_O PyObject *,py___or__, *aa |= (CC)*bb, *aa |= (II)*bb, throw PY::err(PyExc_ArithmeticError, "cannot <double |= double>"),);
    MATH_OP2(PYMETH_ADD_O PyObject *,py___xor__, *aa ^= (CC)*bb, *aa ^= (II)*bb, throw PY::err(PyExc_ArithmeticError, "cannot <double ^= double>"),);
    MATH_OP2(PYMETH_ADD_O PyObject *,py_atan2, throw PY::err(PyExc_ArithmeticError, "cannot <atan2(char, char)>"), throw PY::err(PyExc_ArithmeticError, "cannot <atan2(int64, int64)>"), *aa = atan2(*aa, (FF)*bb),);

#define __MATH_OP3(TT, UU, fnc)                                         \
    if (PyNumber_Check(them2)) { TT tt; as_TT(&tt, them2); NUMBYTES_LOOP2((numbytes<TT> *)self, (numbytes<UU> *)them1) fnc(getoffset((numbytes<TT> *)self, i0, j0), getoffset((numbytes<UU> *)them1, i1, j1), &tt); } else { \
      NUMBYTES_SWITCH(tcode_self(them2), them2,                         \
                      NUMBYTES_LOOP3((numbytes<TT> *)self, (numbytes<UU> *)them1, (numbytes<CC> *)them2) fnc(getoffset((numbytes<TT> *)self, i0, j0), getoffset((numbytes<UU> *)them1, i1, j1), getoffset((numbytes<CC> *)them2, i2, j2)), \
                      NUMBYTES_LOOP3((numbytes<TT> *)self, (numbytes<UU> *)them1, (numbytes<II> *)them2) fnc(getoffset((numbytes<TT> *)self, i0, j0), getoffset((numbytes<UU> *)them1, i1, j1), getoffset((numbytes<II> *)them2, i2, j2)), \
                      NUMBYTES_LOOP3((numbytes<TT> *)self, (numbytes<UU> *)them1, (numbytes<FF> *)them2) fnc(getoffset((numbytes<TT> *)self, i0, j0), getoffset((numbytes<UU> *)them1, i1, j1), getoffset((numbytes<FF> *)them2, i2, j2)), \
                      ); }
#define _MATH_OP3(TT, fnc)                                              \
    if (PyNumber_Check(them1)) { TT uu; as_TT(&uu, them1);              \
      if (PyNumber_Check(them2)) { TT vv; as_TT(&vv, them1); NUMBYTES_LOOP1((numbytes<TT> *)self) fnc(getoffset((numbytes<TT> *)self, i0, j0), &uu, &vv); } else { \
        NUMBYTES_SWITCH(tcode_self(them2), them2,                       \
                        NUMBYTES_LOOP2((numbytes<TT> *)self, (numbytes<CC> *)them2) fnc(getoffset((numbytes<TT> *)self, i0, j0), &uu, getoffset((numbytes<CC> *)them2, i1, j1)), \
                        NUMBYTES_LOOP2((numbytes<TT> *)self, (numbytes<II> *)them2) fnc(getoffset((numbytes<TT> *)self, i0, j0), &uu, getoffset((numbytes<II> *)them2, i1, j1)), \
                        NUMBYTES_LOOP2((numbytes<TT> *)self, (numbytes<FF> *)them2) fnc(getoffset((numbytes<TT> *)self, i0, j0), &uu, getoffset((numbytes<FF> *)them2, i1, j1)), \
                        ); } } else { NUMBYTES_SWITCH(tcode_self(them1), them1, __MATH_OP3(TT, CC, fnc), __MATH_OP3(TT, II, fnc), __MATH_OP3(TT, FF, fnc),); }
#define MATH_OP3(rtype, fnc, dd, ii, ff, _) template<typename UU, typename VV> void fnc(CC *aa, UU *bb, VV *cc) { dd; }; template<typename UU, typename VV> void fnc(II *aa, UU *bb, VV *cc) { ii; }; template<typename UU, typename VV> void fnc(FF *aa, UU *bb, VV *cc) { ff; }; \
    PyObject *fnc(PyObject *self, PyObject *args) { try {               \
        PyObject *them1, *them2; if (not PyArg_ParseTuple(args, "OO:MATH_OP3", &them1, &them2)) throw ERROR; \
        NUMBYTES_SWITCH(tcode_self(self), self, _MATH_OP3(CC, fnc), _MATH_OP3(II, fnc), _MATH_OP3(FF, fnc),); \
        Py_INCREF(self); return self; } catch (...) { return NULL; } }

    MATH_OP3(PYMETH_ADD_VARARGS PyObject *,py___eq__, *aa = *bb == *cc, *aa = *bb == *cc, *aa = *bb == *cc,);
    MATH_OP3(PYMETH_ADD_VARARGS PyObject *,py___ne__, *aa = *bb != *cc, *aa = *bb != *cc, *aa = *bb != *cc,);
    MATH_OP3(PYMETH_ADD_VARARGS PyObject *,py___lt__, *aa = *bb <  *cc, *aa = *bb <  *cc, *aa = *bb <  *cc,);
    MATH_OP3(PYMETH_ADD_VARARGS PyObject *,py___le__, *aa = *bb <= *cc, *aa = *bb <= *cc, *aa = *bb <= *cc,);
    MATH_OP3(PYMETH_ADD_VARARGS PyObject *,py___gt__, *aa = *bb >  *cc, *aa = *bb >  *cc, *aa = *bb >  *cc,);
    MATH_OP3(PYMETH_ADD_VARARGS PyObject *,py___ge__, *aa = *bb >= *cc, *aa = *bb >= *cc, *aa = *bb >= *cc,);
    MATH_OP3(PYMETH_ADD_VARARGS PyObject *,py_fma, *aa = fma(*bb, *cc, *aa), *aa = fma(*bb, *cc, *aa), *aa = fma(*bb, *cc, *aa),);
  }
  namespace MODULE { PyInit_module(_math_op, {}); }
}
