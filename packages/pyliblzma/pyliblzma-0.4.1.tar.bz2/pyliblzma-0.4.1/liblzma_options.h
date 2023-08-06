#ifndef LIBLZMA_OPTIONS_H
#define LIBLZMA_OPTIONS_H 1

#include "liblzma.h"
#include <structmember.h>

#define CHECK_RANGE(x, a, b, msg) if (check_range(x, a, b)) { PyErr_Format(PyExc_ValueError, msg, a, b, (int32_t)x); return false; }
static inline bool check_range(uint32_t x, uint32_t a, uint32_t b){
	return (x < a || x > b);
}
#define MEMBER_DESCRIPTOR(name, type, variable, text) (PyMemberDef){name, type, offsetof(LZMAOptionsObject, variable), RO, PyString_AsString(PyString_Format(PyString_FromString((char*)text), (PyObject*)self->variable))}

#define	LZMA_BEST_SPEED			1
#define	LZMA_BEST_COMPRESSION		9
#define	LZMA_DEFAULT_COMPRESSION	7
#define	LZMA_MODE_DEFAULT		LZMA_MODE_NORMAL
#define LZMA_MODE_INVALID		-1
#define LZMA_MF_INVALID			-1

#define	LZMA_MF_DEFAULT			LZMA_MF_BT4
#define	LZMA_MF_CYCLES_DEFAULT		0
#define LZMA_DICT_SIZE_MAX 		(UINT32_C(1) << 30) + (UINT32_C(1) << 29)
#define LZMA_NICE_LEN_MIN		5
#define LZMA_NICE_LEN_MAX		273
#define LZMA_NICE_LEN_DEFAULT		128

typedef struct
{
	PyObject_HEAD
	PyObject *format;
	PyObject *eopm;
	PyObject *level;
	PyObject *dict_size;
	PyObject *lc;
	PyObject *lp;
	PyObject *pb;
	PyObject *mode_dict;
	PyObject *mode;
	PyObject *nice_len;
	PyObject *mf_dict;
	PyObject *mf;
	PyObject *depth;
} LZMAOptionsObject;

extern PyTypeObject LZMAOptions_Type;

bool init_lzma_options(const char *funcName, PyObject *kwargs, lzma_options_lzma *options);
PyObject *LZMA_options_get(lzma_options_lzma lzma_options);

#endif /* LIBLZMA_OPTIONS_H */
