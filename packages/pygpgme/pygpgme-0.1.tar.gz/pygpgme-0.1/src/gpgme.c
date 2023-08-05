/* -*- mode: C; c-basic-offset: 4; indent-tabs-mode: nil -*- */
/*
    pygpgme - a Python wrapper for the gpgme library
    Copyright (C) 2006  James Henstridge

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

#include <Python.h>
#include "pygpgme.h"

static PyMethodDef pygpgme_functions[] = {
    { "make_constants", (PyCFunction)pygpgme_make_constants, METH_VARARGS },
    { NULL, NULL, 0 }
};

PyMODINIT_FUNC
init_gpgme(void)
{
    PyObject *mod;

    pygpgme_error = PyErr_NewException("gpgme.GpgmeError",
                                       PyExc_RuntimeError, NULL);

#define INIT_TYPE(type)                      \
    if (!type.ob_type)                       \
        type.ob_type = &PyType_Type;         \
    if (!type.tp_alloc)                      \
        type.tp_alloc = PyType_GenericAlloc; \
    if (!type.tp_new)                        \
        type.tp_new = PyType_GenericNew;     \
    if (PyType_Ready(&type) < 0)             \
        return

#define ADD_TYPE(type)                \
    Py_INCREF(&PyGpgme ## type ## _Type); \
    PyModule_AddObject(mod, #type, (PyObject *)&PyGpgme ## type ## _Type)

    INIT_TYPE(PyGpgmeContext_Type);
    INIT_TYPE(PyGpgmeKey_Type);
    INIT_TYPE(PyGpgmeSubkey_Type);
    INIT_TYPE(PyGpgmeUserId_Type);
    INIT_TYPE(PyGpgmeKeySig_Type);
    INIT_TYPE(PyGpgmeNewSignature_Type);
    INIT_TYPE(PyGpgmeSignature_Type);
    INIT_TYPE(PyGpgmeImportResult_Type);
    INIT_TYPE(PyGpgmeKeyIter_Type);

    mod = Py_InitModule("gpgme._gpgme", pygpgme_functions);

    ADD_TYPE(Context);
    ADD_TYPE(Key);
    ADD_TYPE(Subkey);
    ADD_TYPE(UserId);
    ADD_TYPE(KeySig);
    ADD_TYPE(NewSignature);
    ADD_TYPE(Signature);
    ADD_TYPE(ImportResult);
    ADD_TYPE(KeyIter);

    Py_INCREF(pygpgme_error);
    PyModule_AddObject(mod, "GpgmeError", pygpgme_error);
}
