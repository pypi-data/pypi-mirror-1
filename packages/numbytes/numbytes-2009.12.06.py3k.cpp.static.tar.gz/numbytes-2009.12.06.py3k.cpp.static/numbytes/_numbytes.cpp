extern "C" {
#include "Python.h" // must be included first
#include "structmember.h" // python struct
#include "png.h" // png
}

#include <cmath>
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
#define SIGN(aa) (aa < 0 ? -1 : aa > 0 ? 1 : 0)
#define SWAP(aa, bb, cc) cc = aa; aa = bb; bb = cc;
#define VSNPRINTF(ss, ll, fmt) char ss[ll]; va_list args; va_start(args, fmt); vsnprintf(ss, ll, fmt, args); va_end(args);
const char *ssformat(const char *fmt, ...) { static VSNPRINTF(ss, 1024, fmt); return ss; }

namespace MATH {
  const double INVLOG2 = 1.0 / log(2.0);
  inline u64 popcount64(u64 aa) {
    aa -= ((aa >> 1) & 0x5555555555555555LLU); // count 2 bit
    aa = (((aa >> 2) & 0x3333333333333333LLU) + (aa & 0x3333333333333333LLU)); // count 4 bit
    aa = (((aa >> 4) + aa) & 0x0f0f0f0f0f0f0f0fLLU); // count 8 bit
    aa += (aa >> 8); aa += (aa >> 16); aa += (aa >> 32); return aa & 0x7f; // count 16/32/64 bit
  }
  inline u64 log64(u64 aa) { aa |= (aa >> 1); aa |= (aa >> 2); aa |= (aa >> 4); aa |= (aa >> 16); aa |= (aa >> 32); return popcount64(aa) - 1; }
  inline double roundeven(double aa) {
    if (aa < 0) return -roundeven(-aa);
    double bb = floor(aa + 0.5);
    if (bb == aa + 0.5) return floor(bb * 0.5) * 2; // round even
    return bb;
  }
}

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
struct PYGETSETDEF: vector<PyGetSetDef> { ~PYGETSETDEF() {} PYGETSETDEF() { resize(1); }
  void add(const char *fname, PyObject *(fnc)(PyObject *, PyObject *)) { insert(begin(), (PyGetSetDef) { (char *)fname, (getter)fnc, }); }
};
struct PYMETHODDEF: vector<PyMethodDef> { ~PYMETHODDEF() {} PYMETHODDEF() { resize(1); }
  void add(const char *fname, PyObject *(fnc)(PyObject *, PyObject *), int flags) { insert(begin(), (PyMethodDef) { fname, (PyCFunction)fnc, flags}); }
};







namespace NUMBYTES {
  //// typedef
  typedef char CC; typedef i64 II; typedef double FF;
  const int tcode_CC='c',tcode_II='i',tcode_FF='f';
  inline int tcode_TT(const CC *tt) { return tcode_CC; }
  inline int tcode_TT(const II *tt) { return tcode_II; }
  inline int tcode_TT(const FF *tt) { return tcode_FF; }

  //// helper
  inline void as_TT(CC *tt, PyObject *oo) { *tt = PyLong_AsLong    (oo); if (*tt == ERROR and PyErr_Occurred()) throw ERROR; }
  inline void as_TT(II *tt, PyObject *oo) { *tt = PyLong_AsLongLong(oo); if (*tt == ERROR and PyErr_Occurred()) throw ERROR; }
  inline void as_TT(FF *tt, PyObject *oo) { *tt = PyFloat_AsDouble (oo); if (*tt == ERROR and PyErr_Occurred()) throw ERROR; }
  inline PyObject *from_TT(const CC *tt) { return PyLong_FromLong    (*tt); }
  inline PyObject *from_TT(const II *tt) { return PyLong_FromLongLong(*tt); }
  inline PyObject *from_TT(const FF *tt) { return PyFloat_FromDouble (*tt); }
  inline void str_TT(const CC *tt, char *&ss) { *ss = *tt < 0 ? '-' : ' '; ss ++; ss += sprintf(ss, "%.2x ", abs(*tt)); }
  inline void str_TT(const II *tt, char *&ss) { static const int ll = 10 + 2; static const i64 mm = pow(10, ll - 2); ss += abs(*tt) < mm ? sprintf(ss, "%*lli ", ll - 1, *tt) : sprintf(ss, "%*.*e ", ll - 1, ll - 8, (double)*tt); }
  inline void str_TT(const FF *tt, char *&ss) { static const int ll = 6 + 8; ss += sprintf(ss, "%*.*g ", ll - 1, ll - 8, *tt); }

  //// struct
  template<typename TT> struct numbytes;
  PyTypeObject TYPE = {PyVarObject_HEAD_INIT(NULL, 0)"_numbytes",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  inline int CHECK_NUMBYTES(PyObject *self) { return PyObject_TypeCheck(self, &TYPE); }
  PySequenceMethods PYSEQUENCE = {NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,};
  PYGETSETDEF GETSET; PYMETHODDEF METHOD;

  //// template
  template<typename TT> struct numbytes: PyObject { int tcode; PyObject *bytes; TT *words; int shape0, shape1, strides0, strides1;
#define NUMBYTES_METH
#define NUMBYTES_TT(TT, self) ((numbytes<TT> *)self)
#define NUMBYTES_LOOP1(self) for (int i0 = 0, j0 = 0; i0 < (self)-> shape0; i0 ++) for (j0 = 0; j0 < (self)-> shape1; j0 ++)
#define NUMBYTES_LOOP2(self, them1) (self)-> CHECK_SHAPE(them1); for (int i0 = 0, j0 = 0, i1 = 0, j1 = 0, di1 = (them1)-> shape0 == 1 ? 0 : 1, dj1 = (them1)-> shape1 == 1 ? 0 : 1; i0 < (self)-> shape0; i0 ++, i1 += di1) for (j0 = j1 = 0; j0 < (self)-> shape1; j0 ++, j1 += dj1)
#define NUMBYTES_LOOP3(self, them1, them2) (self)-> CHECK_SHAPE(them1); (self)-> CHECK_SHAPE(them2); for (int i0 = 0, j0 = 0, i1 = 0, j1 = 0, i2 = 0, j2 = 0, di1 = (them1)-> shape0 == 1 ? 0 : 1, dj1 = (them1)-> shape1 == 1 ? 0 : 1, di2 = (them2)-> shape0 == 1 ? 0 : 1, dj2 = (them2)-> shape1 == 1 ? 0 : 1; i0 < (self)-> shape0; i0 ++, i1 += di1, i2 += di2) for (j0 = j1 = j2 = 0; j0 < (self)-> shape1; j0 ++, j1 += dj1, j2 += dj2)
#define NUMBYTES_SWITCH(tcode, check, cc, ii, ff, _) switch (tcode) {   \
    case tcode_CC: if (check and CHECK_NUMBYTES(check)) NUMBYTES_TT(CC, check)-> CHECK_MEM(); cc; break; \
    case tcode_II: if (check and CHECK_NUMBYTES(check)) NUMBYTES_TT(II, check)-> CHECK_MEM(); ii; break; \
    case tcode_FF: if (check and CHECK_NUMBYTES(check)) NUMBYTES_TT(FF, check)-> CHECK_MEM(); ff; break; \
    default: throw PYERR(PyExc_ValueError, "invalid tcode <%c>", tcode); }

    inline int CHECK_IDX0(int idx) { if ((idx < 0 ? idx += shape0 : idx) < 0 or shape0 <= idx) throw PYERR(PyExc_IndexError, "index0 <%i> out of range", idx); return idx; }
    inline int CHECK_IDX1(int idx) { if ((idx < 0 ? idx += shape1 : idx) < 0 or shape1 <= idx) throw PYERR(PyExc_IndexError, "index1 <%i> out of range", idx); return idx; }
    inline void CHECK_MEM() { if (words < BYTES(bytes) or PyObject_Size(bytes) < (words - BYTES(bytes)) + shape0 * shape1) throw PYERR(PyExc_MemoryError, "numbytes memory invalidated"); }
    template <typename UU> inline void CHECK_SHAPE(numbytes<UU> *them) {
      if ((them-> shape0 != 1 and them-> shape0 != shape0) or (them-> shape1 != 1 and them-> shape1 != shape1)) throw PYERR(PyExc_IndexError, "incompatible shape0 - self <%i %i> vs them <%i %i>", shape0, shape1, them-> shape0, them-> shape1);
    }
    template <typename UU> inline void CHECK_TCODE(numbytes<UU> *them) { if (them -> tcode != tcode) throw pyerr(PyExc_TypeError, "incompatible tcode self <%c> vs them <%c>", tcode, them -> tcode); }
    inline static TT *BYTES(PyObject *bytes) { return (TT *)PyByteArray_AS_STRING(bytes); }
    inline int CONTIGUOUS() { return strides1 == 1 and BYTES(bytes) == words; }
    inline TT *GETWORD(int ii, int jj) { return words + ii * strides0 + jj * strides1; }
    inline int LENGTH() { return shape0 * shape1; }
    inline int TRANSPOSED() { return strides1 != 1; }
    inline static int TSIZE() { return sizeof(TT); }

    //// constructor
    static void numbytes_dealloc(numbytes *self, PyObject *args) { Py_DECREF(self-> bytes); Py_TYPE(self)-> tp_free(self); }
    static numbytes<TT> *numbytes_new(PyTypeObject *type, int tcode, PyObject *bytes, TT *words, int shape0, int shape1, int strides0, int strides1) {
      numbytes *self = (numbytes *)type-> tp_alloc(type, 0); if (not self) throw ERROR;
      self-> tcode = tcode; self-> bytes = bytes; self-> words = words; self-> shape0 = shape0; self-> shape1 = shape1; self-> strides0 = strides0; self-> strides1 = strides1; Py_INCREF(bytes); return self;
    }
    static PyObject *numbytes_new(numbytes<TT> *type, PyObject *args) {
      static const TT *tt; PyObject *tcode, *bytes; if (not PyArg_ParseTuple(args, "OO:numbytes_new", &tcode, &bytes)) throw ERROR;
      if (not PyByteArray_Check(bytes)) throw PYERR(PyExc_TypeError, "not bytearray type <%s>", PYTPNAME(bytes));
      int ll = PyObject_Size(bytes); if (ll % TSIZE()) throw PYERR(PyExc_IndexError, "bytearray size <%i> not multiple of tsize <%i>", ll, TSIZE());
      ll /= TSIZE(); return numbytes_new((PyTypeObject *)type, tcode_TT(tt), bytes, BYTES(bytes), 1, ll, ll, 1);
    }
    static PyObject *__str__(numbytes *self, PyObject *args) {
      char ss[self-> LENGTH() * 16 + 1]; char *tt = ss; NUMBYTES_LOOP1(self) str_TT(self-> GETWORD(i0, j0), tt);
      return PyUnicode_FromStringAndSize(ss, tt - ss);
    }
    NUMBYTES_METH static PyObject *static_tsize_from_tcode(PyObject *_, PyObject *args) { return PyLong_FromLong(TSIZE()); }

    //// sequence
    static int sq_length(numbytes *self, PyObject *args) { return self-> LENGTH(); }
    static int sq_contains(numbytes *self, PyObject *aa) { TT bb; as_TT(&bb, aa); NUMBYTES_LOOP1(self) if (*self-> GETWORD(i0, j0) == bb) return true; return false; }
    static PyObject *sq_item(numbytes *self, PyObject *args) { ssz ii = (ssz)args; if (ii >= self-> LENGTH()) throw ERROR; return from_TT(self-> GETWORD(ii / self-> shape1, ii % self-> shape1)); }
    inline static void PARSE_SLICE(numbytes *self, int ii, PyObject *slice, ssz *start, ssz *stop, ssz *step, ssz *slicelength) {
      if (PyLong_Check(slice)) { *start = ii ? self-> CHECK_IDX1(PyLong_AsLong(slice)) : self-> CHECK_IDX0(PyLong_AsLong(slice)); *stop = *start + 1; *step = 1; *slicelength = 1; }
      else if (PySlice_Check(slice)) { if (PySlice_GetIndicesEx((PySliceObject *)slice, ii ? self-> shape1 : self-> shape0, start, stop, step, slicelength) == ERROR) throw ERROR; }
      else throw PYERR(PyExc_TypeError, "invalid index%i type <%s>", ii, PYTPNAME(slice));
    }
    NUMBYTES_METH static PyObject *_getitem(numbytes *self, PyObject *args) {
      int ii, jj; if (PyArg_ParseTuple(args, "ii:_getitem", &ii, &jj)) { return from_TT(self-> GETWORD(self-> CHECK_IDX0(ii), self-> CHECK_IDX1(jj))); } else { PyErr_Clear(); }
      PyObject *slice0 = NULL, *slice1 = NULL; if (not PyArg_ParseTuple(args, "OO:_getitem", &slice0, &slice1)) throw ERROR;
      ssz start0, stop0, step0, slicelength0; PARSE_SLICE(self, 0, slice0, &start0, &stop0, &step0, &slicelength0);
      ssz start1, stop1, step1, slicelength1; PARSE_SLICE(self, 1, slice1, &start1, &stop1, &step1, &slicelength1);
      return numbytes_new(Py_TYPE(self), self-> tcode, self-> bytes, self-> GETWORD(start0, start1), slicelength0, slicelength1, step0 * self-> strides0, step1 * self-> strides1);
    }
    template<typename UU> inline static void SETSLICE(numbytes *self, numbytes<UU> *them) { NUMBYTES_LOOP2(self, them) *self-> GETWORD(i0, j0) = (TT)*them-> GETWORD(i1, j1); }
    NUMBYTES_METH static PyObject *_setitem(numbytes *self, PyObject *args) {
      PyObject *slices; numbytes<TT> *them; if (not PyArg_ParseTuple(args, "OO:__setitem__", &slices, &them)) throw ERROR;
      int ii, jj; if (PyArg_ParseTuple(slices, "ii:__setitem__", &ii, &jj)) { as_TT(self-> GETWORD(ii, jj), them); Py_RETURN_NONE; } else { PyErr_Clear(); }
      self = (numbytes *) _getitem(self, slices);
      try {
        if (PyNumber_Check(them)) { TT bb; as_TT(&bb, them); NUMBYTES_LOOP1(self) *self-> GETWORD(i0, j0) = bb; } // number
        else if (CHECK_NUMBYTES(them)) { NUMBYTES_SWITCH(them-> tcode, them, SETSLICE(self, NUMBYTES_TT(CC, them)), SETSLICE(self, NUMBYTES_TT(II, them)), SETSLICE(self, NUMBYTES_TT(FF, them)),); }
        else throw PYERR(PyExc_TypeError, "invalid setitem type <%s>", PYTPNAME(them));
        Py_DECREF(self); Py_RETURN_NONE;
      } catch (...) { Py_DECREF(self); throw; }
    }

    //// getset
    NUMBYTES_METH static PyObject *get_base(numbytes *self, PyObject *closure) { return numbytes_new(&TYPE, self-> tcode, self-> bytes, self-> words, self-> shape0, self-> shape1, self-> strides0, self-> strides1); }
    NUMBYTES_METH static PyObject *get_bytes(numbytes *self, PyObject *closure) { Py_INCREF(self-> bytes); return self-> bytes; }
    NUMBYTES_METH static PyObject *get_contiguous(numbytes *self, PyObject *closure) { return PyLong_FromLong(self-> CONTIGUOUS()); }
    NUMBYTES_METH static PyObject *get_shape0(numbytes *self, PyObject *closure) { return PyLong_FromLong(self-> shape0); }
    NUMBYTES_METH static PyObject *get_shape1(numbytes *self, PyObject *closure) { return PyLong_FromLong(self-> shape1); }
    NUMBYTES_METH static PyObject *get_strides0(numbytes *self, PyObject *closure) { return PyLong_FromLong(self-> strides0); }
    NUMBYTES_METH static PyObject *get_strides1(numbytes *self, PyObject *closure) { return PyLong_FromLong(self-> strides1); }
    NUMBYTES_METH static PyObject *get_T(numbytes *self, PyObject *closure) { return numbytes_new(Py_TYPE(self), self-> tcode, self-> bytes, self-> words, self-> shape1, self-> shape0, self-> strides1, self-> strides0); }
    NUMBYTES_METH static PyObject *get_tcode(numbytes *self, PyObject *closure) { return PyUnicode_FromFormat("%c", self-> tcode); }
    NUMBYTES_METH static PyObject *get_transposed(numbytes *self, PyObject *closure) { return PyLong_FromLong(self-> TRANSPOSED()); }
    NUMBYTES_METH static PyObject *get_tsize(numbytes *self, PyObject *closure) { return PyLong_FromLong(TSIZE()); }

    //// method
    template <typename UU> inline static void copy_to(numbytes *self, numbytes<UU> *them) { NUMBYTES_LOOP2(self, them) *them-> GETWORD(i1, j1) = (UU)*self-> GETWORD(i0, j0); }
    NUMBYTES_METH static PyObject *copy_to(numbytes *self, PyObject *args) {
      numbytes<TT> *them; if (not PyArg_ParseTuple(args, "O:copy_to", &them)) throw ERROR;
      NUMBYTES_SWITCH(them-> tcode, them, copy_to(self, NUMBYTES_TT(CC, them)), copy_to(self, NUMBYTES_TT(II, them)), copy_to(self, NUMBYTES_TT(FF, them)),);
      Py_INCREF(them); return them;
    }
    NUMBYTES_METH static PyObject *fill_from_itr(numbytes *self, PyObject *args) {
      PyObject *itr, *aa; if (not PyArg_ParseTuple(args, "O:fill_from_itr", &itr)) throw ERROR;
      try {
        if (PyIter_Check(itr)) {
          NUMBYTES_LOOP1(self) {
            if (not (aa = PyIter_Next(itr))) Py_RETURN_NONE;
            as_TT(self-> GETWORD(i0, j0), aa);
            Py_XDECREF(aa);
          }
        }
        else throw PYERR(PyExc_TypeError, "invalid fill type <%s>", PYTPNAME(itr));
        Py_INCREF(self); return self;
      } catch (...) { Py_XDECREF(aa); throw; }
    }
    NUMBYTES_METH static PyObject *reshape(numbytes *self, PyObject *args) {
      int ll, mm; if (not PyArg_ParseTuple(args, "ii:reshape", &ll, &mm)) throw ERROR;
      if (not self-> CONTIGUOUS()) throw PYERR(PyExc_IndexError, "cannot reshape non-contiguous numbytes");
      if (ll == -1) ll = self-> LENGTH() / mm; else if (mm == -1) mm = self-> LENGTH() / ll;
      if (ll < 0 or ll * mm != self-> LENGTH()) throw PYERR(PyExc_IndexError, "invalid reshape <%i %i>-> <%i %i>", self-> shape0, self-> shape1, ll, mm);
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
  inline int TCODE_SELF(PyObject *self) { return NUMBYTES_TT(CC, self)-> tcode; }

#undef NUMBYTES_METH
#define NUMBYTES_METH(rtype, fnc, err, tcode) rtype fnc(PyObject *self, PyObject *args) { try { \
      NUMBYTES_SWITCH(tcode, self,                                      \
                      return numbytes<CC>::fnc(NUMBYTES_TT(CC, self), args);, \
                      return numbytes<II>::fnc(NUMBYTES_TT(II, self), args);, \
                      return numbytes<FF>::fnc(NUMBYTES_TT(FF, self), args);, \
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
#define MATH_IOP1(fname, cc, ii, ff, _) inline void fname(CC *aa) { cc; }; inline void fname(II *aa) { ii; }; inline void fname(FF *aa) { ff; }; \
  PyObject *fname(PyObject *self, PyObject *args) { try {               \
      if (not PyArg_ParseTuple(args, ":MATH_IOP1")) throw ERROR;        \
      NUMBYTES_SWITCH(TCODE_SELF(self), self,                           \
                      NUMBYTES_LOOP1(NUMBYTES_TT(CC, self)) fname((NUMBYTES_TT(CC, self))-> GETWORD(i0, j0));, \
                      NUMBYTES_LOOP1(NUMBYTES_TT(II, self)) fname((NUMBYTES_TT(II, self))-> GETWORD(i0, j0));, \
                      NUMBYTES_LOOP1(NUMBYTES_TT(FF, self)) fname((NUMBYTES_TT(FF, self))-> GETWORD(i0, j0));, \
                      ); } catch (...) { return NULL; } Py_INCREF(self); return self; }
#define MATH_IOP2(fname, cc, ii, ff, _) template<typename UU> inline void fname(CC *aa, UU *bb) { cc; }; template<typename UU> inline void fname(II *aa, UU *bb) { ii; }; template<typename UU> inline void fname(FF *aa, UU *bb) { ff; }; \
  template<typename TT> void fname(numbytes<TT> *self, numbytes<CC> *them1) { \
    if (PyNumber_Check(them1)) { TT uu; as_TT(&uu, them1); NUMBYTES_LOOP1(self) fname(self-> GETWORD(i0, j0), &uu); } \
    else if (CHECK_NUMBYTES(them1)) {                                    \
      NUMBYTES_SWITCH(them1-> tcode, them1,                               \
                      NUMBYTES_LOOP2(self, them1) fname(self-> GETWORD(i0, j0), NUMBYTES_TT(CC, them1)-> GETWORD(i1, j1)), \
                      NUMBYTES_LOOP2(self, them1) fname(self-> GETWORD(i0, j0), NUMBYTES_TT(II, them1)-> GETWORD(i1, j1)), \
                      NUMBYTES_LOOP2(self, them1) fname(self-> GETWORD(i0, j0), NUMBYTES_TT(FF, them1)-> GETWORD(i1, j1)), \
                      ); }                                              \
    else throw PYERR(PyExc_TypeError, "invalid operand type <%s>", PYTPNAME(them1)); } \
  PyObject *fname(PyObject *self, PyObject *args) { try {               \
      numbytes<CC> *them1; if (not PyArg_ParseTuple(args, "O:MATH_IOP2", &them1)) throw ERROR; \
      NUMBYTES_SWITCH(TCODE_SELF(self), self, fname(NUMBYTES_TT(CC, self), them1), fname(NUMBYTES_TT(II, self), them1), fname(NUMBYTES_TT(FF, self), them1),); \
      Py_INCREF(self); return self; } catch (...) { return NULL; } }
#define MATH_IOP3_(UU, fname)                                           \
  NUMBYTES_SWITCH(them2-> tcode, them2,                                 \
                  NUMBYTES_LOOP3(self, them1, them2) fname(self-> GETWORD(i0, j0), NUMBYTES_TT(UU, them1)-> GETWORD(i1, j1), NUMBYTES_TT(CC, them2)-> GETWORD(i2, j2)), \
                  NUMBYTES_LOOP3(self, them1, them2) fname(self-> GETWORD(i0, j0), NUMBYTES_TT(UU, them1)-> GETWORD(i1, j1), NUMBYTES_TT(II, them2)-> GETWORD(i2, j2)), \
                  NUMBYTES_LOOP3(self, them1, them2) fname(self-> GETWORD(i0, j0), NUMBYTES_TT(UU, them1)-> GETWORD(i1, j1), NUMBYTES_TT(FF, them2)-> GETWORD(i2, j2)),)
#define MATH_IOP3(fname, dd, ii, ff, _)                                 \
  inline void fname(CC *aa, CC *bb, CC *cc) { dd; } inline void fname(CC *aa, CC *bb, II *cc) { dd; } inline void fname(CC *aa, CC *bb, FF *cc) { dd; } \
  inline void fname(CC *aa, II *bb, CC *cc) { dd; } inline void fname(CC *aa, II *bb, II *cc) { dd; } inline void fname(CC *aa, II *bb, FF *cc) { dd; } \
  inline void fname(CC *aa, FF *bb, CC *cc) { dd; } inline void fname(CC *aa, FF *bb, II *cc) { dd; } inline void fname(CC *aa, FF *bb, FF *cc) { dd; } \
  inline void fname(II *aa, CC *bb, CC *cc) { ii; } inline void fname(II *aa, CC *bb, II *cc) { ii; } inline void fname(II *aa, CC *bb, FF *cc) { ii; } \
  inline void fname(II *aa, II *bb, CC *cc) { ii; } inline void fname(II *aa, II *bb, II *cc) { ii; } inline void fname(II *aa, II *bb, FF *cc) { ii; } \
  inline void fname(II *aa, FF *bb, CC *cc) { ii; } inline void fname(II *aa, FF *bb, II *cc) { ii; } inline void fname(II *aa, FF *bb, FF *cc) { ii; } \
  inline void fname(FF *aa, CC *bb, CC *cc) { ff; } inline void fname(FF *aa, CC *bb, II *cc) { ff; } inline void fname(FF *aa, CC *bb, FF *cc) { ff; } \
  inline void fname(FF *aa, II *bb, CC *cc) { ff; } inline void fname(FF *aa, II *bb, II *cc) { ff; } inline void fname(FF *aa, II *bb, FF *cc) { ff; } \
  inline void fname(FF *aa, FF *bb, CC *cc) { ff; } inline void fname(FF *aa, FF *bb, II *cc) { ff; } inline void fname(FF *aa, FF *bb, FF *cc) { ff; } \
  template<typename TT> void fname(numbytes<TT> *self, numbytes<CC> *them1, numbytes<CC> *them2) { \
    if (PyNumber_Check(them1)) { TT uu; as_TT(&uu, them1);              \
      if (PyNumber_Check(them2)) { TT vv; as_TT(&vv, them2); NUMBYTES_LOOP1(self) fname(self-> GETWORD(i0, j0), &uu, &vv); } \
      else if (CHECK_NUMBYTES(them1)) {                                 \
        NUMBYTES_SWITCH(them2-> tcode, them2,                           \
                        NUMBYTES_LOOP2(self, them2) fname(self-> GETWORD(i0, j0), &uu, NUMBYTES_TT(CC, them2)-> GETWORD(i1, j1)), \
                        NUMBYTES_LOOP2(self, them2) fname(self-> GETWORD(i0, j0), &uu, NUMBYTES_TT(II, them2)-> GETWORD(i1, j1)), \
                        NUMBYTES_LOOP2(self, them2) fname(self-> GETWORD(i0, j0), &uu, NUMBYTES_TT(FF, them2)-> GETWORD(i1, j1)), \
                        ); }                                            \
      else throw PYERR(PyExc_TypeError, "invalid operand type <%s>", PYTPNAME(them2)); } \
    else if (CHECK_NUMBYTES(them1)) {                                   \
      if (PyNumber_Check(them2)) { TT vv; as_TT(&vv, them2);            \
        NUMBYTES_SWITCH(them1-> tcode, them1,                           \
                        NUMBYTES_LOOP2(self, them1) fname(self-> GETWORD(i0, j0), NUMBYTES_TT(CC, them1)-> GETWORD(i1, j1), &vv), \
                        NUMBYTES_LOOP2(self, them1) fname(self-> GETWORD(i0, j0), NUMBYTES_TT(II, them1)-> GETWORD(i1, j1), &vv), \
                        NUMBYTES_LOOP2(self, them1) fname(self-> GETWORD(i0, j0), NUMBYTES_TT(FF, them1)-> GETWORD(i1, j1), &vv), \
                        ); }                                            \
      else if (CHECK_NUMBYTES(them2)) { NUMBYTES_SWITCH(them1-> tcode, them1, MATH_IOP3_(CC, fname), MATH_IOP3_(II, fname), MATH_IOP3_(FF, fname),); }\
      else throw PYERR(PyExc_TypeError, "invalid operand type <%s>", PYTPNAME(them2)); } \
    else throw PYERR(PyExc_TypeError, "invalid operand type <%s>", PYTPNAME(them1)); } \
  PyObject *fname(PyObject *self, PyObject *args) { try {               \
      numbytes<CC> *them1, *them2; if (not PyArg_ParseTuple(args, "OO:MATH_IOP3", &them1, &them2)) throw ERROR; \
      NUMBYTES_SWITCH(TCODE_SELF(self), self, fname(NUMBYTES_TT(CC, self), them1, them2), fname(NUMBYTES_TT(II, self), them1, them2), fname(NUMBYTES_TT(FF, self), them1, them2),); \
      Py_INCREF(self); return self; } catch (...) { return NULL; } }

  MATH_IOP1(math___neg__, *aa = -*aa, *aa = -*aa, *aa = -*aa,);
  MATH_IOP1(math___pos__, , , ,);
  MATH_IOP1(math___abs__, *aa = abs(*aa), *aa = abs(*aa), *aa = abs(*aa),);
  MATH_IOP1(math___invert__, *aa = *aa ^ -1, *aa = *aa ^ -1LL, throw PYERR(PyExc_ArithmeticError, "cannot <~double>"),);
  MATH_IOP1(math_cos, throw PYERR(PyExc_ArithmeticError, "cannot <cos(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <cos(int64)>"), *aa = cos(*aa),);
  MATH_IOP1(math_sin, throw PYERR(PyExc_ArithmeticError, "cannot <sin(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <sin(int64)>"), *aa = sin(*aa),);
  MATH_IOP1(math_tan, throw PYERR(PyExc_ArithmeticError, "cannot <tan(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <tan(int64)>"), *aa = tan(*aa),);
  MATH_IOP1(math_acos, throw PYERR(PyExc_ArithmeticError, "cannot <acos(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <acos(int64)>"), *aa = acos(*aa),);
  MATH_IOP1(math_asin, throw PYERR(PyExc_ArithmeticError, "cannot <asin(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <asin(int64)>"), *aa = asin(*aa),);
  MATH_IOP1(math_atan, throw PYERR(PyExc_ArithmeticError, "cannot <atan(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <atan(int64)>"), *aa = atan(*aa),);
  MATH_IOP1(math_cosh, throw PYERR(PyExc_ArithmeticError, "cannot <cosh(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <cosh(int64)>"), *aa = cosh(*aa),);
  MATH_IOP1(math_sinh, throw PYERR(PyExc_ArithmeticError, "cannot <sinh(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <sinh(int64)>"), *aa = sinh(*aa),);
  MATH_IOP1(math_tanh, throw PYERR(PyExc_ArithmeticError, "cannot <tanh(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <tanh(int64)>"), *aa = tanh(*aa),);
  MATH_IOP1(math_exp, throw PYERR(PyExc_ArithmeticError, "cannot <exp(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <exp(int64)>"), *aa = exp(*aa),);
  MATH_IOP1(math_log, throw PYERR(PyExc_ArithmeticError, "cannot <log(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <log(int64)>"), *aa = log(*aa),);
  MATH_IOP1(math_log10, throw PYERR(PyExc_ArithmeticError, "cannot <log10(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <log10(int64)>"), *aa = log10(*aa),);
  MATH_IOP1(math_sqrt, throw PYERR(PyExc_ArithmeticError, "cannot <sqrt(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <sqrt(int64)>"), *aa = sqrt(*aa),);
  MATH_IOP1(math_ceil, throw PYERR(PyExc_ArithmeticError, "cannot <ceil(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <ceil(int64)>"), *aa = ceil(*aa),);
  MATH_IOP1(math_floor, throw PYERR(PyExc_ArithmeticError, "cannot <floor(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <floor(int64)>"), *aa = floor(*aa),);
  MATH_IOP1(math_log2, *aa = *aa <= 0 ? -1 : MATH::log64((uch)*aa), *aa = *aa <= 0 ? -1 : MATH::log64(*aa), *aa = log(*aa) * MATH::INVLOG2, );
  MATH_IOP1(math_popcount, *aa = MATH::popcount64((uch)*aa), *aa = MATH::popcount64(*aa), throw PYERR(PyExc_ArithmeticError, "cannot <popcount(double)>"),);
  MATH_IOP1(math_roundeven, throw PYERR(PyExc_ArithmeticError, "cannot <roundeven(char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <roundeven(int64)>"), *aa = MATH::roundeven(*aa),);
  MATH_IOP1(math_sign, *aa = SIGN(*aa), *aa = SIGN(*aa), *aa = SIGN(*aa),);

  MATH_IOP2(math___add__, *aa += (CC)*bb, *aa += (II)*bb, *aa += (FF)*bb,);
  MATH_IOP2(math___sub__, *aa -= (CC)*bb, *aa -= (II)*bb, *aa -= (FF)*bb,);
  MATH_IOP2(math___mul__, *aa *= (CC)*bb, *aa *= (II)*bb, *aa *= (FF)*bb,);
  MATH_IOP2(math___truediv__, *aa /= (CC)*bb, *aa /= (II)*bb, *aa /= (FF)*bb,);
  MATH_IOP2(math___mod__, *aa %= (CC)*bb, *aa %= (II)*bb, fmod(*aa, (FF)*bb),);
  MATH_IOP2(math___pow__, *aa = pow(*aa, (CC)*bb), *aa = pow(*aa, (II)*bb), *aa = pow(*aa, (FF)*bb),);
  MATH_IOP2(math___lshift__, *aa <<= (CC)*bb, *aa <<= (II)*bb, throw PYERR(PyExc_ArithmeticError, "cannot <double <<= double>"),);
  MATH_IOP2(math___rshift__, *aa >>= (CC)*bb, *aa >>= (II)*bb, throw PYERR(PyExc_ArithmeticError, "cannot <double >>= double>"),);
  MATH_IOP2(math___and__, *aa &= (CC)*bb, *aa &= (II)*bb, throw PYERR(PyExc_ArithmeticError, "cannot <double &= double>"),);
  MATH_IOP2(math___or__, *aa |= (CC)*bb, *aa |= (II)*bb, throw PYERR(PyExc_ArithmeticError, "cannot <double |= double>"),);
  MATH_IOP2(math___xor__, *aa ^= (CC)*bb, *aa ^= (II)*bb, throw PYERR(PyExc_ArithmeticError, "cannot <double ^= double>"),);
  MATH_IOP2(math_atan2, throw PYERR(PyExc_ArithmeticError, "cannot <atan2(char, char)>"), throw PYERR(PyExc_ArithmeticError, "cannot <atan2(int64, int64)>"), *aa = atan2(*aa, (FF)*bb),);

  MATH_IOP3(math___eq__, *aa = *bb == *cc, *aa = *bb == *cc, *aa = *bb == *cc,);
  MATH_IOP3(math___ne__, *aa = *bb != *cc, *aa = *bb != *cc, *aa = *bb != *cc,);
  MATH_IOP3(math___lt__, *aa = *bb <  *cc, *aa = *bb <  *cc, *aa = *bb <  *cc,);
  MATH_IOP3(math___le__, *aa = *bb <= *cc, *aa = *bb <= *cc, *aa = *bb <= *cc,);
  MATH_IOP3(math___gt__, *aa = *bb >  *cc, *aa = *bb >  *cc, *aa = *bb >  *cc,);
  MATH_IOP3(math___ge__, *aa = *bb >= *cc, *aa = *bb >= *cc, *aa = *bb >= *cc,);
  MATH_IOP3(math_fma, *aa = fma(*bb, *cc, *aa), *aa = fma(*bb, *cc, *aa), *aa = fma(*bb, *cc, *aa),);
}







namespace IMG2TXT {
  const i64 FBMP0[256] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0x100104104100LL,0xa28aLL,0x1457caf94500LL,0x43d450c1c5784LL,0x46a50c295880LL,0x799b6638a100LL,0x4104LL,0x30204104104230LL,0x3108208208103LL,0xa19b100LL,0x1047c4100000LL,0x10830c000000000LL,0x1e000000LL,0x30c000000000LL,0x108210c210420LL,0x391451451380LL,0x7c4104105180LL,0x782108410380LL,0x39040c410780LL,0x2087c928c200LL,0x39040e082780LL,0x3914cd042700LL,0x82104210780LL,0x39144e251380LL,0x1c841e451380LL,0x30c00c300000LL,0x10830c00c300000LL,0x40c0cc400000LL,0x3f03f000000LL,0x46606040000LL,0x100108412780LL,0x781f55751780LL,0x85279228c300LL,0x3d144f4513c0LL,0x702041042700LL,0x3d14514513c0LL,0x78208e082780LL,0x8208e082780LL,0x712459042700LL,0x45145f451440LL,0x7c41041047c0LL,0x188208208380LL,0x449143149440LL,0x782082082080LL,0x4555576db440LL,0x4596555d3440LL,0x391451451380LL,0x4104f4513c0LL,0x30391451451380LL,0x4491472491c0LL,0x39040c082700LL,0x1041041047c0LL,0x391451451440LL,0x10c292491840LL,0x28a3d5555440LL,0x852308312840LL,0x10410428a440LL,0x7c10842107c0LL,0x1c10410410411cLL,0x20410204102081LL,0xe20820820820eLL,0x1128a284100LL,0x3f000000000000LL,0x204LL,0xf92710380000LL,0x3d1453341041LL,0x781041780000LL,0x599451790410LL,0x7817d1380000LL,0x104104784118LL,0x390599451780000LL,0x451453741041LL,0x208208380008LL,0x1c8208208380008LL,0x48a18a482082LL,0x104104104107LL,0x5555557c0000LL,0x451453740000LL,0x391451380000LL,0x413d1453340000LL,0x410599451780000LL,0x82096680000LL,0x390302700000LL,0x604104784100LL,0x5d9451440000LL,0x10a28a440000LL,0x492b6d940000LL,0x44a10a440000LL,0xc430c492840000LL,0x7c21087c0000LL,0x1c10410210411cLL,0x4104104104104LL,0xe20821020820eLL,0xe67000000LL,0x0LL,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0xfffffffffffffffLL,0xfffeffefbefbeffLL,0xfffffffffff5d75LL,0xfffeba83506baffLL,0xffbc2baf3e3a87bLL,0xfffb95af3d6a77fLL,0xfff866499c75effLL,0xfffffffffffbefbLL,0xfcfdfbefbefbdcfLL,0xffcef7df7df7efcLL,0xffffffff5e64effLL,0xfffefb83befffffLL,0xef7cf3fffffffffLL,0xfffffffe1ffffffLL,0xfffcf3fffffffffLL,0xffef7def3defbdfLL,0xfffc6ebaebaec7fLL,0xfff83befbefae7fLL,0xfff87def7befc7fLL,0xfffc6fbf3bef87fLL,0xfffdf7836d73dffLL,0xfffc6fbf1f7d87fLL,0xfffc6eb32fbd8ffLL,0xffff7defbdef87fLL,0xfffc6ebb1daec7fLL,0xfffe37be1baec7fLL,0xfffcf3ff3cfffffLL,0xef7cf3ff3cfffffLL,0xfffbf3f33bfffffLL,0xffffc0fc0ffffffLL,0xffffb99f9fbffffLL,0xfffeffef7bed87fLL,0xfff87e0aa8ae87fLL,0xfff7ad86dd73cffLL,0xfffc2ebb0baec3fLL,0xfff8fdfbefbd8ffLL,0xfffc2ebaebaec3fLL,0xfff87df71f7d87fLL,0xffff7df71f7d87fLL,0xfff8edba6fbd8ffLL,0xfffbaeba0baebbfLL,0xfff83befbefb83fLL,0xfffe77df7df7c7fLL,0xfffbb6ebceb6bbfLL,0xfff87df7df7df7fLL,0xfffbaaaa8924bbfLL,0xfffba69aaa2cbbfLL,0xfffc6ebaebaec7fLL,0xffffbefb0baec3fLL,0xfcfc6ebaebaec7fLL,0xfffbb6eb8db6e3fLL,0xfffc6fbf3f7d8ffLL,0xfffefbefbefb83fLL,0xfffc6ebaebaebbfLL,0xfffef3d6db6e7bfLL,0xfffd75c2aaaabbfLL,0xfff7adcf7ced7bfLL,0xfffefbefbd75bbfLL,0xfff83ef7bdef83fLL,0xfe3efbefbefbee3LL,0xfdfbefdfbefdf7eLL,0xff1df7df7df7df1LL,0xffffeed75d7beffLL,0xfc0ffffffffffffLL,0xffffffffffffdfbLL,0xfff06d8efc7ffffLL,0xfffc2ebaccbefbeLL,0xfff87efbe87ffffLL,0xfffa66bae86fbefLL,0xfff87e82ec7ffffLL,0xfffefbefb87bee7LL,0xc6fa66bae87ffffLL,0xfffbaebac8befbeLL,0xfffdf7df7c7fff7LL,0xe37df7df7c7fff7LL,0xfffb75e75b7df7dLL,0xfffefbefbefbef8LL,0xfffaaaaaa83ffffLL,0xfffbaebac8bffffLL,0xfffc6ebaec7ffffLL,0xfbec2ebaccbffffLL,0xbefa66bae87ffffLL,0xffff7df6997ffffLL,0xfffc6fcfd8fffffLL,0xfff9fbefb87beffLL,0xfffa26baebbffffLL,0xfffef5d75bbffffLL,0xfffb6d4926bffffLL,0xfffbb5ef5bbffffLL,0xf3bcf3b6d7bffffLL,0xfff83def783ffffLL,0xfe3efbefdefbee3LL,0xffbefbefbefbefbLL,0xff1df7defdf7df1LL,0xffffff198ffffffLL,0xfffffffffffffffLL};
  const i64 FBMP1[256] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0x4004104104LL,0x28aLL,0x515f2be514LL,0x10f51430715eLL,0x11a9430a562LL,0x1e66d98e284LL,0x104LL,0xc08104104108LL,0xc4208208204LL,0x2866c4LL,0x411f104000LL,0x420c300000000LL,0x780000LL,0xc300000000LL,0x42084308410LL,0xe45145144eLL,0x1f104104146LL,0x1e08421040eLL,0xe41031041eLL,0x821f24a308LL,0xe41038209eLL,0xe45334109cLL,0x208410841eLL,0xe45138944eLL,0x721079144eLL,0xc30030c000LL,0x420c30030c000LL,0x10303310000LL,0xfc0fc0000LL,0x1198181000LL,0x400421049eLL,0x1e07d55d45eLL,0x2149e48a30cLL,0xf4513d144fLL,0x1c08104109cLL,0xf45145144fLL,0x1e08238209eLL,0x208238209eLL,0x1c49164109cLL,0x114517d1451LL,0x1f10410411fLL,0x620820820eLL,0x112450c5251LL,0x1e082082082LL,0x115555db6d1LL,0x116595574d1LL,0xe45145144eLL,0x10413d144fLL,0xc0e45145144eLL,0x112451c9247LL,0xe41030209cLL,0x410410411fLL,0xe451451451LL,0x430a492461LL,0xa28f555551LL,0x2148c20c4a1LL,0x410410a291LL,0x1f04210841fLL,0x704104104104LL,0x810408104082LL,0x388208208208LL,0x44a28a104LL,0xfc0000000000LL,0x8LL,0x3e49c40e000LL,0xf4514cd041LL,0x1e04105e000LL,0x1665145e410LL,0x1e05f44e000LL,0x410411e104LL,0xe41665145e000LL,0x114514dd041LL,0x820820e000LL,0x720820820e000LL,0x12286292082LL,0x4104104104LL,0x1555555f000LL,0x114514dd000LL,0xe45144e000LL,0x104f4514cd000LL,0x1041665145e000LL,0x208259a000LL,0xe40c09c000LL,0x1810411e104LL,0x17651451000LL,0x428a291000LL,0x124adb65000LL,0x11284291000LL,0x310c3124a1000LL,0x1f08421f000LL,0x704104084104LL,0x104104104104LL,0x388208408208LL,0x399c0000LL,0x0LL,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x3fffffffffffffLL,0x3fffbffbefbefbLL,0x3ffffffffffd75LL,0x3fffaea0d41aebLL,0x3fef0aebcf8ea1LL,0x3ffee56bcf5a9dLL,0x3ffe1992671d7bLL,0x3ffffffffffefbLL,0x3f3f7efbefbef7LL,0x3ff3bdf7df7dfbLL,0x3fffffffd7993bLL,0x3fffbee0efbfffLL,0x3bdf3cffffffffLL,0x3fffffff87ffffLL,0x3fff3cffffffffLL,0x3ffbdf7bcf7befLL,0x3fff1baebaebb1LL,0x3ffe0efbefbeb9LL,0x3ffe1f7bdefbf1LL,0x3fff1befcefbe1LL,0x3fff7de0db5cf7LL,0x3fff1befc7df61LL,0x3fff1baccbef63LL,0x3fffdf7bef7be1LL,0x3fff1baec76bb1LL,0x3fff8def86ebb1LL,0x3fff3cffcf3fffLL,0x3bdf3cffcf3fffLL,0x3ffefcfcceffffLL,0x3ffff03f03ffffLL,0x3fffee67e7efffLL,0x3fffbffbdefb61LL,0x3ffe1f82aa2ba1LL,0x3ffdeb61b75cf3LL,0x3fff0baec2ebb0LL,0x3ffe3f7efbef63LL,0x3fff0baebaebb0LL,0x3ffe1f7dc7df61LL,0x3fffdf7dc7df61LL,0x3ffe3b6e9bef63LL,0x3ffeebae82ebaeLL,0x3ffe0efbefbee0LL,0x3fff9df7df7df1LL,0x3ffeedbaf3adaeLL,0x3ffe1f7df7df7dLL,0x3ffeeaaaa2492eLL,0x3ffee9a6aa8b2eLL,0x3fff1baebaebb1LL,0x3fffefbec2ebb0LL,0x3f3f1baebaebb1LL,0x3ffeedbae36db8LL,0x3fff1befcfdf63LL,0x3fffbefbefbee0LL,0x3fff1baebaebaeLL,0x3fffbcf5b6db9eLL,0x3fff5d70aaaaaeLL,0x3ffdeb73df3b5eLL,0x3fffbefbef5d6eLL,0x3ffe0fbdef7be0LL,0x3f8fbefbefbefbLL,0x3f7efbf7efbf7dLL,0x3fc77df7df7df7LL,0x3ffffbb5d75efbLL,0x3f03ffffffffffLL,0x3ffffffffffff7LL,0x3ffc1b63bf1fffLL,0x3fff0baeb32fbeLL,0x3ffe1fbefa1fffLL,0x3ffe99aeba1befLL,0x3ffe1fa0bb1fffLL,0x3fffbefbee1efbLL,0x31be99aeba1fffLL,0x3ffeebaeb22fbeLL,0x3fff7df7df1fffLL,0x38df7df7df1fffLL,0x3ffedd79d6df7dLL,0x3fffbefbefbefbLL,0x3ffeaaaaaa0fffLL,0x3ffeebaeb22fffLL,0x3fff1baebb1fffLL,0x3efb0baeb32fffLL,0x2fbe99aeba1fffLL,0x3fffdf7da65fffLL,0x3fff1bf3f63fffLL,0x3ffe7efbee1efbLL,0x3ffe89aebaefffLL,0x3fffbd75d6efffLL,0x3ffedb5249afffLL,0x3ffeed7bd6efffLL,0x3cef3cedb5efffLL,0x3ffe0f7bde0fffLL,0x3f8fbefbf7befbLL,0x3fefbefbefbefbLL,0x3fc77df7bf7df7LL,0x3fffffc663ffffLL,0x3fffffffffffffLL};
  const i64 FBMP2[256] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0x4004104104000LL,0x28a280LL,0x515f2be514000LL,0x10f51430715e100LL,0x11a9430a562000LL,0x1e66d98e284000LL,0x104100LL,0xc08104104108c00LL,0xc42082082040c0LL,0x2866c4000LL,0x411f104000000LL,0x20c300000000000LL,0x780000000LL,0xc300000000000LL,0x42084308410800LL,0xe45145144e000LL,0x1f104104146000LL,0x1e08421040e000LL,0xe41031041e000LL,0x821f24a308000LL,0xe41038209e000LL,0xe45334109c000LL,0x208410841e000LL,0xe45138944e000LL,0x721079144e000LL,0xc30030c000000LL,0x20c30030c000000LL,0x10303310000000LL,0xfc0fc0000000LL,0x1198181000000LL,0x400421049e000LL,0x1e07d55d45e000LL,0x2149e48a30c000LL,0xf4513d144f000LL,0x1c08104109c000LL,0xf45145144f000LL,0x1e08238209e000LL,0x208238209e000LL,0x1c49164109c000LL,0x114517d1451000LL,0x1f10410411f000LL,0x620820820e000LL,0x112450c5251000LL,0x1e082082082000LL,0x115555db6d1000LL,0x116595574d1000LL,0xe45145144e000LL,0x10413d144f000LL,0xc0e45145144e000LL,0x112451c9247000LL,0xe41030209c000LL,0x410410411f000LL,0xe451451451000LL,0x430a492461000LL,0xa28f555551000LL,0x2148c20c4a1000LL,0x410410a291000LL,0x1f04210841f000LL,0x704104104104700LL,0x810408104082040LL,0x388208208208380LL,0x44a28a104000LL,0xfc0000000000000LL,0x8100LL,0x3e49c40e000000LL,0xf4514cd041040LL,0x1e04105e000000LL,0x1665145e410400LL,0x1e05f44e000000LL,0x410411e104600LL,0x41665145e000000LL,0x114514dd041040LL,0x820820e000200LL,0x20820820e000200LL,0x12286292082080LL,0x41041041041c0LL,0x1555555f000000LL,0x114514dd000000LL,0xe45144e000000LL,0x4f4514cd000000LL,0x41665145e000000LL,0x208259a000000LL,0xe40c09c000000LL,0x1810411e104000LL,0x17651451000000LL,0x428a291000000LL,0x124adb65000000LL,0x11284291000000LL,0x10c3124a1000000LL,0x1f08421f000000LL,0x704104084104700LL,0x104104104104100LL,0x388208408208380LL,0x399c0000000LL,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0xfffffffffffffc0LL,0xffbffbefbefbfc0LL,0xfffffffffd75d40LL,0xffaea0d41aebfc0LL,0xef0aebcf8ea1ec0LL,0xfee56bcf5a9dfc0LL,0xfe1992671d7bfc0LL,0xfffffffffefbec0LL,0x3f7efbefbef73c0LL,0xf3bdf7df7dfbf00LL,0xffffffd7993bfc0LL,0xffbee0efbffffc0LL,0xdf3cfffffffffc0LL,0xffffff87fffffc0LL,0xff3cfffffffffc0LL,0xfbdf7bcf7bef7c0LL,0xff1baebaebb1fc0LL,0xfe0efbefbeb9fc0LL,0xfe1f7bdefbf1fc0LL,0xff1befcefbe1fc0LL,0xff7de0db5cf7fc0LL,0xff1befc7df61fc0LL,0xff1baccbef63fc0LL,0xffdf7bef7be1fc0LL,0xff1baec76bb1fc0LL,0xff8def86ebb1fc0LL,0xff3cffcf3ffffc0LL,0xdf3cffcf3ffffc0LL,0xfefcfccefffffc0LL,0xfff03f03fffffc0LL,0xffee67e7effffc0LL,0xffbffbdefb61fc0LL,0xfe1f82aa2ba1fc0LL,0xfdeb61b75cf3fc0LL,0xff0baec2ebb0fc0LL,0xfe3f7efbef63fc0LL,0xff0baebaebb0fc0LL,0xfe1f7dc7df61fc0LL,0xffdf7dc7df61fc0LL,0xfe3b6e9bef63fc0LL,0xfeebae82ebaefc0LL,0xfe0efbefbee0fc0LL,0xff9df7df7df1fc0LL,0xfeedbaf3adaefc0LL,0xfe1f7df7df7dfc0LL,0xfeeaaaa2492efc0LL,0xfee9a6aa8b2efc0LL,0xff1baebaebb1fc0LL,0xffefbec2ebb0fc0LL,0x3f1baebaebb1fc0LL,0xfeedbae36db8fc0LL,0xff1befcfdf63fc0LL,0xffbefbefbee0fc0LL,0xff1baebaebaefc0LL,0xffbcf5b6db9efc0LL,0xff5d70aaaaaefc0LL,0xfdeb73df3b5efc0LL,0xffbefbef5d6efc0LL,0xfe0fbdef7be0fc0LL,0x8fbefbefbefb8c0LL,0x7efbf7efbf7df80LL,0xc77df7df7df7c40LL,0xfffbb5d75efbfc0LL,0x3fffffffffffc0LL,0xfffffffffff7ec0LL,0xfc1b63bf1ffffc0LL,0xff0baeb32fbef80LL,0xfe1fbefa1ffffc0LL,0xfe99aeba1befbc0LL,0xfe1fa0bb1ffffc0LL,0xffbefbee1efb9c0LL,0xbe99aeba1ffffc0LL,0xfeebaeb22fbef80LL,0xff7df7df1fffdc0LL,0xdf7df7df1fffdc0LL,0xfedd79d6df7df40LL,0xffbefbefbefbe00LL,0xfeaaaaaa0ffffc0LL,0xfeebaeb22ffffc0LL,0xff1baebb1ffffc0LL,0xfb0baeb32ffffc0LL,0xbe99aeba1ffffc0LL,0xffdf7da65ffffc0LL,0xff1bf3f63ffffc0LL,0xfe7efbee1efbfc0LL,0xfe89aebaeffffc0LL,0xffbd75d6effffc0LL,0xfedb5249affffc0LL,0xfeed7bd6effffc0LL,0xef3cedb5effffc0LL,0xfe0f7bde0ffffc0LL,0x8fbefbf7befb8c0LL,0xefbefbefbefbec0LL,0xc77df7bf7df7c40LL,0xffffc663fffffc0LL,0xfffffffffffffc0LL};
  const i64 FBMP3[256] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0x80082082080LL,0x5145LL,0x823c57ca280LL,0x21ca2860c23c2LL,0x21528614a440LL,0x3cc5931c5080LL,0x2082LL,0x18102082082118LL,0x1084104104081LL,0x50cd080LL,0x823c2080000LL,0x84186000000000LL,0xf000000LL,0x186000000000LL,0x41086108210LL,0x1c82082081c0LL,0x3c20820820c0LL,0x3c10842081c0LL,0x1c82062083c0LL,0x1043c4146100LL,0x1c82070413c0LL,0x1c8246001380LL,0x410821083c0LL,0x1c82071081c0LL,0xc420f2081c0LL,0x186006180000LL,0x84186006180000LL,0x206046200000LL,0x1f01f000000LL,0x3303000000LL,0x800842093c0LL,0x3c078a3883c0LL,0x4093c9146180LL,0x1c82072081c0LL,0x381000001380LL,0x1c82082081c0LL,0x3c10470413c0LL,0x410470413c0LL,0x38920c001380LL,0x20820f208200LL,0x3c20820823c0LL,0xc41041041c0LL,0x204081084200LL,0x3c1041041040LL,0x20a28b34d200LL,0x20c30a2c9200LL,0x1c82082081c0LL,0x72081c0LL,0x181c82082081c0LL,0x2040831040c0LL,0x1c8206041380LL,0x820820823c0LL,0x1c8208208200LL,0x86149248400LL,0x1451ca28a200LL,0x409184189400LL,0x82082145200LL,0x3c00421083c0LL,0xe08208208208eLL,0x10208102081040LL,0x7104104104107LL,0x8145142080LL,0x1f000000000000LL,0x102LL,0x7c93881c0000LL,0x1c8209180000LL,0x3c00003c0000LL,0x2cc2083c8208LL,0x3c03c81c0000LL,0x820823c208cLL,0x1c82cc2083c0000LL,0x208209380000LL,0x1041041c0004LL,0xc41041041c0004LL,0x2450c5241041LL,0x82082082083LL,0x28a28a3c0000LL,0x208209380000LL,0x1c82081c0000LL,0x1c8209180000LL,0x2082cc2083c0000LL,0x4104b340000LL,0x1c8181380000LL,0x3020823c2080LL,0x2cc208200000LL,0x85145200000LL,0x249596480000LL,0x205085200000LL,0x42186249400000LL,0x3c10843c0000LL,0xe08208108208eLL,0x2082082082082LL,0x7104108104107LL,0x713000000LL,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0x7df7df7df7df7dfLL,0x7df75f75d75d75fLL,0x7df7df7df7da69aLL,0x7df75d41a01555fLL,0x7dd61555971d41dLL,0x7df5ca55969539fLL,0x7df41324c61a75fLL,0x7df7df7df7dd75dLL,0x7c76dd75d75d6c7LL,0x7de75b6db6db75eLL,0x7df7df7da71275fLL,0x7df75d41d75f7dfLL,0x75b6597df7df7dfLL,0x7df7df7d07df7dfLL,0x7df6597df7df7dfLL,0x7df79e7596d75cfLL,0x7df6175d75d761fLL,0x7df41d75d75d71fLL,0x7df41e75b5d761fLL,0x7df6175d95d741fLL,0x7df6db41b6996dfLL,0x7df6175d879e41fLL,0x7df6175997de45fLL,0x7df79e75d6d741fLL,0x7df6175d86d761fLL,0x7df71b5d05d761fLL,0x7df6597d965f7dfLL,0x75b6597d965f7dfLL,0x7df5d97995df7dfLL,0x7df7c07c07df7dfLL,0x7df7dc4dc7df7dfLL,0x7df75f75b5d641fLL,0x7df41f05545741fLL,0x7df3d641669965fLL,0x7df6175d85d761fLL,0x7df45e7df7de45fLL,0x7df6175d75d761fLL,0x7df41e79879e41fLL,0x7df79e79879e41fLL,0x7df4565d37de45fLL,0x7df5d75d05d75dfLL,0x7df41d75d75d41fLL,0x7df71b6db6db61fLL,0x7df5db75e75b5dfLL,0x7df41e79e79e79fLL,0x7df5d55544925dfLL,0x7df5d34d55165dfLL,0x7df6175d75d761fLL,0x7df7df7d85d761fLL,0x7c76175d75d761fLL,0x7df5db75c6db71fLL,0x7df6175d979e45fLL,0x7df75d75d75d41fLL,0x7df6175d75d75dfLL,0x7df7596965973dfLL,0x7df69a6155555dfLL,0x7df3d665b6563dfLL,0x7df75d75d69a5dfLL,0x7df41f79d6d741fLL,0x7d175d75d75d751LL,0x7cf5d76dd75e79fLL,0x7d86db6db6db6d8LL,0x7df7d769a69d75fLL,0x7c07df7df7df7dfLL,0x7df7df7df7df6ddLL,0x7df01645761f7dfLL,0x7df6175d665f7dfLL,0x7df41f7df41f7dfLL,0x7df5135d74175d7LL,0x7df41f41761f7dfLL,0x7df75d75d41d753LL,0x6175135d741f7dfLL,0x7df5d75d645f7dfLL,0x7df6db6db61f7dbLL,0x71b6db6db61f7dbLL,0x7df59a71a59e79eLL,0x7df75d75d75d75cLL,0x7df55555541f7dfLL,0x7df5d75d645f7dfLL,0x7df6175d761f7dfLL,0x7df6175d665f7dfLL,0x5d75135d741f7dfLL,0x7df79e79449f7dfLL,0x7df61765e45f7dfLL,0x7df4dd75d41d75fLL,0x7df5135d75df7dfLL,0x7df75a69a5df7dfLL,0x7df59624935f7dfLL,0x7df5da75a5df7dfLL,0x79d6595963df7dfLL,0x7df41e75b41f7dfLL,0x7d175d75e75d751LL,0x7dd75d75d75d75dLL,0x7d86db6d76db6d8LL,0x7df7df0cc7df7dfLL,0x7df7df7df7df7dfLL};
  const i64 FBMP4[256] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0x200208208200LL,0x14514LL,0x28af94f28a00LL,0x87a8a1838af08LL,0x894a1852a100LL,0xf3268c714200LL,0x8208LL,0x20408208208420LL,0x6210410410206LL,0x14336200LL,0x208f88200000LL,0x210618000000000LL,0x3c000000LL,0x618000000000LL,0x2104218420800LL,0x7228a28a2700LL,0xf8820820a300LL,0xf04210820700LL,0x720818820f00LL,0x410f92518400LL,0x72081c104f00LL,0x72299a084e00LL,0x104208420f00LL,0x72289c4a2700LL,0x39083c8a2700LL,0x618018600000LL,0x210618018600000LL,0x818198800000LL,0x3e03e000000LL,0x8cc0c080000LL,0x200210824f00LL,0xf02eaaea2f00LL,0xa4f24518600LL,0x7a289e8a2780LL,0xe04082084e00LL,0x7a28a28a2780LL,0xf0411c104f00LL,0x10411c104f00LL,0xe248b2084e00LL,0x8a28be8a2880LL,0xf88208208f80LL,0x310410410700LL,0x892286292880LL,0xf04104104100LL,0x8aaaaedb6880LL,0x8b2caaba6880LL,0x7228a28a2700LL,0x8209e8a2780LL,0x207228a28a2700LL,0x89228e492380LL,0x720818104e00LL,0x208208208f80LL,0x7228a28a2880LL,0x218524922080LL,0x5147aaaaa880LL,0xa4610624080LL,0x208208514880LL,0xf82108420f80LL,0x38208208208238LL,0x820408204102LL,0x1c41041041041cLL,0x22514508200LL,0x3e000000000000LL,0x408LL,0xf24e20700000LL,0x7a28a6682082LL,0xf02082f00000LL,0xb328a2f20820LL,0xf02fa2700000LL,0x208208f08230LL,0x720b328a2f00000LL,0x8a28a6e82082LL,0x410410700010LL,0x390410410700010LL,0x914314904104LL,0x20820820820eLL,0xaaaaaaf80000LL,0x8a28a6e80000LL,0x7228a2700000LL,0x827a28a6680000LL,0x820b328a2f00000LL,0x10412cd00000LL,0x720604e00000LL,0xc08208f08200LL,0xbb28a2880000LL,0x214514880000LL,0x92469a280000LL,0x894214880000LL,0x188618924080000LL,0xf84210f80000LL,0x38208204208238LL,0x8208208208208LL,0x1c41042041041cLL,0xc8e000000LL,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0xfbefbefbefbefbeLL,0xfbedbedb6db6dbeLL,0xfbefbefbefaaaaaLL,0xfbed3402a0965beLL,0xfb68165a6c340b6LL,0xfbe72a5a6a94ebeLL,0xfbe08c9328aadbeLL,0xfbefbefbefb6db6LL,0xf9ebb6db6db6b9eLL,0xfb8daebaebaedb8LL,0xfbefbefaac88dbeLL,0xfbedb6036dbefbeLL,0xdae9a6fbefbefbeLL,0xfbefbef82fbefbeLL,0xfbe9a6fbefbefbeLL,0xfbcebada6b9e7beLL,0xfbe89c71c71c8beLL,0xfbe036db6db4cbeLL,0xfbe0badae79e8beLL,0xfbe89e7a679e0beLL,0xfbebae02caa6bbeLL,0xfbe89e7a2eba0beLL,0xfbe89c624f3a1beLL,0xfbeebadb6b9e0beLL,0xfbe89c722b1c8beLL,0xfbec2e78271c8beLL,0xfbe9a6fa69befbeLL,0xdae9a6fa69befbeLL,0xfbe7a6e267befbeLL,0xfbef80f80fbefbeLL,0xfbef323b2f3efbeLL,0xfbedbedae79a0beLL,0xfbe0bc11411c0beLL,0xfbef1a09aaa69beLL,0xfbe81c72071c83eLL,0xfbe1baf3cf3a1beLL,0xfbe81c71c71c83eLL,0xfbe0baea2eba0beLL,0xfbeebaea2eba0beLL,0xfbe19a70cf3a1beLL,0xfbe71c70071c73eLL,0xfbe036db6db603eLL,0xfbecaebaebae8beLL,0xfbe72cd38d2c73eLL,0xfbe0baebaebaebeLL,0xfbe71451020873eLL,0xfbe70c31441873eLL,0xfbe89c71c71c8beLL,0xfbef3cf2071c83eLL,0xf9e89c71c71c8beLL,0xfbe72cd30b2cc3eLL,0xfbe89e7a6eba1beLL,0xfbedb6db6db603eLL,0xfbe89c71c71c73eLL,0xfbeda6a9a69cf3eLL,0xfbeaaa81451473eLL,0xfbef1a9ae99af3eLL,0xfbedb6db6aaa73eLL,0xfbe03ceb6b9e03eLL,0xf86db6db6db6d86LL,0xfbe79ebb6dbaebcLL,0xfa2baebaebaeba2LL,0xfbef9caaaab6dbeLL,0xf80fbefbefbefbeLL,0xfbefbefbefbebb6LL,0xfbe09a19e8befbeLL,0xfbe81c71893cf3cLL,0xfbe0bcf3c0befbeLL,0xfbe48c71c09e79eLL,0xfbe0bc01c8befbeLL,0xfbedb6db60b6d8eLL,0x89e48c71c0befbeLL,0xfbe71c71813cf3cLL,0xfbebaebae8befaeLL,0xc2ebaebae8befaeLL,0xfbe6aacaa6baebaLL,0xfbedb6db6db6db0LL,0xfbe51451403efbeLL,0xfbe71c71813efbeLL,0xfbe89c71c8befbeLL,0xf3c81c71893efbeLL,0x79e48c71c0befbeLL,0xfbeebae922befbeLL,0xfbe89e9ba1befbeLL,0xfbe3b6db60b6dbeLL,0xfbe40c71c73efbeLL,0xfbedaaaaa73efbeLL,0xfbe69a924d3efbeLL,0xfbe72adaa73efbeLL,0xe369a669af3efbeLL,0xfbe03adae03efbeLL,0xf86db6dbadb6d86LL,0xfb6db6db6db6db6LL,0xfa2baeb9ebaeba2LL,0xfbefbe330fbefbeLL,0xfbefbefbefbefbeLL};
  const int FPOP [190] = {0,6,6,20,21,16,20,3,11,11,9,9,6,4,4,10,16,13,12,13,14,14,16,10,17,16,8,10,8,12,8,10,23,16,20,11,18,15,12,15,17,15,10,14,10,22,20,16,15,18,16,12,11,15,13,19,13,10,15,13,9,13,10,6,2,14,17,11,17,15,12,18,16,8,12,13,10,17,13,12,16,16,9,10,11,13,9,15,9,13,13,13,9,13,8,
                          60,54,54,40,39,44,40,57,49,49,51,51,54,56,56,50,44,47,48,47,46,46,44,50,43,44,52,50,52,48,52,50,37,44,40,49,42,45,48,45,43,45,50,46,50,38,40,44,45,42,44,48,49,45,47,41,47,50,45,47,51,47,50,54,58,46,43,49,43,45,48,42,44,52,48,47,50,43,47,48,44,44,51,50,49,47,51,45,51,47,47,47,51,47,52};
  const int FBIN [ 11] = {0,10,12,14,17,37,44,46,48,51,61};
  const int FBINN[ 10] = {37,57,58,58,54,50,51,58,61,44};
  const int FBINI[ 10][61] = {{0x20,0x60,0x27,0x2d,0x2e,0x21,0x22,0x2c,0x5f,0x3a,0x3c,0x3e,0x69,0x7e,0x2a,0x2b,0x5c,0x72,0x76,0x78,0x7c,0x2f,0x37,0x3b,0x3f,0x4a,0x4c,0x59,0x5e,0x6c,0x73,0x28,0x29,0x43,0x54,0x63,0x74},
                              {0x20,0x60,0x27,0x2d,0x2e,0x21,0x22,0x2c,0x5f,0x3a,0x3c,0x3e,0x69,0x7e,0x2a,0x2b,0x5c,0x72,0x76,0x78,0x7c,0x2f,0x37,0x3b,0x3f,0x4a,0x4c,0x59,0x5e,0x6c,0x73,0x28,0x29,0x43,0x54,0x63,0x74,0x32,0x3d,0x46,0x53,0x66,0x6a,0x6f,0x31,0x33,0x56,0x58,0x5b,0x5d,0x6b,0x6e,0x75,0x79,0x7a,0x7b,0x7d},
                              {0x2f,0x37,0x3b,0x3f,0x4a,0x4c,0x59,0x5e,0x6c,0x73,0x28,0x29,0x43,0x54,0x63,0x74,0x32,0x3d,0x46,0x53,0x66,0x6a,0x6f,0x31,0x33,0x56,0x58,0x5b,0x5d,0x6b,0x6e,0x75,0x79,0x7a,0x7b,0x7d,0x34,0x35,0x4b,0x61,0x45,0x47,0x49,0x50,0x55,0x5a,0x65,0x77,0x25,0x30,0x36,0x39,0x41,0x4f,0x52,0x68,0x70,0x71},
                              {0x32,0x3d,0x46,0x53,0x66,0x6a,0x6f,0x31,0x33,0x56,0x58,0x5b,0x5d,0x6b,0x6e,0x75,0x79,0x7a,0x7b,0x7d,0x34,0x35,0x4b,0x61,0x45,0x47,0x49,0x50,0x55,0x5a,0x65,0x77,0x25,0x30,0x36,0x39,0x41,0x4f,0x52,0x68,0x70,0x71,0x38,0x48,0x62,0x64,0x6d,0x44,0x51,0x67,0x57,0x23,0x26,0x42,0x4e,0x24,0x4d,0x40},
                              {0x34,0x35,0x4b,0x61,0x45,0x47,0x49,0x50,0x55,0x5a,0x65,0x77,0x25,0x30,0x36,0x39,0x41,0x4f,0x52,0x68,0x70,0x71,0x38,0x48,0x62,0x64,0x6d,0x44,0x51,0x67,0x57,0x23,0x26,0x42,0x4e,0x24,0x4d,0x40,0xc0,0xcd,0xa4,0xa3,0xa6,0xc2,0xce,0xd7,0xc4,0xd1,0xe7,0xb8,0xc8,0xe2,0xe4,0xed},
                              {0x38,0x48,0x62,0x64,0x6d,0x44,0x51,0x67,0x57,0x23,0x26,0x42,0x4e,0x24,0x4d,0x40,0xc0,0xcd,0xa4,0xa3,0xa6,0xc2,0xce,0xd7,0xc4,0xd1,0xe7,0xb8,0xc8,0xe2,0xe4,0xed,0xa5,0xb0,0xb6,0xb9,0xc1,0xcf,0xd2,0xe8,0xf0,0xf1,0xc5,0xc7,0xc9,0xd0,0xd5,0xda,0xe5,0xf7},
                              {0xc0,0xcd,0xa4,0xa3,0xa6,0xc2,0xce,0xd7,0xc4,0xd1,0xe7,0xb8,0xc8,0xe2,0xe4,0xed,0xa5,0xb0,0xb6,0xb9,0xc1,0xcf,0xd2,0xe8,0xf0,0xf1,0xc5,0xc7,0xc9,0xd0,0xd5,0xda,0xe5,0xf7,0xb4,0xb5,0xcb,0xe1,0xb1,0xb3,0xd6,0xd8,0xdb,0xdd,0xeb,0xee,0xf5,0xf9,0xfa,0xfb,0xfd},
                              {0xa5,0xb0,0xb6,0xb9,0xc1,0xcf,0xd2,0xe8,0xf0,0xf1,0xc5,0xc7,0xc9,0xd0,0xd5,0xda,0xe5,0xf7,0xb4,0xb5,0xcb,0xe1,0xb1,0xb3,0xd6,0xd8,0xdb,0xdd,0xeb,0xee,0xf5,0xf9,0xfa,0xfb,0xfd,0xb2,0xbd,0xc6,0xd3,0xe6,0xea,0xef,0xa8,0xa9,0xc3,0xd4,0xe3,0xf4,0xaf,0xb7,0xbb,0xbf,0xca,0xcc,0xd9,0xde,0xec,0xf3},
                              {0xb4,0xb5,0xcb,0xe1,0xb1,0xb3,0xd6,0xd8,0xdb,0xdd,0xeb,0xee,0xf5,0xf9,0xfa,0xfb,0xfd,0xb2,0xbd,0xc6,0xd3,0xe6,0xea,0xef,0xa8,0xa9,0xc3,0xd4,0xe3,0xf4,0xaf,0xb7,0xbb,0xbf,0xca,0xcc,0xd9,0xde,0xec,0xf3,0xaa,0xab,0xdc,0xf2,0xf6,0xf8,0xfc,0xba,0xbc,0xbe,0xe9,0xfe,0xa1,0xa2,0xac,0xdf,0xad,0xae,0xa7,0xe0,0xa0},
                              {0xb2,0xbd,0xc6,0xd3,0xe6,0xea,0xef,0xa8,0xa9,0xc3,0xd4,0xe3,0xf4,0xaf,0xb7,0xbb,0xbf,0xca,0xcc,0xd9,0xde,0xec,0xf3,0xaa,0xab,0xdc,0xf2,0xf6,0xf8,0xfc,0xba,0xbc,0xbe,0xe9,0xfe,0xa1,0xa2,0xac,0xdf,0xad,0xae,0xa7,0xe0,0xa0}};
  const i64 FMASK = 0x0fffffffffffffffLL; // asc font
  const uch ABLACK = 0, AWHITE = 215, CBLACK = 0xa0, CWHITE = 0x20;
  const int FROWS = 10, FCOLS = 6, TBUF_MAXSIZE = 1600 * 1200, HEADER_SIZE = 8;

  inline int popcount60(i64 aa) { return MATH::popcount64(aa & FMASK); }

  //// struct
  template<typename TT> struct img2txt;
  PyTypeObject TYPE = {PyVarObject_HEAD_INIT(NULL, 0)"_img2txt",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  inline int CHECK_IMG2TXT(PyObject *self) { return PyObject_TypeCheck(self, &TYPE); }
  PySequenceMethods PYSEQUENCE = {NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,};
  PYGETSETDEF GETSET; PYMETHODDEF METHOD;

  //// img2txt
  template<typename TT> struct img2txt: NUMBYTES::numbytes<i64> {
    NUMBYTES::numbytes<char> color;
    NUMBYTES::numbytes<char> txt;

  };

  //// export
  PyObject *img2txt_init(PyObject *module) {
    // type
    TYPE.tp_basicsize = sizeof(img2txt<i64>);
    TYPE.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE;
    TYPE.tp_base = &NUMBYTES::TYPE;
    TYPE.tp_getset = &GETSET[0];
    TYPE.tp_methods = &METHOD[0];
    // TYPE.tp_dealloc = (destructor)img2txt_dealloc;
    // TYPE.tp_new = (newfunc)img2txt_new;
    // TYPE.tp_str = (reprfunc)__str__;

    if (PyType_Ready(&TYPE) < 0) return NULL; Py_INCREF(&TYPE); PyModule_AddObject(module, "_img2txt", (PyObject *) &TYPE); return module;
  }
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
      if (not NUMBYTES::numbytes_init(module)) return NULL;
      if (not IMG2TXT::img2txt_init(module)) return NULL;
      return module;
    }
  }
}
