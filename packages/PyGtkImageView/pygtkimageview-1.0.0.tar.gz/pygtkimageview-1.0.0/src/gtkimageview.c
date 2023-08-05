/* -- THIS FILE IS GENERATED - DO NOT EDIT *//* -*- Mode: C; c-basic-offset: 4 -*- */

#include <Python.h>



#line 3 "gtkimageview.override"
#include <Python.h>
#include <gtkimageview/gtkanimview.h>
#include <gtkimageview/gtkimageview.h>
#include <gtkimageview/gtkimagescrollwin.h>
#include <gtkimageview/gtkimagetooldragger.h>
#include <gtkimageview/gtkimagetoolpainter.h>
#include <gtkimageview/gtkimagetoolselector.h>
#include <gtkimageview/gtkzooms.h>
#include "pygobject.h"
#include "enums-public.h"

/* This is apparently something you need to copy into every .override
   file because of the code codegen.py generates. Craptastic. */
gboolean
static pygdk_rectangle_from_pyobject (PyObject     *object,
                                      GdkRectangle *rectangle)
{
    g_return_val_if_fail (rectangle, FALSE);

    if (pyg_boxed_check (object, GDK_TYPE_RECTANGLE))
    {
	*rectangle = *pyg_boxed_get (object, GdkRectangle);
	return TRUE;
    }
    if (PyArg_ParseTuple (object, "iiii",
                          &rectangle->x, &rectangle->y,
                          &rectangle->width, &rectangle->height))
	return TRUE;
    
    PyErr_Clear ();
    PyErr_SetString (PyExc_TypeError, "could not convert to GdkRectangle");
    return FALSE;
}

#line 43 "gtkimageview.c"


/* ---------- types from other modules ---------- */
static PyTypeObject *_PyGObject_Type;
#define PyGObject_Type (*_PyGObject_Type)
static PyTypeObject *_PyGtkWidget_Type;
#define PyGtkWidget_Type (*_PyGtkWidget_Type)
static PyTypeObject *_PyGtkWindow_Type;
#define PyGtkWindow_Type (*_PyGtkWindow_Type)
static PyTypeObject *_PyGtkTable_Type;
#define PyGtkTable_Type (*_PyGtkTable_Type)
static PyTypeObject *_PyGdkPixbuf_Type;
#define PyGdkPixbuf_Type (*_PyGdkPixbuf_Type)
static PyTypeObject *_PyGdkPixbufAnimation_Type;
#define PyGdkPixbufAnimation_Type (*_PyGdkPixbufAnimation_Type)


/* ---------- forward type declarations ---------- */
PyTypeObject G_GNUC_INTERNAL PyGtkImageNav_Type;
PyTypeObject G_GNUC_INTERNAL PyGtkImageScrollWin_Type;
PyTypeObject G_GNUC_INTERNAL PyGtkImageToolDragger_Type;
PyTypeObject G_GNUC_INTERNAL PyGtkImageToolSelector_Type;
PyTypeObject G_GNUC_INTERNAL PyGtkImageView_Type;
PyTypeObject G_GNUC_INTERNAL PyGtkAnimView_Type;
PyTypeObject G_GNUC_INTERNAL PyGtkIImageTool_Type;

#line 70 "gtkimageview.c"



/* ----------- GtkImageNav ----------- */

static int
_wrap_gtk_image_nav_new(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    GType obj_type = pyg_type_from_object((PyObject *) self);
    GParameter params[1];
    PyObject *parsed_args[1] = {NULL, };
    char *arg_names[] = {"view", NULL };
    char *prop_names[] = {"view", NULL };
    guint nparams, i;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O:None.ImageNav.__init__" , arg_names , &parsed_args[0]))
        return -1;

    memset(params, 0, sizeof(GParameter)*1);
    if (!pyg_parse_constructor_args(obj_type, arg_names,
                                    prop_names, params, 
                                    &nparams, parsed_args))
        return -1;
    pygobject_constructv(self, nparams, params);
    for (i = 0; i < nparams; ++i)
        g_value_unset(&params[i].value);
    if (!self->obj) {
        PyErr_SetString(
            PyExc_RuntimeError, 
            "could not create None.ImageNav object");
        return -1;
    }
    return 0;
}

static PyObject *
_wrap_gtk_image_nav_get_pixbuf(PyGObject *self)
{
    GdkPixbuf *ret;

    
    ret = gtk_image_nav_get_pixbuf(GTK_IMAGE_NAV(self->obj));
    
    /* pygobject_new handles NULL checking */
    return pygobject_new((GObject *)ret);
}

static PyObject *
_wrap_gtk_image_nav_grab(PyGObject *self)
{
    
    gtk_image_nav_grab(GTK_IMAGE_NAV(self->obj));
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_nav_release(PyGObject *self)
{
    
    gtk_image_nav_release(GTK_IMAGE_NAV(self->obj));
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_nav_show_and_grab(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "center_x", "center_y", NULL };
    int center_x, center_y;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"ii:GtkImageNav.show_and_grab", kwlist, &center_x, &center_y))
        return NULL;
    
    gtk_image_nav_show_and_grab(GTK_IMAGE_NAV(self->obj), center_x, center_y);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static const PyMethodDef _PyGtkImageNav_methods[] = {
    { "get_pixbuf", (PyCFunction)_wrap_gtk_image_nav_get_pixbuf, METH_NOARGS,
      NULL },
    { "grab", (PyCFunction)_wrap_gtk_image_nav_grab, METH_NOARGS,
      NULL },
    { "release", (PyCFunction)_wrap_gtk_image_nav_release, METH_NOARGS,
      NULL },
    { "show_and_grab", (PyCFunction)_wrap_gtk_image_nav_show_and_grab, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { NULL, NULL, 0, NULL }
};

PyTypeObject G_GNUC_INTERNAL PyGtkImageNav_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                 /* ob_size */
    "ImageNav",                   /* tp_name */
    sizeof(PyGObject),          /* tp_basicsize */
    0,                                 /* tp_itemsize */
    /* methods */
    (destructor)0,        /* tp_dealloc */
    (printfunc)0,                      /* tp_print */
    (getattrfunc)0,       /* tp_getattr */
    (setattrfunc)0,       /* tp_setattr */
    (cmpfunc)0,           /* tp_compare */
    (reprfunc)0,             /* tp_repr */
    (PyNumberMethods*)0,     /* tp_as_number */
    (PySequenceMethods*)0, /* tp_as_sequence */
    (PyMappingMethods*)0,   /* tp_as_mapping */
    (hashfunc)0,             /* tp_hash */
    (ternaryfunc)0,          /* tp_call */
    (reprfunc)0,              /* tp_str */
    (getattrofunc)0,     /* tp_getattro */
    (setattrofunc)0,     /* tp_setattro */
    (PyBufferProcs*)0,  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,                      /* tp_flags */
    NULL,                        /* Documentation string */
    (traverseproc)0,     /* tp_traverse */
    (inquiry)0,             /* tp_clear */
    (richcmpfunc)0,   /* tp_richcompare */
    offsetof(PyGObject, weakreflist),             /* tp_weaklistoffset */
    (getiterfunc)0,          /* tp_iter */
    (iternextfunc)0,     /* tp_iternext */
    (struct PyMethodDef*)_PyGtkImageNav_methods, /* tp_methods */
    (struct PyMemberDef*)0,              /* tp_members */
    (struct PyGetSetDef*)0,  /* tp_getset */
    NULL,                              /* tp_base */
    NULL,                              /* tp_dict */
    (descrgetfunc)0,    /* tp_descr_get */
    (descrsetfunc)0,    /* tp_descr_set */
    offsetof(PyGObject, inst_dict),                 /* tp_dictoffset */
    (initproc)_wrap_gtk_image_nav_new,             /* tp_init */
    (allocfunc)0,           /* tp_alloc */
    (newfunc)0,               /* tp_new */
    (freefunc)0,             /* tp_free */
    (inquiry)0              /* tp_is_gc */
};



/* ----------- GtkImageScrollWin ----------- */

 static int
_wrap_gtk_image_scroll_win_new(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    GType obj_type = pyg_type_from_object((PyObject *) self);
    GParameter params[1];
    PyObject *parsed_args[1] = {NULL, };
    char *arg_names[] = {"view", NULL };
    char *prop_names[] = {"view", NULL };
    guint nparams, i;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O:None.ImageScrollWin.__init__" , arg_names , &parsed_args[0]))
        return -1;

    memset(params, 0, sizeof(GParameter)*1);
    if (!pyg_parse_constructor_args(obj_type, arg_names,
                                    prop_names, params, 
                                    &nparams, parsed_args))
        return -1;
    pygobject_constructv(self, nparams, params);
    for (i = 0; i < nparams; ++i)
        g_value_unset(&params[i].value);
    if (!self->obj) {
        PyErr_SetString(
            PyExc_RuntimeError, 
            "could not create None.ImageScrollWin object");
        return -1;
    }
    return 0;
}

PyTypeObject G_GNUC_INTERNAL PyGtkImageScrollWin_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                 /* ob_size */
    "ImageScrollWin",                   /* tp_name */
    sizeof(PyGObject),          /* tp_basicsize */
    0,                                 /* tp_itemsize */
    /* methods */
    (destructor)0,        /* tp_dealloc */
    (printfunc)0,                      /* tp_print */
    (getattrfunc)0,       /* tp_getattr */
    (setattrfunc)0,       /* tp_setattr */
    (cmpfunc)0,           /* tp_compare */
    (reprfunc)0,             /* tp_repr */
    (PyNumberMethods*)0,     /* tp_as_number */
    (PySequenceMethods*)0, /* tp_as_sequence */
    (PyMappingMethods*)0,   /* tp_as_mapping */
    (hashfunc)0,             /* tp_hash */
    (ternaryfunc)0,          /* tp_call */
    (reprfunc)0,              /* tp_str */
    (getattrofunc)0,     /* tp_getattro */
    (setattrofunc)0,     /* tp_setattro */
    (PyBufferProcs*)0,  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,                      /* tp_flags */
    NULL,                        /* Documentation string */
    (traverseproc)0,     /* tp_traverse */
    (inquiry)0,             /* tp_clear */
    (richcmpfunc)0,   /* tp_richcompare */
    offsetof(PyGObject, weakreflist),             /* tp_weaklistoffset */
    (getiterfunc)0,          /* tp_iter */
    (iternextfunc)0,     /* tp_iternext */
    (struct PyMethodDef*)NULL, /* tp_methods */
    (struct PyMemberDef*)0,              /* tp_members */
    (struct PyGetSetDef*)0,  /* tp_getset */
    NULL,                              /* tp_base */
    NULL,                              /* tp_dict */
    (descrgetfunc)0,    /* tp_descr_get */
    (descrsetfunc)0,    /* tp_descr_set */
    offsetof(PyGObject, inst_dict),                 /* tp_dictoffset */
    (initproc)_wrap_gtk_image_scroll_win_new,             /* tp_init */
    (allocfunc)0,           /* tp_alloc */
    (newfunc)0,               /* tp_new */
    (freefunc)0,             /* tp_free */
    (inquiry)0              /* tp_is_gc */
};



/* ----------- GtkImageToolDragger ----------- */

 static int
_wrap_gtk_image_tool_dragger_new(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    GType obj_type = pyg_type_from_object((PyObject *) self);
    GParameter params[1];
    PyObject *parsed_args[1] = {NULL, };
    char *arg_names[] = {"view", NULL };
    char *prop_names[] = {"view", NULL };
    guint nparams, i;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O:None.ImageToolDragger.__init__" , arg_names , &parsed_args[0]))
        return -1;

    memset(params, 0, sizeof(GParameter)*1);
    if (!pyg_parse_constructor_args(obj_type, arg_names,
                                    prop_names, params, 
                                    &nparams, parsed_args))
        return -1;
    pygobject_constructv(self, nparams, params);
    for (i = 0; i < nparams; ++i)
        g_value_unset(&params[i].value);
    if (!self->obj) {
        PyErr_SetString(
            PyExc_RuntimeError, 
            "could not create None.ImageToolDragger object");
        return -1;
    }
    return 0;
}

PyTypeObject G_GNUC_INTERNAL PyGtkImageToolDragger_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                 /* ob_size */
    "ImageToolDragger",                   /* tp_name */
    sizeof(PyGObject),          /* tp_basicsize */
    0,                                 /* tp_itemsize */
    /* methods */
    (destructor)0,        /* tp_dealloc */
    (printfunc)0,                      /* tp_print */
    (getattrfunc)0,       /* tp_getattr */
    (setattrfunc)0,       /* tp_setattr */
    (cmpfunc)0,           /* tp_compare */
    (reprfunc)0,             /* tp_repr */
    (PyNumberMethods*)0,     /* tp_as_number */
    (PySequenceMethods*)0, /* tp_as_sequence */
    (PyMappingMethods*)0,   /* tp_as_mapping */
    (hashfunc)0,             /* tp_hash */
    (ternaryfunc)0,          /* tp_call */
    (reprfunc)0,              /* tp_str */
    (getattrofunc)0,     /* tp_getattro */
    (setattrofunc)0,     /* tp_setattro */
    (PyBufferProcs*)0,  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,                      /* tp_flags */
    NULL,                        /* Documentation string */
    (traverseproc)0,     /* tp_traverse */
    (inquiry)0,             /* tp_clear */
    (richcmpfunc)0,   /* tp_richcompare */
    offsetof(PyGObject, weakreflist),             /* tp_weaklistoffset */
    (getiterfunc)0,          /* tp_iter */
    (iternextfunc)0,     /* tp_iternext */
    (struct PyMethodDef*)NULL, /* tp_methods */
    (struct PyMemberDef*)0,              /* tp_members */
    (struct PyGetSetDef*)0,  /* tp_getset */
    NULL,                              /* tp_base */
    NULL,                              /* tp_dict */
    (descrgetfunc)0,    /* tp_descr_get */
    (descrsetfunc)0,    /* tp_descr_set */
    offsetof(PyGObject, inst_dict),                 /* tp_dictoffset */
    (initproc)_wrap_gtk_image_tool_dragger_new,             /* tp_init */
    (allocfunc)0,           /* tp_alloc */
    (newfunc)0,               /* tp_new */
    (freefunc)0,             /* tp_free */
    (inquiry)0              /* tp_is_gc */
};



/* ----------- GtkImageToolSelector ----------- */

 static int
_wrap_gtk_image_tool_selector_new(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    GType obj_type = pyg_type_from_object((PyObject *) self);
    GParameter params[1];
    PyObject *parsed_args[1] = {NULL, };
    char *arg_names[] = {"view", NULL };
    char *prop_names[] = {"view", NULL };
    guint nparams, i;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O:None.ImageToolSelector.__init__" , arg_names , &parsed_args[0]))
        return -1;

    memset(params, 0, sizeof(GParameter)*1);
    if (!pyg_parse_constructor_args(obj_type, arg_names,
                                    prop_names, params, 
                                    &nparams, parsed_args))
        return -1;
    pygobject_constructv(self, nparams, params);
    for (i = 0; i < nparams; ++i)
        g_value_unset(&params[i].value);
    if (!self->obj) {
        PyErr_SetString(
            PyExc_RuntimeError, 
            "could not create None.ImageToolSelector object");
        return -1;
    }
    return 0;
}

static PyObject *
_wrap_gtk_image_tool_selector_get_selection(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "rect", NULL };
    PyObject *py_rect;
    GdkRectangle rect = { 0, 0, 0, 0 };

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"O:GtkImageToolSelector.get_selection", kwlist, &py_rect))
        return NULL;
    if (!pygdk_rectangle_from_pyobject(py_rect, &rect))
        return NULL;
    
    gtk_image_tool_selector_get_selection(GTK_IMAGE_TOOL_SELECTOR(self->obj), &rect);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_tool_selector_set_selection(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "rect", NULL };
    PyObject *py_rect;
    GdkRectangle rect = { 0, 0, 0, 0 };

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"O:GtkImageToolSelector.set_selection", kwlist, &py_rect))
        return NULL;
    if (!pygdk_rectangle_from_pyobject(py_rect, &rect))
        return NULL;
    
    gtk_image_tool_selector_set_selection(GTK_IMAGE_TOOL_SELECTOR(self->obj), &rect);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static const PyMethodDef _PyGtkImageToolSelector_methods[] = {
    { "get_selection", (PyCFunction)_wrap_gtk_image_tool_selector_get_selection, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "set_selection", (PyCFunction)_wrap_gtk_image_tool_selector_set_selection, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { NULL, NULL, 0, NULL }
};

PyTypeObject G_GNUC_INTERNAL PyGtkImageToolSelector_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                 /* ob_size */
    "ImageToolSelector",                   /* tp_name */
    sizeof(PyGObject),          /* tp_basicsize */
    0,                                 /* tp_itemsize */
    /* methods */
    (destructor)0,        /* tp_dealloc */
    (printfunc)0,                      /* tp_print */
    (getattrfunc)0,       /* tp_getattr */
    (setattrfunc)0,       /* tp_setattr */
    (cmpfunc)0,           /* tp_compare */
    (reprfunc)0,             /* tp_repr */
    (PyNumberMethods*)0,     /* tp_as_number */
    (PySequenceMethods*)0, /* tp_as_sequence */
    (PyMappingMethods*)0,   /* tp_as_mapping */
    (hashfunc)0,             /* tp_hash */
    (ternaryfunc)0,          /* tp_call */
    (reprfunc)0,              /* tp_str */
    (getattrofunc)0,     /* tp_getattro */
    (setattrofunc)0,     /* tp_setattro */
    (PyBufferProcs*)0,  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,                      /* tp_flags */
    NULL,                        /* Documentation string */
    (traverseproc)0,     /* tp_traverse */
    (inquiry)0,             /* tp_clear */
    (richcmpfunc)0,   /* tp_richcompare */
    offsetof(PyGObject, weakreflist),             /* tp_weaklistoffset */
    (getiterfunc)0,          /* tp_iter */
    (iternextfunc)0,     /* tp_iternext */
    (struct PyMethodDef*)_PyGtkImageToolSelector_methods, /* tp_methods */
    (struct PyMemberDef*)0,              /* tp_members */
    (struct PyGetSetDef*)0,  /* tp_getset */
    NULL,                              /* tp_base */
    NULL,                              /* tp_dict */
    (descrgetfunc)0,    /* tp_descr_get */
    (descrsetfunc)0,    /* tp_descr_set */
    offsetof(PyGObject, inst_dict),                 /* tp_dictoffset */
    (initproc)_wrap_gtk_image_tool_selector_new,             /* tp_init */
    (allocfunc)0,           /* tp_alloc */
    (newfunc)0,               /* tp_new */
    (freefunc)0,             /* tp_free */
    (inquiry)0              /* tp_is_gc */
};



/* ----------- GtkImageView ----------- */

 static int
_wrap_gtk_image_view_new(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char* kwlist[] = { NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,
                                     ":None.ImageView.__init__",
                                     kwlist))
        return -1;

    pygobject_constructv(self, 0, NULL);
    if (!self->obj) {
        PyErr_SetString(
            PyExc_RuntimeError, 
            "could not create None.ImageView object");
        return -1;
    }
    return 0;
}

#line 60 "gtkimageview.override"
static PyObject*
_wrap_gtk_image_view_get_viewport (PyGObject *self)
{
    GdkRectangle rect;
    if (!gtk_image_view_get_viewport (GTK_IMAGE_VIEW (self->obj), &rect))
        return Py_None;
    return pyg_boxed_new (GDK_TYPE_RECTANGLE, &rect, TRUE, TRUE);
}
#line 524 "gtkimageview.c"


#line 70 "gtkimageview.override"
static PyObject*
_wrap_gtk_image_view_get_draw_rect (PyGObject *self)
{
    GdkRectangle rect;
    if (!gtk_image_view_get_draw_rect (GTK_IMAGE_VIEW (self->obj), &rect))
        return Py_None;
    return pyg_boxed_new (GDK_TYPE_RECTANGLE, &rect, TRUE, TRUE);
}

#line 537 "gtkimageview.c"


#line 51 "gtkimageview.override"
static PyObject*
_wrap_gtk_image_view_get_check_colors (PyGObject *self)
{
    int col1, col2;
    gtk_image_view_get_check_colors (GTK_IMAGE_VIEW (self->obj), &col1, &col2);
    return Py_BuildValue ("(ii)", col1, col2);
}
#line 548 "gtkimageview.c"


static PyObject *
_wrap_gtk_image_view_set_offset(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "x", "y", "invalidate", NULL };
    int invalidate = FALSE;
    double x, y;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"dd|i:GtkImageView.set_offset", kwlist, &x, &y, &invalidate))
        return NULL;
    
    gtk_image_view_set_offset(GTK_IMAGE_VIEW(self->obj), x, y, invalidate);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_view_set_transp(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "transp", "transp_color", NULL };
    PyObject *py_transp = NULL;
    int transp_color = 0x00000000;
    GtkImageTransp transp;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"O|i:GtkImageView.set_transp", kwlist, &py_transp, &transp_color))
        return NULL;
    if (pyg_enum_get_value(GTK_TYPE_IMAGE_TRANSP, py_transp, (gpointer)&transp))
        return NULL;
    
    gtk_image_view_set_transp(GTK_IMAGE_VIEW(self->obj), transp, transp_color);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_view_get_fitting(PyGObject *self)
{
    int ret;

    
    ret = gtk_image_view_get_fitting(GTK_IMAGE_VIEW(self->obj));
    
    return PyBool_FromLong(ret);

}

static PyObject *
_wrap_gtk_image_view_set_fitting(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "fitting", NULL };
    int fitting;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"i:GtkImageView.set_fitting", kwlist, &fitting))
        return NULL;
    
    gtk_image_view_set_fitting(GTK_IMAGE_VIEW(self->obj), fitting);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_view_get_pixbuf(PyGObject *self)
{
    GdkPixbuf *ret;

    
    ret = gtk_image_view_get_pixbuf(GTK_IMAGE_VIEW(self->obj));
    
    /* pygobject_new handles NULL checking */
    return pygobject_new((GObject *)ret);
}

static PyObject *
_wrap_gtk_image_view_set_pixbuf(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "pixbuf", "reset_fit", NULL };
    PyGObject *py_pixbuf;
    int reset_fit = TRUE;
    GdkPixbuf *pixbuf = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"O|i:GtkImageView.set_pixbuf", kwlist, &py_pixbuf, &reset_fit))
        return NULL;
    if (py_pixbuf && pygobject_check(py_pixbuf, &PyGdkPixbuf_Type))
        pixbuf = GDK_PIXBUF(py_pixbuf->obj);
    else if ((PyObject *)py_pixbuf != Py_None) {
        PyErr_SetString(PyExc_TypeError, "pixbuf should be a GdkPixbuf or None");
        return NULL;
    }
    
    gtk_image_view_set_pixbuf(GTK_IMAGE_VIEW(self->obj), (GdkPixbuf *) pixbuf, reset_fit);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_view_get_zoom(PyGObject *self)
{
    double ret;

    
    ret = gtk_image_view_get_zoom(GTK_IMAGE_VIEW(self->obj));
    
    return PyFloat_FromDouble(ret);
}

static PyObject *
_wrap_gtk_image_view_set_zoom(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "zoom", NULL };
    double zoom;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"d:GtkImageView.set_zoom", kwlist, &zoom))
        return NULL;
    
    gtk_image_view_set_zoom(GTK_IMAGE_VIEW(self->obj), zoom);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_view_set_black_bg(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "black_bg", NULL };
    int black_bg;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"i:GtkImageView.set_black_bg", kwlist, &black_bg))
        return NULL;
    
    gtk_image_view_set_black_bg(GTK_IMAGE_VIEW(self->obj), black_bg);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_view_get_black_bg(PyGObject *self)
{
    int ret;

    
    ret = gtk_image_view_get_black_bg(GTK_IMAGE_VIEW(self->obj));
    
    return PyBool_FromLong(ret);

}

static PyObject *
_wrap_gtk_image_view_set_show_frame(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "show_frame", NULL };
    int show_frame;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"i:GtkImageView.set_show_frame", kwlist, &show_frame))
        return NULL;
    
    gtk_image_view_set_show_frame(GTK_IMAGE_VIEW(self->obj), show_frame);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_view_get_show_frame(PyGObject *self)
{
    int ret;

    
    ret = gtk_image_view_get_show_frame(GTK_IMAGE_VIEW(self->obj));
    
    return PyBool_FromLong(ret);

}

static PyObject *
_wrap_gtk_image_view_set_interpolation(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "interp", NULL };
    PyObject *py_interp = NULL;
    GdkInterpType interp;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"O:GtkImageView.set_interpolation", kwlist, &py_interp))
        return NULL;
    if (pyg_enum_get_value(GDK_TYPE_INTERP_TYPE, py_interp, (gpointer)&interp))
        return NULL;
    
    gtk_image_view_set_interpolation(GTK_IMAGE_VIEW(self->obj), interp);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_view_get_interpolation(PyGObject *self)
{
    gint ret;

    
    ret = gtk_image_view_get_interpolation(GTK_IMAGE_VIEW(self->obj));
    
    return pyg_enum_from_gtype(GDK_TYPE_INTERP_TYPE, ret);
}

static PyObject *
_wrap_gtk_image_view_set_show_cursor(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "show_cursor", NULL };
    int show_cursor;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"i:GtkImageView.set_show_cursor", kwlist, &show_cursor))
        return NULL;
    
    gtk_image_view_set_show_cursor(GTK_IMAGE_VIEW(self->obj), show_cursor);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_view_get_show_cursor(PyGObject *self)
{
    int ret;

    
    ret = gtk_image_view_get_show_cursor(GTK_IMAGE_VIEW(self->obj));
    
    return PyBool_FromLong(ret);

}

static PyObject *
_wrap_gtk_image_view_set_tool(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "tool", NULL };
    PyGObject *tool;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"O!:GtkImageView.set_tool", kwlist, &PyGtkIImageTool_Type, &tool))
        return NULL;
    
    gtk_image_view_set_tool(GTK_IMAGE_VIEW(self->obj), GTK_IIMAGE_TOOL(tool->obj));
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_view_get_tool(PyGObject *self)
{
    GtkIImageTool *ret;

    
    ret = gtk_image_view_get_tool(GTK_IMAGE_VIEW(self->obj));
    
    /* pygobject_new handles NULL checking */
    return pygobject_new((GObject *)ret);
}

static PyObject *
_wrap_gtk_image_view_zoom_in(PyGObject *self)
{
    
    gtk_image_view_zoom_in(GTK_IMAGE_VIEW(self->obj));
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_image_view_zoom_out(PyGObject *self)
{
    
    gtk_image_view_zoom_out(GTK_IMAGE_VIEW(self->obj));
    
    Py_INCREF(Py_None);
    return Py_None;
}

static const PyMethodDef _PyGtkImageView_methods[] = {
    { "get_viewport", (PyCFunction)_wrap_gtk_image_view_get_viewport, METH_NOARGS,
      NULL },
    { "get_draw_rect", (PyCFunction)_wrap_gtk_image_view_get_draw_rect, METH_NOARGS,
      NULL },
    { "get_check_colors", (PyCFunction)_wrap_gtk_image_view_get_check_colors, METH_NOARGS,
      NULL },
    { "set_offset", (PyCFunction)_wrap_gtk_image_view_set_offset, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "set_transp", (PyCFunction)_wrap_gtk_image_view_set_transp, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "get_fitting", (PyCFunction)_wrap_gtk_image_view_get_fitting, METH_NOARGS,
      NULL },
    { "set_fitting", (PyCFunction)_wrap_gtk_image_view_set_fitting, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "get_pixbuf", (PyCFunction)_wrap_gtk_image_view_get_pixbuf, METH_NOARGS,
      NULL },
    { "set_pixbuf", (PyCFunction)_wrap_gtk_image_view_set_pixbuf, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "get_zoom", (PyCFunction)_wrap_gtk_image_view_get_zoom, METH_NOARGS,
      NULL },
    { "set_zoom", (PyCFunction)_wrap_gtk_image_view_set_zoom, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "set_black_bg", (PyCFunction)_wrap_gtk_image_view_set_black_bg, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "get_black_bg", (PyCFunction)_wrap_gtk_image_view_get_black_bg, METH_NOARGS,
      NULL },
    { "set_show_frame", (PyCFunction)_wrap_gtk_image_view_set_show_frame, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "get_show_frame", (PyCFunction)_wrap_gtk_image_view_get_show_frame, METH_NOARGS,
      NULL },
    { "set_interpolation", (PyCFunction)_wrap_gtk_image_view_set_interpolation, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "get_interpolation", (PyCFunction)_wrap_gtk_image_view_get_interpolation, METH_NOARGS,
      NULL },
    { "set_show_cursor", (PyCFunction)_wrap_gtk_image_view_set_show_cursor, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "get_show_cursor", (PyCFunction)_wrap_gtk_image_view_get_show_cursor, METH_NOARGS,
      NULL },
    { "set_tool", (PyCFunction)_wrap_gtk_image_view_set_tool, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "get_tool", (PyCFunction)_wrap_gtk_image_view_get_tool, METH_NOARGS,
      NULL },
    { "zoom_in", (PyCFunction)_wrap_gtk_image_view_zoom_in, METH_NOARGS,
      NULL },
    { "zoom_out", (PyCFunction)_wrap_gtk_image_view_zoom_out, METH_NOARGS,
      NULL },
    { NULL, NULL, 0, NULL }
};

PyTypeObject G_GNUC_INTERNAL PyGtkImageView_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                 /* ob_size */
    "ImageView",                   /* tp_name */
    sizeof(PyGObject),          /* tp_basicsize */
    0,                                 /* tp_itemsize */
    /* methods */
    (destructor)0,        /* tp_dealloc */
    (printfunc)0,                      /* tp_print */
    (getattrfunc)0,       /* tp_getattr */
    (setattrfunc)0,       /* tp_setattr */
    (cmpfunc)0,           /* tp_compare */
    (reprfunc)0,             /* tp_repr */
    (PyNumberMethods*)0,     /* tp_as_number */
    (PySequenceMethods*)0, /* tp_as_sequence */
    (PyMappingMethods*)0,   /* tp_as_mapping */
    (hashfunc)0,             /* tp_hash */
    (ternaryfunc)0,          /* tp_call */
    (reprfunc)0,              /* tp_str */
    (getattrofunc)0,     /* tp_getattro */
    (setattrofunc)0,     /* tp_setattro */
    (PyBufferProcs*)0,  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,                      /* tp_flags */
    NULL,                        /* Documentation string */
    (traverseproc)0,     /* tp_traverse */
    (inquiry)0,             /* tp_clear */
    (richcmpfunc)0,   /* tp_richcompare */
    offsetof(PyGObject, weakreflist),             /* tp_weaklistoffset */
    (getiterfunc)0,          /* tp_iter */
    (iternextfunc)0,     /* tp_iternext */
    (struct PyMethodDef*)_PyGtkImageView_methods, /* tp_methods */
    (struct PyMemberDef*)0,              /* tp_members */
    (struct PyGetSetDef*)0,  /* tp_getset */
    NULL,                              /* tp_base */
    NULL,                              /* tp_dict */
    (descrgetfunc)0,    /* tp_descr_get */
    (descrsetfunc)0,    /* tp_descr_set */
    offsetof(PyGObject, inst_dict),                 /* tp_dictoffset */
    (initproc)_wrap_gtk_image_view_new,             /* tp_init */
    (allocfunc)0,           /* tp_alloc */
    (newfunc)0,               /* tp_new */
    (freefunc)0,             /* tp_free */
    (inquiry)0              /* tp_is_gc */
};



/* ----------- GtkAnimView ----------- */

static int
_wrap_gtk_anim_view_new(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char* kwlist[] = { NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,
                                     ":None.AnimView.__init__",
                                     kwlist))
        return -1;

    pygobject_constructv(self, 0, NULL);
    if (!self->obj) {
        PyErr_SetString(
            PyExc_RuntimeError, 
            "could not create None.AnimView object");
        return -1;
    }
    return 0;
}

static PyObject *
_wrap_gtk_anim_view_get_anim(PyGObject *self)
{
    GdkPixbufAnimation *ret;

    
    ret = gtk_anim_view_get_anim(GTK_ANIM_VIEW(self->obj));
    
    /* pygobject_new handles NULL checking */
    return pygobject_new((GObject *)ret);
}

static PyObject *
_wrap_gtk_anim_view_set_anim(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "anim", NULL };
    PyGObject *anim;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"O!:GtkAnimView.set_anim", kwlist, &PyGdkPixbufAnimation_Type, &anim))
        return NULL;
    
    gtk_anim_view_set_anim(GTK_ANIM_VIEW(self->obj), GDK_PIXBUF_ANIMATION(anim->obj));
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_anim_view_set_is_playing(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "playing", NULL };
    int playing;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"i:GtkAnimView.set_is_playing", kwlist, &playing))
        return NULL;
    
    gtk_anim_view_set_is_playing(GTK_ANIM_VIEW(self->obj), playing);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_anim_view_get_is_playing(PyGObject *self)
{
    int ret;

    
    ret = gtk_anim_view_get_is_playing(GTK_ANIM_VIEW(self->obj));
    
    return PyBool_FromLong(ret);

}

static PyObject *
_wrap_gtk_anim_view_step(PyGObject *self)
{
    
    gtk_anim_view_step(GTK_ANIM_VIEW(self->obj));
    
    Py_INCREF(Py_None);
    return Py_None;
}

static const PyMethodDef _PyGtkAnimView_methods[] = {
    { "get_anim", (PyCFunction)_wrap_gtk_anim_view_get_anim, METH_NOARGS,
      NULL },
    { "set_anim", (PyCFunction)_wrap_gtk_anim_view_set_anim, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "set_is_playing", (PyCFunction)_wrap_gtk_anim_view_set_is_playing, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "get_is_playing", (PyCFunction)_wrap_gtk_anim_view_get_is_playing, METH_NOARGS,
      NULL },
    { "step", (PyCFunction)_wrap_gtk_anim_view_step, METH_NOARGS,
      NULL },
    { NULL, NULL, 0, NULL }
};

PyTypeObject G_GNUC_INTERNAL PyGtkAnimView_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                 /* ob_size */
    "AnimView",                   /* tp_name */
    sizeof(PyGObject),          /* tp_basicsize */
    0,                                 /* tp_itemsize */
    /* methods */
    (destructor)0,        /* tp_dealloc */
    (printfunc)0,                      /* tp_print */
    (getattrfunc)0,       /* tp_getattr */
    (setattrfunc)0,       /* tp_setattr */
    (cmpfunc)0,           /* tp_compare */
    (reprfunc)0,             /* tp_repr */
    (PyNumberMethods*)0,     /* tp_as_number */
    (PySequenceMethods*)0, /* tp_as_sequence */
    (PyMappingMethods*)0,   /* tp_as_mapping */
    (hashfunc)0,             /* tp_hash */
    (ternaryfunc)0,          /* tp_call */
    (reprfunc)0,              /* tp_str */
    (getattrofunc)0,     /* tp_getattro */
    (setattrofunc)0,     /* tp_setattro */
    (PyBufferProcs*)0,  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,                      /* tp_flags */
    NULL,                        /* Documentation string */
    (traverseproc)0,     /* tp_traverse */
    (inquiry)0,             /* tp_clear */
    (richcmpfunc)0,   /* tp_richcompare */
    offsetof(PyGObject, weakreflist),             /* tp_weaklistoffset */
    (getiterfunc)0,          /* tp_iter */
    (iternextfunc)0,     /* tp_iternext */
    (struct PyMethodDef*)_PyGtkAnimView_methods, /* tp_methods */
    (struct PyMemberDef*)0,              /* tp_members */
    (struct PyGetSetDef*)0,  /* tp_getset */
    NULL,                              /* tp_base */
    NULL,                              /* tp_dict */
    (descrgetfunc)0,    /* tp_descr_get */
    (descrsetfunc)0,    /* tp_descr_set */
    offsetof(PyGObject, inst_dict),                 /* tp_dictoffset */
    (initproc)_wrap_gtk_anim_view_new,             /* tp_init */
    (allocfunc)0,           /* tp_alloc */
    (newfunc)0,               /* tp_new */
    (freefunc)0,             /* tp_free */
    (inquiry)0              /* tp_is_gc */
};



/* ----------- GtkIImageTool ----------- */

static PyObject *
_wrap_gtk_iimage_tool_button_press(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "ev", NULL };
    GdkEvent *ev = NULL;
    PyObject *py_ev;
    int ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"O:GtkIImageTool.button_press", kwlist, &py_ev))
        return NULL;
    if (pyg_boxed_check(py_ev, GDK_TYPE_EVENT))
        ev = pyg_boxed_get(py_ev, GdkEvent);
    else {
        PyErr_SetString(PyExc_TypeError, "ev should be a GdkEvent");
        return NULL;
    }
    
    ret = gtk_iimage_tool_button_press(GTK_IIMAGE_TOOL(self->obj), (GdkEventButton *)ev);
    
    return PyBool_FromLong(ret);

}

static PyObject *
_wrap_gtk_iimage_tool_button_release(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "ev", NULL };
    GdkEvent *ev = NULL;
    PyObject *py_ev;
    int ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"O:GtkIImageTool.button_release", kwlist, &py_ev))
        return NULL;
    if (pyg_boxed_check(py_ev, GDK_TYPE_EVENT))
        ev = pyg_boxed_get(py_ev, GdkEvent);
    else {
        PyErr_SetString(PyExc_TypeError, "ev should be a GdkEvent");
        return NULL;
    }
    
    ret = gtk_iimage_tool_button_release(GTK_IIMAGE_TOOL(self->obj), (GdkEventButton *)ev);
    
    return PyBool_FromLong(ret);

}

static PyObject *
_wrap_gtk_iimage_tool_motion_notify(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "ev", NULL };
    GdkEvent *ev = NULL;
    PyObject *py_ev;
    int ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"O:GtkIImageTool.motion_notify", kwlist, &py_ev))
        return NULL;
    if (pyg_boxed_check(py_ev, GDK_TYPE_EVENT))
        ev = pyg_boxed_get(py_ev, GdkEvent);
    else {
        PyErr_SetString(PyExc_TypeError, "ev should be a GdkEvent");
        return NULL;
    }
    
    ret = gtk_iimage_tool_motion_notify(GTK_IIMAGE_TOOL(self->obj), (GdkEventMotion *)ev);
    
    return PyBool_FromLong(ret);

}

static PyObject *
_wrap_gtk_iimage_tool_pixbuf_changed(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "reset_fit", NULL };
    int reset_fit;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"i:GtkIImageTool.pixbuf_changed", kwlist, &reset_fit))
        return NULL;
    
    gtk_iimage_tool_pixbuf_changed(GTK_IIMAGE_TOOL(self->obj), reset_fit);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_wrap_gtk_iimage_tool_cursor_at_point(PyGObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "x", "y", NULL };
    int x, y;
    GdkCursor *ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"ii:GtkIImageTool.cursor_at_point", kwlist, &x, &y))
        return NULL;
    
    ret = gtk_iimage_tool_cursor_at_point(GTK_IIMAGE_TOOL(self->obj), x, y);
    
    /* pyg_boxed_new handles NULL checking */
    return pyg_boxed_new(GDK_TYPE_CURSOR, ret, TRUE, TRUE);
}

static const PyMethodDef _PyGtkIImageTool_methods[] = {
    { "button_press", (PyCFunction)_wrap_gtk_iimage_tool_button_press, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "button_release", (PyCFunction)_wrap_gtk_iimage_tool_button_release, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "motion_notify", (PyCFunction)_wrap_gtk_iimage_tool_motion_notify, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "pixbuf_changed", (PyCFunction)_wrap_gtk_iimage_tool_pixbuf_changed, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "cursor_at_point", (PyCFunction)_wrap_gtk_iimage_tool_cursor_at_point, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { NULL, NULL, 0, NULL }
};

PyTypeObject G_GNUC_INTERNAL PyGtkIImageTool_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                 /* ob_size */
    "IImageTool",                   /* tp_name */
    sizeof(PyObject),          /* tp_basicsize */
    0,                                 /* tp_itemsize */
    /* methods */
    (destructor)0,        /* tp_dealloc */
    (printfunc)0,                      /* tp_print */
    (getattrfunc)0,       /* tp_getattr */
    (setattrfunc)0,       /* tp_setattr */
    (cmpfunc)0,           /* tp_compare */
    (reprfunc)0,             /* tp_repr */
    (PyNumberMethods*)0,     /* tp_as_number */
    (PySequenceMethods*)0, /* tp_as_sequence */
    (PyMappingMethods*)0,   /* tp_as_mapping */
    (hashfunc)0,             /* tp_hash */
    (ternaryfunc)0,          /* tp_call */
    (reprfunc)0,              /* tp_str */
    (getattrofunc)0,     /* tp_getattro */
    (setattrofunc)0,     /* tp_setattro */
    (PyBufferProcs*)0,  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,                      /* tp_flags */
    NULL,                        /* Documentation string */
    (traverseproc)0,     /* tp_traverse */
    (inquiry)0,             /* tp_clear */
    (richcmpfunc)0,   /* tp_richcompare */
    0,             /* tp_weaklistoffset */
    (getiterfunc)0,          /* tp_iter */
    (iternextfunc)0,     /* tp_iternext */
    (struct PyMethodDef*)_PyGtkIImageTool_methods, /* tp_methods */
    (struct PyMemberDef*)0,              /* tp_members */
    (struct PyGetSetDef*)0,  /* tp_getset */
    NULL,                              /* tp_base */
    NULL,                              /* tp_dict */
    (descrgetfunc)0,    /* tp_descr_get */
    (descrsetfunc)0,    /* tp_descr_set */
    0,                 /* tp_dictoffset */
    (initproc)0,             /* tp_init */
    (allocfunc)0,           /* tp_alloc */
    (newfunc)0,               /* tp_new */
    (freefunc)0,             /* tp_free */
    (inquiry)0              /* tp_is_gc */
};



/* ----------- functions ----------- */

static PyObject *
_wrap_gtk_zooms_get_zoom_in(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "zoom", NULL };
    double zoom, ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"d:zooms_get_zoom_in", kwlist, &zoom))
        return NULL;
    
    ret = gtk_zooms_get_zoom_in(zoom);
    
    return PyFloat_FromDouble(ret);
}

static PyObject *
_wrap_gtk_zooms_get_zoom_out(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "zoom", NULL };
    double zoom, ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"d:zooms_get_zoom_out", kwlist, &zoom))
        return NULL;
    
    ret = gtk_zooms_get_zoom_out(zoom);
    
    return PyFloat_FromDouble(ret);
}

static PyObject *
_wrap_gtk_zooms_get_min_zoom(PyObject *self)
{
    double ret;

    
    ret = gtk_zooms_get_min_zoom();
    
    return PyFloat_FromDouble(ret);
}

static PyObject *
_wrap_gtk_zooms_get_max_zoom(PyObject *self)
{
    double ret;

    
    ret = gtk_zooms_get_max_zoom();
    
    return PyFloat_FromDouble(ret);
}

static PyObject *
_wrap_gtk_zooms_clamp_zoom(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "zoom", NULL };
    double zoom, ret;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,"d:zooms_clamp_zoom", kwlist, &zoom))
        return NULL;
    
    ret = gtk_zooms_clamp_zoom(zoom);
    
    return PyFloat_FromDouble(ret);
}

const PyMethodDef gtkimageview_functions[] = {
    { "zooms_get_zoom_in", (PyCFunction)_wrap_gtk_zooms_get_zoom_in, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "zooms_get_zoom_out", (PyCFunction)_wrap_gtk_zooms_get_zoom_out, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { "zooms_get_min_zoom", (PyCFunction)_wrap_gtk_zooms_get_min_zoom, METH_NOARGS,
      NULL },
    { "zooms_get_max_zoom", (PyCFunction)_wrap_gtk_zooms_get_max_zoom, METH_NOARGS,
      NULL },
    { "zooms_clamp_zoom", (PyCFunction)_wrap_gtk_zooms_clamp_zoom, METH_VARARGS|METH_KEYWORDS,
      NULL },
    { NULL, NULL, 0, NULL }
};


/* ----------- enums and flags ----------- */

void
gtkimageview_add_constants(PyObject *module, const gchar *strip_prefix)
{
  pyg_enum_add(module, "ImageTransp", strip_prefix, GTK_TYPE_IMAGE_TRANSP);

  if (PyErr_Occurred())
    PyErr_Print();
}

/* initialise stuff extension classes */
void
gtkimageview_register_classes(PyObject *d)
{
    PyObject *module;

    if ((module = PyImport_ImportModule("gobject")) != NULL) {
        _PyGObject_Type = (PyTypeObject *)PyObject_GetAttrString(module, "GObject");
        if (_PyGObject_Type == NULL) {
            PyErr_SetString(PyExc_ImportError,
                "cannot import name GObject from gobject");
            return ;
        }
    } else {
        PyErr_SetString(PyExc_ImportError,
            "could not import gobject");
        return ;
    }
    if ((module = PyImport_ImportModule("gtk")) != NULL) {
        _PyGtkWidget_Type = (PyTypeObject *)PyObject_GetAttrString(module, "Widget");
        if (_PyGtkWidget_Type == NULL) {
            PyErr_SetString(PyExc_ImportError,
                "cannot import name Widget from gtk");
            return ;
        }
        _PyGtkWindow_Type = (PyTypeObject *)PyObject_GetAttrString(module, "Window");
        if (_PyGtkWindow_Type == NULL) {
            PyErr_SetString(PyExc_ImportError,
                "cannot import name Window from gtk");
            return ;
        }
        _PyGtkTable_Type = (PyTypeObject *)PyObject_GetAttrString(module, "Table");
        if (_PyGtkTable_Type == NULL) {
            PyErr_SetString(PyExc_ImportError,
                "cannot import name Table from gtk");
            return ;
        }
    } else {
        PyErr_SetString(PyExc_ImportError,
            "could not import gtk");
        return ;
    }
    if ((module = PyImport_ImportModule("gtk.gdk")) != NULL) {
        _PyGdkPixbuf_Type = (PyTypeObject *)PyObject_GetAttrString(module, "Pixbuf");
        if (_PyGdkPixbuf_Type == NULL) {
            PyErr_SetString(PyExc_ImportError,
                "cannot import name Pixbuf from gtk.gdk");
            return ;
        }
        _PyGdkPixbufAnimation_Type = (PyTypeObject *)PyObject_GetAttrString(module, "PixbufAnimation");
        if (_PyGdkPixbufAnimation_Type == NULL) {
            PyErr_SetString(PyExc_ImportError,
                "cannot import name PixbufAnimation from gtk.gdk");
            return ;
        }
    } else {
        PyErr_SetString(PyExc_ImportError,
            "could not import gtk.gdk");
        return ;
    }


#line 1392 "gtkimageview.c"
    pyg_register_interface(d, "IImageTool", GTK_TYPE_IIMAGE_TOOL, &PyGtkIImageTool_Type);
    pygobject_register_class(d, "GtkImageNav", GTK_TYPE_IMAGE_NAV, &PyGtkImageNav_Type, Py_BuildValue("(O)", &PyGtkWindow_Type));
    pyg_set_object_has_new_constructor(GTK_TYPE_IMAGE_NAV);
    pygobject_register_class(d, "GtkImageScrollWin", GTK_TYPE_IMAGE_SCROLL_WIN, &PyGtkImageScrollWin_Type, Py_BuildValue("(O)", &PyGtkTable_Type));
    pyg_set_object_has_new_constructor(GTK_TYPE_IMAGE_SCROLL_WIN);
    pygobject_register_class(d, "GtkImageToolDragger", GTK_TYPE_IMAGE_TOOL_DRAGGER, &PyGtkImageToolDragger_Type, Py_BuildValue("(O)", &PyGObject_Type));
    pyg_set_object_has_new_constructor(GTK_TYPE_IMAGE_TOOL_DRAGGER);
    pygobject_register_class(d, "GtkImageToolSelector", GTK_TYPE_IMAGE_TOOL_SELECTOR, &PyGtkImageToolSelector_Type, Py_BuildValue("(O)", &PyGObject_Type));
    pyg_set_object_has_new_constructor(GTK_TYPE_IMAGE_TOOL_SELECTOR);
    pygobject_register_class(d, "GtkImageView", GTK_TYPE_IMAGE_VIEW, &PyGtkImageView_Type, Py_BuildValue("(O)", &PyGtkWidget_Type));
    pyg_set_object_has_new_constructor(GTK_TYPE_IMAGE_VIEW);
    pygobject_register_class(d, "GtkAnimView", GTK_TYPE_ANIM_VIEW, &PyGtkAnimView_Type, Py_BuildValue("(O)", &PyGtkImageView_Type));
    pyg_set_object_has_new_constructor(GTK_TYPE_ANIM_VIEW);
}
