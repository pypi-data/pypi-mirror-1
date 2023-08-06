# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

import gtk
import gtk.glade
from os.path import exists, expanduser, join, dirname
import os.path

from brisa.core import log, config


class Assistant(object):

    def __init__(self):
        self.xml = gtk.glade.XML(join(dirname(__file__),
                                 'assistant.glade'))
        self.window = self.xml.get_widget('assistant1')
        self.window.connect('destroy', self.quit)

        for p in range(4):
            page = self.window.get_nth_page(p)
            self.window.set_page_complete(page, True)
            self.window.set_page_title(page, 'BRisa Media Server Preferences')

        self.window.connect('apply', self.apply)
        self.window.connect('cancel', self.quit)
        self.window.connect('close', self.quit)
        self._autoguess_folders()

    def _autoguess_folders(self):
        music_folder_widget = self.xml.get_widget('music_folder')
        music_folder = join(expanduser('~'), 'Music')
        music_folder_m = join(expanduser('~'), '.MyDocs', '.sounds')

        video_folder_widget = self.xml.get_widget('video_folder')
        video_folder = join(expanduser('~'), 'Videos')
        video_folder_m = join(expanduser('~'), '.MyDocs', '.videos')

        pic_folder_widget = self.xml.get_widget('picture_folder')
        pic_folder = join(expanduser('~'), 'Pictures')
        pic_folder_m = join(expanduser('~'), '.MyDocs', '.images')

        if exists(music_folder):
            music_folder_widget.set_current_folder(music_folder)
        elif exists(music_folder_m):
            music_folder_widget.set_current_folder(music_folder_m)
        if exists(video_folder):
            video_folder_widget.set_current_folder(video_folder)
        elif exists(video_folder_m):
            video_folder_widget.set_current_folder(video_folder_m)
        if exists(pic_folder):
            pic_folder_widget.set_current_folder(pic_folder)
        elif exists(pic_folder_m):
            pic_folder_widget.set_current_folder(pic_folder_m)

    def quit(self, s=None, t=None):
        self.window.destroy()
        gtk.main_quit()

    def apply(self, b=None):
        plugin_sect = 'media_server_plugin-media-library'

        # Check if the plugin has already been basic config'd
        if plugin_sect not in config.manager.get_section_names():
            log.debug('Plugin config not created yet, trying to create it')
            # Create it!
            import brisa_media_server.plugins.media_library

            # Check again
            if plugin_sect not in config.manager.get_section_names():
                log.error('Could not create plugin config.')
                raise RuntimeError('Could not create plugin config.')
            else:
                log.debug('Plugin config created sucessfully')

        enable_music_watch = \
            self.xml.get_widget('enable_music_watch').get_active()
        enable_video_watch = \
            self.xml.get_widget('enable_video_watch').get_active()
        enable_pic_watch = \
            self.xml.get_widget('enable_picture_watch').get_active()

        xbox_compat = self.xml.get_widget('xbox_compat').get_active()
        server_name = self.xml.get_widget('server_name').get_text()

        if enable_music_watch:
            config.manager.set_parameter(plugin_sect, 'enable_audio_listing',
                                         True)
            folder = self.xml.get_widget('music_folder').get_current_folder()
            if folder:
                config.manager.set_parameter(plugin_sect, 'audio_folders',
                                             folder)
                log.debug('Music watch enabled to folder %s' % folder)
            else:
                log.error('Music watch enabled and empty folder')
        else:
            config.manager.set_parameter(plugin_sect, 'enable_audio_listing',
                                         False)
            log.debug('Music watch disabled')

        if enable_video_watch:
            config.manager.set_parameter(plugin_sect, 'enable_video_listing',
                                         True)
            folder = self.xml.get_widget('video_folder').get_current_folder()
            if folder:
                config.manager.set_parameter(plugin_sect, 'video_folders',
                                             folder)
                log.debug('Video watch enabled to folder %s' % folder)
            else:
                log.error('Music watch enabled and empty folder')
        else:
            config.manager.set_parameter(plugin_sect, 'enable_video_listing',
                                         False)
            log.debug('Video watch disabled')

        if enable_pic_watch:
            config.manager.set_parameter(plugin_sect, 'enable_image_listing',
                                         True)
            folder = self.xml.get_widget('picture_folder').get_current_folder()
            if folder:
                config.manager.set_parameter(plugin_sect, 'image_folders',
                                             folder)
                log.debug('Picture watch enabled to folder %s' % folder)
            else:
                log.error('Picture watch enabled and empty folder')
        else:
            config.manager.set_parameter(plugin_sect, 'enable_image_listing',
                                         False)
            log.debug('Picture watch disabled')


        log.debug('Xbox compatibility: %s' % str(xbox_compat))

        if xbox_compat:
            config.manager.set_parameter('media_server', 'xbox_cmopatible',
                                         True)
        else:
            config.manager.set_parameter('media_server', 'xbox_compatible',
                                         False)

        log.debug('Preffered server name: %s' % str(server_name))
        config.manager.set_parameter('media_server', 'name', server_name)
        config.manager.save()

    def run(self):
        self.window.show()
        gtk.main()


if __name__ == '__main__':
    assist = Assistant()
    assist.run()
