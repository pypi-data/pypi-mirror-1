/* -*- Mode: C; c-basic-offset: 4 -*- */

#define NO_IMPORT
#include <pygobject.h>
#include <pygtk/pygtk.h>

void pyscintilla_register_classes (PyObject *d);
/*void pyscintilla_add_constants(PyObject *module, const gchar *strip_prefix);*/

extern PyMethodDef pyscintilla_functions[];

DL_EXPORT(void)
init_scintilla(void)
{
    PyObject *m, *d;

    /* initialise gobject */
    init_pygobject();
    init_pygtk();
    g_assert(pygobject_register_class != NULL);


    m = Py_InitModule ("_scintilla", pyscintilla_functions);
    d = PyModule_GetDict (m);
	
    pyscintilla_register_classes (d);
    /* pyscintilla_add_constants(m, "SCINTILLA_"); */

    if (PyErr_Occurred ()) {
	Py_FatalError ("can't initialise module _scintilla");
    }
    
}
