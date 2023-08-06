#include "iGeom_Python.h"
#include "iBase_Python.h"
#include "structmember.h"

static int
iGeomIterObj_init(iGeomIter_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set","type","size",0};
    iGeomEntitySet_Object *set;
    int type,array_size=1,err;

    if( !PyArg_ParseTupleAndKeywords(args,kw,"O!i|i",kwlist,
                                     &iGeomEntitySet_Type,&set,&type,
                                     &array_size) )
        return -1;

    self->instance = set->instance;
    Py_INCREF(self->instance);

    if(array_size == 1)
    {
        self->is_arr = 0;
        iGeom_initEntIter(self->instance->handle,set->base.handle,type,
                          &self->iter,&err);
    }
    else
    {
        self->is_arr = 1;
        iGeom_initEntArrIter(self->instance->handle,set->base.handle,type,
                             array_size,&self->arr_iter,&err);
    }
    if(checkError(self->instance->handle,err))
        return -1;

    return 0;
}

static void
iGeomIterObj_dealloc(iGeomIter_Object *self)
{
    if(self->instance && self->iter)
    {
        int err;
        if(self->is_arr)
            iGeom_endEntArrIter(self->instance->handle,self->arr_iter,&err);
        else
            iGeom_endEntIter(self->instance->handle,self->iter,&err);
    }

    Py_XDECREF(self->instance);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iGeomIterObj_reset(iGeomIter_Object *self)
{
    int err;
    if(self->is_arr)
        iGeom_resetEntArrIter(self->instance->handle,self->arr_iter,&err);
    else
        iGeom_resetEntIter(self->instance->handle,self->iter,&err);

    if(checkError(self->instance->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomIterObj_iternext(iGeomIter_Object *self)
{
    int has_data,err;

    if(self->is_arr)
    {
        iBase_EntityHandle *entities=0;
        int alloc=0,size;

        iGeom_getNextEntArrIter(self->instance->handle,self->arr_iter,&entities,
                                &alloc,&size,&has_data,&err);
        if(checkError(self->instance->handle,err))
            return NULL;
        if(!has_data)
            return NULL;

        npy_intp dims[] = {size};
        return PyArray_NewFromMalloc(1,dims,NPY_IBASEENT,entities);
    }
    else
    {
        iBase_EntityHandle entity;
        iGeom_getNextEntIter(self->instance->handle,self->iter,&entity,
                             &has_data,&err);
        if(checkError(self->instance->handle,err))
            return NULL;
        if(!has_data)
            return NULL;

        iBaseEntity_Object *o = iBaseEntity_New();
        o->handle = entity;
        return (PyObject*)o;
    }
}

static PyMethodDef iGeomIterObj_methods[] = {
    { "reset", (PyCFunction)iGeomIterObj_reset, METH_NOARGS,
      "Reset the iterator"
    },
    {0}
};

static PyMemberDef iGeomIterObj_members[] = {
    {"instance", T_OBJECT_EX, offsetof(iGeomIter_Object, instance), READONLY,
     "base iGeom instance"},
    {0}
};

static PyTypeObject iGeomIter_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iGeom.Iterator",                   /* tp_name */
    sizeof(iGeomIter_Object),                 /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iGeomIterObj_dealloc,         /* tp_dealloc */
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER |
    Py_TPFLAGS_BASETYPE,                      /* tp_flags */
    "iGeom iterator object",                  /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    PyObject_SelfIter,                        /* tp_iter */
    (iternextfunc)iGeomIterObj_iternext,      /* tp_iternext */
    iGeomIterObj_methods,                     /* tp_methods */
    iGeomIterObj_members,                     /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)iGeomIterObj_init,              /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};
