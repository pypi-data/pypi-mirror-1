# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

__all__ = ['ConfigurationGUI']

import gtk
import gtk.glade

import os.path


class ConfigurationGUI(object):

    def __init__(self):
        self.controller = None
        self._fields = {}
        self.xml = gtk.glade.XML(os.path.join(os.path.dirname(__file__),
                                 'interface.glade'))
        self.window = self.xml.get_widget('gtk_gui')
        self.about_window = self.xml.get_widget('about')
        self.window.connect('destroy', gtk.main_quit)
        self._assign_signals()

    def _build_brisa_tab(self):
        """ Builds the tab on the notebook that corresponds with BRisa basic
        configurations.
        """
        # Get all items
        specs = self.controller.get_fields_specs('brisa')

        # Retrieve base scrolled window and create the new box to add
        # parameters
        box = self.xml.get_widget('brisa_scrolled')
        vbox = gtk.VBox()
        box.add_with_viewport(vbox)

        if not box:
            returnk

        # Main label
        main_label = gtk.Label('<b>Information about current python-brisa</b>')
        main_label.set_use_markup(True)
        main_label.show()
        align = gtk.Alignment(0.5)
        align.set_padding(5, 5, 10, 0)
        align.add(main_label)
        align.show()
        vbox.pack_start(align, False, False)

        # Add parameters
        for s in specs:
            if s.name == 'home':
                continue

            if s.type == 'checkbox':
                c = gtk.CheckButton(str(s))
                c.set_active(s.initial_value)
                c.show()
                align = gtk.Alignment()
                align.set_padding(5, 5, 8, 0)
                align.add(c)
                align.show()
                vbox.pack_start(align, False, False)
                self._fields[('brisa', s.name)] = c.get_active
            elif s.type == 'entry':
                label = gtk.Label('%s:' % str(s))
                label.set_justify(gtk.JUSTIFY_RIGHT)
                label.show()
                e = gtk.Entry()
                e.set_text(s.initial_value)
                e.show()
                in_hbox = gtk.HBox()
                in_hbox.pack_start(label, False, False)
                in_hbox.pack_start(e, False, False, 5)
                in_hbox.show()
                align = gtk.Alignment()
                align.set_padding(5, 5, 10, 0)
                align.add(in_hbox)
                align.show()
                vbox.pack_start(align, False, False)
                self._fields[('brisa', s.name)] = e.get_text
            elif s.type == 'select-file' or s.type == 'select-folder':
                label = gtk.Label('%s:' % str(s))
                label.set_justify(gtk.JUSTIFY_RIGHT)
                label.show()
                e = gtk.Entry()
                e.set_text(s.initial_value)
                e.show()
                button = None

                if s.type == 'select-file':
                    button = gtk.Button('Select', gtk.STOCK_FIND)
                    button.connect('clicked', lambda w, e:\
                                   self._select_file_dialog(e), e)
                else:
                    button = gtk.Button('Select', gtk.STOCK_ADD)
                    button.connect('clicked', lambda w, e:\
                                   self._select_folder_dialog(e), e)

                button.show()
                clear = gtk.Button('Clear', gtk.STOCK_CLEAR)
                clear.connect('clicked', lambda w, e: e.set_text(''), e)
                clear.show()
                in_hbox = gtk.HBox()
                in_hbox.pack_start(label, False, False)
                in_hbox.pack_start(e, False, False, 5)
                in_hbox.pack_start(button, False, False, 5)
                in_hbox.pack_start(clear, False, False, 5)
                in_hbox.show()
                align = gtk.Alignment()
                align.set_padding(5, 5, 10, 0)
                align.add(in_hbox)
                align.show()
                vbox.pack_start(align, False, False)
                self._fields[('brisa', s.name)] = e.get_text
            else:
                label = gtk.Label('%s: %s' % (str(s), s.initial_value))
                label.set_justify(gtk.JUSTIFY_RIGHT)
                label.show()
                align = gtk.Alignment()
                align.set_padding(5, 5, 10, 0)
                align.add(label)
                align.show()
                vbox.pack_start(align, False, False)

        vbox.show()

    def _build_server_tab(self):
        """ Builds the tab corresponding to media server configurations.
        """
        # Get box from glade and clean it
        box = self.xml.get_widget('media_server_scrolled')

        if not box:
            return

        for c in box.get_children():
            box.remove(c)

        # Box to add parameters
        vbox = gtk.VBox()
        box.add_with_viewport(vbox)

        main_label = gtk.Label('<b>Configuration for BRisa Media Server</b>')
        main_label.set_use_markup(True)
        main_label.show()
        align = gtk.Alignment(0.5)
        align.set_padding(5, 10, 10, 0)
        align.add(main_label)
        align.show()
        vbox.pack_start(align, False, False)

        specs = self.controller.get_fields_specs('media_server')

        for s in specs:
            if s.name == 'home':
                continue

            if s.type == 'checkbox':
                c = gtk.CheckButton(str(s))
                c.set_active(s.initial_value)
                c.show()
                align = gtk.Alignment()
                align.set_padding(5, 5, 8, 0)
                align.add(c)
                align.show()
                vbox.pack_start(align, False, False)
                self._fields[('media_server', s.name)] = c.get_active
            elif s.type == 'entry':
                label = gtk.Label('%s:' % str(s))
                label.set_justify(gtk.JUSTIFY_RIGHT)
                label.show()
                e = gtk.Entry()
                e.set_text(s.initial_value)
                e.show()
                in_hbox = gtk.HBox()
                in_hbox.pack_start(label, False, False)
                in_hbox.pack_start(e, False, False, 5)
                in_hbox.show()
                align = gtk.Alignment()
                align.set_padding(5, 5, 10, 0)
                align.add(in_hbox)
                align.show()
                vbox.pack_start(align, False, False)
                self._fields[('media_server', s.name)] = e.get_text
            elif s.type == 'select-file' or s.type == 'select-folder':
                label = gtk.Label('%s:' % str(s))
                label.set_justify(gtk.JUSTIFY_RIGHT)
                label.show()
                e = gtk.Entry()
                e.set_text(s.initial_value)
                e.show()
                button = None

                if s.type == 'select-file':
                    button = gtk.Button('Select', gtk.STOCK_FIND)
                    button.connect('clicked', lambda w, e:\
                                   self._select_file_dialog(e), e)
                else:
                    button = gtk.Button('Select', gtk.STOCK_ADD)
                    button.connect('clicked', lambda w, e:\
                                   self._select_folder_dialog(e), e)

                button.show()
                clear = gtk.Button('Clear', gtk.STOCK_CLEAR)
                clear.connect('clicked', lambda w, e: e.set_text(''), e)
                clear.show()
                in_hbox = gtk.HBox()
                in_hbox.pack_start(label, False, False)
                in_hbox.pack_start(e, False, False, 5)
                in_hbox.pack_start(button, False, False, 5)
                in_hbox.pack_start(clear, False, False, 5)
                in_hbox.show()
                align = gtk.Alignment()
                align.set_padding(5, 5, 10, 0)
                align.add(in_hbox)
                align.show()
                vbox.pack_start(align, False, False)
                self._fields[('media_server', s.name)] = e.get_text
            else:
                label = gtk.Label('%s: %s' % (str(s), s.initial_value))
                label.set_justify(gtk.JUSTIFY_RIGHT)
                label.show()
                align = gtk.Alignment()
                align.set_padding(5, 5, 10, 0)
                align.add(label)
                align.show()
                vbox.pack_start(align, False, False)

        vbox.show()

    def _build_plugins_tab(self):
        # Get scrolled for plugins, clean it
        scrolled = self.xml.get_widget('plugins_scrolled')

        for c in scrolled.get_children():
            scrolled.remove(c)

        # Create box for plugins
        main_vbox = gtk.VBox()
        scrolled.add_with_viewport(main_vbox)

        for p in self.controller.get_plugin_names():
            vbox = gtk.VBox()
            vbox.show()
            main_vbox.pack_start(vbox, False, False, 10)
            label = gtk.Label('<b>%s</b>' % ' '.join(w.capitalize() for w in\
                              p.replace('-', ' ').split(' ')))
            label.set_use_markup(True)
            align = gtk.Alignment()
            align.set_padding(5, 10, 10, 0)
            align.add(label)
            align.show()
            label.show()
            vbox.pack_start(align, False, False)

            separator = gtk.HSeparator()
            main_vbox.pack_start(separator)
            separator.show()

            specs = self.controller.get_plugin_fields_specs(p)

            for s in specs:
                if s.type == 'checkbox':
                    align = gtk.Alignment()
                    align.set_padding(5, 5, 20, 0)
                    c = gtk.CheckButton(s.label or \
                                        str(s))
                    c.set_active(s.initial_value)
                    c.show()
                    align.add(c)
                    align.show()
                    vbox.pack_start(align, False, False)
                    self._fields[('media_server_plugin-%s' % p, s.name)]\
                    = c.get_active
                elif s.type == 'entry':
                    label = gtk.Label('%s:' % (s.label or str(s)))
                    label.set_justify(gtk.JUSTIFY_RIGHT)
                    label.show()
                    e = gtk.Entry()
                    e.set_text(s.initial_value)
                    e.show()
                    in_hbox = gtk.HBox()
                    in_hbox.pack_start(label, False, False)
                    in_hbox.pack_start(e, False, False, 5)
                    in_hbox.show()
                    align = gtk.Alignment()
                    align.set_padding(5, 5, 20, 0)
                    align.add(in_hbox)
                    align.show()
                    vbox.pack_start(align, False, False)
                    self._fields[('media_server_plugin-%s' % p, s.name)]\
                    = e.get_text
                elif s.type == 'select-file' or s.type == 'select-folder':
                    label = gtk.Label('%s:' % str(s))
                    label.set_justify(gtk.JUSTIFY_RIGHT)
                    label.show()
                    e = gtk.Entry()
                    e.set_text(s.initial_value)
                    e.show()

                    if s.type == 'select-file':
                        button = gtk.Button('Select', gtk.STOCK_FIND)
                        button.connect('clicked', lambda w, e:\
                                       self._select_file_dialog(e), e)
                    else:
                        button = gtk.Button('Select', gtk.STOCK_ADD)
                        button.connect('clicked', lambda w, e:\
                                       self._select_folder_dialog(e), e)

                    button.show()
                    clear = gtk.Button('Clear', gtk.STOCK_CLEAR)
                    clear.connect('clicked', lambda w, e: e.set_text(''), e)
                    clear.show()
                    in_hbox = gtk.HBox()
                    in_hbox.pack_start(label, False, False)
                    in_hbox.pack_start(e, True, False, 5)
                    in_hbox.pack_start(button, False, False, 5)
                    in_hbox.pack_start(clear, False, False, 5)
                    in_hbox.show()
                    align = gtk.Alignment()
                    align.set_padding(5, 5, 20, 0)
                    align.add(in_hbox)
                    align.show()
                    vbox.pack_start(align, False, False)
                    self._fields[('media_server_plugin-%s' % p, s.name)] =\
                    e.get_text
                else:
                    label = gtk.Label('%s: %s' % (s.label or str(s),
                                                  s.initial_value))
                    label.set_justify(gtk.JUSTIFY_RIGHT)
                    label.show()
                    align = gtk.Alignment()
                    align.set_padding(5, 5, 20, 0)
                    align.add(label)
                    align.show()

        main_vbox.show()

    def _assign_signals(self):
        signals = {'on_save_button_clicked': self.save,
                   'on_revert_button_clicked': self.revert,
                   'on_quit_button_clicked': gtk.main_quit,
                   'on_about_button_clicked': self.about,
                   'on_about_close': lambda w: self.about_window.hide(),
                   'on_about_response': lambda w, v: self.about_window.hide()}

        self.xml.signal_autoconnect(signals)

    def _select_file_dialog(self, entry):
        window = gtk.FileChooserDialog(title='Select file',
                                  action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                       buttons=(gtk.STOCK_CANCEL,
                                                gtk.RESPONSE_CANCEL,
                                                gtk.STOCK_OPEN,
                                                gtk.RESPONSE_OK))
        window.set_select_multiple(False)
        window.set_show_hidden(True)
        window.set_current_folder(os.path.expanduser('~'))

        if window.run() == gtk.RESPONSE_OK:
            entry.set_text('%s' % window.get_filename())

        window.destroy()

    def _select_folder_dialog(self, entry):
        window = gtk.FileChooserDialog(title='Select folder',
                                  action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                       buttons=(gtk.STOCK_CANCEL,
                                                gtk.RESPONSE_CANCEL,
                                                gtk.STOCK_OPEN,
                                                gtk.RESPONSE_OK))
        window.set_select_multiple(True)
        window.set_current_folder(os.path.expanduser('~'))

        if window.run() == gtk.RESPONSE_OK:
            old_folders = entry.get_text()
            dir_names = window.get_filenames()
            if old_folders:
                entry.set_text('%s:%s' % (old_folders,
                               ':'.join(dir_names)))
            else:
                entry.set_text(':'.join(dir_names))

        window.destroy()

    def set_controller(self, c):
        self.controller = c

    def start(self):
        gtk.gdk.threads_init()
        self._build_server_tab()
        self._build_brisa_tab()
        self._build_plugins_tab()
        self.window.show()
        gtk.main()

    def save(self, button):
        for s in self._fields:
            self.controller.set_parameter(s[0], s[1], self._fields[s]())

        self.controller.save()

    def revert(self, button):
        self.controller.revert()
        self._build_server_tab()
        self._build_plugins_tab()

    def about(self, button):
        self.about_window = self.xml.get_widget('about')
        self.about_window.run()
