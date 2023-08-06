# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2008 Brisa Team <brisa-develop@garage.maemo.org>

import shutil

from distutils.core import setup


long_description = """
BRisa Media Server allows users to share media. It has support for plugins,
which can share media from a range of different sources. For example, a
youtube plugin can share favorite videos, and so on.
"""
version = '0.1.1'


def main():
    setup(
        name='brisa-media-server',
        version=version,
        description='BRisa Media Server',
        long_description=long_description,
        author='BRisa Team',
        author_email='brisa-develop@garage.maemo.org',
        url='https://garage.maemo.org/projects/brisa/',
        download_url='https://garage.maemo.org/projects/brisa/',
        license='MIT',
        maintainer='Andre Dieb Martins (dieb_)',
        maintainer_email='dieb@embedded.ufcg.edu.br',
        platforms='any',
        scripts=['bin/brisa-media-server', 'bin/brisa-media-server-conf',
                 'bin/brisa-media-server-assistant'],
        keywords=['UPnP', 'Media Server', 'Multimedia', 'Sharing'],
        package_dir = {'brisa_media_server': 'src',
                       'brisa_media_server/services': 'src/services',
                       'brisa_media_server/services/media_registrar_ms':
                       'src/services/media_registrar_ms',
                       'brisa_media_server/plugins': 'src/plugins',
                       'brisa_media_server/plugins/media_library':
                       'src/plugins/media_library',
                       'brisa_media_server/conf': 'src/conf',
                       'brisa_media_server/conf/gui': 'src/conf/gui',
                       'brisa_media_server/conf/gui/gtk': 'src/conf/gui/gtk',
                       'brisa_media_server/assistant': 'src/assistant',
                       'brisa_media_server/xml_descriptions':
                       'src/xml_descriptions'},
        packages=['brisa_media_server',
                  'brisa_media_server/services',
                  'brisa_media_server/services/media_registrar_ms',
                  'brisa_media_server/plugins',
                  'brisa_media_server/plugins/media_library',
                  'brisa_media_server/conf',
                  'brisa_media_server/conf/gui',
                  'brisa_media_server/conf/gui/gtk',
                  'brisa_media_server/assistant',
                  'brisa_media_server/xml_descriptions'],
        package_data={'brisa_media_server/conf/gui/gtk': ['*.png', '*.glade'],
                      'brisa_media_server/assistant': ['*.glade'],
                      'brisa_media_server/xml_descriptions': ['*.xml']},
        classifiers=['Development Status :: 3 - Alpha',
                     'Environment :: Other Environment',
                     'Intended Audience :: Developers',
                     'Intended Audience :: End Users/Desktop',
                     'License :: OSI Approved :: MIT License',
                     'Natural Language :: English',
                     'Operating System :: POSIX :: Linux',
                     'Programming Language :: Python',
                     'Topic :: Multimedia'],
        data_files=[('share/dbus-1/services',
                    ['src/br.edu.ufcg.embedded.brisa.MediaServer.service']),
                    ('share/applications/hildon',
                    ['data/brisa_media_server_conf.desktop'])])

if __name__ == "__main__":
    main()
