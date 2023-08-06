# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

import dbus.service

from brisa.core import reactor, log, config


# DBus constants
DBUS_OBJECT_PATH = '/br/edu/ufcg/embedded/brisa/MediaRenderer'
DBUS_IF = 'br.edu.ufcg.embedded.brisa.MediaRenderer'


class DMRObject(dbus.service.Object):
    """ DBus interface for the media renderer, or DMR (Digital Media Renderer).

    This media renderer contains a .service dbus file. This means that
    bringing up the media renderer through its dbus interface can be simply
    achieved by using the object path and interface constants defined above
    to retrieve the dbus object.
    """
    def __init__(self, avt_service, rc_service, cm_service):
        bus_name = dbus.service.BusName(DBUS_IF, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, DBUS_OBJECT_PATH)
        self.avt = avt_service.control_controller
        self.rc = rc_service.control_controller
        self.cm = cm_service.control_controller

    @dbus.service.method(DBUS_IF)
    def dmr_halt(self):
        """ Halts the media renderer.
        """
        reactor.main_quit()

    @dbus.service.method(DBUS_IF)
    def dmr_get_renderer_info(self):
        """ Returns a 6-tuple containing information about the device. The
        format is (device version, brisa framework version, application
        version, renderer name, logging level, logging output).

        @rtype: tuple
        """
        version = 'MediaRenderer V 1.0'
        brisa_version = config.get_parameter('brisa', 'version')
        app_version = config.get_parameter('media_renderer', 'version')
        name = config.get_parameter('media_renderer', 'name')
        log_level = config.get_parameter('brisa', 'logging')
        log_output = config.get_parameter('brisa', 'logging_output')
        return (version, brisa_version, app_version, name, log_level,
                log_output)

    # AVTransport

    @dbus.service.method(DBUS_IF)
    def dmr_avt_set_av_transport_uri(self, instance_id, current_uri,
                                     current_uri_metadata):
        ret = self.avt.soap_SetAVTransportURI(InstanceID=str(instance_id),
                                              CurrentURI=str(current_uri),
                                              CurrentURIMetaData=\
                                              str(current_uri_metadata))
        return ret['SetAVTransportURIResponse'] or ''

    @dbus.service.method(DBUS_IF)
    def dmr_avt_get_media_info(self):
        return self.avt.soap_GetMediaInfo()['GetMediaInfoResponse']

    @dbus.service.method(DBUS_IF)
    def dmr_avt_get_media_info_ext(self):
        return self.avt.soap_GetMediaInfo_Ext()['GetMediaInfo_ExtResponse']

    @dbus.service.method(DBUS_IF)
    def dmr_avt_get_transport_info(self):
        return self.avt.soap_GetTransportInfo()['GetTransportInfoResponse']

    @dbus.service.method(DBUS_IF)
    def dmr_avt_get_position_info(self):
        ret = self.avt.soap_GetPositionInfo()['GetPositionInfoResponse']
        return ret

    @dbus.service.method(DBUS_IF)
    def dmr_avt_get_device_caps(self):
        ret = self.avt.soap_GetDeviceCapabilities()
        return ret['GetDeviceCapabilitiesResponse']

    @dbus.service.method(DBUS_IF)
    def dmr_avt_get_transport_settings(self):
        ret = self.avt.soap_GetTransportSettings()
        return ret['GetTransportSettingsResponse']

    @dbus.service.method(DBUS_IF)
    def dmr_avt_play(self):
        return self.avt.soap_Play()['PlayResponse'] or ''

    @dbus.service.method(DBUS_IF)
    def dmr_avt_stop(self):
        return self.avt.soap_Stop()['StopResponse'] or ''

    @dbus.service.method(DBUS_IF)
    def dmr_avt_pause(self):
        return self.avt.soap_Pause()['PauseResponse'] or ''

    @dbus.service.method(DBUS_IF)
    def dmr_avt_seek(self, instance_id, unit, target):
        return self.avt.soap_Seek(instance_id, unit, target)['SeekResponse'] \
           or ''

    @dbus.service.method(DBUS_IF)
    def dmr_avt_next(self):
        return self.avt.soap_Next()['NextResponse'] or ''

    @dbus.service.method(DBUS_IF)
    def dmr_avt_previous(self):
        return self.avt.soap_Previous()['PreviousResponse'] or ''

    # Render Control

    @dbus.service.method(DBUS_IF)
    def dmr_rc_list_presets(self):
        return self.rc.soap_ListPresets()['ListPresetsResponse']

    @dbus.service.method(DBUS_IF)
    def dmr_rc_select_preset(self, preset):
        return self.rc.soap_SelectPreset(preset)['SelectPresetResponse'] or ''

    @dbus.service.method(DBUS_IF)
    def dmr_rc_get_volume(self, instance_id, channel):
        return self.rc.soap_GetVolume(instance_id, channel)['GetVolumeResponse']

    @dbus.service.method(DBUS_IF)
    def dmr_rc_set_volume(self, instance_id, channel, desired_volume):
        ret = self.rc.soap_SetVolume(instance_id, channel, desired_volume)
        return ret['SetVolumeResponse'] or ''

    # Connection Manager

    @dbus.service.method(DBUS_IF)
    def dmr_cm_get_protocol_info(self):
        return self.cm.soap_GetProtocolInfo()['GetProtocolInfoResponse']

    @dbus.service.method(DBUS_IF)
    def dmr_cm_get_current_connection_info(self):
        ret = self.cm.soap_GetCurrentConnectionInfo()
        return ret['GetCurrentConnectionInfoResponse']

    @dbus.service.method(DBUS_IF)
    def dmr_cm_get_current_connection_ids(self):
        ret = self.cm.soap_GetCurrentConnectionIDs()
        return ret['GetCurrentConnectionIDsResponse']
