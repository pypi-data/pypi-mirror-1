#include "Python.h"
#include "seal2.h"

typedef struct {
        PyObject_HEAD
        seal_ctx context;
} seal2object;

static PyTypeObject SEAL2Type;



PyDoc_STRVAR(s2new_doc,
        "new(key) -> seal2 object\n"
        );

static seal2object* s2new(PyObject *self, PyObject *args) {
    seal2object *ob;
    unsigned char *key;
    int len;

    if (args==NULL) {
        PyErr_Format(PyExc_TypeError, "no key given");
        return NULL;
    }

    if (!PyArg_ParseTuple(args, "s#:new", &key, &len)) {
        PyErr_Format(PyExc_TypeError, "Invalid key given");
        return NULL;
    }

    if (len!=20) {
        PyErr_Format(PyExc_ValueError, "SEAL2 keys have to be 20 bytes");
        return NULL;
    }

    ob = PyObject_New(seal2object, &SEAL2Type);
    if (ob==NULL)
        return NULL;

    seal_key(&ob->context, key);

    return ob;
}


static void s2dealloc(seal2object *ob) {
    PyObject_Del(ob);
}



typedef void transform_func(seal_ctx *, const unsigned char*, int, unsigned char*);

static PyObject *transform(transform_func func, seal2object *ob, PyObject *args) {

    unsigned char *source;
    unsigned char *target;
    PyObject *result;
    int len;

    if (!PyArg_ParseTuple(args, "s#", &source, &len))
        return NULL;

    target=(unsigned char*)malloc(len);
    if (target==NULL)
        return NULL;

    func(&ob->context, source, len, target);

    result=PyString_FromStringAndSize((char*)target, len);
    free(target);

    return result;
}


PyDoc_STRVAR(s2encrypt_doc,
    "encrypt(key) -> string\n"
    "\n"
    "Encrypt a string using the SEAL2 algorithm.");

static PyObject *s2encrypt(seal2object *ob, PyObject *args) {
    return transform(seal_encrypt, ob, args);
}


PyDoc_STRVAR(s2decrypt_doc,
    "decrypt(key) -> string\n"
    "\n"
    "Decrypt a string using the SEAL2 algorithm.");

static PyObject *s2decrypt(seal2object *ob, PyObject *args) {
    return transform(seal_decrypt, ob, args);
}



static PyObject *s2getattr(seal2object *ob, char* name) {
    static PyMethodDef seal2_methods[] = {
        { "encrypt", (PyCFunction)s2encrypt, METH_VARARGS, s2encrypt_doc },
        { "decrypt", (PyCFunction)s2decrypt, METH_VARARGS, s2decrypt_doc },
        { NULL, NULL, 0, NULL },
    };
    if (strcmp(name, "key_size")==0)
        return PyInt_FromLong(20);

    return Py_FindMethod(seal2_methods, (PyObject*)ob, name);
}


static PyTypeObject SEAL2Type = {
    PyObject_HEAD_INIT(NULL)
    0,          // ob_size
    "seal2",    // tp_name
    sizeof(seal2object), // tp_basicsize
    0,                   // tp_itemsize

    (destructor)s2dealloc, // tp_dealloc
    NULL,               // tp_print
    (getattrfunc)s2getattr, // tp_getattr
    NULL,               // tp_setattr
    NULL,               // tp_compare
    NULL,               // tp_repr,
    NULL,               // tp_as_number
    NULL,               // tp_as_sequence
    NULL,               // tp_as_mapping,

    NULL,               // tp_hash,
    NULL,               // tp_call
    NULL,               // tp_str
    NULL,               // tp_getattro
    NULL,               // tp_setattro

    NULL,               // tp_as_buffer
    0,                  // tp_flags
    NULL,               // documentation string

    NULL,               // tp_traverse
    NULL,               // tp_clear
    NULL,               // tp_richcompare
    0,                  // tp_weaklistoffset
    NULL,               // tp_iter
    NULL,               // tp_iternext
    NULL,               // tp_methods
    NULL,               // tp_members
    NULL,               // tp_getset
    NULL,               // tp_base
    NULL,               // tp_dict
    NULL,               // tp_descr_get
    NULL,               // tp_descr_set
    0,                  // tp_dictoffset
    NULL,               // tp_init
    NULL,               // tp_alloc
    NULL,               // tp_new
    NULL,               // tp_free
    NULL,               // tp_is_gc
    NULL,               // tp_bases
    NULL,               // tp_mro
    NULL,               // tp_cache
    NULL,               // tp_subclasses
    NULL,               // tp_weaklist
    NULL,               // tp_del
};


static PyMethodDef seal2_functions[] = {
    { "new", (PyCFunction)s2new, METH_VARARGS, s2new_doc },
    { NULL, NULL, 0, NULL },
};

PyMODINIT_FUNC initseal2(void) {
    PyObject *module;

    SEAL2Type.ob_type=&PyType_Type;
    module=Py_InitModule("seal2", seal2_functions);
    if (module==NULL)
        return;

    PyModule_AddIntConstant(module, "key_size", 20);
}



