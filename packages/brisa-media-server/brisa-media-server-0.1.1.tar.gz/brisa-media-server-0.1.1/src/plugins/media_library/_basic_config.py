# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

import os
import brisa_media_server

from brisa.core import config


user_home = os.path.expanduser('~')
plugin_section = 'media_server_plugin-media-library'


def guess_folder(match_list):
    matchs = []

    for k in [user_home, '%s/MyDocs' % user_home]:
        for (root, dirs, others) in os.walk(k):
            if root != k:
                break
            matchs.extend(['%s/%s' % (root, f) for f in match_list \
                           if f in dirs])

    return ':'.join(matchs)


def setup_basic_configuration():
    audio_folder = guess_folder(['music', 'Music', 'audio', 'Audio',
                                 '.sounds'])
    video_folder = guess_folder(['video', 'Video', 'videos', 'Videos',
                                 '.videos'])
    image_folder = guess_folder(['pictures', 'Pictures', 'images', 'Images',
                                 '.images'])

    config.manager.set_parameter(plugin_section, 'owner',
                                 'media_server_plugin-media_library')
    config.manager.set_parameter(plugin_section, 'database_location',
                                 '%s/%s' % (user_home,
                                            '.brisa/media_library.db'))
    config.manager.set_parameter(plugin_section, 'enable', True)

    config.manager.set_parameter(plugin_section, 'audio_folders', audio_folder)
    config.manager.set_parameter(plugin_section, 'video_folders', video_folder)
    config.manager.set_parameter(plugin_section, 'image_folders', image_folder)

    config.manager.set_parameter(plugin_section, 'enable_audio_listing',
                                 True)
    config.manager.set_parameter(plugin_section, 'enable_video_listing',
                                 True)
    config.manager.set_parameter(plugin_section, 'enable_image_listing',
                                 True)


def setup_fields_spec():
    config.manager.set_parameter(plugin_section, 'enable.field_type',
                                 'checkbox')
    config.manager.set_parameter(plugin_section, 'enable.priority',
                                 '0')

    config.manager.set_parameter(plugin_section,
                                 'audio_folders.field_type',
                                 'select-folder')
    config.manager.set_parameter(plugin_section,
                                 'audio_folders.priority',
                                 '7')

    config.manager.set_parameter(plugin_section,
                                 'video_folders.field_type',
                                 'select-folder')
    config.manager.set_parameter(plugin_section,
                                 'video_folders.priority',
                                 '8')

    config.manager.set_parameter(plugin_section,
                                 'image_folders.field_type',
                                 'select-folder')
    config.manager.set_parameter(plugin_section,
                                 'image_folders.priority',
                                 '9')

    config.manager.set_parameter(plugin_section,
                                 'enable_audio_listing.field_type',
                                 'checkbox')
    config.manager.set_parameter(plugin_section,
                                 'enable_audio_listing.priority',
                                 '1')

    config.manager.set_parameter(plugin_section,
                                 'enable_video_listing.field_type',
                                 'checkbox')
    config.manager.set_parameter(plugin_section,
                                 'enable_video_listing.priority',
                                 '2')

    config.manager.set_parameter(plugin_section,
                                 'enable_image_listing.field_type',
                                 'checkbox')
    config.manager.set_parameter(plugin_section,
                                 'enable_image_listing.priority',
                                 '3')


def main():
    setup_basic_configuration()
    setup_fields_spec()
    config.manager.save()


if __name__ == "__main__":
    main()
