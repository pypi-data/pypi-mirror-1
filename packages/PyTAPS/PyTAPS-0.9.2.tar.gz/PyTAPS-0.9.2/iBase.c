#define _IBASE_MODULE
#include "iBase_Python.h"
#include "common.h"

#include <numpy/arrayobject.h>
#include <numpy/ufuncobject.h>

static PyObject *PyExc_ITAPSError;
static PyTypeObject iBaseEntity_Type;

static PyTypeObject iBase_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iBase.Base",                       /* tp_name */
    sizeof(iBase_Object),                     /* tp_basicsize */
    0,                                        /* tp_itemsize */
    0,                                        /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    0,                                        /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                       /* tp_flags */
    "iBase instance objects"                  /* tp_doc */
};

#define HANDLE_TYPE Entity
#include "iBase_handleTempl.def"
#undef HANDLE_TYPE

#define HANDLE_TYPE EntitySet
#include "iBase_handleTempl.def"
#undef HANDLE_TYPE

#define HANDLE_TYPE Tag
#include "iBase_handleTempl.def"
#undef HANDLE_TYPE

static int NPY_IBASEENT;
static int NPY_IBASEENTSET;
static int NPY_IBASETAG;

ENUM_TYPE(iBaseType,           "iBase.Type",           "");
ENUM_TYPE(iBaseAdjCost,        "iBase.AdjCost",        "");
ENUM_TYPE(iBaseStorageOrder,   "iBase.StorageOrder",   "");
ENUM_TYPE(iBaseCreationStatus, "iBase.CreationStatus", "");

static PyMethodDef module_methods[] = {
    {0}
};

static void
ArrDeallocObj_dealloc(ArrDealloc_Object *self)
{
    free(self->memory);
    Py_XDECREF(self->base);

    self->ob_type->tp_free((PyObject *)self);
}

static PyTypeObject ArrDealloc_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                          /* ob_size */
    "arrdealloc",                               /* tp_name */
    sizeof(ArrDealloc_Object),                  /* tp_basicsize */
    0,                                          /* tp_itemsize */
    (destructor)ArrDeallocObj_dealloc,          /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    0,                                          /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                         /* tp_flags */
    "Internal deallocator object",              /* tp_doc */
};

static ArrDealloc_Object *
ArrDealloc_New(PyObject *base, void *memory)
{
    ArrDealloc_Object *o = PyObject_New(ArrDealloc_Object,&ArrDealloc_Type);
    o->memory = memory;
    o->base = base;
    Py_XINCREF(base);
    return o;
}

PyMODINIT_FUNC initiBase(void)
{
    PyArray_Descr *descr;
    PyObject *m = Py_InitModule("iBase",module_methods);
    import_array();
    import_ufunc();

    PyExc_ITAPSError = PyErr_NewException("iBase.ITAPSError",0,0);
    Py_INCREF(PyExc_ITAPSError);
    PyModule_AddObject(m,"ITAPSError",PyExc_ITAPSError);

    ArrDealloc_Type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&ArrDealloc_Type) < 0)
        return;

    /***** register C API *****/
    static void *IBase_API[] = {
        NULL, /* PyExc_ITAPSError */
        &ArrDealloc_Type,
        &ArrDealloc_New,
        &iBase_Type,
        &iBaseEntity_Type,
        &iBaseEntitySet_Type,
        &iBaseTag_Type,
        &NPY_IBASEENT,
        &NPY_IBASEENTSET,
        &NPY_IBASETAG,
        &iBaseEntityArr_equal,
        &iBaseEntitySetArr_equal,
        &iBaseTagArr_equal,
    };
    IBase_API[0] = PyExc_ITAPSError;
    PyObject *api_obj;

    /* Create a CObject containing the API pointer array's address */
    api_obj = PyCObject_FromVoidPtr(IBase_API,NULL);

    if(api_obj != NULL)
        PyModule_AddObject(m, "_C_API", api_obj);

    /***** acquire "equal" ufunc *****/
    PyObject *ops = PyArray_GetNumericOps();
    PyUFuncObject *ufunc = (PyUFuncObject*)PyDict_GetItemString(ops,"equal");
    Py_DECREF(ops);
    int types[3];

    REGISTER_CLASS(m,"Base",iBase);

    /***** initialize type enum *****/
    REGISTER_CLASS(m,"Type",iBaseType);

    ADD_ENUM(iBaseType,"vertex", iBase_VERTEX);
    ADD_ENUM(iBaseType,"edge",   iBase_EDGE);
    ADD_ENUM(iBaseType,"face",   iBase_FACE);
    ADD_ENUM(iBaseType,"region", iBase_REGION);
    ADD_ENUM(iBaseType,"all",    iBase_ALL_TYPES);

    /***** initialize adjacency cost enum *****/
    REGISTER_CLASS(m,"AdjCost",iBaseAdjCost);

    ADD_ENUM(iBaseAdjCost,"unavailable",     iBase_UNAVAILABLE);
    ADD_ENUM(iBaseAdjCost,"all_order_1",     iBase_ALL_ORDER_1);
    ADD_ENUM(iBaseAdjCost,"all_order_logn",  iBase_ALL_ORDER_LOGN);
    ADD_ENUM(iBaseAdjCost,"all_order_n",     iBase_ALL_ORDER_N);
    ADD_ENUM(iBaseAdjCost,"some_order_1",    iBase_SOME_ORDER_1);
    ADD_ENUM(iBaseAdjCost,"some_order_logn", iBase_SOME_ORDER_LOGN);
    ADD_ENUM(iBaseAdjCost,"some_order_n",    iBase_SOME_ORDER_N);

    /***** initialize storage order enum *****/
    REGISTER_CLASS(m,"StorageOrder",iBaseStorageOrder);

    ADD_ENUM(iBaseStorageOrder,"blocked",     iBase_BLOCKED);
    ADD_ENUM(iBaseStorageOrder,"interleaved", iBase_INTERLEAVED);

    /***** initialize creation status enum *****/
    REGISTER_CLASS(m,"CreationStatus",iBaseCreationStatus);

    ADD_ENUM(iBaseCreationStatus,"new",        iBase_NEW);
    ADD_ENUM(iBaseCreationStatus,"exists",     iBase_ALREADY_EXISTED);
    ADD_ENUM(iBaseCreationStatus,"duplicated", iBase_CREATED_DUPLICATE);
    ADD_ENUM(iBaseCreationStatus,"failed",     iBase_CREATION_FAILED);

    /***** initialize handles *****/
    REGISTER_CLASS(m,"Entity",iBaseEntity);
    REGISTER_CLASS(m,"EntitySet",iBaseEntitySet);
    REGISTER_CLASS(m,"Tag",iBaseTag);

    /***** initialize iBaseEntity array type *****/
    descr = PyArray_DescrNewFromType(NPY_INTP);
    descr->f = &iBaseEntityArr_funcs;

    descr->typeobj = &iBaseEntity_Type;
    descr->kind = 'V';
    descr->type = 'j';
    descr->hasobject = NPY_USE_GETITEM|NPY_USE_SETITEM;
    descr->elsize = sizeof(iBase_EntityHandle);

    NPY_IBASEENT = PyArray_RegisterDataType(descr);
    PyModule_AddObject(m,"npy_ent",(PyObject*)descr);

    types[0] = types[1] = NPY_IBASEENT; types[2] = NPY_BOOL;
    PyUFunc_RegisterLoopForType(ufunc,NPY_IBASEENT,iBaseEntityArr_equal,types,
                                0);

    /***** initialize iBaseEntitySet array type *****/
    descr = PyArray_DescrNewFromType(NPY_INTP);
    descr->f = &iBaseEntitySetArr_funcs;

    descr->typeobj = &iBaseEntitySet_Type;
    descr->kind = 'V';
    descr->type = 'J';
    descr->hasobject = NPY_USE_GETITEM|NPY_USE_SETITEM;
    descr->elsize = sizeof(iBase_EntitySetHandle);

    NPY_IBASEENTSET = PyArray_RegisterDataType(descr);
    PyModule_AddObject(m,"npy_entset",(PyObject*)descr);

    types[0] = types[1] = NPY_IBASEENTSET; types[2] = NPY_BOOL;
    PyUFunc_RegisterLoopForType(ufunc,NPY_IBASEENTSET,iBaseEntitySetArr_equal,
                                types,0);

    /***** initialize iBaseTag array type *****/
    descr = PyArray_DescrNewFromType(NPY_INTP);
    descr->f = &iBaseTagArr_funcs;

    descr->typeobj = &iBaseTag_Type;
    descr->kind = 'V';
    descr->type = 'T';
    descr->hasobject = NPY_USE_GETITEM|NPY_USE_SETITEM;
    descr->elsize = sizeof(iBase_TagHandle);

    NPY_IBASETAG = PyArray_RegisterDataType(descr);
    PyModule_AddObject(m,"npy_tag",(PyObject*)descr);

    types[0] = types[1] = NPY_IBASETAG; types[2] = NPY_BOOL;
    PyUFunc_RegisterLoopForType(ufunc,NPY_IBASETAG,iBaseTagArr_equal,types,0);
}
