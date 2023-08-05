/* GtkScintilla2: Wrapper widget for the Scintilla editing component.
 *
 * Copyright (c) 2003  Archaeopteryx Software, Inc. <info@wingide.com>
 * Copyright (c) 2002  Dennis J Houy <djhouy@paw.co.za>
 * Copyright (c) 2001  Michele Campeotto <micampe@micampe.it>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the 
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330, 
 * Boston, MA  02111-1307  USA.
 */

#include "gtkscintilladoc.h"

#define PLAT_GTK 2
#include <gtk/gtk.h>
#include "Scintilla.h"
//#include "scintilla/include/ScintillaWidget.h"
#include "ContractionState.h"
#include "SVector.h"
#include "CellBuffer.h"
#include "Document.h"

#include <string.h>

enum {
    MODIFY_ATTEMPT,
    SAVE_POINT,
    MODIFIED,
    STYLE_NEEDED,
    LAST_SIGNAL
};

/* Class to watch scintilla documents and convert scintillla events into
   signal emissions.  Only 1 global instance is used, the GtkScintillaDoc
   pointer is stored in the userData that's set when the watcher instance
   is added to a particular Document. */
class DocWatcherBridge: public DocWatcher {
public:
    DocWatcherBridge();
    void NotifyModifyAttempt(Document *doc, void *userData);
    void NotifySavePoint(Document *doc, void *userData, bool atSavePoint);
    void NotifyModified(Document *doc, DocModification mh, void *userData);
    void NotifyDeleted(Document *doc, void *userData);
    void NotifyStyleNeeded(Document *doc, void *userData, int pos);

private:
    /* Disable copying and copy construction */
    DocWatcherBridge(const DocWatcherBridge&);
    DocWatcherBridge& operator= (const DocWatcherBridge&);
};

static void gtk_scintilla_doc_class_init (GtkScintillaDocClass *klass);
static void gtk_scintilla_doc_init       (GtkScintillaDoc      *sci);
static void gtk_scintilla_doc_finalize   (GObject              *object);

static gpointer parent_class;
static guint signals[LAST_SIGNAL] = { 0 };
static DocWatcherBridge doc_watcher;

static inline Document* sdoc(GtkScintillaDoc* g_doc)
{
    return static_cast<Document*>(g_doc->sci_doc);
}

DocWatcherBridge::DocWatcherBridge()
{
}

void 
DocWatcherBridge::NotifyModifyAttempt(Document *doc,
				      void *userData)
{
    g_signal_emit (G_OBJECT(userData), signals[MODIFY_ATTEMPT], 0);
}

void 
DocWatcherBridge::NotifySavePoint(Document *doc,
				  void *userData,
				  bool atSavePoint)
{
    gboolean val = atSavePoint ? TRUE : FALSE;
    g_signal_emit (G_OBJECT(userData), signals[SAVE_POINT], 0, val);
}

void 
DocWatcherBridge::NotifyModified(Document *doc,
				 DocModification mh,
				 void *userData)
{
    gchar* text;

    if (mh.text == NULL || mh.length == 0) {
	g_signal_emit (G_OBJECT (userData),
		       signals[MODIFIED], 0,
		       (gint) mh.position,
		       (gint) mh.modificationType,
		       "",
		       0,
		       (gint) mh.linesAdded,
		       (gint) mh.line,
		       (gint) mh.foldLevelNow,
		       (gint) mh.foldLevelPrev);
    }
    else {
	// Copy text to a NULL terminated buffer
	text = (gchar*) g_malloc (mh.length + 1);
	strncpy (text, mh.text, mh.length);
	text[mh.length] = '\0';

	g_signal_emit (G_OBJECT (userData),
		       signals[MODIFIED], 0,
		       (gint) mh.position,
		       (gint) mh.modificationType,
		       text,
		       mh.length,
		       (gint) mh.linesAdded,
		       (gint) mh.line,
		       (gint) mh.foldLevelNow,
		       (gint) mh.foldLevelPrev);

	g_free (text);
    }
}

void
DocWatcherBridge::NotifyDeleted(Document *doc, 
				void *userData)
{
}

void
DocWatcherBridge::NotifyStyleNeeded(Document *doc,
				    void *userData,
				    int pos)
{
    g_signal_emit (G_OBJECT(userData), signals[STYLE_NEEDED], 0, pos);
}

GType
gtk_scintilla_doc_get_type (void)
{
    static GType our_type = 0;

    if (!our_type) {
        static const GTypeInfo our_info =
        {
            sizeof (GtkScintillaDocClass),
            NULL,               /* base_init */
            NULL,               /* base_finalize */
            (GClassInitFunc) gtk_scintilla_doc_class_init,
            NULL,               /* class_finalize */
            NULL,               /* class_data */
            sizeof (GtkScintillaDocClass),
            0,                  /* n_preallocs */
            (GInstanceInitFunc) gtk_scintilla_doc_init,
        };

        our_type = g_type_register_static (G_TYPE_OBJECT, "GtkScintillaDoc",
                                           &our_info, (GTypeFlags) 0);
    }
    
    return our_type;
}

static void
gtk_scintilla_doc_class_init (GtkScintillaDocClass *klass)
{
    GObjectClass *object_class;
    
    object_class = (GObjectClass *) klass;
    parent_class = g_type_class_peek_parent (klass);

    object_class->finalize = gtk_scintilla_doc_finalize;

    signals[MODIFY_ATTEMPT] =
	g_signal_new ("modify_attempt",
		      G_OBJECT_CLASS_TYPE (object_class),
		      (GSignalFlags) 0,
		      0,
		      NULL, NULL,
                      g_cclosure_marshal_VOID__VOID,
		      G_TYPE_NONE, 0);
    signals[SAVE_POINT] =
	g_signal_new ("save_point",
		      G_OBJECT_CLASS_TYPE (object_class),
		      (GSignalFlags) 0,
		      0,
		      NULL, NULL,
                      g_cclosure_marshal_VOID__VOID,
		      G_TYPE_NONE, 1,
		      G_TYPE_BOOLEAN);
    signals[MODIFIED] =
        g_signal_new ("modified",
                      G_OBJECT_CLASS_TYPE (object_class),
		      (GSignalFlags) 0,
		      0,
                      NULL, NULL,
                      g_cclosure_marshal_VOID__VOID,
                      G_TYPE_NONE, 8,
                      G_TYPE_INT, G_TYPE_INT, G_TYPE_STRING,
                      G_TYPE_INT, G_TYPE_INT, G_TYPE_INT,
                      G_TYPE_INT, G_TYPE_INT);
    signals[STYLE_NEEDED] =
        g_signal_new ("style_needed",
                      G_OBJECT_CLASS_TYPE (object_class),
		      (GSignalFlags) 0,
		      0,
                      NULL, NULL,
                      g_cclosure_marshal_VOID__VOID,
                      G_TYPE_NONE, 1,
                      G_TYPE_INT);
}

static void
gtk_scintilla_doc_init (GtkScintillaDoc *doc)
{
    doc->sci_doc = NULL;
}

static void
gtk_scintilla_doc_finalize (GObject *object)
{
    GtkScintillaDoc *doc;

    g_return_if_fail (object != NULL);

    doc = GTK_SCINTILLA_DOC(object);
    sdoc(doc)->RemoveWatcher(&doc_watcher, doc);
    sdoc(doc)->Release();
    doc->sci_doc = NULL;

    G_OBJECT_CLASS (parent_class)->finalize (object);
}

GtkScintillaDoc *gtk_scintilla_doc_new (void* sci_doc)
{
    GtkScintillaDoc *doc;

    if (sci_doc == NULL) {
	// Scintilla documents are initialized with a ref count of 0,
	// but we'll be adding a ref to it almost immediately
	sci_doc = new Document ();
    }

    doc = (GtkScintillaDoc *) g_object_new (gtk_scintilla_doc_get_type (),
					    NULL);
    doc->sci_doc = sci_doc;
    sdoc(doc)->AddRef();
    sdoc(doc)->AddWatcher(&doc_watcher, doc);

    return doc;
}

int gtk_scintilla_doc_line_from_position(GtkScintillaDoc *doc,
					 int pos)
{
    return sdoc(doc)->LineFromPosition (pos);
}

gboolean gtk_scintilla_doc_is_cr_lf (GtkScintillaDoc *doc,
				     gint pos)
{
    return sdoc(doc)->IsCrLf (pos);
}

gboolean gtk_scintilla_doc_delete_chars (GtkScintillaDoc *doc,
					 int pos,
					 int len)
{
    return sdoc(doc)->DeleteChars (pos, len);
}

gboolean gtk_scintilla_doc_insert_styled_string (GtkScintillaDoc *doc,
						 int position,
						 char *s,
						 int insert_length)
{
    return sdoc(doc)->InsertStyledString (position, s, insert_length);
}


int gtk_scintilla_doc_undo (GtkScintillaDoc *doc)
{
    return sdoc(doc)->Undo ();
}


int gtk_scintilla_doc_redo (GtkScintillaDoc *doc)
{
    return sdoc(doc)->Redo ();
}


gboolean gtk_scintilla_doc_can_undo (GtkScintillaDoc *doc)
{
    return sdoc(doc)->CanUndo ();
}


gboolean gtk_scintilla_doc_can_redo (GtkScintillaDoc *doc)
{
    return sdoc(doc)->CanRedo ();
}


void gtk_scintilla_doc_delete_undo_history (GtkScintillaDoc *doc)
{
    sdoc(doc)->DeleteUndoHistory ();
}


gboolean gtk_scintilla_doc_set_undo_collection (GtkScintillaDoc *doc,
						gboolean collect_undo)
{
    return sdoc(doc)->SetUndoCollection (collect_undo);
}


gboolean gtk_scintilla_doc_is_collecting_undo (GtkScintillaDoc *doc)
{
    return sdoc(doc)->IsCollectingUndo ();
}


void gtk_scintilla_doc_begin_undo_action (GtkScintillaDoc *doc)
{
    sdoc(doc)->BeginUndoAction ();
}


void gtk_scintilla_doc_end_undo_action (GtkScintillaDoc *doc)
{
    sdoc(doc)->EndUndoAction ();
}

void gtk_scintilla_doc_set_save_point (GtkScintillaDoc *doc)
{
    sdoc(doc)->SetSavePoint ();
}

gboolean gtk_scintilla_doc_is_save_point (GtkScintillaDoc *doc)
{
    return sdoc(doc)->IsSavePoint();
}

void gtk_scintilla_doc_set_read_only (GtkScintillaDoc *doc,
				      gboolean read_only)
{
    sdoc(doc)->SetReadOnly(read_only);
}

gboolean gtk_scintilla_doc_is_read_only (GtkScintillaDoc *doc)
{
    return sdoc(doc)->IsReadOnly();
}

void gtk_scintilla_doc_get_char_range (GtkScintillaDoc *doc,
				       char* buffer,
				       int position,
				       int length)
{
    if (doc->sci_doc == NULL || position < 0
	|| position + length > sdoc(doc)->Length()) {
	strcpy (buffer, "");
	return;
    }

    sdoc(doc)->GetCharRange(buffer, position, length);
}

void gtk_scintilla_doc_insert_string (GtkScintillaDoc *doc, 
				      int position,
				      const char* str,
				      int length)

{
    g_return_if_fail (position >= 0);

    sdoc(doc)->InsertString(position, str, length);
}

int gtk_scintilla_doc_line_start (GtkScintillaDoc *doc,
				  int lineno)
{
    return sdoc(doc)->LineStart (lineno);
}

int gtk_scintilla_doc_line_end (GtkScintillaDoc *doc,
				int lineno)
{
    return sdoc(doc)->LineEnd (lineno);
}

int gtk_scintilla_doc_line_end_position (GtkScintillaDoc *doc,
					 int pos)
{
    return sdoc(doc)->LineEndPosition (pos);
}

int gtk_scintilla_doc_length (GtkScintillaDoc *doc)
{
    return sdoc(doc)->Length ();
}

int gtk_scintilla_doc_lines_total (GtkScintillaDoc *doc)
{
    return sdoc(doc)->LinesTotal ();
}

gint gtk_scintilla_doc_get_end_styled (GtkScintillaDoc *doc)
{
    return sdoc(doc)->GetEndStyled();
}

void gtk_scintilla_doc_ensure_styled_to (GtkScintillaDoc *doc, 
					 int position)
{
    if (doc->sci_doc == NULL)
	return;

    if (position > sdoc(doc)->Length())
	position = sdoc(doc)->Length();

    sdoc(doc)->EnsureStyledTo (position);
}

char gtk_scintilla_doc_style_at (GtkScintillaDoc *doc, 
				 int position)
{
    if (doc->sci_doc == NULL)
	return 0;

    if (position > sdoc(doc)->Length())
	position = sdoc(doc)->Length();

    return sdoc(doc)->StyleAt (position);
}

void gtk_scintilla_doc_start_styling (GtkScintillaDoc *doc, 
				      gint position,
				      gchar flags)
{
    if (doc->sci_doc == NULL)
	return;

    if (position > sdoc(doc)->Length())
	position = sdoc(doc)->Length();

    sdoc(doc)->StartStyling (position, flags);
}

gboolean gtk_scintilla_doc_set_style_for (GtkScintillaDoc *doc, 
					  gint length,
					  gchar style)
{
    if (doc->sci_doc == NULL)
	return FALSE;

    return sdoc(doc)->SetStyleFor (length, style);
}

int gtk_scintilla_doc_get_code_page (GtkScintillaDoc *doc)
{
    if (doc->sci_doc == NULL)
	return 0;

    return sdoc(doc)->dbcsCodePage;
}

void gtk_scintilla_doc_set_code_page (GtkScintillaDoc *doc, int code_page)
{
    if (doc->sci_doc == NULL)
	return;

    sdoc(doc)->dbcsCodePage = code_page;
}

int gtk_scintilla_doc_move_position_outside_char (GtkScintillaDoc *doc, int pos, int move_dir, gboolean check_line_end)
{
    if (doc->sci_doc == NULL)
	return -1;

    return sdoc(doc)->MovePositionOutsideChar(pos, move_dir, check_line_end);
}
    
