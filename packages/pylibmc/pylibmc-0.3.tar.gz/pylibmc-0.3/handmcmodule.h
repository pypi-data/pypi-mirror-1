/**
 * handmc: hand-made libmemcached bindings for Python
 *
 * Copyright (c) 2008, Ludvig Ericson
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 *  - Redistributions of source code must retain the above copyright notice,
 *  this list of conditions and the following disclaimer.
 * 
 *  - Redistributions in binary form must reproduce the above copyright notice,
 *  this list of conditions and the following disclaimer in the documentation
 *  and/or other materials provided with the distribution.
 * 
 *  - Neither the name of the author nor the names of the contributors may be
 *  used to endorse or promote products derived from this software without
 *  specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#ifndef __HANDMC_H__
#define __HANDMC_H__

#include <Python.h>
#include <libmemcached/memcached.h>

/* Server types. */
#define HANDMC_SERVER_TCP   (1 << 0)
#define HANDMC_SERVER_UDP   (1 << 1)
#define HANDMC_SERVER_UNIX  (1 << 2)

/* Key flags from python-memcache. */
#define HANDMC_FLAG_NONE    0
#define HANDMC_FLAG_PICKLE  (1 << 0)
#define HANDMC_FLAG_INTEGER (1 << 1)
#define HANDMC_FLAG_LONG    (1 << 2)

#define HANDMC_INC  (1 << 0)
#define HANDMC_DEC  (1 << 1)

typedef memcached_return (*_HandMC_SetCommand)(memcached_st *, const char *,
        size_t, const char *, size_t, time_t, uint32_t);

/* {{{ Exceptions */
static PyObject *HandMCExc_MemcachedError;
/* }}} */

/* {{{ handmc.client */
typedef struct {
    PyObject_HEAD
    memcached_st *mc;
} HandMC_Client;

/* {{{ Prototypes */
static HandMC_Client *HandMC_ClientType_new(PyTypeObject *, PyObject *,
        PyObject *);
static void HandMC_ClientType_dealloc(HandMC_Client *);
static int HandMC_Client_init(HandMC_Client *, PyObject *, PyObject *);
static PyObject *HandMC_Client_get(HandMC_Client *, PyObject *arg);
static PyObject *HandMC_Client_set(HandMC_Client *, PyObject *, PyObject *);
static PyObject *HandMC_Client_replace(HandMC_Client *, PyObject *,
        PyObject *);
static PyObject *HandMC_Client_add(HandMC_Client *, PyObject *, PyObject *);
static PyObject *HandMC_Client_prepend(HandMC_Client *, PyObject *,
        PyObject *);
static PyObject *HandMC_Client_append(HandMC_Client *, PyObject *, PyObject *);
static PyObject *HandMC_Client_delete(HandMC_Client *, PyObject *);
static PyObject *HandMC_Client_incr(HandMC_Client *, PyObject *);
static PyObject *HandMC_Client_decr(HandMC_Client *, PyObject *);
static PyObject *HandMC_Client_get_multi(HandMC_Client *, PyObject *, PyObject *);
static PyObject *HandMC_Client_set_multi(HandMC_Client *, PyObject *, PyObject *);
static PyObject *HandMC_Client_delete_multi(HandMC_Client *, PyObject *,
        PyObject *);
static PyObject *HandMC_ErrFromMemcached(HandMC_Client *, const char *,
        memcached_return);
static PyObject *_HandMC_Unpickle(const char *, size_t);
static PyObject *_HandMC_Pickle(PyObject *);
static int _HandMC_CheckKey(PyObject *);
/* }}} */

/* {{{ Type's method table */
static PyMethodDef HandMC_ClientType_methods[] = {
    {"get", (PyCFunction)HandMC_Client_get, METH_O,
        "Retrieve a key from a memcached."},
    {"set", (PyCFunction)HandMC_Client_set, METH_VARARGS|METH_KEYWORDS,
        "Set a key unconditionally."},
    {"replace", (PyCFunction)HandMC_Client_replace, METH_VARARGS|METH_KEYWORDS,
        "Set a key only if it exists."},
    {"add", (PyCFunction)HandMC_Client_add, METH_VARARGS|METH_KEYWORDS,
        "Set a key only if doesn't exist."},
    {"prepend", (PyCFunction)HandMC_Client_prepend, METH_VARARGS|METH_KEYWORDS,
        "Prepend data to  a key."},
    {"append", (PyCFunction)HandMC_Client_append, METH_VARARGS|METH_KEYWORDS,
        "Append data to a key."},
    {"delete", (PyCFunction)HandMC_Client_delete, METH_VARARGS,
        "Delete a key."},
    {"incr", (PyCFunction)HandMC_Client_incr, METH_VARARGS,
        "Increment a key by a delta."},
    {"decr", (PyCFunction)HandMC_Client_decr, METH_VARARGS,
        "Decrement a key by a delta."},
    {"get_multi", (PyCFunction)HandMC_Client_get_multi,
        METH_VARARGS|METH_KEYWORDS, "Get multiple keys at once."},
    {"set_multi", (PyCFunction)HandMC_Client_set_multi,
        METH_VARARGS|METH_KEYWORDS, "Set multiple keys at once."},
    {"delete_multi", (PyCFunction)HandMC_Client_delete_multi,
        METH_VARARGS|METH_KEYWORDS, "Delete multiple keys at once."},
    {NULL}
};
/* }}} */

/* {{{ Type def */
static PyTypeObject HandMC_ClientType = {
    PyObject_HEAD_INIT(NULL)
    0,
    "client",
    sizeof(HandMC_Client),
    0,
    (destructor)HandMC_ClientType_dealloc,

    0,
    0,
    0,
    0,
    0,

    0,
    0,
    0,

    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    "memcached client type",
    0,
    0,
    0,
    0,
    0,
    0,
    HandMC_ClientType_methods,
    0,                                   
    0,                                   
    0,                                   
    0,                                   
    0,                                   
    0,                                   
    0,                                   
    (initproc)HandMC_Client_init,
    0,                                   
    (newfunc)HandMC_ClientType_new,              
    0,          
    0,          
    0,          
    0,          
    0,          
    0,          
    0,          
};

/* }}} */

#endif /* def __HANDMC_H__ */
