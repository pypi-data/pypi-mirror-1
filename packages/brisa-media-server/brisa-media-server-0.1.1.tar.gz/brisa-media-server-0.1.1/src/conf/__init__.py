# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

import os
import brisa_media_server.conf.gui

from brisa_media_server.conf import controller


def get_ifaces_list():
    """ Returns a list of available interfaces for the configuration.
    """
    return [s for s in dir(brisa_configuration_tool.gui) if '__' not in s]


def launch_gui(gui_name):
    _controller = controller.Controller()

    module_path = 'brisa_media_server.conf.gui.%s' % gui_name

    __import__(module_path, globals(), locals(), ['ConfigurationGUI'])

    _gui = eval('%s.ConfigurationGUI()' % module_path)
    _gui.set_controller(_controller)
    _gui.start()


def main():
    launch_gui('gtk')
