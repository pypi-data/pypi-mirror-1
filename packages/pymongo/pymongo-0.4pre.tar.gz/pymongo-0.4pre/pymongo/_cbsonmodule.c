/*
 * Copyright 2009 10gen, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/*
 * This file contains C implementations of some of the functions needed by the
 * bson module. If possible, these implementations should be used to speed up
 * BSON encoding and decoding.
 */

#include <Python.h>
#include <datetime.h>
#include <time.h>

static PyObject* CBSONError;
static PyObject* _cbson_dict_to_bson(PyObject* self, PyObject* dict);
static PyObject* _wrap_py_string_as_object(PyObject* string);
static PyObject* SON;
static PyObject* Binary;
static PyObject* Code;
static PyObject* ObjectId;
static PyObject* DBRef;

static char* shuffle_oid(const char* oid) {
    char* shuffled = (char*) malloc(12);

    if (!shuffled) {
        PyErr_NoMemory();
        return NULL;
    }

    int i;
    for (i = 0; i < 8; i++) {
        shuffled[i] = oid[7 - i];
    }
    for (i = 0; i < 4; i++) {
        shuffled[i + 8] = oid[11 - i];
    }

    return shuffled;
}

static PyObject* _cbson_shuffle_oid(PyObject* self, PyObject* args) {
    char* data;
    int length;
    if (!PyArg_ParseTuple(args, "s#", &data, &length)) {
        return NULL;
    }

    if (length != 12) {
        PyErr_SetString(PyExc_ValueError, "oid must be of length 12");
        return NULL;
    }

    char* shuffled = shuffle_oid(data);
    if (!shuffled) {
        return NULL;
    }

    PyObject* result = Py_BuildValue("s#", shuffled, 12);
    free(shuffled);
    return result;
}

static PyObject* build_element(const char type, const char* name, const int length, const char* data) {
    int name_length = strlen(name) + 1;
    int built_length = 1 + name_length + length;
    char* built = (char*)malloc(built_length);
    if (!built) {
        PyErr_NoMemory();
        return NULL;
    }

    built[0] = type;
    memcpy(built + 1, name, name_length);
    memcpy(built + 1 + name_length, data, length);

    PyObject* result = Py_BuildValue("s#", built, built_length);
    free(built);
    return result;
}

static PyObject* build_string(int type, const char* string, const char* name) {
    int string_length = strlen(string) + 1;
    int data_length = 4 + string_length;

    char* data = (char*)malloc(data_length);
    if (!data) {
        PyErr_NoMemory();
        return NULL;
    }
    memcpy(data, &string_length, 4);
    memcpy(data + 4, string, string_length);

    PyObject* result = build_element(type, name, data_length, data);
    free(data);
    return result;
}

/* TODO our platform better be little-endian w/ 4-byte ints! */
static PyObject* _cbson_element_to_bson(PyObject* self, PyObject* args) {
    const char* name;
    PyObject* value;
    if (!PyArg_ParseTuple(args, "etO", "utf-8", &name, &value)) {
        return NULL;
    }

    /* TODO this isn't quite the same as the Python version:
     * here we check for type equivalence, not isinstance in some
     * places. */
    if (PyString_CheckExact(value)) {
        const char* encoded_bytes = PyString_AsString(value);
        if (!encoded_bytes) {
            return NULL;
        }
        return build_string(0x02, encoded_bytes, name);
    } else if (PyUnicode_CheckExact(value)) {
        PyObject* encoded = PyUnicode_AsUTF8String(value);
        if (!encoded) {
            return NULL;
        }
        const char* encoded_bytes = PyString_AsString(encoded);
        if (!encoded_bytes) {
            return NULL;
        }
        return build_string(0x02, encoded_bytes, name);
    } else if (PyInt_CheckExact(value)) {
        int int_value = (int)PyInt_AsLong(value);
        return build_element(0x10, name, 4, (char*)&int_value);
    } else if (PyBool_Check(value)) {
        long bool = PyInt_AsLong(value);
        char c = bool ? 0x01 : 0x00;
        return build_element(0x08, name, 1, &c);
    } else if (PyFloat_CheckExact(value)) {
        double d = PyFloat_AsDouble(value);
        return build_element(0x01, name, 8, (char*)&d);
    } else if (value == Py_None) {
        return build_element(0x0A, name, 0, 0);
    } else if (PyDict_Check(value)) {
        PyObject* object = _cbson_dict_to_bson(self, value);
        if (!object) {
            return NULL;
        }
        return build_element(0x03, name, PyString_Size(object), PyString_AsString(object));
    } else if (PyList_CheckExact(value)) {
        PyObject* string = PyString_FromString("");
        int items = PyList_Size(value);
        int i;
        for(i = 0; i < items; i++) {
            char* name;
            asprintf(&name, "%d", i);
            if (!name) {
                PyErr_NoMemory();
                return NULL;
            }
            PyObject* element = _cbson_element_to_bson(self,
                                                       Py_BuildValue("sO", name,
                                                                     PyList_GetItem(value, i)));
            free(name);
            if (!element) {
                return NULL;
            }
            PyString_ConcatAndDel(&string, element);
        }
        PyObject* object = _wrap_py_string_as_object(string);
        return build_element(0x04, name, PyString_Size(object), PyString_AsString(object));
    } else if (PyObject_IsInstance(value, Binary)) {
        PyObject* subtype_object = PyObject_CallMethod(value, "subtype", NULL);
        if (!subtype_object) {
            return NULL;
        }
        long subtype = PyInt_AsLong(subtype_object);
        PyObject* string;
        int length = PyString_Size(value);
        if (subtype == 2) {
            string = PyString_FromStringAndSize((char*)&length, 4);
            PyString_Concat(&string, value);
            length += 4;
        } else {
            string = value;
        }
        char* data = malloc(5 + length);
        if (!data) {
            PyErr_NoMemory();
            return NULL;
        }
        const char* string_data = PyString_AsString(string);
        if (!string_data) {
            return NULL;
        }
        memcpy(data, &length, 4);
        data[4] = (char)subtype;
        memcpy(data + 5, string_data, length);
        PyObject* result = build_element(0x05, name, length + 5, data);
        free(data);
        return result;
    } else if (PyObject_IsInstance(value, Code)) {
        const char* encoded_bytes = PyString_AsString(value);
        if (!encoded_bytes) {
            return NULL;
        }
        return build_string(0x0D, encoded_bytes, name);
    } else if (PyDateTime_CheckExact(value)) {
        time_t rawtime;
        time(&rawtime);
        struct tm* timeinfo = localtime(&rawtime);
        timeinfo->tm_year = PyDateTime_GET_YEAR(value) - 1900;
        timeinfo->tm_mon = PyDateTime_GET_MONTH(value) - 1;
        timeinfo->tm_mday = PyDateTime_GET_DAY(value);
        timeinfo->tm_hour = PyDateTime_DATE_GET_HOUR(value);
        timeinfo->tm_min = PyDateTime_DATE_GET_MINUTE(value);
        timeinfo->tm_sec = PyDateTime_DATE_GET_SECOND(value);
        long long time_since_epoch = timegm(timeinfo);
        time_since_epoch = time_since_epoch * 1000;
        time_since_epoch += PyDateTime_DATE_GET_MICROSECOND(value) / 1000;
        return build_element(0x09, name, 8, (char*)&time_since_epoch);
    } else if (PyObject_IsInstance(value, ObjectId)) {
        const char* pre_shuffle = PyString_AsString(PyObject_Str(value));
        if (!pre_shuffle) {
            return NULL;
        }
        char* shuffled = shuffle_oid(pre_shuffle);
        PyObject* result = build_element(0x07, name, 12, shuffled);
        free(shuffled);
        return result;
    } else if (PyObject_IsInstance(value, DBRef)) {
        PyObject* collection_object = PyObject_CallMethod(value, "collection", NULL);
        if (!collection_object) {
            return NULL;
        }
        PyObject* encoded_collection = PyUnicode_AsUTF8String(collection_object);
        if (!encoded_collection) {
            return NULL;
        }
        const char* collection = PyString_AsString(encoded_collection);
        if (!collection) {
            return NULL;
        }
        PyObject* id_object = PyObject_CallMethod(value, "id", NULL);
        if (!id_object) {
            return NULL;
        }
        const char* id = PyString_AsString(PyObject_Str(id_object));
        if (!id) {
            return NULL;
        }
        char* shuffled = shuffle_oid(id);

        int collection_length = strlen(collection) + 1;
        char* data = (char*)malloc(4 + collection_length + 12);
        if (!data) {
            free(shuffled);
            PyErr_NoMemory();
            return NULL;
        }
        memcpy(data, &collection_length, 4);
        memcpy(data + 4, collection, collection_length);
        memcpy(data + 4 + collection_length, shuffled, 12);
        free(shuffled);

        PyObject* result = build_element(0x0C, name, 16 + collection_length, data);
        free(data);
        return result;
    } else if (PyObject_HasAttrString(value, "pattern") &&
               PyObject_HasAttrString(value, "flags")) { // TODO just a proxy for checking if it is a compiled re
        const char* pattern =  PyString_AsString(PyObject_GetAttrString(value, "pattern"));
        long int_flags = PyInt_AsLong(PyObject_GetAttrString(value, "flags"));
        char flags[10];
        flags[0] = 0;
        // TODO don't hardcode these
        if (int_flags & 2) {
            strcat(flags, "i");
        }
        if (int_flags & 4) {
            strcat(flags, "l");
        }
        if (int_flags & 8) {
            strcat(flags, "m");
        }
        if (int_flags & 16) {
            strcat(flags, "s");
        }
        if (int_flags & 32) {
            strcat(flags, "u");
        }
        if (int_flags & 64) {
            strcat(flags, "x");
        }
        int pattern_length = strlen(pattern) + 1;
        int flags_length = strlen(flags) + 1;
        char* data = malloc(pattern_length + flags_length);
        if (!data) {
            PyErr_NoMemory();
            return NULL;
        }
        memcpy(data, pattern, pattern_length);
        memcpy(data + pattern_length, flags, flags_length);
        PyObject* result = build_element(0x0B, name, pattern_length + flags_length, data);
        free(data);
        return result;
    }
    PyErr_SetString(CBSONError, "no c encoder for this type yet");
    return NULL;
}

static PyObject* _wrap_py_string_as_object(PyObject* string) {
    int length = PyString_Size(string) + 5;
    char* data = (char*)malloc(length);
    if (!data) {
        PyErr_NoMemory();
        return NULL;
    }
    const char* elements = PyString_AsString(string);
    memcpy(data, &length, 4);
    memcpy(data + 4, elements, length - 5);
    data[length - 1] = 0x00;

    PyObject* result = Py_BuildValue("s#", data, length);
    free(data);
    return result;
}

static PyObject* _cbson_dict_to_bson(PyObject* self, PyObject* dict) {
    if (PyDict_CheckExact(dict)) {
        PyObject* key;
        PyObject* value;
        Py_ssize_t pos = 0;
        PyObject* string = PyString_FromString("");
        if (!string) {
            return NULL;
        }
        while (PyDict_Next(dict, &pos, &key, &value)) {
            PyObject* element = _cbson_element_to_bson(self,
                                                       Py_BuildValue("OO", key, value));
            if (!element) {
                return NULL;
            }
            PyString_ConcatAndDel(&string, element);
        }
        return _wrap_py_string_as_object(string);
    } else if (PyObject_IsInstance(dict, SON)) {
        PyObject* string = PyString_FromString("");
        if (!string) {
            return NULL;
        }
        PyObject* keys = PyObject_CallMethod(dict, "keys", NULL);
        if (!keys) {
            return NULL;
        }
        int items = PyList_Size(keys);
        int i;
        for(i = 0; i < items; i++) {
            PyObject* name = PyList_GetItem(keys, i);
            if (!name) {
                return NULL;
            }
            PyObject* element = _cbson_element_to_bson(self,
                                                       Py_BuildValue("OO", name,
                                                                     PyDict_GetItem(dict, name)));
            if (!element) {
                return NULL;
            }
            PyString_ConcatAndDel(&string, element);
        }
        return _wrap_py_string_as_object(string);
    }
    PyErr_SetString(PyExc_TypeError, "argument to from_dict must be a mapping type");
    return NULL;
}

static PyMethodDef _CBSONMethods[] = {
    {"_shuffle_oid", _cbson_shuffle_oid, METH_VARARGS,
     "shuffle an ObjectId into proper byte order."},
    {"_element_to_bson", _cbson_element_to_bson, METH_VARARGS,
     "convert a key and value to its bson representation."},
    {"_dict_to_bson", _cbson_dict_to_bson, METH_O,
     "convert a dictionary to a string containing it's BSON representation."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC init_cbson(void) {
    PyDateTime_IMPORT;
    PyObject *m;
    m = Py_InitModule("_cbson", _CBSONMethods);
    if (m == NULL) {
        return;
    }

    CBSONError = PyErr_NewException("_cbson.error", NULL, NULL);
    Py_INCREF(CBSONError);
    PyModule_AddObject(m, "error", CBSONError);

    PyObject* son_module = PyImport_ImportModule("pymongo.son");
    SON = PyObject_GetAttrString(son_module, "SON");

    PyObject* binary_module = PyImport_ImportModule("pymongo.binary");
    Binary = PyObject_GetAttrString(binary_module, "Binary");

    PyObject* code_module = PyImport_ImportModule("pymongo.code");
    Code = PyObject_GetAttrString(code_module, "Code");

    PyObject* objectid_module = PyImport_ImportModule("pymongo.objectid");
    ObjectId = PyObject_GetAttrString(objectid_module, "ObjectId");

    PyObject* dbref_module = PyImport_ImportModule("pymongo.dbref");
    DBRef = PyObject_GetAttrString(dbref_module, "DBRef");
}
