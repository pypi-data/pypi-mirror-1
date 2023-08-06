#include "errors.h"
#include "iMesh_Python.h"
#include "iBase_Python.h"
#include "structmember.h"

static int
iMeshEntSetObj_init(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set","instance",0};
    iMesh_Object *instance=0;
    iBaseEntitySet_Object *set;

    if( !PyArg_ParseTupleAndKeywords(args,kw,"O!|O!",kwlist,
                                     &iBaseEntitySet_Type,&set,&iMesh_Type,
                                     &instance))
        return -1;

    if(instance)
    {
        if(iMeshEntitySet_Check(set))
        {
            PyErr_SetString(PyExc_ValueError,ERR_MESH_SET_CTOR);
            return -1;
        }
        self->instance = instance;
    }
    else
    {
        if(!iMeshEntitySet_Check(set))
        {
            PyErr_SetString(PyExc_ValueError,ERR_EXP_INSTANCE);
            return -1;
        }
        self->instance = iMeshTag_GetInstance(set);
    }

    self->base.handle = set->handle;
    Py_XINCREF(self->instance);
    return 0;
}

static void
iMeshEntSetObj_dealloc(iMeshEntitySet_Object *self)
{
    Py_XDECREF(self->instance);
    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iMeshEntSetObj_load(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"filename","options",0};
    const char *name = 0;
    const char *options = "";
    if(!PyArg_ParseTupleAndKeywords(args,kw,"s|s",kwlist,&name,&options))
        return NULL;

    int err;
    iMesh_load(self->instance->handle,self->base.handle,name,options,&err,
               strlen(name),strlen(options));
    if(checkError(self->instance->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshEntSetObj_save(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"filename","options",0};
    const char *name = 0;
    const char *options = "";
    if(!PyArg_ParseTupleAndKeywords(args,kw,"s|s",kwlist,&name,&options))
        return NULL;

    int err;
    iMesh_save(self->instance->handle,self->base.handle,name,options,&err,
               strlen(name),strlen(options));
    if(checkError(self->instance->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshEntSetObj_getNumOfType(iMeshEntitySet_Object *self,PyObject *args,
                            PyObject *kw)
{
    static char *kwlist[] = {"type",0};
    enum iBase_EntityType type;
    int num,err;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&type))
        return NULL;

    iMesh_getNumOfType(self->instance->handle,self->base.handle,type,&num,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num);
}

static PyObject *
iMeshEntSetObj_getNumOfTopo(iMeshEntitySet_Object *self,PyObject *args,
                            PyObject *kw)
{
    static char *kwlist[] = {"topo",0};
    enum iMesh_EntityTopology topo;
    int num,err;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&topo))
        return NULL;

    iMesh_getNumOfTopo(self->instance->handle,self->base.handle,topo,&num,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num);
}

static PyObject *
iMeshEntSetObj_getEntities(iMeshEntitySet_Object *self,PyObject *args,
                           PyObject *kw)
{
    static char *kwlist[] = {"type","topo",0};
    enum iBase_EntityType type;
    enum iMesh_EntityTopology topo;
    iBase_EntityHandle *entities=0;
    int alloc=0,size,err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"ii",kwlist,&type,&topo))
        return NULL;

    iMesh_getEntities(self->instance->handle,self->base.handle,type,topo,
                      &entities,&alloc,&size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {size};
    return PyArray_NewFromMalloc(1,dims,NPY_IBASEENT,entities);
}

static PyObject *
iMeshEntSetObj_getAdjEntIndices(iMeshEntitySet_Object *self,PyObject *args,
                                PyObject *kw)
{
    static char *kwlist[] = {"type","topo","adj_type",0};
    int type_requestor,topo_requestor,type_requested;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"iii",kwlist,&type_requestor,
                                    &topo_requestor,&type_requested))
        return NULL;

    iBase_EntityHandle *entities=0;
    int ent_alloc=0,ent_size;
    iBase_EntityHandle *adj_ents=0;
    int adj_alloc=0,adj_size;
    int *indices=0;
    int ind_alloc=0,ind_size;
    int *offsets=0;
    int off_alloc=0,off_size;

    iMesh_getAdjEntIndices(self->instance->handle,self->base.handle,
                           type_requestor,topo_requestor,type_requested,
                           &entities,&ent_alloc,&ent_size,
                           &adj_ents,&adj_alloc,&adj_size,
                           &indices, &ind_alloc,&ind_size,
                           &offsets, &off_alloc,&off_size,
                           &err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp ent_dims[] = {ent_size};
    npy_intp adj_dims[] = {adj_size};
    npy_intp ind_dims[] = {ind_size};
    npy_intp off_dims[] = {off_size};

    return IndexedOffsetList_New(
        PyArray_NewFromMalloc(1,ent_dims,NPY_IBASEENT,entities),
        PyArray_NewFromMalloc(1,ind_dims,NPY_INT,indices),
        PyArray_NewFromMalloc(1,off_dims,NPY_INT,offsets),
        PyArray_NewFromMalloc(1,adj_dims,NPY_IBASEENT,adj_ents)
        );
}

static PyObject *
iMeshEntSetObj_isList(iMeshEntitySet_Object *self,void *closure)
{
    int is_list,err;
    iMesh_isList(self->instance->handle,self->base.handle,&is_list,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyBool_FromLong(is_list);
}

static PyObject *
iMeshEntSetObj_getNumEntSets(iMeshEntitySet_Object *self,PyObject *args,
                             PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int num_hops,num_sets,err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&num_hops))
        return NULL;

    iMesh_getNumEntSets(self->instance->handle,self->base.handle,num_hops,
                        &num_sets,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num_sets);
}

static PyObject *
iMeshEntSetObj_getEntSets(iMeshEntitySet_Object *self,PyObject *args,
                          PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int num_hops,err;
    iBase_EntitySetHandle *sets=0;
    int sets_alloc=0,sets_size;
  
    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&num_hops))
        return NULL;

    iMesh_getEntSets(self->instance->handle,self->base.handle,num_hops,&sets,
                     &sets_alloc,&sets_size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {sets_size};
    return PyArray_NewFromMallocBase(1,dims,NPY_IMESHENTSET,sets,
                                     (PyObject*)self->instance);
}

static PyObject *
iMeshEntSetObj_add(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
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
        iMesh_addEntArrToSet(self->instance->handle,data,size,
                             self->base.handle,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntitySet_Check(obj))
    {
        iBaseEntitySet_Object *set = (iBaseEntitySet_Object*)obj;
        iMesh_addEntSet(self->instance->handle,set->handle,self->base.handle,
                        &err);
    }
    else if(iBaseEntity_Check(obj))
    {
        iBaseEntity_Object *ent = (iBaseEntity_Object*)obj;
        iMesh_addEntToSet(self->instance->handle,ent->handle,self->base.handle,
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
iMeshEntSetObj_remove(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
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
        iMesh_rmvEntArrFromSet(self->instance->handle,data,size,
                               self->base.handle,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntitySet_Check(obj))
    {
        iBaseEntitySet_Object *set = (iBaseEntitySet_Object*)obj;
        iMesh_rmvEntSet(self->instance->handle,set->handle,self->base.handle,
                        &err);
    }
    else if(iBaseEntity_Check(obj))
    {
        iBaseEntity_Object *ent = (iBaseEntity_Object*)obj;
        iMesh_rmvEntFromSet(self->instance->handle,ent->handle,
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
iMeshEntSetObj_contains(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
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
        iMesh_isEntArrContained(self->instance->handle,self->base.handle,data,
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
        iMesh_isEntSetContained(self->instance->handle,self->base.handle,
                                iBaseEntitySet_GetHandle(obj),&contains,&err);
        if(checkError(self->instance->handle,err))
            return NULL;

        return PyBool_FromLong(contains);
    }
    else if(iBaseEntity_Check(obj))
    {
        int contains;
        iMesh_isEntContained(self->instance->handle,self->base.handle,
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
iMeshEntSetObj_in(iMeshEntitySet_Object *self,PyObject *value)
{
    int err;
    int contains;

    if(iBaseEntitySet_Check(value))
    {
        iMesh_isEntSetContained(self->instance->handle,self->base.handle,
                                iBaseEntitySet_GetHandle(value),&contains,&err);
        if(checkError(self->instance->handle,err))
            return -1;

        return contains;
    }
    else if(iBaseEntity_Check(value))
    {
        iMesh_isEntContained(self->instance->handle,self->base.handle,
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
iMeshEntSetObj_addChild(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iMesh_addPrntChld(self->instance->handle,self->base.handle,set->handle,
                      &err);
    if(checkError(self->instance->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshEntSetObj_removeChild(iMeshEntitySet_Object *self,PyObject *args,
                           PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iMesh_rmvPrntChld(self->instance->handle,self->base.handle,set->handle,
                      &err);
    if(checkError(self->instance->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshEntSetObj_isChild(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int is_child,err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iMesh_isChildOf(self->instance->handle,self->base.handle,set->handle,
                    &is_child,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyBool_FromLong(is_child);
}

static PyObject *
iMeshEntSetObj_getNumChildren(iMeshEntitySet_Object *self,PyObject *args,
                              PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int num_hops,num_children,err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&num_hops))
        return NULL;

    iMesh_getNumChld(self->instance->handle,self->base.handle,num_hops,
                     &num_children,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num_children);
}

static PyObject *
iMeshEntSetObj_getNumParents(iMeshEntitySet_Object *self,PyObject *args,
                             PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int num_hops,num_parents,err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&num_hops))
        return NULL;

    iMesh_getNumPrnt(self->instance->handle,self->base.handle,num_hops,
                     &num_parents,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num_parents);
}

static PyObject *
iMeshEntSetObj_getChildren(iMeshEntitySet_Object *self,PyObject *args,
                           PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int num_hops,sets_alloc=0,sets_size,err;
    iBase_EntitySetHandle *sets;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&num_hops))
        return NULL;

    iMesh_getChldn(self->instance->handle,self->base.handle,num_hops,&sets,
                   &sets_alloc,&sets_size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {sets_size};
    return PyArray_NewFromMallocBase(1,dims,NPY_IMESHENTSET,sets,
                                     (PyObject*)self->instance);
}

static PyObject *
iMeshEntSetObj_getParents(iMeshEntitySet_Object *self,PyObject *args,
                          PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int num_hops,sets_alloc=0,sets_size,err;
    iBase_EntitySetHandle *sets;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&num_hops))
        return NULL;

    iMesh_getPrnts(self->instance->handle,self->base.handle,num_hops,&sets,
                   &sets_alloc,&sets_size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {sets_size};
    return PyArray_NewFromMallocBase(1,dims,NPY_IMESHENTSET,sets,
                                     (PyObject*)self->instance);
}

static PyObject *
iMeshEntSetObj_iterate(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"type","topo","count",0};
    Py_ssize_t size = PyTuple_Size(args);
    PyObject *type;
    PyObject *topo;
    PyObject *count=0;
    PyObject *tuple;
    PyObject *ret;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O",kwlist,&type,&topo,&count))
        return NULL;

    tuple = PyTuple_Pack(size+1,self,type,topo,count);
    ret = PyObject_CallObject((PyObject*)&iMeshIter_Type,tuple);
    Py_DECREF(tuple);

    return ret;
}


static PyObject *
iMeshEntSetObj_sub(iMeshEntitySet_Object *lhs,iMeshEntitySet_Object *rhs)
{
    int err;
    iMeshEntitySet_Object *result;

    if(lhs->instance->handle != rhs->instance->handle)
        return NULL;

    result = iMeshEntitySet_New(lhs->instance);

    iMesh_subtract(lhs->instance->handle,lhs->base.handle,rhs->base.handle,
                   &result->base.handle,&err);
    if(checkError(lhs->instance->handle,err))
    {
        Py_DECREF((PyObject*)result);
        return NULL;
    }

    return (PyObject*)result;
}

static PyObject *
iMeshEntSetObj_bitand(iMeshEntitySet_Object *lhs,iMeshEntitySet_Object *rhs)
{
    int err;
    iMeshEntitySet_Object *result;

    if(lhs->instance->handle != rhs->instance->handle)
        return NULL;

    result = iMeshEntitySet_New(lhs->instance);

    iMesh_intersect(lhs->instance->handle,lhs->base.handle,rhs->base.handle,
                    &result->base.handle,&err);
    if(checkError(lhs->instance->handle,err))
    {
        Py_DECREF((PyObject*)result);
        return NULL;
    }

    return (PyObject*)result;
}

static PyObject *
iMeshEntSetObj_bitor(iMeshEntitySet_Object *lhs,iMeshEntitySet_Object *rhs)
{
    int err;
    iMeshEntitySet_Object *result;

    if(lhs->instance->handle != rhs->instance->handle)
        return NULL;

    result = iMeshEntitySet_New(lhs->instance);

    iMesh_unite(lhs->instance->handle,lhs->base.handle,rhs->base.handle,
                &result->base.handle,&err);
    if(checkError(lhs->instance->handle,err))
    {
        Py_DECREF((PyObject*)result);
        return NULL;
    }

    return (PyObject*)result;
}


static PyObject *
iMeshEntSetObj_difference(iMeshEntitySet_Object *self,PyObject *args,
                          PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    iMeshEntitySet_Object *rhs;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iMeshEntitySet_Type,
                                    &rhs))
        return NULL;

    return iMeshEntSetObj_sub(self,rhs);
}

static PyObject *
iMeshEntSetObj_intersection(iMeshEntitySet_Object *self,PyObject *args,
                            PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    iMeshEntitySet_Object *rhs;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iMeshEntitySet_Type,
                                    &rhs))
        return NULL;

    return iMeshEntSetObj_bitand(self,rhs);
}

static PyObject *
iMeshEntSetObj_union(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    iMeshEntitySet_Object *rhs;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iMeshEntitySet_Type,
                                    &rhs))
        return NULL;

    return iMeshEntSetObj_bitor(self,rhs);
}

static PyObject *
iMeshEntSetObj_repr(iMeshEntitySet_Object *self)
{
    return PyString_FromFormat("<itaps.iMesh.EntitySet %p>",self->base.handle);
}

static PyObject *
iMeshEntSetObj_richcompare(iMeshEntitySet_Object *lhs,
                           iMeshEntitySet_Object *rhs,int op)
{
    if(!iMeshEntitySet_Check(lhs) || !iMeshEntitySet_Check(rhs))
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


static PyMethodDef iMeshEntSetObj_methods[] = {
    { "load", (PyCFunction)iMeshEntSetObj_load, METH_KEYWORDS,
      "Load a mesh from a file into this set"
    },
    { "save", (PyCFunction)iMeshEntSetObj_save, METH_KEYWORDS,
      "Save this set of the mesh to a file"
    },
    { "getNumOfType", (PyCFunction)iMeshEntSetObj_getNumOfType, METH_KEYWORDS,
      "Get the number of entities with the specified type in this set"
    },
    { "getNumOfTopo", (PyCFunction)iMeshEntSetObj_getNumOfTopo, METH_KEYWORDS,
      "Get the number of entities with the specified topology in the set"
    },
    { "getEntities", (PyCFunction)iMeshEntSetObj_getEntities, METH_KEYWORDS,
      "Get entities of specific type and/or topology in this set"
    },
    { "getAdjEntIndices", (PyCFunction)iMeshEntSetObj_getAdjEntIndices,
      METH_KEYWORDS,
      "Get indexed representation of this set"
    },
    { "getNumEntSets", (PyCFunction)iMeshEntSetObj_getNumEntSets, METH_KEYWORDS,
      "Get the number of entity sets contained in this set"
    },
    { "getEntSets", (PyCFunction)iMeshEntSetObj_getEntSets, METH_KEYWORDS,
      "Get the entity sets contained in this set"
    },
    { "add", (PyCFunction)iMeshEntSetObj_add, METH_KEYWORDS,
      "Add an entity (or array of entities or entity set) to this set"
    },
    { "remove", (PyCFunction)iMeshEntSetObj_remove, METH_KEYWORDS,
      "Remove an entity (or array of entities or entity set) from this set"
    },
    { "contains", (PyCFunction)iMeshEntSetObj_contains, METH_KEYWORDS,
      "Return whether an entity (or array of entities or entity set) are "
      "contained in this set"
    },
    { "addChild", (PyCFunction)iMeshEntSetObj_addChild, METH_KEYWORDS,
      "Add parent/child links between two sets"
    },
    { "removeChild", (PyCFunction)iMeshEntSetObj_removeChild, METH_KEYWORDS,
      "Remove parent/child links between two sets"
    },
    { "isChild", (PyCFunction)iMeshEntSetObj_isChild, METH_KEYWORDS,
      "Return whether a set is a child of this set"
    },
    { "getNumChildren", (PyCFunction)iMeshEntSetObj_getNumChildren,
      METH_KEYWORDS,
      "Get the number of child sets linked from this set"
    },
    { "getNumParents", (PyCFunction)iMeshEntSetObj_getNumParents, METH_KEYWORDS,
      "Get the number of parent sets linked from this set"
    },
    { "getChildren", (PyCFunction)iMeshEntSetObj_getChildren, METH_KEYWORDS,
      "Get the child sets linked from this set"
    },
    { "getParents", (PyCFunction)iMeshEntSetObj_getParents, METH_KEYWORDS,
      "Get the parent sets linked from this set"
    },
    { "iterate", (PyCFunction)iMeshEntSetObj_iterate, METH_KEYWORDS,
      "Initialize an iterator over specified entity type, topology, and size"
    },
    { "difference", (PyCFunction)iMeshEntSetObj_difference, METH_KEYWORDS,
      "Get the difference of the two sets"
    },
    { "intersection", (PyCFunction)iMeshEntSetObj_intersection, METH_KEYWORDS,
      "Get the intersection of the two sets"
    },
    { "union", (PyCFunction)iMeshEntSetObj_union, METH_KEYWORDS,
      "Get the union of the two sets"
    },
    {0}
};

static PyMemberDef iMeshEntSetObj_members[] = {
    {"instance", T_OBJECT_EX, offsetof(iMeshEntitySet_Object, instance),
     READONLY, "base iMesh instance"},
    {0}
};

static PyGetSetDef iMeshEntSetObj_getset[] = {
    { "isList", (getter)iMeshEntSetObj_isList, 0,
      "Return whether a specified set is ordered or unordered", 0 },
    {0}
};

static PyNumberMethods iMeshEntSetObj_num = {
    0,                                        /* nb_add */
    (binaryfunc)iMeshEntSetObj_sub,           /* nb_subtract */
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
    (binaryfunc)iMeshEntSetObj_bitand,        /* nb_and */
    0,                                        /* nb_xor */
    (binaryfunc)iMeshEntSetObj_bitor,         /* nb_or */
    0,                                        /* nb_coerce */
    0,                                        /* nb_int */
    0,                                        /* nb_long */
    0,                                        /* nb_float */
    0,                                        /* nb_oct */
    0,                                        /* nb_hex */
};

static PySequenceMethods iMeshEntSetObj_seq = {
    0,                                        /* sq_length */
    0,                                        /* sq_concat */
    0,                                        /* sq_repeat */
    0,                                        /* sq_item */
    0,                                        /* sq_slice */
    0,                                        /* sq_ass_item */
    0,                                        /* sq_ass_slice */
    (objobjproc)iMeshEntSetObj_in,            /* sq_contains */
    0,                                        /* sq_inplace_concat */
    0,                                        /* sq_inplace_repeat */
};

static PyTypeObject iMeshEntitySet_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iMesh.EntitySet",                  /* tp_name */
    sizeof(iMeshEntitySet_Object),            /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iMeshEntSetObj_dealloc,       /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc)iMeshEntSetObj_repr,            /* tp_repr */
    &iMeshEntSetObj_num,                      /* tp_as_number */
    &iMeshEntSetObj_seq,                      /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "iMesh entity set object",                /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iMeshEntSetObj_richcompare,  /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iMeshEntSetObj_methods,                   /* tp_methods */
    iMeshEntSetObj_members,                   /* tp_members */
    iMeshEntSetObj_getset,                    /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)iMeshEntSetObj_init,            /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};
