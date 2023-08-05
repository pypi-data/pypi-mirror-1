# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005-2006 The PIDA Project

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

# system import(s)
import threading
import gobject
import gtk

# pida core import(s)
import pida.core.service as service
from pida.core import actions

# pidagtk import(s)
import pida.pidagtk.tree as tree
import pida.pidagtk.contentview as contentview

import re
import commands
import os

defs = service.definitions

from pida.model import attrtypes as types

class manpage_hint(object):

    def __init__(self, pattern, number, manpage):
        self.number = number
        self.manpage = manpage
        self.pattern = pattern
        self.key = '%s(%d)' % (manpage, int(number))

class man_view(contentview.content_view):

    LONG_TITLE = 'Man Viewer'
    SHORT_TITLE = 'MAN'
    ICON_NAME = 'gtk-library'

    HAS_CONTROL_BOX = True

    def init(self):
        self.__vbox = gtk.VBox()
        self.__entry = gtk.Entry()
        self.__entry.connect('changed', self.cb_entry_changed)

        self.__list = tree.Tree()
        self.__list.set_property('markup-format-string',
                                 '%(pattern)s'
                                 '(<span color="#0000c0">%(number)s</span>) '
                                 '%(manpage)s')
        self.__list.connect('double-clicked', self.cb_list_d_clicked)


        self.__vbox.pack_start(self.__entry, expand=False)
        self.__vbox.pack_start(self.__list)
        self.widget.pack_start(self.__vbox)

    def set_manpages(self, manpages):
        self.__list.clear()
        for manpage in manpages:
            self.__list.add_item(manpage)

    def cb_list_d_clicked(self, tree, item):
        commandargs = ['/usr/bin/man', item.value.number, item.value.pattern]
        directory = os.path.dirname(commandargs[0])
        self.service.boss.call_command('terminal', 'execute',
                command_args=commandargs,
                icon_name='gtk-library',
                term_type='dumb',
                kwdict={'directory': directory},
                short_title='Man %s(%d)' %
                (item.value.pattern, int(item.value.number)))

    def cb_entry_changed(self, w):
        self.service.boss.call_command('man', 'find', pattern=w.get_text())


class man(service.service):

    class MAN(defs.View):
        view_type = man_view
        book_name = 'plugin'

    def init(self):
        self._view = None
        self.counter = 0
        self._currentdocument = None

    display_name = 'Man Viewer'

    def reset(self):
        self._visact = self.action_group.get_action('man+man_viewer')
        self._visact.set_active(True)

    def set_manpages(self, args):
        counter, manpages = args
        if self.counter != counter:
            return
        self._view.set_manpages(manpages)

    def cmd_find(self, pattern):
        def new_thread(counter):
            manpages = []
            if len(pattern) > 1:
                manpages = self._cmd_find(pattern)
            gobject.idle_add(self.set_manpages, (counter, manpages))

        threading.Thread(target=new_thread, args=(self.counter,)).start()

    def _cmd_find(self, pattern):
        cmd = 'man -k "%s"' % pattern
        ret = commands.getoutput(cmd)
        results = ret.split('\n')
        manpages = []
        for result in results:
            reman = re.compile('[(]([\d]+)[)]')
            list = reman.findall(result)
            if not len(list):
                continue
            name = result.split('(')[0].strip()
            res = result.split('- ',1)
            manpages.append(manpage_hint(name, list[0], res[1]))
        return manpages

    @actions.action(type=actions.TYPE_TOGGLE,
                    stock_id='gtk-library',
                    label='Man Viewer')
    def act_man_viewer(self, action):
        """View a man page."""
        self.set_view_visible(action.get_active())

    def set_view_visible(self, visibility):
        if visibility:
            if self._view is None:
                self._view = self.create_view('MAN')
                self.show_view(view=self._view)
            self._view.raise_page()
        else:
            if self._view is not None:
                self.close_view(self._view)
            self._view = None

    def view_closed(self, view):
        self._view = None
        self._visact.set_active(False)

    def get_menu_definition(self):
        return """
                <menubar>
                <menu name="base_view" action="base_view_menu" >
                    <placeholder name="TopViewMenu">
                        <menuitem action="man+man_viewer" />
                    </placeholder>
                </menu>

                </menubar>
               """

Service = man

