#include "Python.h"

#include <stdio.h>
#include <stdint.h>
#include <math.h>

typedef union {
  double d;
  struct {
    unsigned long mantissa:52;
    unsigned exp:11;
    unsigned sign:1;
  } i;
} fpval;

static char *_binstring(uint64_t n, int digits, char *str)
{
  int i, bit, top=-1;

  for (i=0; i<64; i++) {
    bit = (n>>i) & 1;
    if (bit) top=i;
    str[63-i] = (bit ? '1' : '0');
  }
  str[64] = 0;

  if (top<digits)
    top = digits-1;
  return str + (63-top);
}

static const char binint__doc__[] =
  "binint(n, [digits=1]) -> string\n"
  "binary representation of an unsigned 64-bit integer, with leading zeros padding out to width";

static PyObject* binint(PyObject *self, PyObject *args)
{
  uint64_t val;
  int digits=1;
  char str[65];

  if (!PyArg_ParseTuple(args, "k|i", &val, &digits))
    return NULL;

  return PyString_FromString(_binstring(val, digits, str));
}

static const char binfloat__doc__[] =
  "binfloat(x) -> string\n"
  "pretty-print a floating-point value's binary rep";

static PyObject* binfloat(PyObject *self, PyObject *args)
{
  fpval x;
  int s, e;
  long m;

  char out[128];

  if (!PyArg_ParseTuple(args, "d", &x.d))
    return NULL;
  s = x.i.sign ? '-' : '+';
  e = x.i.exp;
  m = x.i.mantissa;

  if (e==(1<<11)-1) { /* inf or nan */
    snprintf(out, 128, "%c%s", s, m==0?"inf":"nan");
  } else if (e==0 && m==0) { /* zero */
    snprintf(out, 128, "%c%d", s, 0);
  } else {
    char buf[65];
    int biased;
    if (e==0) biased=-1022;
    else if (e<0) biased=-(e-1023);
    else biased=e-1023;
    snprintf(out, 128, "%c%c.%sb %s %d%s", s, e!=0?'1':'0', _binstring(m, 52, buf), e>=0?"<<":">>", biased, e==0?" (denormal)":"");
  }	
  return PyString_FromString(out);
}

static const char split__doc__[] =
  "split(float) -> (signbit, biasedexp, mantissa)\n"
  "split a floating-point value into IEEE 754 64-bit sign, biased exponent, and mantissa";

static PyObject* split(PyObject *self, PyObject *args)
{
  fpval x;

  if (!PyArg_ParseTuple(args, "d", &x.d))
    return NULL;

  return Py_BuildValue("ikk", x.i.sign, x.i.exp, x.i.mantissa);
}

static const char join__doc__[] =
  "join(signbit, biasedexp, mantissa) -> float\n"
  "join sign, biased exponent, and mantissa into an IEEE 754 64-bit floating point value";

static PyObject* join(PyObject *self, PyObject *args)
{
  int s, e;
  unsigned long m;
  fpval x;

  if (!PyArg_ParseTuple(args, "iik", &s, &e, &m))
    return NULL;
  x.i.sign = s;
  x.i.exp = e;
  x.i.mantissa = m;

  return PyFloat_FromDouble(x.d);
}

static const char ftoi__doc__[] =
  "return an IEEE 754 64-bit floating-point value's binary representation as a 64-bit integer";

static PyObject* ftoi(PyObject *self, PyObject *args)
{
  double x;
  uint64_t xrep;

  if (!PyArg_ParseTuple(args, "d", &x))
    return NULL;

  xrep = *((uint64_t *)&x);
  return Py_BuildValue("k", xrep);
}

static const char itof__doc__[] =
  "return a 64-bit integer's binary representation as an IEEE 754 64-bit floating-point value";

static PyObject* itof(PyObject *self, PyObject *args)
{
  double x;
  uint64_t xrep;

  if (!PyArg_ParseTuple(args, "k", &xrep))
    return NULL;

  x = *((double *)&xrep);
  return PyFloat_FromDouble(x);
}


static const char frexp__doc__[] =
  "frexp(x) -> (exponent, mantissa)\n"
  "split floating-point value into integer exponent and floating-point mantissa";

static PyObject* frexp_(PyObject *self, PyObject *args)
{
  double x;
  int expo;

  if (!PyArg_ParseTuple(args, "d", &x))
    return NULL;

  x = frexp(x, &expo);
  return Py_BuildValue("id", expo, x);
}

/* List of methods defined in the module */

static struct PyMethodDef methods[] = {
  {"split", split, METH_VARARGS, split__doc__},
  {"join", join, METH_VARARGS, join__doc__},
  {"binint", binint, METH_VARARGS, binint__doc__},
  {"binfloat", binfloat, METH_VARARGS, binfloat__doc__},
  {"ftoi", ftoi, METH_VARARGS, ftoi__doc__},
  {"itof", itof, METH_VARARGS, itof__doc__},
  {"frexp", frexp_, METH_VARARGS, frexp__doc__},
  {NULL, NULL}
};

/* Initialization function for the module */

static char module_documentation[] = 
  "This module manipulates the binary representation of IEEE 754 64-bit\n"
  "floating-point values.  For details of the 64-bit format, see:\n"
  "  http://en.wikipedia.org/wiki/IEEE_754#Double-precision_64_bit";

void initieee754bin(void)
{
	PyObject *m;

	/* Create the module and add the functions */
	m = Py_InitModule4("ieee754bin", methods, module_documentation,
		(PyObject*)NULL, PYTHON_API_VERSION);

	/* Check for errors */
	if (PyErr_Occurred())
		Py_FatalError("can't initialize module");
}
