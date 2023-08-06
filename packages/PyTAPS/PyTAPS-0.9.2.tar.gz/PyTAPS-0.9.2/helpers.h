#ifndef PYTAPS_HELPERS_H
#define PYTAPS_HELPERS_H

#include <Python.h>

/* TODO: these are never freed! */
static PyObject *g_offset_list;
static PyObject *g_ind_offset_list;

/* NOTE: steals references to offsets and data */
#define OffsetList_New(offsets,data)                                    \
    PyObject_CallFunction(g_offset_list,"NN",(offsets),(data))

/* NOTE: steals references to offsets and data */
#define IndexedOffsetList_New(ents,indices,offsets,data)                \
    PyObject_CallFunction(g_ind_offset_list,"NNNN",(ents),(indices),    \
                          (offsets),(data))

#if PY_VERSION_HEX >= 0x020600f0

static PyObject *g_namedtuple;

static PyObject *
NamedTuple_New(PyObject *type,const char *fmt,...)
{
    va_list args;
    va_start(args,fmt);
    PyObject *py_args = Py_VaBuildValue(fmt,args);
    va_end(args);

    PyObject *res = PyObject_Call(type,py_args,NULL);
    Py_DECREF(py_args);

    return res;
}
#define NamedTuple_CreateType(name,fields)                              \
    PyObject_CallFunction(g_namedtuple,"ss",(name),(fields))

#else

static PyObject *
NamedTuple_New(PyObject *type,const char *fmt,...)
{
    va_list args;
    va_start(args,fmt);
    PyObject *res = Py_VaBuildValue(fmt,args);
    va_end(args);

    return res;
}
#define NamedTuple_CreateType(name,fields) 0

#endif

static int import_helpers(void)
{
    PyObject *helper_module;

    if( (helper_module = PyImport_ImportModule("itaps.helpers")) == NULL)
        return -1;
    if( (g_offset_list = PyObject_GetAttrString(helper_module,"OffsetList"))
        == NULL)
        return -1;
    if( (g_ind_offset_list = PyObject_GetAttrString(helper_module,
        "IndexedOffsetList")) == NULL)
        return -1;
    Py_DECREF(helper_module);

#if PY_VERSION_HEX >= 0x020600f0
    PyObject *collections_module;

    if( (collections_module = PyImport_ImportModule("collections")) == NULL)
        return -1;
    if( (g_namedtuple = PyObject_GetAttrString(collections_module,
        "namedtuple")) == NULL)
        return -1;
    Py_DECREF(collections_module);
#endif

    return 0;

    /* Suppress warnings if this function isn't used */
    (void)NamedTuple_New;
}

#endif
