/**********************************************************************
 * Copyright (c) 2007-2008 David Carter <dcarter@arm4.org> and others.
 * All rights reserved.   This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: 
 * David Carter - Initial API and implementation
 **********************************************************************/

#include "Python.h"

#include <arm4.h>
#include <limits.h>

/* Check for version 3 or later */
#if PY_MAJOR_VERSION >= 3
#define IS_PY3K
#endif

#ifndef PyVarObject_HEAD_INIT
#define PyVarObject_HEAD_INIT(type, size) \
	PyObject_HEAD_INIT(type) size,
#endif

struct module_state
{
	PyObject *errorStatus;	/* This contains the status of the last call? */
	int enableExceptions;	/* Non-zero if exceptions are enabled */
};

#ifdef IS_PY3K
static struct PyModuleDef moduledef;

#define GETSTATE(m) ((struct module_state *) PyModule_GetState (m))
#define GETSTATE0 GETSTATE(PyState_FindModule (&moduledef))
#else
#define GETSTATE(m) (&g_state)
#define GETSTATE0 (&g_state)
static struct module_state g_state;
#endif

PyDoc_STRVAR(arm4_module_documentation,
"Python language bindings for the Application Response Measurement (ARM) Version 4.0 standard.\n"
"\n"
"This module provides a Python language implementation of the ARM 4.0\n"
"standard. At it's simplest, it's a straight exposure of the C language\n"
"bindings with enough concessions to make it fit the Python language.\n"
"\n"
"Usage:\n"
"\n"
"  import arm4\n"
"\n"
"  # Register\n"
"  app_id = arm4.register_application (\"Python test\")\n"
"  tran_id = arm4.register_transaction (app_id, \"Python hello world\")\n"
"\n"
"  # Start our application and transaction measurements\n"
"  app_handle = arm4.start_application (app_id, \"Example\")\n"
"  tran_handle = arm4.start_transaction (app_handle, tran_id)\n"
"\n"
"  # Do our work\n"
"  print 'Hello, world!'\n"
"\n"
"  # Stop our measurements\n"
"  arm4.stop_transaction (tran_handle) # Default status is arm4.ARM_STATUS_GOOD\n"
"  arm4.stop_application (app_handle)\n"
"\n"
"  # Finish up\n"
"  arm4.destroy_application (app_id)\n"
"\n"
"This is a simple example that doesn't make use of ARM's advanced\n"
"correlators or metrics. More examples can be found at http://www.arm4.org\n"
"\n"
"This module is based on the ARM Issue 4.0, Version 2 - C Binding standard. More information\n"
"can be found at http://www.opengroup.org/management/arm.htm\n"
);

/*--- Determine the strings used to parse the various integer types ---*/
#if INT_MAX == 2147483647l
#define PARSE_INT32_FMT  "i"
#define PARSE_UINT32_FMT  "I"
#elif LONG_MAX == 2147483647l
#define PARSE_INT32_FMT  "l"
#define PARSE_UINT32_FMT  "k"
#else
#error "can't determine 32bit integer type"
#endif /* INT_MAX == 2147483647l */

#if LONG_MAX > 2147483647l
#define PARSE_INT64_FMT  "l"
#define PARSE_UINT64_FMT "k"
#else
#define PARSE_INT64_FMT  "L"
#define PARSE_UINT64_FMT "K"
#endif /* LONG_MAX > 2147483647l */

#ifndef ARM_SUCCESS
#define ARM_SUCCESS		(0)
#endif

/*--- Define the local object types ---*/
static PyTypeObject ArmID_Type;
static PyTypeObject ArmHandle_Type;
static PyTypeObject ArmCorrelator_Type;
static PyTypeObject ArmArrivalTime_Type;
static PyTypeObject ArmBuffer_Type;
static PyTypeObject ArmSubbufferCharset_Type;
static PyTypeObject ArmSubbufferAppIdentity_Type;
static PyTypeObject ArmSubbufferAppContext_Type;
static PyTypeObject ArmSubbufferTranIdentity_Type;
static PyTypeObject ArmSubbufferTranContext_Type;
static PyTypeObject ArmSubbufferArrivalTime_Type;
static PyTypeObject ArmSubbufferMetricBindings_Type;
static PyTypeObject ArmSubbufferMetricValues_Type;
static PyTypeObject ArmSubbufferUser_Type;
static PyTypeObject ArmSubbufferSystemAddress_Type;
static PyTypeObject ArmSubbufferDiagDetail_Type;

#define ArmID_Object_Check(v)	PyObject_TypeCheck ((v), &ArmID_Type)
#define ArmHandle_Object_Check(v)	PyObject_TypeCheck ((v), &ArmHandle_Type)
#define ArmCorrelator_Object_Check(v)	PyObject_TypeCheck ((v), &ArmCorrelator_Type)
#define ArmArrivalTime_Object_Check(v)	PyObject_TypeCheck ((v), &ArmArrivalTime_Type)
#define ArmBuffer_Object_Check(v)	PyObject_TypeCheck ((v), &ArmBuffer_Type)
#define ArmSubbufferCharset_Object_Check(v)	PyObject_TypeCheck ((v), &ArmSubbufferCharset_Type)
#define ArmSubbufferAppIdentity_Object_Check(v)	PyObject_TypeCheck ((v), &ArmSubbufferAppIdentity_Type)
#define ArmSubbufferAppContext_Object_Check(v)	PyObject_TypeCheck ((v), &ArmSubbufferAppContext_Type)
#define ArmSubbufferTranIdentity_Object_Check(v)	PyObject_TypeCheck ((v), &ArmSubbufferTranIdentity_Type)
#define ArmSubbufferTranContext_Object_Check(v)	PyObject_TypeCheck ((v), &ArmSubbufferTranContext_Type)
#define ArmSubbufferArrivalTime_Object_Check(v)	PyObject_TypeCheck ((v), &ArmSubbufferArrivalTime_Type)
#define ArmSubbufferMetricBindings_Object_Check(v)	PyObject_TypeCheck ((v), &ArmSubbufferMetricBindings_Type)
#define ArmSubbufferMetricValues_Object_Check(v)	PyObject_TypeCheck ((v), &ArmSubbufferMetricValues_Type)
#define ArmSubbufferUser_Object_Check(v)	PyObject_TypeCheck ((v), &ArmSubbufferUser_Type)
#define ArmSubbufferSystemAddress_Object_Check(v)	PyObject_TypeCheck ((v), &ArmSubbufferSystemAddress_Type)
#define ArmSubbufferDiagDetail_Object_Check(v)	PyObject_TypeCheck ((v), &ArmSubbufferDiagDetail_Type)

static void
set_arm_error (arm_error_t error_code, const char *method_name)
{
	char error_message [ARM_MSG_BUFFER_LENGTH];
	arm_error_t status;

	status = arm_get_error_message (ARM_CHARSET_ASCII, error_code, error_message);
	if (status == ARM_SUCCESS)
		PyErr_Format (PyExc_RuntimeError, "%s() -> %d %s\n", method_name, error_code, error_message);
	else
		PyErr_Format (PyExc_RuntimeError, "%s() -> %d\n", method_name, error_code);
}

/*--- Define the arm_id_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_id_t	arm_id;
} ArmID;

static ArmID *
newArmID(arm_id_t *id_ptr)
{
	ArmID *self;

	self = PyObject_New(ArmID, &ArmID_Type);
	if (self == NULL)
		return NULL;

	/* By default the arm_id_t has no initializer */
	if (id_ptr == NULL)
		memset (&self->arm_id, 0, sizeof (arm_id_t));
	else
		memcpy (&self->arm_id, id_ptr, sizeof (arm_id_t));

	return self;
}

/* ArmID methods */

static void
ArmID_dealloc(ArmID *self)
{
	PyObject_Del(self);
}

PyDoc_STRVAR(ArmID_type__doc__, "Opaque wrapper for an ARM 4 ID structure.");

static PyTypeObject ArmID_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmID",			/*tp_name*/
	sizeof(ArmID),			/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmID_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmID_type__doc__,      /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	0,                      /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	0,                      /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_handle_*_t Python equivalents ---*/

typedef struct {
	PyObject_HEAD
	arm_int64_t	arm_handle;
} ArmHandle;

static ArmHandle *
newArmHandle(arm_int64_t handle)
{
	ArmHandle *self;

	self = PyObject_New(ArmHandle, &ArmHandle_Type);
	if (self == NULL)
		return NULL;

	self->arm_handle = handle;

	return self;
}

/* ArmHandle methods */

static void
ArmHandle_dealloc(ArmHandle *self)
{
	PyObject_Del(self);
}

PyDoc_STRVAR(ArmHandle_type__doc__, "Opaque wrapper for an ARM 4 handle structure.");

static PyTypeObject ArmHandle_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmHandle",		/*tp_name*/
	sizeof(ArmHandle),		/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmHandle_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmHandle_type__doc__,  /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	0,                      /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	0,                      /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_correlator_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_correlator_t	arm_correlator;
	PyObject	*x_attr;	/* Attributes dictionary */
} ArmCorrelator;

static ArmCorrelator *
newArmCorrelator(arm_correlator_t *corr_ptr)
{
	ArmCorrelator *self;

	self = PyObject_New(ArmCorrelator, &ArmCorrelator_Type);
	if (self == NULL)
		return NULL;

	/* By default the arm_id_t has no initializer */
	if (corr_ptr == NULL)
		memset (&self->arm_correlator, 0, sizeof (arm_correlator_t));
	else
		memcpy (&self->arm_correlator, corr_ptr, sizeof (arm_correlator_t));

	self->x_attr = NULL;

	return self;
}

/* ArmCorrelator methods */

static void
ArmCorrelator_dealloc(ArmCorrelator *self)
{
	Py_XDECREF(self->x_attr);
	PyObject_Del(self);
}

static void
stringify(unsigned char *in, char *out, int len)
{
    int i;
    char to_hex[] = { '0', '1', '2', '3', '4', '5', '6', '7',
                      '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', } ;

    for(i=0; i<len;i++) {
        out[2*i] = to_hex[(in[i]>>4) & 0x0f];
        out[1+2*i] = to_hex[in[i] & 0x0f];
    }

    out[2*len] = '\0';
}

static void
destringify(const char *in, unsigned char *out, int orig_len)
{
    int len=0;
    int i;
    int maxlen = orig_len * 2 + 1;

    while((in[len] != '\0') && isxdigit(in[len]) && (len < maxlen)) {
        len++;
    }

    /*
     * if (in[len] != '\0') at this point we're ignoring trailing non xdigit chars
     * also, len should be even, but we're not checking ...
     */
    for(i=0;i<(len/2);i++) {
        if(isdigit(in[2*i])) {
            if(isdigit(in[1+2*i])) {
                out[i] = ((in[2*i]-'0')<<4)|(0x0f & (in[1+2*i]-'0'));
            }
            else  {
                out[i] = ((in[2*i]-'0')<<4)|(0x0f & (10+toupper(in[1+2*i])-'A'));
            }
        }
        else {
            if(isdigit(in[1+2*i])) {
                out[i] = ((10+toupper(in[2*i])-'A')<<4)|(0x0f & (in[1+2*i]-'0'));
            }
            else {
                out[i] = ((10+toupper(in[2*i])-'A')<<4) |
                  (0x0f & (10+toupper(in[1+2*i])-'A'));
            }
        }
    }
}

static PyObject *
ArmCorrelator_str(ArmCorrelator *self, PyObject *args)
{
	arm_correlator_length_t length;
	arm_error_t status;
	PyObject *result;
	char correlator_string [ARM_CORR_MAX_LENGTH * 2 + 1];

	status = arm_get_correlator_length(&(self->arm_correlator), &length);
	if (status >= 0)
	{
		stringify ((unsigned char *) &(self->arm_correlator), correlator_string, length);
#ifdef IS_PY3K
		result = PyBytes_FromString(correlator_string);
#else
		result = PyString_FromString(correlator_string);
#endif
	}
	else
	{
		result = Py_None;
		Py_INCREF(Py_None);
	}

	return result;
}

PyDoc_STRVAR(ArmCorrelator_from_string__doc__,
"from_string (hex): Set the user name\n"
"\n"
"DESCRIPTION\n"
"  Sets correlator value from its hexadecimal representation.\n"
"\n"
"  This is useful for correlators passed into the application from an external source, such as\n"
"  the Apache web server.\n"
"PARAMETERS\n"
"  hex   A string containing a hexadecimal representation of a correlator. This is the same\n"
"        as produced by str().\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmCorrelator_from_string(ArmCorrelator *self, PyObject *args)
{
	const char *correlator_string;

	/* Get the hex version of the string */
	if (!PyArg_ParseTuple(args, "s", &correlator_string))
		return NULL;

	destringify(correlator_string, (unsigned char *) &(self->arm_correlator), ARM_CORR_MAX_LENGTH);

	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(ArmCorrelator_length__doc__,
"length(): get length of correlator\n"
"\n"
"DESCRIPTION\n"
"  length() returns the length of a correlator, based on the length field within\n"
"  the correlator header. Note that this length is not necessarily the length of the\n"
"  buffer containing the correlator.\n"
"\n"
"  A correlator header contains a length field. length() is used to return the length. The function\n"
"  handles any required conversion from the network byte order used in the header and the endian\n"
"  (big versus little) of the platform. See generate_correlator() for a description of a correlator.\n"
"PARAMETERS\n"
"  None\n"
"RETURN VALUE\n"
"  The length of the correlator\n"
);

static PyObject *
ArmCorrelator_length(ArmCorrelator *self, PyObject *args)
{
	arm_correlator_length_t length;
	arm_error_t status;
	PyObject *result;

	status = arm_get_correlator_length(&(self->arm_correlator), &length);
	if (status >= 0)
	{
#ifdef IS_PY3K
		result = PyLong_FromLong(length);
#else
		result = PyInt_FromLong(length);
#endif
	}
	else
	{
		result = Py_None;
		Py_INCREF(Py_None);
	}

	return result;
}

PyDoc_STRVAR(ArmCorrelator_get_flags__doc__,
"get_flags(flags): get value of flag\n"
"\n"
"DESCRIPTION\n"
"  get_flags() returns the value of a specified flag in the correlator.\n"
"\n"
"  A correlator contains bit flags, and get_flags() is used to test the value of\n"
"  those flags. See generate_correlator() for a description of a correlator.\n"
"PARAMETERS\n"
"  flags     An enumerated value that indicates which flag's value is requested. The\n"
"            enumerated values are:\n"
"            ARM_CORR_FLAGNUM_APP_TRACE = Application trace flag\n"
"            ARM_CORR_FLAGNUM_AGENT_TRACE = Agent trace flag\n"
"RETURN VALUE\n"
"  Boolean object indicating whether the flag is set.\n"
);

static PyObject *
ArmCorrelator_get_flags (ArmCorrelator *self, PyObject *args)
{

    arm_error_t status;
    arm_int32_t flag_num;
	arm_boolean_t flag;

	/*
	 * Supported calling signatures:
	 *	get_flags (flags)
	 */
    if (!PyArg_ParseTuple(args, PARSE_INT32_FMT, &flag_num))
        return NULL;

	status = arm_get_correlator_flags(
		&(self->arm_correlator),
		flag_num,
		&flag);
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_get_correlator_flags");
		return NULL;
	}

	/* Return the flag value */
	return PyBool_FromLong (flag);
}

static PyMethodDef ArmCorrelator_methods[] = {
	{"from_string",	(PyCFunction)ArmCorrelator_from_string,	METH_VARARGS, ArmCorrelator_from_string__doc__},
	{"length",	    (PyCFunction)ArmCorrelator_length,	    METH_NOARGS,  ArmCorrelator_length__doc__},
	{"get_flags",	(PyCFunction)ArmCorrelator_get_flags,	METH_VARARGS, ArmCorrelator_get_flags__doc__},
	{NULL,		NULL}		/* sentinel */
};

PyDoc_STRVAR(ArmCorrelator_type__doc__, "Opaque wrapper for an ARM 4 correlator structure.");

static PyTypeObject ArmCorrelator_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmCorrelator",	/*tp_name*/
	sizeof(ArmCorrelator),	/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmCorrelator_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	(reprfunc)ArmCorrelator_str, /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmCorrelator_type__doc__, /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	ArmCorrelator_methods,	/*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	0,                      /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_arrival_time_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_arrival_time_t	arm_time;
} ArmArrivalTime;

static ArmArrivalTime *
newArmArrivalTime(void)
{
	ArmArrivalTime *self;
	arm_arrival_time_t arrival;

	/* Always get the time first! */
	arm_get_arrival_time(&arrival);

	self = PyObject_New(ArmArrivalTime, &ArmArrivalTime_Type);
	if (self == NULL)
		return NULL;

	self->arm_time = arrival;

	return self;
}

/* ArmArrivalTime methods */

static void
ArmArrivalTime_dealloc(ArmArrivalTime *self)
{
	PyObject_Del(self);
}

PyDoc_STRVAR(ArmArrivalTime_type__doc__,
			 "Opaque wrapper for an ARM 4 arrival time structure.\n"
			 "This is created by calling get_arrival_time ()\n");

static PyTypeObject ArmArrivalTime_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmArrivalTime",		/*tp_name*/
	sizeof(ArmArrivalTime),		/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmArrivalTime_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmArrivalTime_type__doc__, /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	0,                      /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	0,                      /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_subbuffer_charset_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_subbuffer_charset_t	arm_buffer;
} ArmSubbufferCharset;

static PyObject *
newArmSubbufferCharset(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ArmSubbufferCharset *self;

    self = (ArmSubbufferCharset *)type->tp_alloc(type, 0);
    if (self != NULL) {
		self->arm_buffer.header.format = ARM_SUBBUFFER_CHARSET;
		self->arm_buffer.charset = ARM_CHARSET_ASCII;
		self->arm_buffer.flags = 0;
    }

    return (PyObject *)self;
}

static int
ArmSubbufferCharset_init(ArmSubbufferCharset *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"charset", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", kwlist, 
                                      &(self->arm_buffer.charset)))
        return -1; 

    return 0;
}

/* ArmSubbufferCharset methods */

static void
ArmSubbufferCharset_dealloc(ArmSubbufferCharset *self)
{
	PyObject_Del(self);
}

PyDoc_STRVAR(ArmSubbufferCharset_type__doc__,
"Applications may specify on register_application() the character set encoding for all\n"
"strings passed by the application. An ARM library must support certain encodings, depending on\n"
"the platform (see Table 1). The application may always use one of the mandatory encodings.\n"
"This module defines names of the form ARM_CHARSET_* for all the mandatory\n"
"encodings. The application may optionally ask the ARM library if another encoding is supported\n"
"using is_charset_supported().\n"
"\n"
"When the application registers with register_application(), it may optionally provide the\n"
"character set encoding sub-buffer. In the sub-buffer, the application specifies the MIBenum\n"
"value of a character set encoding that has been assigned by the IANA (Internet Assigned\n"
"Numbers Authority - see www.iana.org). The MIBenum value in the sub-buffer should only be\n"
"either a mandatory encoding for the platform or a MIBenum value for which support has been\n"
"verified using is_charset_supported().\n"
"\n"
"The list of supported encodings must restrict itself to those that do not contain any embedded\n"
"null bytes. Exceptions are permitted for character sets that have fixed-length characters (e.g.,\n"
"two bytes) and that do not allow a character of all zeros (e.g., 0x0000). These include UTF-\n"
"16LE, UTF-16BE, and UTF-16 (MIBenum values 1013, 1014, 1015). For these encodings, there\n"
"will be a convention that a character of all zeros is the null-termination character.\n"
);

static PyTypeObject ArmSubbufferCharset_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmSubbufferCharset",		/*tp_name*/
	sizeof(ArmSubbufferCharset),	/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmSubbufferCharset_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmSubbufferCharset_type__doc__, /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	0,                      /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	(initproc)ArmSubbufferCharset_init, /*tp_init*/
	0,                      /*tp_alloc*/
	newArmSubbufferCharset, /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_subbuffer_app_identity_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_subbuffer_app_identity_t arm_buffer;
	PyObject  *x_attr;
} ArmSubbufferAppIdentity;

static PyObject *
newArmSubbufferAppIdentity(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ArmSubbufferAppIdentity *self;

    self = (ArmSubbufferAppIdentity *)type->tp_alloc(type, 0);
    if (self != NULL) {
		self->arm_buffer.header.format = ARM_SUBBUFFER_APP_IDENTITY;
		self->arm_buffer.identity_property_count = 0;
		self->arm_buffer.identity_property_array = NULL;
		self->arm_buffer.context_name_count = 0;
		self->arm_buffer.context_name_array = NULL;
    }

	return (PyObject *)self;
}

/* ArmSubbufferAppIdentity methods */

static void
ArmSubbufferAppIdentity_free_property (ArmSubbufferAppIdentity *self, int index)
{
	if (self->arm_buffer.identity_property_array [index].name != NULL)
		free ((char *) self->arm_buffer.identity_property_array [index].name);
	if (self->arm_buffer.identity_property_array [index].value != NULL)
		free ((char *) self->arm_buffer.identity_property_array [index].value);
}

static void
ArmSubbufferAppIdentity_free_properties (ArmSubbufferAppIdentity *self)
{
	int i;

	if (self->arm_buffer.identity_property_array != NULL)
	{
		for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
			ArmSubbufferAppIdentity_free_property (self, i);
		free ((char *) self->arm_buffer.identity_property_array);
	}
}

static void
ArmSubbufferAppIdentity_free_context_name (ArmSubbufferAppIdentity *self, int index)
{
	if (self->arm_buffer.context_name_array [index] != NULL)
		free ((char *) self->arm_buffer.context_name_array [index]);
}


static void
ArmSubbufferAppIdentity_free_context (ArmSubbufferAppIdentity *self)
{
	int i;

	if (self->arm_buffer.context_name_array != NULL)
	{
		for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
			ArmSubbufferAppIdentity_free_context_name (self, i);
		free (self->arm_buffer.context_name_array);
	}
}

static void
ArmSubbufferAppIdentity_dealloc(ArmSubbufferAppIdentity *self)
{
	ArmSubbufferAppIdentity_free_properties (self);
	ArmSubbufferAppIdentity_free_context (self);

	PyObject_Del(self);
}

PyDoc_STRVAR(ArmSubbufferAppIdentity_set_property__doc__,
"set_property(index, name, value): Set an application identity name/value pair\n"
"\n"
"DESCRIPTION\n"
"  set_property() sets the name/value pair in the specified index.\n"
"PARAMETERS\n"
"  index     The array index of a property value between 0 and 19\n"
"            The array index of a property value in the value array is bound to the property name at the\n"
"            same index in the name array. Moving the (name,value) pair to a different index does not\n"
"            affect the identity of the application. For example, if an application registers once with a\n"
"            name A and a value X in array indices 0 and once with the same name and value in array\n"
"            indices 1, the registered identity has not changed.\n"
"  name      A string representing the name part of the (name,value) pair. Each string has a maximum\n"
"            length of 127 characters. If the string is zero-length, the (name,value) pair is ignored.\n"
"            Names should not contain trailing blank characters or consist of only blank characters.\n"
"  value     A string representing the value part of the (name,value) pair. Each string has a maximum\n"
"            length of 255 characters. If the string is zero-length, the (name,value) pair is ignored.\n"
"            Values should not contain trailing blank characters or consist of only blank characters.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferAppIdentity_set_property (ArmSubbufferAppIdentity *self, PyObject *args)
{
	int index;
	const char *name_ptr;
	const char *value_ptr;
	int i;

	/*
	 * Supported calling signatures:
	 *	set_property (index, name, value)
	 */
    if (!PyArg_ParseTuple(args, "iss", &index, &name_ptr, &value_ptr))
        return NULL;
	if ((index < ARM_PROPERTY_MIN_ARRAY_INDEX) || (index > ARM_PROPERTY_MAX_ARRAY_INDEX))
		return NULL;

	/* Allocate the property array as required */
	if (self->arm_buffer.identity_property_array == NULL)
	{
		self->arm_buffer.identity_property_array = calloc (sizeof (arm_property_t), ARM_PROPERTY_MAX_COUNT);
		for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
		{
			((arm_property_t *) self->arm_buffer.identity_property_array) [i].name = NULL;
			((arm_property_t *) self->arm_buffer.identity_property_array) [i].value = NULL;
		}
	}

	/* Prevent memory loss when overwriting a value */
	ArmSubbufferAppIdentity_free_property (self, index);

	/* Copy the names */
	((arm_property_t *) self->arm_buffer.identity_property_array) [index].name = strndup (name_ptr, ARM_PROPERTY_NAME_MAX_CHARS);
	((arm_property_t *) self->arm_buffer.identity_property_array) [index].value = strndup (name_ptr, ARM_PROPERTY_VALUE_MAX_CHARS);

	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(ArmSubbufferAppIdentity_set_context_name__doc__,
"set_context_name(index, name): Set an application context name\n"
"\n"
"DESCRIPTION\n"
"  set_context_name() sets the name in the specified index.\n"
"PARAMETERS\n"
"  index     The array index of a property value between 0 and 19\n"
"\n"
"            If a name is repeated in the array, the name and its corresponding value (in the application\n"
"            context sub-buffer) are ignored, and the first instance of the name in the array (and its\n"
"            corresponding value) is used.\n"
"  name      A string representing the name part of the (name,value) pair. Each string has a maximum\n"
"            length of 127 characters. If the string is zero-length, the (name,value) pair is ignored.\n"
"            The values are provided in the ArmSubbufferApplicationContext object. Names should not contain\n"
"            trailing blank characters or consist of only blank characters.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferAppIdentity_set_context_name (ArmSubbufferAppIdentity *self, PyObject *args)
{
	int index;
	const char *name_ptr;
	int i;

	/*
	 * Supported calling signatures:
	 *	set_property (index, set_context_name)
	 */
	if (!PyArg_ParseTuple(args, "is", &index, &name_ptr))
		return NULL;
	if ((index < ARM_PROPERTY_MIN_ARRAY_INDEX) || (index > ARM_PROPERTY_MAX_ARRAY_INDEX))
		return NULL;

	/* Allocate the property array as required */
	if (self->arm_buffer.context_name_array == NULL)
	{
		self->arm_buffer.context_name_array = calloc (sizeof (arm_char_t *), ARM_PROPERTY_MAX_COUNT);
		for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
		{
			self->arm_buffer.context_name_array [i] = NULL;
		}
	}

	/* Prevent memory loss when overwriting a value */
	ArmSubbufferAppIdentity_free_context_name (self, index);

	/* Copy the names */
	self->arm_buffer.context_name_array [index] = strndup (name_ptr, ARM_PROPERTY_NAME_MAX_CHARS);

	index++;
	if (index > self->arm_buffer.context_name_count)
		self->arm_buffer.context_name_count = index;

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef ArmSubbufferAppIdentity_methods[] = {
	{"set_property",		(PyCFunction)ArmSubbufferAppIdentity_set_property,		METH_VARARGS, ArmSubbufferAppIdentity_set_property__doc__},
	{"set_context_name",	(PyCFunction)ArmSubbufferAppIdentity_set_context_name,	METH_VARARGS, ArmSubbufferAppIdentity_set_context_name__doc__},
	{NULL,		NULL}		/* sentinel */
};

PyDoc_STRVAR(ArmSubbufferAppIdentity_type__doc__,
"Applications are identified by a name and an optional set of identity attribute (name,value) pairs.\n"
"Application instances are further identified by an optional set of context (name,value) pairs. The\n"
"optional context property names are provided in this sub-buffer on the\n"
"register_application() call. The optional context property values are provided on the\n"
"start_application() call. The sub-buffer is ignored if it is passed on any other call.\n"
"\n"
"The names of identity and context properties can be any string, with one exception. Strings\n"
"beginning with the four characters \"ARM:\" are reserved for the ARM specification. The\n"
"specification will define names with known semantics using this prefix. One name format is\n"
"currently defined. Any name beginning with the eight-character prefix \"ARM:CIM:\" represents\n"
"a name defined using the DMTF CIM (Distributed Management Task Force Common\n"
"Information Model) naming rules. For example, \"ARM:CIM:CIM_SoftwareElement.Name\"\n"
"indicates that the property value has the semantics of the Name property of the\n"
"CIM_SoftwareElement class. It is anticipated that additional naming semantics are likely to be\n"
"added in the future.\n"
"\n"
"Identity Properties\n"
"  The array index of a property value in the value array is bound to the property name at the\n"
"  same index in the name array. Moving the (name,value) pair to a different index does not\n"
"  affect the identity of the application. For example, if an application registers once with a\n"
"  name A and a value X in array indices 0 and once with the same name and value in array\n"
"  indices 1, the registered identity has not changed.\n"
"\n"
"  If a name is repeated in the array, the name and its corresponding value are ignored, and\n"
"  the first instance of the name and value in the array is used. The implementation may\n"
"  return an error code but is not obliged to do so.\n"
"\n"
"  Each structure contains:\n"
"  o   Name: A string representing the name part of the (name,value) pair. Each string has a maximum\n"
"          length of 127 characters. If the string is zero-length, the (name,value) pair is ignored.\n"
"          Names should not contain trailing blank characters or consist of only blank characters.\n"
"  o   Value: A string representing the value part of the (name,value) pair. Each string has a maximum\n"
"          length of 255 characters. If the string is zero-length, the (name,value) pair is ignored.\n"
"          Values should not contain trailing blank characters or consist of only blank characters.\n"
"\n"
"Context Properties\n"
"  If a name is repeated in the array, the name and its corresponding value (in the application\n"
"  context sub-buffer) are ignored, and the first instance of the name in the array (and its\n"
"  corresponding value) is used. The implementation may return an error code but is not\n"
"  obliged to do so.\n"
"\n"
"  Each array element contains:\n"
"  o   Name: A string representing the name part of the (name,value) pair. Each string has a maximum\n"
"	      length of 127 characters. If the string is zero-length, the (name,value) pair is ignored.\n"
"	      The values are provided in the ArmSubbufferApplicationContext object. Names should not contain\n"
"	      trailing blank characters or consist of only blank characters.\n"
);

static PyTypeObject ArmSubbufferAppIdentity_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmSubbufferAppIdentity",		/*tp_name*/
	sizeof(ArmSubbufferAppIdentity),	/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmSubbufferAppIdentity_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmSubbufferAppIdentity_type__doc__, /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	ArmSubbufferAppIdentity_methods, /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	newArmSubbufferAppIdentity, /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_subbuffer_app_context_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_subbuffer_app_context_t arm_buffer;
	PyObject *x_attr;
} ArmSubbufferAppContext;

static PyObject *
newArmSubbufferAppContext(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ArmSubbufferAppContext *self;

    self = (ArmSubbufferAppContext *)type->tp_alloc(type, 0);
    if (self != NULL) {
		self->arm_buffer.header.format = ARM_SUBBUFFER_APP_CONTEXT;
		self->arm_buffer.context_value_count = 0;
		self->arm_buffer.context_value_array = NULL;
    }

	return (PyObject *)self;
}

/* ArmSubbufferAppContext methods */

static void
ArmSubbufferAppContext_free_context_value (ArmSubbufferAppContext *self, int index)
{
	if (self->arm_buffer.context_value_array [index] != NULL)
		free ((char *) self->arm_buffer.context_value_array [index]);
}


static void
ArmSubbufferAppContext_free_context (ArmSubbufferAppContext *self)
{
	int i;

	if (self->arm_buffer.context_value_array != NULL)
	{
		for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
			ArmSubbufferAppContext_free_context_value (self, i);
		free (self->arm_buffer.context_value_array);
	}
}

static void
ArmSubbufferAppContext_dealloc(ArmSubbufferAppContext *self)
{
	ArmSubbufferAppContext_free_context(self);

	PyObject_Del(self);
}

PyDoc_STRVAR(ArmSubbufferAppContext_set_context_value__doc__,
"set_context_value(index, value): Set an application context value\n"
"\n"
"DESCRIPTION\n"
"  set_context_value() sets the value in the specified index.\n"
"PARAMETERS\n"
"  index     The array index of a property value between 0 and 19\n"
"\n"
"            The values in the array are position-sensitive; each must align with the corresponding context\n"
"            property name in the application identity sub-buffer. If the corresponding property name string\n"
"            is zero-length, the value is ignored.\n"
"  name      A string representing the name part of the (name,value) pair. Each string has a maximum\n"
"            length of 255 characters. If any string is zero-length, the meaning is that there is no value\n"
"            for this instance. The value should not contain trailing blank characters or consist of only\n"
"            blank characters.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferAppContext_set_context_value (ArmSubbufferAppContext *self, PyObject *args)
{
	int index;
	const char *value_ptr;
	int i;

	/*
	 * Supported calling signatures:
	 *	set_context_value (index, value)
	 */
	if (!PyArg_ParseTuple(args, "is", &index, &value_ptr))
		return NULL;
	if ((index < ARM_PROPERTY_MIN_ARRAY_INDEX) || (index > ARM_PROPERTY_MAX_ARRAY_INDEX))
		return NULL;

	/* Allocate the property array as required */
	if (self->arm_buffer.context_value_array == NULL)
	{
		self->arm_buffer.context_value_array = calloc (sizeof (arm_char_t *), ARM_PROPERTY_MAX_COUNT);
		for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
		{
			self->arm_buffer.context_value_array [i] = NULL;
		}
	}

	/* Prevent memory loss when overwriting a value */
	ArmSubbufferAppContext_free_context_value (self, index);

	/* Copy the value */
	self->arm_buffer.context_value_array [index] = strndup (value_ptr, ARM_PROPERTY_VALUE_MAX_CHARS);

	index++;
	if (index > self->arm_buffer.context_value_count)
		self->arm_buffer.context_value_count = index;

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef ArmSubbufferAppContext_methods[] = {
	{"set_context_value",	(PyCFunction)ArmSubbufferAppContext_set_context_value,	METH_VARARGS, ArmSubbufferAppContext_set_context_value__doc__},
	{NULL,		NULL}		/* sentinel */
};

PyDoc_STRVAR(ArmSubbufferAppContext_type__doc__,
"Applications are identified by a name and an optional set of identity attribute (name,value) pairs.\n"
"Application instances are further identified by an optional set of context (name,value) pairs.\n"
"These properties could indicate something about the runtime instance of the application, such as\n"
"the instance identifier and the name of a configuration file used.\n"
"\n"
"The optional context property names are provided in the application identity sub-buffer on the\n"
"register_application() call. The optional context property values are provided in this sub-\n"
"buffer on the start_application() call. The sub-buffer is ignored if it is passed on any other\n"
"call.\n"
"\n"
"Context Values\n"
"  The values in the array are position-sensitive; each must align with the corresponding context\n"
"  property name in the application identity sub-buffer. If the corresponding property name string\n"
"  is zero-length, the value is ignored.\n"
"\n"
"  Each array element contains:\n"
"  o   Value: A string representing the value part of the (name,value) pair. Each string has a maximum\n"
"          length of 255 characters. If any string is zero-length, the meaning is that there is no value\n"
"          for this instance. The value should not contain trailing blank characters or consist of only\n"
"          blank characters.\n"
);

static PyTypeObject ArmSubbufferAppContext_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmSubbufferAppContext",		/*tp_name*/
	sizeof(ArmSubbufferAppContext),	/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmSubbufferAppContext_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmSubbufferAppContext_type__doc__, /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	ArmSubbufferAppContext_methods, /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	newArmSubbufferAppContext, /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_subbuffer_tran_identity_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_subbuffer_tran_identity_t arm_buffer;
	PyObject *x_attr;
} ArmSubbufferTranIdentity;

#ifdef DEBUG
static void dump_tran_identity (ArmSubbufferTranIdentity *self)
{
	int i;

	printf ("arm_subbuffer_tran_identity_t\n");
	printf ("\tproperty count: %d\n", self->arm_buffer.identity_property_count);
	if (self->arm_buffer.identity_property_count > 0)
	{
		for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
		{
			if (self->arm_buffer.identity_property_array [i].name &&
				self->arm_buffer.identity_property_array [i].value)
				printf ("\t%d: (%s,%s)\n", i, 
						self->arm_buffer.identity_property_array [i].name,
						self->arm_buffer.identity_property_array [i].value);
			else
				printf ("\t%d: NULL\n", i);
		}
	}

	printf ("\t%d\n", self->arm_buffer.context_name_count);

	for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
	{
		if (self->arm_buffer.context_name_array [i])
            printf ("\t%d: %s\n", i, 
					self->arm_buffer.context_name_array [i]);
		else
			printf ("\t%d: NULL\n", i);
	}

	if (self->arm_buffer.uri)
		printf ("\tURI: %s\n", self->arm_buffer.uri);
	else
		printf ("\tURI: NULL\n");
}
#endif

static PyObject *
newArmSubbufferTranIdentity(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ArmSubbufferTranIdentity *self;

    self = (ArmSubbufferTranIdentity *)type->tp_alloc(type, 0);
    if (self != NULL) {
		self->arm_buffer.header.format = ARM_SUBBUFFER_TRAN_IDENTITY;
		self->arm_buffer.identity_property_count = 0;
		self->arm_buffer.identity_property_array = NULL;
		self->arm_buffer.context_name_count = 0;
		self->arm_buffer.context_name_array = NULL;
		self->arm_buffer.uri = NULL;
    }

	return (PyObject *)self;
}

/* ArmSubbufferTranIdentity methods */

static void
ArmSubbufferTranIdentity_free_property (ArmSubbufferTranIdentity *self, int index)
{
	if (self->arm_buffer.identity_property_array [index].name != NULL)
		free ((char *) self->arm_buffer.identity_property_array [index].name);
	if (self->arm_buffer.identity_property_array [index].value != NULL)
		free ((char *) self->arm_buffer.identity_property_array [index].value);
}

static void
ArmSubbufferTranIdentity_free_properties (ArmSubbufferTranIdentity *self)
{
	int i;

	if (self->arm_buffer.identity_property_array != NULL)
	{
		for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
			ArmSubbufferTranIdentity_free_property (self, i);
		free ((char *) self->arm_buffer.identity_property_array);
	}
}

static void
ArmSubbufferTranIdentity_free_context_name (ArmSubbufferTranIdentity *self, int index)
{
	if (self->arm_buffer.context_name_array [index] != NULL)
		free ((char *) self->arm_buffer.context_name_array [index]);
}

static void
ArmSubbufferTranIdentity_free_context (ArmSubbufferTranIdentity *self)
{
	int i;

	if (self->arm_buffer.context_name_array != NULL)
	{
		for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
			ArmSubbufferTranIdentity_free_context_name (self, i);
		free (self->arm_buffer.context_name_array);
	}
}

static void
ArmSubbufferTranIdentity_free_uri (ArmSubbufferTranIdentity *self)
{
	if (self->arm_buffer.uri != NULL)
		free ((char *) self->arm_buffer.uri);
}

static void
ArmSubbufferTranIdentity_dealloc(ArmSubbufferTranIdentity *self)
{
	ArmSubbufferTranIdentity_free_properties (self);
	ArmSubbufferTranIdentity_free_context (self);
	ArmSubbufferTranIdentity_free_uri (self);

	PyObject_Del(self);
}

PyDoc_STRVAR(ArmSubbufferTranIdentity_set_property__doc__,
"set_property(index, name, value): Set a transaction identity name/value pair\n"
"\n"
"DESCRIPTION\n"
"  set_property() sets the name/value pair in the specified index.\n"
"PARAMETERS\n"
"  index     The array index of a property value between 0 and 19\n"
"\n"
"            The array index of a property value in the value array is bound to the property name at the\n"
"            same index in the name array. Moving the (name,value) pair to a different index does not\n"
"            affect the identity of the transaction. For example, if a transaction registers once with a\n"
"            name A and a value X in array indices 0 and once with the same name and value in array\n"
"            indices 1, the registered identity has not changed.\n"
"  name      A string representing the name part of the (name,value) pair. Each string has a maximum\n"
"            length of 127 characters. If the string is zero-length, the (name,value) pair is ignored.\n"
"            Names should not contain trailing blank characters or consist of only blank characters.\n"
"  value     A string representing the value part of the (name,value) pair. Each string has a maximum\n"
"            length of 255 characters. If the string is zero-length, the (name,value) pair is ignored.\n"
"            Values should not contain trailing blank characters or consist of only blank characters.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferTranIdentity_set_property (ArmSubbufferTranIdentity *self, PyObject *args)
{
	int index;
	const char *name_ptr;
	const char *value_ptr;
	int i;

	/*
	 * Supported calling signatures:
	 *	set_property (index, name, value)
	 */
    if (!PyArg_ParseTuple(args, "iss", &index, &name_ptr, &value_ptr))
        return NULL;
	if ((index < ARM_PROPERTY_MIN_ARRAY_INDEX) || (index > ARM_PROPERTY_MAX_ARRAY_INDEX))
		return NULL;

	/* Allocate the property array as required */
	if (self->arm_buffer.identity_property_array == NULL)
	{
		self->arm_buffer.identity_property_array = calloc (sizeof (arm_property_t), ARM_PROPERTY_MAX_COUNT);
		for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
		{
			((arm_property_t *) self->arm_buffer.identity_property_array) [i].name = NULL;
			((arm_property_t *) self->arm_buffer.identity_property_array) [i].value = NULL;
		}
	}

	/* Prevent memory loss when overwriting a value */
	ArmSubbufferTranIdentity_free_property (self, index);

	/* Copy the names */
	((arm_property_t *) self->arm_buffer.identity_property_array) [index].name = strndup (name_ptr, ARM_PROPERTY_NAME_MAX_CHARS);
	((arm_property_t *) self->arm_buffer.identity_property_array) [index].value = strndup (name_ptr, ARM_PROPERTY_VALUE_MAX_CHARS);

	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(ArmSubbufferTranIdentity_set_context_name__doc__,
"set_context_name(index, name): Set a transaction context name\n"
"\n"
"DESCRIPTION\n"
"  set_context_name() sets the name in the specified index.\n"
"PARAMETERS\n"
"  index     The array index of a property value between 0 and 19\n"
"\n"
"            If a name is repeated in the array, the name and its corresponding value (in the transaction\n"
"            context sub-buffer) are ignored, and the first instance of the name in the array (and its\n"
"            corresponding value) is used.\n"
"  name      A string representing the name part of the (name,value) pair. Each string has a maximum\n"
"            length of 127 characters. If the string is zero-length, the (name,value) pair is ignored.\n"
"            The values are provided in the ArmSubbufferTranContext object. Names should not contain\n"
"            trailing blank characters or consist of only blank characters.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferTranIdentity_set_context_name (ArmSubbufferTranIdentity *self, PyObject *args)
{
	int index;
	const char *name_ptr;
	int i;

	/*
	 * Supported calling signatures:
	 *	set_context_name (index, name)
	 */
	if (!PyArg_ParseTuple(args, "is", &index, &name_ptr))
		return NULL;
	if ((index < ARM_PROPERTY_MIN_ARRAY_INDEX) || (index > ARM_PROPERTY_MAX_ARRAY_INDEX))
		return NULL;

	/* Allocate the property array as required */
	if (self->arm_buffer.context_name_array == NULL)
	{
		self->arm_buffer.context_name_array = calloc (sizeof (arm_char_t *), ARM_PROPERTY_MAX_COUNT);
		for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
		{
			self->arm_buffer.context_name_array [i] = NULL;
		}
	}

	/* Prevent memory loss when overwriting a value */
	ArmSubbufferTranIdentity_free_context_name (self, index);

	/* Copy the names */
	self->arm_buffer.context_name_array [index] = strndup (name_ptr, ARM_PROPERTY_NAME_MAX_CHARS);

	index++;
	if (index > self->arm_buffer.context_name_count)
		self->arm_buffer.context_name_count = index;

	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(ArmSubbufferTranIdentity_set_uri__doc__,
"set_uri(uri): Set a transaction uri\n"
"\n"
"DESCRIPTION\n"
"  set_uri() sets the uri for the transaction.\n"
"PARAMETERS\n"
"  uri       A string representing the the uri of the transaction. This string has a maximum\n"
"            length of 4095 characters. If the string is zero-length, the uri is ignored.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferTranIdentity_set_uri (ArmSubbufferTranIdentity *self, PyObject *args)
{
	const char *uri_ptr;

	/*
	 * Supported calling signatures:
	 *	set_property (index, set_context_name)
	 */
	if (!PyArg_ParseTuple(args, "s", &uri_ptr))
		return NULL;

	/* Prevent memory loss when overwriting a value */
	ArmSubbufferTranIdentity_free_uri (self);

	/* Copy the uri */
	self->arm_buffer.uri = strndup (uri_ptr, ARM_PROPERTY_URI_MAX_CHARS);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef ArmSubbufferTranIdentity_methods[] = {
	{"set_property",		(PyCFunction)ArmSubbufferTranIdentity_set_property,		METH_VARARGS, ArmSubbufferTranIdentity_set_property__doc__},
	{"set_context_name",	(PyCFunction)ArmSubbufferTranIdentity_set_context_name,	METH_VARARGS, ArmSubbufferTranIdentity_set_context_name__doc__},
	{"set_uri",				(PyCFunction)ArmSubbufferTranIdentity_set_uri,			METH_VARARGS, ArmSubbufferTranIdentity_set_uri__doc__},
	{NULL,		NULL}		/* sentinel */
};

PyDoc_STRVAR(ArmSubbufferTranIdentity_type__doc__,
"Transactions are identified by a name, an optional URI value, and an optional set of attribute\n"
"(name,value) pairs. The URI and optional (name,value) pairs are provided in this sub-buffer on\n"
"the register_transaction() call. The sub-buffer is ignored if it is passed on any other call.\n"
"The identity is scoped to a single application.\n"
"\n"
"The names of identity and context properties can be any string, with one exception. Strings\n"
"beginning with the four characters \"ARM:\" are reserved for the ARM specification. The\n"
"specification will define names with known semantics using this prefix. One name format is\n"
"currently defined. Any name beginning with the eight-character prefix \"ARM:CIM:\" represents\n"
"a name defined using the DMTF CIM (Distributed Management Task Force Common\n"
"Information Model) naming rules. For example, \"ARM:CIM:CIM_SoftwareElement.Name\"\n"
"indicates that the property value has the semantics of the Name property of the\n"
"CIM_SoftwareElement class. It is anticipated that additional naming semantics are likely to be\n"
"added in the future.\n"
"\n"
"Idenitity Properties\n"
"  The array index of a property value in the value array is bound to the property name at the\n"
"  same index in the name array. Moving the (name,value) pair to a different index does not\n"
"  affect the identity of the transaction. For example, if an application is registered once with\n"
"  a name A and a value X in array indices 0 and once with the same name and value in array\n"
"  indices 1, the registered identity has not changed.\n"
"\n"
"  If a name is repeated in the array, the name and its corresponding value (in the transaction\n"
"  context sub-buffer) are ignored, and the first instance of the name in the array (and its\n"
"  corresponding value) is used. The implementation may return an error code but is not\n"
"  obliged to do so.\n"
"\n"
"  Each structure contains:\n"
"  o   Name: A string representing the name part of the (name,value) pair. Each string has a maximum\n"
"          length of 127 characters. If the string is zero-length, the (name,value) pair is ignored.\n"
"          Names should not contain trailing blank characters or consist of only blank characters.\n"
"  o   Value: A string representing the value part of the (name,value) pair. Each string has a maximum\n"
"          length of 255 characters. If the string is zero-length, the (name,value) pair is ignored.\n"
"          Values should not contain trailing blank characters or consist of only blank characters.\n"
"\n"
"Context Properties\n"
"  An array of strings, each containing a context property name. Each array element is a string\n"
"  representing the name part of the (name,value) pair. Each string has a maximum length of 127\n"
"  characters. The name is passed on register_transaction().\n"
"\n"
"  If a name is repeated in the array, the name and its corresponding value (in the transaction\n"
"  context sub-buffer) are ignored, and the first instance of the name in the array (and its\n"
"  corresponding value) is used\n"
"\n"
"  Each array element contains:\n"
"  o   Name: A string representing the name part of the (name,value) pair. Each string has a maximum\n"
"	      length of 127 characters. If the string is zero-length, the (name,value) pair is ignored.\n"
"          The values are provided in the ArmSubbufferTransactionContext object. Names should not\n"
"          contain trailing blank characters or consist of only blank characters.\n"
"\n"
"URI\n"
"  A string containing a URI, with a maximum of 4095 characters.\n"
);

static PyTypeObject ArmSubbufferTranIdentity_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmSubbufferTranIdentity",		/*tp_name*/
	sizeof(ArmSubbufferTranIdentity),	/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmSubbufferTranIdentity_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmSubbufferTranIdentity_type__doc__, /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	ArmSubbufferTranIdentity_methods, /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	newArmSubbufferTranIdentity, /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_subbuffer_tran_context_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_subbuffer_tran_context_t arm_buffer;
	PyObject *x_attr;
} ArmSubbufferTranContext;

static PyObject *
newArmSubbufferTranContext(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ArmSubbufferTranContext *self;

    self = (ArmSubbufferTranContext *)type->tp_alloc(type, 0);
    if (self != NULL) {
		self->arm_buffer.header.format = ARM_SUBBUFFER_TRAN_CONTEXT;
		self->arm_buffer.context_value_count = 0;
		self->arm_buffer.context_value_array = NULL;
		self->arm_buffer.uri = NULL;
    }

	return (PyObject *)self;
}

/* ArmSubbufferTranContext methods */

static void
ArmSubbufferTranContext_free_context_value (ArmSubbufferTranContext *self, int index)
{
	if (self->arm_buffer.context_value_array [index] != NULL)
		free ((char *) self->arm_buffer.context_value_array [index]);
}

static void
ArmSubbufferTranContext_free_context (ArmSubbufferTranContext *self)
{
	int i;

	if (self->arm_buffer.context_value_array != NULL)
	{
		for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
			ArmSubbufferTranContext_free_context_value (self, i);
		free (self->arm_buffer.context_value_array);
	}
}

static void
ArmSubbufferTranContext_free_uri (ArmSubbufferTranContext *self)
{
	if (self->arm_buffer.uri != NULL)
		free ((char *) self->arm_buffer.uri);
}

static void
ArmSubbufferTranContext_dealloc(ArmSubbufferTranContext *self)
{
	ArmSubbufferTranContext_free_context (self);
	ArmSubbufferTranContext_free_uri (self);

	PyObject_Del(self);
}

PyDoc_STRVAR(ArmSubbufferTranContext_set_context_value__doc__,
"set_context_value(index, value): Set a transaction context value\n"
"\n"
"DESCRIPTION\n"
"  set_context_value() sets the value in the specified index.\n"
"PARAMETERS\n"
"  index     The array index of a property value between 0 and 19\n"
"\n"
"            If a value is repeated in the array, the value and its corresponding value (in the transaction\n"
"            context sub-buffer) are ignored, and the first instance of the value in the array (and its\n"
"            corresponding value) is used.\n"
"  value     A string representing the value part of the (name,value) pair. Each string has a maximum\n"
"            length of 255 characters. If the string is zero-length, the (name,value) pair is ignored.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferTranContext_set_context_value (ArmSubbufferTranContext *self, PyObject *args)
{
	int index;
	const char *value_ptr;
	int i;

	/*
	 * Supported calling signatures:
	 *	set_property (index, value)
	 */
	if (!PyArg_ParseTuple(args, "is", &index, &value_ptr))
		return NULL;
	if ((index < ARM_PROPERTY_MIN_ARRAY_INDEX) || (index > ARM_PROPERTY_MAX_ARRAY_INDEX))
		return NULL;

	/* Allocate the property array as required */
	if (self->arm_buffer.context_value_array == NULL)
	{
		self->arm_buffer.context_value_array = calloc (sizeof (arm_char_t *), ARM_PROPERTY_MAX_COUNT);
		for (i = 0; i < ARM_PROPERTY_MAX_COUNT; i++)
		{
			self->arm_buffer.context_value_array [i] = NULL;
		}
	}

	/* Prevent memory loss when overwriting a value */
	ArmSubbufferTranContext_free_context_value (self, index);

	/* Copy the values */
	self->arm_buffer.context_value_array [index] = strndup (value_ptr, ARM_PROPERTY_VALUE_MAX_CHARS);

	index++;
	if (index > self->arm_buffer.context_value_count)
		self->arm_buffer.context_value_count = index;

	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(ArmSubbufferTranContext_set_uri__doc__,
"set_uri(uri): Set a transaction uri\n"
"\n"
"DESCRIPTION\n"
"  set_uri() sets the uri for the transaction.\n"
"PARAMETERS\n"
"  uri       A string representing the the uri of the transaction. This string has a maximum\n"
"            length of 4095 characters. If the string is zero-length, the uri is ignored.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferTranContext_set_uri (ArmSubbufferTranContext *self, PyObject *args)
{
	const char *uri_ptr;

	/*
	 * Supported calling signatures:
	 *	set_uri (uri)
	 */
	if (!PyArg_ParseTuple(args, "s", &uri_ptr))
		return NULL;

	/* Prevent memory loss when overwriting a value */
	ArmSubbufferTranContext_free_uri (self);

	/* Copy the uri */
	self->arm_buffer.uri = strndup (uri_ptr, ARM_PROPERTY_URI_MAX_CHARS);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef ArmSubbufferTranContext_methods[] = {
	{"set_context_value",	(PyCFunction)ArmSubbufferTranContext_set_context_value,	METH_VARARGS, ArmSubbufferTranContext_set_context_value__doc__},
	{"set_uri",				(PyCFunction)ArmSubbufferTranContext_set_uri,			METH_VARARGS, ArmSubbufferTranContext_set_uri__doc__},
	{NULL,		NULL}		/* sentinel */
};

PyDoc_STRVAR(ArmSubbufferTranContext_type__doc__,
"In addition to the identity properties, a transaction may be described with additional context\n"
"properties. Context properties differ from identity properties in that although the name is\n"
"provided when the transaction is registered [register_transaction()], the values are\n"
"provided when a transaction is measured [start_transaction() or report_transaction()].\n"
"The value of an identity property never changes, whereas the value of a context property may\n"
"change every time a transaction executes.\n"
"\n"
"Context properties are of two forms. There may be one URI value and up to twenty (name,value)\n"
"pairs. No name may duplicate the name of a transaction identity property.\n"
"\n"
"Context Values\n"
"  An array strings containing the property values. The values in the array are position-sensitive;\n"
"  each must align with the corresponding context property name in the ArmSubbufferTranIdentity\n"
"  object. If the corresponding property name is a zero-length string, the value is ignored.\n"
"\n"
"  Each array element contains:\n"
"  o   Value: A string representing the value part of the (name,value) pair. Each string has a maximum\n"
"          length of 255 characters. If any string is zero-length, the meaning is that there is no value\n"
"          for this instance. Values should not contain trailing blank characters or consist of only\n"
"          blank characters.\n"
"\n"
"URI\n"
"  A string containing a URI, with a maximum of 4095 characters.\n"
"\n"
"  If a URI is provided in both the transaction identity sub-buffer and in the transaction\n"
"  context sub-buffer, the URI in the transaction identity sub-buffer must be the same as the\n"
"  URI provided in the transaction context sub-buffer, or a truncated subset.\n"
);

static PyTypeObject ArmSubbufferTranContext_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmSubbufferTranContext",		/*tp_name*/
	sizeof(ArmSubbufferTranContext),	/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmSubbufferTranContext_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmSubbufferTranContext_type__doc__, /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	ArmSubbufferTranContext_methods, /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	newArmSubbufferTranContext, /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_subbuffer_arrival_time_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_subbuffer_arrival_time_t arm_buffer;
	PyObject *x_attr;
} ArmSubbufferArrivalTime;

static PyObject *
newArmSubbufferArrivalTime(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ArmSubbufferArrivalTime *self;

    self = (ArmSubbufferArrivalTime *)type->tp_alloc(type, 0);
    if (self != NULL) {
		self->arm_buffer.header.format = ARM_SUBBUFFER_ARRIVAL_TIME;
		memset (&(self->arm_buffer.opaque_time), 0, sizeof (arm_arrival_time_t));
    }

	return (PyObject *)self;
}

/* ArmSubbufferArrivalTime methods */

static void
ArmSubbufferArrivalTime_dealloc(ArmSubbufferArrivalTime *self)
{
	PyObject_Del(self);
}

PyDoc_STRVAR(ArmSubbufferArrivalTime_set_arrival_time__doc__,
"set_arrival_time(arrival_time): Sets the transaction arrival time\n"
"\n"
"DESCRIPTION\n"
"  set_arrival_time() sets the arrival time for the transaction.\n"
"PARAMETERS\n"
"  arrival_time  an ArmArrivalTime object containing the value returned by the\n"
"                get_arrival_time() function.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferArrivalTime_set_arrival_time (ArmSubbufferArrivalTime *self, PyObject *args)
{
	ArmArrivalTime *arrival;

	/*
	 * Supported calling signatures:
	 *	set_arrival_time (arrival_time)
	 */
	if (!PyArg_ParseTuple(args, "O", &arrival))
		return NULL;
	if (!ArmArrivalTime_Object_Check(arrival))
		return NULL;

	/* Copy the arrival time */
	memcpy (&(self->arm_buffer.opaque_time), &(arrival->arm_time), sizeof (arm_arrival_time_t));

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef ArmSubbufferArrivalTime_methods[] = {
	{"set_arrival_time",	(PyCFunction)ArmSubbufferArrivalTime_set_arrival_time,	METH_VARARGS, ArmSubbufferArrivalTime_set_arrival_time__doc__},
	{NULL,		NULL}		/* sentinel */
};

PyDoc_STRVAR(ArmSubbufferArrivalTime_type__doc__,
"Some applications may start processing a transaction before all the context information that\n"
"identifies the transaction is known. For example, it might by necessary to retrieve the context\n"
"information as the first step in processing the transaction. For these cases, the application can\n"
"call get_arrival_time() to receive a timestamp value for the current time from the ARM\n"
"implementation. This timestamp value is known as the \"arrival time\". When the transaction\n"
"context data is all known, start_transaction() is called, passing the optional arrival time\n"
"value in a sub-buffer, to indicate when the transaction actually started executing. The arrival\n"
"time is provided in this sub-buffer.\n"
"\n"
"The arrival time field is an ArmArrivalTime object containing the value returned by the\n"
"get_arrival_time() function.\n"
);

static PyTypeObject ArmSubbufferArrivalTime_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmSubbufferArrivalTime",		/*tp_name*/
	sizeof(ArmSubbufferArrivalTime),	/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmSubbufferArrivalTime_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmSubbufferArrivalTime_type__doc__, /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	ArmSubbufferArrivalTime_methods, /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	newArmSubbufferArrivalTime, /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_subbuffer_metric_bindings_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_subbuffer_metric_bindings_t arm_buffer;
	PyObject *x_attr;
} ArmSubbufferMetricBindings;

static PyObject *
newArmSubbufferMetricBindings(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ArmSubbufferMetricBindings *self;

    self = (ArmSubbufferMetricBindings *)type->tp_alloc(type, 0);
    if (self != NULL) {
		self->arm_buffer.header.format = ARM_SUBBUFFER_METRIC_BINDINGS;
		self->arm_buffer.count = 0;
		self->arm_buffer.metric_binding_array = NULL;
    }

	return (PyObject *)self;
}

/* ArmSubbufferMetricBindings methods */

static void
ArmSubbufferMetricBindings_free_array (ArmSubbufferMetricBindings *self)
{
	if (self->arm_buffer.metric_binding_array != NULL)
		free ((arm_metric_binding_t *) self->arm_buffer.metric_binding_array);
}

static void
ArmSubbufferMetricBindings_dealloc(ArmSubbufferMetricBindings *self)
{
	ArmSubbufferMetricBindings_free_array (self);

	PyObject_Del(self);
}

PyDoc_STRVAR(ArmSubbufferMetricBindings_bind__doc__,
"bind(index, metric_id): Set a transaction context value\n"
"\n"
"DESCRIPTION\n"
"  bind() binds a metric to the specified index.\n"
"PARAMETERS\n"
"  index     The array index of a metric between 0 and 7\n"
"  metric_id An ArmID object for this metric definition. The ID must have been previously returned from\n"
"            register_metric().\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferMetricBindings_bind (ArmSubbufferMetricBindings *self, PyObject *args)
{
	int index;
	ArmID *metric;

	/*
	 * Supported calling signatures:
	 *	bind (index, id)
	 */
	if (!PyArg_ParseTuple(args, "iO", &index, &metric))
		return NULL;
	if ((index < ARM_METRIC_MIN_ARRAY_INDEX) || (index > ARM_METRIC_MAX_ARRAY_INDEX))
		return NULL;
	if (!ArmID_Object_Check(metric))
		return NULL;

	/* Allocate the metric binding array as required */
	if (self->arm_buffer.metric_binding_array == NULL)
	{
		self->arm_buffer.metric_binding_array = calloc (sizeof (arm_metric_binding_t), ARM_METRIC_MAX_COUNT);
		memset ((void *) self->arm_buffer.metric_binding_array, 0, sizeof (arm_metric_binding_t) * ARM_METRIC_MAX_COUNT);
	}

	/* Copy the values */
	if (self->arm_buffer.count >= ARM_METRIC_MAX_ARRAY_INDEX)
		return NULL;
	((arm_metric_binding_t *) self->arm_buffer.metric_binding_array) [self->arm_buffer.count].slot = index;
	((arm_metric_binding_t *) self->arm_buffer.metric_binding_array) [self->arm_buffer.count].id = metric->arm_id;
	self->arm_buffer.count++;

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef ArmSubbufferMetricBindings_methods[] = {
	{"bind",	(PyCFunction)ArmSubbufferMetricBindings_bind,	METH_VARARGS, ArmSubbufferMetricBindings_bind__doc__},
	{NULL,		NULL}		/* sentinel */
};

PyDoc_STRVAR(ArmSubbufferMetricBindings_type__doc__,
"Applications may provide additional data about a transaction when the transaction starts, while it\n"
"is executing, and/or after it has stopped. This additional data may serve several purposes, such as\n"
"indicating the size of a transaction (e.g., the number of bytes in a file for a file transfer\n"
"transaction), the state of the system (e.g., the number of queued up transactions when this\n"
"transaction arrived), or an error code. The metadata describing each metric is provided with the\n"
"register_metric() function.\n"
"\n"
"Each transaction definition may define zero to seven metrics for which data values may be\n"
"provided on start_transaction(), update_transaction(), stop_transaction(), or\n"
"report_transaction(). Each metric is assigned to an array slot numbered 0 to 6 (they were\n"
"numbered 1 to 7 in ARM 2.0). This sub-buffer is passed on the register_transaction()\n"
"function to indicate which metrics are assigned to which slots.\n"
"\n"
"Metric Bindings\n"
"  An array of ArmID objects containing the metric bindings.\n"
"\n"
"  Each structure contains:\n"
"  o   Slot number: A byte slot number. Valid values are 0 to 6. If a slot number is repeated,\n"
"          the first time it appears is the only one processed; all others are ignored.\n"
"  o   ID: An ArmID object for this metric definition. The ID must have been previously returned from\n"
"          register_metric().\n"
);

static PyTypeObject ArmSubbufferMetricBindings_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmSubbufferMetricBindings",		/*tp_name*/
	sizeof(ArmSubbufferMetricBindings),	/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmSubbufferMetricBindings_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmSubbufferMetricBindings_type__doc__, /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	ArmSubbufferMetricBindings_methods, /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	newArmSubbufferMetricBindings, /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_subbuffer_metric_values_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_subbuffer_metric_values_t arm_buffer;
	PyObject *x_attr;
} ArmSubbufferMetricValues;

static PyObject *
newArmSubbufferMetricValues(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ArmSubbufferMetricValues *self;

    self = (ArmSubbufferMetricValues *)type->tp_alloc(type, 0);
    if (self != NULL) {
		self->arm_buffer.header.format = ARM_SUBBUFFER_METRIC_VALUES;
		self->arm_buffer.count = 0;
		self->arm_buffer.metric_value_array = NULL;
    }

	return (PyObject *)self;
}

/* ArmSubbufferMetricValues methods */

static void
ArmSubbufferMetricValues_free_array (ArmSubbufferMetricValues *self)
{
	int i;

	if (self->arm_buffer.metric_value_array != NULL)
	{
		for (i = 0; i < self->arm_buffer.count; i++)
			if (self->arm_buffer.metric_value_array [i].format == ARM_METRIC_FORMAT_STRING32)
				free ((void *) (self->arm_buffer.metric_value_array [i].metric_u.string32));
		free ((arm_metric_t *) self->arm_buffer.metric_value_array);
	}
}

static void
ArmSubbufferMetricValues_dealloc(ArmSubbufferMetricValues *self)
{
	ArmSubbufferMetricValues_free_array (self);

	PyObject_Del(self);
}

PyDoc_STRVAR(ArmSubbufferMetricValues_set_value__doc__,
"set_value(slot, format, usage, value): Set a single numeric value\n"
"set_value(slot, format, usage, value, divisor): Set a value with a divisor\n"
"set_value(slot, usage, string_value): Set a string value\n"
"\n"
"DESCRIPTION\n"
"  set_value() sets a metric value for the specified slot.\n"
"PARAMETERS\n"
"  slot      The array index of a metric between 0 and 7\n"
"  format    A single-byte format indicator. Valid values are 1 to 8 and are the\n"
"            same as ARM 2.0. Only values 1 to 8 are valid in slots 0-5. Only value 10 is valid in\n"
"            slot 6. This is a carry-over from ARM 2.0. The format must be the same as the\n"
"            corresponding entry in the metric bindings sub-buffer. This is not required for a string\n"
"            value.\n"
"\n"
"            1 (ARM_METRIC_FORMAT_COUNTER32) = arm_int32_t counter\n"
"            2 (ARM_METRIC_FORMAT_COUNTER64) = arm_int64_t counter\n"
"            3 (ARM_METRIC_FORMAT_CNTRDIVR32) = arm_int32_t counter + arm_int32_t divisor\n"
"            4 (ARM_METRIC_FORMAT_GAUGE32) = arm_int32_t gauge\n"
"            5 (ARM_METRIC_FORMAT_GAUGE64) = arm_int64_t gauge\n"
"            6 (ARM_METRIC_FORMAT_GAUGEDIVR32) = arm_int32_t gauge + arm_int32_t divisor\n"
"            7 (ARM_METRIC_FORMAT_NUMERICID32) = arm_int32_t numeric ID\n"
"            8 (ARM_METRIC_FORMAT_NUMERICID64) = arm_int64_t numeric ID\n"
"  usage     An arm_metric_usage_t indicating how the metric is used. The usage must\n"
"            be the same as the usage parameter passed on the register_metric() call that\n"
"            registered the metric ID with the same slot number that is in the metric bindings sub-\n"
"            buffer.\n"
"\n"
"            0 (ARM_METRIC_USE_GENERAL) = no usage is declared\n"
"            1 (ARM_METRIC_USE_TRAN_SIZE) = the metric indicates the transaction size (e.g., the size\n"
"                of a file or the number of jobs in a network backup operation)\n"
"            2 (ARM_METRIC_USE_TRAN_STATUS) = the metric is a status code (numeric ID) or text message\n"
"                (string). It would typically be used with stop_transaction() or report_transaction()\n"
"                to provide additional details about a transaction status of Failed.\n"
"            3:32767 = Reserved.\n"
"            -32768:-1 = available for implementation-defined purposes.\n"
"  value     A metric value where the data type matches the metric format indicator (above).\n"
"  divisor   A divisor as required by the ARM_METRIC_FORMAT_CNTRDIVR and ARM_METRIC_FORMAT_GAUGEDIVR32 formats.\n"
"  string_value\n"
"            A 32 character string. For this value type, a format of ARM_METRIC_FORMAT_STRING32 is assumed.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferMetricValues_set_value (ArmSubbufferMetricValues *self, PyObject *args)
{
	int slot;
	int format;
	int usage;
	int parsed;
	arm_int64_t value64;
	arm_int32_t value32;
	arm_int32_t div32;
	const char *string_ptr = NULL;
	
	int i;
	int index;

	/* Poor man's polymorphism */
	parsed = PyArg_ParseTuple(args, "iii" PARSE_INT64_FMT ":set_value", &slot, &format, &usage, &value64);
	if (!parsed)
	{
		PyErr_Clear ();
        parsed = PyArg_ParseTuple(args, "iii" PARSE_INT32_FMT PARSE_INT32_FMT ":set_value", &slot, &format, &usage, &value32, &div32);
	}
	if (!parsed)
	{
		PyErr_Clear ();
		if (!PyArg_ParseTuple(args, "iis:set_value", &slot, &usage, &string_ptr))
			return NULL;
	}
	
	if ((slot < ARM_METRIC_MIN_ARRAY_INDEX) || (slot > ARM_METRIC_MAX_ARRAY_INDEX))
		return NULL;

	if (string_ptr && (strlen (string_ptr) > 0))
		format = ARM_METRIC_FORMAT_STRING32;

	/* Allocate the metric binding array as required */
	if (self->arm_buffer.metric_value_array == NULL)
	{
		self->arm_buffer.metric_value_array = calloc (sizeof (arm_metric_t), ARM_METRIC_MAX_COUNT);
		memset ((void *) self->arm_buffer.metric_value_array, 0, sizeof (arm_metric_t) * ARM_METRIC_MAX_COUNT);
	}
	
	/* See if an entry already exists */
	index = self->arm_buffer.count; /* Default index for a new value */
	for (i = 0; i < self->arm_buffer.count; i++)
	{
		if (self->arm_buffer.metric_value_array [i].slot == slot)
		{
			index = i;
			break;
		}
	}
	if (index == self->arm_buffer.count)
		self->arm_buffer.count++;
	
	/* Copy the values */
	if (index >= ARM_METRIC_MAX_ARRAY_INDEX)
		return NULL;
	((arm_metric_t *) self->arm_buffer.metric_value_array) [index].slot = slot;
	((arm_metric_t *) self->arm_buffer.metric_value_array) [index].format = format;
	((arm_metric_t *) self->arm_buffer.metric_value_array) [index].usage = usage;
	((arm_metric_t *) self->arm_buffer.metric_value_array) [index].valid = ARM_TRUE;

	switch (format)
	{
	case ARM_METRIC_FORMAT_COUNTER32:
		((arm_metric_t *) self->arm_buffer.metric_value_array) [index].metric_u.counter32 = value64;
		break;

	case ARM_METRIC_FORMAT_COUNTER64:
		((arm_metric_t *) self->arm_buffer.metric_value_array) [index].metric_u.counter64 = value64;
		break;

	case ARM_METRIC_FORMAT_GAUGE32:
		((arm_metric_t *) self->arm_buffer.metric_value_array) [index].metric_u.gauge32 = value64;
		break;

	case ARM_METRIC_FORMAT_GAUGE64:
		((arm_metric_t *) self->arm_buffer.metric_value_array) [index].metric_u.gauge64 = value64;
		break;

	case ARM_METRIC_FORMAT_NUMERICID32:
		((arm_metric_t *) self->arm_buffer.metric_value_array) [index].metric_u.numericid32 = value64;
		break;

	case ARM_METRIC_FORMAT_NUMERICID64:
		((arm_metric_t *) self->arm_buffer.metric_value_array) [index].metric_u.numericid64 = value64;
		break;

	case ARM_METRIC_FORMAT_CNTRDIVR32:
		((arm_metric_t *) self->arm_buffer.metric_value_array) [index].metric_u.counterdivisor32.counter = value32;
		((arm_metric_t *) self->arm_buffer.metric_value_array) [index].metric_u.counterdivisor32.divisor = div32;
		break;

	case ARM_METRIC_FORMAT_GAUGEDIVR32:
		((arm_metric_t *) self->arm_buffer.metric_value_array) [index].metric_u.gaugedivisor32.gauge = value32;
		((arm_metric_t *) self->arm_buffer.metric_value_array) [index].metric_u.gaugedivisor32.divisor = div32;
		break;

	case ARM_METRIC_FORMAT_STRING32:
		((arm_metric_t *) self->arm_buffer.metric_value_array) [index].metric_u.string32 = strndup (string_ptr, ARM_METRIC_STRING32_MAX_CHARS);
		break;
	}

	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(ArmSubbufferMetricValues_set_valid__doc__,
"set_value(slot, valid): Set the valid flag for a metric\n"
"\n"
"DESCRIPTION\n"
"  set_valid() sets the valid flag for the specified slot.\n"
"PARAMETERS\n"
"  slot      The array index of a metric between 0 and 7\n"
"  valid     A boolean that indicates whether the data in the metric value field is\n"
"            currently valid.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferMetricValues_set_valid (ArmSubbufferMetricValues *self, PyObject *args)
{
	int slot;
	int valid;
	int i;

	if (!PyArg_ParseTuple(args, "ii:set_valid", &slot, &valid))
		return NULL;
	
	if ((slot < ARM_METRIC_MIN_ARRAY_INDEX) || (slot > ARM_METRIC_MAX_ARRAY_INDEX))
		return NULL;

	/* The buffer should exist already */
	if (self->arm_buffer.metric_value_array == NULL)
		return NULL;
	
	/* Find the entry */
	for (i = 0; i < self->arm_buffer.count; i++)
		if (self->arm_buffer.metric_value_array [i].slot == slot)
		{
			((arm_metric_t *) self->arm_buffer.metric_value_array) [i].valid = valid;
			return Py_None;
		}

	/* If we've reached here then we haven't found our entry */
	return NULL;
}

static PyMethodDef ArmSubbufferMetricValues_methods[] = {
	{"set_value",	(PyCFunction)ArmSubbufferMetricValues_set_value,	METH_VARARGS, ArmSubbufferMetricValues_set_value__doc__},
	{"set_valid",	(PyCFunction)ArmSubbufferMetricValues_set_valid,	METH_VARARGS, ArmSubbufferMetricValues_set_valid__doc__},
	{NULL,		NULL}		/* sentinel */
};

PyDoc_STRVAR(ArmSubbufferMetricValues_type__doc__,
"The buffer is used to pass metric values on any of start_transaction(),\n"
"update_transaction(), stop_transaction(), and report_transaction().\n"
"\n"
"Metric Values\n"
"  Each structure is in the following format:\n"
"  o   Slot number: A single-byte slot number. Valid values are 0 to 6. The slot number\n"
"          must be the same as the corresponding entry in the metric bindings sub-buffer. Each\n"
"          slot number should be used at most once; if a slot number is reused, the first entry is\n"
"          used and all others are ignored.\n"
"  o   Metric format: A single-byte format indicator. Valid values are 1 to 10 and are the\n"
"          same as ARM 2.0. Only values 1 to 8 are valid in slots 0-5. Only value 10 is valid in\n"
"          slot 6. This is a carry-over from ARM 2.0. The format must be the same as the\n"
"          corresponding entry in the metric bindings sub-buffer.\n"
"\n"
"          1 (ARM_METRIC_FORMAT_COUNTER32) = arm_int32_t counter\n"
"          2 (ARM_METRIC_FORMAT_COUNTER64) = arm_int64_t counter\n"
"          3 (ARM_METRIC_FORMAT_CNTRDIVR32) = arm_int32_t counter + arm_int32_t divisor\n"
"          4 (ARM_METRIC_FORMAT_GAUGE32) = arm_int32_t gauge\n"
"          5 (ARM_METRIC_FORMAT_GAUGE64) = arm_int64_t gauge\n"
"          6 (ARM_METRIC_FORMAT_GAUGEDIVR32) = arm_int32_t gauge + arm_int32_t divisor\n"
"          7 (ARM_METRIC_FORMAT_NUMERICID32) = arm_int32_t numeric ID\n"
"          8 (ARM_METRIC_FORMAT_NUMERICID64) = arm_int64_t numeric ID\n"
"          9 = (DEPRECATED)\n"
"          10 (ARM_METRIC_FORMAT_STRING32) = string of a maximum length of 32 characters\n"
"  o   Usage: An arm_metric_usage_t indicating how the metric is used. The usage must\n"
"          be the same as the usage parameter passed on the register_metric() call that\n"
"          registered the metric ID with the same slot number that is in the metric bindings sub-\n"
"          buffer.\n"
"\n"
"          0 (ARM_METRIC_USE_GENERAL) = no usage is declared\n"
"          1 (ARM_METRIC_USE_TRAN_SIZE) = the metric indicates the transaction size (e.g., the size\n"
"                of a file or the number of jobs in a network backup operation)\n"
"          2 (ARM_METRIC_USE_TRAN_STATUS) = the metric is a status code (numeric ID) or text message\n"
"                (string). It would typically be used with stop_transaction() or report_transaction()\n"
"                to provide additional details about a transaction status of Failed.\n"
"          3:32767 = Reserved.\n"
"          -32768:-1 = available for implementation-defined purposes.\n"
"  o   Valid flag: A boolean that indicates whether the data in the metric value field is\n"
"          currently valid.\n"
"  o   Metric value: A metric value where the data type matches the metric format indicator (above).\n"
);

static PyTypeObject ArmSubbufferMetricValues_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmSubbufferMetricValues",		/*tp_name*/
	sizeof(ArmSubbufferMetricValues),	/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmSubbufferMetricValues_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmSubbufferMetricValues_type__doc__, /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	ArmSubbufferMetricValues_methods, /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	newArmSubbufferMetricValues, /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_subbuffer_user_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_subbuffer_user_t arm_buffer;
	PyObject *x_attr;
} ArmSubbufferUser;

static PyObject *
newArmSubbufferUser(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ArmSubbufferUser *self;

    self = (ArmSubbufferUser *)type->tp_alloc(type, 0);
    if (self != NULL) {
		self->arm_buffer.header.format = ARM_SUBBUFFER_USER;
		self->arm_buffer.name = NULL;
		self->arm_buffer.id_valid = ARM_FALSE;
		memset (&(self->arm_buffer.id), 0, sizeof(arm_id_t));
    }

	return (PyObject *)self;
}

/* ArmSubbufferUser methods */

static void
ArmSubbufferUser_dealloc(ArmSubbufferUser *self)
{
	PyObject_Del(self);
}

PyDoc_STRVAR(ArmSubbufferUser_set_user__doc__,
"set_user (name): Set the user name\n"
"\n"
"DESCRIPTION\n"
"  Sets the user name.\n"
"PARAMETERS\n"
"  name   A string with a maximum length of 127 characters.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferUser_set_user (ArmSubbufferUser *self, PyObject *args)
{
	const char *name;

	/*
	 * Supported calling signatures:
	 *	set_user (name)
	 */
    if (!PyArg_ParseTuple(args, "s", &name))
        return NULL;

	if (self->arm_buffer.name != NULL)
		free ((char *) self->arm_buffer.name);
	self->arm_buffer.name = malloc (ARM_NAME_MAX_LENGTH);
	strncpy ((char *) self->arm_buffer.name, name, ARM_NAME_MAX_LENGTH);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef ArmSubbufferUser_methods[] = {
	{"set_user",	(PyCFunction)ArmSubbufferUser_set_user,	METH_VARARGS, ArmSubbufferUser_set_user__doc__},
	{NULL,		NULL}		/* sentinel */
};

PyDoc_STRVAR(ArmSubbufferUser_type__doc__,
"A user name and/or ID may be optionally associated with each transaction instance. A name is a\n"
"character string. An ID is a 16-byte binary value, such as a UUID. Either or both\n"
"may be provided.\n"
);

static PyTypeObject ArmSubbufferUser_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmSubbufferUser",		/*tp_name*/
	sizeof(ArmSubbufferUser),	/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmSubbufferUser_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmSubbufferUser_type__doc__, /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	ArmSubbufferUser_methods, /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	newArmSubbufferUser,	/*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_subbuffer_system_address_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_subbuffer_system_address_t arm_buffer;
	PyObject *x_attr;
} ArmSubbufferSystemAddress;

static PyObject *
newArmSubbufferSystemAddress(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ArmSubbufferSystemAddress *self;

    self = (ArmSubbufferSystemAddress *)type->tp_alloc(type, 0);
    if (self != NULL) {
		self->arm_buffer.header.format = ARM_SUBBUFFER_SYSTEM_ADDRESS;
		self->arm_buffer.address_format = ARM_SYSADDR_FORMAT_RESERVED;
		self->arm_buffer.address_length = 0;
		self->arm_buffer.address = NULL;
		self->arm_buffer.id_valid = ARM_FALSE;
		memset (&(self->arm_buffer.id), 0, sizeof(arm_id_t));
    }

	return (PyObject *)self;
}

/* ArmSubbufferSystemAddress methods */

static void
ArmSubbufferSystemAddress_free_address (ArmSubbufferSystemAddress *self)
{
	if (self->arm_buffer.address != NULL)
		free ((arm_uint8_t *) self->arm_buffer.address);
}

static void
ArmSubbufferSystemAddress_dealloc(ArmSubbufferSystemAddress *self)
{
	ArmSubbufferSystemAddress_free_address (self);

	PyObject_Del(self);
}

PyDoc_STRVAR(ArmSubbufferSystemAddress_set_hostname__doc__,
"set_hostname (name): Set the system hostname\n"
"\n"
"DESCRIPTION\n"
"  set_hostname() sets the system address with a host name.\n"
"PARAMETERS\n"
"  name   A string giving the hostname.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferSystemAddress_set_hostname (ArmSubbufferSystemAddress *self, PyObject *args)
{
	const char *name;

    if (!PyArg_ParseTuple(args, "s", &name))
        return NULL;

	/* Ensure any address currently defined is removed */
	ArmSubbufferSystemAddress_free_address (self);

	self->arm_buffer.address_format = ARM_SYSADDR_FORMAT_HOSTNAME;
	self->arm_buffer.address_length = strlen (name);
	self->arm_buffer.address = (arm_uint8_t *) strdup (name);

	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(ArmSubbufferSystemAddress_set_local__doc__,
"set_local (): Set the system address to be the local host\n"
"\n"
"DESCRIPTION\n"
"  set_local() sets the system address to be the local host.\n"
"PARAMETERS\n"
"  None\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferSystemAddress_set_local (ArmSubbufferSystemAddress *self, PyObject *args)
{
	/* Ensure any address currently defined is removed */
	ArmSubbufferSystemAddress_free_address (self);

	self->arm_buffer.address_format = ARM_SYSADDR_FORMAT_RESERVED;
	self->arm_buffer.address_length = 0;

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef ArmSubbufferSystemAddress_methods[] = {
	{"set_hostname",	(PyCFunction)ArmSubbufferSystemAddress_set_hostname,	METH_VARARGS, ArmSubbufferSystemAddress_set_hostname__doc__},
	{"set_local",		(PyCFunction)ArmSubbufferSystemAddress_set_local,		METH_NOARGS, ArmSubbufferSystemAddress_set_local__doc__},
	{NULL,		NULL}		/* sentinel */
};

PyDoc_STRVAR(ArmSubbufferSystemAddress_type__doc__,
"The system address sub-buffer is used with start_application() when the transactions that\n"
"will be reported execute on a different system than the one on which they will be reported.\n"
"\n"
"  o   If no system address sub-buffer is provided on start_application(), all transactions\n"
"          reported by this application instance execute in the current process.\n"
"  o   If a system address sub-buffer is provided on start_application(), all transactions\n"
"          execute in a different process.\n"
"  o   If a system address sub-buffer is provided in which the system address length is zero, or\n"
"          the system address pointer is null, the system is the local system, as determined by the\n"
"          ARM implementation.\n"
"  o   If a system address sub-buffer is provided in which there is a non-null system address and\n"
"          length, the system may be the local system or a remote system. Interpretation of what is\n"
"          local versus remote is at the discretion of the ARM implementation.\n"
"\n"
"Address Formats\n"
"  The following formats are defined:\n"
"  o   0 = Reserved.\n"
"  o   1 (ARM_SYSADDR_FORMAT_IPV4) = IPv4\n"
"          Bytes 0:3 = 4-byte IP address\n"
"  o   2 (ARM_SYSADDR_FORMAT_IPV4PORT) = IPv4 + port number\n"
"          Bytes 0:3 = 4-byte IP address\n"
"          Bytes 4:5 = 2-byte IP port number\n"
"  o   3 (ARM_SYSADDR_FORMAT_IPV6) = IPv6\n"
"          Bytes 0:15 = 16-byte IP address\n"
"  o   4 (ARM_SYSADDR_FORMAT_IPV6PORT) = IPv6 + port number\n"
"          Bytes 0:15 = 16-byte IP address\n"
"          Bytes 16:17 = 2-byte IP port number\n"
"  o   5 (ARM_SYSADDR_FORMAT_SNA) = SNA\n"
"          Bytes 0:7 = EBCDIC-encoded network ID\n"
"          Bytes 8:15 = EBCDIC-encoded network accessible unit (control point or LU)\n"
"  o   6 (ARM_SYSADDR_FORMAT_X25) = X.25\n"
"          Bytes 0:15 = The X.25 address (also referred to as an X.121 address). This is up to 16\n"
"          ASCII character digits ranging from 0-9.\n"
"  o   7 (ARM_SYSADDR_FORMAT_HOSTNAME) = hostname (characters, not null-terminated)\n"
"          Bytes 0:?? = hostname\n"
"  o   8 (ARM_SYSADDR_FORMAT_UUID) = Universally-unique ID\n"
"          Bytes 0:15 = UUID in binary. This is useful for applications that define their system\n"
"          by a UUID rather than a network address or hostname or some other address form.\n"
"  o   9:32767 = Reserved.\n"
"  o   -32768:-1 = Available for implementation-defined use.\n"
"\n"
"          There are no semantics associated with the address format. It will be an unusual\n"
"          situation where a new format is needed, but this provides a solution if this is needed.\n"
"          The preferred approach is to get a new format defined that is in the 0-32767 range.\n"
"          There is a risk that two different agent developers will choose the same ID, but this\n"
"          risk is deemed small.\n"
"\n"
"Address Length\n"
"  An 16 bit integer length of system address in bytes.\n"
"  o   There is no maximum length.\n"
"  o   A length of zero refers to the local system.\n"
);

static PyTypeObject ArmSubbufferSystemAddress_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmSubbufferSystemAddress",	/*tp_name*/
	sizeof(ArmSubbufferSystemAddress),	/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmSubbufferSystemAddress_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmSubbufferSystemAddress_type__doc__, /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	ArmSubbufferSystemAddress_methods, /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	newArmSubbufferSystemAddress,	/*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_subbuffer_diag_detail_t Python equivalent ---*/

typedef struct {
	PyObject_HEAD
	arm_subbuffer_diag_detail_t arm_buffer;
	PyObject *x_attr;
} ArmSubbufferDiagDetail;

static PyObject *
newArmSubbufferDiagDetail(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ArmSubbufferDiagDetail *self;

    self = (ArmSubbufferDiagDetail *)type->tp_alloc(type, 0);
    if (self != NULL) {
		self->arm_buffer.header.format = ARM_SUBBUFFER_DIAG_DETAIL;
		self->arm_buffer.diag_detail = NULL;
    }

	return (PyObject *)self;
}

/* ArmSubbufferDiagDetail methods */

static void
ArmSubbufferDiagDetail_free_detail (ArmSubbufferDiagDetail *self)
{
	if (self->arm_buffer.diag_detail != NULL)
		free ((arm_char_t *) self->arm_buffer.diag_detail);
}

static void
ArmSubbufferDiagDetail_dealloc(ArmSubbufferDiagDetail *self)
{
	ArmSubbufferDiagDetail_free_detail (self);

	PyObject_Del(self);
}

PyDoc_STRVAR(ArmSubbufferDiagDetail_set_detail__doc__,
"set_detail (detail): Set the diagnostic detail string\n"
"\n"
"DESCRIPTION\n"
"  set_detail() sets the diagnostic detail string.\n"
"PARAMETERS\n"
"  detail    A string containing the diagnostic data. Each string has a maximum length\n"
"            of 4095 characters.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmSubbufferDiagDetail_set_detail (ArmSubbufferDiagDetail *self, PyObject *args)
{
	const char *name;

    if (!PyArg_ParseTuple(args, "s", &name))
        return NULL;

	/* Ensure any address currently defined is removed */
	ArmSubbufferDiagDetail_free_detail (self);

	self->arm_buffer.diag_detail = strndup (name, ARM_PROPERTY_URI_MAX_CHARS);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef ArmSubbufferDiagDetail_methods[] = {
	{"set_detail",		(PyCFunction)ArmSubbufferDiagDetail_set_detail,		METH_VARARGS, ArmSubbufferDiagDetail_set_detail__doc__},
	{NULL,		NULL}		/* sentinel */
};

PyDoc_STRVAR(ArmSubbufferDiagDetail_type__doc__,
"When a transaction completion is reported with stop_transaction() or report_transaction(),\n"
"and the transaction status is not ARM_STATUS_GOOD, the application may provide a character\n"
"string containing any arbitrary diagnostic data. The string may not be longer than 4095 characters.\n"
"For example,the application might provide the SQL query text for a failing database transaction.\n"
);

static PyTypeObject ArmSubbufferDiagDetail_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmSubbufferDiagDetail",	/*tp_name*/
	sizeof(ArmSubbufferDiagDetail),	/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmSubbufferDiagDetail_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmSubbufferDiagDetail_type__doc__, /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	ArmSubbufferDiagDetail_methods, /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	newArmSubbufferDiagDetail,	/*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/*--- Define the arm_buffer4_t Python equivalent ---*/

#define MAX_SUBBUFFERS 11	/* One for each type */

typedef struct {
	PyObject_HEAD
	arm_buffer4_t	arm_buffer;
	PyObject *x_attr;
	ArmSubbufferCharset *charset_ptr;
	ArmSubbufferAppIdentity *app_identity_ptr;
	ArmSubbufferAppContext *app_context_ptr;
	ArmSubbufferTranIdentity *tran_identity_ptr;
	ArmSubbufferTranContext *tran_context_ptr;
	ArmSubbufferArrivalTime *arrival_time_ptr;
	ArmSubbufferMetricBindings *metric_bindings_ptr;
	ArmSubbufferMetricValues *metric_values_ptr;
	ArmSubbufferUser *user_ptr;
	ArmSubbufferSystemAddress *system_address_ptr;
	ArmSubbufferDiagDetail *diag_detail_ptr;
} ArmBuffer;


static PyObject *
newArmBuffer(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ArmBuffer *self;

    self = (ArmBuffer *)type->tp_alloc(type, 0);
    if (self != NULL) {
		self->arm_buffer.count = 0;
		self->arm_buffer.subbuffer_array = NULL;
		self->charset_ptr = NULL;
		self->app_identity_ptr = NULL;
		self->app_context_ptr = NULL;
		self->tran_identity_ptr = NULL;
		self->tran_context_ptr = NULL;
		self->arrival_time_ptr = NULL;
		self->metric_bindings_ptr = NULL;
		self->metric_values_ptr = NULL;
		self->user_ptr = NULL;
		self->system_address_ptr = NULL;
		self->diag_detail_ptr = NULL;
    }

    return (PyObject *)self;
}

static void prepare (ArmBuffer *self)
{
	arm_subbuffer_t *sub_ptr = NULL;
	int i;

	/* The buffer should be empty at this point */
	self->arm_buffer.count = 0;
	if (self->arm_buffer.subbuffer_array == NULL) {
		/* Allocate the subbuffer array */
		self->arm_buffer.subbuffer_array = (arm_subbuffer_t **) malloc (MAX_SUBBUFFERS * sizeof(arm_subbuffer_t *));
		for (i = 0; i < MAX_SUBBUFFERS; i++)
			self->arm_buffer.subbuffer_array [i] = NULL;
	}

	if (self->charset_ptr)
	{
		sub_ptr = (arm_subbuffer_t *) &(self->charset_ptr->arm_buffer);
		self->arm_buffer.subbuffer_array [self->arm_buffer.count++] = sub_ptr;
	}
	if (self->app_identity_ptr)
	{
		sub_ptr = (arm_subbuffer_t *) &(self->app_identity_ptr->arm_buffer);
		self->arm_buffer.subbuffer_array [self->arm_buffer.count++] = sub_ptr;
	}
	if (self->app_context_ptr)
	{
		sub_ptr = (arm_subbuffer_t *) &(self->app_context_ptr->arm_buffer);
		self->arm_buffer.subbuffer_array [self->arm_buffer.count++] = sub_ptr;
	}
	if (self->tran_identity_ptr)
	{
		sub_ptr = (arm_subbuffer_t *) &(self->tran_identity_ptr->arm_buffer);
		self->arm_buffer.subbuffer_array [self->arm_buffer.count++] = sub_ptr;
	}
	if (self->tran_context_ptr)
	{
		sub_ptr = (arm_subbuffer_t *) &(self->tran_context_ptr->arm_buffer);
		self->arm_buffer.subbuffer_array [self->arm_buffer.count++] = sub_ptr;
	}
	if (self->arrival_time_ptr)
	{
		sub_ptr = (arm_subbuffer_t *) &(self->arrival_time_ptr->arm_buffer);
		self->arm_buffer.subbuffer_array [self->arm_buffer.count++] = sub_ptr;
	}
	if (self->metric_bindings_ptr)
	{
		sub_ptr = (arm_subbuffer_t *) &(self->metric_bindings_ptr->arm_buffer);
		self->arm_buffer.subbuffer_array [self->arm_buffer.count++] = sub_ptr;
	}
	if (self->metric_values_ptr)
	{
		sub_ptr = (arm_subbuffer_t *) &(self->metric_values_ptr->arm_buffer);
		self->arm_buffer.subbuffer_array [self->arm_buffer.count++] = sub_ptr;
	}
	if (self->user_ptr)
	{
		sub_ptr = (arm_subbuffer_t *) &(self->user_ptr->arm_buffer);
		self->arm_buffer.subbuffer_array [self->arm_buffer.count++] = sub_ptr;
	}
	if (self->system_address_ptr)
	{
		sub_ptr = (arm_subbuffer_t *) &(self->system_address_ptr->arm_buffer);
		self->arm_buffer.subbuffer_array [self->arm_buffer.count++] = sub_ptr;
	}
	if (self->diag_detail_ptr)
	{
		sub_ptr = (arm_subbuffer_t *) &(self->diag_detail_ptr->arm_buffer);
		self->arm_buffer.subbuffer_array [self->arm_buffer.count++] = sub_ptr;
	}
}

/* ArmBuffer methods */

static void
ArmBuffer_dealloc(ArmBuffer *self)
{
	if (self->arm_buffer.subbuffer_array != NULL)
		free (self->arm_buffer.subbuffer_array);

	Py_XDECREF (self->charset_ptr);
	Py_XDECREF (self->app_identity_ptr);
	Py_XDECREF (self->app_context_ptr);
	Py_XDECREF (self->tran_identity_ptr);
	Py_XDECREF (self->tran_context_ptr);
	Py_XDECREF (self->arrival_time_ptr);
	Py_XDECREF (self->metric_bindings_ptr);
	Py_XDECREF (self->metric_values_ptr);
	Py_XDECREF (self->user_ptr);
	Py_XDECREF (self->system_address_ptr);
	Py_XDECREF (self->diag_detail_ptr);

	PyObject_Del(self);
}

PyDoc_STRVAR(ArmBuffer_add_subbuffer__doc__,
"add_subbuffer(sub_buffer): add a sub-buffer\n"
"\n"
"DESCRIPTION\n"
"  Adds a sub-buffer object to the user data buffer. This can then be passed to any of the arm4\n"
"  methods as required and appropriate.\n"
"\n"
"  This abstracts the ARM 4 arm_buffer4_t internals\n"
"PARAMETERS\n"
"  sub_buffer   A valid ArmSubbuffer* object\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
ArmBuffer_add_subbuffer (ArmBuffer *self, PyObject *args)
{
	PyObject *subbuffer;

	/*
	 * Supported calling signatures:
	 *	add_subbuffer (subbuffer)
	 */
    if (!PyArg_ParseTuple(args, "O", &subbuffer))
        return NULL;

	if (ArmSubbufferCharset_Object_Check(subbuffer))
	{
		Py_XDECREF (self->charset_ptr);
		self->charset_ptr = (ArmSubbufferCharset *) subbuffer;
	}
	else if (ArmSubbufferAppIdentity_Object_Check(subbuffer))
	{
		Py_XDECREF (self->app_identity_ptr);
		self->app_identity_ptr = (ArmSubbufferAppIdentity *) subbuffer;
	}
	else if (ArmSubbufferAppContext_Object_Check(subbuffer))
	{
		Py_XDECREF (self->app_context_ptr);
		self->app_context_ptr = (ArmSubbufferAppContext *) subbuffer;
	}
	else if (ArmSubbufferTranIdentity_Object_Check(subbuffer))
	{
		Py_XDECREF (self->tran_identity_ptr);
		self->tran_identity_ptr = (ArmSubbufferTranIdentity *) subbuffer;
	}
	else if (ArmSubbufferTranContext_Object_Check(subbuffer))
	{
		Py_XDECREF (self->tran_context_ptr);
		self->tran_context_ptr = (ArmSubbufferTranContext *) subbuffer;
	}
	else if (ArmSubbufferArrivalTime_Object_Check(subbuffer))
	{
		Py_XDECREF (self->arrival_time_ptr);
		self->arrival_time_ptr = (ArmSubbufferArrivalTime *) subbuffer;
	}
	else if (ArmSubbufferMetricBindings_Object_Check(subbuffer))
	{
		Py_XDECREF (self->metric_bindings_ptr);
		self->metric_bindings_ptr = (ArmSubbufferMetricBindings *) subbuffer;
	}
	else if (ArmSubbufferMetricValues_Object_Check(subbuffer))
	{
		Py_XDECREF (self->metric_values_ptr);
		self->metric_values_ptr = (ArmSubbufferMetricValues *) subbuffer;
	}
	else if (ArmSubbufferUser_Object_Check(subbuffer))
	{
		Py_XDECREF (self->user_ptr);
		self->user_ptr = (ArmSubbufferUser *) subbuffer;
	}
	else if (ArmSubbufferSystemAddress_Object_Check(subbuffer))
	{
		Py_XDECREF (self->system_address_ptr);
		self->system_address_ptr = (ArmSubbufferSystemAddress *) subbuffer;
	}
	else if (ArmSubbufferDiagDetail_Object_Check(subbuffer))
	{
		Py_XDECREF (self->diag_detail_ptr);
		self->diag_detail_ptr = (ArmSubbufferDiagDetail *) subbuffer;
	}
	else
		return NULL;

	/* Since we're saving a copy... */
	Py_INCREF (subbuffer);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef ArmBuffer_methods[] = {
	{"add_subbuffer",	(PyCFunction)ArmBuffer_add_subbuffer,	METH_VARARGS, ArmBuffer_add_subbuffer__doc__},
	{NULL,		NULL}		/* sentinel */
};

PyDoc_STRVAR(ArmBuffer_type__doc__,
"Many of the ARM function calls provide a way for the application and ARM implementation to\n"
"exchange optional data, in addition to the required data in other function parameters. This buffer\n"
"describes the format of the exchanged data.\n"
"\n"
"Almost all functions define a ArmBuffer parameter. When the value is provided, the value points to\n"
"a buffer containing a number of sub-buffers. It differs from the ARM 2.0 format in that the buffer\n"
"contains  pointers to sub-buffers, rather than inline contiguous data. The sub-buffers contain the\n"
"meaningful data. The internals of this buffer are hidden in the ArmBuffer object.\n"
"\n"
"Each sub-buffer may be in the user data buffer once. If there is more than one instance of a sub-\n"
"buffer in the buffer, all instances after the first will be ignored.\n"
);

static PyTypeObject ArmBuffer_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyVarObject_HEAD_INIT(NULL, 0)
	"arm4.ArmBuffer",		/*tp_name*/
	sizeof(ArmBuffer),		/*tp_basicsize*/
	0,						/*tp_itemsize*/
	/* methods */
	(destructor)ArmBuffer_dealloc, /*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	0,						/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,     /*tp_flags*/
	ArmBuffer_type__doc__,  /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	ArmBuffer_methods,      /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	newArmBuffer,           /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

PyDoc_STRVAR(arm4_register_application__doc__,
"register_application(app_name, [buffer]): describe application\n"
"\n"
"DESCRIPTION\n"
"  register_application() describes metadata about an application.\n"
"\n"
"  The application uses register_application() to inform the ARM library of metadata about\n"
"  the application. This metadata does not change from one application instance to another. It\n"
"  contains part of the function of the ARM 2.0 call arm_init(); start_application() contains\n"
"  the other part.\n"
"\n"
"  ARM generates an ID that is passed in register_transaction() and start_application().\n"
"PARAMETERS\n"
"  app_name     Pointer to a null-terminated string containing the name of the application. The\n"
"               maximum length of the name is 128 characters, including the termination character.\n"
"               It serves no purpose and is illegal to make this call if the pointer is null. A name\n"
"               should be chosen that is unique, so generic names that might be used by a different\n"
"               development team, such as \"Payroll Application\", should not be used. The name\n"
"               should not contain trailing blank characters or consist of only blank characters. If\n"
"               the application has a copyrighted product name, the copyrighted name would be a\n"
"               good choice.\n"
"  buffer       An ArmBuffer object, if any. The sub-buffer formats that might be used are\n"
"               ArmSubbufferAppIdentity and ArmSubbufferEncoding.\n"
"RETURN VALUE\n"
"  An ArmID object app_id.\n"
);

static PyObject *
register_application(PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	arm_id_t app_id;
	const char *app_name;
	ArmBuffer *buffer = NULL;
	arm_buffer4_t *buffer_ptr = NULL;

	/*
	 * Supported calling signatures:
	 *	register_application ("Name")
	 *	register_application ("Name",(buffers...))
	 */
	static char *kwlist[] = {"app_name", "buffer", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "s|O:register_application", kwlist, &app_name, &buffer))
        return NULL;
	if (buffer && ArmBuffer_Object_Check(buffer))
	{
		prepare (buffer);
		buffer_ptr = &(buffer->arm_buffer);
	}

	status = arm_register_application(
		app_name,	/* application name */
		NULL,		/* input app id */
		0,			/* flags */
		buffer_ptr,		/* buffer4 */
		&app_id);	/* output app id */
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_register_application");
		return NULL;
	}

	/* Return the application ID */
	PyObject *id_ptr = (PyObject *) newArmID (&app_id);
	return id_ptr;
}

PyDoc_STRVAR(arm4_destroy_application__doc__,
"destroy_application(app_id): destroy application data\n"
"\n"
"DESCRIPTION\n"
"  destroy_application() indicates that the registration data about an application previously\n"
"  registered with register_application() is no longer needed.\n"
"  The purpose of this call is to signal the ARM implementation so it can release any storage it is\n"
"  holding. Ending a process or unloading the ARM library results in an implicit\n"
"  destroy_application() for any previously registered applications.\n"
"  It is possible for multiple register_application() calls to be made in the same process with\n"
"  identical identity data. When this is done, destroy_application() is assumed to be paired\n"
"  with one register_application(). For example, if register_application() is executed\n"
"  twice with the same output ID, and destroy_application() is executed once using this ID, it\n"
"  is assumed that an instance of the application is still active and it is not safe to discard the\n"
"  application registration data associated with the ID.\n"
"PARAMETERS\n"
"  app_id        ArmID object returned from a register_application() call in the same\n"
"                process.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
destroy_application(PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	ArmID *app_id;

	/*
	 * Supported calling signatures:
	 *	destroy_application (app_id)
	 */
	static char *kwlist[] = {"app_id", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "O:destroy_application", kwlist, &app_id))
		return NULL;
	if (!ArmID_Object_Check(app_id))
		return NULL;

	status = arm_destroy_application(
		&(app_id->arm_id),
		0,
		NULL); /* No buffers defined */
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_destroy_application");
		return NULL;
	}

	/* Empty return */
	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(arm4_register_transaction__doc__,
"register_transaction(app_id, name, [buffer]): describe transaction\n"
"\n"
"DESCRIPTION\n"
"  register_transaction() describes metadata about a transaction.\n"
"\n"
"  The application uses register_transaction() to inform the ARM library of metadata about\n"
"  the transaction measured by the application. This metadata does not change from one application\n"
"  instance to another. It is the equivalent of the ARM 2.0 call arm_getid().\n"
"\n"
"  ARM generates an ID that is passed in start_transaction() and report_transaction().\n"
"PARAMETERS\n"
"  app_id        Application ID returned from an arm_register_application() call in the same\n"
"                process.\n"
"  buffer        ArmBuffer object, if any. The sub-buffers that may be used are ArmSubbufferMetricBindings\n"
"                and ArmSubbufferTranIdentity. The names of any transaction context properties are supplied\n"
"                in the ArmSubbufferTranIdentity sub-buffer. They do not change afterwards; that is, the\n"
"                names are immutable. The transaction context values may change with each start_transaction()\n"
"                or report_transaction().\n"
"  tran_name     A string containing the name of the transaction. Each transaction registered by an application\n"
"                must have a unique name. The maximum length of the string is 127 characters. The name should\n"
"                not contain trailing blank characters or consist of only blank characters.\n"
"RETURN VALUE\n"
"  An ArmID object tran_id.\n"
);

static PyObject *
register_transaction (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	arm_id_t tran_id;
	ArmID *app_id;
	const char *transaction_name;
	ArmBuffer *buffer = NULL;
	arm_buffer4_t *buffer_ptr = NULL;

	/*
	 * Supported calling signatures:
	 *	register_transaction (app_id, "Name")
	 *	register_transaction (app_id, "Name",(buffers...))
	 */
	static char *kwlist[] = {"app_id", "tran_name", "buffer", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "Os|O:register_transaction", kwlist,
									  &app_id, &transaction_name, &buffer))
        return NULL;
	if (!ArmID_Object_Check(app_id))
		return NULL;
	if (buffer && ArmBuffer_Object_Check(buffer))
	{
		prepare (buffer);
		buffer_ptr = &(buffer->arm_buffer);
	}

	status = arm_register_transaction(
		&(app_id->arm_id),
		transaction_name,
		NULL,
		0,
		buffer_ptr,
		&tran_id);
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_register_transaction");
		return NULL;
	}

	/* Return the transaction ID */
	PyObject *id_ptr = (PyObject *) newArmID (&tran_id);
	return id_ptr;
}

PyDoc_STRVAR(arm4_register_metric__doc__,
"register_metric(app_id, name, format, usage, [units]): describe metrics\n"
"\n"
"DESCRIPTION\n"
"  register_metric() describes metadata about a metric.\n"
"\n"
"  The application uses register_metric() to inform the ARM library of metadata about each\n"
"  metric the application provides.\n"
"\n"
"  ARM generates an ArmID object that is passed in the ArmSubbufferMetricBindings object\n"
"  to register_transaction().\n"
"PARAMETERS\n"
"  app_id       ArmID object returned from a register_application() call in the same process.\n"
"  format       Describes the data type. The value must be one of the following values.\n"
"                     ARM_METRIC_FORMAT_COUNTER32 = arm_int32_t counter\n"
"                     ARM_METRIC_FORMAT_COUNTER64 = arm_int64_t counter\n"
"                     ARM_METRIC_FORMAT_CNTRDIVR = arm_int32_t counter + arm_int32_t divisor\n"
"                     ARM_METRIC_FORMAT_GAUGE32 = arm_int32_t gauge\n"
"                     ARM_METRIC_FORMAT_GAUGE64 = arm_int64_t gauge\n"
"                     ARM_METRIC_FORMAT_GAUGEDIVR32 = arm_int32_t gauge + arm_int32_t divisor\n"
"                     ARM_METRIC_FORMAT_NUMERICID32 = arm_int32_t numeric ID\n"
"                     ARM_METRIC_FORMAT_NUMERICID64 = arm_int64_t numeric ID\n"
"                     ARM_METRIC_FORMAT_STRING32 = string of a maximum length of 32 characters\n"
"  name         A string containing the name of the metric. The maximum length of the string is\n"
"               127 characters. The name should not contain trailing blank characters or consist\n"
"               of only blank characters.\n"
"\n"
"               The name can be any string, with one exception. Strings beginning with the four\n"
"               characters \"ARM:\" are reserved for the ARM specification. The specification will\n"
"               define names with known semantics using this prefix. One name format is currently\n"
"               defined. Any name beginning with the eight character prefix \"ARM:CIM:\"\n"
"               represents a name defined using the DMTF CIM (Distributed Management Task\n"
"               Force Common Information Model) naming rules. For example,\n"
"               \"ARM:CIM:CIM_SoftwareElement.Name\" indicates that the metric value has the\n"
"               semantics of the Name property of the CIM_SoftwareElement class. It is anticipated\n"
"               that additional naming semantics are likely to be added in the future.\n"
"  units        Pointer to a null-terminated string containing the units (such as \"files transferred\")\n"
"               of the metric. The maximum length of the string is 127 characters\n"
"  usage        Describes how the metric is used. The value must be one of the following values, or\n"
"               a negative value (any negative value is specific to the application; the negative\n"
"               values are not expected to be widely used).\n"
"                    ARM_METRIC_USE_GENERAL = a metric without a specified usage. Most\n"
"                                             metrics are described with a GENERAL usage.\n"
"                    ARM_METRIC_USE_TRAN_SIZE = a metric that indicates the size of a transaction. The size\n"
"                                             is something that would be expected to affect the response\n"
"                                             time, such as the number of bytes in a file transfer or the\n"
"                                             number of files backed up by a backup transaction. ARM\n"
"                                             implementations can use this knowledge to better\n"
"                                             interpret the response time.\n"
"                    ARM_METRIC_USE_TRAN_STATUS = a metric that further explains the transaction status\n"
"                                             passed on stop_transaction(), such as a sense code that\n"
"                                             explains why a transaction failed.\n"
"RETURN VALUE\n"
"  An ArmID object metric_id.\n"
);

static PyObject *
register_metric (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	arm_id_t metric_id;
	ArmID *app_id;
	char *name;
    int format;
    int usage;
    char *units = NULL;

	/*
	 * Supported calling signatures:
	 *	register_metric (app_id, "Name", format, usage, "units")
	 */
	static char *kwlist[] = {"app_id", "name", "format", "usage", "units", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "Osii|s:register_metric", kwlist,
			&app_id, &name, &format, &usage, &units))
        return NULL;
	if (!ArmID_Object_Check(app_id))
		return NULL;

	status = arm_register_metric(
		&(app_id->arm_id),
		name,
		format,
		usage,
		units,
		NULL,
		0,
		NULL, /* No sub-buffers defined */
		&metric_id);
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_register_metric");
		return NULL;
	}

	/* Return the transaction ID */
	PyObject *id_ptr = (PyObject *) newArmID (&metric_id);
	return id_ptr;
}

PyDoc_STRVAR(arm4_start_application__doc__,
"start_application(app_id, [group_name, instance_name, buffer]): check application is running\n"
"\n"
"DESCRIPTION\n"
"  start_application() indicates that an instance of an application has started running and is\n"
"  prepared to make ARM calls. In many cases, there will be only one application instance in a\n"
"  process, but there are cases in which there could be multiple instances. An example of multiple\n"
"  application instances in the same process is if several Java applications run in the same JVM\n"
"  (Java Virtual Machine) in the same process, and they each call the ARM 4.0 C interface (either\n"
"  directly, or indirectly via an implementation of the ARM 4.0 Java interface). They might share\n"
"  the same application ID or they might be separately registered.\n"
"\n"
"  Application context properties may be used to differentiate between instances. The values do not\n"
"  have to be different from other instances, though making them unique is suggested. The context\n"
"  properties are provided through function parameters and/or a sub-buffer.\n"
"\n"
"  The group and instance names are provided as function parameters.\n"
"\n"
"  Up to twenty (name,value) pairs of context properties may be provided in a sub-buffer.\n"
"\n"
"  There is a special case in which a system address sub-buffer is provided. The system address\n"
"  sub-buffer is provided when report_transaction() will be used to report data about\n"
"  transactions that executed on a different system. In this case, the start_application()\n"
"  provides a scoping context for the transaction instances, but does not indicate that the\n"
"  application instance is running on the local system.\n"
"\n"
"  The combination of register_application() and start_application() is equivalent to the\n"
"  ARM 2.0 call arm_init().\n"
"PARAMETERS\n"
"  app_group A string containing the identity of a group of application instances, if any. Application\n"
"            instances for a given software product that are started for a common runtime purpose are\n"
"            typically very good candidates for using the same group name. For example, identical\n"
"            replica instances of a product started across multiple processes or servers to address\n"
"            a specific transaction workload objective can be, advantageously to the ARM agent,\n"
"            commonly identified by the group name. The maximum length of the string is 255\n"
"            characters.\n"
"  app_id    An ArmID object returned by a register_application() call.\n"
"  app_instance\n"
"            A string containing the identity of this instance of the application. It might contain\n"
"            the process ID, or a UUID in printable characters, for example. The maximum length of\n"
"            the string is 255.\n"
"  buffer    An ArmBuffer object containing the user data buffer, if any. The sub-buffer formats that\n"
"            might be used are ArmSubbufferAppContext and ArmSubbufferSystemAddress.\n"
"\n"
"            If no system address sub-buffer is provided on start_application(), all\n"
"            transactions reported by this application instance execute in the current process.\n"
"\n"
"            If a system address sub-buffer is provided on start_application(), all\n"
"            transactions execute in a different process.\n"
"\n"
"            If a system address sub-buffer is provided in which the system address length is\n"
"            zero, or the system address pointer is null, the system is the local system, as\n"
"            determined by the ARM implementation.\n"
"\n"
"            If a system address sub-buffer is provided in which there is a non-null system\n"
"            address and length, the system may be the local system or a remote system.\n"
"            Interpretation of what is local versus remote is at the discretion of the ARM\n"
"            implementation.\n"
"RETURN VALUE\n"
"  An ArmID object app_handle.\n"
);

static PyObject *
start_application (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	arm_app_start_handle_t app_handle;
	ArmID *app_id;
	const char *group_name = ARM_STRING_NONE;
	const char *instance_name = ARM_STRING_NONE;
	ArmBuffer *buffer = NULL;
	arm_buffer4_t *buffer_ptr = NULL;

	/*
	 * Supported calling signatures:
	 *	start_application (app_id)
	 *	start_application (app_id, "Group", "Instance")
	 *	start_application (app_id, "Group", "Instance",(buffers...))
	 */
	static char *kwlist[] = {"app_id", "group_name", "instance_name", "buffer", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "O|ssO:start_application", kwlist,
									  &app_id, &group_name, &instance_name, &buffer))
        return NULL;
	if (!ArmID_Object_Check(app_id))
		return NULL;
	if (buffer && ArmBuffer_Object_Check(buffer))
	{
		prepare (buffer);
		buffer_ptr = &(buffer->arm_buffer);
	}

	status = arm_start_application(
		&(app_id->arm_id),
		group_name,
		instance_name,
		0,
		buffer_ptr,
		&app_handle);
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_start_application");
		return NULL;
	}

	/* Return the transaction ID */
	PyObject *id_ptr = (PyObject *) newArmHandle (app_handle);
	return id_ptr;
}

PyDoc_STRVAR(arm4_stop_application__doc__,
"stop_application(app_handle): stop application\n"
"\n"
"DESCRIPTION\n"
"  stop_application() indicates that the application instance has finished making ARM calls. It\n"
"  typically means that the instance is ending, such as just prior to the process exiting or a thread\n"
"  that represents an application instance terminating.\n"
"\n"
"  For any transactions that are still in-process [start_transaction() executed without a\n"
"  matching stop_transaction()], an implicit discard_transaction() is executed.\n"
"\n"
"  If the start_application() used the system address sub-buffer to indicate that the ARM calls\n"
"  would be about an application instance on a different system, stop_application() indicates\n"
"  that no more calls about that application instance and its transactions will be made.\n"
"\n"
"  After executing stop_application(), no further calls should be made for this application,\n"
"  including calls for transactions created by this application, until a new instance session is\n"
"  started using start_application(). Data from any other calls that are made will be ignored.\n"
"  This function is the equivalent of the ARM 2.0 function arm_end().\n"
"PARAMETERS\n"
"  app_handle   The handle returned from an start_application() call in the same process.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
stop_application (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	ArmHandle *app_handle;

	/*
	 * Supported calling signatures:
	 *	stop_application (app_handle)
	 */
	static char *kwlist[] = {"app_handle", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "O:stop_application", kwlist, &app_handle))
        return NULL;
	if (!ArmHandle_Object_Check(app_handle))
		return NULL;

	status = arm_stop_application(
		app_handle->arm_handle,
		0,
		NULL);
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_stop_application");
		return NULL;
	}

	/* Empty return */
	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(arm4_start_transaction__doc__,
"start_transaction(app_handle, tran_id, [parent, correlator, flags, buffer]): start transaction\n"
"\n"
"DESCRIPTION\n"
"  start_transaction() is used to indicate that a transaction is beginning execution.\n"
"\n"
"  Call start_transaction() just prior to a transaction beginning execution. start_transaction()\n"
"  signals the ARM library to start timing the transaction response time. There is one exception: when\n"
"  get_arrival_time() is used to get a start time before start_transaction() executes. See\n"
"  get_arrival_time() to understand this usage.\n"
"\n"
"  start_transaction() is also the means to pass to ARM the correlation token (called a correlator in\n"
"  ARM) from a caller - the parent - and to request a correlator that can be passed to transactions\n"
"  called by this transaction. The correlation token may be used to establish a calling hierarchy across\n"
"  processes and systems. A correlator contains a two-byte length field, a one-byte format ID, a one-byte\n"
"  flag field, plus it may contain other data that is used to uniquely identify an instance of a transaction.\n"
"  Applications do not need to understand correlator internals. The maximum length of a correlator is 512\n"
"  (ARM_CORR_MAX_LENGTH) bytes. (In ARM 2.0 it was 168 bytes.)\n"
"PARAMETERS\n"
"  app_handle   An ArmHandle object returned from a start_application() call in the same process.\n"
"  buffer       An ArmBuffer object containing the user data buffer, if any. The sub-buffers that may be\n"
"               used are ArmSubbufferArrivalTime, ArmSubbufferMetricValues, ArmSubbufferTranContext, and\n"
"               ArmSubbufferUser.\n"
"  correlator   An ArmCorrelator object into which the ARM implementation will store a correlator for\n"
"               the transaction instance, if any. If this parameter is not provided, the application is\n"
"               not requesting that a correlator be created.\n"
"\n"
"               If the correlator object is provided, the application is requesting that a correlator be\n"
"               created. In this case the ARM implementation may (but need not) create a correlator in the\n"
"               object. It may not create a correlator if it does not support the function or if it is\n"
"               configured to not create a correlator.\n"
"\n"
"               After start_transaction() completes, the application tests the length field using\n"
"               the ArmCorrelator length() method to determine whether a correlator has been stored. If\n"
"               the length is still zero, no correlator has been stored. The ARM implementation\n"
"               must store zero in the length field if it does not generate a correlator.\n"
"\n"
"  flags        Contains 32-bit flags which may be combined using a bitwise or. Three flags are defined:\n"
"                   ARM_FLAG_TRACE_REQUEST = the application requests/suggests a trace.\n"
"                   ARM_FLAG_BIND_THREAD = the started transaction is bound to this thread. Setting this\n"
"                       flag is equivalent to immediately calling bind_thread() after the start_transaction()\n"
"                       completes, except the timing is a little more accurate and the extra call is avoided.\n"
"                   ARM_FLAG_CORR_IN_PROCESS = the application is stating that it will not send the correlator\n"
"	                   outside the current process. An ARM implementation may be able to optimize correlator\n"
"	                   handling if it knows this, because it may be able to avoid serialization to create\n"
"                       the correlator.\n"
"  parent       An ArmCorrelator object from the parent transaction.\n"
"  tran_id      An ArmID transaction ID returned from a register_transaction() call in the same process.\n"
"RETURN VALUE\n"
"  An ArmHandle object that will represent the transaction instance in all calls, up to and including\n"
"  the stop_transaction() that indicates that the instance has completed executing.\n"
"\n"
"  The scope of the handle is the process in which the start_transaction() is executed.\n"
);

static PyObject *
start_transaction (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	ArmHandle *app_handle;
	ArmID *tran_id;
	ArmHandle *tran_handle;
	ArmCorrelator *parent = NULL;
	arm_correlator_t *parent_ptr = NULL;
	ArmCorrelator *correlator = NULL;
	arm_correlator_t *correlator_ptr = NULL;
	int flags = ARM_FLAG_NONE;
	ArmBuffer *buffer = NULL;
	arm_buffer4_t *buffer_ptr = NULL;

	/*
	 * Supported calling signatures:
	 *	start_transaction (app_handle, tran_id, parent=, correlator=)
	 *	start_transaction (app_handle, tran_id, parent=, correlator=, (buffers...))
	 */

	static char *kwlist[] = {"app_handle", "tran_id", "parent", "correlator", "flags", "buffer", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "OO|OOiO:start_transaction", kwlist,
				&app_handle, &tran_id, &parent, &correlator, &flags, &buffer))
        return NULL;
	if (!ArmHandle_Object_Check(app_handle))
		return NULL;
	if (!ArmID_Object_Check(tran_id))
		return NULL;
	if (buffer && ArmBuffer_Object_Check(buffer))
	{
		prepare (buffer);
		buffer_ptr = &(buffer->arm_buffer);
	}

	/* Set up our optional parameters */
	if (parent && ArmCorrelator_Object_Check (parent))
		parent_ptr = &(parent->arm_correlator);
	else
		parent_ptr = NULL;
	if (correlator && ArmCorrelator_Object_Check (correlator))
		correlator_ptr = &(correlator->arm_correlator);
	else
		correlator_ptr = NULL;

	tran_handle = newArmHandle (0);

	status = arm_start_transaction(
		app_handle->arm_handle,
		&(tran_id->arm_id),
		parent_ptr,
		flags,
		buffer_ptr,
		&(tran_handle->arm_handle),
		correlator_ptr);
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_start_transaction");
		return NULL;
	}

	/* Return the transaction handle */
	return (PyObject *) tran_handle;
}

PyDoc_STRVAR(arm4_stop_transaction__doc__,
"stop_transaction(tran_handle, [status, buffer]): stop transaction\n"
"\n"
"DESCRIPTION\n"
"  stop_transaction() signals the end of a transaction.\n"
"\n"
"  Call stop_transaction() just after a transaction completes. start_transaction() signals\n"
"  the ARM library to start timing the transaction response time. stop_transaction() signals\n"
"  the ARM library to stop timing the transaction response time. It can be called from any thread in\n"
"  the process that executed the start_transaction().\n"
"\n"
"  Implicit unbind_thread() and unblock_transaction() calls are made for any pending\n"
"  bind_thread() and block_transaction() calls, respectively, that have not been\n"
"  explicitly unbound or unblocked with unbind_thread() and unblock_transaction().\n"
"PARAMETERS\n"
"  buffer       An ArmBuffer user data buffer, if any. The sub-buffers that may be used are\n"
"               ArmSubbufferDiagDetail and ArmSubbufferMetricValues.\n"
"  tran_handle  An ArmHandle object returned from a start_transaction() call in the same process.\n"
"  tran_status  Indicates the status of the transaction. The following values are allowed:\n"
"                   ARM_STATUS_GOOD = transaction completed successfully. This is the default.\n"
"                   ARM_STATUS_ABORTED = transaction was aborted before it completed. For\n"
"                       example, the user might have pressed Stop or Back on a browser while a\n"
"                       transaction was in process, causing the transaction, as measured at the browser, to\n"
"                       be aborted.\n"
"                   ARM_STATUS_FAILED = transaction completed in error\n"
"                   ARM_STATUS_UNKNOWN = transaction completed but the status was unknown. This would\n"
"                       most likely occur if middleware or some other form of proxy instrumentation\n"
"                       measured the transaction. This instrumentation may know enough to know when the\n"
"                       transaction starts and stops, but does not understand the application-specific\n"
"                       semantics sufficiently well to know whether the transaction was successful.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
stop_transaction (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	ArmHandle *tran_handle;
	arm_tran_status_t tran_status = ARM_STATUS_GOOD;
	ArmBuffer *buffer = NULL;
	arm_buffer4_t *buffer_ptr = NULL;

	/*
	 * Supported calling signatures:
	 *	stop_transaction (tran_handle)
	 *	stop_transaction (tran_handle, status)
	 *	stop_transaction (tran_handle, status,(buffers...))
	 */
	static char *kwlist[] = {"tran_handle", "status", "buffer", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "O|"PARSE_INT32_FMT"O:stop_transaction", kwlist,
									 &tran_handle, &tran_status, &buffer))
        return NULL;
	if (!ArmHandle_Object_Check(tran_handle))
		return NULL;
	if (buffer && ArmBuffer_Object_Check(buffer))
	{
		prepare (buffer);
		buffer_ptr = &(buffer->arm_buffer);
	}

	status = arm_stop_transaction(
		tran_handle->arm_handle,
		tran_status,
		0,
		buffer_ptr);
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_stop_transaction");
		return NULL;
	}

	/* Empty return */
	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(arm4_update_transaction__doc__,
"update_transaction(tran_handle, [buffer]): get transaction status\n"
"\n"
"DESCRIPTION\n"
"  update_transaction() signals that a transaction is still processing.\n"
"\n"
"  update_transaction() is useful as a heartbeat. It is also used to pass additional data about a\n"
"  transaction. It can be called from any thread in the process that executed the start_transaction().\n"
"PARAMETERS\n"
"  buffer       An ArmBuffer object with the user data buffer, if any. The sub-buffer that might be used\n"
"               is ArmSubbufferMetricValues.\n"
"  tran_handle  An ArmHandle object returned from a start_transaction() call in the same process.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
update_transaction (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	ArmHandle *tran_handle;
	ArmBuffer *buffer = NULL;
	arm_buffer4_t *buffer_ptr = NULL;

	/*
	 * Supported calling signatures:
	 *	update_transaction (tran_handle)
	 *	update_transaction (tran_handle, (buffers...))
	 */
	static char *kwlist[] = {"tran_handle", "buffer", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "O|O:update_transaction", kwlist, &tran_handle, &buffer))
        return NULL;
	if (!ArmHandle_Object_Check(tran_handle))
		return NULL;
	if (buffer && ArmBuffer_Object_Check(buffer))
	{
		prepare (buffer);
		buffer_ptr = &(buffer->arm_buffer);
	}

	status = arm_update_transaction(
		tran_handle->arm_handle,
		0,
		buffer_ptr);
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_update_transaction");
		return NULL;
	}

	/* Empty return */
	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(arm4_discard_transaction__doc__,
"discard_transaction(tran_handle): discard transaction\n"
"\n"
"DESCRIPTION\n"
"  discard_transaction() signals that the referenced start_transaction() should be\n"
"  ignored and treated as if it never happened. Measurements associated with a transaction that is\n"
"  processing should be discarded. Either discard_transaction() or stop_transaction() is\n"
"  used - never both.\n"
"  An example of when a transaction would be discarded could happen is if proxy instrumentation\n"
"  believes a transaction is starting, but then learns that it did not. It can be called from any thread\n"
"  in the process that executed the start_transaction(). In general, the use of\n"
"  discard_transaction() is discouraged, but experience has shown a few use cases that\n"
"  require the functionality.\n"
"  discard_transaction() clears any thread bindings [bind_thread()] and blocking\n"
"  conditions [block_transaction()].\n"
"PARAMETERS\n"
"  tran_handle   A handle returned from an start_transaction() call in the same process.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
discard_transaction (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	ArmHandle *tran_handle;

	/*
	 * Supported calling signatures:
	 *	discard_transaction (tran_handle)
	 */
	static char *kwlist[] = {"tran_handle", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "O:discard_transaction", kwlist, &tran_handle))
        return NULL;
	if (!ArmHandle_Object_Check(tran_handle))
		return NULL;

	status = arm_discard_transaction(
		tran_handle->arm_handle,
		0,
		NULL); /* No buffers defined */
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_discard_transaction");
		return NULL;
	}

	/* Empty return */
	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(arm4_block_transaction__doc__,
"block_transaction(tran_handle): block transaction\n"
"\n"
"DESCRIPTION\n"
"  block_transaction() is used to indicate that the transaction instance is blocked waiting on\n"
"  an external transaction (which may or may not be instrumented with ARM) or some other event\n"
"  to complete. It has been found useful to separate out this blocked time from the elapsed time\n"
"  between the start_transaction() and stop_transaction().\n"
"  A transaction remains blocked until unblock_transaction() is executed passing the same\n"
"  block_handle, or either a discard_transaction() or stop_transaction() is executed passing the\n"
"  same tran_handle.\n"
"  The blocking conditions of most interest are those that could result in a significant and/or\n"
"  variable length delay relative to the response time of the transaction. For example, a remote\n"
"  procedure call would be a good situation to indicate with block_transaction() or\n"
"  unblock_transaction(), whereas a disk I/O would not.\n"
"  A transaction may be blocked by multiple conditions simultaneously. In many application\n"
"  architectures block_transaction() would be called just prior to a thread suspending, because\n"
"  the thread is waiting to be signaled that an event has occurred. In other application architectures\n"
"  there would not be a tight relationship between the thread behavior and the blocking conditions.\n"
"  bind_thread() and block_transaction() are used independently of each other.\n"
"PARAMETERS\n"
"  tran_handle   An ArmHandle object returned from an start_transaction() call in the same process.\n"
"RETURN VALUE\n"
"  block_handle  An ArmHandle object that is passed on to unblock_transaction() calls in the same\n"
"                process.\n"
);

static PyObject *
block_transaction (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	ArmHandle *tran_handle;
	ArmHandle *block_handle;

	/*
	 * Supported calling signatures:
	 *	block_transaction (tran_handle)
	 */
	static char *kwlist[] = {"tran_handle", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "O:block_transaction", kwlist, &tran_handle))
        return NULL;
	if (!ArmHandle_Object_Check(tran_handle))
		return NULL;

	block_handle = newArmHandle (0);
	status = arm_block_transaction(
		tran_handle->arm_handle,
		0,
		NULL, /* No valid buffer types */
		&(block_handle->arm_handle));
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_block_transaction");
		return NULL;
	}

	/* Return the handle */
	return (PyObject *) block_handle;
}

PyDoc_STRVAR(arm4_unblock_transaction__doc__,
"unblock_transaction(tran_handle, block_handle): unblock transaction\n"
"\n"
"DESCRIPTION\n"
"  unblock_transaction() indicates that the suspension indicated by the block_handle for the\n"
"  transaction identified by the start handle is no longer waiting for a downstream transaction to\n"
"  complete.\n"
"\n"
"  Call unblock_transaction() when a transaction is no longer blocked on an external event. It\n"
"  should be called when block_transaction() was previously called and the blocking\n"
"  condition no longer exists. Knowledge of when a transaction is blocked can be useful for better\n"
"  understanding response times. It is useful to separate out this blocked time from the elapsed\n"
"  start-to-stop time. The unblocked call is paired with a block call for finer grained analysis.\n"
"\n"
"  stop_transaction() is an implicit unblock_transaction() for any blocking condition for\n"
"  the transaction instance that has not been cleared yet [block_transaction() issued without a\n"
"  matching unblock_transaction()]. It should only be called without calling\n"
"  unblock_transaction() first when the blocking condition ends immediately prior to the\n"
"  transaction ending.\n"
"PARAMETERS\n"
"  block_handle  An ArmHandle object returned from a block_transaction() call in the same process.\n"
"  tran_handle   An ArmHandle object returned from a start_transaction() call in the same process.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
unblock_transaction (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	ArmHandle *tran_handle;
	ArmHandle *block_handle;

	/*
	 * Supported calling signatures:
	 *	unblock_transaction (tran_handle, block_handle)
	 */
	static char *kwlist[] = {"tran_handle", "block_handle", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "OO:unblock_transaction", kwlist, &tran_handle, &block_handle))
        return NULL;
	if (!ArmHandle_Object_Check(tran_handle))
		return NULL;
	if (!ArmHandle_Object_Check(block_handle))
		return NULL;

	status = arm_unblock_transaction(
		tran_handle->arm_handle,
		block_handle->arm_handle,
		0,
		NULL);
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_unblock_transaction");
		return NULL;
	}

	/* Empty return */
	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(arm4_bind_thread__doc__,
"bind_thread(tran_handle): bind thread\n"
"\n"
"DESCRIPTION\n"
"  bind_thread() indicates that the thread from which it is called is performing on behalf of\n"
"  the transaction identified by the start handle.\n"
"  The thread binding could be useful for managing computing resources at a finer level of\n"
"  granularity than a process. There can be any number of threads simultaneously bound to the\n"
"  same transaction.\n"
"  A transaction remains bound to a thread until either a _discard_transaction(),\n"
"  stop_transaction(), or unbind_thread() is executed passing the same start handle.\n"
"  bind_thread() and block_transaction() are used independently of each other.\n"
"PARAMETERS\n"
"  tran_handle   A handle returned a start_transaction() call in the same process.\n"
"RETURN VALUE\n"
"  None.\n"
);

static PyObject *
bind_thread (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	ArmHandle *tran_handle;

	/*
	 * Supported calling signatures:
	 *	bind_thread (tran_handle)
	 */
	static char *kwlist[] = {"tran_handle", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "O:bind_thread", kwlist, &tran_handle))
        return NULL;
	if (!ArmHandle_Object_Check(tran_handle))
		return NULL;

	status = arm_bind_thread(
		tran_handle->arm_handle,
		0,
		NULL); /* No valid buffers for this call */
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_bind_thread");
		return NULL;
	}

	/* Empty return */
	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(arm4_unbind_thread__doc__,
"unbind_thread(tran_handle): unbind a thread\n"
"\n"
"DESCRIPTION\n"
"  unbind_thread() indicates that the thread from which it is called is no longer performing on\n"
"  behalf of the transaction identified by the start handle.\n"
"\n"
"  Call unbind_thread() when a thread is no longer executing a transaction. The thread\n"
"  binding is useful for managing computing resources at a finer level of granularity than the\n"
"  process. It should be called when, for this transaction and this thread, either:\n"
"  o   bind_thread() was previously called, or\n"
"  o   The ARM_FLAG_BIND_THREAD flag was on in the start_transaction() call.\n"
"\n"
"  stop_transaction() is an implicit unbind_thread() for any threads still bound to the\n"
"  transaction instance [bind_thread() issued without a matching unbind_thread()]. As\n"
"  long as the transaction is bound to the thread when the stop_transaction() executes, there is\n"
"  no need nor any value in calling unbind_thread() before calling stop_transaction().\n"
"PARAMETERS\n"
"  tran_handle   An ArmHandle object returned from a start_transaction() call in the same process.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
unbind_thread (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	ArmHandle *tran_handle;

	/*
	 * Supported calling signatures:
	 *	unbind_thread (tran_handle)
	 */
	static char *kwlist[] = {"tran_handle", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "O:unbind_thread", kwlist, &tran_handle))
        return NULL;
	if (!ArmHandle_Object_Check(tran_handle))
		return NULL;

	status = arm_unbind_thread(
		tran_handle->arm_handle,
		0,
		NULL);
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_unbind_thread");
		return NULL;
	}

	/* Empty return */
	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(arm4_report_transaction__doc__,
"report_transaction(app_handle, tran_id, response_time, stop_time, [status, parent, correlator, flags, buffer):\n"
"                    report transaction statistics\n"
"\n"
"DESCRIPTION\n"
"  report_transaction() is used to report statistics about a transaction that has already\n"
"  completed.\n"
"\n"
"  report_transaction() may be used instead of a paired start_transaction() and\n"
"  stop_transaction() call. The application would have measured the response time. The\n"
"  transaction could have executed on the local system or on a remote system. If it executes on a\n"
"  remote system, the system address sub-buffer passed on the start_application() provides\n"
"  the addressing information for the remote system.\n"
"\n"
"  If the transaction represented by the report_transaction() call is the correlation parent of\n"
"  another transaction, generate_correlator() must be used to get a parent correlator, prior to\n"
"  invoking the child transaction (because it must be passed to the child). In this case, the sequence\n"
"  is the following:\n"
"\n"
"      1. generate_correlator() to get a correlator for this transaction.\n"
"      2. Invoke the child transaction, passing the correlator returned in step (1) to the child.\n"
"      3. When this transaction is complete, invoke report_transaction() to report the\n"
"         statistics about the transaction.\n"
"\n"
"  When used, it prevents certain types of proactive management, such as monitoring for hung\n"
"  transactions or adjusting priorities, because the ARM implementation is not invoked when the\n"
"  transaction is started. Because of this, the use of start_transction() and stop_transaction()\n"
"  is preferred over report_transaction().\n"
"\n"
"  The intended use is to report status and response time about transactions that recently completed\n"
"  (typically several seconds ago) in the absence of an ARM-enabled application and/or ARM\n"
"  implementation on the system on which the transaction executed.\n"
"PARAMETERS\n"
"  app_handle  A ArmID object returned from a start_application() call in the same process.\n"
"  buffer      An ArmBuffer object, if any. The sub-buffers that may be used are\n"
"              ArmSubbufferDiagDetail, ArmSubbufferMetricValues, ArmSubbufferTranContext, and\n"
"              ArmSubbufferUser.\n"
"  correlator  An ArmCorrelator object returned from generate_correlator(), if any.\n"
"  flags       ARM_FLAG_TRACE_REQUEST is the only valid flag if the application requests/suggests a\n"
"              trace.\n"
"  parent      An ArmCorrelator object for the parent transaction, if any.\n"
"  response_time\n"
"              Response time in nanoseconds.\n"
"  stop_time   A long integer that contains the number of milliseconds since Jan 1, 1970 using\n"
"              the Gregorian calendar. The time base is GMT (Greenwich Mean Time). There is\n"
"              one special value, ARM_USE_CURRENT_TIME, which means use the current time.\n"
"  tran_id     An ArmID transaction ID returned from a register_transaction() call in the same process.\n"
"  status      Indicates the status of the transaction. The following values are allowed:\n"
"                    ARM_STATUS_GOOD = transaction completed successfully. This is the default value.\n"
"                    ARM_STATUS_ABORTED = transaction was aborted before it completed. For example,\n"
"                        the user might have pressed Stop or Back on a browser while a transaction was\n"
"                        in process, causing the transaction, as measured at the browser, to be aborted.\n"
"                    ARM_STATUS_FAILED = transaction completed in error\n"
"                    ARM_STATUS_UNKNOWN = transaction completed but the status was unknown. This would\n"
"                        most likely occur if middleware or some other form of proxy instrumentation\n"
"                        measured the transaction. This instrumentation may know enough to know when\n"
"                        the transaction starts and stops, but does not understand the application-specific\n"
"                        semantics sufficiently well to know whether the transaction was successful.\n"
"RETURN VALUE\n"
"  None\n"
);

static PyObject *
report_transaction (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	ArmHandle *app_handle;
	ArmID *tran_id;
	arm_response_time_t response_time;
	arm_stop_time_t stop_time;
	arm_tran_status_t tran_status = ARM_STATUS_GOOD;
	ArmCorrelator *parent = NULL;
	arm_correlator_t *parent_ptr = NULL;
	ArmCorrelator *correlator = NULL;
	arm_correlator_t *correlator_ptr = NULL;
	int flags = ARM_FLAG_NONE;
	ArmBuffer *buffer = NULL;
	arm_buffer4_t *buffer_ptr = NULL;

	/*
	 * Supported calling signatures:
	 *	report_transaction (app_handle, tran_id, response_time, stop_time, status=, parent=, correlator=)
	 *	report_transaction (app_handle, tran_id, response_time, stop_time, status=, parent=, correlator=, (buffers...))
	 */

	static char *kwlist[] = {"app_handle", "tran_id", "response_time", "stop_time",
								"status", "parent", "correlator", "flags", "buffer", NULL};

	if (!PyArg_ParseTupleAndKeywords(args,
				keywds,
				"OO" PARSE_INT64_FMT PARSE_INT64_FMT "|" PARSE_INT32_FMT "OOiO:report_transaction",
				kwlist,
				&app_handle,
				&tran_id,
				&response_time,
				&stop_time,
				&tran_status,
				&parent,
				&correlator,
				&flags,
				&buffer))
        return NULL;
	if (!ArmHandle_Object_Check(app_handle))
		return NULL;
	if (!ArmID_Object_Check(tran_id))
		return NULL;
	if (buffer && ArmBuffer_Object_Check(buffer))
	{
		prepare (buffer);
		buffer_ptr = &(buffer->arm_buffer);
	}

	/* Set up our optional parameters */
	if (parent && ArmCorrelator_Object_Check (parent))
		parent_ptr = &(parent->arm_correlator);
	else
		parent_ptr = NULL;
	if (correlator && ArmCorrelator_Object_Check (correlator))
		correlator_ptr = &(correlator->arm_correlator);
	else
		correlator_ptr = NULL;

	status = arm_report_transaction(
		app_handle->arm_handle,
		&(tran_id->arm_id),
		tran_status,
		response_time,
		stop_time,
		parent_ptr,
		correlator_ptr,
		flags,
		buffer_ptr);
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_report_transaction");
		return NULL;
	}

	/* Empty return */
	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(arm4_generate_correlator__doc__,
"generate_correlator(app_handle, tran_id, [parent, flags, buffer]): generate a correlator\n"
"\n"
"DESCRIPTION\n"
"  generate_correlator() is used to generate a correlator for use with report_transaction().\n"
"\n"
"  A correlator is a correlation token passed from a calling transaction to a called transaction. The\n"
"  correlation token may be used to establish a calling hierarchy across processes and systems.\n"
"  Applications do not need to understand correlator internals.\n"
"\n"
"  It is useful to think about its use in the context of what start_transaction() and\n"
"  stop_transaction() do:\n"
"  o      start_transaction() performs two functions. It establishes the identity of a transaction\n"
"         instance (encapsulated in the current correlator) and begins the measurements of the\n"
"         instance. stop_transaction() causes the measurements to be captured. The start\n"
"         handle links a start_transaction() and a stop_transaction().\n"
"  o      generate_correlator() establishes the identity of a transaction instance, like\n"
"         start_transaction(), also encapsulating it in a correlator. It has no relationship to\n"
"         measurements about the transaction instance. report_transaction() combines the\n"
"         measurement function of both start_transaction() and stop_transaction().\n"
"\n"
"  Based on this positioning, it should be clear that generate_correlator() can be used\n"
"  whenever an start_transaction() can be used. More specifically, the following calls must\n"
"  have been executed first: register_application(), register_transaction(), and\n"
"  start_application(). The same parameters are also used, except there's no need for a start\n"
"  handle, and there's no need for the arrival time or metric values sub-buffers. The other sub-\n"
"  buffers may be used. The correlator that is returned can be used in the same way that a correlator\n"
"  returned from start_transaction() is used.\n"
"PARAMETERS\n"
"  app_handle The ArmHandle object returned from a start_application() call in the same process. The\n"
"             ARM implementation may use this handle to access application instance data that\n"
"             may become part of the correlator; e.g., the ArmSubbufferSystemAddress object.\n"
"  buffer     The ArmBuffer object, if any. The sub-buffers that may be used are\n"
"             ArmSubbufferTranContext, and ArmSubbufferUser.\n"
"  flags      Contains 32-bit flags. The may be or'ed together as required.\n"
"             ARM_FLAG_TRACE_REQUEST is specified if the application requests/suggests a trace.\n"
"             ARM_FLAG_CORR_IN_PROCESS is specified if the application is stating that it will not\n"
"                    send the correlator outside the current process. An ARM implementation may be\n"
"                    able to optimize correlator handling if it knows this, because it may be able\n"
"                    to avoid serialization to create the correlator.\n"
"  parent_correlator\n"
"             An ArmCorrelator object refferring to the parent correlator, if any.\n"
"  tran_id    An ArmID transaction ID returned from a register_transaction() call in the same process.\n"
"RETURN VALUE\n"
"             A ArmCorrelator object which contains a correlator for the transaction instance.\n"
);

static PyObject *
generate_correlator (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
	ArmHandle *app_handle;
	ArmID *tran_id;
	ArmCorrelator *parent = NULL;
	arm_correlator_t *parent_ptr = NULL;
	ArmCorrelator *correlator = NULL;
	arm_correlator_t *correlator_ptr = NULL;
	ArmBuffer *buffer = NULL;
	arm_buffer4_t *buffer_ptr = NULL;
	int flags = ARM_FLAG_NONE;

	/*
	 * Supported calling signatures:
	 *	generate_correlator (app_handle, tran_id, parent=, flags=, buffers=)
	 */

	static char *kwlist[] = {"app_handle", "tran_id", "parent", "flags", "buffer", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "OO|OiO:generate_correlator", kwlist,
				&app_handle, &tran_id, &parent, &flags, &buffer))
        return NULL;
	if (!ArmHandle_Object_Check(app_handle))
		return NULL;
	if (!ArmID_Object_Check(tran_id))
		return NULL;
	if (buffer && ArmBuffer_Object_Check(buffer))
	{
		prepare (buffer);
		buffer_ptr = &(buffer->arm_buffer);
	}

	/* Set up our optional parameters */
	if (parent && ArmCorrelator_Object_Check (parent))
		parent_ptr = &(parent->arm_correlator);
	else
		parent_ptr = NULL;

	correlator = newArmCorrelator (NULL);
	correlator_ptr = &(correlator->arm_correlator);

	status = arm_generate_correlator(
		app_handle->arm_handle,
		&(tran_id->arm_id),
		parent_ptr,
		flags,
		buffer_ptr,
		correlator_ptr);
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_generate_correlator");
		return NULL;
	}

	/* Return the correlator */
	return (PyObject *) correlator;
}

PyDoc_STRVAR(arm4_get_arrival_time__doc__,
"get_arrival_time(): store current time\n"
"\n"
"DESCRIPTION\n"
"  get_arrival_time() stores an opaque representation of the current time.\n"
"\n"
"  There are situations in which there is a significant delay between the time when processing of a\n"
"  transaction begins and when all the context property values that are needed before\n"
"  start_transaction() can be executed are known. In order to get a more accurate response\n"
"  time, get_arrival_time() can be used to capture an implementation-defined representation\n"
"  of the current time. This value is later stored in the ArmSubbufferArrivalTime sub-buffer when\n"
"  start_transaction() executes. The ARM library will use the arrival time as the start time\n"
"  rather than the moment when start_transaction() executes.\n"
"PARAMETERS\n"
"  None\n"
"RETURN VALUE\n"
"  An ArmArrivalTime object that will contain the arrival time value. Note that the\n"
"  value is implementation-defined so the application should not make any\n"
"  conclusions based on its contents.\n"
);

static PyObject *
get_arrival_time (PyObject *self, PyObject *args)
{
	/* Return a ArmArrivalTime object */
	return (PyObject *) newArmArrivalTime ();
}

PyDoc_STRVAR(arm4_is_charset_supported__doc__,
"is_charset_supported(charset): check character encoding\n"
"\n"
"DESCRIPTION\n"
"  is_charset_supported() indicates whether an ARM library supports a specified character\n"
"  encoding.\n"
"\n"
"  The default encoding for all strings provided by the application on all operating systems is\n"
"  UTF-8. An application may specify an alternate encoding when executing register_application(),\n"
"  and then use it for all strings it provides on all calls including register_application(), but\n"
"  should never do so without first issuing is_charset_supported() to test whether the value is\n"
"  supported.\n"
"\n"
"  An ARM library on the operating systems listed in Table 1 must support the specified\n"
"  encodings. Applications are encouraged to use one of these encodings to ensure that any ARM\n"
"  implementation will support the application's ARM instrumentation. Another alternative is to\n"
"  use one of these encodings along with a preferred encoding. If the ARM library supports the\n"
"  preferred encoding, it is used; otherwise, one of the mandatory encodings is used.\n"
"\n"
"  IANA                                  Character Set Common       UNIX     Microsoft   IBM      IBM\n"
"  MIBenum                                      Name                 and      Windows   OS/400    zOS\n"
"                                                                   Linux\n"
"\n"
"   3       ARM_CHARSET_ASCII             ASCII-7 (US-ASCII)         Yes      Yes         Yes      Yes\n"
"\n"
"   106     ARM_CHARSET_UTF8              UTF-8                      Yes      Yes         Yes      Yes\n"
"                                         (UCS-2 characters only)\n"
"\n"
"   1014    ARM_CHARSET_UTF16LE           UTF-16 Little Endian                Yes\n"
"                                         (UCS-2 characters only)\n"
"\n"
"   2028    ARM_CHARSET_IBM037            IBM037                                          Yes\n"
"\n"
"   2102    ARM_CHARSET_IBM1047           IBM1047                                                  Yes\n"
"\n"
"PARAMETERS\n"
"  charset      An IANA (Internet Assigned Numbers Authority - see http://www.iana.org) MIBenum\n"
"               value. Support for some values is mandatory by any ARM implementation on a\n"
"               specified platform, as shown in the table.\n"
"RETURN VALUE\n"
"  Boolean object that is set to true or false to indicate whether charset is a supported encoding.\n"
);

static PyObject *
is_charset_supported (PyObject *self, PyObject *args, PyObject *keywds)
{
    arm_error_t status;
    arm_charset_t charset;
	arm_boolean_t supported;

	/*
	 * Supported calling signatures:
	 *	is_charset_supported (charset)
	 */
	static char *kwlist[] = {"charset", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, PARSE_INT32_FMT ":is_charset_supported", kwlist, &charset))
        return NULL;

	status = arm_is_charset_supported(
		charset,
		&supported);
	if (GETSTATE0->enableExceptions && (status != ARM_SUCCESS))
	{
		set_arm_error (status, "arm_is_charset_supported");
		return NULL;
	}

	/* Return the flag value */
	return PyBool_FromLong (supported);
}

PyDoc_STRVAR(arm4_enable_exceptions__doc__,
"enable_exceptions(enable): enable exception generation\n"
"\n"
"DESCRIPTION\n"
"  enable_exceptions() is used to control the generation of exceptions by the arm4 module. One of\n"
"  the key principles of the ARM standard is that errors in the measurement of applications shouldn't\n"
"  affect the applications themselves. In the Python world, this means that no exceptions should\n"
"  be generated when the ARM routines encounter an error. Unfortunately this can make debugging\n"
"  difficult.\n"
"\n"
"  To give the programmer/developer the best of both worlds, exception processing can be turned on\n"
"  or off programatically. When debugging the instrumentation, it is best to have the exceptions\n"
"  turned on, while production dictates that no exceptions be generated.\n"
"\n"
"  By default, exception generation is turned off.\n"
"PARAMETERS\n"
"  enable       A integer boolean value indicating wether exceptions should be generated.\n"
"RETURN VALUE\n"
"  None.\n"
);

static PyObject *
enable_exceptions (PyObject *self, PyObject *args, PyObject *keywds)
{
	int enable;

	static char *kwlist[] = {"enabled", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "i:enable_exceptions", kwlist, &enable))
        return NULL;

	GETSTATE0->enableExceptions = enable;

	Py_INCREF(Py_None);
	return Py_None;
}


static PyMethodDef arm4_methods[] = {
	{"register_application", (PyCFunction)register_application, METH_VARARGS | METH_KEYWORDS, arm4_register_application__doc__},
	{"destroy_application",  (PyCFunction)destroy_application,  METH_VARARGS | METH_KEYWORDS, arm4_destroy_application__doc__},
	{"register_transaction", (PyCFunction)register_transaction, METH_VARARGS | METH_KEYWORDS, arm4_register_transaction__doc__},
	{"register_metric",      (PyCFunction)register_metric,      METH_VARARGS | METH_KEYWORDS, arm4_register_metric__doc__},
	{"start_application",    (PyCFunction)start_application,    METH_VARARGS | METH_KEYWORDS, arm4_start_application__doc__},
	{"stop_application",     (PyCFunction)stop_application,     METH_VARARGS | METH_KEYWORDS, arm4_stop_application__doc__},
	{"start_transaction",    (PyCFunction)start_transaction,    METH_VARARGS | METH_KEYWORDS, arm4_start_transaction__doc__},
	{"stop_transaction",     (PyCFunction)stop_transaction,     METH_VARARGS | METH_KEYWORDS, arm4_stop_transaction__doc__},
	{"update_transaction",   (PyCFunction)update_transaction,   METH_VARARGS | METH_KEYWORDS, arm4_update_transaction__doc__},
	{"discard_transaction",  (PyCFunction)discard_transaction,  METH_VARARGS | METH_KEYWORDS, arm4_discard_transaction__doc__},
	{"block_transaction",    (PyCFunction)block_transaction,    METH_VARARGS | METH_KEYWORDS, arm4_block_transaction__doc__},
	{"unblock_transaction",  (PyCFunction)unblock_transaction,  METH_VARARGS | METH_KEYWORDS, arm4_unblock_transaction__doc__},
	{"bind_thread",          (PyCFunction)bind_thread,          METH_VARARGS | METH_KEYWORDS, arm4_bind_thread__doc__},
	{"unbind_thread",        (PyCFunction)unbind_thread,        METH_VARARGS | METH_KEYWORDS, arm4_unbind_thread__doc__},
	{"report_transaction",   (PyCFunction)report_transaction,   METH_VARARGS | METH_KEYWORDS, arm4_report_transaction__doc__},
	{"generate_correlator",  (PyCFunction)generate_correlator,  METH_VARARGS | METH_KEYWORDS, arm4_generate_correlator__doc__},
	{"get_arrival_time",     get_arrival_time,                  METH_NOARGS,                  arm4_get_arrival_time__doc__},
	{"is_charset_supported", (PyCFunction)is_charset_supported, METH_VARARGS | METH_KEYWORDS, arm4_is_charset_supported__doc__},
	{"enable_exceptions",    (PyCFunction)enable_exceptions,    METH_VARARGS | METH_KEYWORDS, arm4_enable_exceptions__doc__},
	{NULL, NULL}
};

static void
init_constants (PyObject *module)
{
	/* Add symbolic constants to the module */

	/* Transaction status */
	PyModule_AddIntConstant(module, "ARM_STATUS_GOOD", ARM_STATUS_GOOD);
	PyModule_AddIntConstant(module, "ARM_STATUS_ABORTED", ARM_STATUS_ABORTED);
	PyModule_AddIntConstant(module, "ARM_STATUS_FAILED", ARM_STATUS_FAILED);
	PyModule_AddIntConstant(module, "ARM_STATUS_UNKNOWN", ARM_STATUS_UNKNOWN);

	/* --- current time for arm_report_transaction() stop time ------- */
	PyModule_AddIntConstant(module, "ARM_USE_CURRENT_TIME", ARM_USE_CURRENT_TIME);

	/* ------------- flags to be passed on API calls ----------------- */
	PyModule_AddIntConstant(module, "ARM_FLAG_NONE", ARM_FLAG_NONE);
	PyModule_AddIntConstant(module, "ARM_FLAG_TRACE_REQUEST", ARM_FLAG_TRACE_REQUEST);
	PyModule_AddIntConstant(module, "ARM_FLAG_BIND_THREAD", ARM_FLAG_BIND_THREAD);
	PyModule_AddIntConstant(module, "ARM_FLAG_CORR_IN_PROCESS", ARM_FLAG_CORR_IN_PROCESS);

	/* --------------- correlator defines ---------------------------- */
	PyModule_AddIntConstant(module, "ARM_CORR_FLAGNUM_APP_TRACE", ARM_CORR_FLAGNUM_APP_TRACE);
	PyModule_AddIntConstant(module, "ARM_CORR_FLAGNUM_AGENT_TRACE", ARM_CORR_FLAGNUM_AGENT_TRACE);

	/* -------------------- metric defines --------------------------- */
	PyModule_AddIntConstant(module, "ARM_METRIC_FORMAT_RESERVED", ARM_METRIC_FORMAT_RESERVED);
	PyModule_AddIntConstant(module, "ARM_METRIC_FORMAT_COUNTER32", ARM_METRIC_FORMAT_COUNTER32);
	PyModule_AddIntConstant(module, "ARM_METRIC_FORMAT_COUNTER64", ARM_METRIC_FORMAT_COUNTER64);
	PyModule_AddIntConstant(module, "ARM_METRIC_FORMAT_CNTRDIVR32", ARM_METRIC_FORMAT_CNTRDIVR32);
	PyModule_AddIntConstant(module, "ARM_METRIC_FORMAT_GAUGE32", ARM_METRIC_FORMAT_GAUGE32);
	PyModule_AddIntConstant(module, "ARM_METRIC_FORMAT_GAUGE64", ARM_METRIC_FORMAT_GAUGE64);
	PyModule_AddIntConstant(module, "ARM_METRIC_FORMAT_GAUGEDIVR32", ARM_METRIC_FORMAT_GAUGEDIVR32);
	PyModule_AddIntConstant(module, "ARM_METRIC_FORMAT_NUMERICID32", ARM_METRIC_FORMAT_NUMERICID32);
	PyModule_AddIntConstant(module, "ARM_METRIC_FORMAT_NUMERICID64", ARM_METRIC_FORMAT_NUMERICID64);
	PyModule_AddIntConstant(module, "ARM_METRIC_FORMAT_STRING32", ARM_METRIC_FORMAT_STRING32);

	PyModule_AddIntConstant(module, "ARM_METRIC_USE_GENERAL", ARM_METRIC_USE_GENERAL);
	PyModule_AddIntConstant(module, "ARM_METRIC_USE_TRAN_SIZE", ARM_METRIC_USE_TRAN_SIZE);
	PyModule_AddIntConstant(module, "ARM_METRIC_USE_TRAN_STATUS", ARM_METRIC_USE_TRAN_STATUS);

	/* -------------- system address format values ------------------- */
	PyModule_AddIntConstant(module, "ARM_SYSADDR_FORMAT_IPV4", ARM_SYSADDR_FORMAT_IPV4);
	PyModule_AddIntConstant(module, "ARM_SYSADDR_FORMAT_IPV4PORT", ARM_SYSADDR_FORMAT_IPV4PORT);
	PyModule_AddIntConstant(module, "ARM_SYSADDR_FORMAT_IPV6", ARM_SYSADDR_FORMAT_IPV6);
	PyModule_AddIntConstant(module, "ARM_SYSADDR_FORMAT_IPV6PORT", ARM_SYSADDR_FORMAT_IPV6PORT);
	PyModule_AddIntConstant(module, "ARM_SYSADDR_FORMAT_SNA", ARM_SYSADDR_FORMAT_SNA);
	PyModule_AddIntConstant(module, "ARM_SYSADDR_FORMAT_X25", ARM_SYSADDR_FORMAT_X25);
	PyModule_AddIntConstant(module, "ARM_SYSADDR_FORMAT_HOSTNAME", ARM_SYSADDR_FORMAT_HOSTNAME);
	PyModule_AddIntConstant(module, "ARM_SYSADDR_FORMAT_UUID", ARM_SYSADDR_FORMAT_UUID);

	/* ------------------ mandatory charsets ------------------------- */
	PyModule_AddIntConstant(module, "ARM_CHARSET_ASCII", ARM_CHARSET_ASCII);
	PyModule_AddIntConstant(module, "ARM_CHARSET_UTF8", ARM_CHARSET_UTF8);
	PyModule_AddIntConstant(module, "ARM_CHARSET_UTF16BE", ARM_CHARSET_UTF16BE);
	PyModule_AddIntConstant(module, "ARM_CHARSET_UTF16LE", ARM_CHARSET_UTF16LE);
	PyModule_AddIntConstant(module, "ARM_CHARSET_UTF16", ARM_CHARSET_UTF16);
	PyModule_AddIntConstant(module, "ARM_CHARSET_IBM037", ARM_CHARSET_IBM037);
	PyModule_AddIntConstant(module, "ARM_CHARSET_IBM1047", ARM_CHARSET_IBM1047);
}

#ifdef IS_PY3K

static struct PyModuleDef moduledef =
{
	PyModuleDef_HEAD_INIT,
	"arm4",
	arm4_module_documentation,
	sizeof(struct module_state),
	arm4_methods,
	NULL,
	NULL,
	NULL,
	NULL
};

#define INITERROR	return NULL

/* This is the initialization function signature */
PyObject *
PyInit_arm4 (void)
#else /* IS_PY3K */

#define INITERROR	return

/* This is the initialization function signature */
PyMODINIT_FUNC
initarm4(void)
#endif
{
	PyObject *m;	/* This is the module object */
	struct module_state *state;

	/* Finalize the type objects including setting type of the new type
	 * object; doing it here is required for portability to Windows 
	 * without requiring C++. */
	ArmID_Type.tp_new = PyType_GenericNew;
	if (PyType_Ready(&ArmID_Type) < 0)
		INITERROR;
	ArmHandle_Type.tp_new = PyType_GenericNew;
	if (PyType_Ready(&ArmHandle_Type) < 0)
		INITERROR;
	ArmCorrelator_Type.tp_new = PyType_GenericNew;
	if (PyType_Ready(&ArmCorrelator_Type) < 0)
		INITERROR;

	/* No allocator for arrival time! */
	if (PyType_Ready(&ArmArrivalTime_Type) < 0)
		INITERROR;

	if (PyType_Ready(&ArmBuffer_Type) < 0)
		INITERROR;
	if (PyType_Ready(&ArmSubbufferCharset_Type) < 0)
		INITERROR;
	if (PyType_Ready(&ArmSubbufferAppIdentity_Type) < 0)
		INITERROR;
	if (PyType_Ready(&ArmSubbufferAppContext_Type) < 0)
		INITERROR;
	if (PyType_Ready(&ArmSubbufferTranIdentity_Type) < 0)
		INITERROR;
	if (PyType_Ready(&ArmSubbufferTranContext_Type) < 0)
		INITERROR;
	if (PyType_Ready(&ArmSubbufferArrivalTime_Type) < 0)
		INITERROR;
	if (PyType_Ready(&ArmSubbufferMetricBindings_Type) < 0)
		INITERROR;
	if (PyType_Ready(&ArmSubbufferMetricValues_Type) < 0)
		INITERROR;
	if (PyType_Ready(&ArmSubbufferUser_Type) < 0)
		INITERROR;
	if (PyType_Ready(&ArmSubbufferSystemAddress_Type) < 0)
		INITERROR;
	if (PyType_Ready(&ArmSubbufferDiagDetail_Type) < 0)
		INITERROR;

#ifdef IS_PY3K
	m = PyModule_Create (&moduledef);
#else
	m = Py_InitModule3("arm4", arm4_methods, arm4_module_documentation);
#endif

	/* Add the types to the module dictionary */
    PyModule_AddObject(m, "ArmID", (PyObject *)&ArmID_Type);
	PyModule_AddObject(m, "ArmHandle", (PyObject *)&ArmHandle_Type);
	PyModule_AddObject(m, "ArmCorrelator", (PyObject *)&ArmCorrelator_Type);
	PyModule_AddObject(m, "ArmArrivalTime", (PyObject *)&ArmArrivalTime_Type);
	PyModule_AddObject(m, "ArmBuffer", (PyObject *)&ArmBuffer_Type);
	PyModule_AddObject(m, "ArmSubbufferCharset", (PyObject *)&ArmSubbufferCharset_Type);
	PyModule_AddObject(m, "ArmSubbufferAppIdentity", (PyObject *)&ArmSubbufferAppIdentity_Type);
	PyModule_AddObject(m, "ArmSubbufferAppContext", (PyObject *)&ArmSubbufferAppContext_Type);
	PyModule_AddObject(m, "ArmSubbufferTranIdentity", (PyObject *)&ArmSubbufferTranIdentity_Type);
	PyModule_AddObject(m, "ArmSubbufferTranContext", (PyObject *)&ArmSubbufferTranContext_Type);
	PyModule_AddObject(m, "ArmSubbufferArrivalTime", (PyObject *)&ArmSubbufferArrivalTime_Type);
	PyModule_AddObject(m, "ArmSubbufferMetricBindings", (PyObject *)&ArmSubbufferMetricBindings_Type);
	PyModule_AddObject(m, "ArmSubbufferMetricValues", (PyObject *)&ArmSubbufferMetricValues_Type);
	PyModule_AddObject(m, "ArmSubbufferUser", (PyObject *)&ArmSubbufferUser_Type);
	PyModule_AddObject(m, "ArmSubbufferSystemAddress", (PyObject *)&ArmSubbufferSystemAddress_Type);
	PyModule_AddObject(m, "ArmSubbufferDiagDetail", (PyObject *)&ArmSubbufferDiagDetail_Type);

	/* Add our constants */
	init_constants (m);

	/* Create the error object */
	state = GETSTATE(m);
	state->errorStatus = PyErr_NewException("arm4.error", NULL, NULL);
    Py_INCREF(state->errorStatus);
    PyModule_AddObject(m, "error", state->errorStatus);
	state->enableExceptions = 0;

#ifdef IS_PY3K
	return m;
#endif
}
