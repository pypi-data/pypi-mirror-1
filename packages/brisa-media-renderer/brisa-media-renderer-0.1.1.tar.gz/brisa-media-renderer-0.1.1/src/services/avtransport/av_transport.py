# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

__all__ = ('AVTransport', )

import os.path
import platform

from brisa.core import log
from brisa.upnp.device import Service, ServiceController
from brisa_media_renderer.services.gst_renderer import GSTRendererMaemo,\
GSTRenderer

service_name = 'AVTransport'
service_type = 'urn:schemas-upnp-org:service:AVTransport:1'


class AVTransport(Service):

    def __init__(self, xml_path):
        Service.__init__(self, service_name, service_type, '',
                         os.path.join(xml_path, 'render-transport-scpd.xml'))
        self.av_transport_uri = ''
        self.number_of_tracks = 0

        if "arm" in platform.uname()[4]:
            self.gst_player = GSTRendererMaemo()
        elif platform.system() == 'Linux':
            self.gst_player = GSTRenderer()

        self.urilist = {}
        self.transport_state = 'NO_MEDIA_PRESENT'
        self.transport_status= 'OK'
        self.transport_speed = 1

    def get_player(self):
        return self.gst_player

    def soap_SetAVTransportURI(self, *args, **kwargs):
        """Specifies the URI of resource.

        This action specifies the URI of the resource to be controlled
        by the specified AVTransport instance. It is RECOMMENDED that the
        AVTransport service checks the MIME-type of the specified resource
        when executing this action"""

        instance_id = kwargs['InstanceID']
        current_uri = kwargs['CurrentURI']
        current_uri_metadata = kwargs['CurrentURIMetaData']

        self.av_transport_uri = current_uri
        self.number_of_tracks = 1
        self.gst_player.av_uri = current_uri
        self.transport_state = 'STOPPED'

        log.info('SetAVTransportURI()')

        return {'SetAVTransportURI': {}}

    def soap_GetMediaInfo(self, *args, **kwargs):
        """Return information of current Media.

        This action returns information associated with the current
        media of the specified instance; it has no effect on state."""

        log.info('GetMediaInfo()')

        return {'NrTracks': str(self.number_of_tracks),
                'MediaDuration': str(self.gst_player.query_duration()[0]),
                'CurrentURI': self.av_transport_uri,
                'CurrentURIMetaData': '',
                'NextURI': '', 'NextURIMetaData': '',
                'PlayMedium': 'NETWORK',
                'RecordMedium': '',
                'WriteStatus': ''}

    def soap_GetMediaInfo_Ext(self, *args, **kwargs):
        """Return information of current Media and CurrentType argment.

        This action returns information associated with the current
        media of the specified instance; it has no effect on state.The
        information returned is identical to the information returned
        by the GetMediaInfo() action, except for the additionally
        returned CurrentType argument """

        log.info('GetMediaInfo_Ext()')

        return {'CurrentType': 'TRACK_UNAWARE',
                'NrTracks': str(self.number_of_tracks),
                'MediaDuration': str(self.gst_player.query_duration()[0]),
                'CurrentURI': self.av_transport_uri,
                'CurrentURIMetaData': '',
                'NextURI': '', 'NextURIMetaData': '',
                'PlayMedium': 'NETWORK',
                'RecordMedium': '',
                'WriteStatus': ''}

    def soap_GetTransportInfo(self, *args, **kwargs):
        """Return informations os current Transport state.

        This action returns information associated with the current
        transport state of the specified instance; it has no effect on
        state."""

        self.transport_state = self.gst_player.get_state()

        return {'CurrentTransportState':
                                             self.transport_state,
                                             'CurrentTransportStatus':
                                             self.transport_status,
                                             'CurrentSpeed':
                                             str(self.transport_speed)}

    def soap_GetPositionInfo(self, *args, **kwargs):
        """Return information of the Transporte of the specified instante.

        This action returns information associated with the current
        position of the transport of the specified instance; it has no
        effect on state."""

        dur = self.gst_player.query_duration()
        pos = self.gst_player.query_position()

        duration = dur[0]

        if dur[1] == -1:
            duration = pos[0]


        abs_pos = pos[1]
        rel_pos = pos[1]

        if dur[1] > 2147483646:
            abs_pos = pos[1]*2147483646/dur[1]

        if pos[1] == -1:
            abs_pos = 0
            rel_pos = 0

        return {'Track': '1',
                                            'TrackDuration': \
                                            '"%s"' % str(duration) if duration \
                                            else '',
                                            'TrackMetaData': '',
                                            'TrackURI': \
                                            self.av_transport_uri,
                                            'RelTime': '"%s"' % str(pos[0]) if\
                                            pos[0] else '',
                                            'AbsTime': '"%s"' % str(pos[0]) if\
                                            pos[0] else '',
                                            'RelCount': str(rel_pos),
                                            'AbsCount': str(abs_pos)}

    def soap_GetDeviceCapabilities(self, *args, **kwargs):
        """Return information on device capabilities.

        This action returns information on device capabilities of
        the specified instance, such as the supported playback and
        recording formats, and the supported quality levels for
        recording. This action has no effect on state."""

        log.info('GetDeviceCapabilities()')

        return {'PlayMedia': 'NONE',
                                        'RecMedia': 'NOT_IMPLEMENTED',
                                        'ReqQualityMode': 'NOT_IMPLEMENTED'}

    def soap_GetTransportSettings(self, *args, **kwargs):
        """Return information on various settings of instance.

        This action returns information on various settings of the
        specified instance, such as the current play mode and the
        current recording quality mode. This action has no effect on
        state."""

        log.info('GetTransportSettings()')

        return {'PlayMode': 'DIRECT_1',
                                        'ReqQualityMode': 'NOT_IMPLEMENTED'}

    def soap_Stop(self, *args, **kwargs):
        """Stop progression of current resource.

        This action stops the progression of the current resource that
        is associated with the specified instance."""

        log.info('Stop()')
        self.transport_state = 'TRANSITIONING'
        self.gst_player.stop()
        self.transport_state = 'STOPPED'

        return {}

    def soap_Play(self, *args, **kwargs):
        """Play the resource of instance.

        This action starts playing the resource of the specified
        instance, at the specified speed, starting at the current
        position, according to the current play mode."""

        log.info('Play()')
        log.debug('Playing uri: %r', self.gst_player.av_uri)
        self.transport_state = 'TRANSITIONING'

        self.gst_player.play()

        self.transport_state = 'PLAYING'

        return {}

    def soap_Pause(self, *args, **kwargs):
        """Pause the resouce of instance.

        This action starts playing the resource of the specified
        instance, at the specified speed, starting at the current
        position, according to the current play mode."""

        log.info('Pause()')

        self.transport_state = 'TRANSITIONING'

        self.gst_player.pause()

        self.transport_state = 'PAUSED_PLAYBACK'

        return {}

    def soap_Seek(self, *args, **kwargs):
        """Seek through the resource controlled.

        This action starts seeking through the resource controlled
        by the specified instance - as fast as possible - to the position,
        specified in the Target argument."""

        (instance_id, unit, target) = args

        self.gst_player.seek(unit, target)

        log.info('Seek()')

        return {}

    def soap_Next(self, *args, **kwargs):
        """Advance to the next track.

        This is a convenient action to advance to the next track. This
        action is functionally equivalent to Seek(TRACK_NR, CurrentTrackNr+1).
        This action does not cycle back to the first track."""

        log.info('Next()')
        return {}

    def soap_Previous(self, *args, **kwargs):
        """Advance to the previous track.

        This is a convenient action to advance to the previous track. This
        action is functionally equivalent to Seek(TRACK_NR, CurrentTrackNr-1).
        This action does not cycle back to the last track."""

        log.info('Previous()')
        return {}
