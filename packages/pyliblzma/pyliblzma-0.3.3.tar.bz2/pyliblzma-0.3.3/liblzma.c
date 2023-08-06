#include "liblzma.h"
#include "liblzma_compressobj.h"
#include "liblzma_decompressobj.h"
#include "liblzma_options.h"

bool
CatchlibLZMAError(lzma_ret lzuerror, lzma_stream *lzus)
{
	bool ret = true;
	switch(lzuerror) {
		case LZMA_OK:
		case LZMA_STREAM_END:
			break;

		case LZMA_PROG_ERROR:
			PyErr_SetString(PyExc_ValueError,
					"the lzma library has received wrong "
					"options");
			ret = false;
			break;

		case LZMA_DATA_ERROR:
			PyErr_SetString(PyExc_IOError, "invalid data stream");
			ret = false;
			break;

		case LZMA_MEM_ERROR:
			PyErr_SetString(PyExc_MemoryError, "cannot allocate memory");
			ret = false;
			break;

		case LZMA_BUF_ERROR:
			if (lzus->avail_out > 0) {
				PyErr_SetString(PyExc_IOError, "unknown BUF error");
				ret = false;
			}
			break;

		case LZMA_HEADER_ERROR:
			PyErr_SetString(PyExc_RuntimeError, "invalid or unsupported header");
			ret = false;
			break;

		case LZMA_UNSUPPORTED_CHECK:
			PyErr_SetString(libLZMAError, "check type is unknown");
			ret = false;
			break;

		default:
			ret = false;
			PyErr_SetString(libLZMAError, "unknown error!");
			break;

	}
	return ret;
}

static const char __author__[] =
"The liblzma python module was written by:\n\
\n\
    Per Øyvind Karlsen <peroyvind@mandriva.org>\n\
";

PyDoc_STRVAR(libLZMA_compress__doc__,
"compress(string[format=alone, eopm=False, level=7, dictionary_size=23,\n\
literal_contextbits=3 literal_pos_bits=0, pos_bits=2, mode=2, fast_bytes=128,\n\
match_finder='bt4', match_finder_cycles=0]) -- Compress data using the given\n\
parameters, returning a string containing the compressed data.");

static PyObject *
libLZMA_compress(__attribute__((unused)) PyObject *self, PyObject *args, PyObject *kwargs)
{
	PyObject *RetVal = NULL;
	uint8_t *input;
	Py_ssize_t length, bufsize;
	lzma_ret lzuerror;
	lzma_stream _lzus;
	lzma_stream *lzus = &_lzus;
	lzma_options_alone alone;
	bool eopm = false;
	if(kwargs != NULL){
		PyObject* eopmString = PyString_FromString("eopm");
		if(PyDict_Contains(kwargs, eopmString)){
			eopm =  (bool)(int)PyInt_AsLong(PyDict_GetItem(kwargs, eopmString));
			PyDict_DelItem(kwargs, eopmString);
		}
	}

	if (!PyArg_ParseTuple(args, "s#:compress", &input, &length))
		return NULL;

	alone.lzma = lzma_preset_lzma[LZMA_DEFAULT_COMPRESSION-1];
	if(PyDict_Size(kwargs) >= 0)
		if(!init_lzma_options("compress", kwargs, &alone.lzma))
			return NULL;

	*lzus = LZMA_STREAM_INIT_VAR;
	bufsize = length + (length/100+1) + 600;

	if (!(RetVal = PyString_FromStringAndSize(NULL, bufsize)))
		return NULL;
	if(eopm)
		alone.uncompressed_size = LZMA_VLI_VALUE_UNKNOWN;
	else
		alone.uncompressed_size = (uint64_t)length;

	lzuerror = lzma_alone_encoder(lzus, &alone);
	if(!CatchlibLZMAError(lzuerror, lzus))
		goto error;

	lzus->avail_in = (size_t)length;
	lzus->next_in = input;
	lzus->next_out = (uint8_t *)PyString_AS_STRING(RetVal);
	lzus->avail_out = (size_t)bufsize;

	Py_BEGIN_ALLOW_THREADS
	lzuerror = lzma_code(lzus, LZMA_FINISH);
	Py_END_ALLOW_THREADS

	if(!CatchlibLZMAError(lzuerror, lzus))
		goto error;
	
	lzma_end(lzus);
	if (lzuerror == LZMA_STREAM_END)
		_PyString_Resize(&RetVal, (Py_ssize_t)lzus->total_out);

	return RetVal;

 error:
	if(lzuerror != LZMA_MEM_ERROR && lzuerror != LZMA_PROG_ERROR)
		lzma_end(lzus);
	Py_XDECREF(RetVal);
	return NULL;
}

PyDoc_STRVAR(libLZMA_decompress__doc__,
"decompress(string[, bufsize]) -- Return decompressed string.\n\
\n\
Optional arg bufsize is the initial output buffer size.");

static PyObject *
libLZMA_decompress(__attribute__((unused)) PyObject *self, PyObject *args)
{
	PyObject *result_str = NULL;
	uint8_t *input;
	Py_ssize_t length, r_strlen=DEFAULTALLOC;
	lzma_ret lzuerror;
	lzma_stream _lzus;
	lzma_stream *lzus = &_lzus;

	if (!PyArg_ParseTuple(args, "s#|l:decompress",
			  &input, &length, &r_strlen))
		return NULL;

	if (r_strlen <= 0)
		r_strlen = 1;

	*lzus = LZMA_STREAM_INIT_VAR;
	lzus->avail_in = (size_t)length;
	lzus->avail_out = (size_t)r_strlen;
	if (!(result_str = PyString_FromStringAndSize(NULL, r_strlen)))
		return NULL;

	lzus->next_out =  (uint8_t *)PyString_AS_STRING(result_str);
	lzus->next_in = (uint8_t *)input;
	lzuerror = lzma_auto_decoder(lzus, 0, 0);

	if(!CatchlibLZMAError(lzuerror, lzus))
		goto error;

	while (lzuerror != LZMA_STREAM_END){
		Py_BEGIN_ALLOW_THREADS
		lzuerror=lzma_code(lzus, LZMA_RUN);
		Py_END_ALLOW_THREADS

		if(!CatchlibLZMAError(lzuerror, lzus))
			goto error;
		if(lzuerror == LZMA_STREAM_END)
			break;
		if(lzuerror == LZMA_OK){
			if (_PyString_Resize(&result_str, r_strlen << 1) < 0) {
				goto error;
			}
		lzus->next_out = (uint8_t *)PyString_AS_STRING(result_str) + r_strlen;
		lzus->avail_out = (size_t)r_strlen;
		r_strlen = r_strlen << 1;
		}
	} 
	lzma_end(lzus);

	_PyString_Resize(&result_str, (Py_ssize_t)lzus->total_out);
	return result_str;
	
 error:
	if(lzuerror != LZMA_MEM_ERROR && lzuerror != LZMA_PROG_ERROR)
		lzma_end(lzus);	
	Py_XDECREF(result_str);
	return NULL;
}

PyDoc_STRVAR(libLZMA_crc32__doc__,
"crc32(string[, start]) -- Compute a CRC-32 checksum of string.\n\
\n\
An optional starting value can be specified. The returned checksum is\n\
an integer.");

static PyObject *
libLZMA_crc32(__attribute__((unused)) PyObject *self, PyObject *args)
{
	uint32_t crc32val = lzma_crc32(NULL, (size_t)0,  (uint32_t)0);
    	uint8_t *buf;
    	Py_ssize_t size;
    	if (!PyArg_ParseTuple(args, "s#|k:crc32", &buf, &size, &crc32val))
		return NULL;
    	crc32val = lzma_crc32(buf, (size_t)size, crc32val);
    	return PyInt_FromLong((long)crc32val);
}

PyDoc_STRVAR(libLZMA_crc64__doc__,
"crc64(string[, start]) -- Compute a CRC-64 checksum of string.\n\
\n\
An optional starting value can be specified.  The returned checksum is\n\
an integer.");

static PyObject *
libLZMA_crc64(__attribute__((unused)) PyObject *self, PyObject *args)
{
	uint64_t crc64val = lzma_crc64(NULL, (size_t)0, (uint64_t)0);
    	uint8_t *buf;
    	Py_ssize_t size;
    	if (!PyArg_ParseTuple(args, "s#|k:crc64", &buf, &size, &crc64val))
		return NULL;
    	crc64val = lzma_crc64(buf, (size_t)size, crc64val);
    	return PyLong_FromUnsignedLongLong(crc64val);
}

static PyMethodDef liblzma_methods[] = {
	{"compress", (PyCFunction)libLZMA_compress,
		METH_VARARGS|METH_KEYWORDS, libLZMA_compress__doc__},
    	{"crc32", (PyCFunction)libLZMA_crc32,
		METH_VARARGS, libLZMA_crc32__doc__},
    	{"crc64", (PyCFunction)libLZMA_crc64,
		METH_VARARGS, libLZMA_crc64__doc__},
	{"decompress", (PyCFunction)libLZMA_decompress,
		METH_VARARGS, libLZMA_decompress__doc__},
	{0, 0, 0, 0}
};

PyDoc_STRVAR(liblzma_module_documentation,
"The python liblzma module provides a comprehensive interface for\n\
the lzma compression library. It implements one shot (de)compression\n\
functions, CRC-32 & CRC-64 checksum copmutations, types for sequential\n\
(de)compression, and advanced options for lzma compression.\n\
");

/* declare function before defining it to avoid compile warnings */
PyMODINIT_FUNC initlzma(void);
PyMODINIT_FUNC
initlzma(void)
{
	PyObject *m, *ver, *optionsSingleton;
	char verstring[10], major, minor[5], micro[5], *s;
    	libLZMAComp_Type.ob_type = &PyType_Type;
    	libLZMADecomp_Type.ob_type = &PyType_Type;
	
    	m = Py_InitModule3("lzma", liblzma_methods,
 			liblzma_module_documentation);
    	if (m == NULL)
		return;
	
	optionsSingleton = PyType_GenericNew(&libLZMAOptions_Type, NULL, NULL);
	
	if(PyType_Ready(&libLZMAOptions_Type) < 0)
		return;

	libLZMAError = PyErr_NewException("libLZMA.error", NULL, NULL);
    	if (libLZMAError != NULL) {
		Py_INCREF(libLZMAError);
		PyModule_AddObject(m, "error", libLZMAError);
    	}
    
	Py_INCREF(&libLZMAOptions_Type);
	PyModule_AddObject(m, "LZMAOptions", (PyObject *)&libLZMAOptions_Type);

	Py_INCREF(&libLZMAComp_Type);
	PyModule_AddObject(m, "LZMACompressor", (PyObject *)&libLZMAComp_Type);

	Py_INCREF(&libLZMADecomp_Type);
	PyModule_AddObject(m, "LZMADecompressor", (PyObject *)&libLZMADecomp_Type);

	PyModule_AddObject(m, "options", optionsSingleton);
    	PyModule_AddIntConstant(m, "LZMA_RUN", (ulong)LZMA_RUN);
	/* LZMA_SYNC_FLUSH & LZMA_FULL_FLUSH isn't supported by LZMA_Alone format,
	 * but let's just leave it for future anyways. Should be moved to options
	 * class as as well..
	 */
	PyModule_AddIntConstant(m, "LZMA_SYNC_FLUSH", (ulong)LZMA_SYNC_FLUSH);
	PyModule_AddIntConstant(m, "LZMA_FULL_FLUSH", (ulong)LZMA_FULL_FLUSH);
	PyModule_AddIntConstant(m, "LZMA_FINISH", (ulong)LZMA_FINISH);

	PyModule_AddObject(m, "__author__", PyString_FromString(__author__));

	/* A bit ugly, but what the hell.. */
	snprintf(verstring, (ulong)10, "%ld", (ulong)LZMA_VERSION);
	major = verstring[0];
	snprintf(minor, (ulong)5, "%c%c%c", verstring[1], verstring[2], verstring[3]);
	snprintf(micro, (ulong)5, "%c%c%c", verstring[4], verstring[5], verstring[6]);
	if(verstring[7] == 0)
		s = "alpha";
	else if(verstring[7] == 1)
		s = "beta";
	else
		s = "stable";

	ver = PyString_FromFormat("%c.%d.%d%s", major, atoi(minor), atoi(micro), s);
    	if (ver != NULL)
		PyModule_AddObject(m, "LZMA_VERSION", ver);

	PyModule_AddStringConstant(m, "__version__", VERSION);
}
