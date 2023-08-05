
#include "Python.h"
#include "shapefil.h"

typedef struct {
    PyObject_HEAD
    SHPTree *tree;
} Quadtree;

staticforward PyTypeObject QuadtreeType;

/* Alloc/dealloc */

static void
Quadtree_dealloc(Quadtree *self)
{
    if (self->tree)
        SHPDestroyTree(self->tree);
    self->tree = NULL;
    self->ob_type->tp_free((PyObject*) self);
}

static int
Quadtree_init(Quadtree *self, PyObject *args, PyObject *kwds)
{
    int d=16;
    double min[2], max[2];
        
    if (!PyArg_ParseTuple(args, "(dddd)|i", &min[0], &min[1], &max[0], &max[1],
                          &d)
        )
        return -1;
    self->tree = SHPCreateTree(NULL, 2, d, min, max);
    if (!self->tree) return -1;
    return 0;
}

/* Methods */

static PyObject *
Quadtree_add(Quadtree *self, PyObject *args)
{
    int n;
    double min[2], max[2];
    SHPObject *s;

    /* our shapes are boxes, single rings */
    int part_start[1] = {0};
    double x[5], y[5];
    
    if (!PyArg_ParseTuple(args, "i(dddd)", &n,
                          &min[0], &min[1], &max[0], &max[1]))
        return NULL;

    /* make shape vertices */
    x[0] = min[0];
    x[1] = min[0];
    x[2] = max[0];
    x[3] = max[0];
    x[4] = min[0];
    
    y[0] = min[1];
    y[1] = max[1];
    y[2] = max[1];
    y[3] = min[1];
    y[4] = min[1];
    
    s = (SHPObject *) SHPCreateObject(5, n, 1, part_start, NULL, 5,
                                      x, y, NULL, NULL);
    if (!SHPTreeAddShapeId(self->tree, s))
    {
        PyErr_SetString(PyExc_Exception, "Failed to index item");
        return NULL;
    }
    SHPDestroyObject(s);
    
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject *
Quadtree_intersection(Quadtree *self, PyObject *args)
{
    int *hits, count=0, i;
    double min[2], max[2];
    PyObject *list;

    if (!PyArg_ParseTuple(args, "(dddd)", &min[0], &min[1], &max[0], &max[1]))
        return NULL;

    hits = SHPTreeFindLikelyShapes(self->tree, min, max, &count);
    list = PyList_New((size_t)count);
    for (i=0; i<count; i++)
    {
        PyList_SET_ITEM(list, (size_t)i, Py_BuildValue("i", hits[i]));
    }
    
    return PySeqIter_New(list);
}

/* Define Methods */

static PyMethodDef module_methods[] = {
    {"add", (PyCFunction)Quadtree_add, METH_VARARGS, "Add an item to an index, specifying an integer id and a bounding box"},
    {"likely_intersection", (PyCFunction)Quadtree_intersection, METH_VARARGS, "Return an iterator over integer ids of items that are likely to intersect with the specified bounding box."},
    {NULL}
};

/* Define Type */

static PyTypeObject QuadtreeType = {
    PyObject_HEAD_INIT(NULL)
    0,                              /*ob_size*/
    "Quadtree",                     /*tp_name*/
    sizeof(Quadtree),               /*tp_basicsize*/
    0,                              /*tp_itemsize*/
    (destructor)Quadtree_dealloc,   /*tp_dealloc*/
    0,                              /*tp_print*/
    0,                              /*tp_getattr*/
    0,                              /*tp_setattr*/
    0,                              /*tp_compare*/
    0,                              /*tp_repr*/
    0,                              /*tp_as_number*/
    0,                              /*tp_as_sequence*/
    0,                              /*tp_as_mapping*/
    0,                              /*tp_hash */
    0,                              /*tp_call*/
    0,                              /*tp_str*/
    0,                              /*tp_getattro*/
    0,                              /*tp_setattro*/
    0,                              /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Quadtree spatial index",       /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    module_methods,             /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Quadtree_init,   /* tp_init */
    0,                         /* tp_alloc */
    PyType_GenericNew,         /* tp_new */
};

/* Initialization */

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_tree(void) 
{
    PyObject* m;
    if (PyType_Ready(&QuadtreeType) < 0)
        return;
    m = Py_InitModule3("_tree", module_methods,
                       "Quadtree spatial index.");
    if (m == NULL)
      return;

    Py_INCREF(&QuadtreeType);
    PyModule_AddObject(m, "Quadtree", (PyObject *)&QuadtreeType);

}

