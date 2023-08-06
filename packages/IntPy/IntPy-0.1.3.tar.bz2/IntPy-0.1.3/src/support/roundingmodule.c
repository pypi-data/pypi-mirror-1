/*
 * support/roundingmodule.c
 *
 * Copyright 2008 Rafael Menezes Barreto <rmb3@cin.ufpe.br,
 * rafaelbarreto87@gmail.com>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License version 2
 * as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 */


/*
 * Extension for floating point rounding control
 *
 * With this extension it's possible to control how floating point roundings
 * are done by the system.
 *
 * It was developed in CIn/UFPE (Brazil) by Rafael Menezes Barreto
 * <rmb3@cin.ufpe.br, rafaelbarreto87@gmail.com> as part of the IntPy package
 * and it's free software.
 */


#include <Python.h>
#include <fenv.h>


static PyObject * rounding_get_mode(PyObject * self, PyObject * args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    return Py_BuildValue("i", fegetround());
}

static PyObject * rounding_set_mode(PyObject * self, PyObject * args) {
    int mode;
    if (!PyArg_ParseTuple(args, "i", &mode)) {
        return NULL;
    }
    int return_val = 1;
    if (mode == -1) {
        return_val = fesetround(FE_DOWNWARD);
    } else if (mode == 0) {
        return_val = fesetround(FE_TONEAREST);
    } else if (mode == 1) {
        return_val = fesetround(FE_UPWARD);
    } else {
        return_val = fesetround(mode);
    }
    return Py_BuildValue("i", return_val);
}


static PyMethodDef rounding_functions[] = {
    {"get_mode", rounding_get_mode, METH_VARARGS,
        "Returns the current rounding mode"
    },
    {"set_mode", rounding_set_mode, METH_VARARGS,
        "Sets the rounding mode and returns 0 if it's OK or 1 if an error"
        " ocurred"
    },
    {0}
};


PyMODINIT_FUNC initrounding() {
    char * __doc__ =
        "Module to control the floating point rounding\n\n"

        "With this module it's possible to control how floating point"
        " roundings are done\nby the system.\n\n"

        "It was developed in CIn/UFPE (Brazil) by Rafael Menezes Barreto\n"
        "<rmb3@cin.ufpe.br, rafaelbarreto87@gmail.com> as part of the IntPy"
        " package and\nit's free software.";
    Py_InitModule3("rounding", rounding_functions, __doc__);
}
