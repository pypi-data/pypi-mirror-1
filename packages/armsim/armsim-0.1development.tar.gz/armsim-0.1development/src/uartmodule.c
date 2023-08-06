#include <pty.h>
#include <stdlib.h>
#include <stdio.h>
#include <Python.h>

static PyObject *
uart_openpty(PyObject *self, PyObject *args) {
	PyObject *result;
	int m, s;
	if(openpty(&m, &s, NULL, NULL, NULL) == -1) {
		Py_INCREF(Py_None);
		result = Py_None;
	} else {
		printf("%d %d\n", m, s);
		result = Py_BuildValue("(i, i, s, s)",
                         m, s, ptsname(m), ptsname(s));
	}
	return result;
}

static PyMethodDef UartMethods[] = {
	{"openpty", uart_openpty, METH_VARARGS, "Open a real PTY"},
	{NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
inituart(void)
{
	(void)Py_InitModule("uart", UartMethods);
}

