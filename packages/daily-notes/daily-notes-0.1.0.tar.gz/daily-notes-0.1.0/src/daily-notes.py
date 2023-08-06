#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# example daily-nots.py
# This program is targeted to who will make some notes everyday. 
#
# Copyright (C) 2008 Ray Wang <wanglei1123@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

# imports
import pdb
import os, sys, time
import gtk, pygtk
import gettext
pygtk.require('2.0')

class Daily_notes:
    """Daily_notes class"""


    def __init__(self):
        """Daily_notes init function"""

        # the file which log the daily notes
        self.note_file = os.getenv('HOME') + "/.daily_notes"

        # for i18n support
        app_name = "daily-notes"
        gettext.bindtextdomain(app_name)
        gettext.textdomain(app_name)
        _ = gettext.gettext

        # create "Window" widget
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(_("Daily Notes"))
        self.window.set_border_width(5)
        self.window.set_resizable(False)
        self.window.connect("delete_event", self.delete_event)

        # create "VBox" widget
        self.vbox = gtk.VBox(False, 0)
        self.hbox = gtk.HBox()

        # The top part of the window, Calendar, Note_TextBox and Save_Button.
        self.hbutton_box = gtk.HButtonBox()
        self.hbutton_box.set_layout(gtk.BUTTONBOX_SPREAD)
        self.hbutton_box.set_spacing(5)

        # create "Calendar" widget
        self.frame = gtk.Frame(_("Calendar"))
        self.calendar = gtk.Calendar()
        self.frame.add(self.calendar)
        self.calendar.connect("day-selected", self.day_selected)

        # create "VBox" again on the top right
        self.vbox2 = gtk.VBox()
        self.frame2 = gtk.Frame(_("Notes"))
        self.text_entry = gtk.Entry()
        self.frame2.add(self.text_entry)

        # create Save Button
        self.button = gtk.Button(_("Save"))
        self.button.connect("clicked", self.save_to_file, self.text_entry)

        # create the bottom part of window
        self.copyright_label = gtk.Label()
        self.copyright_label.set_text(_("\nDaily Notes 0.1.0\n - make your notes of everyday\n\nCopyright (C) 2008 Ray Wang\n<wanglei1123@gmail.com>\n"))
        self.frame3 = gtk.Frame(_("Copyright"))
        self.frame3.add(self.copyright_label)

        self.button2 = gtk.Button(_("Quit"))
        self.button2.connect("clicked", lambda x: gtk.main_quit())
        
        self.hbutton_box2 = gtk.HButtonBox()
        self.hbutton_box2.set_layout(gtk.BUTTONBOX_END)
        self.hbutton_box2.add(self.button2)

        # pack widgets
        # def pack_start(child, expand=True, fill=True, padding=0)
        self.vbox.pack_start(self.hbox, True, True, 0)
        self.vbox.pack_start(self.frame3, True, True, 0)
        self.vbox.pack_start(self.hbutton_box2, False, False, 0)
        self.hbox.pack_start(self.hbutton_box, False, False, 0)
        self.hbutton_box.pack_start(self.frame, False, True, 0)
        self.hbox.pack_start(self.vbox2, False, False, 0)
        self.vbox2.pack_start(self.frame2, True, True, 0)
        self.vbox2.pack_start(self.button, False, False, 0)

        # load the content of that day
        self.day_selected(self.calendar)

        # add widgets to window
        self.window.add(self.vbox)

        # show all the widgets
        self.window.show_all()

    def delete_event(self, widget, event, data=None):
        """program quit when kill the window by window manager"""
        
        gtk.main_quit()
        return False

    def save_to_file(self, widget, data):
        """save the content of Entry to daily_notes file"""

        try:
            fd = open(self.note_file, 'r')
        except IOError, error:
            print "IOError: '%s' %s, errno: %d" % \
                    (self.note_file, error[1], error[0])
            return
        else:
            date = self.calendar_get_date_to_string()
            page = fd.read()
            contents = eval(page)
            contents[date] = data.get_text()

            # remove all empty keys
            for (k, v) in contents.items():
                if v == '':
                    del contents[k]

            fd.close()
            fd = open(self.note_file, 'w')
            fd.write(str(contents))
        finally:
            fd.close()

    def day_selected(self, widget, data=None):
        """update the gtk.Entry widget's content"""

        try:
            # to test if the open could be open as 'read' or not.
            fd = open(self.note_file, 'r')
        except IOError, error:
            # if the files doesnot exist, then create it.
            try:
                fd = open(self.note_file, 'w')
            except IOError, error:
                # file could not be created if it is not in 'HOME' directory.
                print "IOError: '%s' %s, errno: %d" % \
                        (self.note_file, error[1], error[0])
            else:
                # write a net line in case the file is empty.
                fd.write("{}")
                fd.close()
        else:
            self.check_mark_day(self)
            # file could be read, then start to read the contents.
            date = self.calendar_get_date_to_string()
            page = fd.read()
            contents = eval(page)

            # set the contents which you type in Entry of Entry.
            if contents.has_key(date):
                self.text_entry.set_text(str(contents[date]))
            else:
                self.text_entry.set_text('')
            fd.close()
            
    def calendar_get_date_to_string(self):
        """convert date to a string"""

        (year, month, day) = self.calendar.get_date()
        mytime = time.mktime((year, (month + 1), day, 0, 0, 0, 0, 0, -1))
        date = time.strftime("%F", time.localtime(mytime))
        return date

    def check_mark_day(self, widget, data=None):
        """mark the day which has contents which loading the window"""

        try:
            # to test if the open could be open as 'read' or not.
            fd = open(self.note_file, 'r')
        except IOError, error:
            print "IOError: '%s' %s, errno: %d" % \
                    (self.note_file, error[1], error[0])
        else:
            date = self.calendar_get_date_to_string()
            page = fd.read()
            contents = eval(page)
            
            # mark days which has notes
            self.calendar.clear_marks()
            for (d, c) in contents.iteritems():
                if d[0:7] == date[0:7] and c != '':
                    self.calendar.mark_day(int(d[8:]))

    def main(self):
        """main object method"""
        gtk.main()

# if this script was run in terminal
if __name__ == "__main__":
    daily_notes = Daily_notes()
    sys.exit(daily_notes.main())
