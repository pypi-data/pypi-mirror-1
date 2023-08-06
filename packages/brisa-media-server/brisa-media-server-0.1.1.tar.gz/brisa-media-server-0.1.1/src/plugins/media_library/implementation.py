# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

""" Media Library plugin enables sharing of locally stored media (audio, video,
image).
"""

import os.path
import lightmediascanner

from brisa.core.plugin import PluginInterface
from brisa.core.config import manager
from brisa.core import webserver

from brisa_media_server.plugins.media_library import facade

plugin_section = 'media_server_plugin-media-library'


class MediaLibraryResource(webserver.CustomResource):
    """ Resource for serving Media Library files.
    """

    def get_render(self, uri, request):
        id = uri.split('/')[-1].split('-')[1]
        path = facade.get_file_path(id)

        if path:
            return webserver.StaticFile(str(id), path)
        else:
            return None


class MediaLibrary(PluginInterface):
    """ Media Library plugin enables sharing of locally stored media.

    TODO: support playlists
    """
    name = 'media_library'
    usage = manager.get_parameter_bool(plugin_section, 'enable')
    db_path = manager.get_parameter(plugin_section, 'database_location')
    containers = {}
    containers_cb = {}
    media_scanner = None

    def load(self):
        """ Loads config, virtual containers according to config, publishes the
        resource and prepares the scanner.
        """
        self._load_config()
        self._load_scanner()

        if self.usage_audio:
            self._load_audio()

        if self.usage_video:
            self._load_video()

        if self.usage_image:
            self._load_images()

    def unload(self):
        facade.exit()

    def publish(self, webserver):
        facade.init(self.db_path, webserver)
        webserver.add_resource(MediaLibraryResource(self.name))

    def _load_scanner(self):
        """ Loads lightmediascanner with all parsers.
        """
        self.media_scanner = lightmediascanner.LightMediaScanner(self.db_path)

        for parser in ['asf', 'id3', 'jpeg', 'm3u', 'pls', 'png', 'rm',
                       'audio-dummy', 'video-dummy', 'dummy']:
            self.media_scanner.parser_find_and_add(parser)

    def process_all_folders(self):
        self._process_folder(self.audio_folders)
        self._process_folder(self.video_folders)
        self._process_folder(self.image_folders)

    def _process_folder(self, flist):
        """ Process each folder of a list.
        """
        for folder in flist:
            self.media_scanner.process(folder)

    def _check_folder(self, flist):
        """ Check each folder of a list.
        """
        for folder in flist:
            self.media_scanner.check(folder)

    def _load_config(self):
        """ Load config for Media Library plugin.
        """
        self.usage_audio = manager.get_parameter_bool(plugin_section,
                                                      'enable_audio_listing')
        self.usage_video = manager.get_parameter_bool(plugin_section,
                                                      'enable_video_listing')
        self.usage_image = manager.get_parameter_bool(plugin_section,
                                                      'enable_image_listing')
        self.audio_folders = manager.get_parameter_as_list(plugin_section,
                                                           'audio_folders',
                                                           ':')
        self.video_folders = manager.get_parameter_as_list(plugin_section,
                                                           'video_folders',
                                                           ':')
        self.image_folders = manager.get_parameter_as_list(plugin_section,
                                                           'image_folders',
                                                           ':')
        self.already_scanned = manager.get_parameter_bool(plugin_section,
                                                     '.scanned')


        if not self.already_scanned:
            manager.set_parameter(plugin_section, '.scanned', True)
            manager.save()

    def _load_audio(self):
        """ Loads audio virtual containers.
        """
        if self.already_scanned:
            self._check_folder(self.audio_folders)
        else:
            self._process_folder(self.audio_folders)

        rp = self.plugin_manager.root_plugin

        audio_container = rp.get_container('Audio')

        if not audio_container:
            audio_container = rp.add_container('Audio', 0)

        self.genres_container = rp.add_container('Audio Genres',
                                                 audio_container.id, self)
        self.artists_container = rp.add_container('Audio Artists',
                                                  audio_container.id, self)
        self.albums_container = rp.add_container('Audio Albums',
                                                 audio_container.id, self)
        self.all_container = rp.add_container('All Audios',
                                              audio_container.id, self)
        self.containers[self.genres_container.id] = self.genres_container
        self.containers[self.artists_container.id] = self.artists_container
        self.containers[self.albums_container.id] = self.albums_container
        self.containers[self.all_container.id] = self.all_container

        self.containers_cb[self.genres_container.id] = facade.get_audio_genres
        self.containers_cb[self.artists_container.id] = \
            facade.get_audio_artists
        self.containers_cb[self.albums_container.id] = facade.get_audio_albums
        self.containers_cb[self.all_container.id] = facade.get_audio_all

        playlist_container = rp.get_container('Playlists')

        if not playlist_container:
            playlist_container = rp.add_container('Playlists', 0)

        self.playlists_container = rp.add_container('Local Playlists',
                                                    playlist_container.id,
                                                    self)
        self.containers[self.playlists_container.id] = self.playlists_container
        self.containers_cb[self.playlists_container.id] = facade.get_playlists

    def _load_video(self):
        """ Loads video virtual containers.
        """
        if self.already_scanned:
            self._check_folder(self.video_folders)
        else:
            self._process_folder(self.video_folders)

        rp = self.plugin_manager.root_plugin

        videos_container = rp.get_container('Videos')

        if not videos_container:
            videos_container = rp.add_container('Videos', 0)

        self.videos_container = rp.add_container('All Videos',
                                                 videos_container.id, self)
        self.containers[self.videos_container.id] = self.videos_container
        self.containers_cb[self.videos_container.id] = facade.get_videos_local

    def _load_images(self):
        """ Loads image virtual containers.
        """
        if self.already_scanned:
            self._check_folder(self.image_folders)
        else:
            self._process_folder(self.image_folders)

        rp = self.plugin_manager.root_plugin

        image_container = rp.get_container('Images')

        if not image_container:
            image_container = rp.add_container('Images', 0)

        self.images_container = rp.add_container('All Images',
                                                 image_container.id, self)
        self.containers[self.images_container.id] = self.images_container
        self.containers_cb[self.images_container.id] = facade.get_images_local

    def unload(self):
        """ Unloads Media Library plugin.
        """
        pass

    def browse(self, id, browse_flag, filter, starting_index, requested_count,
               sort_criteria):
        """ Plugin.browse() implementation.
        """
        if id in self.containers:
            if not self.containers[id].items:
                self.containers[id].items = self.containers_cb[id]()
            return self.containers[id].items
        else:
            return self._inner_browse(id)

    def _inner_browse(self, id):
        """ Folders and items browse.
        """
        namespace, id = id.split(':')[1].split('-')

        if not namespace or not id:
            # If browse does not have a namespace and reached here, there's
            # probably a malicious control point trying to break things.
            # Id should not eval to False (0, '', etc..) (invalid id's).
            return []

        return {'audio': lambda id: facade.get_audio_item(id),
                'video': lambda id: facade.get_video_item(id),
                'image': lambda id: facade.get_image_item(id),
                'genre': lambda id: facade.get_audio_genre(id),
                'album': lambda id: facade.get_audio_album(id),
                'artist': lambda id: facade.get_audio_artist(id),
                'playlist': lambda id: facade.get_playlist(id)}.\
                get(namespace, lambda id: [])(id)
