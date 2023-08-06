#include "iGeom_Python.h"
#include "iBase_Python.h"
#include "errors.h"
#include "structmember.h"

static char typechars[] = {'i','d','E','b'};

static enum iBase_TagValueType
char_to_type(char c)
{
    int i;
    for(i=0; i<sizeof(typechars); i++)
    {
        if(typechars[i] == c)
            return i;
    }
    return -1;
}

static char
type_to_char(enum iBase_TagValueType t)
{
    return typechars[t];
}

static int
iGeomTagObj_init(iGeomTag_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"tag","instance",0};
    iGeom_Object *instance=0;
    iBaseTag_Object *tag;

    if( !PyArg_ParseTupleAndKeywords(args,kw,"O!|O!",kwlist,&iBaseTag_Type,
                                     &tag,&iGeom_Type,&instance))
        return -1;

    if(instance)
    {
        if(iGeomTag_Check(tag))
        {
            PyErr_SetString(PyExc_ValueError,ERR_GEOM_TAG_CTOR);
            return -1;
        }
        self->instance = instance;
    }
    else
    {
        if(!iGeomTag_Check(tag))
        {
            PyErr_SetString(PyExc_ValueError,ERR_EXP_INSTANCE);
            return -1;
        }
        self->instance = iGeomTag_GetInstance(tag);
    }

    self->base.handle = tag->handle;
    Py_XINCREF(self->instance);
    return 0;
}

static void
iGeomTagObj_dealloc(iGeomTag_Object *self)
{
    Py_XDECREF(self->instance);
    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iGeomTagObj_getName(iGeomTag_Object *self,void *closure)
{
    char name[512];
    int err;
    iGeom_getTagName(self->instance->handle,self->base.handle,name,&err,
                     sizeof(name));
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyString_FromString(name);
}

static PyObject *
iGeomTagObj_getSizeValues(iGeomTag_Object *self,void *closure)
{
    int size,err;
    iGeom_getTagSizeValues(self->instance->handle,self->base.handle,&size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(size);
}

static PyObject *
iGeomTagObj_getSizeBytes(iGeomTag_Object *self,void *closure)
{
    int size,err;
    iGeom_getTagSizeBytes(self->instance->handle,self->base.handle,&size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(size);
}

static PyObject *
iGeomTagObj_getType(iGeomTag_Object *self,void *closure)
{
    int type,err;
    iGeom_getTagType(self->instance->handle,self->base.handle,&type,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return Py_BuildValue("c",type_to_char(type));
}

static PyObject *
iGeomTagObj_setData(iGeomTag_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","data","type",0};
    PyObject *obj;
    PyObject *data_obj;
    char typechar=0;
    int type;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|c",kwlist,&obj,&data_obj,
                                    &typechar))
        return NULL;

    if(typechar == 0)
    {
        /* infer the type of the data */
        iGeom_getTagType(self->instance->handle,self->base.handle,&type,&err);
        if(checkError(self->instance->handle,err))
            return NULL;
    }
    else
    {
        type = char_to_type(typechar);
        if(type == -1)
        {
            PyErr_SetString(PyExc_ValueError,ERR_TYPE_CODE);
            return NULL;
        }
    }
 
    PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        int ent_size;
        iBase_EntityHandle *entities;
        int data_size;
        PyObject *data_arr=0;

        ent_size = PyArray_SIZE(ents);
        entities = PyArray_DATA(ents);

        if(type == iBase_INTEGER)
        {
            data_arr = PyArray_FROMANY(data_obj,NPY_INT,1,1,NPY_C_CONTIGUOUS);
            if(data_arr == NULL)
                return NULL;

            data_size = PyArray_SIZE(data_arr);
            int *data = PyArray_DATA(data_arr);
            iGeom_setIntArrData(self->instance->handle,entities,ent_size,
                                self->base.handle,data,data_size,&err);
        }
        else if(type == iBase_DOUBLE)
        {
            data_arr = PyArray_FROMANY(data_obj,NPY_DOUBLE,1,1,
                                       NPY_C_CONTIGUOUS);
            if(data_arr == NULL)
                return NULL;

            data_size = PyArray_SIZE(data_arr);
            double *data = PyArray_DATA(data_arr);
            iGeom_setDblArrData(self->instance->handle,entities,ent_size,
                                self->base.handle,data,data_size,&err);
        }
        else if(type == iBase_ENTITY_HANDLE)
        {
            data_arr = PyArray_FROMANY(data_obj,NPY_IBASEENT,1,1,
                                       NPY_C_CONTIGUOUS);
            if(data_arr == NULL)
                return NULL;

            data_size = PyArray_SIZE(data_arr);
            iBase_EntityHandle *data = PyArray_DATA(data_arr);
            iGeom_setEHArrData(self->instance->handle,entities,ent_size,
                               self->base.handle,data,data_size,&err);
        }
        else /* iBase_BYTES */
        {
            data_arr = PyArray_FROMANY(data_obj,NPY_BYTE,1,1,NPY_C_CONTIGUOUS);
            if(data_arr == NULL)
                return NULL;

            data_size = PyArray_SIZE(data_arr);
            char *data = PyArray_DATA(data_arr);
            iGeom_setArrData(self->instance->handle,entities,ent_size,
                             self->base.handle,data,data_size,&err);
        }

        Py_DECREF(ents);
        Py_XDECREF(data_arr);
    }
    else if(iBaseEntitySet_Check(obj))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GetHandle(obj);

        if(type == iBase_INTEGER)
        {
            PyObject *o = PyNumber_Int(data_obj);
            if(o == NULL)
                return NULL;
            iGeom_setEntSetIntData(self->instance->handle,set,self->base.handle,
                                   PyInt_AsLong(o),&err);
            Py_DECREF(o);
        }
        else if(type == iBase_DOUBLE)
        {
            PyObject *o = PyNumber_Float(data_obj);
            if(o == NULL)
                return NULL;
            iGeom_setEntSetDblData(self->instance->handle,set,self->base.handle,
                                   PyFloat_AsDouble(o),&err);
            Py_DECREF(o);
        }
        else if(type == iBase_ENTITY_HANDLE)
        {
            if(!iBaseEntity_Check(data_obj))
                return NULL;
            iGeom_setEntSetEHData(self->instance->handle,set,self->base.handle,
                                  iBaseEntity_GetHandle(data_obj),&err);
        }
        else /* iBase_BYTES */
        {
            PyObject *data_arr = PyArray_FROMANY(data_obj,NPY_BYTE,1,1,
                                                 NPY_C_CONTIGUOUS);
            if(data_arr == NULL)
                return NULL;

            char *data = PyArray_DATA(data_arr);
            int data_size = PyArray_SIZE(data_arr);
            iGeom_setEntSetData(self->instance->handle,set,self->base.handle,
                                data,data_size,&err);
            Py_DECREF(data_arr);
        }
    }
    else if(iBaseEntity_Check(obj))
    {
        iBase_EntityHandle entity = iBaseEntity_GetHandle(obj);

        if(type == iBase_INTEGER)
        {
            PyObject *o = PyNumber_Int(data_obj);
            if(o == NULL)
                return NULL;
            iGeom_setIntData(self->instance->handle,entity,self->base.handle,
                             PyInt_AsLong(o),&err);
            Py_DECREF(o);
        }
        else if(type == iBase_DOUBLE)
        {
            PyObject *o = PyNumber_Float(data_obj);
            if(o == NULL)
                return NULL;
            iGeom_setDblData(self->instance->handle,entity,self->base.handle,
                             PyFloat_AsDouble(o),&err);
            Py_DECREF(o);
        }
        else if(type == iBase_ENTITY_HANDLE)
        {
            if(!iBaseEntity_Check(data_obj))
                return NULL;
            iGeom_setEHData(self->instance->handle,entity,self->base.handle,
                            iBaseEntity_GetHandle(data_obj),&err);
        }
        else /* iBase_BYTES */
        {
            PyObject *data_arr = PyArray_FROMANY(data_obj,NPY_BYTE,1,1,
                                                 NPY_C_CONTIGUOUS);
            if(data_arr == NULL)
                return NULL;

            char *data = PyArray_DATA(data_arr);
            int data_size = PyArray_SIZE(data_arr);
            iGeom_setData(self->instance->handle,entity,self->base.handle,data,
                          data_size,&err);
            Py_DECREF(data_arr);
        }
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
iGeomTagObj_getData(iGeomTag_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","type",0};
    PyObject *obj;
    char typechar=0;
    int type;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|c",kwlist,&obj,&typechar))
        return NULL;

    if(typechar == 0)
    {
        /* infer the type of the data */
        iGeom_getTagType(self->instance->handle,self->base.handle,&type,&err);
        if(checkError(self->instance->handle,err))
            return NULL;
    }
    else
    {
        type = char_to_type(typechar);
        if(type == -1)
        {
            PyErr_SetString(PyExc_ValueError,"invalid type code");
            return NULL;
        }
    }

    PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        int ent_size = PyArray_SIZE(ents);
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        PyObject *ret = 0;

        if(type == iBase_INTEGER)
        {
            int *data=0;
            int alloc=0,size;

            iGeom_getIntArrData(self->instance->handle,entities,ent_size,
                                self->base.handle,&data,&alloc,&size,&err);
            if(!checkError(self->instance->handle,err))
            {
                npy_intp dims[] = {size};
                ret = PyArray_NewFromMalloc(1,dims,NPY_INT,data);
            }
        }
        else if(type == iBase_DOUBLE)
        {
            double *data=0;
            int alloc=0,size;

            iGeom_getDblArrData(self->instance->handle,entities,ent_size,
                                self->base.handle,&data,&alloc,&size,&err);
            if(!checkError(self->instance->handle,err))
            {
                npy_intp dims[] = {size};
                ret = PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,data);
            }
        }
        else if(type == iBase_ENTITY_HANDLE)
        {
            iBase_EntityHandle *data=0;
            int alloc=0,size;

            iGeom_getEHArrData(self->instance->handle,entities,ent_size,
                               self->base.handle,&data,&alloc,&size,&err);
            if(!checkError(self->instance->handle,err))
            {
                npy_intp dims[] = {size};
                ret = PyArray_NewFromMalloc(1,dims,NPY_IBASEENT,data);
            }
        }
        else /* iBase_BYTES */
        {
            char *data=0;
            int alloc=0,size;

            iGeom_getArrData(self->instance->handle,entities,ent_size,
                             self->base.handle,&data,&alloc,&size,&err);
            if(!checkError(self->instance->handle,err))
            {
                npy_intp dims[] = {size};
                ret = PyArray_NewFromMalloc(1,dims,NPY_BYTE,data);
            }
        }

        Py_DECREF(ents);
        return ret;
    }
    else if(iBaseEntitySet_Check(obj))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GetHandle(obj);

        if(type == iBase_INTEGER)
        {
            int data;
            iGeom_getEntSetIntData(self->instance->handle,set,
                                   self->base.handle,&data,&err);
            if(checkError(self->instance->handle,err))
                return NULL;
            return PyInt_FromLong(data);
        }
        else if(type == iBase_DOUBLE)
        {
            double data;
            iGeom_getEntSetDblData(self->instance->handle,set,
                                   self->base.handle,&data,&err);
            if(checkError(self->instance->handle,err))
                return NULL;
            return PyFloat_FromDouble(data);
        }
        else if(type == iBase_ENTITY_HANDLE)
        {
            iBaseEntity_Object *data = iBaseEntity_New();
            iGeom_getEntSetEHData(self->instance->handle,set,self->base.handle,
                                  &data->handle,&err);
            if(checkError(self->instance->handle,err))
            {
                Py_DECREF(data);
                return NULL;
            }
            return (PyObject*)data;
        }
        else /* iBase_BYTES */
        {
            char *data=0;
            int alloc=0,size;
            iGeom_getEntSetData(self->instance->handle,set,self->base.handle,
                                &data,&alloc,&size,&err);
            if(checkError(self->instance->handle,err))
                return NULL;
            npy_intp dims[] = {size};
            return PyArray_NewFromMalloc(1,dims,NPY_BYTE,data);
        }
    }
    else if(iBaseEntity_Check(obj))
    {
        iBase_EntityHandle entity = iBaseEntity_GetHandle(obj);

        if(type == iBase_INTEGER)
        {
            int data;
            iGeom_getIntData(self->instance->handle,entity,self->base.handle,
                             &data,&err);
            if(checkError(self->instance->handle,err))
                return NULL;
            return PyInt_FromLong(data);
        }
        else if(type == iBase_DOUBLE)
        {
            double data;
            iGeom_getDblData(self->instance->handle,entity,self->base.handle,
                             &data,&err);
            if(checkError(self->instance->handle,err))
                return NULL;
            return PyFloat_FromDouble(data);
        }
        else if(type == iBase_ENTITY_HANDLE)
        {
            iBaseEntity_Object *data = iBaseEntity_New();
            iGeom_getEHData(self->instance->handle,entity,self->base.handle,
                            &data->handle,&err);
            if(checkError(self->instance->handle,err))
            {
                Py_DECREF(data);
                return NULL;
            }
            return (PyObject*)data;
        }
        else /* iBase_BYTES */
        {
            char *data=0;
            int alloc=0,size;
            iGeom_getData(self->instance->handle,entity,self->base.handle,&data,
                          &alloc,&size,&err);
            if(checkError(self->instance->handle,err))
                return NULL;
            npy_intp dims[] = {size};
            return PyArray_NewFromMalloc(1,dims,NPY_BYTE,data);
        }
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }
}

static PyObject *
iGeomTagObj_remove(iGeomTag_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    PyObject *obj;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&obj))
        return NULL;

    PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        int ent_size = PyArray_SIZE(ents);
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        iGeom_rmvArrTag(self->instance->handle,entities,ent_size,
                        self->base.handle,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntitySet_Check(obj))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GetHandle(obj);
        iGeom_rmvEntSetTag(self->instance->handle,set,self->base.handle,&err);
    }
    else if(iBaseEntity_Check(obj))
    {
        iBase_EntityHandle entity = iBaseEntity_GetHandle(obj);
        iGeom_rmvTag(self->instance->handle,entity,self->base.handle,&err);
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
iGeomTagObj_repr(iGeomTag_Object *self)
{
    char name[512];
    int err;
    iGeom_getTagName(self->instance->handle,self->base.handle,name,&err,
                     sizeof(name));
    if(checkError(self->instance->handle,err))
    {
        PyErr_Clear();
        return PyString_FromFormat("<itaps.iGeom.Tag %p>",self->base.handle);
    }
    else
    {
        return PyString_FromFormat("<itaps.iGeom.Tag '%s' %p>",name,
                                   self->base.handle);
    }
}

static PyObject *
iGeomTagObj_richcompare(iGeomTag_Object *lhs,
                        iGeomTag_Object *rhs,int op)
{
    if(!iGeomTag_Check(lhs) || !iGeomTag_Check(rhs))
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


static PyMethodDef iGeomTagObj_methods[] = {
    { "setData", (PyCFunction)iGeomTagObj_setData, METH_KEYWORDS,
      "Set tag values on an entity (or array/set of entities)"
    },
    { "getData", (PyCFunction)iGeomTagObj_getData, METH_KEYWORDS,
      "Get tag values on an entity (or array/set of entities)"
    },
    { "remove", (PyCFunction)iGeomTagObj_remove, METH_KEYWORDS,
      "Remove a tag value from an entity (or array/set of entities)"
    },
    {0}
};

static PyMemberDef iGeomTagObj_members[] = {
    {"instance", T_OBJECT_EX, offsetof(iGeomTag_Object, instance), READONLY,
     "base iGeom instance"},
    {0}
};

static PyGetSetDef iGeomTagObj_getset[] = {
    { "name", (getter)iGeomTagObj_getName, 0,
      "Get the name for a given tag handle", 0
    },
    { "sizeValues", (getter)iGeomTagObj_getSizeValues, 0,
      "Get size of a tag in units of numbers of tag data type", 0
    },
    { "sizeBytes", (getter)iGeomTagObj_getSizeBytes, 0,
      "Get size of a tag in units of bytes", 0
    },
    { "type", (getter)iGeomTagObj_getType, 0,
      "Get the data type of the specified tag handle", 0
    },
    {0}
};


static PyTypeObject iGeomTag_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iGeom.Tag",                        /* tp_name */
    sizeof(iGeomTag_Object),                  /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iGeomTagObj_dealloc,          /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc)iGeomTagObj_repr,               /* tp_repr */
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
    "iGeom tag object",                       /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iGeomTagObj_richcompare,     /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iGeomTagObj_methods,                      /* tp_methods */
    iGeomTagObj_members,                      /* tp_members */
    iGeomTagObj_getset,                       /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)iGeomTagObj_init,               /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};

