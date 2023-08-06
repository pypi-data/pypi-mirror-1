/*
 *Copyright 2009 armsim authors.
 *
 *This file is part of armsim.
 *
 *armsim is free software: you can redistribute it and/or modify
 *it under the terms of the GNU General Public License as published by
 *the Free Software Foundation, either version 3 of the License, or
 *(at your option) any later version.
 *
 *armsim is distributed in the hope that it will be useful,
 *but WITHOUT ANY WARRANTY; without even the implied warranty of
 *MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *GNU General Public License for more details.
 *
 *You should have received a copy of the GNU General Public License
 *along with armsim.  If not, see <http://www.gnu.org/licenses/>.
 */

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

