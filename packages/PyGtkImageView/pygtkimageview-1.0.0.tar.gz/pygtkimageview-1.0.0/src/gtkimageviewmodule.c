#include <pygobject.h>
#include <pygtk/pygtk.h>

void gtkimageview_register_classes (PyObject *d);
void gtkimageview_add_constants (PyObject *m, char *prefix);

extern PyMethodDef gtkimageview_functions[];

DL_EXPORT(void)
init_gtkimageview (void)
{
    PyObject *m, *d;

    init_pygobject ();
    init_pygtk ();

    m = Py_InitModule ("_gtkimageview", gtkimageview_functions);
    d = PyModule_GetDict (m);

    gtkimageview_register_classes (d);
    gtkimageview_add_constants (m, "GTK_IMAGE_");
}
