# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

import os
import brisa_media_server

from brisa.core import config


def setup_basic_configuration():
    config.manager.set_parameter('media_server', 'name', 'BRisa Media Server')
    config.manager.set_parameter('media_server', 'owner', 'brisa-media-server')
    config.manager.set_parameter('media_server', 'home',
                                 brisa_media_server.__path__[0])
    config.manager.set_parameter('media_server', 'version',
                                 brisa_media_server.version)
    config.manager.set_parameter('media_server', 'xbox_compatible', 'True')


def setup_field_types():
    config.manager.set_parameter('media_server', 'name.field_type', 'entry')
    config.manager.set_parameter('media_server', 'xbox_compatible.field_type',
                                 'checkbox')


def main():
    setup_basic_configuration()
    setup_field_types()
    config.manager.save()


if __name__ == "__main__":
    main()
