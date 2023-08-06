#ifndef PYTAPS_IGEOM_PYTHON_H
#define PYTAPS_IGEOM_PYTHON_H

#include <Python.h>
#include <iGeom.h>
#include "iBase_Python.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct
{
    PyObject_HEAD
    iGeom_Instance handle;
} iGeom_Object;

#define iGeom_Check(o)                                 \
    PyObject_TypeCheck((PyObject*)(o),&iGeom_Type)

typedef struct
{
    PyObject_HEAD
    iGeom_Object *instance;
    int is_arr;
    union
    {
        iGeom_EntityIterator    one;
        iGeom_EntityArrIterator arr;
    } iter;
} iGeomIter_Object;

typedef struct
{
    iBaseEntitySet_Object base;
    iGeom_Object *instance;
} iGeomEntitySet_Object;

#define iGeomEntitySet_NewRaw()                         \
    PyObject_New(iGeomEntitySet_Object,&iGeomEntitySet_Type)

#define iGeomEntitySet_Check(o)                         \
    PyObject_TypeCheck((PyObject*)(o),&iGeomEntitySet_Type)

#define iGeomEntitySet_GetInstance(o)                   \
    ( ((iGeomEntitySet_Object*)(o))->instance )

typedef struct
{
    iBaseTag_Object base;
    iGeom_Object *instance;
} iGeomTag_Object;

#define iGeomTag_NewRaw()                               \
        PyObject_New(iGeomTag_Object,&iGeomTag_Type)

#define iGeomTag_Check(o)                               \
    PyObject_TypeCheck((PyObject*)(o),&iGeomTag_Type)

#define iGeomTag_GetInstance(o)                         \
    ( ((iGeomTag_Object*)(o))->instance )

enum iGeomExt_Basis
{
    iGeomExt_XYZ,
    iGeomExt_U,
    iGeomExt_UV
};


#ifndef _IGEOM_MODULE

#if defined(PY_IGEOM_UNIQUE_SYMBOL)
#define IGeom_API PY_IGEOM_UNIQUE_SYMBOL
#endif

#if defined(NO_IMPORT) || defined(NO_IMPORT_IGEOM)
extern void **IGeom_API;
#elif defined(PY_IGEOM_UNIQUE_SYMBOL)
void **IGeom_API;
#else
static void **IGeom_API = NULL;
#endif

#define iGeom_Type          (*(PyTypeObject*)    IGeom_API[ 0])
#define iGeomIter_Type      (*(PyTypeObject*)    IGeom_API[ 1])
#define iGeomEntitySet_Type (*(PyTypeObject*)    IGeom_API[ 2])
#define iGeomTag_Type       (*(PyTypeObject*)    IGeom_API[ 3])
#define NPY_IGEOMENTSET     (*(int*)             IGeom_API[ 4])
#define NPY_IGEOMTAG        (*(int*)             IGeom_API[ 5])
#define iGeomEntitySet_New  ( (iGeomEntitySet_Object * (*)      \
                              (iGeom_Object *))  IGeom_API[ 6])
#define iGeomTag_New        ( (iGeomTag_Object * (*)            \
                              (iGeom_Object *))  IGeom_API[ 7])
#define NormalPl_Type       (*(PyTypeObject*)    IGeom_API[ 8])
#define FaceEval_Type       (*(PyTypeObject*)    IGeom_API[ 9])
#define EdgeEval_Type       (*(PyTypeObject*)    IGeom_API[10])
#define Deriv1st_Type       (*(PyTypeObject*)    IGeom_API[11])
#define Deriv2nd_Type       (*(PyTypeObject*)    IGeom_API[12])
#define Intersect_Type      (*(PyTypeObject*)    IGeom_API[13])
#define Tolerance_Type      (*(PyTypeObject*)    IGeom_API[14])


#if !defined(NO_IMPORT_IGEOM) && !defined(NO_IMPORT)
static int import_iGeom(void)
{
    PyObject *module = PyImport_ImportModule("itaps.iGeom");
    PyObject *c_api = NULL;

    if(module == NULL)
        return -1;

    c_api = PyObject_GetAttrString(module,"_C_API");
    if(c_api == NULL)
    {
        Py_DECREF(module);
        return -2;
    }

    if(PyCObject_Check(c_api))
        IGeom_API = (void **)PyCObject_AsVoidPtr(c_api);

    Py_DECREF(c_api);
    Py_DECREF(module);

    if(IGeom_API == NULL)
        return -3;
    return 0;
}
#endif

#endif


#ifdef __cplusplus
} /* extern "C" */
#endif

#endif
