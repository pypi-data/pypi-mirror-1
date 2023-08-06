#define _IMESH_MODULE
#include "iMesh_Python.h"
#include "errors.h"
#include "common.h"
#include "helpers.h"
#include "numpy_extensions.h"

#include <numpy/ufuncobject.h>

static PyObject *CreateEnt_Type;

static enum iBase_TagValueType char_to_type(char c);
static char type_to_char(enum iBase_TagValueType t);

static PyTypeObject iMesh_Type;
static PyTypeObject iMeshIter_Type;
static PyTypeObject iMeshEntitySet_Type;
static int NPY_IMESHENTSET;
static PyTypeObject iMeshTag_Type;
static int NPY_IMESHTAG;

static int
checkError(iMesh_Instance mesh,int err)
{
    if(err)
    {
        char descr[120];
        int descr_err;
        iMesh_getDescription(mesh,descr,&descr_err,sizeof(descr)-1);
        if(descr_err)
            strncpy(descr,"Unable to retrieve error description",sizeof(descr));

        PyErr_SetString(PyExc_ITAPSError,descr);
        return 1;
    }
    else
        return 0;
}

static iMeshEntitySet_Object *
iMeshEntitySet_New(iMesh_Object *instance)
{
    iMeshEntitySet_Object *o = iMeshEntitySet_NewRaw();
    o->instance = instance;
    o->base.handle = NULL;
    Py_INCREF(o->instance);
    return o;
}

static iMeshTag_Object *
iMeshTag_New(iMesh_Object *instance)
{
    iMeshTag_Object *o = iMeshTag_NewRaw();
    o->instance = instance;
    o->base.handle = NULL;
    Py_INCREF(o->instance);
    return o;
}

static int
iMeshObj_init(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"options",0};
    const char *options = "";
    int err;

    if( !PyArg_ParseTupleAndKeywords(args,kw,"|s",kwlist,&options) )
        return -1;

    /* __init__ can be called multiple times, so destroy the old interface
       if necessary */
    if(self->handle)
    {
        iMesh_dtor(self->handle,&err);
        if(checkError(self->handle,err))
            return -1;
    }
    iMesh_newMesh(options,&self->handle,&err,strlen(options));
    if(checkError(self->handle,err))
        return -1;
    return 0;
}

static void
iMeshObj_dealloc(iMesh_Object *self)
{
    if(self->handle)
    {
        int err;
        iMesh_dtor(self->handle,&err);
    }
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iMeshObj_getRootSet(iMesh_Object *self,void *closure)
{
    iMeshEntitySet_Object *rootset = iMeshEntitySet_New(self);

    int err;
    iMesh_getRootSet(self->handle,&rootset->base.handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF((PyObject*)rootset);
        return NULL;
    }

    return (PyObject*)rootset;
}


static PyObject *
iMeshObj_getGeometricDimension(iMesh_Object *self,void *closure)
{
    int dim,err;
    iMesh_getGeometricDimension(self->handle,&dim,&err);
    if(checkError(self->handle,err))
        return NULL;

    return PyInt_FromLong(dim);
}

static int
iMeshObj_setGeometricDimension(iMesh_Object *self,PyObject *value,void *closure)
{
    if(value == NULL)
    {
        PyErr_SetString(PyExc_TypeError, 
                        "Cannot delete the geometricDimension attribute");
        return -1;
    }
  
    int dim,err;
    if(!PyArg_Parse(value,"i",&dim))
        return -1;
    iMesh_setGeometricDimension(self->handle,dim,&err);
    if(checkError(self->handle,err))
        return -1;

    return 0;
}

static PyObject *
iMeshObj_getDefaultStorage(iMesh_Object *self,void *closure)
{
    int order,err;
    iMesh_getDfltStorage(self->handle,&order,&err);
    if(checkError(self->handle,err))
        return NULL;

    return PyInt_FromLong(order);
}

static PyObject *
iMeshObj_getAdjTable(iMesh_Object *self,void *closure)
{
    int *adjtable=0;
    int alloc=0,size,err;

    iMesh_getAdjTable(self->handle,&adjtable,&alloc,&size,&err);
    if(checkError(self->handle,err))
        return NULL;

    npy_intp dims[] = {4,4};
    return PyArray_NewFromMalloc(2,dims,NPY_INT,adjtable);
}

static PyObject *
iMeshObj_areEHValid(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"reset",0};
    int reset,invariant,err;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&reset))
        return NULL;

    iMesh_areEHValid(self->handle,reset,&invariant,&err);
    if(checkError(self->handle,err))
        return NULL;

    return PyInt_FromLong(invariant);
}

static PyObject *
iMeshObj_getVtxCoords(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","storage_order",0};
    PyObject *obj;
    int storage_order=-1;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|i",kwlist,&obj,&storage_order))
        return NULL;

    PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        if(storage_order == -1)
        {
            Py_DECREF(ents);
            PyErr_SetString(PyExc_ValueError,ERR_STORAGE_ORDER);
            return NULL;
        }

        int size;
        double *coords=0;
        int coords_alloc=0,coords_size;

        size = PyArray_SIZE(ents);
        iBase_EntityHandle *data = PyArray_DATA(ents);

        iMesh_getVtxArrCoords(self->handle,data,size,storage_order,&coords,
                              &coords_alloc,&coords_size,&err);
        Py_DECREF(ents);

        if(checkError(self->handle,err))
            return NULL;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = 3;
        dims[!vec_index] = coords_size/3;
        return PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,coords);
    }
    else if(iBaseEntity_Check(obj))
    {
        double *v = malloc(3*sizeof(double));
        iMesh_getVtxCoord(self->handle,iBaseEntity_GetHandle(obj), v+0,v+1,v+2,
                          &err);
        if(checkError(self->handle,err))
        {
            free(v);
            return NULL;
        }

        npy_intp dims[] = {3};
        return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,v);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iMeshObj_getEntTopo(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    PyObject *obj;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&obj))
        return NULL;

    PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        int size;
        iBase_EntityHandle *data;
        int *topos=0;
        int topo_alloc=0,topo_size;

        size = PyArray_SIZE(ents);
        data = PyArray_DATA(ents);

        iMesh_getEntArrTopo(self->handle,data,size,&topos,&topo_alloc,
                            &topo_size,&err);
        Py_DECREF(ents);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {topo_size};
        return PyArray_NewFromMalloc(1,dims,NPY_UINT,topos);
    }
    else if(iBaseEntity_Check(obj))
    {
        int topo;
        iBase_EntityHandle handle = ((iBaseEntity_Object*)obj)->handle;

        iMesh_getEntTopo(self->handle,handle,&topo,&err);
        if(checkError(self->handle,err))
            return NULL;

        return PyInt_FromLong(topo);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iMeshObj_getEntType(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    PyObject *obj;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&obj))
        return NULL;

    PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        int size;
        iBase_EntityHandle *data;
        int *types=0;
        int type_alloc=0,type_size;

        size = PyArray_SIZE(ents);
        data = PyArray_DATA(ents);
      
        iMesh_getEntArrType(self->handle,data,size,&types,&type_alloc,
                            &type_size,&err);
        Py_DECREF(ents);
        if(checkError(self->handle,err))
            return NULL;
    
        npy_intp dims[] = {type_size};
        return PyArray_NewFromMalloc(1,dims,NPY_UINT,types);
    }
    else if(iBaseEntity_Check(obj))
    {
        int type;
        iBase_EntityHandle handle = ((iBaseEntity_Object*)obj)->handle;
        iMesh_getEntType(self->handle,handle,&type,&err);
        if(checkError(self->handle,err))
            return NULL;
    
        return PyInt_FromLong(type);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iMeshObj_getEntAdj(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","type",0};
    PyObject *obj;
    int type_req;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"Oi",kwlist,&obj,&type_req))
        return NULL;

    PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        int size;
        iBase_EntityHandle *data;
        iBase_EntityHandle *adj=NULL;
        int adj_alloc=0,adj_size;
        int *offsets=NULL;
        int offsets_alloc=0,offsets_size;
    
        size = PyArray_SIZE(ents);
        data = PyArray_DATA(ents);

        iMesh_getEntArrAdj(self->handle,data,size,type_req,&adj,&adj_alloc,
                           &adj_size,&offsets,&offsets_alloc,&offsets_size,
                           &err);
        Py_DECREF(ents);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp adj_dims[] = {adj_size};
        npy_intp off_dims[] = {offsets_size};

        return OffsetList_New(
            PyArray_NewFromMalloc(1,off_dims,NPY_INT,offsets),
            PyArray_NewFromMalloc(1,adj_dims,NPY_IBASEENT,adj)
            );

    }
    else if(iBaseEntity_Check(obj))
    {
        iBase_EntityHandle *adj=0;
        int adj_alloc=0,adj_size;
        iBase_EntityHandle handle = iBaseEntity_GetHandle(obj);

        iMesh_getEntAdj(self->handle,handle,type_req,&adj,&adj_alloc,&adj_size,
                        &err);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {adj_size};
        return PyArray_NewFromMalloc(1,dims,NPY_IBASEENT,adj);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iMeshObj_getEnt2ndAdj(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","bridge_type","type",0};
    PyObject *obj;
    int bridge_type,type_req;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"Oii",kwlist,&obj,&bridge_type,
                                    &type_req))
        return NULL;

    PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        int size;
        iBase_EntityHandle *data;
        iBase_EntityHandle *adj=0;
        int adj_alloc=0,adj_size;
        int *offsets;
        int offsets_alloc=0,offsets_size;

        size = PyArray_SIZE(ents);
        data = PyArray_DATA(ents);

        iMesh_getEntArr2ndAdj(self->handle,data,size,bridge_type,type_req,&adj,
                              &adj_alloc,&adj_size,&offsets,&offsets_alloc,
                              &offsets_size,&err);
        Py_DECREF(ents);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp adj_dims[] = {adj_size};
        npy_intp off_dims[] = {offsets_size};

        return OffsetList_New(
            PyArray_NewFromMalloc(1,off_dims,NPY_INT,offsets),
            PyArray_NewFromMalloc(1,adj_dims,NPY_IBASEENT,adj)
            );
    }
    else if(iBaseEntity_Check(obj))
    {
        iBase_EntityHandle *adj=0;
        int adj_alloc=0,adj_size;
        iBase_EntityHandle handle = iBaseEntity_GetHandle(obj);

        iMesh_getEnt2ndAdj(self->handle,handle,bridge_type,type_req,&adj,
                           &adj_alloc,&adj_size,&err);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {adj_size};
        return PyArray_NewFromMalloc(1,dims,NPY_IBASEENT,adj);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iMeshObj_createEntSet(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"ordered",0};
    int isList,err;
    PyObject *obj;
    iMeshEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&PyBool_Type,&obj))
        return NULL;

    set = iMeshEntitySet_New(self);

    isList = (obj == Py_True);
  
    iMesh_createEntSet(self->handle,isList,&set->base.handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF((PyObject*)set);
        return NULL;
    }

    return (PyObject*)set;  
}

static PyObject *
iMeshObj_destroyEntSet(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iMesh_destroyEntSet(self->handle,set->handle,&err);
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshObj_setVtxCoords(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order",0};
    PyObject *obj;
    int storage_order = -1;
    PyObject *data;
    PyObject *ents = 0;
    PyObject *verts = 0;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|i",kwlist,&obj,&data,
                                    &storage_order))
        return NULL;

    ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        if(storage_order == -1)
        {
            Py_DECREF(ents);
            PyErr_SetString(PyExc_ValueError,ERR_STORAGE_ORDER);
            goto err;
        }

        verts = PyArray_ToVectors(data,NPY_DOUBLE,2,3,
                                  storage_order==iBase_INTERLEAVED);
        if(verts == NULL)
            goto err;

        int ent_size = PyArray_SIZE(ents);
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int coord_size = PyArray_SIZE(verts);
        double *coords = PyArray_DATA(verts);

        iMesh_setVtxArrCoords(self->handle,entities,ent_size,storage_order,
                              coords,coord_size,&err);
        Py_DECREF(ents);
        Py_DECREF(verts);
    }
    else if(iBaseEntity_Check(obj))
    {
        verts = PyArray_ToVectors(data,NPY_DOUBLE,1,3,0);
        if(verts == NULL)
            goto err;

        double *v = PyArray_DATA(verts);
        iBase_EntityHandle entity = iBaseEntity_GetHandle(obj);

        iMesh_setVtxCoord(self->handle,entity, v[0],v[1],v[2], &err);
        Py_DECREF(verts);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iMeshObj_createVtx(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"coords","storage_order",0};
    int storage_order=-1;
    PyObject *data;
    PyObject *vertices;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|i",kwlist,&data,&storage_order))
        return NULL;

    if( (vertices = PyArray_TryFromObject(data,NPY_DOUBLE,2,2)) != NULL)
    {
        if(storage_order == -1)
        {
            Py_DECREF(vertices);
            PyErr_SetString(PyExc_ValueError,ERR_STORAGE_ORDER);
            return NULL;
        }

        int index = storage_order == iBase_BLOCKED;
        int count = PyArray_DIM(vertices,index); /* this is a bit odd! */
        int coord_size = PyArray_SIZE(vertices);
        double *coords = PyArray_DATA(vertices);
        iBase_EntityHandle *entities=0;
        int ent_alloc=0,ent_size;

        iMesh_createVtxArr(self->handle,count,storage_order,coords,coord_size,
                           &entities,&ent_alloc,&ent_size,&err);
        Py_DECREF(vertices);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {ent_size};
        return PyArray_NewFromMalloc(1,dims,NPY_IBASEENT,entities);
    }
    else if( (vertices = PyArray_TryFromObject(data,NPY_DOUBLE,1,1)) != NULL)
    {
        if(PyArray_SIZE(vertices) != 3)
        {
            Py_DECREF(vertices);
            PyErr_SetString(PyExc_ValueError,ERR_ARR_SIZE);
            return NULL;
        }

        double *v = PyArray_DATA(vertices);

        iBaseEntity_Object *entity = iBaseEntity_New();
        iMesh_createVtx(self->handle, v[0],v[1],v[2], &entity->handle,&err);
        Py_DECREF(vertices);

        if(checkError(self->handle,err))
        {
            Py_DECREF((PyObject*)entity);
            return NULL;
        }
        return (PyObject*)entity;
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ARR_DIMS);
        return NULL;
    }
}

static PyObject *
iMeshObj_createEnt(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"topo","entities",0};
    int topo,status,err;
    PyObject *obj;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"iO",kwlist,&topo,&obj))
        return NULL;

    PyObject *ents = PyArray_FROMANY(obj,NPY_IBASEENT,1,1,NPY_C_CONTIGUOUS);
    if(ents == NULL)
        return NULL;

    int lower_size = PyArray_SIZE(ents);
    iBase_EntityHandle *lower = PyArray_DATA(ents);

    iBaseEntity_Object *entity = iBaseEntity_New();

    iMesh_createEnt(self->handle,topo,lower,lower_size,&entity->handle,&status,
                    &err);
    Py_DECREF(ents);
    if(checkError(self->handle,err))
    {
        Py_DECREF((PyObject*)entity);
        return NULL;
    }

    return NamedTuple_New(CreateEnt_Type,"(Ni)",entity,status);
}

static PyObject *
iMeshObj_createEntArr(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"topo","entities",0};
    int topo,err;
    PyObject *obj;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"iO",kwlist,&topo,&obj))
        return NULL;

    PyObject *ents = PyArray_FROMANY(obj,NPY_IBASEENT,1,1,NPY_C_CONTIGUOUS);
    if(ents == NULL)
        return NULL;

    int lower_size = PyArray_SIZE(ents);
    iBase_EntityHandle *lower = PyArray_DATA(ents);

    iBase_EntityHandle *entities=0;
    int ent_alloc=0,ent_size;
    int *status;
    int stat_alloc=0,stat_size;

    iMesh_createEntArr(self->handle,topo,lower,lower_size,&entities,&ent_alloc,
                       &ent_size,&status,&stat_alloc,&stat_size,&err);
    Py_DECREF(ents);
    if(checkError(self->handle,err))
        return NULL;

    npy_intp ent_dims[] = {ent_size};
    npy_intp stat_dims[] = {stat_size};
    return NamedTuple_New(CreateEnt_Type,"(NN)",
        PyArray_NewFromMalloc(1,ent_dims,NPY_IBASEENT,entities),
        PyArray_NewFromMalloc(1,stat_dims,NPY_INT,status)
        );
}


static PyObject *
iMeshObj_deleteEnt(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    PyObject *obj;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&obj))
        return NULL;

    PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        int size = PyArray_SIZE(ents);
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        iMesh_deleteEntArr(self->handle,entities,size,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntity_Check(obj))
    {
        iBase_EntityHandle entity = iBaseEntity_GetHandle(obj);
        iMesh_deleteEnt(self->handle,entity,&err);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}


static PyObject *
iMeshObj_createTag(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"name","size","type",0};
    char *name;
    char typechar;
    int size,type,err;
    iMeshTag_Object *tag;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"sic",kwlist,&name,&size,&typechar))
        return NULL;

    type = char_to_type(typechar);
    if(type == -1)
    {
        PyErr_SetString(PyExc_ValueError,ERR_TYPE_CODE);
        return NULL;
    }

    tag = iMeshTag_New(self);

    iMesh_createTag(self->handle,name,size,type,&tag->base.handle,&err,
                    strlen(name));
    if(checkError(self->handle,err))
    {
        Py_DECREF((PyObject*)tag);
        return NULL;
    }

    return (PyObject*)tag;
}

static PyObject *
iMeshObj_destroyTag(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"tag","force",0};
    int forced,err;
    iBaseTag_Object *tag;
    PyObject *obj;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O!",kwlist,&iBaseTag_Type,&tag,
                                    &PyBool_Type,&obj))
        return NULL;

    forced = (obj == Py_True);

    iMesh_destroyTag(self->handle,tag->handle,forced,&err);
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshObj_getTagHandle(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"name",0};
    char *name;
    iMeshTag_Object *tag;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"s",kwlist,&name))
        return NULL;

    tag = iMeshTag_New(self);

    iMesh_getTagHandle(self->handle,name,&tag->base.handle,&err,strlen(name));
    if(checkError(self->handle,err))
    {
        Py_DECREF((PyObject*)tag);
        return NULL;
    }

    return (PyObject*)tag;
}

static PyObject *
iMeshObj_getAllTags(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    PyObject *ents;
    iBase_TagHandle *tags=0;
    int alloc=0,size;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&ents))
        return NULL;

    if(iBaseEntitySet_Check(ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GetHandle(ents);

        iMesh_getAllEntSetTags(self->handle,set,&tags,&alloc,&size,&err);
        if(checkError(self->handle,err))
            return NULL;
    }
    else if(iBaseEntity_Check(ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GetHandle(ents);

        iMesh_getAllTags(self->handle,entity,&tags,&alloc,&size,&err);
        if(checkError(self->handle,err))
            return NULL;
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTSET);
        return NULL;
    }

    npy_intp dims[] = {size};
    return PyArray_NewFromMallocBase(1,dims,NPY_IMESHTAG,tags,
                                     (PyObject*)self);
}


static PyMethodDef iMeshObj_methods[] = {
    { "areEHValid", (PyCFunction)iMeshObj_areEHValid, METH_KEYWORDS,
      "Return whether entity handles have changed since last reset or since "
      "instance construction"
    },
    { "getVtxCoords", (PyCFunction)iMeshObj_getVtxCoords, METH_KEYWORDS,
      "Get coordinates of specified vertex(ices)"
    },
    { "getEntTopo", (PyCFunction)iMeshObj_getEntTopo, METH_KEYWORDS,
      "Get the entity topology(ies) for the specified entity(ies)"
    },
    { "getEntType", (PyCFunction)iMeshObj_getEntType, METH_KEYWORDS,
      "Get the entity type(s) for the specified entity(ies)"
    },
    { "getEntAdj", (PyCFunction)iMeshObj_getEntAdj, METH_KEYWORDS,
      "Get entities of specified type adjacent to entity(ies)"
    },
    { "getEnt2ndAdj", (PyCFunction)iMeshObj_getEnt2ndAdj, METH_KEYWORDS,
      "Get \"2nd order\" adjacencies to entity(ies)"
    },
    { "createEntSet", (PyCFunction)iMeshObj_createEntSet, METH_KEYWORDS,
      "Create an entity set"
    },
    { "destroyEntSet", (PyCFunction)iMeshObj_destroyEntSet, METH_KEYWORDS,
      "Destroy an entity set"
    },
    { "setVtxCoords", (PyCFunction)iMeshObj_setVtxCoords, METH_KEYWORDS,
      "Set coordinates for a vertex or array of vertices"
    },
    { "createVtx", (PyCFunction)iMeshObj_createVtx, METH_KEYWORDS,
      "Create a new vertex or array of vertices at specified coordinates"
    },
    { "createEnt", (PyCFunction)iMeshObj_createEnt, METH_KEYWORDS,
      "Create a new entity with specified lower-order topology"
    },
    { "createEntArr", (PyCFunction)iMeshObj_createEntArr, METH_KEYWORDS,
      "Create an array of entities with specified lower-order topology"
    },
    { "deleteEnt", (PyCFunction)iMeshObj_deleteEnt, METH_KEYWORDS,
      "Delete specified entity(ies)"
    },
    { "createTag", (PyCFunction)iMeshObj_createTag, METH_KEYWORDS,
      "Create a tag with specified name, size, and type"
    },
    { "destroyTag", (PyCFunction)iMeshObj_destroyTag, METH_KEYWORDS,
      "Destroy a tag"
    },
    { "getTagHandle", (PyCFunction)iMeshObj_getTagHandle, METH_KEYWORDS,
      "Get the handle of an existing tag with the specified name"
    },
    { "getAllTags", (PyCFunction)iMeshObj_getAllTags, METH_KEYWORDS,
      "Get all the tags associated with a specified entity handle (or "
      "array/set of entities)"
    },
  {0}
};

static PyGetSetDef iMeshObj_getset[] = {
    { "rootSet", (getter)iMeshObj_getRootSet, 0,
      "Return the root set of the mesh", 0
    },
    { "geometricDimension", (getter)iMeshObj_getGeometricDimension,
      (setter)iMeshObj_setGeometricDimension,
      "Get/set the geometric dimension of the mesh", 0
    },
    { "defaultStorage",(getter)iMeshObj_getDefaultStorage, 0,
      "Return default storage order of the mesh", 0
    },
    { "adjTable",(getter)iMeshObj_getAdjTable, 0,
      "Return a table representing the relative cost of querying adjacencies", 0
    },
    {0}
};

static PyObject * iMeshObj_getAttr(PyObject *self,PyObject *attr_name)
{
    PyObject *ret;

    ret = PyObject_GenericGetAttr(self,attr_name);
    if(ret)
        return ret;
    else
    {
        PyErr_Clear();
        PyObject *root = iMeshObj_getRootSet((iMesh_Object*)self,0);
        if(!root)
            return NULL;
        ret = PyObject_GetAttr(root,attr_name);
        Py_DECREF(root);
        return ret;
    }
}

static PyTypeObject iMesh_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iMesh.Mesh",                       /* tp_name */
    sizeof(iMesh_Object),                     /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iMeshObj_dealloc,             /* tp_dealloc */
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
    iMeshObj_getAttr,                         /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "iMesh objects",                          /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iMeshObj_methods,                         /* tp_methods */
    0,                                        /* tp_members */
    iMeshObj_getset,                          /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)iMeshObj_init,                  /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};


static PyMethodDef module_methods[] = {
    {0}
};

static PyObject *
iMeshEntitySetArr_getitem(void *data,void *arr)
{
    PyObject *b = PyArray_BASE(arr);
    while(PyArray_Check(b))
        b = PyArray_BASE(b);
    if(!ArrDealloc_Check(b))
    {
        PyErr_SetString(PyExc_RuntimeError,ERR_ARR_BASE);
        return NULL;
    }

    ArrDealloc_Object *base = (ArrDealloc_Object*)b;
    iMesh_Object *instance = (iMesh_Object*)base->base;
    iMeshEntitySet_Object *o = iMeshEntitySet_New(instance);

    o->base.handle = *(iBase_EntitySetHandle*)data;

    return (PyObject*)o;
}

static int
iMeshEntitySetArr_setitem(PyObject *item,void *data,void *arr)
{
    if(!iBaseEntitySet_Check(item))
    {
        PyErr_SetString(PyExc_ValueError,ERR_ARR_TYPE);
        return -1;
    }

    PyObject *b = PyArray_BASE(arr);
    while(b != NULL && PyArray_Check(b))
        b = PyArray_BASE(b);
    if(b != NULL && !ArrDealloc_Check(b))
    {
        PyErr_SetString(PyExc_RuntimeError,ERR_ARR_BASE);
        return -1;
    }

    ArrDealloc_Object *base = (ArrDealloc_Object*)b;
    if(base == NULL)
    {
        if(!iMeshEntitySet_Check(item))
            return -1;
        base = ArrDealloc_New((PyObject*)iMeshEntitySet_GetInstance(item),0);
        PyArray_BASE(arr) = (PyObject*)base;
    }

    if(iMeshEntitySet_Check(item))
    {
        iMesh_Object *instance = (iMesh_Object*)base->base;
        if(iMeshEntitySet_GetInstance(item)->handle != instance->handle)
        {
            PyErr_SetString(PyExc_ValueError,ERR_ARR_INSTANCE);
            return -1;
        }
    }

    *(iBase_EntitySetHandle*)data = iBaseEntitySet_GetHandle(item);
    return 0;
}

static PyObject *
iMeshTagArr_getitem(void *data,void *arr)
{
    PyObject *b = PyArray_BASE(arr);
    while(PyArray_Check(b))
        b = PyArray_BASE(b);
    if(!ArrDealloc_Check(b))
    {
        PyErr_SetString(PyExc_RuntimeError,ERR_ARR_BASE);
        return NULL;
    }

    ArrDealloc_Object *base = (ArrDealloc_Object*)b;
    iMesh_Object *instance = (iMesh_Object*)base->base;
    iMeshTag_Object *o = iMeshTag_New(instance);

    o->base.handle = *(iBase_TagHandle*)data;

    return (PyObject*)o;
}

static int
iMeshTagArr_setitem(PyObject *item,void *data,void *arr)
{
    if(!iBaseTag_Check(item))
    {
        PyErr_SetString(PyExc_ValueError,ERR_ARR_TYPE);
        return -1;
    }

    PyObject *b = PyArray_BASE(arr);
    while(b != NULL && PyArray_Check(b))
        b = PyArray_BASE(b);
    if(b != NULL && !ArrDealloc_Check(b))
    {
        PyErr_SetString(PyExc_RuntimeError,ERR_ARR_BASE);
        return -1;
    }

    ArrDealloc_Object *base = (ArrDealloc_Object*)b;
    if(base == NULL)
    {
        if(!iMeshTag_Check(item))
            return -1;
        base = ArrDealloc_New((PyObject*)iMeshTag_GetInstance(item),0);
        PyArray_BASE(arr) = (PyObject*)base;
    }

    if(iMeshTag_Check(item))
    {
        iMesh_Object *instance = (iMesh_Object*)base->base;
        if(iMeshTag_GetInstance(item)->handle != instance->handle)
        {
            PyErr_SetString(PyExc_ValueError,ERR_ARR_INSTANCE);
            return -1;
        }
    }

    *(iBase_TagHandle*)data = iBaseTag_GetHandle(item);
    return 0;
}

static PyArray_ArrFuncs iMeshEntitySetArr_Funcs;
static int NPY_IMESHENTSET;

static PyArray_ArrFuncs iMeshTagArr_Funcs;
static int NPY_IMESHTAG;

ENUM_TYPE(iMeshTopology,"iMesh.Topology","");


PyMODINIT_FUNC initiMesh(void)
{
    PyObject *m;
    PyArray_Descr *descr;

    m = Py_InitModule("iMesh",module_methods);
    import_array();
    import_ufunc();
    import_iBase();
    import_helpers();

    /***** register C API *****/
    static void *IMesh_API[7];
    PyObject *api_obj;

    /* Initialize the C API pointer array */
    IMesh_API[0] = &iMesh_Type;
    IMesh_API[1] = &iMeshIter_Type;
    IMesh_API[2] = &iMeshEntitySet_Type;
    IMesh_API[3] = &NPY_IMESHENTSET;
    IMesh_API[4] = &iMeshTag_Type;
    IMesh_API[5] = &NPY_IMESHTAG;
    IMesh_API[6] = CreateEnt_Type;

    /* Create a CObject containing the API pointer array's address */
    api_obj = PyCObject_FromVoidPtr(IMesh_API,NULL);

    if(api_obj != NULL)
        PyModule_AddObject(m, "_C_API", api_obj);

    /***** acquire "equal" ufunc *****/
    PyObject *ops = PyArray_GetNumericOps();
    PyUFuncObject *ufunc = (PyUFuncObject*)PyDict_GetItemString(ops,"equal");
    Py_DECREF(ops);
    int types[3];

    REGISTER_CLASS_BASE(m,"Mesh",     iMesh,         iBase);
    REGISTER_CLASS_BASE(m,"EntitySet",iMeshEntitySet,iBaseEntitySet);
    REGISTER_CLASS_BASE(m,"Tag",      iMeshTag,      iBaseTag);
    REGISTER_CLASS     (m,"Iterator", iMeshIter);

    /***** initialize topology enum *****/
    REGISTER_CLASS(m,"Topology",iMeshTopology);

    ADD_ENUM(iMeshTopology,"point",         iMesh_POINT);
    ADD_ENUM(iMeshTopology,"line_segment",  iMesh_LINE_SEGMENT);
    ADD_ENUM(iMeshTopology,"polygon",       iMesh_POLYGON);
    ADD_ENUM(iMeshTopology,"triangle",      iMesh_TRIANGLE);
    ADD_ENUM(iMeshTopology,"quadrilateral", iMesh_QUADRILATERAL);
    ADD_ENUM(iMeshTopology,"polyhedron",    iMesh_POLYHEDRON);
    ADD_ENUM(iMeshTopology,"tetrahedron",   iMesh_TETRAHEDRON);
    ADD_ENUM(iMeshTopology,"hexahedron",    iMesh_HEXAHEDRON);
    ADD_ENUM(iMeshTopology,"prism",         iMesh_PRISM);
    ADD_ENUM(iMeshTopology,"pyramid",       iMesh_PYRAMID);
    ADD_ENUM(iMeshTopology,"septahedron",   iMesh_SEPTAHEDRON);
    ADD_ENUM(iMeshTopology,"all",           iMesh_ALL_TOPOLOGIES);

    /***** initialize iMeshEntitySet array *****/
    descr = PyArray_DescrNewFromType(NPY_IBASEENTSET);
    memcpy(&iMeshEntitySetArr_Funcs,descr->f,sizeof(PyArray_ArrFuncs));
    descr->f = &iMeshEntitySetArr_Funcs;

    descr->typeobj = &iMeshEntitySet_Type;
    descr->type = 'M';
    descr->f->getitem = iMeshEntitySetArr_getitem;
    descr->f->setitem = iMeshEntitySetArr_setitem;

    NPY_IMESHENTSET = PyArray_RegisterDataType(descr);
    PyModule_AddObject(m,"npy_entset",(PyObject*)descr);

    types[0] = types[1] = NPY_IMESHENTSET; types[2] = NPY_BOOL;
    PyUFunc_RegisterLoopForType(ufunc,NPY_IMESHENTSET,iBaseEntitySetArr_equal,
                                types,0);

    /***** initialize iMeshTag array *****/
    descr = PyArray_DescrNewFromType(NPY_IBASETAG);
    memcpy(&iMeshTagArr_Funcs,descr->f,sizeof(PyArray_ArrFuncs));
    descr->f = &iMeshTagArr_Funcs;

    descr->typeobj = &iMeshTag_Type;
    descr->type = 'M';
    descr->f->getitem = iMeshTagArr_getitem;
    descr->f->setitem = iMeshTagArr_setitem;

    NPY_IMESHTAG = PyArray_RegisterDataType(descr);
    PyModule_AddObject(m,"npy_tag",(PyObject*)descr);

    types[0] = types[1] = NPY_IMESHTAG; types[2] = NPY_BOOL;
    PyUFunc_RegisterLoopForType(ufunc,NPY_IMESHTAG,iBaseTagArr_equal,types,0);

    /***** create named tuple types *****/
    /* TODO: add this to the module dictionary and do error checking */
    CreateEnt_Type = NamedTuple_CreateType("create_ent","entity status");
}

/* Include source files so that everything is in one translation unit */
#include "iMesh_entSet.inl"
#include "iMesh_iter.inl"
#include "iMesh_tag.inl"
