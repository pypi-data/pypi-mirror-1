# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

import os
import brisa_media_renderer

from brisa.core import config


def setup_basic_configuration():
    config.manager.set_parameter('media_renderer', 'name',
                                 'BRisa Media Renderer')
    config.manager.set_parameter('media_renderer', 'owner',
                                 'brisa-media-renderer')
    config.manager.set_parameter('media_renderer', 'home',
                                 brisa_media_renderer.__path__[0])
    config.manager.set_parameter('media_renderer', 'version',
                                 brisa_media_renderer.version)


def main():
    setup_basic_configuration()
    config.manager.save()


if __name__ == "__main__":
    main()
