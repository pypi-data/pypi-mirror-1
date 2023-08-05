/* Dummy header used to force inclusion of extra interface via scintilla.override */

/* Misc higher level calls */
PyObject* gtk_scintilla_get_selection(GtkScintilla* sci,);
PyObject* gtk_scintilla_set_selection(GtkScintilla* sci, int start, int end);
PyObject* gtk_scintilla_get_target(GtkScintilla* sci);
PyObject* gtk_scintilla_set_target(GtkScintilla* sci, int start, int end);
PyObject* gtk_scintilla_scroll_to_line(GtkScintilla* sci, int line, int hpos);

/* High-level folding interface */
PyObject *gtk_scintilla_enable_folding(GtkScintilla* sci, int enable, int style, int internal);
PyObject *gtk_scintilla_fold_all(GtkScintilla* sci, int expand);
PyObject *gtk_scintilla_expand_more(GtkScintilla* sci, int lineno);
PyObject *gtk_scintilla_collapse_more(GtkScintilla* sci, int lineno);
PyObject *gtk_scintilla_expand_recursive(GtkScintilla* sci, int lineno);
PyObject *gtk_scintilla_collapse_recursive(GtkScintilla* sci, int lineno);
PyObject *gtk_scintilla_get_fold_expansion(GtkScintilla* sci, int lineno);

/* Macro support */
PyObject *gtk_scintilla_macro_action(GtkScintilla* sci, PyObject *args);

