# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

import dbus.service

from brisa.core import reactor, log, config, threaded_call


# DBus constants
DBUS_OBJECT_PATH = '/br/edu/ufcg/embedded/brisa/MediaServer'
DBUS_IF = 'br.edu.ufcg.embedded.brisa.MediaServer'

cfg_mger = config.manager
cfg_section = 'media_server'
mlib_section = 'media_server_plugin-media-library'


class DMSObject(dbus.service.Object):
    """ DBus interface for the media server, or DMS (Digital Media Server).

    This media server contains a .service dbus file. This means that
    bringing up the media server through its dbus interface can be simply
    achieved by using the object path and interface constants defined above
    to retrieve the dbus object.
    """
    def __init__(self, cds_service, connmgr_service):
        bus_name = dbus.service.BusName(DBUS_IF, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, DBUS_OBJECT_PATH)
        self.cds = cds_service
        self.connmgr = connmgr_service
        self.cds_ctrl = self.cds.control_controller
        self.cm_ctrl = self.connmgr.control_controller

    @dbus.service.method(DBUS_IF)
    def dms_halt(self):
        """ Halts the media server.
        """
        reactor.main_quit()

    @dbus.service.method(DBUS_IF)
    def dms_get_server_info(self):
        """ Returns a 7-tuple containing information about the device. The
        format is (device version, brisa framework version, application
        version, server name, xbox compatibility, logging level, logging
        output).

        @rtype: tuple
        """
        version = 'MediaServer V 1.0'
        brisa_version = cfg_mger.get_parameter('brisa', 'version')
        app_version = cfg_mger.get_parameter(cfg_section, 'version')
        server_name = cfg_mger.get_parameter(cfg_section, 'name')
        xbox_compat = cfg_mger.get_parameter(cfg_section, 'xbox_compatible')
        log_level = cfg_mger.get_parameter('brisa', 'logging')
        log_output = cfg_mger.get_parameter('brisa', 'logging_output')
        return (version, brisa_version, app_version, server_name, xbox_compat,
                log_level, log_output)

    @dbus.service.method(DBUS_IF)
    def dms_reload_config(self):
        cfg_mger.update()

    @dbus.service.method(DBUS_IF)
    def dms_save_config(self):
        cfg_mger.save()

    @dbus.service.method(DBUS_IF)
    def dms_set_xbox_compatibility(self, enable=True):
        cfg_mger.set_parameter(cfg_section, 'xbox_compatible', bool(enable))

    # Content Directory

    @dbus.service.method(DBUS_IF)
    def dms_cds_list_watched_audio_folders(self):
        l = cfg_mger.get_parameter_as_list(mlib_section, 'audio_folders')
        if not l:
            return None
        return l

    @dbus.service.method(DBUS_IF)
    def dms_cds_list_watched_video_folders(self):
        l = cfg_mger.get_parameter_as_list(mlib_section, 'video_folders')
        if not l:
            return None
        return l

    @dbus.service.method(DBUS_IF)
    def dms_cds_list_watched_picture_folders(self):
        l = cfg_mger.get_parameter_as_list(mlib_section, 'image_folders')
        if not l:
            return None
        return l

    @dbus.service.method(DBUS_IF)
    def dms_cds_remove_watched_audio_folder(self, folder):
        folders = cfg_mger.get_parameter_as_list(mlib_section, 'audio_folders')
        if folder in folders:
            folders.remove(folder)
            cfg_mger.set_parameter(mlib_section,
                                   'audio_folders',
                                   ':'.join(folders))

    @dbus.service.method(DBUS_IF)
    def dms_cds_remove_watched_video_folder(self, folder):
        folders = cfg_mger.get_parameter_as_list(mlib_section, 'video_folders')
        if folder in folders:
            folders.remove(folder)
            cfg_mger.set_parameter(mlib_section,
                                   'video_folders',
                                   ':'.join(folders))

    @dbus.service.method(DBUS_IF)
    def dms_cds_remove_watched_picture_folder(self, folder):
        folders = cfg_mger.get_parameter_as_list(mlib_section, 'image_folders')
        if folder in folders:
            folders.remove(folder)
            cfg_mger.set_parameter(mlib_section,
                                   'image_folders',
                                   ':'.join(folders))

    @dbus.service.method(DBUS_IF)
    def dms_cds_add_watch_audio_folder(self, folder):
        folders = cfg_mger.get_parameter_as_list(mlib_section, 'audio_folders')
        if folder not in folders:
            folders.append(folder)
            cfg_mger.set_parameter(mlib_section,
                                   'audio_folders',
                                   ':'.join(folders))

    @dbus.service.method(DBUS_IF)
    def dms_cds_add_watch_video_folder(self, folder):
        folders = cfg_mger.get_parameter_as_list(mlib_section, 'video_folders')
        if folder not in folders:
            folders.append(folder)
            cfg_mger.set_parameter(mlib_section,
                                   'video_folders',
                                   ':'.join(folders))

    @dbus.service.method(DBUS_IF)
    def dms_cds_add_watch_picture_folder(self, folder):
        folders = cfg_mger.get_parameter_as_list(mlib_section, 'image_folders')
        if folder not in folders:
            folders.append(folder)
            cfg_mger.set_parameter(mlib_section,
                                   'image_folders',
                                   ':'.join(folders))

    @dbus.service.method(DBUS_IF)
    def dms_cds_rescan_folders(self):
        if not self.cds:
            return
        pm = self.cds_ctrl.plugin_manager
        # HACK: should we have access to plugins ? If so, fix this hack
        if not 'media_library' in pm.plugins_instances:
            return

        ml = pm.plugins_instances['media_library']
        threaded_call.run_async_function(ml.process_all_folders)

    @dbus.service.method(DBUS_IF)
    def dms_cds_browse(self, object_id, browse_flag, filter, starting_index,
                       requested_count, sort_criteria):
        # TODO improve the service so that you don't have to reuse this soap
        # method.
        ret = self.cds_ctrl.soap_Browse(ObjectID=str(object_id),
                                        BrowseFlag=str(browse_flag),
                                        Filter=str(filter),
                                        StartingIndex=int(starting_index),
                                        RequestedCount=int(requested_count),
                                        SortCriteria=str(sort_criteria))
        return ret['BrowseResponse'].get('Result', '')

    @dbus.service.method(DBUS_IF)
    def dms_cds_search(self, container_id, search_criteria, filter,
                       starting_index, requested_count, sort_criteria):
        # TODO improve the service so that you don't have to reuse this soap
        # method.
        ret = self.cds_ctrl.soap_Search(ContainerID=str(container_id),
                                        SearchCriteria=str(search_criteria),
                                        Filter=str(filter),
                                        StartingIndex=int(starting_index),
                                        RequestedCount=int(requested_count),
                                        SortCriteria=str(sort_criteria))
        return ret['SearchResponse'].get('Result', '')

    @dbus.service.method(DBUS_IF)
    def dms_cds_get_search_caps(self):
        ret = self.cds_ctrl.soap_GetSearchCapabilities()
        return ret['SearchCapabilitiesResponse'].get('SearchCaps', '')

    @dbus.service.method(DBUS_IF)
    def dms_cds_get_sort_caps(self):
        ret = self.cds_ctrl.soap_GetSortCapabilities()
        return ret['SortCapabilitiesResponse'].get('SortCaps', '')

    @dbus.service.method(DBUS_IF)
    def dms_cds_get_system_update_id(self):
        ret = self.cds_ctrl.soap_GetSystemUpdateID()
        return ret['GetSystemUpdateIDResponse'].get('Id', '')

    @dbus.service.method(DBUS_IF)
    def dms_cm_get_protocol_info(self):
        ret = self.cm_ctrl.soap_GetProtocolInfo()
        return ret['GetProtocolInfoResponse']

    @dbus.service.method(DBUS_IF)
    def dms_cm_get_current_connection_ids(self):
        ret = self.cm_ctrl.soap_GetCurrentConnectionIDs()
        return ret['GetCurrentConnectionIDsResponse']

    @dbus.service.method(DBUS_IF)
    def dms_cm_get_current_connection_info(self):
        ret = self.cm_ctrl.soap_GetCurrentConnectionInfo()
        return ret['GetCurrentConnectionInfoResponse']
