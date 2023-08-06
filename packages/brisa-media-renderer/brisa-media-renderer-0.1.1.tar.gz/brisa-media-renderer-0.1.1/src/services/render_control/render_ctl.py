# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

__all__ = ('RenderingControl', )

import os.path

from brisa.core import log
from brisa.upnp.device import Service, ServiceController


service_name = 'RenderingControl'
service_type = 'urn:schemas-upnp-org:service:RenderingControl:1'


class RenderingControl(Service):

    def __init__(self, xml_path, gst_player):
        Service.__init__(self, service_name, service_type, '',
                         os.path.join(xml_path, 'render-control-scpd.xml'))
        self.gst_player = gst_player

    def soap_ListPresets(self, *args, **kwargs):
        """ Return List of currently defined. This action returns a list of
        the currently defined presets.
        """
        log.debug('Action on RenderingControlController: ListPresets()')
        return {'CurrentPresetNameList': ''}

    def soap_SelectPreset(self, *args, **kwargs):
        """ Select Present state variables. This action restores (a subset) of
        the state variables to the values associated with the specified
        preset.
        """
        log.debug('Action on RenderingControlController: SelectPreset()')
        return {}

    def soap_GetVolume(self, *args, **kwargs):
        """ Return the current volume state. This action retrieves the current
        value of the Volume state variable of the specified channel for the
        specified instance of this service
        """
        log.debug('Action on RenderingControlController: GetVolume()')
        (instance_id, channel) = args
        volume = int(self.gst_player.get_volume())
        return {'CurrentVolume': volume}

    def soap_SetVolume(self, *args, **kwargs):
        """Set volume of instance and chanel.

        This action sets the Volume state variable of the specified
        instance and channel to the specified value."""
        log.debug('Action on RenderingControlController: SetVolume%s', args)
        (instance_id, channel, desired_volume) = args
        self.gst_player.set_volume(int(desired_volume))
        return {}
