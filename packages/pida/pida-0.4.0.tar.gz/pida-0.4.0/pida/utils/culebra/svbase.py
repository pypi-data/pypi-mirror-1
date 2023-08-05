
import mimetypes
import gtksourceview
from rat import text

LANG_MANAGER = gtksourceview.SourceLanguagesManager()

class BaseView(gtksourceview.SourceView):
    def __init__(self):
        super(BaseView, self).__init__()
        self.set_auto_indent(True)
        self.set_show_line_numbers(True)
        self.set_show_line_markers(True)
        self.set_tabs_width(4)
        self.set_margin(80)
        self.set_show_margin(True)
        self.set_smart_home_end(True)
        self.set_highlight_current_line(True)
        self.set_insert_spaces_instead_of_tabs(True)
        text.make_source_view_indentable(self)


class BaseBuffer(gtksourceview.SourceBuffer):

    def __init__(self):
        super(BaseBuffer, self).__init__()
        self.languages_manager = LANG_MANAGER
        self.set_highlight(True)

    def set_mime_type(self, mtype):
        mts = '/'.join(mtype)
        lang = self.languages_manager.get_language_from_mime_type(mts)
        if lang is not None:
            self.set_language(lang)
            