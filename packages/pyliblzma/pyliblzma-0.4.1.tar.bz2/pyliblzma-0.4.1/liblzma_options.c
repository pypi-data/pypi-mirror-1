#include "liblzma_options.h"

PyDoc_STRVAR(LZMAOptions__doc__,
"This class describes the different LZMA compression options and holds the\n\
different min and max value constants for these in the variables.\n\
\n\
\n");

static PyMemberDef LZMAOptions_members[12];

static PyObject *mode, *mf, *format;

static PyObject *
LZMAOptions_repr(LZMAOptionsObject *obj)
{
	return PyString_FromFormat("%s singleton for accessing descriptors", obj->ob_type->tp_name);
}

static void
LZMAOptions_dealloc(LZMAOptionsObject* self)
{
	Py_XDECREF(self->eopm);
	Py_XDECREF(self->level);
	Py_XDECREF(self->dict_size);
	Py_XDECREF(self->lc);
	Py_XDECREF(self->lp);
	Py_XDECREF(self->pb);
	Py_XDECREF(self->mode_dict);
	Py_XDECREF(self->mode);
	Py_XDECREF(self->nice_len);
	Py_XDECREF(self->mf_dict);
	Py_XDECREF(self->mf);
	Py_XDECREF(self->depth);
	self->ob_type->tp_free((PyObject*)self);
}

PyObject *
LZMA_options_get(lzma_options_lzma lzma_options){
	PyObject * options = PyDict_New();
	PyMapping_SetItemString(options, "dict_size", PyInt_FromLong((long)lzma_options.dict_size));
	PyMapping_SetItemString(options, "lc", PyInt_FromLong((long)lzma_options.lc));
	PyMapping_SetItemString(options, "lp", PyInt_FromLong((long)lzma_options.lp));
	PyMapping_SetItemString(options, "pb", PyInt_FromLong((long)lzma_options.pb));
	PyMapping_SetItemString(options, "mode", PyDict_GetItem(mode, PyInt_FromLong((long)lzma_options.mode)));
	PyMapping_SetItemString(options, "nice_len", PyInt_FromLong((long)lzma_options.nice_len));
	PyMapping_SetItemString(options, "mf", PyDict_GetItem(mf, PyInt_FromLong((long)lzma_options.mf)));
	PyMapping_SetItemString(options, "depth", PyInt_FromLong((long)lzma_options.depth));
	return options;
}

/* This function is for parsing the options given for compression, since we have both a
 * one shot compress function and a sequential compressor object class, we'll share
 * this code amongst them.
 */
bool
init_lzma_options(const char *funcName, PyObject *kwargs, lzma_options_lzma *options){
	const char *argtypes = "|iiiiiiOO:";
	PyObject *args;
	char argstring[strlen(argtypes)+strlen(funcName)+2];
    	static char *kwlist[] = {"dict_size",
		"lc", "lp", "pb", "nice_len",
		"depth", "mode", "mf", NULL};
	PyObject *mf_key = NULL, *mode_key = NULL;

	if(kwargs != NULL){
		PyObject* levelString = PyString_FromString("level");
		if(PyDict_Contains(kwargs, levelString)){
			uint8_t level =  (uint8_t)PyInt_AsLong(PyDict_GetItem(kwargs, levelString));
			PyDict_DelItem(kwargs, levelString);
			CHECK_RANGE(level, LZMA_BEST_SPEED, LZMA_BEST_COMPRESSION, "compression level must be between %d and %d, got %d");
			lzma_lzma_preset(options, level);
		}
	}

	/* This is quite simple now, just added for future compatibility.. */
	if(kwargs != NULL){
		PyObject* formatString = PyString_FromString("format");
		if(PyDict_Contains(kwargs, formatString)){
			PyObject* myFormat = PyDict_GetItem(kwargs, formatString);
			PyDict_DelItem(kwargs, formatString);

			if(!(&PyTuple_Type)->tp_as_sequence->sq_contains(format, myFormat)){
				PyErr_SetObject(PyExc_ValueError,
					PyString_Format(PyString_FromString(
					"only LZMA_Alone ('%s') format is currently supported"),
					format));
				return false;
			}
		}
	}

	/* We create an empty tuple since we only want to parse keywords */
	args = PyTuple_New(0);
	snprintf(argstring, strlen(argtypes)+strlen(funcName)+2, "%s%s\n", argtypes, funcName);
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, argstring, kwlist,
				&options->dict_size, &options->lc, &options->lp, &options->pb,
				&options->nice_len, &options->depth, &mode_key, &mf_key))
		return false;
	Py_XDECREF(args);
	CHECK_RANGE(options->dict_size, LZMA_DICT_SIZE_MIN, LZMA_DICT_SIZE_MAX,
			"dict_size must be between %d and %d, got %d");
    	CHECK_RANGE(options->lc, LZMA_LCLP_MIN, LZMA_LCLP_MAX,
			"lc must be between %d and %d, got %d");
    	CHECK_RANGE(options->lp, LZMA_LCLP_MIN, LZMA_LCLP_MAX,
		       	"lp must be between %d and %d, got %d");
    	CHECK_RANGE(options->pb, LZMA_PB_MIN, LZMA_PB_MAX,
		       	"pb must be between %d and %d, got %d");
    	CHECK_RANGE(options->nice_len, LZMA_NICE_LEN_MIN, LZMA_NICE_LEN_MAX,
		       	"fast_bytes must be between %d and %d, got %d");
	if((int)options->depth < 0){
		PyErr_Format(PyExc_ValueError, "depth must be >= 0");
		return false;
	}

	/* FIXME: This could be done a lot simpler.. */
	if(mode_key){
		options->mode = LZMA_MODE_INVALID;
		if(PyInt_Check(mode_key))
			options->mode = PyInt_AsLong(mode_key);
		else
			if(PyString_Check(mode_key) && PyDict_Contains(mode, mode_key))
				options->mode = PyInt_AsLong(PyDict_GetItem(mode, mode_key));
			else if(PyString_Check(mode_key)){
				PyObject *key, *value;
				Py_ssize_t pos = 0;
				
				while (PyDict_Next(mode, &pos, &key, &value)) {
					if(PyObject_RichCompareBool(mode_key,value,Py_EQ)){
						options->mode = PyInt_AsLong(key);
						break;
					}
				}
			}
		}
	Py_XDECREF(mode_key);
	switch(options->mode){
		case(LZMA_MODE_FAST):
		case(LZMA_MODE_NORMAL):
			break;
		case(LZMA_MODE_INVALID):
		default:
			PyErr_SetObject(PyExc_ValueError,
					PyString_Format(PyString_FromString(
					"mode must be either '%s' or '%s'"),
					PyList_AsTuple(PyDict_Values(mode))));
			return false;
	}

	if(mf_key){
		options->mf = LZMA_MF_INVALID;
		if(PyInt_Check(mf_key))
			options->mf = PyInt_AsLong(mf_key);
		else if(PyString_Check(mf_key) && PyDict_Contains(mf, mf_key))
			options->mf = PyInt_AsLong(PyDict_GetItem(mf, mf_key));
		else if(PyString_Check(mf_key)){
			PyObject *key, *value;
			Py_ssize_t pos = 0;
			
			while (PyDict_Next(mf, &pos, &key, &value)) {
				if(PyObject_RichCompareBool(mf_key,value,Py_EQ)){
					options->mf = PyInt_AsLong(key);
					break;
				}
			}
		}
	}
	Py_XDECREF(mf_key);
	switch(options->mf){
		case(LZMA_MF_HC3):
		case(LZMA_MF_HC4):
		case(LZMA_MF_BT2):
		case(LZMA_MF_BT3):
		case(LZMA_MF_BT4):
			break;
		case(LZMA_MF_INVALID):
		default:
			PyErr_SetObject(PyExc_ValueError,
					PyString_Format(PyString_FromString(
					"mf must be either '%s', '%s', '%s', '%s' or '%s'"),
					PyList_AsTuple(PyDict_Values(mf))));
			return false;
	}
	return true;
}

/* Maybe not the best way, but it will at least prevent new instances.. */
static PyObject *
LZMAOptions_alloc(PyTypeObject *type, Py_ssize_t nitems)
{
	LZMAOptionsObject *self = (LZMAOptionsObject*)PyType_GenericAlloc(type, nitems);
	PyObject *levelopts, *levelString, *mf_list;

	self->format = PyTuple_Pack(1, PyString_FromString("alone"));
	format = self->format;
	self->eopm = PyTuple_Pack(2, Py_False, Py_True);
	self->level = PyTuple_Pack(2, PyInt_FromLong((ulong)LZMA_BEST_SPEED),
			PyInt_FromLong((ulong)LZMA_BEST_COMPRESSION));
	self->dict_size = PyTuple_Pack(2, PyInt_FromLong((ulong)LZMA_DICT_SIZE_MIN),
			PyInt_FromLong((ulong)LZMA_DICT_SIZE_MAX));
	self->lc = PyTuple_Pack(2, PyInt_FromLong((ulong)LZMA_LCLP_MIN),
			PyInt_FromLong((ulong)LZMA_LCLP_MAX));
	self->lp = PyTuple_Pack(2, PyInt_FromLong((ulong)LZMA_LCLP_MIN),
			PyInt_FromLong((ulong)LZMA_LCLP_MAX));
	self->pb = PyTuple_Pack(2, PyInt_FromLong((ulong)LZMA_PB_MIN),
			PyInt_FromLong((ulong)LZMA_PB_MAX));
	self->mode_dict = PyDict_New();
	self->nice_len = PyTuple_Pack(2, PyInt_FromLong((ulong)LZMA_NICE_LEN_MIN),
		       	PyInt_FromLong((ulong)LZMA_NICE_LEN_MAX));
	self->mf_dict = PyDict_New();
	self->depth = PyInt_FromLong(0);

	PyDict_SetItem(self->mode_dict, PyInt_FromLong((ulong)LZMA_MODE_FAST),
			PyString_FromString("fast"));
	PyDict_SetItem(self->mode_dict, PyInt_FromLong((ulong)LZMA_MODE_NORMAL),
			PyString_FromString("best"));
	mode = self->mode_dict;

	self->mode = PyList_AsTuple(PyDict_Values(self->mode_dict));
	PyDict_SetItem(self->mf_dict, PyInt_FromLong((ulong)LZMA_MF_HC3),
			PyString_FromString("hc3"));
	PyDict_SetItem(self->mf_dict, PyInt_FromLong((ulong)LZMA_MF_HC4),
			PyString_FromString("hc4"));
	PyDict_SetItem(self->mf_dict, PyInt_FromLong((ulong)LZMA_MF_BT2),
			PyString_FromString("bt2"));
	PyDict_SetItem(self->mf_dict, PyInt_FromLong((ulong)LZMA_MF_BT3),
			PyString_FromString("bt3"));
	PyDict_SetItem(self->mf_dict, PyInt_FromLong((ulong)LZMA_MF_BT4),
			PyString_FromString("bt4"));
	mf_list = PyDict_Values(self->mf_dict);
	PyList_Sort(mf_list);
	self->mf =  PyList_AsTuple(mf_list);
	Py_DECREF(mf_list);
	mf = self->mf_dict;
	Py_INCREF(self);

	LZMAOptions_members[0] = MEMBER_DESCRIPTOR("eopm", T_OBJECT, eopm,
"End of payload marker (%s / %s)\n\
The LZMA_Alone format cannot have both uncompressed size field in the header\n\
and end of payload marker. If setting the end of payload marker, uncompressed\n\
size will not be stored in the header.\n");

	levelString = PyString_FromString(
"Compression preset level (%u - %u)\n\
This will automatically set the values for the various compression options.\n\
Setting any of the other compression options at the same time as well will\n\
override the specific value set by this preset level.\n\
\n\
Preset level settings:\n\
level\t lc\t lp\t dict\t\t pb\t mode\t mf\t fb\t mfc\n");
	levelopts = PyString_FromString("%%d\t %u\t %u\t %u  \t %u\t %s\t %s\t %u\t %u\n");
	
	{off_t i;
	for(i = LZMA_BEST_COMPRESSION; i >= LZMA_BEST_SPEED; i--){
		lzma_options_lzma options;
		lzma_lzma_preset(&options, i-1);
		PyObject *settingsString = PyString_Format(levelopts,
			       	PyList_AsTuple(PyDict_Values(LZMA_options_get(options))));
		PyObject *levelNum = PyString_Format(settingsString, PyInt_FromLong(i));
		PyString_Concat(&levelString,levelNum);
		Py_DECREF(settingsString);
		Py_DECREF(levelNum);
	}}
	Py_DECREF(levelopts);

	LZMAOptions_members[1] = MEMBER_DESCRIPTOR("level", T_OBJECT, level, PyString_AsString(levelString));
	Py_DECREF(levelString);
	LZMAOptions_members[2] = MEMBER_DESCRIPTOR("dict_size", T_OBJECT, dict_size,
"Dictionary size in bytes (%u - %u)\n\
Dictionary size indicates how many bytes of the recently processed\n\
uncompressed data is kept in memory. One method to reduce size of\n\
the uncompressed data is to store distance-length pairs, which\n\
indicate what data to repeat from the dictionary buffer. Thus,\n\
the bigger the dictionary, the better compression ratio usually is.\n");
	LZMAOptions_members[3] = MEMBER_DESCRIPTOR("lc", T_OBJECT, lc,
"Number of literal context bits (%u - %u)\n\
How many of the highest bits of the previous uncompressed\n\
eight-bit byte (also known as `literal') are taken into\n\
account when predicting the bits of the next literal.\n\
\n\
There is a limit that applies to literal context bits and literal\n\
position bits together: lc + lp <= 4. Without this limit the\n\
decoding could become very slow, which could have security related\n\
results in some cases like email servers doing virus scanning.");
	LZMAOptions_members[4] = MEMBER_DESCRIPTOR("lp", T_OBJECT, lp,
"Number of literal position bits (%u - %u)\n\
How many of the lowest bits of the current position (number\n\
of bytes from the beginning of the uncompressed data) in the\n\
uncompressed data is taken into account when predicting the\n\
bits of the next literal (a single eight-bit byte).\n");
	LZMAOptions_members[5] = MEMBER_DESCRIPTOR("pb", T_OBJECT, pb,
"Number of position bits Position bits (%u - %u)\n\
How many of the lowest bits of the current position in the\n\
uncompressed data is taken into account when estimating\n\
probabilities of matches. A match is a sequence of bytes for\n\
which a matching sequence is found from the dictionary and\n\
thus can be stored as distance-length pair.\n\
\n\
Example: If most of the matches occur at byte positions\n\
of 8 * n + 3, that is, 3, 11, 19, ... set pos_bits to 3,\n\
because 2**3 == 8.\n");
	LZMAOptions_members[6] = MEMBER_DESCRIPTOR("mode", T_OBJECT, mode,
"Available modes: '%s' or '%s'.\n\
Fast mode is usually at its best when combined with a hash chain match finder.\n\
Best is usually notably slower than fast mode. Use this together with binary\n\
tree match finders to expose the full potential of the LZMA encoder.");
	LZMAOptions_members[7] = MEMBER_DESCRIPTOR("nice_len", T_OBJECT, nice_len,
"Nice lengt of a match (also known as number of fast bytes) (%u - %u)\n\
Nice length of match determines how many bytes the encoder\n\
compares from the match candidates when looking for the best\n\
match. Bigger fast bytes value usually increase both compression\n\
ratio and time.\n");
	LZMAOptions_members[8] = MEMBER_DESCRIPTOR("mf", T_OBJECT, mf,
"Match finder has major effect on both speed and compression ratio.\n\
Usually hash chains are faster than binary trees.\n\
Available match finders:\n\
'%s': Binary Tree with 2 bytes hashing\n\
       Memory requirements: 9.5 * dict_size + 4 MiB\n\
'%s': Binary Tree with 3 bytes hashing\n\
       Memory requirements: 11.5 * dict_size + 4 MiB\n\
'%s': Binary Tree with 4 bytes hashing\n\
       Memory requirements: 11.5 * dict_size + 4 MiB\n\
'%s': Hash Chain with 3 bytes hashing\n\
'%s': Hash Chain with 4 bytes hashing\n\
       Memory requirements: 7.5 * dict_size + 4 MiB\n");
	LZMAOptions_members[9] = MEMBER_DESCRIPTOR("depth", T_INT, depth,
"Depth (also known as match finder cycles)\n\
Higher values give slightly better compression ratio but\n\
decrease speed. Use special value %u to let liblzma use\n\
match-finder-dependent default value.\n");

	LZMAOptions_members[10] = MEMBER_DESCRIPTOR("format", T_OBJECT, format,
"File format to use for compression:\n\
'%s': LZMA_Alone format used by older lzma utils. Currently default and only\n\
         supported format. Support for the newer formats will be added in the\n\
         future and the default format will then change as well. If you want\n\
         to ensure to always use this format (ie. beneficial for backwards\n\
         compatibility etc.), you should set this as it won't be default\n\
         in the future.\n");

	LZMAOptions_members[11] = (PyMemberDef){NULL, 0, 0, 0, NULL};	/* Sentinel */

	return (PyObject*)self;
}

/* Don't allow messing with this data.. */
static int8_t
LZMAOptions_setattr(__attribute__((unused)) LZMAOptionsObject *self, const char *name)
{
    (void)PyErr_Format(PyExc_RuntimeError, "Read-only attribute: %s\n", name);
    return -1;
}

PyTypeObject LZMAOptions_Type = {
	0,					/*ob_refcnt*/
	0,					/*ob_type*/
	0,					/*ob_size*/
	"liblzma.LZMAOptions",			/*tp_name*/
	sizeof(LZMAOptionsObject),		/*tp_basicsize*/
	0,					/*tp_itemsize*/
	(destructor)LZMAOptions_dealloc,	/*tp_dealloc*/
	0,					/*tp_print*/
	0,					/*tp_getattr*/
	(setattrfunc)LZMAOptions_setattr,	/*tp_setattr*/
	0,					/*tp_compare*/
	(reprfunc)LZMAOptions_repr,		/*tp_repr*/
	0,					/*tp_as_number*/
	0,					/*tp_as_sequence*/
	0,					/*tp_as_mapping*/
	0,					/*tp_hash*/
	0,					/*tp_call*/
	0,					/*tp_str*/
	0,					/*tp_getattro*/
	0,					/*tp_setattro*/
	0,					/*tp_as_buffer*/
	0,					/*tp_flags*/
	LZMAOptions__doc__,         		/*tp_doc*/
	0,					/*tp_traverse*/
	0,					/*tp_clear*/
	0,					/*tp_richcompare*/
	0,					/*tp_weaklistoffset*/
	0,					/*tp_iter*/
	0,					/*tp_iternext*/
	0,					/*tp_methods*/
	LZMAOptions_members,			/*tp_members*/
	0,					/*tp_getset*/
	0,					/*tp_base*/
	0,					/*tp_dict*/
	0,					/*tp_descr_get*/
	0,					/*tp_descr_set*/
	0,					/*tp_dictoffset*/
	0,					/*tp_init*/
	LZMAOptions_alloc,			/*tp_alloc*/
	0,					/*tp_new*/
	0,					/*tp_free*/
	0,					/*tp_is_gc*/
	0,					/*tp_bases*/
	0,					/*tp_mro*/
	0,					/*tp_cache*/
	0,					/*tp_subclasses*/
	0,					/*tp_weaklist*/
	0					/*tp_del*/
};
