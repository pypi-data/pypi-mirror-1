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

#include "handmcmodule.h"

/* {{{ handmc.client implementation */
/* {{{ Type methods */
static HandMC_Client *HandMC_ClientType_new(PyTypeObject *type,
        PyObject *args, PyObject *kwds) {
    HandMC_Client *self;

    self = (HandMC_Client *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->mc = memcached_create(NULL);
    }

    return self;
}

static void HandMC_ClientType_dealloc(HandMC_Client *self) {
    memcached_free(self->mc);
}
/* }}} */

static int HandMC_Client_init(HandMC_Client *self, PyObject *args,
        PyObject *kwds) {
    PyObject *srv_list, *srv_list_it;

    if (!PyArg_ParseTuple(args, "O", &srv_list)) {
        return -1;
    }

    if ((srv_list_it = PyObject_GetIter(srv_list)) != NULL) {
        PyObject *c_srv;

        while ((c_srv = PyIter_Next(srv_list_it)) != NULL
                && !PyErr_Occurred()) {
            unsigned char stype;
            char *hostname;
            unsigned short int port;

            port = 0;
            if (PyString_Check(c_srv)) {
                memcached_server_st *list;

                list = memcached_servers_parse(PyString_AS_STRING(c_srv));
                if (list != NULL) {
                    memcached_return rc;

                    rc = memcached_server_push(self->mc, list);
                    if (rc != MEMCACHED_SUCCESS) {
                        HandMC_ErrFromMemcached(self,
                                "memcached_server_push", rc);
                    }
                    free(list);
                } else {
                    PyErr_SetString(HandMCExc_MemcachedError,
                            "memcached_servers_parse returned NULL");
                }
            } else if (PyArg_ParseTuple(c_srv, "Bs|H",
                        &stype, &hostname, &port)) {
                switch (stype) {
                    case HANDMC_SERVER_TCP:
                        memcached_server_add(self->mc, hostname, port);
                        break;
                    case HANDMC_SERVER_UDP:
                        memcached_server_add_udp(self->mc, hostname, port);
                        break;
                    case HANDMC_SERVER_UNIX:
                        if (port) {
                            PyErr_SetString(PyExc_ValueError,
                                    "can't set port on unix sockets");
                        } else {
                            memcached_server_add_unix_socket(
                                    self->mc, hostname);
                        }
                        break;
                    default:
                        PyErr_Format(PyExc_ValueError,
                                "bad server type: %u", stype);
                }
            }
            Py_DECREF(c_srv);
        }
        Py_DECREF(srv_list_it);
    }

    return PyErr_Occurred() ? -1 : 0;
}

static PyObject *_HandMC_parse_memcached_value(char *value, size_t size,
        uint32_t flags) {
    PyObject *retval;

    retval = NULL;
    switch (flags) {
        case HANDMC_FLAG_PICKLE:
            retval = _HandMC_Unpickle(value, size);
            break;
        case HANDMC_FLAG_INTEGER:
        case HANDMC_FLAG_LONG:
            retval = PyInt_FromString(value, NULL, 10);
            break;
        case HANDMC_FLAG_NONE:
            retval = PyString_FromStringAndSize(value, (Py_ssize_t)size);
            break;
        default:
            PyErr_Format(HandMCExc_MemcachedError,
                    "unknown memcached key flags %u", flags);
    }

    return retval;
}

static PyObject *HandMC_Client_get(HandMC_Client *self, PyObject *arg) {
    char *mc_val;
    size_t val_size;
    uint32_t flags;
    memcached_return error;

    if (!_HandMC_CheckKey(arg)) {
        return NULL;
    } else if (!PySequence_Length(arg) ) {
        /* Others do this, so... */
        Py_RETURN_NONE;
    }

    mc_val = memcached_get(self->mc,
            PyString_AS_STRING(arg), PyString_GET_SIZE(arg),
            &val_size, &flags, &error);
    if (mc_val != NULL) {
        PyObject *r = _HandMC_parse_memcached_value(mc_val, val_size, flags);
        free(mc_val);
        return r;
    }

    if (error == MEMCACHED_NOTFOUND) {
        /* Since python-memcache returns None when the key doesn't exist,
         * so shall we. */
        Py_RETURN_NONE;
    }

    return HandMC_ErrFromMemcached(self, "memcached_get", error);
}

/* {{{ Set commands (set, replace, add, prepend, append) */
static PyObject *_HandMC_RunSetCommand(HandMC_Client *self, _HandMC_SetCommand f,
        char *fname, PyObject *args, PyObject *kwds) {
    char *key;
    size_t key_len;
    PyObject *val, *retval;
    time_t time;
    static char *kws[] = { "key", "val", "time", NULL };

    retval = NULL;
    time = 0;
    if (PyArg_ParseTupleAndKeywords(args, kwds, "s#O|I", kws,
                &key, &key_len, &val, &time)) {
        PyObject *store_val = NULL;
        uint32_t store_flags = 0;

        Py_INCREF(val);
        if (!_HandMC_CheckKey(PyString_FromString(key))) {
            /* Hum di dum. */
        } else if (PyString_Check(val)) {
            store_val = val;
        } else if (PyInt_Check(val)) {
            store_flags |= HANDMC_FLAG_INTEGER;
            store_val = PyObject_Str(val);
        } else if (PyLong_Check(val)) {
            store_flags |= HANDMC_FLAG_LONG;
            store_val = PyObject_Str(val);
        } else {
            store_flags |= HANDMC_FLAG_PICKLE;
            store_val = _HandMC_Pickle(val);
        }

        Py_INCREF(store_val);
        if (store_val != NULL) {
            memcached_return rc;
            const char *raw_val;
            size_t raw_val_len;
            
            raw_val = PyString_AS_STRING(store_val);
            raw_val_len = PyString_GET_SIZE(store_val);
            rc = f(self->mc, key, key_len, raw_val, raw_val_len, time,
                    store_flags);
            switch (rc) {
                case MEMCACHED_SUCCESS:
                    retval = Py_True;
                    break;
                case MEMCACHED_FAILURE:
                case MEMCACHED_NO_KEY_PROVIDED:
                case MEMCACHED_MEMORY_ALLOCATION_FAILURE:
                case MEMCACHED_NOTSTORED:
                    retval = Py_False;
                    break;
                default:
                    HandMC_ErrFromMemcached(self, fname, rc);
            }
        }
        Py_DECREF(store_val);
        Py_DECREF(val);
    }

    Py_XINCREF(retval);
    return retval;
}

/* These all just call _HandMC_RunSetCommand with the appropriate arguments. 
 * In other words: bulk. */
static PyObject *HandMC_Client_set(HandMC_Client *self, PyObject *args,
        PyObject *kwds) {
    return _HandMC_RunSetCommand(
            self, memcached_set, "memcached_set", args, kwds);
}

static PyObject *HandMC_Client_replace(HandMC_Client *self, PyObject *args,
        PyObject *kwds) {
    return _HandMC_RunSetCommand(
            self, memcached_replace, "memcached_replace", args, kwds);
}

static PyObject *HandMC_Client_add(HandMC_Client *self, PyObject *args,
        PyObject *kwds) {
    return _HandMC_RunSetCommand(
            self, memcached_add, "memcached_add", args, kwds);
}

static PyObject *HandMC_Client_prepend(HandMC_Client *self, PyObject *args,
        PyObject *kwds) {
    return _HandMC_RunSetCommand(
            self, memcached_prepend, "memcached_prepend", args, kwds);
}

static PyObject *HandMC_Client_append(HandMC_Client *self, PyObject *args,
        PyObject *kwds) {
    return _HandMC_RunSetCommand(
            self, memcached_append, "memcached_append", args, kwds);
}
/* }}} */

static PyObject *HandMC_Client_delete(HandMC_Client *self, PyObject *args) {
    PyObject *retval;
    char *key;
    size_t key_len;
    time_t time;
    memcached_return rc;

    retval = NULL;
    time = 0;
    if (PyArg_ParseTuple(args, "s#|I", &key, &key_len, &time)
            && _HandMC_CheckKey(PyString_FromStringAndSize(key, key_len))) {
        switch (rc = memcached_delete(self->mc, key, key_len, time)) {
            case MEMCACHED_SUCCESS:
                retval = Py_True;
                break;
            case MEMCACHED_FAILURE:
            case MEMCACHED_NOTFOUND:
            case MEMCACHED_NO_KEY_PROVIDED:
                retval = Py_False;
                break;
            default:
                retval = HandMC_ErrFromMemcached(self, "memcached_delete", rc);
        }
    }

    Py_XINCREF(retval);
    return retval;
}

/* {{{ Increment & decrement */
static PyObject *_HandMC_IncDec(HandMC_Client *self, uint8_t dir, 
        PyObject *args) {
    PyObject *retval;
    char *key;
    size_t key_len;
    unsigned int delta;
    uint64_t result;

    retval = NULL;
    delta = 1;
    if (PyArg_ParseTuple(args, "s#|I", &key, &key_len, &delta)
            && _HandMC_CheckKey(PyString_FromStringAndSize(key, key_len))) {
        memcached_return (*incdec)(memcached_st *, const char *, size_t,
                unsigned int, uint64_t *);
        incdec = (dir == HANDMC_INC) ? memcached_increment
                                     : memcached_decrement;
        incdec(self->mc, key, key_len, delta, &result);
        retval = PyLong_FromUnsignedLong((unsigned long)result);
    }

    Py_XINCREF(retval);
    return retval;
}

static PyObject *HandMC_Client_incr(HandMC_Client *self, PyObject *args) {
    return _HandMC_IncDec(self, HANDMC_INC, args);
}

static PyObject *HandMC_Client_decr(HandMC_Client *self, PyObject *args) {
    return _HandMC_IncDec(self, HANDMC_DEC, args);
}
/* }}} */

static PyObject *HandMC_Client_get_multi(HandMC_Client *self, PyObject *args,
        PyObject *kwds) {
    PyObject *key_seq, **key_objs, *retval = NULL;
    char **keys, *prefix = NULL;
    size_t *key_lens, nkeys, prefix_len = 0;
    memcached_return rc;

    char curr_key[MEMCACHED_MAX_KEY];
    size_t curr_key_len, curr_val_len;
    uint32_t curr_flags;

    static char *kws[] = { "keys", "key_prefix", NULL };

    if (PyArg_ParseTupleAndKeywords(args, kwds, "O|s#", kws,
                &key_seq, &prefix, &prefix_len)) {
        PyObject *key_it, *ckey;
        int i;

        /* First clear any potential earlier mishap because we rely on it in
         * our iteration over keys. */
        PyErr_Clear();
        /* Populate keys and key_lens. */
        nkeys = PySequence_Length(key_seq);
        keys = malloc(sizeof(char *) * nkeys);
        key_lens = malloc(sizeof(size_t) * nkeys);
        key_objs = malloc(sizeof(PyObject *) * nkeys);
        if (keys == NULL || key_lens == NULL || key_objs == NULL) {
            free(keys);
            free(key_lens);
            free(key_objs);
            return PyErr_NoMemory();
        }
        /* Iterate through all keys and set lengths etc. */
        i = 0;
        key_it = PyObject_GetIter(key_seq);
        while (!PyErr_Occurred()
                && i < nkeys
                && (ckey = PyIter_Next(key_it)) != NULL) {
            PyObject *rkey;

            if (!PyString_Check(ckey)) {
                PyErr_SetString(PyExc_TypeError, "keys must be str");
            } else {
                key_lens[i] = PyString_Size(ckey) + prefix_len;
                if (prefix != NULL) {
                    rkey = PyString_FromFormat("%s%s",
                            prefix, PyString_AS_STRING(ckey));
                    Py_DECREF(ckey);
                } else {
                    rkey = ckey;
                }
                keys[i] = PyString_AS_STRING(rkey);
                key_objs[i++] = rkey;
            }
        }
        Py_DECREF(key_it);

        /* TODO Change this interface or at least provide an alternative that
         * returns some kind of iterable which fetches keys sequentially
         * instead of doing it all at once. The current way is grossly
         * inefficient for larger datasets, as a dict has to be allocated that
         * is large enough to hold all the data at once.
         */
        retval = PyDict_New();

        if ((rc = memcached_mget(self->mc, keys, key_lens, nkeys))
                == MEMCACHED_SUCCESS) {
            char *curr_val;

            while ((curr_val = memcached_fetch(
                            self->mc, curr_key, &curr_key_len, &curr_val_len,
                            &curr_flags, &rc)) != NULL
                    && !PyErr_Occurred()) {
                if (curr_val == NULL && rc == MEMCACHED_END) {
                    break;
                } else if (rc == MEMCACHED_NO_KEY_PROVIDED) {
                    /* Do nothing at all. :-) */
                } else if (rc != MEMCACHED_SUCCESS) {
                    Py_DECREF(retval);
                    retval = HandMC_ErrFromMemcached(
                            self, "memcached_fetch", rc);
                } else {
                    PyObject *val;

                    /* This is safe because libmemcached's max key length
                     * includes space for a NUL-byte. */
                    curr_key[curr_key_len] = 0;
                    val = _HandMC_parse_memcached_value(
                            curr_val, curr_val_len, curr_flags);
                    PyDict_SetItemString(retval, curr_key + prefix_len, val);
                    Py_DECREF(val);
                }
                free(curr_val);
            }
            /* Need to cleanup. */
            if (PyErr_Occurred()) {
                /* Not checking rc because an exception already occured, and
                 * we wouldn't want to mask it. */
                memcached_quit(self->mc);
            }
        } else {
            retval = HandMC_ErrFromMemcached(self, "memcached_mget", rc);
        }

        free(key_lens);
        free(keys);
        for (i = 0; i < nkeys; i++)
            Py_DECREF(key_objs[i]);
        free(key_objs);
    }

    /* Not INCREFing because the only two outcomes are NULL and a new dict.
     * We're the owner of that dict already, so. */
    return retval;
}

/**
 * Run func over every item in value, building arguments of:
 *     *(item + extra_args)
 */
static PyObject *_HandMC_DoMulti(PyObject *values, PyObject *func,
        PyObject *prefix, PyObject *extra_args) {
    PyObject *retval = PyList_New(0);
    PyObject *iter = NULL;
    PyObject *item = NULL;
    int is_dict = PyDict_Check(values);

    if (retval == NULL)
        goto error;

    if ((iter = PyObject_GetIter(values)) == NULL)
        goto error;

    while ((item = PyIter_Next(iter)) != NULL) {
        PyObject *args_f = NULL;
        PyObject *value = NULL;
        PyObject *args = NULL;
        PyObject *key = NULL;
        PyObject *ro = NULL;

        /* Calculate key. */
        if (prefix == NULL || prefix == Py_None) {
            /* We now have two owned references to item. */
            Py_INCREF(item);
            key = item;
        } else {
            key = PySequence_Concat(prefix, item);
        }
        if (key == NULL)
            goto iter_error;

        /* Calculate args. */
        if (is_dict) {
            if ((value = PyDict_GetItem(values, item)) == NULL) {
                goto iter_error;
            }
            args = PyTuple_Pack(2, key, value);
        } else {
            args = PyTuple_Pack(1, key);
        }
        if (args == NULL)
            goto iter_error;

        /* Calculate full argument tuple. */
        if (extra_args == NULL) {
            Py_INCREF(args);
            args_f = args;
        } else {
            if ((args_f = PySequence_Concat(args, extra_args)) == NULL)
                goto iter_error;
        }

        /* Call stuff. */
        ro = PyObject_CallObject(func, args_f);
        /* This is actually safe even if True got deleted because we're
         * only comparing addresses. */
        Py_XDECREF(ro);
        if (ro != Py_True) {
            if (PyList_Append(retval, item) != 0)
                goto iter_error;
        }
        Py_DECREF(args_f);
        Py_DECREF(args);
        Py_XDECREF(key);
        Py_DECREF(item);
        continue;
iter_error:
        Py_XDECREF(args_f);
        Py_XDECREF(args);
        Py_XDECREF(key);
        Py_DECREF(item);
        goto error;
    }
    Py_DECREF(iter);

    return retval;
error:
    Py_XDECREF(retval);
    Py_XDECREF(iter);
    return NULL;
}

static PyObject *HandMC_Client_set_multi(HandMC_Client *self, PyObject *args,
        PyObject *kwds) {
    PyObject *prefix = NULL;
    PyObject *time = NULL;
    PyObject *set = NULL;
    PyObject *map;
    PyObject *call_args;
    PyObject *retval;

    static char *kws[] = { "mapping", "time", "key_prefix", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O!S", kws,
                &map, &PyInt_Type, &time, &prefix))
        return NULL;

    if ((set = PyObject_GetAttrString((PyObject *)self, "set")) == NULL)
        return NULL;

    if (time == NULL) {
        retval = _HandMC_DoMulti(map, set, prefix, NULL);
    } else {
        if ((call_args = PyTuple_Pack(1, time)) == NULL)
            goto error;
        retval = _HandMC_DoMulti(map, set, prefix, call_args);
        Py_DECREF(call_args);
    }
    Py_DECREF(set);

    return retval;
error:
    Py_XDECREF(set);
    return NULL;
}

static PyObject *HandMC_Client_delete_multi(HandMC_Client *self,
        PyObject *args, PyObject *kwds) {
    PyObject *prefix = NULL;
    PyObject *time = NULL;
    PyObject *delete;
    PyObject *keys;
    PyObject *call_args;
    PyObject *retval;

    static char *kws[] = { "keys", "time", "key_prefix", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O!S", kws,
                &keys, &PyInt_Type, &time, &prefix))
        return NULL;

    if ((delete = PyObject_GetAttrString((PyObject *)self, "delete")) == NULL)
        return NULL;

    if (time == NULL) {
        retval = _HandMC_DoMulti(keys, delete, prefix, NULL);
    } else {
        if ((call_args = PyTuple_Pack(1, time)) == NULL)
            goto error;
        retval = _HandMC_DoMulti(keys, delete, prefix, call_args);
        Py_DECREF(call_args);
    }
    Py_DECREF(delete);

    return retval;
error:
    Py_XDECREF(delete);
    return NULL;
}
/* }}} */

/* }}} */

static PyObject *HandMC_ErrFromMemcached(HandMC_Client *self, const char *what,
        memcached_return error) {
    if (error == MEMCACHED_ERRNO) {
        PyErr_Format(HandMCExc_MemcachedError,
                "system error %d from %s: %s", errno, what, strerror(errno));
    } else { 
        PyErr_Format(HandMCExc_MemcachedError, "error %d from %s: %s",
                error, what, memcached_strerror(self->mc, error));
    }
    return NULL;
}

/* {{{ Pickling */
static PyObject *_HandMC_GetPickles(const char *attname) {
    PyObject *pickle, *pickle_attr;
    
    pickle_attr = NULL;
    /* Import cPickle or pickle. */
    pickle = PyImport_ImportModule("cPickle");
    if (pickle == NULL) {
        PyErr_Clear();
        pickle = PyImport_ImportModule("pickle");
    }

    /* Find attribute and return it. */
    if (pickle != NULL) {
        pickle_attr = PyObject_GetAttrString(pickle, attname);
        Py_DECREF(pickle);
    }
    return pickle_attr;
}

static PyObject *_HandMC_Unpickle(const char *buff, size_t size) {
    PyObject *pickle_load;
    PyObject *retval = NULL;
    
    retval = NULL;
    pickle_load = _HandMC_GetPickles("loads");
    if (pickle_load != NULL) {
        retval = PyObject_CallFunction(pickle_load, "s#", buff, size);
        Py_DECREF(pickle_load);
    }

    return retval;
}

static PyObject *_HandMC_Pickle(PyObject *val) {
    PyObject *pickle_dump;
    PyObject *retval = NULL;

    retval = NULL;
    pickle_dump = _HandMC_GetPickles("dumps");
    if (pickle_dump != NULL) {
        retval = PyObject_CallFunctionObjArgs(pickle_dump, val, NULL);
        Py_DECREF(pickle_dump);
    }

    return retval;
}
/* }}} */

static int _HandMC_CheckKey(PyObject *key) {
    if (key == NULL) {
        PyErr_SetString(PyExc_ValueError, "key must be given");
    } else if (!PyString_Check(key)) {
        PyErr_SetString(PyExc_TypeError, "key must be an instance of str");
    } else if (PyString_GET_SIZE(key) > MEMCACHED_MAX_KEY) {
        PyErr_Format(PyExc_ValueError, "key too long, max is %d",
                MEMCACHED_MAX_KEY);
    } /* TODO Check key contents here. */

    return PyErr_Occurred() ? 0 : 1;
}

static PyMethodDef HandMC_functions[] = {
    {NULL}
};

PyMODINIT_FUNC inithandmc(void) {
    PyObject *module;

    if (PyType_Ready(&HandMC_ClientType) < 0) {
        return;
    }

    module = Py_InitModule3("handmc", HandMC_functions,
            "Hand-made wrapper for libmemcached.\n\
\n\
You ought to look at python-memcached's documentation for now, seeing\n\
as this module is more or less a drop-in replacement, the difference\n\
being in how you connect. Therefore that's documented here::\n\
\n\
    c = handmc.client([(handmc.server_type_tcp, 'localhost', 11211)])\n\
\n\
As you see, a list of three-tuples of (type, host, port) is used. If \n\
type is `server_type_unix`, no port should be given. A simpler form \n\
can be used as well::\n\
\n\
   c = handmc.client('localhost')\n\
\n\
See libmemcached's memcached_servers_parse for more info on that. I'm told \n\
you can use UNIX domain sockets by specifying paths, and multiple servers \n\
by using comma-separation. Good luck with that.\n\
\n\
Oh, and: plankton.\n");
    if (module == NULL) {
        return;
    }

    HandMCExc_MemcachedError = PyErr_NewException(
            "handmc.MemcachedError", NULL, NULL);

    Py_INCREF(&HandMC_ClientType);
    PyModule_AddObject(module, "client", (PyObject *)&HandMC_ClientType);
    /* Compatibility alias. */
    PyModule_AddObject(module, "Client", (PyObject *)&HandMC_ClientType);

    PyModule_AddIntConstant(module, "server_type_tcp", HANDMC_SERVER_TCP);
    PyModule_AddIntConstant(module, "server_type_udp", HANDMC_SERVER_UDP);
    PyModule_AddIntConstant(module, "server_type_unix", HANDMC_SERVER_UNIX);

    PyModule_AddStringConstant(module,
            "libmemcached_version", LIBMEMCACHED_VERSION_STRING);
}
