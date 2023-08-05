from pyscintilla import *
import unittest

class SciCase(unittest.TestCase):
    def setUp(self):
        self.s = Scintilla()
    
    def lineEquals(self, text, num):
        self.assertEquals(text, self.s.get_line(num))
    
    def textEquals(self, text):
        self.assertEquals(text, self.s.get_text())
    
    def charEquals(self, text, index):
        self.assertEquals(text, self.s.get_char_at(index))

    def rangeEquals(self, text, start, finish):
        self.assertEquals(text, self.s.get_text_range(start, finish))

    def lineCountEquals(self, count):
        self.assertEquals(count, self.s.get_line_count())

class TestRetreivalAndModification(SciCase):

    def test_get_set(self):
        s = self.s
        self.textEquals("")
        
        s.set_text("foo")
        self.textEquals("foo")
    
    def test_get_line(self):
        s = self.s
        self.assertRaises(IndexError, self.lineEquals, "", -1)
        self.lineEquals("", 0)
        self.assertRaises(IndexError, self.lineEquals, "", 1)
        
        s.set_text("foo")

        self.lineEquals("foo", 0)
        self.assertRaises(IndexError, self.lineEquals, "", 1)
        
        s.set_text("foo\n")

        self.lineEquals("foo\n", 0)
        self.lineEquals("", 1)
        self.assertRaises(IndexError, self.lineEquals, "", 2)

        s.set_text("foo\nbar")

        self.lineEquals("foo\n", 0)
        self.lineEquals("bar", 1)
        self.assertRaises(IndexError, self.lineEquals, "", 2)

    def test_clear_all(self):
        s = self.s
        
        self.textEquals("")
        
        s.set_text("foo")
        
        self.textEquals("foo")
        
        s.clear_all()
        
        self.textEquals("")
    
    def test_read_only(self):
        s = self.s
        
        assert s.get_read_only() is False
        
        self.textEquals("")
        s.set_read_only(True)
        assert s.get_read_only() is True

        s.set_text("foo")
        self.textEquals("")

        s.set_read_only(False)
        assert s.get_read_only() is False

        s.set_text("foo")
        self.textEquals("foo")
        
        s.set_read_only(True)
        assert s.get_read_only() is True

        self.textEquals("foo")
        s.clear_all()
        self.textEquals("foo")
        
    def test_get_char_at(self):
        s = self.s
        self.assertRaises(IndexError, self.charEquals, "", 0)
        self.assertRaises(IndexError, self.charEquals, "", -1)
        self.assertRaises(IndexError, self.charEquals, "", 1)
        
        s.set_text("foo")
        self.charEquals("f", 0)
        self.charEquals("o", 1)
        self.charEquals("o", 2)
        self.assertRaises(IndexError, self.charEquals, "", 3)
        
        txt = s.get_text()
        
        for x in range(len(s)):
            self.assertEquals(txt[x], s[x])
        

    def test_modify(self):
        s = self.s
        
        assert s.get_modify() is False, s.get_modify()
        
        s.set_text("foo")
        
        assert s.get_modify() is True, s.get_modify()
        
        s.set_save_point()
        assert s.get_modify() is False, s.get_modify()
        
    def test_get_text_range(self):
        s = self.s
        self.rangeEquals("", 0, 0)
        
        s.set_text("foo")
        self.rangeEquals("", 0, 0)
        self.rangeEquals("f", 0, 1)
        self.rangeEquals("o", 1, 2)
        self.rangeEquals("o", 2, 3)
        self.rangeEquals("foo", 0, 3)
        
        self.assertRaises(ValueError, self.rangeEquals, "foo", -1, 0)
        self.assertRaises(ValueError, self.rangeEquals, "foo", 0, -1)

        import random
        s.set_text("oh so much text it's not even funny")
        txt = s.get_text()
        max_len = len(txt)
        assert len(txt) == len(s)
        
        # Test all combinations of slices possible
        
        for start in range(-max_len, max_len):
            for end in range(-max_len, max_len):
                self.assertEquals(txt[start:end], s[start:end])

        for end in range(-max_len, max_len):
            for start in range(-max_len, max_len):
                self.assertEquals(txt[start:end], s[start:end])

    
    def _test_get_styled_text(self):
        pass
    
    def _test_allocate(self):
        pass
    
    def _test_add_text(self):
        pass
    
    def _test_insert_text(self):
        pass
    
    def _test_clear_document_style(self):
        pass
    
    def _test_get_style_at(self):
        pass
    
    def _test_get_set_style_bits(self):
        pass
    
    def _test_target_as_utf8(self):
        pass
    
    def _test_encoded_from_utf8(self):
        pass
    
    def _test_set_length_for_encode(self):
        pass
    
class TestSearchAndReplace(SciCase):
    def _test_find_next(self):
        pass
    
    def _test_search_anchor(self):
        pass
    
    def _test_search_next(self):
        pass
    
    def _test_search_prev(self):
        pass
    
    def _test_get_set_target_start(self):
        pass
    
    def _test_get_set_target_end(self):
        pass
    
    def _test_target_from_selection(self):
        pass
    
    def _test_get_set_search_flags(self):
        pass
    
    def _test_search_in_target(self):
        pass
    
    def _test_replace_target(self):
        pass
    
    def _test_replace_target_re(self):
        pass
    
class TestOvertypeCutPasteErrorUndoRedo(SciCase):
    def _test_get_set_overtype(self):
        pass
    
    def _test_cut_copy_paste(self):
        pass
    
    def _test_clear(self):
        pass
    
    def _test_can_paste(self):
        pass
    
    def _test_copy_range(self):
        pass
    
    def _test_copy_text(self):
        pass
    
    def _test_get_set_paste_convert_endings(self):
        pass
    
    def _test_get_set_status(self):
        pass

    def _test_undo_can_undo(self):
        pass
        
    def _test_empty_undo_buffer(self):
        pass
    
    def _test_redo_can_redo(self):
        pass
    
    def _test_get_set_undo_collection(self):
        pass
    
    def _test_begin_end_undo_action(self):
        pass

class TestSelection(SciCase):

    def test_get_text_length(self):
        s = self.s
        
        assert len(s.get_text()) == 0
        assert len(s) == 0, len(s)
        assert s.get_length() == 0
        assert s.get_text_length() == 0
        
        s.set_text("foo")

        assert len(s.get_text()) == 3
        assert len(s) == 3, len(s)

    
    def test_get_line_count(self):
        s = self.s
        
        self.lineCountEquals(1)
        
        s.set_text("foo")

        self.lineCountEquals(1)
        
        s.set_text("foo\n")

        self.lineCountEquals(2)

        s.set_text("foo\nbar")
        
        self.lineCountEquals(2)
        
        s.set_text("foo\nbar\n")
        self.lineCountEquals(3)


        s.set_text("foo\nbar\nfoo")
        self.lineCountEquals(3)

    
    def _test_get_first_visible_line(self):
        pass
    
    def _test_lines_on_screen(self):
        pass
    
    def _test_set_sel(self):
        pass
    
    def _test_goto_pos(self):
        pass
    
    def _test_goto_line(self):
        pass
    
    def _test_replace_sel(self):
        pass
    
        

if __name__ == '__main__':
    unittest.main()
