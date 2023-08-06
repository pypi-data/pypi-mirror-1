# Licensed # Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

import os.path

from brisa.core import log
from brisa.upnp.device import Service, ServiceController


log = log.getLogger('media_server.services.msmr')

service_name = 'X_MS_MediaReceiverRegistrar'
service_type = 'urn:microsoft.com:service:X_MS_MediaReceiverRegistrar:1'


class MSMediaRegistrar(Service):

    def __init__(self, xml_path):
        Service.__init__(self, service_name, service_type, '',
                         os.path.join(xml_path,
                                      'media-receiver-registrar-ms.xml'))

    def set_variables(self):
        self.set_variable(0, 'AuthorizationGrantedUpdateID', 0)
        self.set_variable(0, 'AuthorizationDeniedUpdateID', 0)
        self.set_variable(0, 'ValidationSucceededUpdateID', 0)
        self.set_variable(0, 'ValidationRevokedUpdateID', 0)

    def soap_IsAuthorized(self, *args, **kwargs):
        device_id = kwargs['DeviceID']
        log.info('IsAuthorized(%s)', device_id)
        return {'Result': 1}

    def soap_IsValidated(self, *args, **kwargs):
        device_id = kwargs['DeviceID']
        log.info('IsValidated(%s)', device_id)
        return {'Result': 1}

    def soap_RegisterDevice(self, *args, **kwargs):
        reg_msg = kwargs['RegistrationReqMsg']
        log.info('RegisterDevice(%s)', reg_msg)
        return {'RegistrationRespMsg': ' '}
