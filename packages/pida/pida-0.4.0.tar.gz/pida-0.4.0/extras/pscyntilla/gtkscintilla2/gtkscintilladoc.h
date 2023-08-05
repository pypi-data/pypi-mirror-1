/* GtkScintilladoc2: Wrapper widget for the Scintilla editing component.
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

#ifndef __GTK_SCINTILLA_DOC_H__
#define __GTK_SCINTILLA_DOC_H__

#include <glib-object.h>

#ifdef __cplusplus
extern "C" {
#endif

#define GTK_TYPE_SCINTILLA_DOC            (gtk_scintilla_doc_get_type ())
#define GTK_SCINTILLA_DOC(obj)            (GTK_CHECK_CAST ((obj), GTK_TYPE_SCINTILLA_DOC, GtkScintillaDoc))
#define GTK_SCINTILLA_DOC_CLASS(klass)    (GTK_CHECK_CLASS_CAST ((klass), GTK_TYPE_SCINTILLA_DOC, GtkScintillaDocClass))
#define GTK_IS_SCINTILLA_DOC(obj)         (GTK_CHECK_TYPE ((obj), GTK_TYPE_SCINTILLA_DOC))
#define GTK_IS_SCINTILLA_DOC_CLASS(klass) (GTK_CHECK_CLASS_TYPE ((klass), GTK_TYPE_SCINTILLA_DOC))

typedef struct _GtkScintillaDoc      GtkScintillaDoc;
typedef struct _GtkScintillaDocClass GtkScintillaDocClass;

struct _GtkScintillaDoc {
    GObject parent;

    /* Pointer to C++ Document object; declare as void* for C compiling */
    void *sci_doc;
};

struct _GtkScintillaDocClass {
    GObjectClass parent_class;

};

GType      gtk_scintilla_doc_get_type       (void) G_GNUC_CONST;
GtkScintillaDoc *gtk_scintilla_doc_new      (void* sci_doc);

  /* Following functions wrap methods of the C++ Document object from
     scintilla, almost one-for-one.  Commented out C++ decls are
     methods on the C++ object which are not implemented yet */

int gtk_scintilla_doc_line_from_position (GtkScintillaDoc *doc,
					  int pos);
  /*	int ClampPositionIntoDocument(int pos); */
gboolean gtk_scintilla_doc_is_cr_lf (GtkScintillaDoc *doc,
				     gint pos);
  /*	int LenChar(int pos); */
  /*	int MovePositionOutsideChar(int pos, int moveDir, gboolean checkLineEnd=true); */

gboolean gtk_scintilla_doc_delete_chars (GtkScintillaDoc *doc,
					 int pos,
					 int len);
gboolean gtk_scintilla_doc_insert_styled_string (GtkScintillaDoc *doc,
						 int position,
						 char *s,
						 int insert_length);
int gtk_scintilla_doc_undo (GtkScintillaDoc *doc);
int gtk_scintilla_doc_redo (GtkScintillaDoc *doc);
gboolean gtk_scintilla_doc_can_undo (GtkScintillaDoc *doc);
gboolean gtk_scintilla_doc_can_redo (GtkScintillaDoc *doc);
void gtk_scintilla_doc_delete_undo_history (GtkScintillaDoc *doc);
gboolean gtk_scintilla_doc_set_undo_collection (GtkScintillaDoc *doc,
						gboolean collect_undo);
gboolean gtk_scintilla_doc_is_collecting_undo (GtkScintillaDoc *doc);
void gtk_scintilla_doc_begin_undo_action (GtkScintillaDoc *doc);
void gtk_scintilla_doc_end_undo_action (GtkScintillaDoc *doc);

void gtk_scintilla_doc_set_save_point (GtkScintillaDoc *doc);
gboolean gtk_scintilla_doc_is_save_point (GtkScintillaDoc *doc);

  /*	int GetLineIndentation(int line); */
  /*	void SetLineIndentation(int line, int indent); */
  /*	int GetLineIndentPosition(int line); */
  /*	int GetColumn(int position); */
  /*	int FindColumn(int line, int column); */
  /*	void Indent(gboolean forwards, int lineBottom, int lineTop); */
  /*	void ConvertLineEnds(int eolModeSet); */
void gtk_scintilla_doc_set_read_only (GtkScintillaDoc *doc,
				      gboolean read_only);
gboolean gtk_scintilla_doc_is_read_only (GtkScintillaDoc *doc);


  /*	gboolean InsertChar(int pos, char ch); */
void gtk_scintilla_doc_insert_string (GtkScintillaDoc *doc, 
				      int position,
				      const char* str,
				      int length);
  /*	void ChangeChar(int pos, char ch); */
  /*	void DelChar(int pos); */
  /*	void DelCharBack(int pos); */

  /*	char CharAt(int position) { return cb.CharAt(position); } */
void gtk_scintilla_doc_get_char_range (GtkScintillaDoc *doc,
				       char* buffer,
				       int position,
				       int length);
char gtk_scintilla_doc_style_at (GtkScintillaDoc *doc, 
				 int position);
  /*	int GetMark(int line) { return cb.GetMark(line); } */
  /*	int AddMark(int line, int markerNum); */
  /*	void DeleteMark(int line, int markerNum); */
  /*	void DeleteMarkFromHandle(int markerHandle); */
  /*	void DeleteAllMarks(int markerNum); */
  /*	int LineFromHandle(int markerHandle); */
int gtk_scintilla_doc_line_start (GtkScintillaDoc *doc,
				  int lineno);
int gtk_scintilla_doc_line_end (GtkScintillaDoc *doc,
				int lineno);
int gtk_scintilla_doc_line_end_position (GtkScintillaDoc *doc,
					 int pos);
  /*	int VCHomePosition(int position); */

  /*	int SetLevel(int line, int level); */
  /*	int GetLevel(int line) { return cb.GetLevel(line); } */
  /*	void ClearLevels() { cb.ClearLevels(); } */
  /*	int GetLastChild(int lineParent, int level=-1); */
  /*	int GetFoldParent(int line); */

  /*	void Indent(gboolean forwards); */
  /*	int ExtendWordSelect(int pos, int delta, gboolean onlyWordCharacters=false); */
  /*	int NextWordStart(int pos, int delta); */
int gtk_scintilla_doc_length (GtkScintillaDoc *doc);
  /*	long FindText(int minPos, int maxPos, const char *s, */
  /*		gboolean caseSensitive, gboolean word, gboolean wordStart, gboolean regExp, gboolean posix, int *length); */
  /*	long FindText(int iMessage, unsigned long wParam, long lParam); */
  /*	const char *SubstituteByPosition(const char *text, int *length); */
int gtk_scintilla_doc_lines_total (GtkScintillaDoc *doc);

  /*	void ChangeCase(Range r, gboolean makeUpperCase); */

  /*	void SetWordChars(unsigned char *chars); */
  /*	void SetStylingBits(int bits); */
void gtk_scintilla_doc_start_styling (GtkScintillaDoc *doc, 
				      gint position,
				      gchar flags);
gboolean gtk_scintilla_doc_set_style_for (GtkScintillaDoc *doc, 
					  gint length,
					  gchar style);
  /*	gboolean SetStyles(int length, char *styles); */
gint gtk_scintilla_doc_get_end_styled (GtkScintillaDoc *doc);
  /*	gboolean EnsureStyledTo(int pos); */
void gtk_scintilla_doc_ensure_styled_to (GtkScintillaDoc *doc, 
					 int position);
  /*	int GetStyleClock() { return styleClock; } */


  /*	int SetLineState(int line, int state) { return cb.SetLineState(line, state); } */
  /*	int GetLineState(int line) { return cb.GetLineState(line); } */
  /*	int GetMaxLineState() { return cb.GetMaxLineState(); } */

  /*	gboolean IsWordPartSeparator(char ch); */
  /*	int WordPartLeft(int pos); */
  /*	int WordPartRight(int pos); */
  /*	int ExtendStyleRange(int pos,  int delta); */ 
  /*	int ParaUp(int pos); */
  /*	int ParaDown(int pos); */
int gtk_scintilla_doc_get_code_page (GtkScintillaDoc *doc);
void gtk_scintilla_doc_set_code_page (GtkScintillaDoc *doc, int code_page);

int gtk_scintilla_doc_move_position_outside_char (GtkScintillaDoc *doc, int pos, 
            int move_dir, gboolean check_line_end);
    

#ifdef __cplusplus
}
#endif

#endif /* __GTK_SCINTILLA_DOC_H__ */
