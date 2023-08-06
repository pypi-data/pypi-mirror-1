/* Methods used by both the encoder and the decoder. */

#include <Python.h>

#include "amf.h"

// Get typed value from mapper or function. Returns new reference.
static PyObject* get_typed_val(PyObject *mapper, PyObject *callable, PyObject *val)
{
    PyObject *id = PyLong_FromVoidPtr((void*)val);
    if (id == NULL)
        return NULL;

    PyObject *result = PyDict_GetItem(mapper, id);
    if (result == NULL) {
        result = PyObject_CallFunctionObjArgs(callable, val, NULL);
        if (result == NULL) {
            Py_DECREF(id);
            return NULL;
        }

        if (PyDict_SetItem(mapper, id, result) == -1) {
            Py_DECREF(id);
            Py_DECREF(result);
            return NULL;
        }
    } else {
        Py_INCREF(result);
    }

    Py_DECREF(id);
    return result;
}

// Replace values in a list with their correctly typed version
int type_list(PyObject* class_def, PyObject *mapper,
    PyObject* name_list, PyObject* val_list, int type)
{
    PyObject *types;

    switch (type) {
        case 0:
            types = PyObject_GetAttrString(class_def, "encode_types");
            break;
        case 1:
            types = PyObject_GetAttrString(class_def, "decode_types");
            break;
        default:
            return 0;
    }

    if (types == NULL)
        return 0;

    if (types == Py_None)
        // No type mapping has been set.
        return 1;

    Py_ssize_t name_len = PySequence_Size(name_list);
    if (name_len == -1) {
        Py_DECREF(types);
        return 0;
    }

    Py_ssize_t val_len = PySequence_Size(val_list);
    if (val_len == -1) {
        Py_DECREF(types);
        return 0;
    }

    if (val_len != name_len) {
        Py_DECREF(types);
        PyErr_SetString(PyExc_Exception, "Name count does not match value count.");
        return 0;
    }

    int i;
    for (i = 0; i < val_len; i++) {
        PyObject *name = PySequence_GetItem(name_list, i);
        if (name == NULL) {
            Py_DECREF(types);
            return 0;
        }

        PyObject *callable = PyDict_GetItem(types, name);
        Py_DECREF(name);
        if (callable != NULL) {
            Py_INCREF(callable);

            PyObject *item = PySequence_GetItem(val_list, i);
            if (item == NULL) {
                Py_DECREF(types);
                Py_DECREF(callable);
                return 0;
            }

            PyObject *typed_item = get_typed_val(mapper, callable, item);
            Py_DECREF(callable);

            int result = PySequence_SetItem(val_list, i, typed_item);
            Py_DECREF(typed_item);
            if (result == -1) {
                Py_DECREF(types);
                return 0;
            }
        }
    }

    Py_DECREF(types);
    return 1;
}

// Replace values in a dict with their correctly typed version
int type_dict(PyObject* class_def, PyObject *mapper, PyObject* dict, int type)
{
    PyObject *types;

    switch (type) {
        case 0:
            types = PyObject_GetAttrString(class_def, "encode_types");
            break;
        case 1:
            types = PyObject_GetAttrString(class_def, "decode_types");
            break;
        default:
            return 0;
            
    }

    if (types == NULL)
        return 0;

    PyObject *key;
    PyObject *val;
    Py_ssize_t idx = 0;

    while (PyDict_Next(dict, &idx, &key, &val)) {
        PyObject *callable = PyDict_GetItem(types, key);
        if (callable != NULL) {
            Py_INCREF(callable);
            PyObject *typed_item = get_typed_val(mapper, callable, val);
            Py_DECREF(callable);

            if (PyDict_SetItem(dict, key, typed_item) == -1) {
                Py_DECREF(types);
                return 0;
            }
        }
    }

    Py_DECREF(types);
    return 1;
}
