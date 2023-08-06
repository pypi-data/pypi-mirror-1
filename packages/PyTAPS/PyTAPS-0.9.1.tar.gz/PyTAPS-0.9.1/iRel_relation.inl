#include "errors.h"
#include "iRel_Python.h"
#include "iBase_Python.h"
#include "structmember.h"

static int
get_entity_data(PyObject *obj,PyObject **array,iBase_EntityHandle **entities,
                int *size)
{
    if((*array = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1)) != NULL)
    {
        *entities = PyArray_DATA(*array);
        *size = PyArray_SIZE(*array);
    }
    else if(iBaseEntity_Check(obj))
    {
        *entities = &iBaseEntity_GetHandle(obj);
        *size = 1;
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return 0;
    }
    return 1;
}

static int
get_entityset_data(PyObject *obj,PyObject **array,iBase_EntitySetHandle **sets,
                   int *size)
{
    if((*array = PyArray_TryFromObject(obj,NPY_IBASEENTSET,1,1)) != NULL)
    {
        *sets = PyArray_DATA(*array);
        *size = PyArray_SIZE(*array);
    }
    else if(iBaseEntitySet_Check(obj))
    {
        *sets = &iBaseEntitySet_GetHandle(obj);
        *size = 1;
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return 0;
    }
    return 1;
}

static int
npy_set_type(iBase_Object *o)
{
    if(iMesh_Check(o))
        return NPY_IMESHENTSET;
    if(iGeom_Check(o))
        return NPY_IGEOMENTSET;

    return -1;
}

static iBaseEntitySet_Object *
iAnyEntitySet_New(iBase_Object *instance)
{
    if(iMesh_Check(instance))
    {
        iMeshEntitySet_Object *o = iMeshEntitySet_NewRaw();
        o->instance = (iMesh_Object*)instance;
        o->base.handle = NULL;
        Py_INCREF(o->instance);
        return (iBaseEntitySet_Object*)o;
    }
    if(iGeom_Check(instance))
    {
        iGeomEntitySet_Object *o = iGeomEntitySet_NewRaw();
        o->instance = (iGeom_Object*)instance;
        o->base.handle = NULL;
        Py_INCREF(o->instance);
        return (iBaseEntitySet_Object*)o;
    }

    return 0;
}

static void
iRelRelationObj_dealloc(iRelRelation_Object *self)
{
    Py_XDECREF(self->instance);

    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iRelRelationObj_repr(iRelRelation_Object *self)
{
    return PyString_FromFormat("<itaps.iRel.Relation '%s<->%s' %p>",
                               self->related[0]->ob_type->tp_name,
                               self->related[1]->ob_type->tp_name,
                               self->handle);
}

static PyObject *
iRelRelationObj_setAssociation(iRelRelation_Object *self,PyObject *args,
                               PyObject *kw)
{
    static char *kwlist[] = {"first","second",0};

    PyObject *obj1;
    PyObject *obj2;
    int err;
    int swapped = 0;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO",kwlist,&obj1,&obj2))
        return NULL;

    PyObject *arr1 = NULL;
    PyObject *arr2 = NULL;
    iBase_EntityHandle *entities1 = NULL;
    iBase_EntityHandle *entities2 = NULL;
    iBase_EntitySetHandle *sets1 = NULL;
    iBase_EntitySetHandle *sets2 = NULL;
    int size1 = 0;
    int size2 = 0;

    if(!get_entity_data   (obj1,&arr1,&entities1,&size1) &&
       !get_entityset_data(obj1,&arr1,&sets1,    &size1))
        goto err;
    if(!get_entity_data   (obj2,&arr2,&entities2,&size2) &&
       !get_entityset_data(obj2,&arr2,&sets2,    &size2))
        goto err;

    if(arr1 && !arr2)
    {
        PyObject *tmp_arr;
        iBase_EntityHandle *tmp_ents;
        iBase_EntitySetHandle *tmp_sets;
        int tmp_size;

        tmp_arr = arr1; arr1 = arr2; arr2 = tmp_arr;
        tmp_ents = entities1; entities1 = entities2; entities2 = tmp_ents;
        tmp_sets = sets1; sets1 = sets2; sets2 = tmp_sets;
        tmp_size = size1; size1 = size2; size2 = tmp_size;

        swapped = 1;
    }

    if(arr1 && arr2)
    {
        if(entities1)
        {
            if(entities2)
                iRel_setEntArrEntArrAssociation(self->instance->handle,
                                                self->handle,entities1,size1,
                                                entities2,size2,&err);
            else
                iRel_setEntArrSetArrAssociation(self->instance->handle,
                                                self->handle,entities1,size1,
                                                sets2,size2,&err);
        }
        else
        {
            if(entities2)
                iRel_setSetArrEntArrAssociation(self->instance->handle,
                                                self->handle,sets1,size1,
                                                entities2,size2,&err);
            else
                iRel_setSetArrSetArrAssociation(self->instance->handle,
                                                self->handle,sets1,size1,
                                                sets2,size2,&err);
        }
    }
    else if(arr2)
    {
        if(entities1)
        {
            if(entities2)
                iRel_setEntEntArrAssociation(self->instance->handle,
                                             self->handle,entities1[0],swapped,
                                             entities2,size2,&err);
            else
                iRel_setEntSetArrAssociation(self->instance->handle,
                                             self->handle,entities1[0],swapped,
                                             sets2,size2,&err);
        }
        else
        {
            if(entities2)
                iRel_setSetEntArrAssociation(self->instance->handle,
                                             self->handle,sets1[0],swapped,
                                             entities2,size2,&err);
            else
                iRel_setSetSetArrAssociation(self->instance->handle,
                                             self->handle,sets1[0],swapped,
                                             sets2,size2,&err);
        }
    }
    else
    {
        if(entities1)
        {
            if(entities2)
                iRel_setEntEntAssociation(self->instance->handle,self->handle,
                                          entities1[0],entities2[0],&err);
            else
                iRel_setEntSetAssociation(self->instance->handle,self->handle,
                                          entities1[0],sets2[0],&err);
        }
        else
        {
            if(entities2)
                iRel_setSetEntAssociation(self->instance->handle,self->handle,
                                          sets1[0],entities2[0],&err);
            else
                iRel_setSetSetAssociation(self->instance->handle,self->handle,
                                          sets1[0],sets2[0],&err);
        }
    }

    Py_XDECREF(arr1);
    Py_XDECREF(arr2);
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;

err:
    Py_XDECREF(arr1);
    Py_XDECREF(arr2);
    return NULL;
}

static PyObject *
iRelRelationObj_getEntAssociation(iRelRelation_Object *self,PyObject *args,
                                  PyObject *kw)
{
    static char *kwlist[] = {"entities","switch_order",0};

    PyObject *obj1;
    PyObject *obj2;
    int err;
    int swapped;

    if(PyArg_ParseTupleAndKeywords(args,kw,"OO!",kwlist,&obj1,&PyBool_Type,
                                    &obj2))
        swapped = (obj2 == Py_True);
    else
    {
        if(kw == NULL || PyDict_Size(kw) != 1)
            return NULL;

        if((obj1 = PyDict_GetItemString(kw,"first")) != NULL)
            swapped = 0;
        else if((obj1 = PyDict_GetItemString(kw,"second")) != NULL)
            swapped = 1;
        else
            return NULL;
    }

    PyObject *arr;
    if((arr = PyArray_TryFromObject(obj1,NPY_IBASEENT,1,1)) != NULL)
    {
        iBase_EntityHandle *entities = PyArray_DATA(arr);
        int ent_size = PyArray_SIZE(arr);
        iBase_EntityHandle *result = NULL;
        int res_alloc = 0,res_size;
        int *offsets = NULL;
        int off_alloc = 0,off_size;

        iRel_getEntArrEntArrAssociation(self->instance->handle,self->handle,
                                        entities,ent_size,swapped,
                                        &result, &res_alloc,&res_size,
                                        &offsets,&off_alloc,&off_size,&err);
        Py_DECREF(arr);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp off_dims[] = {off_size};
        npy_intp res_dims[] = {res_size};
        return OffsetList_New(
            PyArray_NewFromMalloc(1,off_dims,NPY_INT,offsets),
            PyArray_NewFromMalloc(1,res_dims,NPY_IBASEENT,result)
            );
    }
    else if((arr = PyArray_TryFromObject(obj1,NPY_IBASEENTSET,1,1)) != NULL)
    {
        iBase_EntitySetHandle *sets = PyArray_DATA(arr);
        int set_size = PyArray_SIZE(arr);
        iBase_EntityHandle *result = NULL;
        int res_alloc = 0,res_size;
        int *offsets = NULL;
        int off_alloc = 0,off_size;

        iRel_getSetArrEntArrAssociation(self->instance->handle,self->handle,
                                        sets,set_size,swapped,
                                        &result, &res_alloc,&res_size,
                                        &offsets,&off_alloc,&off_size,&err);
        Py_DECREF(arr);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp off_dims[] = {off_size};
        npy_intp res_dims[] = {res_size};
        return OffsetList_New(
            PyArray_NewFromMalloc(1,off_dims,NPY_INT,offsets),
            PyArray_NewFromMalloc(1,res_dims,NPY_IBASEENT,result)
            );
    }
    else if(iBaseEntity_Check(obj1))
    {
        iBaseEntity_Object *result = iBaseEntity_New();
        iRel_getEntEntAssociation(self->instance->handle,self->handle,
                                  iBaseEntity_GetHandle(obj1),swapped,
                                  &result->handle,&err);
        if(checkError(self->handle,err))
            return NULL;
        return (PyObject*)result;
    }
    else if(iBaseEntitySet_Check(obj1))
    {
        iBaseEntity_Object *result = iBaseEntity_New();
        iRel_getSetEntAssociation(self->instance->handle,self->handle,
                                  iBaseEntitySet_GetHandle(obj1),swapped,
                                  &result->handle,&err);
        if(checkError(self->handle,err))
            return NULL;
        return (PyObject*)result;
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }
}

static PyObject *
iRelRelationObj_getEntArrAssociation(iRelRelation_Object *self,PyObject *args,
                                     PyObject *kw)
{
    static char *kwlist[] = {"entities","switch_order",0};

    PyObject *obj1;
    PyObject *obj2;
    int err;
    int swapped;

    if(PyArg_ParseTupleAndKeywords(args,kw,"OO!",kwlist,&obj1,&PyBool_Type,
                                    &obj2))
        swapped = (obj2 == Py_True);
    else
    {
        if(kw == NULL || PyDict_Size(kw) != 1)
            return NULL;

        if((obj1 = PyDict_GetItemString(kw,"first")) != NULL)
            swapped = 0;
        else if((obj1 = PyDict_GetItemString(kw,"second")) != NULL)
            swapped = 1;
        else
            return NULL;
    }

    PyObject *arr;
    if((arr = PyArray_TryFromObject(obj1,NPY_IBASEENT,1,1)) != NULL)
    {
        iBase_EntityHandle *entities = PyArray_DATA(arr);
        int ent_size = PyArray_SIZE(arr);
        iBase_EntityHandle *result = NULL;
        int res_alloc = 0,res_size;
        int *offsets = NULL;
        int off_alloc = 0,off_size;

        iRel_getEntArrEntArrAssociation(self->instance->handle,self->handle,
                                        entities,ent_size,swapped,
                                        &result, &res_alloc,&res_size,
                                        &offsets,&off_alloc,&off_size,&err);
        Py_DECREF(arr);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp off_dims[] = {off_size};
        npy_intp res_dims[] = {res_size};
        return OffsetList_New(
            PyArray_NewFromMalloc(1,off_dims,NPY_INT,offsets),
            PyArray_NewFromMalloc(1,res_dims,NPY_IBASEENT,result)
            );
    }
    else if((arr = PyArray_TryFromObject(obj1,NPY_IBASEENTSET,1,1)) != NULL)
    {
        iBase_EntitySetHandle *sets = PyArray_DATA(arr);
        int set_size = PyArray_SIZE(arr);
        iBase_EntityHandle *result = NULL;
        int res_alloc = 0,res_size;
        int *offsets = NULL;
        int off_alloc = 0,off_size;

        iRel_getSetArrEntArrAssociation(self->instance->handle,self->handle,
                                        sets,set_size,swapped,
                                        &result, &res_alloc,&res_size,
                                        &offsets,&off_alloc,&off_size,&err);
        Py_DECREF(arr);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp off_dims[] = {off_size};
        npy_intp res_dims[] = {res_size};
        return OffsetList_New(
            PyArray_NewFromMalloc(1,off_dims,NPY_INT,offsets),
            PyArray_NewFromMalloc(1,res_dims,NPY_IBASEENT,result)
            );
    }
    else if(iBaseEntity_Check(obj1))
    {
        iBase_EntityHandle *result = NULL;
        int res_alloc = 0,res_size;
        iRel_getEntEntArrAssociation(self->instance->handle,self->handle,
                                     iBaseEntity_GetHandle(obj1),swapped,
                                     &result,&res_alloc,&res_size,&err);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp res_dims[] = {res_size};
        return PyArray_NewFromMalloc(1,res_dims,NPY_IBASEENT,result);
    }
    else if(iBaseEntitySet_Check(obj1))
    {
        iBase_EntityHandle *result = NULL;
        int res_alloc = 0,res_size;
        iRel_getSetEntArrAssociation(self->instance->handle,self->handle,
                                  iBaseEntitySet_GetHandle(obj1),swapped,
                                  &result,&res_alloc,&res_size,&err);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp res_dims[] = {res_size};
        return PyArray_NewFromMalloc(1,res_dims,NPY_IBASEENT,result);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }
}

static PyObject *
iRelRelationObj_getSetAssociation(iRelRelation_Object *self,PyObject *args,
                                  PyObject *kw)
{
    static char *kwlist[] = {"entities","switch_order",0};

    PyObject *obj1;
    PyObject *obj2;
    int err;
    int swapped;

    if(PyArg_ParseTupleAndKeywords(args,kw,"OO!",kwlist,&obj1,&PyBool_Type,
                                    &obj2))
        swapped = (obj2 == Py_True);
    else
    {
        if(kw == NULL || PyDict_Size(kw) != 1)
            return NULL;

        if((obj1 = PyDict_GetItemString(kw,"first")) != NULL)
            swapped = 0;
        else if((obj1 = PyDict_GetItemString(kw,"second")) != NULL)
            swapped = 1;
        else
            return NULL;
    }

    iBase_Object *related = self->related[!swapped];
    PyObject *arr;
    if((arr = PyArray_TryFromObject(obj1,NPY_IBASEENT,1,1)) != NULL)
    {
        iBase_EntityHandle *entities = PyArray_DATA(arr);
        int ent_size = PyArray_SIZE(arr);
        iBase_EntitySetHandle *result = NULL;
        int res_alloc = 0,res_size;

        iRel_getEntArrSetArrAssociation(self->instance->handle,self->handle,
                                        entities,ent_size,swapped,
                                        &result,&res_alloc,&res_size,&err);
        Py_DECREF(arr);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp res_dims[] = {res_size};
        return PyArray_NewFromMallocBase(1,res_dims,npy_set_type(related),
                                         result,(PyObject*)related);
    }
    else if((arr = PyArray_TryFromObject(obj1,NPY_IBASEENTSET,1,1)) != NULL)
    {
        iBase_EntitySetHandle *sets = PyArray_DATA(arr);
        int set_size = PyArray_SIZE(arr);
        iBase_EntitySetHandle *result = NULL;
        int res_alloc = 0,res_size;

        iRel_getSetArrSetArrAssociation(self->instance->handle,self->handle,
                                        sets,set_size,swapped,
                                        &result,&res_alloc,&res_size,&err);
        Py_DECREF(arr);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp res_dims[] = {res_size};
        return PyArray_NewFromMallocBase(1,res_dims,npy_set_type(related),
                                         result,(PyObject*)related);
    }
    else if(iBaseEntity_Check(obj1))
    {
        iBaseEntitySet_Object *result = iAnyEntitySet_New(related);
        iRel_getEntSetAssociation(self->instance->handle,self->handle,
                                  iBaseEntity_GetHandle(obj1),swapped,
                                  &result->handle,&err);
        if(checkError(self->handle,err))
            return NULL;
        return (PyObject*)result;
    }
    else if(iBaseEntitySet_Check(obj1))
    {
        iBaseEntitySet_Object *result = iAnyEntitySet_New(related);
        iRel_getSetSetAssociation(self->instance->handle,self->handle,
                                  iBaseEntitySet_GetHandle(obj1),swapped,
                                  &result->handle,&err);
        if(checkError(self->handle,err))
            return NULL;
        return (PyObject*)result;
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }
}

static PyObject *
iRelRelationObj_getSetArrAssociation(iRelRelation_Object *self,PyObject *args,
                                     PyObject *kw)
{
    static char *kwlist[] = {"entities","switch_order",0};

    PyObject *obj1;
    PyObject *obj2;
    int err;
    int swapped;

    if(PyArg_ParseTupleAndKeywords(args,kw,"OO!",kwlist,&obj1,&PyBool_Type,
                                    &obj2))
        swapped = (obj2 == Py_True);
    else
    {
        if(kw == NULL || PyDict_Size(kw) != 1)
            return NULL;

        if((obj1 = PyDict_GetItemString(kw,"first")) != NULL)
            swapped = 0;
        else if((obj1 = PyDict_GetItemString(kw,"second")) != NULL)
            swapped = 1;
        else
            return NULL;
    }

    iBase_Object *related = self->related[!swapped];
    PyObject *arr;
    if((arr = PyArray_TryFromObject(obj1,NPY_IBASEENT,1,1)) != NULL)
    {
        iBase_EntityHandle *entities = PyArray_DATA(arr);
        int ent_size = PyArray_SIZE(arr);
        iBase_EntitySetHandle *result = NULL;
        int res_alloc = 0,res_size;

        iRel_getEntArrSetArrAssociation(self->instance->handle,self->handle,
                                        entities,ent_size,swapped,
                                        &result,&res_alloc,&res_size,&err);
        Py_DECREF(arr);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp res_dims[] = {res_size};
        return PyArray_NewFromMallocBase(1,res_dims,npy_set_type(related),
                                         result,(PyObject*)related);
    }
    else if((arr = PyArray_TryFromObject(obj1,NPY_IBASEENTSET,1,1)) != NULL)
    {
        iBase_EntitySetHandle *sets = PyArray_DATA(arr);
        int set_size = PyArray_SIZE(arr);
        iBase_EntitySetHandle *result = NULL;
        int res_alloc = 0,res_size;

        iRel_getSetArrSetArrAssociation(self->instance->handle,self->handle,
                                        sets,set_size,swapped,
                                        &result,&res_alloc,&res_size,&err);
        Py_DECREF(arr);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp res_dims[] = {res_size};
        return PyArray_NewFromMallocBase(1,res_dims,npy_set_type(related),
                                         result,(PyObject*)related);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }
}

static PyObject *
iRelRelationObj_inferAllAssociations(iRelRelation_Object *self)
{
    int err;
    iRel_inferAllAssociations(self->instance->handle,self->handle,&err);
    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iRelRelationObj_inferAssociations(iRelRelation_Object *self,PyObject *args,
                                  PyObject *kw)
{
    static char *kwlist[] = {"entities","switch_order",0};

    PyObject *obj1;
    PyObject *obj2;
    int err;
    int swapped;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO!",kwlist,&obj1,&PyBool_Type,
                                    &obj2))
    {
        if(kw == NULL || PyDict_Size(kw) != 1)
            return NULL;

        if((obj1 = PyDict_GetItemString(kw,"first")) != NULL)
            swapped = 0;
        else if((obj1 = PyDict_GetItemString(kw,"second")) != NULL)
            swapped = 1;
        else
            return NULL;
    }
    else
        swapped = (obj2 == Py_True);

    PyObject *arr;
    if((arr = PyArray_TryFromObject(obj1,NPY_IBASEENT,1,1)) != NULL)
    {
        iBase_EntityHandle *entities = PyArray_DATA(arr);
        int ent_size = PyArray_SIZE(arr);

        iRel_inferEntArrAssociations(self->instance->handle,self->handle,
                                     entities,ent_size,swapped,&err);
        Py_DECREF(arr);
    }
    else if((arr = PyArray_TryFromObject(obj1,NPY_IBASEENTSET,1,1)) != NULL)
    {
        iBase_EntitySetHandle *sets = PyArray_DATA(arr);
        int set_size = PyArray_SIZE(arr);

        iRel_inferSetArrAssociations(self->instance->handle,self->handle,
                                     sets,set_size,swapped,&err);
        Py_DECREF(arr);
    }
    else if(iBaseEntity_Check(obj1))
        iRel_inferEntAssociations(self->instance->handle,self->handle,
                                  iBaseEntity_GetHandle(obj1),swapped,&err);
    else if(iBaseEntitySet_Check(obj1))
        iRel_inferSetAssociations(self->instance->handle,self->handle,
                                  iBaseEntitySet_GetHandle(obj1),swapped,&err);
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iRelRelationObj_richcompare(iRelRelation_Object *lhs,
							iRelRelation_Object *rhs,int op)
{
    if(!iRelRelation_Check(lhs) || !iRelRelation_Check(rhs))
    {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    switch(op)
    {
    case Py_EQ:
        return PyBool_FromLong(lhs->handle == rhs->handle &&
                               lhs->instance->handle == rhs->instance->handle);
    case Py_NE:
        return PyBool_FromLong(lhs->handle != rhs->handle ||
                               lhs->instance->handle != rhs->instance->handle);
    default:
        PyErr_SetNone(PyExc_TypeError);
        return NULL;
    }
}



static PyMethodDef iRelRelationObj_methods[] = {
    { "setAssociation", (PyCFunction)iRelRelationObj_setAssociation,
      METH_KEYWORDS, "Set a relation between two (arrays of) entities and/or "
      "sets"
    },
    { "getEntAssociation", (PyCFunction)iRelRelationObj_getEntAssociation,
      METH_KEYWORDS, "Get the entity related to a specified entity(ies) or "
      "set(s)"
    },
    { "getEntArrAssociation", (PyCFunction)iRelRelationObj_getEntArrAssociation,
      METH_KEYWORDS, "Get the entities related to a specified entity(ies) or "
      "set(s)"
    },
    { "getSetAssociation", (PyCFunction)iRelRelationObj_getSetAssociation,
      METH_KEYWORDS, "Get the entity set related to a specified entity(ies) or "
      "set(s)"
    },
    { "getSetArrAssociation", (PyCFunction)iRelRelationObj_getSetArrAssociation,
      METH_KEYWORDS, "Get the entity sets related to a specified entities or "
      "sets"
    },
    { "inferAllAssociations", (PyCFunction)iRelRelationObj_inferAllAssociations,
      METH_NOARGS, "Infer relations between all entities"
    },
    { "inferAssociations", (PyCFunction)iRelRelationObj_inferAssociations,
      METH_KEYWORDS, "Infer relations between specified entity(ies) or set(s)"
    },
    {0}
};

static PyMemberDef iRelRelationObj_members[] = {
    {"instance", T_OBJECT_EX, offsetof(iRelRelation_Object, instance),
     READONLY, "base iRel instance"},
    {"first", T_OBJECT_EX, offsetof(iRelRelation_Object, related[0]),
     READONLY, "first related instance"},
    {"second", T_OBJECT_EX, offsetof(iRelRelation_Object, related[1]),
     READONLY, "second related instance"},
    {0}
};


static PyTypeObject iRelRelation_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iRel.Relation",                    /* tp_name */
    sizeof(iRelRelation_Object),              /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iRelRelationObj_dealloc,      /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc)iRelRelationObj_repr,           /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "iRel relation object",                   /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iRelRelationObj_richcompare, /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iRelRelationObj_methods,                  /* tp_methods */
    iRelRelationObj_members,                  /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};
