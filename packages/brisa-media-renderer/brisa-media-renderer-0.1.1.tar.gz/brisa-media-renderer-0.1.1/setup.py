# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2008 Brisa Team <brisa-develop@garage.maemo.org>

from distutils.core import setup


long_description = """
BRisa Media Renderer allows users to render media. It can render media from any
UPnP Media Server, including BRisa Media Server.
"""
version = '0.1.1'


def main():
    setup(
        name='brisa-media-renderer',
        version=version,
        description='BRisa Media Renderer',
        long_description=long_description,
        author='BRisa Team',
        author_email='brisa-develop@garage.maemo.org',
        url='https://garage.maemo.org/projects/brisa/',
        download_url='https://garage.maemo.org/projects/brisa/',
        license='MIT',
        maintainer='Andre Dieb Martins (dieb_)',
        maintainer_email='dieb@embedded.ufcg.edu.br',
        platforms='any',
        scripts=['bin/brisa-media-renderer'],
        keywords=['UPnP', 'Media Server', 'Multimedia', 'Rendering'],
        package_dir = {'brisa_media_renderer': 'src',
                       'brisa_media_renderer/services': 'src/services',
                       'brisa_media_renderer/services/avtransport':
                       'src/services/avtransport',
                       'brisa_media_renderer/services/gst_renderer':
                       'src/services/gst_renderer',
                       'brisa_media_renderer/services/render_control':
                       'src/services/render_control',
                       'brisa_media_renderer/xml_descriptions':
                       'src/xml_descriptions'},
        packages=['brisa_media_renderer',
                  'brisa_media_renderer/services',
                  'brisa_media_renderer/services/avtransport',
                  'brisa_media_renderer/services/gst_renderer',
                  'brisa_media_renderer/services/render_control',
                  'brisa_media_renderer/xml_descriptions'],
        package_data={'brisa_media_renderer/xml_descriptions': ['*.xml']},
        data_files=[('share/dbus-1/services',
                     ['src/br.edu.ufcg.embedded.brisa.MediaRenderer.service'])],
        classifiers=['Development Status :: 3 - Alpha',
                     'Environment :: Other Environment',
                     'Intended Audience :: Developers',
                     'Intended Audience :: End Users/Desktop',
                     'License :: OSI Approved :: MIT License',
                     'Natural Language :: English',
                     'Operating System :: POSIX :: Linux',
                     'Programming Language :: Python',
                     'Topic :: Multimedia'])

if __name__ == "__main__":
    main()
