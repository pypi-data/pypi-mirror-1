# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>
#
# Implementation of a UPnP Media Renderer reference 1.0

from brisa.core.reactors import GLib2Reactor
reactor = GLib2Reactor()

import os
import dbus.mainloop.glib

from brisa.core import config
from brisa.upnp.device import Device, Service
from brisa.upnp.services.connmgr import ConnectionManagerRenderer

from brisa_media_renderer.services.avtransport import AVTransport
from brisa_media_renderer.services.render_control import RenderingControl
from brisa_media_renderer.dmr_dbus import DMRObject


# Main Loop setup for DBus
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


class MediaRendererDevice(object):
    """ Media Renderer reference 1.0 implementation. Use should be basic
    start/stop and accessing the DBus interface.

    The dbus interface contains the following methods:

    halt() - Halts the media renderer
    get_renderer_info() - Returns a 6-tuple containing information about the
                          device. The format is (device version, brisa
                          framework version, application version, renderer
                          name, logging level, logging output)

    This media renderer contains a .service dbus file. This means that
    bringing up the media renderer through its dbus interface can be simply
    achieved by using the object path and interface constants defined above
    to retrieve the dbus object.
    """

    def __init__(self, server_name, listen_url=''):
        """ Constructor for the media renderer device.

        @param server_name: friendly name for the device
        @param listen_url: a specific URL to be used for publishing resources
                           and listening for requests. If not specified, the
                           url will be http://IP:random_port

        @type server_name: string
        @type listen_url: string
        """
        self.server_name = server_name
        self.listen_url = listen_url

    def _create_device(self):
        """ Creates the root device and saves the information about the
        device.
        """
        project_page = 'http://brisa.garage.maemo.org'
        serial_no = config.manager.brisa_version.replace('.', '').rjust(7, '0')
        self.device = Device('urn:schemas-upnp-org:device:MediaRenderer:1',
                             self.server_name,
                             force_listen_url=self.listen_url,
                             manufacturer='BRisa Team. Embedded '\
                                          'Laboratory and INdT Brazil',
                             manufacturer_url=project_page,
                             model_description='An Open Source UPnP Media '\
                                               'Renderer',
                             model_name='BRisa Media Renderer',
                             model_number=config.manager.brisa_version,
                             model_url=project_page,
                             serial_number=serial_no)

    def _add_services(self):
        """ Creates the Service's objects and attachs them to the root device.
        Also attaches the dbus interface to the services.
        """
        local_xml_path = os.path.join(os.path.dirname(__file__),
                                      'xml_descriptions')

        avt = AVTransport(local_xml_path)
        rc = RenderingControl(local_xml_path, avt.get_player())
        cm = ConnectionManagerRenderer()

        self.device.add_service(cm)
        self.device.add_service(avt)
        self.device.add_service(rc)

        self.dmr_dbus = DMRObject(avt, rc, cm)

    def start(self):
        """ Starts the device.
        """
        self._create_device()
        self._add_services()
        self.device.start()
        reactor.add_after_stop_func(self.device.stop)
        reactor.main()

