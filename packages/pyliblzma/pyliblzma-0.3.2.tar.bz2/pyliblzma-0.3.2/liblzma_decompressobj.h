#ifndef LIBLZMA_DECOMPRESSOBJ_H
#define LIBLZMA_DECOMPRESSOBJ_H 1
#include "liblzma.h"
#include <structmember.h>

typedef struct
{
	PyObject_HEAD
	lzma_stream lzus;
	PyObject *unused_data;
	PyObject *unconsumed_tail;
	Py_ssize_t max_length;
	bool is_initialised, running;
#ifdef WITH_THREAD
	PyThread_type_lock lock;
#endif
} libLZMADecompObject;

extern PyTypeObject libLZMADecomp_Type;
#endif /* LIBLZMA_DECOMPRESSOBJ_H */
