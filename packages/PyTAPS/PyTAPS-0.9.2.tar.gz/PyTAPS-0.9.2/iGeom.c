#define _IGEOM_MODULE
#include "iGeom_Python.h"
#include "errors.h"
#include "common.h"
#include "helpers.h"
#include "numpy_extensions.h"

#include <numpy/ufuncobject.h>

static enum iBase_TagValueType char_to_type(char c);
static char type_to_char(enum iBase_TagValueType t);

static PyObject *NormalPl_Type;
static PyObject *FaceEval_Type;
static PyObject *EdgeEval_Type;
static PyObject *Deriv1st_Type;
static PyObject *Deriv2nd_Type;
static PyObject *Intersect_Type;
static PyObject *Tolerance_Type;

static int
get_dimension(enum iGeomExt_Basis basis)
{
    switch(basis)
    {
    case iGeomExt_XYZ:
        return 3;
    case iGeomExt_UV:
        return 2;
    case iGeomExt_U:
        return 1;
    default:
        return -1;
    }
}

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
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return 0;
    }
    return 1;
}

static PyTypeObject iGeom_Type;
static PyTypeObject iGeomIter_Type;
static PyTypeObject iGeomEntitySet_Type;
static int NPY_IGEOMENTSET;
static PyTypeObject iGeomTag_Type;
static int NPY_IGEOMTAG;

static int
checkError(iGeom_Instance geom,int err)
{
    if(err)
    {
        char descr[120];
        int descr_err;
        iGeom_getDescription(geom,descr,&descr_err,sizeof(descr)-1);

        PyErr_SetString(PyExc_ITAPSError,descr);
        return 1;
    }
    else
        return 0;
}

static enum iGeomExt_Basis
infer_basis(iGeom_Instance instance,iBase_EntityHandle entity)
{
    int type,err;
    iGeom_getEntType(instance,entity,&type,&err);
    if(checkError(instance,err))
        return -1;

    if(type == iBase_EDGE)
        return iGeomExt_U;
    else if(type == iBase_FACE)
        return iGeomExt_UV;

    /* TODO: error message */
    return -1;
}

static iGeomEntitySet_Object *
iGeomEntitySet_New(iGeom_Object *instance)
{
    iGeomEntitySet_Object *o = iGeomEntitySet_NewRaw();
    o->instance = instance;
    o->base.handle = NULL;
    Py_INCREF(o->instance);
    return o;
}

static iGeomTag_Object *
iGeomTag_New(iGeom_Object *instance)
{
    iGeomTag_Object *o = iGeomTag_NewRaw();
    o->instance = instance;
    o->base.handle = NULL;
    Py_INCREF(o->instance);
    return o;
}

static int
iGeomObj_init(iGeom_Object *self,PyObject *args,PyObject *kw)
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
        iGeom_dtor(self->handle,&err);
        if(checkError(self->handle,err))
            return -1;
    }
    iGeom_newGeom(options,&self->handle,&err,strlen(options));
    if(checkError(self->handle,err))
        return -1;
    return 0;
}

static void
iGeomObj_dealloc(iGeom_Object *self)
{
    if(self->handle)
    {
        int err;
        iGeom_dtor(self->handle,&err);
    }
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iGeomObj_load(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"filename","options",0};
    const char *name = 0;
    const char *options = "";

    if(!PyArg_ParseTupleAndKeywords(args,kw,"s|s",kwlist,&name,&options))
        return NULL;

    int err;
    iGeom_load(self->handle,name,options,&err,strlen(name),strlen(options));
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_save(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"filename","options",0};
    const char *name = 0;
    const char *options = "";

    if(!PyArg_ParseTupleAndKeywords(args,kw,"s|s",kwlist,&name,&options))
        return NULL;

    int err;
    iGeom_save(self->handle,name,options,&err,strlen(name),strlen(options));
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_getRootSet(iGeom_Object *self,void *closure)
{
    iGeomEntitySet_Object *rootset = iGeomEntitySet_New(self);

    int err;
    iGeom_getRootSet(self->handle,&rootset->base.handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF((PyObject*)rootset);
        return NULL;
    }

    return (PyObject*)rootset;
}

static PyObject *
iGeomObj_getBoundBox(iGeom_Object *self,void *closure)
{
    double *box;
    int err;

    box = malloc(sizeof(double)*6);
    iGeom_getBoundBox(self->handle,box+0,box+1,box+2,box+3,box+4,box+5,&err);
    if(checkError(self->handle,err))
    {
        free(box);
        return NULL;
    }

    npy_intp dims[] = {2,3};
    return PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,box);
}

static PyObject *
iGeomObj_getEntType(iGeom_Object *self,PyObject *args,PyObject *kw)
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
      
        iGeom_getArrType(self->handle,data,size,&types,&type_alloc,
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
        iGeom_getEntType(self->handle,handle,&type,&err);
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
iGeomObj_getEntAdj(iGeom_Object *self,PyObject *args,PyObject *kw)
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

        iGeom_getArrAdj(self->handle,data,size,type_req,&adj,&adj_alloc,
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

        iGeom_getEntAdj(self->handle,handle,type_req,&adj,&adj_alloc,&adj_size,
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
iGeomObj_getEnt2ndAdj(iGeom_Object *self,PyObject *args,PyObject *kw)
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

        iGeom_getArr2ndAdj(self->handle,data,size,bridge_type,type_req,&adj,
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

        iGeom_getEnt2ndAdj(self->handle,handle,bridge_type,type_req,&adj,
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
iGeomObj_isEntAdj(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities1","entities2",0};
    PyObject *obj1;
    PyObject *obj2;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO",kwlist,&obj1,&obj2))
        return NULL;

    PyObject *ents1 = NULL;
    iBase_EntityHandle *entities1 = NULL;
    int ent1_size = 0;
    PyObject *ents2 = NULL;
    iBase_EntityHandle *entities2 = NULL;
    int ent2_size = 0;

    if(!get_entity_data(obj1,&ents1,&entities1,&ent1_size))
        goto err;
    if(!get_entity_data(obj2,&ents2,&entities2,&ent2_size))
        goto err;

    if(ents1 || ents2)
    {
        int *adj=0;
        int adj_alloc=0,adj_size;

        iGeom_isArrAdj(self->handle,entities1,ent1_size,entities2,ent2_size,
                       &adj,&adj_alloc,&adj_size,&err);
        Py_XDECREF(ents1);
        Py_XDECREF(ents2);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {adj_size};
        npy_intp strides[] = {sizeof(int)/sizeof(npy_bool)};
        return PyArray_NewFromMallocStrided(1,dims,strides,NPY_BOOL,adj);
    }
    else
    {
        int adj;

        iGeom_isEntAdj(self->handle,entities1[0],entities2[0],&adj,&err);
        if(checkError(self->handle,err))
            return NULL;

        return PyBool_FromLong(adj);
    }
err:
    Py_XDECREF(ents1);
    Py_XDECREF(ents2);
    return NULL;
}

static PyObject *
iGeomObj_getTopoLevel(iGeom_Object *self,void *closure)
{
    int level,err;
    iGeom_getTopoLevel(self->handle,&level,&err);
    if(checkError(self->handle,err))
        return NULL;

    return PyInt_FromLong(level);
}

static PyObject *
iGeomObj_getEntClosestPt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order",0};

    PyObject *obj;
    PyObject *vert_obj;
    int storage_order=-1;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|i",kwlist,&obj,&vert_obj,
                                    &storage_order))
        return NULL;

    PyObject *ents = NULL;
    PyObject *verts = NULL;
    iBase_EntityHandle *entities = NULL;
    int ent_size = 0;

    if(!get_entity_data(obj,&ents,&entities,&ent_size))
        goto err;

    if((verts = PyArray_TryFromObject(vert_obj,NPY_DOUBLE,1,2)) == NULL)
    {
        PyErr_SetString(PyExc_ValueError,ERR_ARR_DIMS);
        goto err;
    }
    int coord_size = PyArray_SIZE(verts);
    double *coords = PyArray_DATA(verts);

    if(ents || PyArray_NDIM(verts) == 2)
    {
        if(storage_order == -1)
        {
            PyErr_SetString(PyExc_ValueError,ERR_STORAGE_ORDER);
            goto err;
        }
        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,3,
           storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,3,0))
            goto err;

        double *on_coords;
        int on_alloc=0,on_size;
        iGeom_getArrClosestPt(self->handle,entities,ent_size,storage_order,
                              coords,coord_size,&on_coords,&on_alloc,&on_size,
                              &err);
        Py_XDECREF(ents);
        Py_DECREF(verts);
        if(checkError(self->handle,err))
            return NULL;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = 3;
        dims[!vec_index] = on_size/3;
        return PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,on_coords);
    }
    else
    {
        if(!PyArray_CheckVectors(verts,1,3,0))
            goto err;

        double *on_coords = malloc(sizeof(double)*3);

        iGeom_getEntClosestPt(self->handle,entities[0],
                              coords[0],coords[1],coords[2],
                              on_coords+0,on_coords+1,on_coords+2,&err);
        Py_DECREF(verts);
        if(checkError(self->handle,err))
        {
            free(on_coords);
            return NULL;
        }

        npy_intp dims[] = {3};
        return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,on_coords);
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iGeomObj_getEntNormal(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order","basis",0};

    PyObject *obj;
    PyObject *vert_obj;
    enum iGeomExt_Basis basis = iGeomExt_XYZ;
    int storage_order = -1;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|ii",kwlist,&obj,&vert_obj,
                                    &storage_order,&basis))
        return NULL;

    if(basis == iGeomExt_U)
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_BASIS);
        return NULL;
    }

    PyObject *ents = NULL;
    PyObject *verts = NULL;
    iBase_EntityHandle *entities = NULL;
    int ent_size = 0;

    if(!get_entity_data(obj,&ents,&entities,&ent_size))
        goto err;

    if((verts = PyArray_TryFromObject(vert_obj,NPY_DOUBLE,1,2)) == NULL)
    {
        PyErr_SetString(PyExc_ValueError,ERR_ARR_DIMS);
        goto err;
    }
    int coord_size = PyArray_SIZE(verts);
    double *coords = PyArray_DATA(verts);

    if(ents || PyArray_NDIM(verts) == 2)
    {
        if(storage_order == -1)
        {
            PyErr_SetString(PyExc_ValueError,ERR_STORAGE_ORDER);
            goto err;
        }
        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,
           get_dimension(basis),storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,
           get_dimension(basis),0))
            goto err;

        double *normals = 0;
        int norm_alloc = 0,norm_size;

        if(basis == iGeomExt_XYZ)
            iGeom_getArrNrmlXYZ(self->handle,entities,ent_size,storage_order,
                                coords,coord_size,
                                &normals,&norm_alloc,&norm_size,&err);
        else
            iGeom_getArrNrmlUV(self->handle,entities,ent_size,storage_order,
                               coords,coord_size,
                               &normals,&norm_alloc,&norm_size,&err);
        Py_XDECREF(ents);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
            goto err;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = 3;
        dims[!vec_index] = norm_size/3;
        return PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,normals);
    }
    else
    {
        if(!PyArray_CheckVectors(verts,1,get_dimension(basis),0))
            goto err;

        double *normal = malloc(3*sizeof(double));

        if(basis == iGeomExt_XYZ)
            iGeom_getEntNrmlXYZ(self->handle,entities[0],
                                coords[0],coords[1],coords[2],
                                normal+0,normal+1,normal+2,&err);
        else
            iGeom_getEntNrmlUV(self->handle,entities[0],
                               coords[0],coords[1],
                               normal+0,normal+1,normal+2,&err);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
        {
            free(normal);
            goto err;
        }

        npy_intp dims[] = {3};
        return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,normal);
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iGeomObj_getEntNormalPl(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order",0};

    PyObject *obj;
    PyObject *vert_obj;
    int storage_order = -1;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|i",kwlist,&obj,&vert_obj,
                                    &storage_order))
        return NULL;

    PyObject *ents = NULL;
    PyObject *verts = NULL;
    iBase_EntityHandle *entities = NULL;
    int ent_size = 0;

    if(!get_entity_data(obj,&ents,&entities,&ent_size))
        goto err;

    if((verts = PyArray_TryFromObject(vert_obj,NPY_DOUBLE,1,2)) == NULL)
    {
        PyErr_SetString(PyExc_ValueError,ERR_ARR_DIMS);
        goto err;
    }
    int coord_size = PyArray_SIZE(verts);
    double *coords = PyArray_DATA(verts);

    if(ents || PyArray_NDIM(verts) == 2)
    {
        if(storage_order == -1)
        {
            PyErr_SetString(PyExc_ValueError,ERR_STORAGE_ORDER);
            goto err;
        }
        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,3,
           storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,3,0))
            goto err;

        double *points = 0;
        int pts_alloc = 0,pts_size;
        double *normals = 0;
        int norm_alloc = 0,norm_size;

        iGeom_getArrNrmlPlXYZ(self->handle,entities,ent_size,storage_order,
                              coords,coord_size,
                              &points,&pts_alloc,&pts_size,
                              &normals,&norm_alloc,&norm_size,&err);
                              
        Py_XDECREF(ents);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
            goto err;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = 3;
        dims[!vec_index] = norm_size/3;
        return NamedTuple_New(NormalPl_Type,"(NN)",
            PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,points),
            PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,normals)
            );
    }
    else
    {
        if(!PyArray_CheckVectors(verts,1,3,0))
            goto err;

        double *point  = malloc(3*sizeof(double));
        double *normal = malloc(3*sizeof(double));

        iGeom_getEntNrmlPlXYZ(self->handle,entities[0],
                              coords[0],coords[1],coords[2],
                              point+0,point+1,point+2,
                              normal+0,normal+1,normal+2,&err);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
        {
            free(point);
            free(normal);
            goto err;
        }

        npy_intp dims[] = {3};
        return NamedTuple_New(NormalPl_Type,"(NN)",
            PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,point),
            PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,normal)
            );
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iGeomObj_getEntTangent(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order","basis",0};

    PyObject *obj;
    PyObject *vert_obj;
    enum iGeomExt_Basis basis = iGeomExt_XYZ;
    int storage_order = -1;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|ii",kwlist,&obj,&vert_obj,
                                    &storage_order,&basis))
        return NULL;

    if(basis == iGeomExt_UV)
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_BASIS);
        return NULL;
    }

    PyObject *ents = NULL;
    PyObject *verts = NULL;
    iBase_EntityHandle *entities = NULL;
    int ent_size = 0;

    if(!get_entity_data(obj,&ents,&entities,&ent_size))
        goto err;

    if((verts = PyArray_TryFromObject(vert_obj,NPY_DOUBLE,1,2)) == NULL)
    {
        PyErr_SetString(PyExc_ValueError,ERR_ARR_DIMS);
        goto err;
    }
    int coord_size = PyArray_SIZE(verts);
    double *coords = PyArray_DATA(verts);

    if(ents || PyArray_NDIM(verts) == 2)
    {
        if(storage_order == -1)
        {
            PyErr_SetString(PyExc_ValueError,ERR_STORAGE_ORDER);
            goto err;
        }
        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,
           get_dimension(basis),storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,
           get_dimension(basis),0))
            goto err;

        double *tangents = 0;
        int tan_alloc = 0,tan_size;

        if(basis == iGeomExt_XYZ)
            iGeom_getArrTgntXYZ(self->handle,entities,ent_size,storage_order,
                                coords,coord_size,
                                &tangents,&tan_alloc,&tan_size,&err);
        else
            iGeom_getArrTgntU(self->handle,entities,ent_size,storage_order,
                              coords,coord_size,
                              &tangents,&tan_alloc,&tan_size,&err);
        Py_XDECREF(ents);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
            goto err;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = 3;
        dims[!vec_index] = tan_size/3;
        return PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,tangents);
    }
    else
    {
        if(!PyArray_CheckVectors(verts,1,get_dimension(basis),0))
            goto err;

        double *tangent = malloc(3*sizeof(double));

        if(basis == iGeomExt_XYZ)
            iGeom_getEntTgntXYZ(self->handle,entities[0],
                                coords[0],coords[1],coords[2],
                                tangent+0,tangent+1,tangent+2,&err);
        else
            iGeom_getEntTgntU(self->handle,entities[0],coords[0],
                              tangent+0,tangent+1,tangent+2,&err);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
        {
            free(tangent);
            goto err;
        }

        npy_intp dims[] = {3};
        return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,tangent);
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iGeomObj_getEnt1stDerivative(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order",0};
    PyObject *obj;
    PyObject *data;
    int storage_order = -1;
    PyObject *ents = 0;
    PyObject *pts = 0;
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

        pts = PyArray_ToVectors(data,NPY_DOUBLE,2,2,
                                storage_order==iBase_INTERLEAVED);
        if(pts == NULL)
            goto err;

        int ent_size = PyArray_SIZE(ents);
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int uv_size = PyArray_SIZE(pts);
        double *uv = PyArray_DATA(pts);

        double *u_deriv=NULL;
        int u_deriv_alloc=0,u_deriv_size;
        double *v_deriv=NULL;
        int v_deriv_alloc=0,v_deriv_size;
        int *u_offsets=NULL;
        int u_offsets_alloc=0,u_offsets_size;
        int *v_offsets=NULL;
        int v_offsets_alloc=0,v_offsets_size;

        iGeom_getArr1stDrvt(self->handle,entities,ent_size,storage_order,
                            uv,uv_size,
                            &u_deriv,&u_deriv_alloc,&u_deriv_size,
                            &u_offsets,&u_offsets_alloc,&u_offsets_size,
                            &v_deriv,&v_deriv_alloc,&v_deriv_size,
                            &v_offsets,&v_offsets_alloc,&v_offsets_size,&err);
        Py_DECREF(ents);
        Py_DECREF(pts);

        if(checkError(self->handle,err))
            return NULL;
        free(v_offsets); /* Not needed */

        /* calculate the dimensions of the output array */
        npy_intp off_dims[] = {u_offsets_size};
        npy_intp uv_dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        uv_dims[ vec_index] = 3;
        uv_dims[!vec_index] = u_deriv_size/3;

        return OffsetList_New(
            PyArray_NewFromMalloc(1,off_dims,NPY_INT,u_offsets),
            NamedTuple_New(Deriv1st_Type,"(NN)",
                PyArray_NewFromMalloc(2,uv_dims,NPY_DOUBLE,u_deriv),
                PyArray_NewFromMalloc(2,uv_dims,NPY_DOUBLE,v_deriv)
                )
            );
    }
    else if(iBaseEntity_Check(obj))
    {
        pts = PyArray_ToVectors(data,NPY_DOUBLE,1,2,0);
        if(pts == NULL)
            goto err;

        double *uv = PyArray_DATA(pts);
        iBase_EntityHandle entity = iBaseEntity_GetHandle(obj);

        double *u_deriv=NULL;
        int u_deriv_alloc=0,u_deriv_size;
        double *v_deriv=NULL;
        int v_deriv_alloc=0,v_deriv_size;

        iGeom_getEnt1stDrvt(self->handle,entity,uv[0],uv[1],
                            &u_deriv,&u_deriv_alloc,&u_deriv_size,
                            &v_deriv,&v_deriv_alloc,&v_deriv_size,&err);
        Py_DECREF(pts);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp uv_dims[] = {u_deriv_size};
        return NamedTuple_New(Deriv1st_Type,"(NN)",
            PyArray_NewFromMalloc(1,uv_dims,NPY_DOUBLE,u_deriv),
            PyArray_NewFromMalloc(1,uv_dims,NPY_DOUBLE,v_deriv)
            );
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(pts);
    return NULL;
}

static PyObject *
iGeomObj_getEnt2ndDerivative(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order",0};
    PyObject *obj;
    PyObject *data;
    int storage_order = -1;
    PyObject *ents = 0;
    PyObject *pts = 0;
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

        pts = PyArray_ToVectors(data,NPY_DOUBLE,2,2,
                                storage_order==iBase_INTERLEAVED);
        if(pts == NULL)
            goto err;

        int ent_size = PyArray_SIZE(ents);
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int uv_size = PyArray_SIZE(pts);
        double *uv = PyArray_DATA(pts);

        double *uu_deriv=NULL;
        int uu_deriv_alloc=0,uu_deriv_size;
        double *vv_deriv=NULL;
        int vv_deriv_alloc=0,vv_deriv_size;
        double *uv_deriv=NULL;
        int uv_deriv_alloc=0,uv_deriv_size;
        int *uu_offsets=NULL;
        int uu_offsets_alloc=0,uu_offsets_size;
        int *vv_offsets=NULL;
        int vv_offsets_alloc=0,vv_offsets_size;
        int *uv_offsets=NULL;
        int uv_offsets_alloc=0,uv_offsets_size;

        iGeom_getArr2ndDrvt(self->handle,entities,ent_size,storage_order,
                            uv,uv_size,
                            &uu_deriv,&uu_deriv_alloc,&uu_deriv_size,
                            &uu_offsets,&uu_offsets_alloc,&uu_offsets_size,
                            &vv_deriv,&vv_deriv_alloc,&vv_deriv_size,
                            &vv_offsets,&vv_offsets_alloc,&vv_offsets_size,
                            &uv_deriv,&uv_deriv_alloc,&uv_deriv_size,
                            &uv_offsets,&uv_offsets_alloc,&uv_offsets_size,
                            &err);
        Py_DECREF(ents);
        Py_DECREF(pts);

        if(checkError(self->handle,err))
            return NULL;
        free(vv_offsets); free(uv_offsets); /* Not needed */

        /* calculate the dimensions of the output array */
        npy_intp off_dims[] = {uu_offsets_size};
        npy_intp uv_dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        uv_dims[ vec_index] = 3;
        uv_dims[!vec_index] = uu_deriv_size/3;

        return OffsetList_New(
            PyArray_NewFromMalloc(1,off_dims,NPY_INT,uu_offsets),
            NamedTuple_New(Deriv2nd_Type,"(NNN)",
                PyArray_NewFromMalloc(2,uv_dims,NPY_DOUBLE,uu_deriv),
                PyArray_NewFromMalloc(2,uv_dims,NPY_DOUBLE,vv_deriv),
                PyArray_NewFromMalloc(2,uv_dims,NPY_DOUBLE,uv_deriv)
                )
            );
    }
    else if(iBaseEntity_Check(obj))
    {
        pts = PyArray_ToVectors(data,NPY_DOUBLE,1,2,0);
        if(pts == NULL)
            goto err;

        double *uv = PyArray_DATA(pts);
        iBase_EntityHandle entity = iBaseEntity_GetHandle(obj);

        double *uu_deriv=NULL;
        int uu_deriv_alloc=0,uu_deriv_size;
        double *vv_deriv=NULL;
        int vv_deriv_alloc=0,vv_deriv_size;
        double *uv_deriv=NULL;
        int uv_deriv_alloc=0,uv_deriv_size;

        iGeom_getEnt2ndDrvt(self->handle,entity,uv[0],uv[1],
                            &uu_deriv,&uu_deriv_alloc,&uu_deriv_size,
                            &vv_deriv,&vv_deriv_alloc,&vv_deriv_size,
                            &uv_deriv,&uv_deriv_alloc,&uv_deriv_size,&err);
        Py_DECREF(pts);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp uv_dims[] = {uu_deriv_size};
        return NamedTuple_New(Deriv2nd_Type,"(NNN)",
            PyArray_NewFromMalloc(1,uv_dims,NPY_DOUBLE,uu_deriv),
            PyArray_NewFromMalloc(1,uv_dims,NPY_DOUBLE,vv_deriv),
            PyArray_NewFromMalloc(1,uv_dims,NPY_DOUBLE,uv_deriv)
            );
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(pts);
    return NULL;
}

static PyObject *
iGeomObj_getEntCurvature(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order","basis",
                             "type",0};

    PyObject *obj;
    PyObject *vert_obj;
    enum iGeomExt_Basis basis = iGeomExt_XYZ;
    int storage_order = -1;
    int type = -1;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|iii",kwlist,&obj,&vert_obj,
                                    &storage_order,&basis,&type))
        return NULL;

    if(basis == iGeomExt_U) /* Not currently supported */
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_BASIS);
        return NULL;
    }

    PyObject *ents = NULL;
    PyObject *verts = NULL;
    iBase_EntityHandle *entities = NULL;
    int ent_size = 0;

    if(!get_entity_data(obj,&ents,&entities,&ent_size))
        goto err;

    if((verts = PyArray_TryFromObject(vert_obj,NPY_DOUBLE,1,2)) == NULL)
    {
        PyErr_SetString(PyExc_ValueError,ERR_ARR_DIMS);
        goto err;
    }
    int coord_size = PyArray_SIZE(verts);
    double *coords = PyArray_DATA(verts);

    if(type == -1) /* deduce entity type */
    {
        iGeom_getEntType(self->handle,entities[0],&type,&err);
        if(checkError(self->handle,err))
            goto err;
    }

    if(ents || PyArray_NDIM(verts) == 2)
    {
        if(storage_order == -1)
        {
            PyErr_SetString(PyExc_ValueError,ERR_STORAGE_ORDER);
            goto err;
        }
        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,
           get_dimension(basis),storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,
           get_dimension(basis),0))
            goto err;

        double *curv1 = 0;
        int curv1_alloc = 0,curv1_size;
        double *curv2 = 0;
        int curv2_alloc = 0,curv2_size;

        if(basis == iGeomExt_XYZ)
            iGeom_getEntArrCvtrXYZ(self->handle,entities,ent_size,storage_order,
                                   coords,coord_size,
                                   &curv1,&curv1_alloc,&curv1_size,
                                   &curv2,&curv2_alloc,&curv2_size,&err);
        else if(type == iBase_FACE)
            iGeom_getFcArrCvtrUV(self->handle,entities,ent_size,storage_order,
                                 coords,coord_size,
                                 &curv1,&curv1_alloc,&curv1_size,
                                 &curv2,&curv2_alloc,&curv2_size,&err);
        else
        {
            PyErr_SetString(PyExc_ValueError,ERR_ENT_TYPE);
            goto err;
        }

        Py_XDECREF(ents);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
            goto err;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = 3;
        dims[!vec_index] = curv1_size/3;
        if(curv2_size != 0)
            return Py_BuildValue("(NN)",
                PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,curv1),
                PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,curv2)
                );
        else
            return PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,curv1);
    }
    else
    {
        if(!PyArray_CheckVectors(verts,1,get_dimension(basis),0))
            goto err;

        if(type == iBase_FACE)
        {
            double *curv1 = malloc(3*sizeof(double));
            double *curv2 = malloc(3*sizeof(double));

            if(basis == iGeomExt_XYZ)
                iGeom_getFcCvtrXYZ(self->handle,entities[0],
                                   coords[0],coords[1],coords[2],
                                   curv1+0,curv1+1,curv1+2,
                                   curv2+0,curv2+1,curv2+2,&err);
            else
                iGeom_getFcCvtrUV(self->handle,entities[0],
                                  coords[0],coords[1],
                                  curv1+0,curv1+1,curv1+2,
                                  curv2+0,curv2+1,curv2+2,&err);
            Py_DECREF(verts);

            if(checkError(self->handle,err))
            {
                free(curv1);
                free(curv2);
                goto err;
            }

            npy_intp dims[] = {3};
            return Py_BuildValue("(NN)",
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,curv1),
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,curv2)
                );
        }
        else if(type == iBase_EDGE)
        {
            if(basis != iGeomExt_XYZ) /* not currently supported */
            {
                PyErr_SetString(PyExc_ValueError,ERR_INVALID_BASIS);
                goto err;
            }

            double *curv = malloc(3*sizeof(double));

            iGeom_getEgCvtrXYZ(self->handle,entities[0],
                               coords[0],coords[1],coords[2],
                               curv+0,curv+1,curv+2,&err);
            Py_DECREF(verts);

            if(checkError(self->handle,err))
            {
                free(curv);
                goto err;
            }

            npy_intp dims[] = {3};
            return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,curv);
        }
        else
        {
            PyErr_SetString(PyExc_ValueError,ERR_ENT_TYPE);
            goto err;
        }
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iGeomObj_getEntEval(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order","type",0};

    PyObject *obj;
    PyObject *vert_obj;
    int storage_order = -1;
    int type = -1;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|ii",kwlist,&obj,&vert_obj,
                                    &storage_order,&type))
        return NULL;

    PyObject *ents = NULL;
    PyObject *verts = NULL;
    iBase_EntityHandle *entities = NULL;
    int ent_size = 0;

    if(!get_entity_data(obj,&ents,&entities,&ent_size))
        goto err;

    if((verts = PyArray_TryFromObject(vert_obj,NPY_DOUBLE,1,2)) == NULL)
    {
        PyErr_SetString(PyExc_ValueError,ERR_ARR_DIMS);
        goto err;
    }
    int coord_size = PyArray_SIZE(verts);
    double *coords = PyArray_DATA(verts);

    if(type == -1) /* deduce entity type */
    {
        iGeom_getEntType(self->handle,entities[0],&type,&err);
        if(checkError(self->handle,err))
            goto err;
    }

    if(ents || PyArray_NDIM(verts) == 2)
    {
        if(storage_order == -1)
        {
            PyErr_SetString(PyExc_ValueError,ERR_STORAGE_ORDER);
            goto err;
        }

        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,3,
           storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,3,0))
            goto err;

        if(type == iBase_FACE)
        {
            double *points = 0;
            int pts_alloc = 0,pts_size;
            double *normals = 0;
            int norm_alloc = 0,norm_size;
            double *curv1 = 0;
            int curv1_alloc = 0,curv1_size;
            double *curv2 = 0;
            int curv2_alloc = 0,curv2_size;

            iGeom_getArrFcEvalXYZ(self->handle,entities,ent_size,storage_order,
                                  coords,coord_size,
                                  &points,&pts_alloc,&pts_size,
                                  &normals,&norm_alloc,&norm_size,
                                  &curv1,&curv1_alloc,&curv1_size,
                                  &curv2,&curv2_alloc,&curv2_size,&err);
            Py_XDECREF(ents);
            Py_DECREF(verts);

            if(checkError(self->handle,err))
                goto err;

            /* calculate the dimensions of the output array */
            npy_intp dims[2];
            int vec_index = storage_order != iBase_BLOCKED;
            dims[ vec_index] = 3;
            dims[!vec_index] = pts_size/3;
            return NamedTuple_New(FaceEval_Type,"(NNNN)",
                PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,points),
                PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,normals),
                PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,curv1),
                PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,curv2)
                );
        }
        else if(type == iBase_EDGE)
        {
            double *points = 0;
            int pts_alloc = 0,pts_size;
            double *tangents = 0;
            int tan_alloc = 0,tan_size;
            double *curv = 0;
            int curv_alloc = 0,curv_size;

            iGeom_getArrEgEvalXYZ(self->handle,entities,ent_size,storage_order,
                                  coords,coord_size,
                                  &points,&pts_alloc,&pts_size,
                                  &tangents,&tan_alloc,&tan_size,
                                  &curv,&curv_alloc,&curv_size,&err);
            Py_XDECREF(ents);
            Py_DECREF(verts);

            if(checkError(self->handle,err))
                goto err;

            /* calculate the dimensions of the output array */
            npy_intp dims[2];
            int vec_index = storage_order != iBase_BLOCKED;
            dims[ vec_index] = 3;
            dims[!vec_index] = pts_size/3;
            return NamedTuple_New(EdgeEval_Type,"(NNN)",
                PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,points),
                PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,tangents),
                PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,curv)
                );
        }
        else
        {
            PyErr_SetString(PyExc_ValueError,ERR_ENT_TYPE);
            goto err;
        }
    }
    else
    {
        if(!PyArray_CheckVectors(verts,1,3,0))
            goto err;

        if(type == iBase_FACE)
        {
            double *point  = malloc(3*sizeof(double));
            double *normal = malloc(3*sizeof(double));
            double *curv1  = malloc(3*sizeof(double));
            double *curv2  = malloc(3*sizeof(double));

            iGeom_getFcEvalXYZ(self->handle,entities[0],
                               coords[0],coords[1],coords[2],
                               point+0,  point+1,  point+2,
                               normal+0, normal+1, normal+2,
                               curv1+0,  curv1+1,  curv1+2,
                               curv2+0,  curv2+1,  curv2+2, &err);
            Py_DECREF(verts);

            if(checkError(self->handle,err))
            {
                free(point);
                free(normal);
                free(curv1);
                free(curv2);
                goto err;
            }

            npy_intp dims[] = {3};
            return NamedTuple_New(FaceEval_Type,"(NNNN)",
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,point),
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,normal),
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,curv1),
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,curv2)
                );
        }
        else if(type == iBase_EDGE)
        {
            double *point   = malloc(3*sizeof(double));
            double *tangent = malloc(3*sizeof(double));
            double *curv    = malloc(3*sizeof(double));

            iGeom_getEgEvalXYZ(self->handle,entities[0],
                               coords[0],coords[1],coords[2],
                               point+0,  point+1,  point+2,
                               tangent+0,tangent+1,tangent+2,
                               curv+0,   curv+1,   curv+2, &err);
            Py_DECREF(verts);

            if(checkError(self->handle,err))
            {
                free(point);
                free(tangent);
                free(curv);
                goto err;
            }

            npy_intp dims[] = {3};
            return NamedTuple_New(EdgeEval_Type,"(NNN)",
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,point),
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,tangent),
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,curv)
                );
        }
        else
        {
            PyErr_SetString(PyExc_ValueError,ERR_ENT_TYPE);
            goto err;
        }
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iGeomObj_getEntBoundBox(iGeom_Object *self,PyObject *args,PyObject *kw)
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
        size = PyArray_SIZE(ents);
        iBase_EntityHandle *data = PyArray_DATA(ents);

        /* XXX: this is one of the only places that I malloc an array myself */
        double *min = malloc(6*sizeof(double)*size);
        double *max = min + 3*size;
        int min_alloc = 3*sizeof(double)*size, min_size;
        int max_alloc = min_alloc, max_size;

        iGeom_getArrBoundBox(self->handle,data,size,storage_order,
                             &min,&min_alloc,&min_size,
                             &max,&max_alloc,&max_size,&err);
        Py_DECREF(ents);

        if(checkError(self->handle,err))
        {
            free(min);
            return NULL;
        }

        /* calculate the dimensions of the output array */
        npy_intp dims[3] = {2};
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index+1] = 3;
        dims[!vec_index+1] = min_size/3;
        return PyArray_NewFromMalloc(3,dims,NPY_DOUBLE,min);
    }
    else if(iBaseEntity_Check(obj))
    {
        double *v = malloc(6*sizeof(double));
        iGeom_getEntBoundBox(self->handle,iBaseEntity_GetHandle(obj),
                             v+0,v+1,v+2,v+3,v+4,v+5, &err);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {2,3};
        return PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,v);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_getVtxCoords(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"src","storage_order","dest",0};

    PyObject *src_obj = 0;
    PyObject *dst_obj = 0;
    enum iGeomExt_Basis dst_basis = -1;
    int storage_order = -1;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|iO",kwlist,&src_obj,
                                    &storage_order,&dst_obj))
        return NULL;
    if(dst_obj && PyTuple_Check(dst_obj))
    {
        if(!PyArg_ParseTuple(dst_obj,"Oi",&dst_obj,&dst_basis))
            return NULL;
    }

    PyObject *src_ents = 0;
    PyObject *dst_ents = 0;

    iBase_EntityHandle *src_entities = NULL;
    int src_size = 0;
    iBase_EntityHandle *dst_entities = NULL;
    int dst_size = 0;

    if(!get_entity_data(src_obj,&src_ents,&src_entities,&src_size))
        goto err;

    if(dst_obj)
    {
        if(!get_entity_data(dst_obj,&dst_ents,&dst_entities,&dst_size))
            goto err;

        if(dst_basis == -1 && (dst_basis = infer_basis(self->handle,
           dst_entities[0])) == -1)
            goto err;
    }
    else
        dst_basis = iGeomExt_XYZ;


    if(src_ents || dst_ents)
    {
        if(storage_order == -1 && dst_basis != iGeomExt_U)
        {
            PyErr_SetString(PyExc_ValueError,ERR_STORAGE_ORDER);
            goto err;
        }

        double *coords=0;
        int coords_alloc=0,coords_size;

        if(dst_basis == iGeomExt_XYZ)
            iGeom_getVtxArrCoords(self->handle,src_entities,src_size,
                                  storage_order,&coords,&coords_alloc,
                                  &coords_size,&err);
        else if(dst_basis == iGeomExt_UV)
            iGeom_getVtxArrToUV(self->handle,src_entities,src_size,dst_entities,
                                dst_size,storage_order,&coords,&coords_alloc,
                                &coords_size,&err);
        else /* iGeomExt_U */
            iGeom_getVtxArrToU(self->handle,src_entities,src_size,dst_entities,
                               dst_size,&coords,&coords_alloc,&coords_size,
                               &err);

        Py_XDECREF(src_ents);
        Py_XDECREF(dst_ents);

        if(checkError(self->handle,err))
            return NULL;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = get_dimension(dst_basis);
        dims[!vec_index] = coords_size/get_dimension(dst_basis);
        return PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,coords);
    }
    else
    {
        double *v = malloc(get_dimension(dst_basis)*sizeof(double));

        if(dst_basis == iGeomExt_XYZ)
            iGeom_getVtxCoord(self->handle,src_entities[0],v+0,v+1,v+2,&err);
        else if(dst_basis == iGeomExt_UV)
            iGeom_getVtxToUV(self->handle,src_entities[0],dst_entities[0],
                             v+0,v+1,&err);
        else /* iGeomExt_U */
            iGeom_getVtxToU(self->handle,src_entities[0],dst_entities[0],v+0,
                            &err);

        if(checkError(self->handle,err))
        {
            free(v);
            return NULL;
        }

        npy_intp dims[] = {get_dimension(dst_basis)};
        return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,v);
    }

err:
    Py_XDECREF(src_ents);
    Py_XDECREF(dst_ents);
    return NULL;
}

static PyObject *
iGeomObj_getPtRayIntersect(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"points","vectors","storage_order",0};
    PyObject *obj1;
    PyObject *obj2;
    PyObject *points  = 0;
    PyObject *vectors = 0;
    int storage_order;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OOi",kwlist,&obj1,&obj2,
                                    &storage_order))
        return NULL;

    if((points = PyArray_ToVectors(obj1,NPY_DOUBLE,2,3,
                                   storage_order==iBase_INTERLEAVED)) != NULL)
    {
        vectors = PyArray_ToVectors(obj2,NPY_DOUBLE,2,3,
                                    storage_order==iBase_INTERLEAVED);
        if(vectors == NULL)
            goto err;

        double *coords  = PyArray_DATA(points);
        int coords_size = PyArray_SIZE(points);
        double *dirs    = PyArray_DATA(vectors);
        int dirs_size   = PyArray_SIZE(vectors);

        iBase_EntityHandle *entities = NULL;
        int ent_alloc = 0,ent_size;
        int *offsets = NULL;
        int off_alloc = 0,off_size;
        double *isect = NULL;
        int isect_alloc = 0,isect_size;
        double *param = NULL;
        int param_alloc = 0,param_size;

        iGeom_getPntArrRayIntsct(self->handle,storage_order,
                                 coords,coords_size,dirs,dirs_size,
                                 &entities,&ent_alloc,  &ent_size,
                                 &offsets, &off_alloc,  &off_size,
                                 &isect,   &isect_alloc,&isect_size,
                                 &param,   &param_alloc,&param_size, &err);
        Py_DECREF(points);
        Py_DECREF(vectors);

        if(checkError(self->handle,err))
            goto err;

        /* calculate the dimensions of the output arrays */
        npy_intp off_dims[] = {off_size};
        npy_intp ent_dims[] = {ent_size};
        npy_intp coord_dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        coord_dims[ vec_index] = 3;
        coord_dims[!vec_index] = isect_size/3;
        npy_intp param_dims[] = {param_size};

        return OffsetList_New(
            PyArray_NewFromMalloc(1,off_dims,NPY_INT,offsets),
            NamedTuple_New(Intersect_Type,"(NNN)",
                PyArray_NewFromMalloc(1,ent_dims,NPY_IBASEENT,entities),
                PyArray_NewFromMalloc(2,coord_dims,NPY_DOUBLE,isect),
                PyArray_NewFromMalloc(1,param_dims,NPY_DOUBLE,param)
                )
            );
    }
    else if((points = PyArray_ToVectors(obj1,NPY_DOUBLE,1,3,0)) != NULL)
    {
        vectors = PyArray_ToVectors(obj2,NPY_DOUBLE,1,3,0);
        if(vectors == NULL)
            goto err;

        double *coords = PyArray_DATA(points);
        double *dirs   = PyArray_DATA(vectors);

        iBase_EntityHandle *entities = 0;
        int ent_alloc = 0,ent_size;
        double *isect = 0;
        int isect_alloc = 0,isect_size;
        double *param = 0;
        int param_alloc = 0,param_size;

        iGeom_getPntRayIntsct(self->handle,coords[0],coords[1],coords[2],
                              dirs[0],dirs[1],dirs[2],
                              &entities,&ent_alloc,  &ent_size,   storage_order,
                              &isect,   &isect_alloc,&isect_size,
                              &param,   &param_alloc,&param_size, &err);
        Py_DECREF(points);
        Py_DECREF(vectors);
        if(checkError(self->handle,err))
            goto err;

        /* calculate the dimensions of the output array */
        npy_intp ent_dims[] = {ent_size};
        npy_intp coord_dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        coord_dims[ vec_index] = 3;
        coord_dims[!vec_index] = isect_size/3;
        return NamedTuple_New(Intersect_Type,"(NNN)",
            PyArray_NewFromMalloc(1,ent_dims,NPY_IBASEENT,entities),
            PyArray_NewFromMalloc(2,coord_dims,NPY_DOUBLE,isect),
            PyArray_NewFromMalloc(2,coord_dims,NPY_DOUBLE,param)
            );
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ARR_DIMS);
        return NULL;
    }
err:
    Py_XDECREF(points);
    Py_XDECREF(vectors);
    return NULL;
}

/* TODO: rename */
static PyObject *
iGeomObj_getPtClass(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"points","storage_order",0};
    PyObject *obj;
    PyObject *points = 0;
    int storage_order = -1;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|i",kwlist,&obj,&storage_order))
        return NULL;

    if((points = PyArray_ToVectors(obj,NPY_DOUBLE,2,3,1)) != NULL)
    {
        if(storage_order == -1)
        {
            Py_DECREF(points);
            PyErr_SetString(PyExc_ValueError,ERR_STORAGE_ORDER);
            return NULL;
        }

        double *coords  = PyArray_DATA(points);
        int coords_size = PyArray_SIZE(points);

        iBase_EntityHandle *entities = 0;
        int ent_alloc = 0,ent_size;

        iGeom_getPntArrClsf(self->handle,storage_order,coords,coords_size,
                            &entities,&ent_alloc,&ent_size,&err);
        Py_DECREF(points);

        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {ent_size};
        return PyArray_NewFromMalloc(1,dims,NPY_IBASEENT,entities);
    }
    else if((points = PyArray_ToVectors(obj,NPY_DOUBLE,1,3,0)) != NULL)
    {
        double *coords = PyArray_DATA(points);

        iBaseEntity_Object *entity = iBaseEntity_New();
        iGeom_getPntClsf(self->handle,coords[0],coords[1],coords[2],
                         &entity->handle,&err);
        Py_DECREF(points);

        if(checkError(self->handle,err))
        {
            Py_DECREF(entity);
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
iGeomObj_getEntNormalSense(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"faces","regions",0};
    PyObject *obj1;
    PyObject *obj2;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO",kwlist,&obj1,&obj2))
        return NULL;

    PyObject *ents1 = NULL;
    iBase_EntityHandle *entities1 = NULL;
    int ent1_size = 0;
    PyObject *ents2 = NULL;
    iBase_EntityHandle *entities2 = NULL;
    int ent2_size = 0;

    if(!get_entity_data(obj1,&ents1,&entities1,&ent1_size))
        goto err;
    if(!get_entity_data(obj2,&ents2,&entities2,&ent2_size))
        goto err;

    if(ents1 || ents2)
    {
        int *sense=0;
        int sense_alloc=0,sense_size;

        iGeom_getArrNrmlSense(self->handle,entities1,ent1_size,entities2,
                              ent2_size,&sense,&sense_alloc,&sense_size,&err);
        Py_XDECREF(ents1);
        Py_XDECREF(ents2);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {sense_size};
        return PyArray_NewFromMalloc(1,dims,NPY_INT,sense);
    }
    else
    {
        int sense;
        iGeom_getEntNrmlSense(self->handle,entities1[0],entities2[0],&sense,
                              &err);
        if(checkError(self->handle,err))
            return NULL;
        return PyInt_FromLong(sense);
    }
err:
    Py_XDECREF(ents1);
    Py_XDECREF(ents2);
    return NULL;
}

static PyObject *
iGeomObj_getEgFcSense(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"edges","faces",0};
    PyObject *obj1;
    PyObject *obj2;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO",kwlist,&obj1,&obj2))
        return NULL;

    PyObject *ents1 = NULL;
    iBase_EntityHandle *entities1 = NULL;
    int ent1_size = 0;
    PyObject *ents2 = NULL;
    iBase_EntityHandle *entities2 = NULL;
    int ent2_size = 0;

    if(!get_entity_data(obj1,&ents1,&entities1,&ent1_size))
        goto err;
    if(!get_entity_data(obj2,&ents2,&entities2,&ent2_size))
        goto err;

    if(ents1 || ents2)
    {
        int *sense=0;
        int sense_alloc=0,sense_size;

        iGeom_getEgFcArrSense(self->handle,entities1,ent1_size,entities2,
                              ent2_size,&sense,&sense_alloc,&sense_size,&err);
        Py_XDECREF(ents1);
        Py_XDECREF(ents2);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {sense_size};
        return PyArray_NewFromMalloc(1,dims,NPY_INT,sense);
    }
    else
    {
        int sense;
        iGeom_getEgFcSense(self->handle,entities1[0],entities2[0],&sense,&err);
        if(checkError(self->handle,err))
            return NULL;
        return PyInt_FromLong(sense);
    }
err:
    Py_XDECREF(ents1);
    Py_XDECREF(ents2);
    return NULL;
}

static PyObject *
iGeomObj_getEgVtxSense(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"edges","vertices1","vertices2",0};
    PyObject *obj1;
    PyObject *obj2;
    PyObject *obj3;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OOO",kwlist,&obj1,&obj2,&obj3))
        return NULL;

    PyObject *ents1 = NULL;
    iBase_EntityHandle *entities1 = NULL;
    int ent1_size = 0;
    PyObject *ents2 = NULL;
    iBase_EntityHandle *entities2 = NULL;
    int ent2_size = 0;
    PyObject *ents3 = NULL;
    iBase_EntityHandle *entities3 = NULL;
    int ent3_size = 0;

    if(!get_entity_data(obj1,&ents1,&entities1,&ent1_size))
        goto err;
    if(!get_entity_data(obj2,&ents2,&entities2,&ent2_size))
        goto err;
    if(!get_entity_data(obj3,&ents3,&entities3,&ent3_size))
        goto err;

    if(ents1 || ents2 || ents3)
    {
        int *sense=0;
        int sense_alloc=0,sense_size;

        iGeom_getEgVtxArrSense(self->handle,entities1,ent1_size,entities2,
                               ent2_size,entities3,ent3_size,&sense,
                               &sense_alloc,&sense_size,&err);
        Py_XDECREF(ents1);
        Py_XDECREF(ents2);
        Py_XDECREF(ents3);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {sense_size};
        return PyArray_NewFromMalloc(1,dims,NPY_INT,sense);
    }
    else
    {
        int sense;
        iGeom_getEgVtxSense(self->handle,entities1[0],entities2[0],
                            entities3[0],&sense,&err);
        if(checkError(self->handle,err))
            return NULL;
        return PyInt_FromLong(sense);
    }
err:
    Py_XDECREF(ents1);
    Py_XDECREF(ents2);
    Py_XDECREF(ents3);
    return NULL;
}

static PyObject *
iGeomObj_measure(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    PyObject *obj;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&obj))
        return NULL;

    PyObject *ents = PyArray_FROMANY(obj,NPY_IBASEENT,1,1,NPY_C_CONTIGUOUS);
    if(ents == NULL)
        return NULL;

    int ent_size = PyArray_SIZE(ents);
    iBase_EntityHandle *entities = PyArray_DATA(ents);

    double *measures = 0;
    int meas_alloc = 0,meas_size;

    iGeom_measure(self->handle,entities,ent_size,&measures,&meas_alloc,
                  &meas_size,&err);
    Py_DECREF(ents);

    if(checkError(self->handle,err))
        return NULL;

    npy_intp dims[] = {meas_size};
    return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,measures);
}

static PyObject *
iGeomObj_getFaceType(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity",0};
    iBaseEntity_Object *entity;
    char type[512];
    int len = sizeof(type);
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntity_Type,
                                    &entity))
        return NULL;

    iGeom_getFaceType(self->handle,entity->handle,type,&err,&len);
    if(checkError(self->handle,err))
        return NULL;
    return PyString_FromString(type);
}

static PyObject *
iGeomObj_getParametric(iGeom_Object *self,void *closure)
{
    int parametric,err;

    iGeom_getParametric(self->handle,&parametric,&err);
    if(checkError(self->handle,err))
        return NULL;
    return PyBool_FromLong(parametric);
}

static PyObject *
iGeomObj_isEntParametric(iGeom_Object *self,PyObject *args,PyObject *kw)
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
        iBase_EntityHandle *data = PyArray_DATA(ents);

        int *param=0;
        int param_alloc=0,param_size;

        iGeom_isArrParametric(self->handle,data,size,&param,&param_alloc,
                              &param_size,&err);
        Py_DECREF(ents);

        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {param_size};
        npy_intp strides[] = {sizeof(int)/sizeof(npy_bool)};
        return PyArray_NewFromMallocStrided(1,dims,strides,NPY_BOOL,param);
    }
    else if(iBaseEntity_Check(obj))
    {
        int param;
        iGeom_isEntParametric(self->handle,iBaseEntity_GetHandle(obj),&param,
                              &err);
        if(checkError(self->handle,err))
            return NULL;
        return PyBool_FromLong(param);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_getEntCoords(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    /* TODO: add hint */
    static char *kwlist[] = {"coords","storage_order","src","dest",0};

    PyObject *vert_obj;
    PyObject *src_obj = 0;
    PyObject *dst_obj = 0;
    enum iGeomExt_Basis src_basis = -1;
    enum iGeomExt_Basis dst_basis = -1;
    int storage_order = -1;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|iOO",kwlist,&vert_obj,
                                    &storage_order,&src_obj,&dst_obj))
        return NULL;

    /***** 1: parse src/dest *****/
    if(src_obj == NULL && dst_obj == NULL)
    {
        /* TODO: better error */
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_BASIS);
        return NULL;
    }

    if(src_obj && PyTuple_Check(src_obj))
    {
        if(!PyArg_ParseTuple(src_obj,"Oi",&src_obj,&src_basis))
            return NULL;
    }
    if(dst_obj && PyTuple_Check(dst_obj))
    {
        if(!PyArg_ParseTuple(dst_obj,"Oi",&dst_obj,&dst_basis))
            return NULL;
    }

    /***** 2: extract verts/entities *****/
    PyObject *verts;
    PyObject *src_ents = 0;
    PyObject *dst_ents = 0;

    iBase_EntityHandle *src_entities = NULL;
    int src_size = 0;
    iBase_EntityHandle *dst_entities = NULL;
    int dst_size = 0;

    if((verts = PyArray_TryFromObject(vert_obj,NPY_DOUBLE,1,2)) == NULL)
    {
        PyErr_SetString(PyExc_ValueError,ERR_ARR_DIMS);
        return NULL;
    }

    double *src_coords = PyArray_DATA(verts);
    int src_coord_size = PyArray_SIZE(verts);

    if(src_obj)
    {
        if(!get_entity_data(src_obj,&src_ents,&src_entities,&src_size))
            goto err;

        if(src_basis == -1 && (src_basis = infer_basis(self->handle,
           src_entities[0])) == -1)
            goto err;
    }
    else
        src_basis = iGeomExt_XYZ;

    if(dst_obj)
    {
        if(!get_entity_data(dst_obj,&dst_ents,&dst_entities,&dst_size))
            goto err;

        if(dst_basis == -1 && (dst_basis = infer_basis(self->handle,
           dst_entities[0])) == -1)
            goto err;
    }
    else
        dst_basis = iGeomExt_XYZ;

    if(src_basis == dst_basis)
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_BASIS);
        return NULL;
    }

    /***** 3: determine which form to use (array vs. single) *****/
    if(PyArray_NDIM(verts) == 2 || src_ents || dst_ents)
    {
        /***** 4a: validate vertex data *****/
        if(storage_order == -1)
        {
            PyErr_SetString(PyExc_ValueError,ERR_STORAGE_ORDER);
            goto err;
        }
        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,
           get_dimension(src_basis),storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,
           get_dimension(src_basis),0))
            goto err;

        double *dst_coords = 0;
        int dst_coord_alloc = 0,dst_coord_size=0;

        /***** 5a: find and call the appropriate function *****/
        if(src_basis == iGeomExt_XYZ)
        {
            if(dst_basis == iGeomExt_UV)
                iGeom_getArrXYZtoUV(self->handle,dst_entities,dst_size,
                                    storage_order,src_coords,src_coord_size,
                                    &dst_coords,&dst_coord_alloc,
                                    &dst_coord_size,&err);
            else /* iGeomExt_U */
                iGeom_getArrXYZtoU(self->handle,dst_entities,dst_size,
                                   storage_order,src_coords,src_coord_size,
                                   &dst_coords,&dst_coord_alloc,
                                   &dst_coord_size,&err);
        }
        else if(src_basis == iGeomExt_UV)
        {
            if(dst_basis == iGeomExt_XYZ)
                iGeom_getArrUVtoXYZ(self->handle,src_entities,src_size,
                                    storage_order,src_coords,src_coord_size,
                                    &dst_coords,&dst_coord_alloc,
                                    &dst_coord_size,&err);
            else /* iGeomExt_U */
            {
                goto err; /* not currently supported */
            }
        }
        else /* iGeomExt_U */
        {
            if(dst_basis == iGeomExt_XYZ)
                iGeom_getArrUtoXYZ(self->handle,src_entities,src_size,
                                   src_coords,src_coord_size,storage_order,
                                   &dst_coords,&dst_coord_alloc,
                                   &dst_coord_size,&err);
            else /* iGeomExt_UV */
                iGeom_getArrUtoUV(self->handle,src_entities,src_size,
                                  dst_entities,dst_size,
                                  src_coords,src_coord_size,storage_order,
                                  &dst_coords,&dst_coord_alloc,
                                  &dst_coord_size,&err);
        }
        Py_DECREF(verts);
        Py_XDECREF(src_ents);
        Py_XDECREF(dst_ents);

        if(checkError(self->handle,err))
            return NULL;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = get_dimension(dst_basis);
        dims[!vec_index] = dst_coord_size/get_dimension(dst_basis);
        return PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,dst_coords);
    }
    else
    {
        /***** 4b: validate vertex data *****/
        if(!PyArray_CheckVectors(verts,1,get_dimension(src_basis),0))
            goto err;

        double *dst_coords = malloc(get_dimension(dst_basis)*sizeof(double));

        /***** 5b: find and call the appropriate function *****/
        if(src_basis == iGeomExt_XYZ)
        {
            if(dst_basis == iGeomExt_UV)
                iGeom_getEntXYZtoUV(self->handle,dst_entities[0],
                                    src_coords[0],src_coords[1],src_coords[2],
                                    dst_coords+0, dst_coords+1,
                                    &err);
            else /* iGeomExt_U */
                iGeom_getEntXYZtoU(self->handle,dst_entities[0],
                                   src_coords[0],src_coords[1],src_coords[2],
                                   dst_coords+0,
                                   &err);
        }
        else if(src_basis == iGeomExt_UV)
        {
            if(dst_basis == iGeomExt_XYZ)
                iGeom_getEntUVtoXYZ(self->handle,src_entities[0],
                                    src_coords[0],src_coords[1],
                                    dst_coords+0, dst_coords+1, dst_coords+2,
                                    &err);
            else /* iGeomExt_U */
            {
                goto err; /* not currently supported */
            }
        }
        else /* iGeomExt_U */
        {
            if(dst_basis == iGeomExt_XYZ)
                iGeom_getEntUtoXYZ(self->handle,src_entities[0],
                                   src_coords[0],
                                   dst_coords+0, dst_coords+1, dst_coords+2,
                                   &err);
            else /* iGeomExt_UV */
                iGeom_getEntUtoUV(self->handle,src_entities[0],dst_entities[0],
                                  src_coords[0],
                                  dst_coords+0, dst_coords+1,
                                  &err);
        }

        if(checkError(self->handle,err))
        {
            free(dst_coords);
            return NULL;
        }

        npy_intp dims[] = {get_dimension(dst_basis)};
        return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,dst_coords);
    }

err:
    Py_XDECREF(verts);
    Py_XDECREF(src_ents);
    Py_XDECREF(dst_ents);
    return NULL;
}

static PyObject *
iGeomObj_getEntRange(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","storage_order","basis",0};

    PyObject *obj;
    enum iGeomExt_Basis basis = -1;
    int storage_order = -1;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|ii",kwlist,&obj,&storage_order,
                                    &basis))
        return NULL;

    if(basis == iGeomExt_XYZ)
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_BASIS);
        return NULL;
    }

    PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        int size = PyArray_SIZE(ents);
        iBase_EntityHandle *entities = PyArray_DATA(ents);

        if(basis == -1 && (basis = infer_basis(self->handle,entities[0])) == -1)
        {
            Py_DECREF(ents);
            return NULL;
        }

        if(storage_order == -1 && basis != iGeomExt_U)
        {
            PyErr_SetString(PyExc_ValueError,ERR_STORAGE_ORDER);
            Py_DECREF(ents);
            return NULL;
        }

        /* XXX: this is one of the only places that I malloc an array myself */
        int min_alloc = get_dimension(basis)*sizeof(double)*size, min_size;
        int max_alloc = min_alloc, max_size;
        double *min = malloc(2*min_alloc);
        double *max = min + min_alloc/sizeof(double);

        if(basis == iGeomExt_UV)
            iGeom_getArrUVRange(self->handle,entities,size,storage_order,
                                &min,&min_alloc,&min_size,
                                &max,&max_alloc,&max_size,&err);
        else
            iGeom_getArrURange(self->handle,entities,size,
                               &min,&min_alloc,&min_size,
                               &max,&max_alloc,&max_size,&err);
        Py_DECREF(ents);

        if(checkError(self->handle,err))
            return NULL;

        npy_intp outer = (storage_order == iBase_BLOCKED) ?
            get_dimension(basis):size;
        npy_intp dims[] = {2,outer,min_size/outer};
        return PyArray_NewFromMalloc(3,dims,NPY_DOUBLE,min);
    }
    else if(iBaseEntity_Check(obj))
    {
        iBase_EntityHandle entity = iBaseEntity_GetHandle(obj);
        if(basis == -1 && (basis = infer_basis(self->handle,entity)) == -1)
            return NULL;

        double *range = malloc(2*get_dimension(basis)*sizeof(double));
        if(basis == iGeomExt_UV)
            iGeom_getEntUVRange(self->handle,entity,range+0,range+1,range+2,
                                range+3,&err);
        else
            iGeom_getEntURange(self->handle,entity,range+0,range+1,&err);

        if(checkError(self->handle,err))
        {
            free(range);
            return NULL;
        }

        npy_intp dims[] = {2,get_dimension(basis)};
        return PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,range);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_isEntPeriodic(iGeom_Object *self,PyObject *args,PyObject *kw)
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
        int *uv=0;
        int uv_alloc=0,uv_size;

        size = PyArray_SIZE(ents);
        iBase_EntityHandle *data = PyArray_DATA(ents);

        iGeom_isArrPeriodic(self->handle,data,size,&uv,&uv_alloc,&uv_size,&err);
        Py_DECREF(ents);

        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {uv_size/2,2};
        npy_intp strides[] = {0,sizeof(int)/sizeof(npy_bool)};
        return PyArray_NewFromMallocStrided(2,dims,strides,NPY_BOOL,uv);
    }
    else if(iBaseEntity_Check(obj))
    {
        int *uv = malloc(sizeof(int)*2);
        iGeom_isEntPeriodic(self->handle,iBaseEntity_GetHandle(obj),
                            uv+0,uv+1,&err);
        if(checkError(self->handle,err))
        {
            free(uv);
            return NULL;
        }

        npy_intp dims[] = {2};
        npy_intp strides[] = {sizeof(int)/sizeof(npy_bool)};
        return PyArray_NewFromMallocStrided(1,dims,strides,NPY_BOOL,uv);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_isFcDegenerate(iGeom_Object *self,PyObject *args,PyObject *kw)
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
        int *degenerate=0;
        int degen_alloc=0,degen_size;

        size = PyArray_SIZE(ents);
        iBase_EntityHandle *data = PyArray_DATA(ents);

        iGeom_isFcArrDegenerate(self->handle,data,size,&degenerate,&degen_alloc,
                                &degen_size,&err);
        Py_DECREF(ents);

        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {degen_size};
        npy_intp strides[] = {sizeof(int)/sizeof(npy_bool)};
        return PyArray_NewFromMallocStrided(1,dims,strides,NPY_BOOL,degenerate);
    }
    else if(iBaseEntity_Check(obj))
    {
        int degenerate;
        iGeom_isFcDegenerate(self->handle,iBaseEntity_GetHandle(obj),
                             &degenerate,&err);
        if(checkError(self->handle,err))
            return NULL;
        return PyBool_FromLong(degenerate);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_getTolerance(iGeom_Object *self,void *closure)
{
    int type;
    double tolerance;
    int err;

    iGeom_getTolerance(self->handle,&type,&tolerance,&err);
    if(checkError(self->handle,err))
        return NULL;
    return NamedTuple_New(Tolerance_Type,"(id)",
        PyInt_FromLong(type),
        PyFloat_FromDouble(tolerance)
        );
}

static PyObject *
iGeomObj_getEntTolerance(iGeom_Object *self,PyObject *args,PyObject *kw)
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
        double *tol=0;
        int tol_alloc=0,tol_size;

        size = PyArray_SIZE(ents);
        iBase_EntityHandle *data = PyArray_DATA(ents);

        iGeom_getArrTolerance(self->handle,data,size,&tol,&tol_alloc,&tol_size,
                              &err);
        Py_DECREF(ents);

        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {tol_size};
        return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,tol);
    }
    else if(iBaseEntity_Check(obj))
    {
        double tol;
        iGeom_getEntTolerance(self->handle,iBaseEntity_GetHandle(obj),&tol,
                              &err);
        if(checkError(self->handle,err))
            return NULL;
        return PyFloat_FromDouble(tol);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_copyEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity",0};
    iBaseEntity_Object *entity;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntity_Type,
                                    &entity))
        return NULL;

    iBaseEntity_Object *copy = iBaseEntity_New();
    iGeom_copyEnt(self->handle,entity->handle,&copy->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(copy);
        return NULL;
    }
    return (PyObject*)copy;
}

static PyObject *
iGeomObj_sweepEntAboutAxis(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity","angle","axis",0};
    iBaseEntity_Object *entity;
    double angle;
    PyObject *obj;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!dO",kwlist,&iBaseEntity_Type,
                                    &entity,&angle,&obj))
        return NULL;

    PyObject *axis = PyArray_ToVectors(obj,NPY_DOUBLE,1,3,0);
    if(axis == NULL)
        return NULL;

    double *v = PyArray_DATA(axis);
    iBaseEntity_Object *result = iBaseEntity_New();
    iGeom_sweepEntAboutAxis(self->handle,entity->handle,angle,v[0],v[1],v[2],
                            &result->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(result);
        return NULL;
    }
    return (PyObject*)result;
}

static PyObject *
iGeomObj_deleteAll(iGeom_Object *self)
{
    int err;
    iGeom_deleteAll(self->handle,&err);
    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_deleteEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity",0};
    PyObject *obj;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&obj))
        return NULL;

    /*PyObject *ents = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1);
    if(ents)
    {
        int size = PyArray_SIZE(ents);
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        iGeom_deleteEntArr(self->handle,entities,size,&err);
        Py_DECREF(ents);
    }
    else*/ if(iBaseEntity_Check(obj))
    {
        iBase_EntityHandle entity = iBaseEntity_GetHandle(obj);
        iGeom_deleteEnt(self->handle,entity,&err);
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
iGeomObj_createSphere(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"radius",0};
    double radius;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"d",kwlist,&radius))
        return NULL;

    iBaseEntity_Object *entity = iBaseEntity_New();
    iGeom_createSphere(self->handle,radius,&entity->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(entity);
        return NULL;
    }
    return (PyObject*)entity;
}

static PyObject *
iGeomObj_createPrism(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"height","sides","major_rad","minor_rad",0};
    double height,major_rad,minor_rad;
    int sides;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"didd",kwlist,&height,&sides,
                                    &major_rad,&minor_rad))
        return NULL;

    iBaseEntity_Object *entity = iBaseEntity_New();
    iGeom_createPrism(self->handle,height,sides,major_rad,minor_rad,
                      &entity->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(entity);
        return NULL;
    }
    return (PyObject*)entity;
}

static PyObject *
iGeomObj_createBrick(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"dimensions",0};
    PyObject *obj;
    PyObject *vec;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&obj))
        obj = args;

    if((vec = PyArray_ToVectors(obj,NPY_DOUBLE,1,3,0)) == NULL)
        return NULL;
    double *v = PyArray_DATA(vec);
    iBaseEntity_Object *entity = iBaseEntity_New();

    iGeom_createBrick(self->handle,v[0],v[1],v[2],&entity->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(entity);
        return NULL;
    }
    return (PyObject*)entity;
}

static PyObject *
iGeomObj_createCylinder(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"height","major_rad","minor_rad",0};
    double height,major_rad,minor_rad;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"ddd",kwlist,&height,&major_rad,
                                    &minor_rad))
        return NULL;

    iBaseEntity_Object *entity = iBaseEntity_New();
    iGeom_createCylinder(self->handle,height,major_rad,minor_rad,
                         &entity->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(entity);
        return NULL;
    }
    return (PyObject*)entity;
}

static PyObject *
iGeomObj_createCone(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"height","major_rad","minor_rad","top_rad",0};
    double height,major_rad,minor_rad,top_rad;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"dddd",kwlist,&height,&major_rad,
                                    &minor_rad,&top_rad))
        return NULL;

    iBaseEntity_Object *entity = iBaseEntity_New();
    iGeom_createCone(self->handle,height,major_rad,minor_rad,top_rad,
                     &entity->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(entity);
        return NULL;
    }
    return (PyObject*)entity;
}

static PyObject *
iGeomObj_createTorus(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"major_rad","minor_rad",0};
    double major_rad,minor_rad;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"dd",kwlist,&major_rad,&minor_rad))
        return NULL;

    iBaseEntity_Object *entity = iBaseEntity_New();
    iGeom_createTorus(self->handle,major_rad,minor_rad,&entity->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(entity);
        return NULL;
    }
    return (PyObject*)entity;
}

static PyObject *
iGeomObj_moveEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity","direction",0};
    iBaseEntity_Object *entity;
    PyObject *obj;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O",kwlist,&iBaseEntity_Type,
                                    &entity,&obj))
        return NULL;

    PyObject *vec = PyArray_ToVectors(obj,NPY_DOUBLE,1,3,0);
    double *coords = PyArray_DATA(vec);
    iGeom_moveEnt(self->handle,entity->handle,coords[0],coords[1],coords[2],
                  &err);
    Py_DECREF(vec);

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_rotateEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity","angle","axis",0};
    iBaseEntity_Object *entity;
    double angle;
    PyObject *obj;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!dO",kwlist,&iBaseEntity_Type,
                                    &entity,&angle,&obj))
        return NULL;

    PyObject *vec = PyArray_ToVectors(obj,NPY_DOUBLE,1,3,0);
    double *coords = PyArray_DATA(vec);
    iGeom_rotateEnt(self->handle,entity->handle,angle,coords[0],coords[1],
                    coords[2],&err);
    Py_DECREF(vec);

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_reflectEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity","axis",0};
    iBaseEntity_Object *entity;
    PyObject *obj;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O",kwlist,&iBaseEntity_Type,
                                    &entity,&obj))
        return NULL;

    PyObject *vec = PyArray_ToVectors(obj,NPY_DOUBLE,1,3,0);
    double *coords = PyArray_DATA(vec);
    iGeom_reflectEnt(self->handle,entity->handle,coords[0],coords[1],coords[2],
                     &err);
    Py_DECREF(vec);

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_scaleEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity","scale",0};
    iBaseEntity_Object *entity;
    PyObject *obj;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O",kwlist,&iBaseEntity_Type,
                                    &entity,&obj))
        return NULL;

    PyObject *vec = PyArray_ToVectors(obj,NPY_DOUBLE,1,3,0);
    double *coords = PyArray_DATA(vec);
    iGeom_scaleEnt(self->handle,entity->handle,coords[0],coords[1],coords[2],
                   &err);
    Py_DECREF(vec);

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_uniteEnts(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    PyObject *obj;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&obj))
        obj = args;

    PyObject *ents = PyArray_FROMANY(obj,NPY_IBASEENT,1,1,NPY_C_CONTIGUOUS);
    if(ents == NULL)
        return NULL;

    int size = PyArray_SIZE(ents);
    iBase_EntityHandle *entities = PyArray_DATA(ents);
    iBaseEntity_Object *result = iBaseEntity_New();

    iGeom_uniteEnts(self->handle,entities,size,&result->handle,&err);
    Py_DECREF(ents);

    if(checkError(self->handle,err))
        return NULL;

    return (PyObject*)result;
}

static PyObject *
iGeomObj_subtractEnts(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity1","entity2",0};
    iBaseEntity_Object *entity1;
    iBaseEntity_Object *entity2;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O!",kwlist,&iBaseEntity_Type,
                                    &entity1,&iBaseEntity_Type,&entity2))
        return NULL;

    iBaseEntity_Object *result = iBaseEntity_New();
    iGeom_subtractEnts(self->handle,entity1->handle,entity2->handle,
                       &result->handle,&err);

    if(checkError(self->handle,err))
    {
        Py_DECREF(result);
        return NULL;
    }
    return (PyObject*)result;
}

static PyObject *
iGeomObj_intersectEnts(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity1","entity2",0};
    iBaseEntity_Object *entity1;
    iBaseEntity_Object *entity2;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O!",kwlist,&iBaseEntity_Type,
                                    &entity1,&iBaseEntity_Type,&entity2))
        return NULL;

    iBaseEntity_Object *result = iBaseEntity_New();
    iGeom_intersectEnts(self->handle,entity1->handle,entity2->handle,
                       &result->handle,&err);

    if(checkError(self->handle,err))
    {
        Py_DECREF(result);
        return NULL;
    }
    return (PyObject*)result;
}

static PyObject *
iGeomObj_sectionEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity","normal","offset","reverse",0};
    iBaseEntity_Object *entity;
    PyObject *obj;
    double offset;
    PyObject* rev;
    PyObject *vec;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!OdO!",kwlist,&iBaseEntity_Type,
                                    &entity,&obj,&offset,&PyBool_Type,&rev))
        return NULL;

    if((vec = PyArray_ToVectors(obj,NPY_DOUBLE,1,3,0)) == NULL)
        return NULL;
    double *coords = PyArray_DATA(vec);
    int reverse = (rev == Py_True);
    iBaseEntity_Object *result = iBaseEntity_New();

    iGeom_sectionEnt(self->handle,entity->handle,coords[0],coords[1],coords[2],
                     offset,reverse,&result->handle,&err);
    Py_DECREF(vec);

    if(checkError(self->handle,err))
    {
        Py_DECREF(result);
        return NULL;
    }
    return (PyObject*)result;
}

static PyObject *
iGeomObj_imprintEnts(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    PyObject *obj;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&obj))
        obj = args;

    PyObject *ents = PyArray_FROMANY(obj,NPY_IBASEENT,1,1,NPY_C_CONTIGUOUS);
    if(ents == NULL)
        return NULL;

    int size = PyArray_SIZE(ents);
    iBase_EntityHandle *entities = PyArray_DATA(ents);

    iGeom_imprintEnts(self->handle,entities,size,&err);
    Py_DECREF(ents);

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_mergeEnts(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","tolerance",0};
    PyObject *obj;
    double tolerance;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"Od",kwlist,&obj,&tolerance))
        return NULL;

    PyObject *ents = PyArray_FROMANY(obj,NPY_IBASEENT,1,1,NPY_C_CONTIGUOUS);
    if(ents == NULL)
        return NULL;

    int size = PyArray_SIZE(ents);
    iBase_EntityHandle *entities = PyArray_DATA(ents);

    iGeom_mergeEnts(self->handle,entities,size,tolerance,&err);
    Py_DECREF(ents);

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_createEntSet(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"ordered",0};
    int isList,err;
    PyObject *obj;
    iGeomEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&PyBool_Type,&obj))
        return NULL;

    set = iGeomEntitySet_New(self);

    isList = (obj == Py_True);
  
    iGeom_createEntSet(self->handle,isList,&set->base.handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF((PyObject*)set);
        return NULL;
    }

    return (PyObject*)set;  
}

static PyObject *
iGeomObj_destroyEntSet(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iGeom_destroyEntSet(self->handle,set->handle,&err);
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_createTag(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"name","size","type",0};
    char *name;
    char typechar;
    int size,type,err;
    iGeomTag_Object *tag;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"sic",kwlist,&name,&size,&typechar))
        return NULL;

    type = char_to_type(typechar);
    if(type == -1)
    {
        PyErr_SetString(PyExc_ValueError,ERR_TYPE_CODE);
        return NULL;
    }

    tag = iGeomTag_New(self);

    iGeom_createTag(self->handle,name,size,type,&tag->base.handle,&err,
                    strlen(name));
    if(checkError(self->handle,err))
    {
        Py_DECREF((PyObject*)tag);
        return NULL;
    }

    return (PyObject*)tag;
}

static PyObject *
iGeomObj_destroyTag(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"tag","force",0};
    int forced,err;
    iBaseTag_Object *tag;
    PyObject *obj;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O!",kwlist,&iBaseTag_Type,&tag,
                                    &PyBool_Type,&obj))
        return NULL;

    forced = (obj == Py_True);

    iGeom_destroyTag(self->handle,tag->handle,forced,&err);
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_getTagHandle(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"name",0};
    char *name;
    iGeomTag_Object *tag;
    int err;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"s",kwlist,&name))
        return NULL;

    tag = iGeomTag_New(self);

    iGeom_getTagHandle(self->handle,name,&tag->base.handle,&err,strlen(name));
    if(checkError(self->handle,err))
    {
        Py_DECREF((PyObject*)tag);
        return NULL;
    }
    return (PyObject*)tag;
}

static PyObject *
iGeomObj_getAllTags(iGeom_Object *self,PyObject *args,PyObject *kw)
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

        iGeom_getAllEntSetTags(self->handle,set,&tags,&alloc,&size,&err);
        if(checkError(self->handle,err))
            return NULL;
    }
    else if(iBaseEntity_Check(ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GetHandle(ents);

        iGeom_getAllTags(self->handle,entity,&tags,&alloc,&size,&err);
        if(checkError(self->handle,err))
            return NULL;
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTSET);
        return NULL;
    }

    npy_intp dims[] = {size};
    return PyArray_NewFromMallocBase(1,dims,NPY_IGEOMTAG,tags,
                                     (PyObject*)self);
}


static PyMethodDef iGeomObj_methods[] = {
    { "load", (PyCFunction)iGeomObj_load, METH_KEYWORDS,
      "Load a geometry from a file into this instance"
    },
    { "save", (PyCFunction)iGeomObj_save, METH_KEYWORDS,
      "Save this geometry to a file"
    },
    { "getEntType", (PyCFunction)iGeomObj_getEntType, METH_KEYWORDS,
      "Get the entity type(s) for the specified entity(ies)"
    },
    { "getEntAdj", (PyCFunction)iGeomObj_getEntAdj, METH_KEYWORDS,
      "Get entities of specified type adjacent to entity(ies)"
    },
    { "getEnt2ndAdj", (PyCFunction)iGeomObj_getEnt2ndAdj, METH_KEYWORDS,
      "Get \"2nd order\" adjacencies to entity(ies)"
    },
    { "isEntAdj", (PyCFunction)iGeomObj_isEntAdj, METH_KEYWORDS,
      "Return whether two entities (or pairs of entities in arrays) are "
      "adjacent"
    },
    { "getEntClosestPt", (PyCFunction)iGeomObj_getEntClosestPt, METH_KEYWORDS,
      "Get closest point(s) to the specified entity(ies)"
    },
    { "getEntNormal", (PyCFunction)iGeomObj_getEntNormal, METH_KEYWORDS,
      "Get normal vector(s) at the specified position(s) of the entity(ies)"
    },
    { "getEntNormalPl", (PyCFunction)iGeomObj_getEntNormalPl, METH_KEYWORDS,
      "Get normal vector(s) and closest point(s) at the specified position(s) "
      "of the entity(ies)"
    },
    { "getEntTangent", (PyCFunction)iGeomObj_getEntTangent, METH_KEYWORDS,
      "Get tangent vector(s) at the specified position(s) of the entity(ies)"
    },
    { "getEnt1stDerivative", (PyCFunction)iGeomObj_getEnt1stDerivative,
      METH_KEYWORDS, "Get the 1st derivative at the specified position(s) of "
      "the entity(ies)"
    },
    { "getEnt2ndDerivative", (PyCFunction)iGeomObj_getEnt2ndDerivative,
      METH_KEYWORDS, "Get the 2nd derivative at the specified position(s) of "
      "the entity(ies)"
    },
    { "getEntCurvature", (PyCFunction)iGeomObj_getEntCurvature, METH_KEYWORDS,
      "Get curvature at the specified position(s) of the entity(ies)"
    },
    { "getEntEval", (PyCFunction)iGeomObj_getEntEval, METH_KEYWORDS,
      "Get the closest point(s), tangent/normal vectors(s), and curvature(s) "
      "at the specified position(s) of the entity(ies)"
    },
    { "getEntBoundBox", (PyCFunction)iGeomObj_getEntBoundBox, METH_KEYWORDS,
      "Get the bounding box of specified vertex(ices)"
    },
    { "getVtxCoords", (PyCFunction)iGeomObj_getVtxCoords, METH_KEYWORDS,
      "Get coordinates of specified vertex(ices)"
    },
    { "getPtRayIntersect", (PyCFunction)iGeomObj_getPtRayIntersect,
      METH_KEYWORDS, "Intersect the specified ray(s) with the model"
    },
    { "getPtClass", (PyCFunction)iGeomObj_getPtClass, METH_KEYWORDS,
      "Get the entity(ies) on which the specified point(s) are located"
    },
    { "getEntNormalSense", (PyCFunction)iGeomObj_getEntNormalSense,
      METH_KEYWORDS, "Get the sense of the specified face(s) with respect to "
      "the corresponding region(s)"
    },
    { "getEgFcSense", (PyCFunction)iGeomObj_getEgFcSense, METH_KEYWORDS,
      "Get the sense of the specified edge(s) with respect to the "
      "corresponding face(s)"
    },
    { "getEgVtxSense", (PyCFunction)iGeomObj_getEgVtxSense, METH_KEYWORDS,
      "Get the sense of the specified edge(s) with respect to the "
      "corresponding pair(s) of vertices"
    },
    { "measure", (PyCFunction)iGeomObj_measure, METH_KEYWORDS,
      "Return the measure (length, area, or volume) of the specified "
      "entity(ies)"
    },
    { "getFaceType", (PyCFunction)iGeomObj_getFaceType, METH_KEYWORDS,
      "Get the geometric type of the specified entity"
    },
    { "isEntParametric", (PyCFunction)iGeomObj_isEntParametric, METH_KEYWORDS,
      "Return whether the specified entity(ies) are parametric"
    },
    { "getEntCoords", (PyCFunction)iGeomObj_getEntCoords, METH_KEYWORDS,
      "Transform the coordinates of the specified entity(ies) to a different "
      "basis"
    },
    { "getEntRange", (PyCFunction)iGeomObj_getEntRange, METH_KEYWORDS,
      "Get the parametric range of the specified entity(ies)"
    },
    { "copyEnt", (PyCFunction)iGeomObj_copyEnt, METH_KEYWORDS,
      "Copy specified entity"
    },
    { "sweepEntAboutAxis", (PyCFunction)iGeomObj_sweepEntAboutAxis,
      METH_KEYWORDS, "Sweep an entity about an axis"
    },
    { "deleteAll", (PyCFunction)iGeomObj_deleteAll, METH_NOARGS,
      "Delete all entities and sets"
    },
    { "deleteEnt", (PyCFunction)iGeomObj_deleteEnt, METH_KEYWORDS,
      "Delete specified entity(ies)"
    },
    { "createSphere", (PyCFunction)iGeomObj_createSphere, METH_KEYWORDS,
      "Create a sphere centered on the origin"
    },
    { "createPrism", (PyCFunction)iGeomObj_createPrism, METH_KEYWORDS,
      "Create a prism centered on the origin"
    },
    { "createBrick", (PyCFunction)iGeomObj_createBrick, METH_KEYWORDS,
      "Create a brick centered on the origin"
    },
    { "createCylinder", (PyCFunction)iGeomObj_createCylinder, METH_KEYWORDS,
      "Create a cylinder centered on the origin"
    },
    { "createCone", (PyCFunction)iGeomObj_createCone, METH_KEYWORDS,
      "Create a cone centered on the origin"
    },
    { "createTorus", (PyCFunction)iGeomObj_createTorus, METH_KEYWORDS,
      "Create a torus centered on the origin"
    },
    { "moveEnt", (PyCFunction)iGeomObj_moveEnt, METH_KEYWORDS,
      "Translate the specified entity"
    },
    { "rotateEnt", (PyCFunction)iGeomObj_rotateEnt, METH_KEYWORDS,
      "Rotate the specified entity"
    },
    { "reflectEnt", (PyCFunction)iGeomObj_reflectEnt, METH_KEYWORDS,
      "Reflect the specified entity"
    },
    { "scaleEnt", (PyCFunction)iGeomObj_scaleEnt, METH_KEYWORDS,
      "Scale the specified entity"
    },
    { "uniteEnts", (PyCFunction)iGeomObj_uniteEnts, METH_KEYWORDS,
      "Return the union of the specified entities"
    },
    { "subtractEnts", (PyCFunction)iGeomObj_subtractEnts, METH_KEYWORDS,
      "Return the difference of the specified entities"
    },
    { "intersectEnts", (PyCFunction)iGeomObj_intersectEnts, METH_KEYWORDS,
      "Return the intersection of the specified entities"
    },
    { "sectionEnt", (PyCFunction)iGeomObj_sectionEnt, METH_KEYWORDS,
      "Section the specified entity"
    },
    { "imprintEnts", (PyCFunction)iGeomObj_imprintEnts, METH_KEYWORDS,
      "Imprint the specified entities"
    },
    { "mergeEnts", (PyCFunction)iGeomObj_mergeEnts, METH_KEYWORDS,
      "Merge the specified entities"
    },
    { "isEntPeriodic", (PyCFunction)iGeomObj_isEntPeriodic, METH_KEYWORDS,
      "Return whether the entity(ies) are periodic"
    },
    { "isFcDegenerate", (PyCFunction)iGeomObj_isFcDegenerate, METH_KEYWORDS,
      "Return whether the face entity(ies) are degenerate"
    },
    { "getEntTolerance", (PyCFunction)iGeomObj_getEntTolerance, METH_KEYWORDS,
      "Get the tolerance(s) for the specified entity(ies)"
    },
    { "createEntSet", (PyCFunction)iGeomObj_createEntSet, METH_KEYWORDS,
      "Create an entity set"
    },
    { "destroyEntSet", (PyCFunction)iGeomObj_destroyEntSet, METH_KEYWORDS,
      "Destroy an entity set"
    },
    { "createTag", (PyCFunction)iGeomObj_createTag, METH_KEYWORDS,
      "Create a tag with specified name, size, and type"
    },
    { "destroyTag", (PyCFunction)iGeomObj_destroyTag, METH_KEYWORDS,
      "Destroy a tag"
    },
    { "getTagHandle", (PyCFunction)iGeomObj_getTagHandle, METH_KEYWORDS,
      "Get the handle of an existing tag with the specified name"
    },
    { "getAllTags", (PyCFunction)iGeomObj_getAllTags, METH_KEYWORDS,
      "Get all the tags associated with a specified entity handle (or "
      "array/set of entities)"
    },
    {0}
};

static PyGetSetDef iGeomObj_getset[] = {
    { "rootSet", (getter)iGeomObj_getRootSet, 0,
      "Return the root set of the geometry", 0
    },
    { "boundBox", (getter)iGeomObj_getBoundBox, 0,
      "Return the bounding box of the entire model", 0
    },
    { "topoLevel", (getter)iGeomObj_getTopoLevel, 0,
      "Return the topology level of the model", 0
    },
    { "parametric", (getter)iGeomObj_getParametric, 0,
      "Return whether the model supports parameterization", 0
    },
    { "tolerance", (getter)iGeomObj_getTolerance, 0,
      "Return the model-level tolerance (if any)", 0
    },
    {0}
};

static PyObject * iGeomObj_getAttr(PyObject *self,PyObject *attr_name)
{
    PyObject *ret;

    ret = PyObject_GenericGetAttr(self,attr_name);
    if(ret)
        return ret;
    else if(!PyErr_ExceptionMatches(PyExc_AttributeError))
        return NULL;
    else
    {
        PyErr_Clear();
        PyObject *root = iGeomObj_getRootSet((iGeom_Object*)self,0);
        if(!root)
            return NULL;
        ret = PyObject_GetAttr(root,attr_name);
        Py_DECREF(root);
        return ret;
    }
}

static PyTypeObject iGeom_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iGeom.Geom",                       /* tp_name */
    sizeof(iGeom_Object),                     /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iGeomObj_dealloc,             /* tp_dealloc */
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
    iGeomObj_getAttr,                         /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "iGeom objects",                          /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iGeomObj_methods,                         /* tp_methods */
    0,                                        /* tp_members */
    iGeomObj_getset,                          /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)iGeomObj_init,                  /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};


static PyMethodDef module_methods[] = {
    {0}
};

static PyObject *
iGeomEntitySetArr_getitem(void *data,void *arr)
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
    iGeom_Object *instance = (iGeom_Object*)base->base;
    iGeomEntitySet_Object *o = iGeomEntitySet_New(instance);

    o->base.handle = *(iBase_EntitySetHandle*)data;

    return (PyObject*)o;
}

static int
iGeomEntitySetArr_setitem(PyObject *item,void *data,void *arr)
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
        if(!iGeomEntitySet_Check(item))
            return -1;
        base = ArrDealloc_New((PyObject*)iGeomEntitySet_GetInstance(item),0);
        PyArray_BASE(arr) = (PyObject*)base;
    }

    if(iGeomEntitySet_Check(item))
    {
        iGeom_Object *instance = (iGeom_Object*)base->base;
        if(iGeomEntitySet_GetInstance(item)->handle != instance->handle)
        {
            PyErr_SetString(PyExc_ValueError,ERR_ARR_INSTANCE);
            return -1;
        }
    }

    *(iBase_EntitySetHandle*)data = iBaseEntitySet_GetHandle(item);
    return 0;
}

static PyObject *
iGeomTagArr_getitem(void *data,void *arr)
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
    iGeom_Object *instance = (iGeom_Object*)base->base;
    iGeomTag_Object *o = iGeomTag_New(instance);

    o->base.handle = *(iBase_TagHandle*)data;

    return (PyObject*)o;
}

static int
iGeomTagArr_setitem(PyObject *item,void *data,void *arr)
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
        if(!iGeomTag_Check(item))
            return -1;
        base = ArrDealloc_New((PyObject*)iGeomTag_GetInstance(item),0);
        PyArray_BASE(arr) = (PyObject*)base;
    }

    if(iGeomTag_Check(item))
    {
        iGeom_Object *instance = (iGeom_Object*)base->base;
        if(iGeomTag_GetInstance(item)->handle != instance->handle)
        {
            PyErr_SetString(PyExc_ValueError,ERR_ARR_INSTANCE);
            return -1;
        }
    }

    *(iBase_TagHandle*)data = iBaseTag_GetHandle(item);
    return 0;
}

static PyArray_ArrFuncs iGeomEntitySetArr_Funcs;
static int NPY_IGEOMENTSET;

static PyArray_ArrFuncs iGeomTagArr_Funcs;
static int NPY_IGEOMTAG;

ENUM_TYPE(iGeomBasis,"iGeom.Basis","");


PyMODINIT_FUNC initiGeom(void)
{
    PyObject *m;
    PyArray_Descr *descr;

    m = Py_InitModule("iGeom",module_methods);
    import_array();
    import_ufunc();
    import_iBase();
    import_helpers();

    /***** register C API *****/
    static void *IGeom_API[] = {
        &iGeom_Type,
        &iGeomIter_Type,
        &iGeomEntitySet_Type,
        &iGeomTag_Type,
        &NPY_IGEOMENTSET,
        &NPY_IGEOMTAG,
        iGeomEntitySet_New,
        iGeomTag_New,
        &NormalPl_Type,
        &FaceEval_Type,
        &EdgeEval_Type,
        &Deriv1st_Type,
        &Deriv2nd_Type,
        &Intersect_Type,
        &Tolerance_Type,
    };
    PyObject *api_obj;

    /* Initialize the C API pointer array */


    /* Create a CObject containing the API pointer array's address */
    api_obj = PyCObject_FromVoidPtr(IGeom_API,NULL);

    if(api_obj != NULL)
        PyModule_AddObject(m, "_C_API", api_obj);

    /***** acquire "equal" ufunc *****/
    PyObject *ops = PyArray_GetNumericOps();
    PyUFuncObject *ufunc = (PyUFuncObject*)PyDict_GetItemString(ops,"equal");
    Py_DECREF(ops);
    int types[3];

    REGISTER_CLASS_BASE(m,"Geom",     iGeom,         iBase);
    REGISTER_CLASS_BASE(m,"EntitySet",iGeomEntitySet,iBaseEntitySet);
    REGISTER_CLASS_BASE(m,"Tag",      iGeomTag,      iBaseTag);
    REGISTER_CLASS     (m,"Iterator", iGeomIter);


    /***** initialize topology enum *****/
    REGISTER_CLASS(m,"Basis",iGeomBasis);

    ADD_ENUM(iGeomBasis,"xyz", iGeomExt_XYZ);
    ADD_ENUM(iGeomBasis,"u",   iGeomExt_U);
    ADD_ENUM(iGeomBasis,"uv",  iGeomExt_UV);

    /***** initialize iGeomEntitySet array *****/
    descr = PyArray_DescrNewFromType(NPY_IBASEENTSET);
    memcpy(&iGeomEntitySetArr_Funcs,descr->f,sizeof(PyArray_ArrFuncs));
    descr->f = &iGeomEntitySetArr_Funcs;

    descr->typeobj = &iGeomEntitySet_Type;
    descr->type = 'G';
    descr->f->getitem = iGeomEntitySetArr_getitem;
    descr->f->setitem = iGeomEntitySetArr_setitem;

    NPY_IGEOMENTSET = PyArray_RegisterDataType(descr);
    PyModule_AddObject(m,"npy_entset",(PyObject*)descr);

    types[0] = types[1] = NPY_IGEOMENTSET; types[2] = NPY_BOOL;
    PyUFunc_RegisterLoopForType(ufunc,NPY_IGEOMENTSET,iBaseEntitySetArr_equal,
                                types,0);

    /***** initialize iGeomTag array *****/
    descr = PyArray_DescrNewFromType(NPY_IBASETAG);
    memcpy(&iGeomTagArr_Funcs,descr->f,sizeof(PyArray_ArrFuncs));
    descr->f = &iGeomTagArr_Funcs;

    descr->typeobj = &iGeomTag_Type;
    descr->type = 'G';
    descr->f->getitem = iGeomTagArr_getitem;
    descr->f->setitem = iGeomTagArr_setitem;

    NPY_IGEOMTAG = PyArray_RegisterDataType(descr);
    PyModule_AddObject(m,"npy_tag",(PyObject*)descr);

    types[0] = types[1] = NPY_IGEOMTAG; types[2] = NPY_BOOL;
    PyUFunc_RegisterLoopForType(ufunc,NPY_IGEOMTAG,iBaseTagArr_equal,types,0);

    /***** create named tuple types *****/
    /* TODO: add these to the module dictionary and do error checking */
    NormalPl_Type  = NamedTuple_CreateType("normal_pl","points normals");
    FaceEval_Type  = NamedTuple_CreateType("face_eval","points normals curv1 "
                                           "curv2");
    EdgeEval_Type  = NamedTuple_CreateType("edge_eval","points tangents curv");
    Deriv1st_Type  = NamedTuple_CreateType("deriv_1st","u v");
    Deriv2nd_Type  = NamedTuple_CreateType("deriv_2nd","uu vv uv");
    Intersect_Type = NamedTuple_CreateType("intersect","entities isect param");
    Tolerance_Type = NamedTuple_CreateType("tolerance","type tolerance");
}

/* Include source files so that everything is in one translation unit */
#include "iGeom_entSet.inl"
#include "iGeom_iter.inl"
#include "iGeom_tag.inl"
