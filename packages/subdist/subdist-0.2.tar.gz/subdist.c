/**
 * subdist.c
 *Copyright (C) Ryan Ginstrom <software@ginstrom.com>
 *
 * MIT License
 **/
#include <Python.h>

#define SUBDIST_VERSION "0.2"
#define AUTHOR "Ryan Ginstrom"

static char
		subdist_doc[] =
				"This module uses Levenshtein distance to find fuzzy\n\
	substring matches.\n\n\
	Usage:\n\
	from subdist import substring\n\
	print substring(u\"needle\", u\"Find the needle in the haystack\")\n\n\
	MIT License";

static char
		subdist_substring_doc[] =
				"substring(needle, haystack)\n\
	\n\
	Return the Levenshtein (edit) distance of needle in haystack.\n\
	needle and haystack must be Unicode strings.";

static char
		subdist_get_score_doc[] =
				"get_score(needle, haystack)\n\
	\n\
	Return the fuzzy match of needle in haystack,\n\
	based on Levenshtein (edit) distance.\n\
	needle and haystack must be Unicode strings.";
    
// minimum of two values
long min2(size_t a, size_t b)
{
	if (a < b)
	{
		return a;
	}
	return b;
}

// minimum of three values
long min(size_t a, size_t b, size_t c)
{
	return min2(a, min2(b, c) ) ;
}

// fuzzy substring match
long substring_c(size_t needle_len, Py_UNICODE *needle_str,
		size_t haystack_len, Py_UNICODE *haystack_str)
{
	// keep static buffers around to avoid allocating memory each call
	static size_t *row1 = 0;
	static size_t *row2 = 0;
	static size_t row_size = 0;

	// ensure our static rows are large enough
	if (row_size < haystack_len+1)
	{
		if (row1)
		{
			free(row1) ;
		}
		if (row2)
		{
			free(row2) ;
		}
		row_size = haystack_len+1;
		row1 = (size_t*)calloc(row_size, sizeof(size_t));
		row2 = (size_t*)calloc(row_size, sizeof(size_t));
		if (!row1 || !row2) // Allocation failed
		{
			PyErr_SetString(PyExc_MemoryError, "Out of memory!");
			return -1;
		}
	}

	// init first row
	size_t i = 0;
	for (i = 0; i <= haystack_len; ++i)
	{
		row1[i] = 0;
	}

	size_t cost = 0;

	// Fill the matrix costs
	size_t j = 0;
	for (i = 0; i < needle_len; ++i)
	{
		row2[0] = i+1;

		for (j = 0; j < haystack_len; ++j)
		{
			cost = 1;
			if (needle_str[i] == haystack_str[j])
			{
				cost = 0;
			}

			row2[j+1] = min(row1[j+1]+1, //  deletion
					row2[j]+1, // insertion
					row1[j]+cost) // substitution
			;
		}

		// row1 = row2
		for (j = 0; j <= haystack_len; ++j)
		{
			row1[j] = row2[j];
		}
	}

	// return min(row1)
	long min_cost = needle_len;
	for (i = 1; i <= haystack_len; ++i)
	{
		if (row1[i] < min_cost)
		{
			min_cost = row1[i];
		}
	}
	return min_cost;
}

int parse_unicode_objects(const char* funcname, PyObject *args,
		PyObject **arg1, PyObject **arg2)
{
	if (!PyArg_UnpackTuple(args, funcname, 2, 2, arg1, arg2))
	{
		PyErr_SetString(PyExc_RuntimeError, "Invalid args");
		return -1;
	}

	// make sure we've got two Unicode strings
	if ( !PyUnicode_Check(*arg1) || !PyUnicode_Check(*arg2) )
	{
		char err_msg[512];
		sprintf(err_msg, "%s requires two Unicode strings.", funcname) ;
		PyErr_SetString(PyExc_TypeError, err_msg);
		return -1;
	}
	return 1;
}

static PyObject* substring_py(PyObject *self, PyObject *args)
{
	// Unpack our arguments
	PyObject *needle, *haystack;
	if (parse_unicode_objects("substring", args, &needle, &haystack) < 0)
	{
		return NULL;
	}

	// Call the pure-C function with nice C data types
	long distance = substring_c(PyUnicode_GET_SIZE(needle),
			PyUnicode_AS_UNICODE(needle), PyUnicode_GET_SIZE(haystack),
			PyUnicode_AS_UNICODE(haystack) ) ;

	if (distance < 0)
	{
		return NULL;
	}
	return PyInt_FromLong(distance);
}

static PyObject* get_score_py(PyObject *self, PyObject *args)
{
	// Unpack our arguments
	PyObject *needle, *haystack;
	if (parse_unicode_objects("substring", args, &needle, &haystack) < 0)
	{
		return NULL;
	}

    long needle_len = PyUnicode_GET_SIZE(needle) ;
	if (needle_len == 0) // avoid divide by zero errors
	{
		return PyFloat_FromDouble(0.0) ;
	}

	// Call the pure-C function with nice C data types
	long distance = substring_c(needle_len,
			PyUnicode_AS_UNICODE(needle), 
            PyUnicode_GET_SIZE(haystack),
			PyUnicode_AS_UNICODE(haystack) ) ;

	double score = ((double)needle_len - (double)distance) / (double)needle_len ;
	return PyFloat_FromDouble(score);
}

static PyMethodDef subdist_methods[] =
{
{ "get_score", get_score_py, METH_VARARGS, subdist_get_score_doc },
{ "substring", substring_py, METH_VARARGS, subdist_substring_doc },
{ NULL, NULL } /* sentinel */
};

PyMODINIT_FUNC initsubdist(void)
{
	PyObject *module = Py_InitModule3("subdist", subdist_methods, subdist_doc);
	PyModule_AddStringConstant(module, "__version__", 
	SUBDIST_VERSION);
	PyModule_AddStringConstant(module, "__author__", 
	AUTHOR);
}
