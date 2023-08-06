#ifndef PYTAPS_NUMPY_EXTENSIONS_H
#define PYTAPS_NUMPY_EXTENSIONS_H

#include <numpy/arrayobject.h>
#include "iBase_Python.h"

#define PyArray_NewFromMalloc(nd,dims,typenum,data)                     \
    PyArray_NewFromMallocBaseStrided(nd,dims,NULL,typenum,data,0)

#define PyArray_NewFromMallocBase(nd,dims,typenum,data,base)            \
    PyArray_NewFromMallocBaseStrided(nd,dims,NULL,typenum,data,base)

#define PyArray_NewFromMallocStrided(nd,dims,strides,typenum,data)      \
    PyArray_NewFromMallocBaseStrided(nd,dims,strides,typenum,data,0)

static PyObject *
PyArray_NewFromMallocBaseStrided(int nd,npy_intp *dims,npy_intp *strides,
                                 int typenum,void *data,PyObject *base)
{
    PyObject *arr = PyArray_New(&PyArray_Type,nd,dims,typenum,strides,data,0,
                                NPY_CARRAY,NULL);

    PyArray_BASE(arr) = (PyObject*)ArrDealloc_New(base,data);
    return arr;
}

static PyObject *
PyArray_TryFromObject(PyObject *obj,int typenum,int min_depth,int max_depth)
{
    PyObject *ret = PyArray_FromAny(obj,PyArray_DescrFromType(typenum),
                                    min_depth,max_depth,NPY_C_CONTIGUOUS,NULL);
    PyErr_Clear();
    return ret;
}

static int
PyArray_CheckVectors(PyObject *obj,int nd,npy_intp vec_dim,int index)
{
    if(PyArray_DIM(obj,index) != vec_dim)
    {
        PyErr_Format(PyExc_ValueError,"Expected %zdd vector or array of %zdd "
                     "vectors",vec_dim,vec_dim);
        return 0;
    }
    return 1;
}

static PyObject *
PyArray_ToVectors(PyObject *obj,int typenum,int nd,npy_intp vec_dim,int index)
{
    assert(index < nd);
    PyObject *ret = PyArray_FromAny(obj,PyArray_DescrFromType(typenum),nd,nd,
                                    NPY_C_CONTIGUOUS,NULL);
    if(ret == NULL)
        return NULL;

	if(PyArray_CheckVectors(ret,nd,vec_dim,index))
        return ret;
    else
    {
        Py_DECREF(ret);
        return NULL;
    }
}

#endif
