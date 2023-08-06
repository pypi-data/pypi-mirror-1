#ifndef LIBLZMA_OPTIONS_H
#define LIBLZMA_OPTIONS_H 1

#include "liblzma.h"
#include <structmember.h>

#define CHECK_RANGE(x, a, b, msg) if (check_range(x, a, b)) { PyErr_Format(PyExc_ValueError, msg, a, b, (int32_t)x); return false; }
static inline bool check_range(uint32_t x, uint32_t a, uint32_t b){
	return (x < a || x > b);
}
#define MEMBER_DESCRIPTOR(name, type, variable, text) (PyMemberDef){name, type, offsetof(LZMAOptionsObject, variable), RO, PyString_AsString(PyString_Format(PyString_FromString((char*)text), (PyObject*)self->variable))}

#define	LZMA_BEST_SPEED 1
#define	LZMA_BEST_COMPRESSION 9
#define	LZMA_DEFAULT_COMPRESSION 7
#define	LZMA_MODE_DEFAULT LZMA_MODE_BEST
#define	LZMA_MF_DEFAULT	LZMA_MF_BT4
#define	LZMA_MF_CYCLES_DEFAULT 0

typedef struct
{
	PyObject_HEAD
	PyObject *format;
	PyObject *eopm;
	PyObject *level;
	PyObject *dictionary_size;
	PyObject *literal_context_bits;
	PyObject *literal_pos_bits;
	PyObject *pos_bits;
	PyObject *mode_dict;
	PyObject *mode;
	PyObject *fast_bytes;
	PyObject *match_finder_dict;
	PyObject *match_finder;
	PyObject *match_finder_cycles;
} LZMAOptionsObject;

extern PyTypeObject LZMAOptions_Type;

bool init_lzma_options(const char *funcName, PyObject *kwargs, lzma_options_lzma *options);
PyObject *LZMA_options_get(lzma_options_lzma lzma_options);

#endif /* LIBLZMA_OPTIONS_H */
