# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>
#
# Implementation of an UPnP Media Server reference 1.0

from brisa.core.reactors import GLib2Reactor
reactor = GLib2Reactor()

import os
import dbus.mainloop.glib

from brisa.core import config
from brisa.upnp.device import Device, Service
from brisa.upnp.services.cds import ContentDirectory
from brisa.upnp.services.connmgr import ConnectionManagerServer

from brisa_media_server.dms_dbus import DMSObject
from brisa_media_server.services.media_registrar_ms import MSMediaRegistrar


# Main Loop setup for DBus
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


class MediaServerDevice(object):
    """ Media Server reference 1.0 device implementation. Use should be basic
    start/stop and accessing the DBus interface.

    For more info on the methods of the DBus interface, please refer to the
    documentation located at the dbus module.
    """
    xbox_comp = config.get_parameter_bool('media_server', 'xbox_compatible')
    plugins_folder = config.get_parameter('media_server', 'home') + '/plugins'
    plugins_module_path = 'brisa_media_server.plugins'

    def __init__(self, server_name, listen_url=''):
        """ Constructor for the media server device.

        @param server_name: friendly name for the server
        @param listen_url: a specific URL to be used for publishing resources
                           and listening for requests. If not specified, the
                           url will be http://IP:random_port

        @type server_name: string
        @type listen_url: string
        """
        self.server_name = server_name
        self.listen_url = listen_url
        self.dms_dbus = None
        self.device = None

    def _create_device(self):
        if self.xbox_comp:
            # Hack to work with Windows Media Center
            model_name = "Windows Media Connect"
        else:
            model_name = 'BRisa Media Server version %s' % \
                         config.manager.brisa_version

        project_page = 'http://brisa.garage.maemo.org'
        serial_no = config.manager.brisa_version.replace('.', '').rjust(7, '0')
        self.device = Device('urn:schemas-upnp-org:device:MediaServer:1',
                             self.server_name,
                             force_listen_url=self.listen_url,
                             manufacturer='BRisa Team. Embedded '\
                                          'Laboratory and INdT Brazil',
                             manufacturer_url=project_page,
                             model_description='An Open Source UPnP Media '\
                                               'Server',
                             model_name=model_name,
                             model_number=config.manager.brisa_version,
                             model_url=project_page,
                             serial_number=serial_no)

    def _add_services(self):
        """ Creates services 'content directory' and 'connection manager', both
        compliant with the UPnP A/V 1.0 specification. Also attaches the Dbus
        interface to the services.
        """
        # Save reference for use on some DBus methods
        cds = ContentDirectory(self.plugins_folder,
                                    self.plugins_module_path)
        cm = ConnectionManagerServer()

        self.device.add_service(cds)
        self.device.add_service(cm)

        if self.xbox_comp:
            local_xml_path = os.path.join(os.path.dirname(__file__),
                                          'xml_descriptions')
            msreg = MSMediaRegistrar(local_xml_path)
            self.device.add_service(msreg)

        self.dms_dbus = DMSObject(cds, cm)

    def start(self):
        """ Starts the Media Server device.
        """
        self._create_device()
        self._add_services()
        self.device.start()
        reactor.add_after_stop_func(self.device.stop)
        reactor.main()
