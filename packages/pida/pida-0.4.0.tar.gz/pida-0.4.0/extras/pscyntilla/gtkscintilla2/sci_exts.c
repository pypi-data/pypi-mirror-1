/******************************************************************************
* A set of extensions for GtkScintilla:  Fast folding (in C for performance), 
* macro support (needs low-level access to scintilla for fast macro playback),
* and win32 printing support (uses win32 API calls not available in Python)
*
* Copyright (c) 1999-2003, Archaeopteryx Software, Inc.  All rights reserved.
*
* Contact: info@wingide.com
*
******************************************************************************/


#include <Python.h>
#include <pygobject.h>
#include "gtkscintilla.h"
#include "Scintilla.h"


/******************************************************************************
* High-level folding implementation
******************************************************************************/

// Define this to use the internal folding implementation, which does
// some basic performance critical work here in C++ rather than passing the
// FOLDCHANGED modification signal to Python.
// XXX Now that I've debugged this, it's not clear it's still needed in the
// XXX current scintilla implementation!  Let's see if leaving it off
// XXX causes any problems.
//#define INTERNAL_FOLDING
#ifdef INTERNAL_FOLDING
extern PyObject *gInternalFoldingMap;
#endif

// Map used to avoid fatal recursion during FoldExpandAll through gtk fold
// changed notification mechanism
#ifdef INTERNAL_FOLDING
static PyObject *gFoldRecursionMap = NULL;
#endif

#define kExpandAll -1
#define kCollapseAll -2

// Fill a map from fold level to values of 0 or 1 to indicate whether
// or not all folds at that level are expanded.  Starts at given line
// number and processes all its children
static void __ComputeFoldDepths(GtkScintilla *scint, int *lineno,
                                PyObject *level_map) {

  // Find level and end of this line's fold range
  int level = gtk_scintilla_get_fold_level(scint, *lineno);
  int maxline = gtk_scintilla_get_last_child(scint, *lineno, level & SC_FOLDLEVELNUMBERMASK);
  
  // Move to next line if this isn't a fold header
  if (!(level & SC_FOLDLEVELHEADERFLAG)) {
    (*lineno)++;
    return;
  }
    
  // Add this fold point to the level map
  {
    int expanded = gtk_scintilla_get_fold_expanded(scint, *lineno);
    PyObject *dict_key = PyInt_FromLong(level & SC_FOLDLEVELNUMBERMASK);
    if (!expanded) {
      PyObject *dict_value = PyInt_FromLong(0);
      PyDict_SetItem(level_map, dict_key, dict_value);
      Py_DECREF(dict_value);
    }
    else if (!PyMapping_HasKey(level_map, dict_key)) {
      PyObject *dict_value = PyInt_FromLong(1);
      PyDict_SetItem(level_map, dict_key, dict_value);
      Py_DECREF(dict_value);
    }
    Py_DECREF(dict_key);
  }
  
  // Process also any children recursively
  (*lineno)++;
  while (*lineno <= maxline)
    __ComputeFoldDepths(scint, lineno, level_map);
}

// Do recursive expand/collapse on scintilla starting at given line.  The
// fold level of lineno must be passed in level.  Pass levels set to 
// one of kExpandAll to expand to maximum depth, kCollapseAll to collapse 
// everything, or a level number to expand all up to and including that 
// level and collapse everything below.
static int __FoldForceRecursive(GtkScintilla *scint, int lineno, int level, 
                                int levels, int visible) {

  // Operate on all children belonging to this line
  int maxline = gtk_scintilla_get_last_child(scint, lineno, level & SC_FOLDLEVELNUMBERMASK);
  //printf("FOLD FORCE RECURSIVE FROM %ld to %ld\n", lineno, maxline);
  lineno++;
  while (lineno <= maxline) {
    int expand;
    
    // Determine operation for this line
    int line_level = gtk_scintilla_get_fold_level(scint, lineno);
    if (levels == kExpandAll) {
      expand = 1;
      visible = 1;
    }
    else if (levels == kCollapseAll) {
      expand = 0;
      visible = 0;
    }
    else {
      expand = ((line_level & SC_FOLDLEVELNUMBERMASK) <= levels);
    }
      
    // Show or hide the child itself
    if (visible)
      gtk_scintilla_show_lines(scint, lineno, lineno);
    else
      gtk_scintilla_hide_lines(scint, lineno, lineno);
      
    // Recurse on this child only if it's a fold point
    if (line_level & SC_FOLDLEVELHEADERFLAG) {
      if (expand)
        gtk_scintilla_set_fold_expanded(scint, lineno, 1);
      else
        gtk_scintilla_set_fold_expanded(scint, lineno, 0);
      lineno = __FoldForceRecursive(scint, lineno, line_level, levels, expand);
    }
    
    // Skip line that's not a fold point
    else
      lineno++;
  }
  
  // Recursive calls return line to which they processed
  return lineno;
}

// Get fold level information about the given line.  Returns the fold level of
// the line itself in this_level, the second to last fully expanded level 
// in prev_exp_level, the last fully expanded level in exp_level, and
// the first unexpanded level in first_unexpanded.
static void __GetFoldExpansion(GtkScintilla *scint, int lineno, int *this_level, 
                               int *prev_exp_level, int *exp_level, int *first_unexpanded) {

  PyObject *fold_map = NULL;
  PyObject *keys = NULL;
  int max_key;
  
  // Bail out if it's not a fold point
  int level = gtk_scintilla_get_fold_level(scint, lineno);
  if (!(level & SC_FOLDLEVELHEADERFLAG)) {
    *this_level = -1;
    *prev_exp_level = -1;
    *exp_level = -1;
    *first_unexpanded = -1;
    return;
  }
    
  // Special case fully collapsed node which isn't handled right by rest of code
  *this_level = level & SC_FOLDLEVELNUMBERMASK;
  if (!gtk_scintilla_get_fold_expanded(scint, lineno)) {
    *prev_exp_level = -1;
    *exp_level = -1;
    *first_unexpanded = *this_level;
    return;
  }
  
  // Compute expansion levels
  {
    int seek_lineno = lineno;
    fold_map = PyDict_New();

    if (!fold_map) {
      PyErr_NoMemory();
      return;
    }
    __ComputeFoldDepths(scint, &seek_lineno, fold_map);
  }
  
  // Find first unexpanded level and list of expanded levels
  {
    int num_expanded = 0;
    int i;
    *first_unexpanded = -1;
    *exp_level = -1;
    *prev_exp_level = -1;
    keys = PyDict_Keys(fold_map);
    max_key = PyList_Size(keys);
    for (i = 0; i < max_key; i++) {
      PyObject *key = PyList_GetItem(keys, i);            // borrowed ref
      PyObject *value = PyDict_GetItem(fold_map, key);    // borrowed ref
      int level = PyInt_AsLong(key);
      int expanded = PyInt_AsLong(value);
      if (expanded) {
	num_expanded++;
	if (level > *exp_level) {
	  *prev_exp_level = *exp_level;
	  *exp_level = level;
	}
	else if (level > *prev_exp_level) {
	  *prev_exp_level = level;
	}
      }
      else {
	if (*first_unexpanded == -1)
	  *first_unexpanded = level;
	else
	  *first_unexpanded = MIN(*first_unexpanded, level);
      }
    }
    if (num_expanded == 1)
      *prev_exp_level = *this_level;
  }  

  // Free temporary objects
  Py_DECREF(fold_map);
  Py_DECREF(keys);
}

// Implements response to fold change notification from scintilla.
// This updates the fold expansion record and makes sure to make all
// lines in expanded fold are visible to avoid ranges that are invisible
// without a fold point.
// This gets called when a fold point is changed, including during 
// initial styling for every fold point in the document... which is
// one area where passing this out to Python is quite slow.
#ifdef INTERNAL_FOLDING
static void __FoldChanged(GtkScintilla *scint, int lineno, int fold_now, int fold_prev) {
  
  // Changing to fold heading: Need to make sure it's set to being expanded so it
  // shows a '-' and not a '+' mark
  if ((fold_now & SC_FOLDLEVELHEADERFLAG) && (!(fold_prev & SC_FOLDLEVELHEADERFLAG))) {
    //printf("CHANGE TO FOLD HEADER: %ld\n", lineno);
    gtk_scintilla_set_fold_expanded(scint, lineno, 1);
  }
  
  // Changing to fold non-header:  Need to recursively force expansion
  // of any collapsed children
  else if ((!(fold_now & SC_FOLDLEVELHEADERFLAG)) && (fold_prev & SC_FOLDLEVELHEADERFLAG)) {
    //printf("CHANGE TO FOLD NON-HEADER: %ld\n", lineno);

    // Allocate fold recursion map on first call
    if (gFoldRecursionMap == NULL) {
      gFoldRecursionMap = PyDict_New();
      if (gFoldRecursionMap == NULL) {
	  Py_FatalError ("failed to allocate gFoldRecursionMap");
      }
    }
    
    // Bail out if already called down to FoldForceRecursive() through here
    // for this scintilla object
    // XXX This is somewhat of a kludge but I think it's probably OK
    char ehex[128];
    PyObject *pyone = PyInt_FromLong(1);
    sprintf(ehex, "%x", int(scint));
    if (PyDict_GetItemString(gFoldRecursionMap, ehex) != NULL) {
      //printf ("BAILING OUT\n");
      return;
    }

    // Otherwise, force expansion of all children of the line and the
    // line itself
    PyDict_SetItemString(gFoldRecursionMap, ehex, pyone);
    __FoldForceRecursive(scint, lineno, fold_prev, kExpandAll, 1);
    PyDict_DelItemString(gFoldRecursionMap, ehex);
  } 
}
#endif

// Utility to fold or expand all fold points in the document
static void __FoldAll(GtkScintilla *scint, int expand) {
  int maxline = gtk_scintilla_get_line_count(scint);
  int seek;

  // Make sure all of document is lexed
  gtk_scintilla_colourise(scint, 0, -1);
    
  // Process all fold points
  for (seek = 0; seek < maxline; seek++) {
    int level = gtk_scintilla_get_fold_level(scint, seek);
    if (level & SC_FOLDLEVELHEADERFLAG) {

      // Expand everything in the document
      if (expand) {
        gtk_scintilla_set_fold_expanded(scint, seek, 1);
        __FoldForceRecursive(scint, seek, level, kExpandAll, 1);
      }
      
      // Collapse everything to all depths
      else {
        gtk_scintilla_set_fold_expanded(scint, seek, 0);
        __FoldForceRecursive(scint, seek, level, kCollapseAll, 1);
      }
    }
  }
}

#ifdef INTERNAL_FOLDING
PyObject *gInternalFoldingMap = NULL;

static void
internal_folding_cb (GObject *w, gint param, gpointer notif, gpointer data)
{
  struct SCNotification *scn = (struct SCNotification *) notif;
  gchar *signal = "sci-notify";
  guint signal_id;
  GQuark detail;

  if (scn->nmhdr.code == SCN_MODIFIED && scn->modificationType & SC_MOD_CHANGEFOLD) {

    __FoldChanged(GTK_SCINTILLA(data), scn->line, scn->foldLevelNow, scn->foldLevelPrev);
		  
    if (g_signal_parse_name(signal, G_OBJECT_TYPE(w), &signal_id, &detail, TRUE)) {
      g_signal_stop_emission(w, signal_id, detail);
    }
  }
}
#endif

// Local utility
static void _define_marker(GtkScintilla *scint, int marker, int markerType, int fore, int back) {
  gtk_scintilla_marker_define(scint, marker, markerType);
  gtk_scintilla_marker_set_fore(scint, marker, fore);
  gtk_scintilla_marker_set_back(scint, marker, back);
}


/******************************************************************************
* Macro support
******************************************************************************/

// Not yet converted:  Probably want to move what's needed in gtkscintilla2
// and pyscintilla2 core instead (mainly need access to scintilla_send_message()
// so values reported in macro record signals can be replayed)
#define DISABLE_MACROS

#ifndef DISABLE_MACROS
// Utility to build SCN_MACRORECORD parameters in python form.
// Should be symmetrical with _wrap_scintilla_macro_action below.
static PyObject *_build_macro_parms(SCNotification *scn) {

  PyObject *pyparm = NULL;
  switch (scn->message) {

  // Package message parameters for those that have them
  case SCI_REPLACESEL: {
    const char *txt = reinterpret_cast<char *>(scn->lParam);
    pyparm = Py_BuildValue("iis", scn->nmhdr.code, scn->message, txt);
    break;
  }
  case SCI_ADDTEXT: {
    const char *txt = reinterpret_cast<char *>(scn->lParam);
    int insert_len = scn->wParam;
    pyparm = Py_BuildValue("iisi",scn->nmhdr.code, scn->message, txt, insert_len);
    break;
  }
  case SCI_INSERTTEXT: {
    int insert_pos = scn->wParam;
    const char *txt = reinterpret_cast<char *>(scn->lParam);
    pyparm = Py_BuildValue("iisi", scn->nmhdr.code, scn->message, txt, insert_pos);
    break;
  }
  case SCI_GOTOLINE: {
    int target = scn->wParam;
    pyparm = Py_BuildValue("iii", scn->nmhdr.code, scn->message, target);
    break;
  }
  case SCI_GOTOPOS: {
    int target = scn->wParam;
    pyparm = Py_BuildValue("iii", scn->nmhdr.code, scn->message, target);
    break;
  }
  case SCI_SEARCHNEXT: {
    const char *txt = reinterpret_cast<char *>(scn->lParam);
    int mode = scn->wParam;
    pyparm = Py_BuildValue("iisi", scn->nmhdr.code, scn->message, txt, mode);
    break;
  }
  case SCI_SEARCHPREV: {
    const char *txt = reinterpret_cast<char *>(scn->lParam);
    int mode = scn->wParam;
    pyparm = Py_BuildValue("iisi", scn->nmhdr.code, scn->message, txt, mode);
    break;
  }
		
  // Message with no parameter
  default: {
//    printf("CODE %d MESSAGE %d\n", scn->nmhdr.code, scn->message);
    pyparm = Py_BuildValue("ii", scn->nmhdr.code, scn->message);
    break;
  }
  }

  return pyparm;
}

// Should be symmetrical with _build_macro_parms above
static PyObject *_wrap_scintilla_macro_action(PyObject *self, PyObject *args) {
  PyObject *editor, *tuple;
  int message;
  uptr_t wParam;
  sptr_t lParam;
  int retval;

  // Extract fixed params
  if (!PyArg_ParseTuple(args, "O!O!:scintilla_macro_action", &PyGtk_Type, 
      &editor, &PyTuple_Type, &tuple))
    return NULL;

  // Get fixed parameter (message id)
  PyObject *pymessage = PyTuple_GetItem(tuple, 0);
  message = PyInt_AsLong(pymessage);

  // Unpack varying params
  switch (message) {

  // Package message parameters for those that have them
  case SCI_REPLACESEL: {
    PyObject *text = PyTuple_GetItem(tuple, 1);
    lParam = (sptr_t) PyString_AsString(text);
    wParam = 0;
    break;
  }
  case SCI_ADDTEXT: {
    PyObject *text = PyTuple_GetItem(tuple, 1);
    lParam = (sptr_t) PyString_AsString(text);
    wParam = 0;
    break;
  }
  case SCI_INSERTTEXT: {
    PyObject *text = PyTuple_GetItem(tuple, 1);
    PyObject *pos = PyTuple_GetItem(tuple, 2);
    lParam = (sptr_t) PyString_AsString(text);
    wParam = (uptr_t) PyInt_AsLong(pos);
    break;
  }
  case SCI_GOTOLINE: {
    PyObject *pos = PyTuple_GetItem(tuple, 1);
    lParam = 0;
    wParam = (uptr_t) PyInt_AsLong(pos);
    break;
  }
  case SCI_GOTOPOS: {
    PyObject *pos = PyTuple_GetItem(tuple, 1);
    lParam = 0;
    wParam = (uptr_t) PyInt_AsLong(pos);
    break;
  }
  case SCI_SEARCHNEXT: {
    PyObject *text = PyTuple_GetItem(tuple, 1);
    PyObject *mode = PyTuple_GetItem(tuple, 2);
    lParam = (sptr_t) PyString_AsString(text);
    wParam = (uptr_t) PyInt_AsLong(mode);
    break;
  }
  case SCI_SEARCHPREV: {
    PyObject *text = PyTuple_GetItem(tuple, 1);
    PyObject *mode = PyTuple_GetItem(tuple, 2);
    lParam = (sptr_t) PyString_AsString(text);
    wParam = (uptr_t) PyInt_AsLong(mode);
    break;
  }
  
  // Message with no parameter
  default: {
    lParam = 0;
    wParam = 0;
    break;
  }
  }

  // Determine whether the command will fail
  // XXX Checks could be added here in the future... may not be needed
#ifdef FUTURE
  switch (message) {
  case SCI_GOTOLINE:
  case SCI_GOTOPOS:
  case SCI_LINEDOWN:
  case SCI_LINEDOWNEXTEND:
  case SCI_LINEUP:
  case SCI_LINEUPEXTEND:
  case SCI_CHARLEFT:
  case SCI_CHARLEFTEXTEND:
  case SCI_CHARRIGHT:
  case SCI_CHARRIGHTEXTEND:
  case SCI_WORDLEFT:
  case SCI_WORDLEFTEXTEND:
  case SCI_WORDRIGHT:
  case SCI_WORDRIGHTEXTEND:
  case SCI_PAGEUP:
  case SCI_PAGEUPEXTEND:
  case SCI_PAGEDOWN:
  case SCI_PAGEDOWNEXTEND:
  case SCI_DELETEBACK:
  case SCI_BACKTAB:
  case SCI_DELWORDLEFT:
  case SCI_DELWORDRIGHT:
  }
#endif

  // Run the command
  retval = scintilla_send_message(GTK_SCINTILLA(scint->obj), message, wParam, lParam);

  // Determine whether the command failed
  switch (message) {
  case SCI_SEARCHNEXT:
  case SCI_SEARCHPREV:
    if (retval != -1)
      retval = 0;
    break;
  default:
    retval = 0;
    break;
  }
  
  // Return 0 to indicate success, non-0 failure (macro should be aborted)
  return PyInt_FromLong(retval);
}
#endif // !DISABLE_MACROS


