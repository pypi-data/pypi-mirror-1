# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

__all__ = ['MediaServerDevice']

from brisa.core import config

version = '0.1.1'


def check_config():
    # Check if basic config has been set up already. If not, do it.
    name = config.get_parameter('media_server', 'name')
    if not name:
        from brisa_media_server import _basic_config
        _basic_config.main()

check_config()

from brisa_media_server.media_server_impl import MediaServerDevice
