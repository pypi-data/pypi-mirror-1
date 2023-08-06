extern "C" {
#include "Python.h" // must be included first
#include "structmember.h" // python struct
#include "png.h" // png
}

#include <cmath>
const double INVLOG2 = 1.0 / log(2.0);
#include <cstdlib>
#include <iostream>
#include <vector>
using namespace std;

typedef long long i64; typedef ssize_t ssz; typedef unsigned char uch; typedef unsigned int uint; typedef unsigned long long u64; int ERROR = -1;
#define CLOSURE(rtype, fname, args, body) class fname##_ { public: static rtype fname args body; }; rtype (*fname) args = &fname##_::fname;
#define DIVCEIL(aa, bb) ((aa + bb - 1) / bb)
#define DIVROUND(aa, bb) ((aa + (bb / 2)) / bb)
#define MAX(aa, bb) ((aa) > (bb) ? (aa) : (bb))
#define MIN(aa, bb) ((aa) < (bb) ? (aa) : (bb))
#define SWAP(aa, bb, cc) cc = aa; aa = bb; bb = cc;
#define VSNPRINTF(ss, ll, fmt) char ss[ll]; va_list args; va_start(args, fmt); vsnprintf(ss, ll, fmt, args); va_end(args);
const char *ssformat(const char *fmt, ...) { static VSNPRINTF(ss, 1024, fmt); return ss; }
inline u64 popcount64(u64 aa) {
  aa -= ((aa >> 1) & 0x5555555555555555LLU); // count 2 bit
  aa = (((aa >> 2) & 0x3333333333333333LLU) + (aa & 0x3333333333333333LLU)); // count 4 bit
  aa = (((aa >> 4) + aa) & 0x0f0f0f0f0f0f0f0fLLU); // count 8 bit
  aa += (aa >> 8); aa += (aa >> 16); aa += (aa >> 32); return aa & 0x7f; // count 16/32/64 bit
}
inline u64 log64(u64 aa) { aa |= (aa >> 1); aa |= (aa >> 2); aa |= (aa >> 4); aa |= (aa >> 16); aa |= (aa >> 32); return popcount64(aa) - 1; }
// template<typename TT> TT log2_TT(TT aa, TT shift = sizeof(TT) / 2, TT log = 0) {
  // if (aa >= 2) {
    // for (; not (aa >> shift); shift >>= 1);
    // return log2_TT<TT>(aa >> shift, shift >> 1, log + shift);
  // }
  // return (aa == 1) log : -1;
// }

#define ASCIIPORN
inline PyObject *PYERR(PyObject *err, const char *fmt = "", ...) { VSNPRINTF(ss, 1024, fmt); PyErr_SetString(err, ss); return err; }
inline int PYPRINT(const char *fmt, ...) { VSNPRINTF(ss, 1024, fmt); PyFile_WriteString(ss, PySys_GetObject("stdout")); return 0; }
inline const char *PYTPNAME(PyObject *aa) { return Py_TYPE(aa)-> tp_name; }
const char *PYSTR(PyObject *aa) {
  static char ss[1024]; PyObject *bb = PyObject_Str(aa), *cc = NULL; if (not bb) throw ERROR;
  try {
    cc = PyUnicode_AsEncodedString(PyObject_Str(bb), "latin", NULL); if (not cc) throw ERROR;
    strncpy(ss, PyBytes_AS_STRING(cc), sizeof(ss)); ss[sizeof(ss) - 1] = 0;
    Py_XDECREF(bb); Py_XDECREF(cc); return ss;
  } catch (...) { Py_XDECREF(bb); Py_XDECREF(cc); throw; }
}






namespace NUMBYTES {
  typedef char CC; typedef i64 II; typedef double FF;
  const int code_CC='c',code_II='i',code_FF='f';
  inline int code_TT(const CC *tt) { return code_CC; }
  inline int code_TT(const II *tt) { return code_II; }
  inline int code_TT(const FF *tt) { return code_FF; }

  //// helper
  inline PyObject *from_TT(const CC *tt) { return PyLong_FromLong    (*tt); }
  inline PyObject *from_TT(const II *tt) { return PyLong_FromLongLong(*tt); }
  inline PyObject *from_TT(const FF *tt) { return PyFloat_FromDouble (*tt); }
  inline void as_TT(CC *tt, PyObject *oo) { *tt = PyLong_AsLong    (oo); if (*tt == ERROR and PyErr_Occurred()) throw ERROR; }
  inline void as_TT(II *tt, PyObject *oo) { *tt = PyLong_AsLongLong(oo); if (*tt == ERROR and PyErr_Occurred()) throw ERROR; }
  inline void as_TT(FF *tt, PyObject *oo) { *tt = PyFloat_AsDouble (oo); if (*tt == ERROR and PyErr_Occurred()) throw ERROR; }
  inline void str_TT(const CC *tt, char *&ss) { *ss = *tt < 0 ? '-' : ' '; ss ++; ss += sprintf(ss, "%.2x ", abs(*tt)); }
  inline void str_TT(const II *tt, char *&ss) { static const int ll = 10 + 2; static const i64 mm = pow(10, ll - 2); ss += abs(*tt) < mm ? sprintf(ss, "%*lli ", ll - 1, *tt) : sprintf(ss, "%*.*e ", ll - 1, ll - 8, (double)*tt); }
  inline void str_TT(const FF *tt, char *&ss) { static const int ll = 6 + 8; ss += sprintf(ss, "%*.*g ", ll - 1, ll - 8, *tt); }

  PyTypeObject TYPE = {PyVarObject_HEAD_INIT(NULL, 0)"_numbytes",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  inline int CHECK_NUMBYTES(PyObject *self) { return PyObject_TypeCheck(self, &TYPE); }
  PySequenceMethods PYSEQUENCE = {NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,};

  struct PYGETSETDEF: vector<PyGetSetDef> {
    ~PYGETSETDEF() {}
    PYGETSETDEF() { resize(1); }
    void add(const char *fname, PyObject *(fnc)(PyObject *, PyObject *)) { insert(begin(), (PyGetSetDef) { (char *)fname, (getter)fnc, }); }
  } GETSET;

  struct PYMETHODDEF: vector<PyMethodDef> {
    ~PYMETHODDEF() {}
    PYMETHODDEF() { resize(1); }
    void add(const char *fname, PyObject *(fnc)(PyObject *, PyObject *), int flags) { insert(begin(), (PyMethodDef) { fname, (PyCFunction)fnc, flags}); }
  } METHOD;

  template<typename TT> struct numbytes: PyObject { int tcode; PyObject *bytes; TT *words; int shape0, shape1, strides0, strides1;

#define NUMBYTES_METH
#define NUMBYTES_LOOP1(self) for (int i0 = 0, j0 = 0; i0 < (self)-> shape0; i0 ++) for (j0 = 0; j0 < (self)-> shape1; j0 ++)
#define NUMBYTES_LOOP2(self, them1) CHECK_SHAPE(self, them1); int i0, j0, i1, j1, di1 = (them1)-> shape0 == 1 ? 0 : 1, dj1 = (them1)-> shape1 == 1 ? 0 : 1; for (i0 = i1 = 0; i0 < (self)-> shape0; i0 ++, i1 += di1) for (j0 = j1 = 0; j0 < (self)-> shape1; j0 ++, j1 += dj1)
#define NUMBYTES_LOOP3(self, them1, them2) CHECK_SHAPE(self, them1); CHECK_SHAPE(self, them2); int i0, j0, i1, j1, i2, j2, di1 = (them1)-> shape0 == 1 ? 0 : 1, dj1 = (them1)-> shape1 == 1 ? 0 : 1, di2 = (them2)-> shape0 == 1 ? 0 : 1, dj2 = (them2)-> shape1 == 1 ? 0 : 1; for (i0 = i1 = i2 = 0; i0 < (self)-> shape0; i0 ++, i1 += di1, i2 += di2) for (j0 = j1 = j2 = 0; j0 < (self)-> shape1; j0 ++, j1 += dj1, j2 += dj2)
#define NUMBYTES_SWITCH(tcode, check, cc, ii, ff, tt) switch (tcode) {  \
    case code_CC: if (check and CHECK_NUMBYTES((PyObject *)check)) numbytes<CC>::CHECK_MEM((numbytes<CC> *)check); cc; break; \
    case code_II: if (check and CHECK_NUMBYTES((PyObject *)check)) numbytes<II>::CHECK_MEM((numbytes<II> *)check); ii; break; \
    case code_FF: if (check and CHECK_NUMBYTES((PyObject *)check)) numbytes<FF>::CHECK_MEM((numbytes<FF> *)check); ff; break; \
    default: throw PYERR(PyExc_ValueError, "invalid tcode <%c>", tcode); }

    inline static int CONTIGUOUS(numbytes *self) { return self-> strides1 == 1 and BYTES(self-> bytes) == self-> words; }
    inline static TT *GETWORD(numbytes *self, int ii, int jj) { return self-> words + ii * self-> strides0 + jj * self-> strides1; }
    inline static int LENGTH(numbytes *self) { return self-> shape0 * self-> shape1; }
    inline static int TRANSPOSED(numbytes *self) { return self-> strides1 != 1; }
    inline static int TCODE(numbytes *self) { return self-> tcode; }
    inline static int TSIZE() { return sizeof(TT); }
    inline static TT *BYTES(PyObject *bytes) { return (TT *)PyByteArray_AS_STRING(bytes); }

    //// constructor
    static void numbytes_dealloc(numbytes *self, PyObject *args) { Py_DECREF(self-> bytes); PyObject_Del(self); }
    static numbytes *numbytes_new(PyTypeObject *type, int tcode, PyObject *bytes, TT *words, int shape0, int shape1, int strides0, int strides1) {
      numbytes *self = (numbytes *)type-> tp_alloc(type, 0); if (not self) throw ERROR;
      self-> tcode = tcode; self-> bytes = bytes; self-> words = words; self-> shape0 = shape0; self-> shape1 = shape1; self-> strides0 = strides0; self-> strides1 = strides1; Py_INCREF(bytes);
      return self;
    }
    static PyObject *numbytes_new(numbytes *type, PyObject *args) {
      static const TT *tt; PyObject *tcode, *bytes; if (not PyArg_ParseTuple(args, "OO:numbytes_new", &tcode, &bytes)) throw ERROR;
      if (not PyByteArray_Check(bytes)) throw PYERR(PyExc_TypeError, "not bytearray type <%s>", PYTPNAME(bytes));
      int ll = PyObject_Size(bytes); if (ll % TSIZE()) throw PYERR(PyExc_IndexError, "bytearray size <%i> not multiple of tsize <%i>", ll, TSIZE());
      ll /= TSIZE(); return numbytes_new((PyTypeObject *)type, code_TT(tt), bytes, BYTES(bytes), 1, ll, ll, 1);
    }
    static PyObject *__str__(numbytes *self, PyObject *args) {
      char ss[LENGTH(self) * 16 + 1]; char *tt = ss; NUMBYTES_LOOP1(self) str_TT(GETWORD(self, i0, j0), tt);
      return PyUnicode_FromStringAndSize(ss, tt - ss);
    }
    NUMBYTES_METH static PyObject *static_tsize_from_tcode(PyObject *_, PyObject *args) { return PyLong_FromLong(TSIZE()); }

    //// sequence
    static int sq_length(numbytes *self, PyObject *args) { return LENGTH(self); }
    static int sq_contains(numbytes *self, PyObject *aa) { TT bb; as_TT(&bb, aa); NUMBYTES_LOOP1(self) if (*GETWORD(self, i0, j0) == bb) return true; return false; }
    static PyObject *sq_item(numbytes *self, PyObject *args) { ssz ii = (ssz)args; if (ii >= LENGTH(self)) throw ERROR; return from_TT(GETWORD(self, ii / self-> shape1, ii % self-> shape1)); }
    inline static int CHECK_IDX0(numbytes *self, int idx) { if ((idx < 0 ? idx += self-> shape0 : idx) < 0 or self-> shape0 <= idx) throw PYERR(PyExc_IndexError, "index0 <%i> out of range", idx); return idx; }
    inline static int CHECK_IDX1(numbytes *self, int idx) { if ((idx < 0 ? idx += self-> shape1 : idx) < 0 or self-> shape1 <= idx) throw PYERR(PyExc_IndexError, "index1 <%i> out of range", idx); return idx; }
    inline static numbytes *CHECK_MEM(numbytes *self) { if (self-> words < BYTES(self-> bytes) or PyObject_Size(self-> bytes) < (self-> words - BYTES(self-> bytes)) + self-> shape0 * self-> shape1) throw PYERR(PyExc_MemoryError, "numbytes memory invalidated"); return self; }
    template <typename UU> inline static void CHECK_SHAPE(numbytes *self, numbytes<UU> *them) {
      if ((them-> shape0 != 1 and them-> shape0 != self-> shape0) or (them-> shape1 != 1 and them-> shape1 != self-> shape1)) throw PYERR(PyExc_IndexError, "inconsistent shape0 - self <%i %i> vs them <%i %i>", self-> shape0, self-> shape1, them-> shape0, them-> shape1);
    }
    // inline numbytes *CHECK_TCODE(PyObject *them) { if (VIEW(TT, them)-> tcode != tcode) throw pyerr(PyExc_TypeError, "inconsistent tcode self<%c> vs them<%c>", tcode, (VIEW(TT, them))-> tcode); return VIEW(TT, them); }
    inline static void PARSE_SLICE(numbytes *self, int ii, PyObject *slice, ssz *start, ssz *stop, ssz *step, ssz *slicelength) {
      if (PyLong_Check(slice)) { *start = ii ? CHECK_IDX1(self, PyLong_AsLong(slice)) : CHECK_IDX0(self, PyLong_AsLong(slice)); *stop = *start + 1; *step = 1; *slicelength = 1; }
      else if (PySlice_Check(slice)) { if (PySlice_GetIndicesEx((PySliceObject *)slice, ii ? self-> shape1 : self-> shape0, start, stop, step, slicelength) == ERROR) throw ERROR; }
      else throw PYERR(PyExc_TypeError, "invalid index%i type <%s>", ii, PYTPNAME(slice));
    }
    NUMBYTES_METH static PyObject *_getitem(numbytes *self, PyObject *args) {
      int ii, jj; if (PyArg_ParseTuple(args, "ii:_getitem", &ii, &jj)) { return from_TT(GETWORD(self, CHECK_IDX0(self, ii), CHECK_IDX1(self, jj))); } else { PyErr_Clear(); }
      PyObject *slice0 = NULL, *slice1 = NULL; if (not PyArg_ParseTuple(args, "OO:_getitem", &slice0, &slice1)) throw ERROR;
      ssz start0, stop0, step0, slicelength0; PARSE_SLICE(self, 0, slice0, &start0, &stop0, &step0, &slicelength0);
      ssz start1, stop1, step1, slicelength1; PARSE_SLICE(self, 1, slice1, &start1, &stop1, &step1, &slicelength1);
      return numbytes_new(Py_TYPE(self), self-> tcode, self-> bytes, GETWORD(self, start0, start1), slicelength0, slicelength1, step0 * self-> strides0, step1 * self-> strides1);
    }
    template<typename UU> inline static void SETSLICE(numbytes *self, numbytes<UU> *them) { NUMBYTES_LOOP2(self, them) *GETWORD(self, i0, j0) = (TT)*numbytes<UU>::GETWORD(them, i1, j1); }
    NUMBYTES_METH static PyObject *_setitem(numbytes *self, PyObject *args) {
      PyObject *slices; numbytes *them; if (not PyArg_ParseTuple(args, "OO:__setitem__", &slices, &them)) throw ERROR;
      int ii, jj; if (PyArg_ParseTuple(slices, "ii:__setitem__", &ii, &jj)) { as_TT(GETWORD(self, ii, jj), them); Py_RETURN_NONE; } else { PyErr_Clear(); }
      self = (numbytes *) _getitem(self, slices);
      try {
        if (PyNumber_Check(them)) { TT bb; as_TT(&bb, them); NUMBYTES_LOOP1(self) *GETWORD(self, i0, j0) = bb; } // number
        else if (CHECK_NUMBYTES(them)) { NUMBYTES_SWITCH(them-> tcode, them, SETSLICE(self, (numbytes<CC> *) them), SETSLICE(self, (numbytes<II> *) them), SETSLICE(self, (numbytes<FF> *) them),); }
        else throw PYERR(PyExc_TypeError, "invalid setitem type <%s>", PYTPNAME(them));
        Py_DECREF(self); Py_RETURN_NONE;
      } catch (...) { Py_DECREF(self); throw; }
    }

    //// getset
    NUMBYTES_METH static PyObject *get_base(numbytes *self, PyObject *closure) { return numbytes_new(&TYPE, self-> tcode, self-> bytes, self-> words, self-> shape0, self-> shape1, self-> strides0, self-> strides1); }
    NUMBYTES_METH static PyObject *get_bytes(numbytes *self, PyObject *closure) { Py_INCREF(self-> bytes); return self-> bytes; }
    NUMBYTES_METH static PyObject *get_contiguous(numbytes *self, PyObject *closure) { return PyLong_FromLong(CONTIGUOUS(self)); }
    NUMBYTES_METH static PyObject *get_shape0(numbytes *self, PyObject *closure) { return PyLong_FromLong(self-> shape0); }
    NUMBYTES_METH static PyObject *get_shape1(numbytes *self, PyObject *closure) { return PyLong_FromLong(self-> shape1); }
    NUMBYTES_METH static PyObject *get_strides0(numbytes *self, PyObject *closure) { return PyLong_FromLong(self-> strides0); }
    NUMBYTES_METH static PyObject *get_strides1(numbytes *self, PyObject *closure) { return PyLong_FromLong(self-> strides1); }
    NUMBYTES_METH static PyObject *get_T(numbytes *self, PyObject *closure) { return numbytes_new(Py_TYPE(self), self-> tcode, self-> bytes, self-> words, self-> shape1, self-> shape0, self-> strides1, self-> strides0); }
    NUMBYTES_METH static PyObject *get_tcode(numbytes *self, PyObject *closure) { return PyUnicode_FromFormat("%c", self-> tcode); }
    NUMBYTES_METH static PyObject *get_transposed(numbytes *self, PyObject *closure) { return PyLong_FromLong(TRANSPOSED(self)); }
    NUMBYTES_METH static PyObject *get_tsize(numbytes *self, PyObject *closure) { return PyLong_FromLong(TSIZE()); }

    //// method
    template <typename UU> inline static void copy_to(numbytes *self, numbytes<UU> *them) { NUMBYTES_LOOP2(self, them) *numbytes<UU>::GETWORD(them, i1, j1) = (UU)*GETWORD(self, i0, j0); }
    NUMBYTES_METH static PyObject *copy_to(numbytes *self, PyObject *args) {
      numbytes *them; if (not PyArg_ParseTuple(args, "O:copy_to", &them)) throw ERROR;
      NUMBYTES_SWITCH(them-> tcode, them, copy_to(self, (numbytes<CC> *)them), copy_to(self, (numbytes<II> *)them), copy_to(self, (numbytes<FF> *)them),);
      Py_INCREF(them); return them;
    }
    NUMBYTES_METH static PyObject *fill_from_itr(numbytes *self, PyObject *args) {
      PyObject *itr, *aa; if (not PyArg_ParseTuple(args, "O:fill_from_itr", &itr)) throw ERROR;
      try {
        if (PyIter_Check(itr)) {
          NUMBYTES_LOOP1(self) {
            if (not (aa = PyIter_Next(itr))) Py_RETURN_NONE;
            as_TT(GETWORD(self, i0, j0), aa);
            Py_DECREF(aa);
          }
        }
        else throw PYERR(PyExc_TypeError, "invalid fill type <%s>", PYTPNAME(itr));
        Py_INCREF(self); return self;
      } catch (...) { Py_XDECREF(aa); throw; }
    }
    NUMBYTES_METH static PyObject *reshape(numbytes *self, PyObject *args) {
      int ll, mm; if (not PyArg_ParseTuple(args, "ii:reshape", &ll, &mm)) throw ERROR;
      if (not CONTIGUOUS(self)) throw PYERR(PyExc_IndexError, "cannot reshape non-contiguous numbytes");
      if (ll == -1) ll = LENGTH(self) / mm; else if (mm == -1) mm = LENGTH(self) / ll;
      if (ll < 0 or ll * mm != LENGTH(self)) throw PYERR(PyExc_IndexError, "invalid reshape <%i %i>-> <%i %i>", self-> shape0, self-> shape1, ll, mm);
      return numbytes_new(Py_TYPE(self), self-> tcode, self-> bytes, self-> words, ll, mm, mm, self-> strides1);
    }
    NUMBYTES_METH static PyObject *retype(numbytes *self, PyObject *args) {
      PyTypeObject *type; if (not PyArg_ParseTuple(args, "O:retype", &type)) throw ERROR;
      return numbytes_new(type, self-> tcode, self-> bytes, self-> words, self-> shape0, self-> shape1, self-> strides0, self-> strides1);
    }
  };

  inline int TCODE_ARGS(PyObject *args) {
    char *tcode; PyObject *_; if (not PyArg_ParseTuple(args, "s|OOOO:TCODE_ARGS", &tcode, &_, &_, &_, &_)) throw ERROR;
    if (not *tcode or tcode[1]) throw PYERR(PyExc_ValueError, "tcode <%s> must be one character", tcode);
    return *tcode;
  }
  inline int TCODE_SELF(PyObject *self) { return  (((numbytes<CC> *)self)-> tcode); }

#undef NUMBYTES_METH
#define NUMBYTES_METH(rtype, fnc, err, tcode) rtype fnc(PyObject *self, PyObject *args) { try { \
      NUMBYTES_SWITCH(tcode, self,                                      \
                      return numbytes<CC>::fnc((numbytes<CC> *)self, args);, \
                      return numbytes<II>::fnc((numbytes<II> *)self, args);, \
                      return numbytes<FF>::fnc((numbytes<FF> *)self, args);, \
                      ); } catch (...) { return err; } }

  NUMBYTES_METH(void, numbytes_dealloc, , TCODE_SELF(self));
  NUMBYTES_METH(PyObject *, numbytes_new, NULL, TCODE_ARGS(args));
  NUMBYTES_METH(PyObject *, __str__, NULL, TCODE_SELF(self));
  NUMBYTES_METH(int, sq_length, ERROR, TCODE_SELF(self));
  NUMBYTES_METH(int, sq_contains, ERROR, TCODE_SELF(self));
  NUMBYTES_METH(PyObject *, sq_item, NULL, TCODE_SELF(self));

  //// export
  PyObject *numbytes_init(PyObject *module) {
    // sequence
    TYPE.tp_as_sequence = &PYSEQUENCE;
    PYSEQUENCE.sq_length = (lenfunc)sq_length;
    PYSEQUENCE.sq_contains = (objobjproc)sq_contains;
    PYSEQUENCE.sq_item = (ssizeargfunc)sq_item;

    // type
    TYPE.tp_basicsize = sizeof(numbytes<CC>);
    TYPE.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE;
    TYPE.tp_getset = &GETSET[0];
    TYPE.tp_methods = &METHOD[0];
    TYPE.tp_dealloc = (destructor)numbytes_dealloc;
    TYPE.tp_new = (newfunc)numbytes_new;
    TYPE.tp_str = (reprfunc)__str__;

    if (PyType_Ready(&TYPE) < 0) return NULL; Py_INCREF(&TYPE); PyModule_AddObject(module, "_numbytes", (PyObject *) &TYPE); return module;
  }

  //// math
#define MATH_IOP1(fname, cc, ii, ff, tt) inline void fname(CC *aa) { cc; }; inline void fname(II *aa) { ii; }; inline void fname(FF *aa) { ff; };
#define MATH_IOP2(fname, cc, ii, ff, tt) template<typename UU> inline void fname(CC *aa, UU *bb) { cc; }; template<typename UU> inline void fname(II *aa, UU *bb) { ii; }; template<typename UU> inline void fname(FF *aa, UU *bb) { ff; };
#define MATH_METH1(fname)                                               \
  PyObject *fname(PyObject *self, PyObject *args) { try {               \
      if (not PyArg_ParseTuple(args, ":MATH_IOP1")) throw ERROR; \
      NUMBYTES_SWITCH(TCODE_SELF(self), self,                           \
                      NUMBYTES_LOOP1((numbytes<CC> *)self) fname(numbytes<CC>::GETWORD((numbytes<CC> *)self, i0, j0));, \
                      NUMBYTES_LOOP1((numbytes<II> *)self) fname(numbytes<II>::GETWORD((numbytes<II> *)self, i0, j0));, \
                      NUMBYTES_LOOP1((numbytes<FF> *)self) fname(numbytes<FF>::GETWORD((numbytes<FF> *)self, i0, j0));, \
                      ); } catch (...) { return NULL; } Py_INCREF(self); return self; }
#define MATH_METH2(fname)                                               \
  template<typename TT> PyObject *fname(numbytes<TT> *self, PyObject *args) { \
    numbytes<TT> *them; if (not PyArg_ParseTuple(args, "O:MATH_IOP2", &them)) throw ERROR; \
    if (PyNumber_Check(them)) { TT tt; as_TT(&tt, them); NUMBYTES_LOOP1(self) fname(numbytes<TT>::GETWORD(self, i0, j0), &tt); } \
    else if (CHECK_NUMBYTES(them)) {                                    \
      numbytes<TT>::CHECK_SHAPE(self, them); int i0, j0, i1, j1, di1 = them-> shape0 == 1 ? 0 : 1, dj1 = them-> shape1 == 1 ? 0 : 1; \
      NUMBYTES_SWITCH(them-> tcode, them,                               \
                      for (i0 = i1 = 0; i0 < self-> shape0; i0 ++, i1 += di1) for (j0 = j1 = 0; j0 < self-> shape1; j0 ++, j1 += dj1) fname<CC>(numbytes<TT>::GETWORD(self, i0, j0), numbytes<CC>::GETWORD((numbytes<CC> *)them, i1, j1));, \
                      for (i0 = i1 = 0; i0 < self-> shape0; i0 ++, i1 += di1) for (j0 = j1 = 0; j0 < self-> shape1; j0 ++, j1 += dj1) fname<II>(numbytes<TT>::GETWORD(self, i0, j0), numbytes<II>::GETWORD((numbytes<II> *)them, i1, j1));, \
                      for (i0 = i1 = 0; i0 < self-> shape0; i0 ++, i1 += di1) for (j0 = j1 = 0; j0 < self-> shape1; j0 ++, j1 += dj1) fname<FF>(numbytes<TT>::GETWORD(self, i0, j0), numbytes<FF>::GETWORD((numbytes<FF> *)them, i1, j1));, \
                      ); }                                              \
    else throw PYERR(PyExc_TypeError, "invalid operand type <%s>", PYTPNAME(them)); \
    Py_INCREF(self); return self; }                                     \
  PyObject *fname(PyObject *self, PyObject *args) { try {               \
  NUMBYTES_SWITCH(TCODE_SELF(self), self, return fname((numbytes<CC> *)self, args), return fname((numbytes<II> *)self, args), return fname((numbytes<FF> *)self, args),); \
    } catch (...) { return NULL; } }

  // inline CC log2(

  MATH_IOP1(__neg__, *aa = -*aa, *aa = -*aa, *aa = -*aa,);
  MATH_IOP1(__pos__, , , ,);
  MATH_IOP1(__abs__, *aa = abs(*aa), *aa = abs(*aa), *aa = abs(*aa),);
  MATH_IOP1(__invert__, *aa = *aa ^ -1, *aa = *aa ^ -1LL, throw PYERR(PyExc_ArithmeticError, "cannot <~double>"),);
  MATH_IOP1(cos, throw PYERR(PyExc_ArithmeticError, "cannot <cos(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <cos(int64)>"), *aa = std::cos(*aa),);
  MATH_IOP1(sin, throw PYERR(PyExc_ArithmeticError, "cannot <sin(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <sin(int64)>"), *aa = std::sin(*aa),);
  MATH_IOP1(tan, throw PYERR(PyExc_ArithmeticError, "cannot <tan(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <tan(int64)>"), *aa = std::tan(*aa),);
  MATH_IOP1(acos, throw PYERR(PyExc_ArithmeticError, "cannot <acos(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <acos(int64)>"), *aa = std::acos(*aa),);
  MATH_IOP1(asin, throw PYERR(PyExc_ArithmeticError, "cannot <asin(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <asin(int64)>"), *aa = std::asin(*aa),);
  MATH_IOP1(atan, throw PYERR(PyExc_ArithmeticError, "cannot <atan(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <atan(int64)>"), *aa = std::atan(*aa),);
  MATH_IOP1(cosh, throw PYERR(PyExc_ArithmeticError, "cannot <cosh(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <cosh(int64)>"), *aa = std::cosh(*aa),);
  MATH_IOP1(sinh, throw PYERR(PyExc_ArithmeticError, "cannot <sinh(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <sinh(int64)>"), *aa = std::sinh(*aa),);
  MATH_IOP1(tanh, throw PYERR(PyExc_ArithmeticError, "cannot <tanh(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <tanh(int64)>"), *aa = std::tanh(*aa),);
  MATH_IOP1(exp, throw PYERR(PyExc_ArithmeticError, "cannot <exp(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <exp(int64)>"), *aa = std::exp(*aa),);
  MATH_IOP1(log, throw PYERR(PyExc_ArithmeticError, "cannot <log(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <log(int64)>"), *aa = std::log(*aa),);
  // MATH_IOP1(log2, if (*aa <= 0) { *aa = -1; return; } CC ii; for (ii = 0; *aa >>= 1; ii ++); *aa = ii, *aa = *aa <= 0 ? -1 : log64(*aa), *aa = std::log(*aa) * INVLOG2, );
  MATH_IOP1(log2, *aa = *aa <= 0 ? -1 : log64((uch)*aa), *aa = *aa <= 0 ? -1 : log64(*aa), *aa = std::log(*aa) * INVLOG2, );
  MATH_IOP1(log10, throw PYERR(PyExc_ArithmeticError, "cannot <log10(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <log10(int64)>"), *aa = std::log10(*aa),);
  MATH_IOP1(sqrt, throw PYERR(PyExc_ArithmeticError, "cannot <sqrt(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <sqrt(int64)>"), *aa = std::sqrt(*aa),);
  MATH_IOP1(ceil, throw PYERR(PyExc_ArithmeticError, "cannot <ceil(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <ceil(int64)>"), *aa = std::ceil(*aa),);
  MATH_IOP1(floor, throw PYERR(PyExc_ArithmeticError, "cannot <floor(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <floor(int64)>"), *aa = std::floor(*aa),);
  MATH_IOP1(popcount, *aa = popcount64((uch)*aa), *aa = popcount64(*aa), throw PYERR(PyExc_ArithmeticError, "cannot <popcount(double)>"),);
  MATH_IOP1(round, throw PYERR(PyExc_ArithmeticError, "cannot <round(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <round(int64)>"), *aa = std::floor(*aa + 0.5),);

  MATH_IOP2(__add__, *aa += (CC)*bb, *aa += (II)*bb, *aa += (FF)*bb,);
  MATH_IOP2(__sub__, *aa -= (CC)*bb, *aa -= (II)*bb, *aa -= (FF)*bb,);
  MATH_IOP2(__mul__, *aa *= (CC)*bb, *aa *= (II)*bb, *aa *= (FF)*bb,);
  MATH_IOP2(__truediv__, *aa /= (CC)*bb, *aa /= (II)*bb, *aa /= (FF)*bb,);
  MATH_IOP2(__mod__, *aa %= (CC)*bb, *aa %= (II)*bb, fmod(*aa, (FF)*bb),);
  MATH_IOP2(__pow__, *aa = pow(*aa, (CC)*bb), *aa = pow(*aa, (II)*bb), *aa = pow(*aa, (FF)*bb),);
  MATH_IOP2(__lshift__, *aa <<= (CC)*bb, *aa <<= (II)*bb, throw PYERR(PyExc_ArithmeticError, "cannot <double <<= double>"),);
  MATH_IOP2(__rshift__, *aa >>= (CC)*bb, *aa >>= (II)*bb, throw PYERR(PyExc_ArithmeticError, "cannot <double >>= double>"),);
  MATH_IOP2(__and__, *aa &= (CC)*bb, *aa &= (II)*bb, throw PYERR(PyExc_ArithmeticError, "cannot <double &= double>"),);
  MATH_IOP2(__or__, *aa |= (CC)*bb, *aa |= (II)*bb, throw PYERR(PyExc_ArithmeticError, "cannot <double |= double>"),);
  MATH_IOP2(__xor__, *aa ^= (CC)*bb, *aa ^= (II)*bb, throw PYERR(PyExc_ArithmeticError, "cannot <double ^= double>"),);
  MATH_IOP2(atan2, throw PYERR(PyExc_ArithmeticError, "cannot <atan2(char, char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <atan2(int64, int64)>"), *aa = std::atan2(*aa, (FF)*bb),);

}







#include "_numbytes.hpp"
namespace numbytes {
  PyObject *is_itr(PyObject *self, PyObject *aa) { return PyLong_FromLong(    PyIter_Check(aa)); }
  PyObject *is_map(PyObject *self, PyObject *aa) { return PyLong_FromLong( PyMapping_Check(aa)); }
  PyObject *is_num(PyObject *self, PyObject *aa) { return PyLong_FromLong(  PyNumber_Check(aa)); }
  PyObject *is_numbytes(PyObject *self, PyObject *aa) { return PyLong_FromLong(NUMBYTES::CHECK_NUMBYTES(aa)); }
  PyObject *is_seq(PyObject *self, PyObject *aa) { return PyLong_FromLong(PySequence_Check(aa)); }
  PyObject *refcnt(PyObject *self, PyObject *aa) { return PyLong_FromSsize_t(Py_REFCNT(aa)); }
  PyMethodDef module_method[] = {
    {"is_itr", is_itr, METH_O},
    {"is_map", is_map, METH_O},
    {"is_num", is_num, METH_O},
    {"is_numbytes", is_numbytes, METH_O},
    {"is_seq", is_seq, METH_O},
    {"refcnt", refcnt, METH_O},
    // {"png_read", IMG2TXT::png_read, METH_VARARGS},
    // {"png_write", IMG2TXT::png_write, METH_VARARGS},
    // {"ansi_str", IMG2TXT::ansi_str, METH_O},
    {NULL} // sentinel
  };

  struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_numbytes", // m_name
    NULL, // m_desc
    -1, // m_size
    module_method, // m_method
    NULL, // m_reload
    NULL, // m_traverse
    NULL, // m_clear
    NULL, // m_free
  };

  extern "C" {
    PyObject *PyInit__numbytes(void) {
      PyObject *module = PyModule_Create(&moduledef); if (not module) return NULL;
      // if (not NUMBYTES::numbytes<char>::init(module)) return NULL;
      if (not NUMBYTES::numbytes_init(module)) return NULL;
      // NUMBYTES::numbytes<char>::foo = NULL;
      return module;
    }
  }
}
