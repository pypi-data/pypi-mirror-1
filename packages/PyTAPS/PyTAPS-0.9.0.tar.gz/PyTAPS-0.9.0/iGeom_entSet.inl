#include "errors.h"
#include "iGeom_Python.h"
#include "iBase_Python.h"
#include "structmember.h"

static int
iGeomEntSetObj_init(iGeomEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set","instance",0};
    iGeom_Object *instance=0;
    iBaseEntitySet_Object *set;

    if( !PyArg_ParseTupleAndKeywords(args,kw,"O!|O!",kwlist,
                                     &iBaseEntitySet_Type,&set,&iGeom_Type,
                                     &instance))
        return -1;

    if(instance)
    {
        if(iGeomEntitySet_Check(set))
        {
            PyErr_SetString(PyExc_ValueError,ERR_GEOM_SET_CTOR);
            return -1;
        }
        self->instance = instance;
    }
    else
    {
        if(!iGeomEntitySet_Check(set))
        {
            PyErr_SetString(PyExc_ValueError,ERR_EXP_INSTANCE);
            return -1;
        }
        self->instance = iGeomTag_GetInstance(set);
    }

    self->base.handle = set->handle;
    Py_XINCREF(self->instance);
    return 0;
}

static void
iGeomEntSetObj_dealloc(iGeomEntitySet_Object *self)
{
    Py_XDECREF(self->instance);
    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iGeomEntSetObj_getNumOfType(iGeomEntitySet_Object *self,PyObject *args,
                            PyObject *kw)
{
    static char *kwlist[] = {"type",0};
    enum iBase_EntityType type;
    int num,err;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&type))
        return NULL;

    iGeom_getNumOfType(self->instance->handle,self->base.handle,type,&num,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num);
}

static PyObject *
iGeomEntSetObj_getEntities(iGeomEntitySet_Object *self,PyObject *args,
                           PyObject *kw)
{
    static char *kwlist[] = {"type",0};
    enum iBase_EntityType type;
    iBase_EntityHandle *entities=0;
    int alloc=0,size,err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&type))
        return NULL;

    iGeom_getEntities(self->instance->handle,self->base.handle,type,
                      &entities,&alloc,&size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {size};
    return PyArray_NewFromMalloc(1,dims,NPY_IBASEENT,entities);
}

static PyObject *
iGeomEntSetObj_isList(iGeomEntitySet_Object *self,void *closure)
{
    int is_list,err;
    iGeom_isList(self->instance->handle,self->base.handle,&is_list,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyBool_FromLong(is_list);
}

static PyObject *
iGeomEntSetObj_getNumEntSets(iGeomEntitySet_Object *self,PyObject *args,
                             PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int num_hops,num_sets,err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&num_hops))
        return NULL;

    iGeom_getNumEntSets(self->instance->handle,self->base.handle,num_hops,
                        &num_sets,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num_sets);
}

static PyObject *
iGeomEntSetObj_getEntSets(iGeomEntitySet_Object *self,PyObject *args,
                          PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int num_hops,err;
    iBase_EntitySetHandle *sets=0;
    int sets_alloc=0,sets_size;
  
    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&num_hops))
        return NULL;

    iGeom_getEntSets(self->instance->handle,self->base.handle,num_hops,&sets,
                     &sets_alloc,&sets_size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {sets_size};
    return PyArray_NewFromMallocBase(1,dims,NPY_IGEOMENTSET,sets,
                                     (PyObject*)self->instance);
}

static PyObject *
iGeomEntSetObj_add(iGeomEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    int err;
    PyObject *obj;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&obj))
        return NULL;

    PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        int size = PyArray_SIZE(ents);
        iBase_EntityHandle *data = PyArray_DATA(ents);
        iGeom_addEntArrToSet(self->instance->handle,data,size,
                             self->base.handle,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntitySet_Check(obj))
    {
        iBaseEntitySet_Object *set = (iBaseEntitySet_Object*)obj;
        iGeom_addEntSet(self->instance->handle,set->handle,self->base.handle,
                        &err);
    }
    else if(iBaseEntity_Check(obj))
    {
        iBaseEntity_Object *ent = (iBaseEntity_Object*)obj;
        iGeom_addEntToSet(self->instance->handle,ent->handle,self->base.handle,
                          &err);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }

    if(checkError(self->instance->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomEntSetObj_remove(iGeomEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    int err;
    PyObject *obj;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&obj))
        return NULL;

    PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        int size = PyArray_SIZE(ents);
        iBase_EntityHandle *data = PyArray_DATA(ents);
        iGeom_rmvEntArrFromSet(self->instance->handle,data,size,
                               self->base.handle,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntitySet_Check(obj))
    {
        iBaseEntitySet_Object *set = (iBaseEntitySet_Object*)obj;
        iGeom_rmvEntSet(self->instance->handle,set->handle,self->base.handle,
                        &err);
    }
    else if(iBaseEntity_Check(obj))
    {
        iBaseEntity_Object *ent = (iBaseEntity_Object*)obj;
        iGeom_rmvEntFromSet(self->instance->handle,ent->handle,
                            self->base.handle,&err);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }

    if(checkError(self->instance->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomEntSetObj_contains(iGeomEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    int err;
    PyObject *obj;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&obj))
        return NULL;

    PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        int *contains=0;
        int contains_alloc=0,contains_size;

        int size = PyArray_SIZE(ents);
        iBase_EntityHandle *data = PyArray_DATA(ents);
        iGeom_isEntArrContained(self->instance->handle,self->base.handle,data,
                                size,&contains,&contains_alloc,&contains_size,
                                &err);
        Py_DECREF(ents);
        if(checkError(self->instance->handle,err))
            return NULL;

        npy_intp dims[] = {contains_size};
        npy_intp strides[] = {sizeof(int)/sizeof(npy_bool)};
        return PyArray_NewFromMallocStrided(1,dims,strides,NPY_BOOL,contains);
    }
    else if(iBaseEntitySet_Check(obj))
    {
        int contains;
        iGeom_isEntSetContained(self->instance->handle,self->base.handle,
                                iBaseEntitySet_GetHandle(obj),&contains,&err);
        if(checkError(self->instance->handle,err))
            return NULL;

        return PyBool_FromLong(contains);
    }
    else if(iBaseEntity_Check(obj))
    {
        int contains;
        iGeom_isEntContained(self->instance->handle,self->base.handle,
                             iBaseEntity_GetHandle(obj),&contains,&err);
        if(checkError(self->instance->handle,err))
            return NULL;

        return PyBool_FromLong(contains);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }
}

static int
iGeomEntSetObj_in(iGeomEntitySet_Object *self,PyObject *value)
{
    int err;
    int contains;

    if(iBaseEntitySet_Check(value))
    {
        iGeom_isEntSetContained(self->instance->handle,self->base.handle,
                                iBaseEntitySet_GetHandle(value),&contains,&err);
        if(checkError(self->instance->handle,err))
            return -1;

        return contains;
    }
    else if(iBaseEntity_Check(value))
    {
        iGeom_isEntContained(self->instance->handle,self->base.handle,
                             iBaseEntity_GetHandle(value),&contains,&err);
        if(checkError(self->instance->handle,err))
            return -1;

        return contains;
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTSET);
        return -1;
    }
}

/* TODO: add/removeParent? */

static PyObject *
iGeomEntSetObj_addChild(iGeomEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iGeom_addPrntChld(self->instance->handle,self->base.handle,set->handle,
                      &err);
    if(checkError(self->instance->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomEntSetObj_removeChild(iGeomEntitySet_Object *self,PyObject *args,
                           PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iGeom_rmvPrntChld(self->instance->handle,self->base.handle,set->handle,
                      &err);
    if(checkError(self->instance->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomEntSetObj_isChild(iGeomEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int is_child,err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iGeom_isChildOf(self->instance->handle,self->base.handle,set->handle,
                    &is_child,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyBool_FromLong(is_child);
}

static PyObject *
iGeomEntSetObj_getNumChildren(iGeomEntitySet_Object *self,PyObject *args,
                              PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int num_hops,num_children,err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&num_hops))
        return NULL;

    iGeom_getNumChld(self->instance->handle,self->base.handle,num_hops,
                     &num_children,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num_children);
}

static PyObject *
iGeomEntSetObj_getNumParents(iGeomEntitySet_Object *self,PyObject *args,
                             PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int num_hops,num_parents,err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&num_hops))
        return NULL;

    iGeom_getNumPrnt(self->instance->handle,self->base.handle,num_hops,
                     &num_parents,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num_parents);
}

static PyObject *
iGeomEntSetObj_getChildren(iGeomEntitySet_Object *self,PyObject *args,
                           PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int num_hops,sets_alloc=0,sets_size,err;
    iBase_EntitySetHandle *sets;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&num_hops))
        return NULL;

    iGeom_getChldn(self->instance->handle,self->base.handle,num_hops,&sets,
                   &sets_alloc,&sets_size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {sets_size};
    return PyArray_NewFromMallocBase(1,dims,NPY_IGEOMENTSET,sets,
                                     (PyObject*)self->instance);
}

static PyObject *
iGeomEntSetObj_getParents(iGeomEntitySet_Object *self,PyObject *args,
                          PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int num_hops,sets_alloc=0,sets_size,err;
    iBase_EntitySetHandle *sets;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&num_hops))
        return NULL;

    iGeom_getPrnts(self->instance->handle,self->base.handle,num_hops,&sets,
                   &sets_alloc,&sets_size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {sets_size};
    return PyArray_NewFromMallocBase(1,dims,NPY_IGEOMENTSET,sets,
                                     (PyObject*)self->instance);
}

static PyObject *
iGeomEntSetObj_iterate(iGeomEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"type","count",0};
    Py_ssize_t size = PyTuple_Size(args);
    PyObject *type;
    PyObject *count=0;
    PyObject *tuple;
    PyObject *ret;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O",kwlist,&type,&count))
        return NULL;

    tuple = PyTuple_Pack(size+1,self,type,count);
    ret = PyObject_CallObject((PyObject*)&iGeomIter_Type,tuple);
    Py_DECREF(tuple);

    return ret;
}


static PyObject *
iGeomEntSetObj_sub(iGeomEntitySet_Object *lhs,iGeomEntitySet_Object *rhs)
{
    int err;
    iGeomEntitySet_Object *result;

    if(lhs->instance->handle != rhs->instance->handle)
        return NULL;

    result = iGeomEntitySet_New(lhs->instance);

    iGeom_subtract(lhs->instance->handle,lhs->base.handle,rhs->base.handle,
                   &result->base.handle,&err);
    if(checkError(lhs->instance->handle,err))
    {
        Py_DECREF((PyObject*)result);
        return NULL;
    }

    return (PyObject*)result;
}

static PyObject *
iGeomEntSetObj_bitand(iGeomEntitySet_Object *lhs,iGeomEntitySet_Object *rhs)
{
    int err;
    iGeomEntitySet_Object *result;

    if(lhs->instance->handle != rhs->instance->handle)
        return NULL;

    result = iGeomEntitySet_New(lhs->instance);

    iGeom_intersect(lhs->instance->handle,lhs->base.handle,rhs->base.handle,
                    &result->base.handle,&err);
    if(checkError(lhs->instance->handle,err))
    {
        Py_DECREF((PyObject*)result);
        return NULL;
    }

    return (PyObject*)result;
}

static PyObject *
iGeomEntSetObj_bitor(iGeomEntitySet_Object *lhs,iGeomEntitySet_Object *rhs)
{
    int err;
    iGeomEntitySet_Object *result;

    if(lhs->instance->handle != rhs->instance->handle)
        return NULL;

    result = iGeomEntitySet_New(lhs->instance);

    iGeom_unite(lhs->instance->handle,lhs->base.handle,rhs->base.handle,
                &result->base.handle,&err);
    if(checkError(lhs->instance->handle,err))
    {
        Py_DECREF((PyObject*)result);
        return NULL;
    }

    return (PyObject*)result;
}


static PyObject *
iGeomEntSetObj_difference(iGeomEntitySet_Object *self,PyObject *args,
                          PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    iGeomEntitySet_Object *rhs;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iGeomEntitySet_Type,
                                    &rhs))
        return NULL;

    return iGeomEntSetObj_sub(self,rhs);
}

static PyObject *
iGeomEntSetObj_intersection(iGeomEntitySet_Object *self,PyObject *args,
                            PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    iGeomEntitySet_Object *rhs;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iGeomEntitySet_Type,
                                    &rhs))
        return NULL;

    return iGeomEntSetObj_bitand(self,rhs);
}

static PyObject *
iGeomEntSetObj_union(iGeomEntitySet_Object *self,PyObject *args,
                     PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    iGeomEntitySet_Object *rhs;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iGeomEntitySet_Type,
                                    &rhs))
        return NULL;

    return iGeomEntSetObj_bitor(self,rhs);
}

static PyObject *
iGeomEntSetObj_repr(iGeomEntitySet_Object *self)
{
    return PyString_FromFormat("<itaps.iGeom.EntitySet %p>",self->base.handle);
}

static PyObject *
iGeomEntSetObj_richcompare(iGeomEntitySet_Object *lhs,
                           iGeomEntitySet_Object *rhs,int op)
{
    if(!iGeomEntitySet_Check(lhs) || !iGeomEntitySet_Check(rhs))
    {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    switch(op)
    {
    case Py_EQ:
        return PyBool_FromLong(lhs->base.handle == rhs->base.handle &&
                               lhs->instance->handle == rhs->instance->handle);
    case Py_NE:
        return PyBool_FromLong(lhs->base.handle != rhs->base.handle ||
                               lhs->instance->handle != rhs->instance->handle);
    default:
        PyErr_SetNone(PyExc_TypeError);
        return NULL;
    }
}

static PyMethodDef iGeomEntSetObj_methods[] = {
    { "getNumOfType", (PyCFunction)iGeomEntSetObj_getNumOfType, METH_KEYWORDS,
      "Get the number of entities with the specified type in this set"
    },
    { "getEntities", (PyCFunction)iGeomEntSetObj_getEntities, METH_KEYWORDS,
      "Get entities of specific type in this set"
    },
    { "getNumEntSets", (PyCFunction)iGeomEntSetObj_getNumEntSets, METH_KEYWORDS,
      "Get the number of entity sets contained in this set"
    },
    { "getEntSets", (PyCFunction)iGeomEntSetObj_getEntSets, METH_KEYWORDS,
      "Get the entity sets contained in this set"
    },
    { "add", (PyCFunction)iGeomEntSetObj_add, METH_KEYWORDS,
      "Add an entity (or array of entities or entity set) to this set"
    },
    { "remove", (PyCFunction)iGeomEntSetObj_remove, METH_KEYWORDS,
      "Remove an entity (or array of entities or entity set) from this set"
    },
    { "contains", (PyCFunction)iGeomEntSetObj_contains, METH_KEYWORDS,
      "Return whether an entity (or array of entities or entity set) are "
      "contained in this set"
    },
    { "addChild", (PyCFunction)iGeomEntSetObj_addChild, METH_KEYWORDS,
      "Add parent/child links between two sets"
    },
    { "removeChild", (PyCFunction)iGeomEntSetObj_removeChild, METH_KEYWORDS,
      "Remove parent/child links between two sets"
    },
    { "isChild", (PyCFunction)iGeomEntSetObj_isChild, METH_KEYWORDS,
      "Return whether a set is a child of this set"
    },
    { "getNumChildren", (PyCFunction)iGeomEntSetObj_getNumChildren,
      METH_KEYWORDS,
      "Get the number of child sets linked from this set"
    },
    { "getNumParents", (PyCFunction)iGeomEntSetObj_getNumParents, METH_KEYWORDS,
      "Get the number of parent sets linked from this set"
    },
    { "getChildren", (PyCFunction)iGeomEntSetObj_getChildren, METH_KEYWORDS,
      "Get the child sets linked from this set"
    },
    { "getParents", (PyCFunction)iGeomEntSetObj_getParents, METH_KEYWORDS,
      "Get the parent sets linked from this set"
    },
    { "iterate", (PyCFunction)iGeomEntSetObj_iterate, METH_KEYWORDS,
      "Initialize an iterator over specified entity type, topology, and size"
    },
    { "difference", (PyCFunction)iGeomEntSetObj_difference, METH_KEYWORDS,
      "Get the difference of the two sets"
    },
    { "intersection", (PyCFunction)iGeomEntSetObj_intersection, METH_KEYWORDS,
      "Get the intersection of the two sets"
    },
    { "union", (PyCFunction)iGeomEntSetObj_union, METH_KEYWORDS,
      "Get the union of the two sets"
    },
    {0}
};

static PyMemberDef iGeomEntSetObj_members[] = {
    {"instance", T_OBJECT_EX, offsetof(iGeomEntitySet_Object, instance),
     READONLY, "base iGeom instance"},
    {0}
};

static PyGetSetDef iGeomEntSetObj_getset[] = {
    { "isList", (getter)iGeomEntSetObj_isList, 0,
      "Return whether a specified set is ordered or unordered", 0 },
    {0}
};

static PyNumberMethods iGeomEntSetObj_num = {
    0,                                        /* nb_add */
    (binaryfunc)iGeomEntSetObj_sub,           /* nb_subtract */
    0,                                        /* nb_multiply */
    0,                                        /* nb_divide */
    0,                                        /* nb_remainder */
    0,                                        /* nb_divmod */
    0,                                        /* nb_power */
    0,                                        /* nb_negative */
    0,                                        /* nb_positive */
    0,                                        /* nb_absolute */
    0,                                        /* nb_nonzero */
    0,                                        /* nb_invert */
    0,                                        /* nb_lshift */
    0,                                        /* nb_rshift */
    (binaryfunc)iGeomEntSetObj_bitand,        /* nb_and */
    0,                                        /* nb_xor */
    (binaryfunc)iGeomEntSetObj_bitor,         /* nb_or */
    0,                                        /* nb_coerce */
    0,                                        /* nb_int */
    0,                                        /* nb_long */
    0,                                        /* nb_float */
    0,                                        /* nb_oct */
    0,                                        /* nb_hex */
};

static PySequenceMethods iGeomEntSetObj_seq = {
    0,                                        /* sq_length */
    0,                                        /* sq_concat */
    0,                                        /* sq_repeat */
    0,                                        /* sq_item */
    0,                                        /* sq_slice */
    0,                                        /* sq_ass_item */
    0,                                        /* sq_ass_slice */
    (objobjproc)iGeomEntSetObj_in,            /* sq_contains */
    0,                                        /* sq_inplace_concat */
    0,                                        /* sq_inplace_repeat */
};

static PyTypeObject iGeomEntitySet_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iGeom.EntitySet",                  /* tp_name */
    sizeof(iGeomEntitySet_Object),            /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iGeomEntSetObj_dealloc,       /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc)iGeomEntSetObj_repr,            /* tp_repr */
    &iGeomEntSetObj_num,                      /* tp_as_number */
    &iGeomEntSetObj_seq,                      /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "iGeom entity set object",                /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iGeomEntSetObj_richcompare,  /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iGeomEntSetObj_methods,                   /* tp_methods */
    iGeomEntSetObj_members,                   /* tp_members */
    iGeomEntSetObj_getset,                    /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)iGeomEntSetObj_init,            /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};
