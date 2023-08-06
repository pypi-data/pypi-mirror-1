#include "liblzma_decompressobj.h"

PyDoc_STRVAR(libLZMADecomp_decompress__doc__,
"decompress(data[, max_length]) -- Return a string containing the decompressed\n\
version of the data.\n\
\n\
After calling this function, some of the input data may still be stored in\n\
internal buffers for later processing.\n\
Call the flush() method to clear these buffers.\n\
If the max_length parameter is specified then the return value will be\n\
no longer than max_length. Unconsumed input data will be stored in\n\
the unconsumed_tail data descriptor.");

static PyObject *
libLZMADecomp_decompress(libLZMADecompObject *self, PyObject *args)
{
	Py_ssize_t inplen, old_length, length = DEFAULTALLOC;
    	uint8_t *input;
    	uint64_t start_total_out;
	PyObject *RetVal = NULL;
	lzma_stream *lzus = &self->lzus;
	lzma_ret lzuerror;
   
	INITCHECK
	if (!PyArg_ParseTuple(args, "s#|i:decompress", &input,
			  &inplen, &self->max_length))
		return NULL;

	ACQUIRE_LOCK(self);
	if (!self->running) {
		PyErr_SetString(PyExc_EOFError, "end of stream was "
						"already found");
		goto error;
	}

    	if (self->max_length < 0) {
		PyErr_SetString(PyExc_ValueError,
				"max_length must be greater than zero");
		goto error;
    	}

	/* limit amount of data allocated to max_length */
	if (self->max_length && length > self->max_length)
		length = self->max_length;

	if(!(RetVal = PyString_FromStringAndSize(NULL, length)))
		goto error;

	start_total_out = lzus->total_out;
	lzus->avail_in = (size_t)inplen;
	lzus->next_in = input;
	lzus->avail_out = (size_t)length;
	lzus->next_out = (uint8_t *)PyString_AS_STRING(RetVal);

	for (;;) {
		Py_BEGIN_ALLOW_THREADS
		lzuerror = lzma_code(lzus, LZMA_RUN);
		Py_END_ALLOW_THREADS

		if (lzus->avail_in == 0 || lzus->avail_out != 0)
			break; /* no more input data */

		/* If max_length set, don't continue decompressing if we've already
		 * reached the limit.
		 */
		if (self->max_length && length >= self->max_length)
			break;

		/* otherwise, ... */
		old_length = length;
		length = length << 1;
		if (self->max_length && length > self->max_length)
			length = self->max_length;
		
		if (_PyString_Resize(&RetVal, length) < 0)
			goto error;
		lzus->next_out = (uint8_t *)PyString_AS_STRING(RetVal) + old_length;
		lzus->avail_out = (size_t)length - (size_t)old_length;
		if(!CatchlibLZMAError(lzuerror, lzus))
			goto error;
	}

    	/* Not all of the compressed data could be accommodated in the output
	 * buffer of specified size. Return the unconsumed tail in an attribute.
	 */
    	if(self->max_length) {
		Py_DECREF(self->unconsumed_tail);
		self->unconsumed_tail = PyString_FromStringAndSize((const char *)lzus->next_in,
				(Py_ssize_t)lzus->avail_in);
		if(!self->unconsumed_tail) {
			goto error;
		}
    	}

    	/* The end of the compressed data has been reached, so set the
	 * unused_data attribute to a string containing the remainder of the
	 * data in the string.  Note that this is also a logical place to call
	 * lzma_end, but the old behaviour of only calling it on flush() is
	 * preserved.
	 */
    	if (lzuerror == LZMA_STREAM_END) {
		Py_XDECREF(self->unused_data);  /* Free original empty string */
		self->unused_data = PyString_FromStringAndSize(
				(const char *)lzus->next_in, (Py_ssize_t)lzus->avail_in);
		if (self->unused_data == NULL) {
			goto error;
		}
		/* We will only get LZMA_BUF_ERROR if the output buffer was full
		 * but there wasn't more output when we tried again, so it is
		 * not an error condition.
		 */
	} else if(!CatchlibLZMAError(lzuerror, lzus))
		goto error;

	_PyString_Resize(&RetVal, (Py_ssize_t)lzus->total_out - (Py_ssize_t)start_total_out);

	RELEASE_LOCK(self);
	return RetVal;

 error:
	RELEASE_LOCK(self);
	Py_XDECREF(RetVal);
	return NULL;
}

PyDoc_STRVAR(libLZMADecomp_flush__doc__,
"flush( [length] ) -- Return a string containing any remaining\n\
decompressed data. length, if given, is the initial size of the\n\
output buffer.\n\
\n\
The decompressor object can only be used again after this call\n\
if reset() is called afterwards.");

static PyObject * libLZMADecomp_flush(libLZMADecompObject *self, PyObject *args)
{
	Py_ssize_t length = DEFAULTALLOC;
	
	PyObject * RetVal = NULL;
	uint64_t start_total_out;
	lzma_stream *lzus = &self->lzus;
	lzma_ret lzuerror;

	INITCHECK

	if (!PyArg_ParseTuple(args, "|i:flush", &length))
		return NULL;

	ACQUIRE_LOCK(self);
	if (!self->running) {
		PyErr_SetString(PyExc_ValueError, "object was already flushed");
		goto error;
	}

	if (!(RetVal = PyString_FromStringAndSize(NULL, length)))
		goto error;

	*lzus = LZMA_STREAM_INIT_VAR;

	start_total_out = lzus->total_out;
	lzus->avail_out = (size_t)length;
	lzus->next_out = (uint8_t *)PyString_AS_STRING(RetVal);

	for (;;) {
		Py_BEGIN_ALLOW_THREADS
		lzuerror = lzma_code(lzus, LZMA_FINISH);
		Py_END_ALLOW_THREADS

		if (lzus->avail_in == 0 || lzus->avail_out != 0)
			break; /* no more input data */

		if (_PyString_Resize(&RetVal, length << 1) < 0)
			goto error;
		lzus->next_out = (uint8_t *)PyString_AS_STRING(RetVal) + length;
		lzus->avail_out = (size_t)length;
		length = length << 1;

		if(!CatchlibLZMAError(lzuerror, lzus))
			goto error;
	}

	
    	/* If flushmode is LZMA_FINISH, we also have to call lzma_end() to free
	 * various data structures. Note we should only get LZMA_STREAM_END when
	 * flushmode is LZMA_FINISH
	 */
	if (lzuerror == LZMA_STREAM_END) {
		lzma_end(lzus);
		self->running = false;
		if(!CatchlibLZMAError(lzuerror, lzus))
			goto error;
	}
	_PyString_Resize(&RetVal, (Py_ssize_t)lzus->total_out - (Py_ssize_t)start_total_out);

	RELEASE_LOCK(self);
	return RetVal;

error:
	RELEASE_LOCK(self);
	Py_XDECREF(RetVal);
    	return RetVal;
}

PyDoc_STRVAR(libLZMADecomp_reset__doc__,
"reset([maxlength]) -- Resets the decompression object.");

static PyObject *
libLZMADecomp_reset(libLZMADecompObject *self, PyObject *args)
{
	PyObject *result=NULL;
	lzma_stream *lzus = &self->lzus;	
	lzma_ret lzuerror;

	INITCHECK
	if (!PyArg_ParseTuple(args, "|i:reset", &self->max_length))
		return NULL;

	if (self->max_length < 0) {
		PyErr_SetString(PyExc_ValueError,
				"max_length must be greater than zero");
		goto error;
	}
	ACQUIRE_LOCK(self);	
	if (self->running)
		lzma_end(lzus);
	Py_CLEAR(self->unused_data);
	Py_CLEAR(self->unconsumed_tail);
	if((self->unused_data = PyString_FromString("")) == NULL)
		goto error;
	if((self->unconsumed_tail = PyString_FromString("")) == NULL)
		goto error;

	lzuerror = lzma_auto_decoder(lzus, 0, 0);
	if(!CatchlibLZMAError(lzuerror, lzus))
		goto error;
	self->running = true;

	result = Py_None;
 error:
	RELEASE_LOCK(self);
	Py_XINCREF(result);
	return result;
}

static PyMemberDef libLZMADecomp_members[] = {
	{"unused_data", T_OBJECT, offsetof(libLZMADecompObject, unused_data),
		RO, NULL},
	{"unconsumed_tail", T_OBJECT, offsetof(libLZMADecompObject,
			unconsumed_tail), RO, NULL},
	{NULL, 0, 0, 0, NULL}	/* Sentinel */
};

static PyMethodDef libLZMADecomp_methods[4] =
{
	{"decompress", (PyCFunction)libLZMADecomp_decompress, METH_VARARGS,
		libLZMADecomp_decompress__doc__},
	{"flush", (PyCFunction)libLZMADecomp_flush, METH_VARARGS,
		libLZMADecomp_flush__doc__},
	{"reset", (PyCFunction)libLZMADecomp_reset, METH_VARARGS,
		libLZMADecomp_reset__doc__},
	{NULL, NULL, 0, NULL} /*sentinel*/
};

static PyObject *
libLZMADecompObject_new(PyTypeObject *type, __attribute__((unused)) PyObject *args, __attribute__((unused)) PyObject *kwargs)
{
	libLZMADecompObject *self;
	self = (libLZMADecompObject *)type->tp_alloc(type, 0);

	if (self != NULL){
		self->is_initialised = false;
		self->running = false;		
		if((self->unused_data = PyString_FromString("")) == NULL)
				goto error;
		if((self->unconsumed_tail = PyString_FromString("")) == NULL)
			goto error;
		self->lzus = LZMA_STREAM_INIT_VAR;
	}
	else
		return NULL;

	return (PyObject *)self;
 error:
	Py_DECREF(self);
	return NULL;
}

static void
libLZMADecomp_dealloc(libLZMADecompObject *self)
{
#ifdef WITH_THREAD
	if (self->lock)
		PyThread_free_lock(self->lock);
#endif
	if (self->is_initialised)
		lzma_end(&self->lzus);
	Py_XDECREF(self->unused_data);
	Py_XDECREF(self->unconsumed_tail);
	self->ob_type->tp_free((PyObject*)self);
}

static int8_t
libLZMADecomp_init(libLZMADecompObject *self, PyObject *args)
{
	lzma_stream *lzus = &self->lzus;	
	lzma_ret lzuerror;
	if (!PyArg_ParseTuple(args, "|:LZMADecompressor", &self->max_length))
		return -1;

#ifdef WITH_THREAD
	self->lock = PyThread_allocate_lock();
	if (!self->lock) {
		PyErr_SetString(PyExc_MemoryError, "unable to allocate lock");
		goto error;
	}
#endif

	if (self->max_length < 0) {
		PyErr_SetString(PyExc_ValueError,
				"max_length must be greater than zero");
		goto error;
	}

	lzuerror = lzma_auto_decoder(lzus, 0, 0);
	if(!CatchlibLZMAError(lzuerror, lzus))
		goto error;

	self->is_initialised = true;
	self->running = true;

	return 0;

 error:
#ifdef WITH_THREAD
	if (self->lock) {
		PyThread_free_lock(self->lock);
		self->lock = NULL;
	}
#endif
	free(self);
	return -1;
}

PyDoc_STRVAR(libLZMADecomp__doc__,
"LZMADecompressor(max_length) -> decompressor object\n\
\n\
Create a new decompressor object. This object may be used to decompress\n\
data sequentially. If you want to decompress data in one shot, use the\n\
decompress() function instead.\n");

PyTypeObject libLZMADecomp_Type = {
	PyObject_HEAD_INIT(NULL)
	0,						/*ob_size*/
	"liblzma.LZMADecompressor",			/*tp_name*/
	sizeof(libLZMADecompObject),			/*tp_basicsize*/
	0,						/*tp_itemsize*/
	(destructor)libLZMADecomp_dealloc,		/*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,						/*tp_call*/
	0,						/*tp_str*/
	PyObject_GenericGetAttr,			/*tp_getattro*/
	PyObject_GenericSetAttr,			/*tp_setattro*/
	0,						/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,		/*tp_flags*/
	libLZMADecomp__doc__,         			/*tp_doc*/
	0,						/*tp_traverse*/
	0,						/*tp_clear*/
	0,						/*tp_richcompare*/
	0,						/*tp_weaklistoffset*/
	0,						/*tp_iter*/
	0,						/*tp_iternext*/
	libLZMADecomp_methods,				/*tp_methods*/
	libLZMADecomp_members,				/*tp_members*/
	0,						/*tp_getset*/
	0,						/*tp_base*/
	0,						/*tp_dict*/
	0,						/*tp_descr_get*/
	0,						/*tp_descr_set*/
	0,						/*tp_dictoffset*/
	(initproc)libLZMADecomp_init,			/*tp_init*/
	PyType_GenericAlloc,				/*tp_alloc*/
	libLZMADecompObject_new,			/*tp_new*/
	_PyObject_Del,					/*tp_free*/
	0,						/*tp_is_gc*/
	0,						/*tp_bases*/
	0,						/*tp_mro*/
	0,						/*tp_cache*/
	0,						/*tp_subclasses*/
	0,						/*tp_weaklist*/
	0						/*tp_del*/
};
