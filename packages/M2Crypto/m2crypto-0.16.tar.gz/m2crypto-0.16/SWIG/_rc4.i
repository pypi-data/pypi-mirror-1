/* -*- Mode: C; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
/* Copyright (c) 1999 Ng Pheng Siong. All rights reserved. */
/* $Id: _rc4.i 370 2006-03-07 20:51:58Z heikki $ */

%{
#include <openssl/rc4.h>
%}

%apply Pointer NONNULL { RC4_KEY * };

%inline %{
RC4_KEY *rc4_new(void) {
    RC4_KEY *key;
    
    if (!(key = (RC4_KEY *)PyMem_Malloc(sizeof(RC4_KEY))))
        PyErr_SetString(PyExc_MemoryError, "rc4_new");
    return key;
}   

void rc4_free(RC4_KEY *key) {
    PyMem_Free((void *)key);
}

PyObject *rc4_set_key(RC4_KEY *key, PyObject *value) {
    const void *vbuf;
    int vlen;

    if (PyObject_AsReadBuffer(value, &vbuf, &vlen) == -1)
        return NULL;

    RC4_set_key(key, vlen, vbuf);
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *rc4_update(RC4_KEY *key, PyObject *in) {
    PyObject *ret;
    const void *buf;
    int len;
    void *out;

    if (PyObject_AsReadBuffer(in, &buf, &len) == -1)
        return NULL;

    if (!(out = PyMem_Malloc(len))) {
        PyErr_SetString(PyExc_MemoryError, "expected a string object");
        return NULL;
    }
    RC4(key, len, buf, out);
    ret = PyString_FromStringAndSize(out, len);
    PyMem_Free(out);
    return ret;
}

int rc4_type_check(RC4_KEY *key) {
    return 1;
}
%}
