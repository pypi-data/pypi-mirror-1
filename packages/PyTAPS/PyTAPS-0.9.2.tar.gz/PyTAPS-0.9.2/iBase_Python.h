#ifndef PYTAPS_IBASE_PYTHON_H
#define PYTAPS_IBASE_PYTHON_H

#include <Python.h>
#include <iBase.h>
#include <numpy/ndarrayobject.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*equal_ufunc)(char **,npy_intp *,npy_intp *,void *);

typedef struct
{
    PyObject_HEAD
    PyObject *base;
    void *memory;
} ArrDealloc_Object;

typedef ArrDealloc_Object* (*arr_func)(PyObject *,void *);

#define ArrDealloc_Check(o)                            \
  PyObject_TypeCheck((PyObject*)(o),&ArrDealloc_Type)

typedef struct
{
    PyObject_HEAD
    iBase_Instance handle;
} iBase_Object;

#define iBase_Check(o)                                 \
    PyObject_TypeCheck((PyObject*)(o),&iBase_Type)

typedef struct
{
    PyObject_HEAD
    iBase_EntityHandle handle;
} iBaseEntity_Object;

#define iBaseEntity_New()                               \
    (iBaseEntity_Object*)PyObject_CallObject(           \
        (PyObject*)&iBaseEntity_Type,NULL)

#define iBaseEntity_Check(o)                            \
    PyObject_TypeCheck((PyObject*)(o),&iBaseEntity_Type)

#define iBaseEntity_GetHandle(o)                        \
    ((iBaseEntity_Object*)(o))->handle

typedef struct
{
    PyObject_HEAD
    iBase_EntitySetHandle handle;
} iBaseEntitySet_Object;

#define iBaseEntitySet_New()                            \
    (iBaseEntitySet_Object*)PyObject_CallObject(        \
        (PyObject*)&iBaseEntitySet_Type,NULL)

#define iBaseEntitySet_Check(o)                         \
  PyObject_TypeCheck((PyObject*)(o),&iBaseEntitySet_Type)

#define iBaseEntitySet_GetHandle(o)                     \
  ((iBaseEntitySet_Object*)(o))->handle

typedef struct
{
  PyObject_HEAD
  iBase_TagHandle handle;
} iBaseTag_Object;

#define iBaseTag_New()                                  \
    (iBaseTag_Object*)PyObject_CallObject(              \
        (PyObject*)&iBaseTag_Type,NULL)

#define iBaseTag_Check(o)                               \
    PyObject_TypeCheck((PyObject*)(o),&iBaseTag_Type)

#define iBaseTag_GetHandle(o)                           \
    ((iBaseTag_Object*)(o))->handle




#ifndef _IBASE_MODULE

#if defined(PY_IBASE_UNIQUE_SYMBOL)
#define IBase_API PY_IBASE_UNIQUE_SYMBOL
#endif

#if defined(NO_IMPORT) || defined(NO_IMPORT_IBASE)
extern void **IBase_API;
#elif defined(PY_IBASE_UNIQUE_SYMBOL)
void **IBase_API;
#else
static void **IBase_API = NULL;
#endif

#define PyExc_ITAPSError        ( (PyObject*)    IBase_API[ 0])
#define ArrDealloc_Type         (*(PyTypeObject*)IBase_API[ 1])
#define ArrDealloc_New          ( (arr_func)     IBase_API[ 2])
#define iBase_Type              (*(PyTypeObject*)IBase_API[ 3])
#define iBaseEntity_Type        (*(PyTypeObject*)IBase_API[ 4])
#define iBaseEntitySet_Type     (*(PyTypeObject*)IBase_API[ 5])
#define iBaseTag_Type           (*(PyTypeObject*)IBase_API[ 6])
#define NPY_IBASEENT            (*(int*)         IBase_API[ 7])
#define NPY_IBASEENTSET         (*(int*)         IBase_API[ 8])
#define NPY_IBASETAG            (*(int*)         IBase_API[ 9])
#define iBaseEntityArr_equal    ( (equal_ufunc)  IBase_API[10])
#define iBaseEntitySetArr_equal ( (equal_ufunc)  IBase_API[11])
#define iBaseTagArr_equal       ( (equal_ufunc)  IBase_API[12])


#if !defined(NO_IMPORT_IBASE) && !defined(NO_IMPORT)
static int import_iBase(void)
{
    PyObject *module = PyImport_ImportModule("itaps.iBase");
    PyObject *c_api = NULL;

    if(module == NULL)
        return -1;

    c_api = PyObject_GetAttrString(module,"_C_API");
    if(c_api == NULL)
    {
        Py_DECREF(module);
        return -1;
    }

    if(PyCObject_Check(c_api))
        IBase_API = (void **)PyCObject_AsVoidPtr(c_api);

    Py_DECREF(c_api);
    Py_DECREF(module);

    if(IBase_API == NULL)
        return -1;
    return 0;
}
#endif

#endif

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif
