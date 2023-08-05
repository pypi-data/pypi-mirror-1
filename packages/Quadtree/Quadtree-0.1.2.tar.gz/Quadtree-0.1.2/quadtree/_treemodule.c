
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
    int n, size;
    PyObject *bounds=NULL;
    double min[2], max[2];
    SHPObject *s;

    /* our shapes are boxes, single rings */
    int part_start[1] = {0};
    double x[5], y[5];
    
    if (!PyArg_ParseTuple(args, "iO", &n, &bounds))
        return NULL;

    /* Check length of the bounds argument */
    if (!PySequence_Check(bounds))
    {
        PyErr_SetString(PyExc_TypeError, "Bounds must be a sequence");
        return NULL;
    }

    size = (int) PySequence_Size(bounds);
    if (size == 2)
    {
        min[0] = max[0] = PyFloat_AsDouble(PySequence_ITEM(bounds, 0));
        min[1] = max[1] = PyFloat_AsDouble(PySequence_ITEM(bounds, 1));
    }
    else if (size == 4)
    {
        min[0] = PyFloat_AsDouble(PySequence_ITEM(bounds, 0));
        min[1] = PyFloat_AsDouble(PySequence_ITEM(bounds, 1));
        max[0] = PyFloat_AsDouble(PySequence_ITEM(bounds, 2));
        max[1] = PyFloat_AsDouble(PySequence_ITEM(bounds, 3));
    }
    else
    {
        PyErr_Format(PyExc_TypeError,
            "Bounds argument must be sequence of length 2 or 4, not %d",
            size);
        return NULL;
    }
    
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
Quadtree_prune(Quadtree *self)
{
    SHPTreeTrimExtraNodes(self->tree);
    Py_INCREF(Py_None);
    return Py_None;
}

/* Tree structure */

static void 
QuadtreeNodeDump(SHPTreeNode *node, PyObject *nodelist)
{
    int i;
    PyObject *g=NULL, *ids=NULL, *bounds=NULL, *children=NULL;

    g = PyDict_New();
    
    /* Save bounds */
    bounds = Py_BuildValue("(dddd)", 
                node->adfBoundsMin[0], node->adfBoundsMin[1], 
                node->adfBoundsMax[0], node->adfBoundsMax[1]); 
    PyDict_SetItemString(g, "bounds", bounds);
 
    /* Save ids */
    ids = PyList_New(0);
    for (i=0; i<node->nShapeCount; i++)
    {
        PyList_Append(ids, Py_BuildValue("i", node->panShapeIds[i]));
    }
    PyDict_SetItemString(g, "ids", ids);

    /* Child nodes */
    children = PyList_New(0);
    for (i=0; i<node->nSubNodes; i++)
    {
        if (node->apsSubNode[i] != NULL)
            QuadtreeNodeDump(node->apsSubNode[i], children);
    }
    PyDict_SetItemString(g, "nodes", children);
    
    /* Add g to the node list */
    PyList_Append(nodelist, g);
}

static PyObject *
Quadtree_struct(Quadtree *self)
{
    PyObject *nodes=NULL;
    nodes = PyList_New(0);
    QuadtreeNodeDump(self->tree->psRoot, nodes);
    return PyList_GetItem(nodes, 0);
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
    {"prune", (PyCFunction)Quadtree_prune, METH_NOARGS, "Remove unused nodes from the tree"},
    {"struct", (PyCFunction)Quadtree_struct, METH_NOARGS, "Return simple graph structure of the tree"},
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

