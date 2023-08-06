# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2008 Brisa Team <brisa-develop@garage.maemo.org>

from distutils.core import setup


long_description = """
BRisa Media Tools is a package that contains tools for BRisa Media Server and
BRisa Media Renderer. For example, brisa-media-applet is a tool included
on the package and allows controlling BRisa Media Server and BRisa Media
Renderer devices from a graphical interface.
"""
version = '0.1.1'


def main():
    setup(
        name='brisa-media-tools',
        version=version,
        description='BRisa Media Tools',
        long_description=long_description,
        author='BRisa Team',
        author_email='brisa-develop@garage.maemo.org',
        url='https://garage.maemo.org/projects/brisa/',
        download_url='https://garage.maemo.org/projects/brisa/',
        license='MIT',
        maintainer='Andre Dieb Martins (dieb_)',
        maintainer_email='dieb@embedded.ufcg.edu.br',
        platforms='any',
        scripts=['bin/brisa-media-applet'],
        keywords=['UPnP', 'Media Server', 'Media Renderer', 'Multimedia',
                  'Control', 'Services', 'Tools'],
        package_dir={'brisa_media_tools': 'src',
                     'brisa_media_tools/applet':
                     'src/applet'},
        packages=['brisa_media_tools',
                  'brisa_media_tools/applet'],
        package_data={'brisa_media_tools/applet': ['*.glade', '*.png']},
        classifiers=['Development Status :: 3 - Alpha',
                     'Environment :: Other Environment',
                     'Intended Audience :: Developers',
                     'Intended Audience :: End Users/Desktop',
                     'License :: OSI Approved :: MIT License',
                     'Natural Language :: English',
                     'Operating System :: POSIX :: Linux',
                     'Programming Language :: Python',
                     'Topic :: Multimedia'],
        data_files=[('share/applications/hildon',
                    ['data/brisa_media_applet.desktop']),
                    ('share/icons/hicolor/16x16/hildon',
                    ['data/icons/16x16/brisa.png']),
                    ('share/icons/hicolor/26x26/hildon',
                    ['data/icons/26x26/brisa.png']),
                    ('share/icons/hicolor/32x32/hildon',
                    ['data/icons/32x32/brisa.png']),
                    ('share/icons/hicolor/40x40/hildon',
                    ['data/icons/40x40/brisa.png']),
                    ('share/icons/hicolor/scalable/hildon',
                    ['data/icons/40x40/brisa.png']),
                    ('share/pixmaps',
                    ['data/icons/40x40/brisa.png'])])


if __name__ == "__main__":
    main()
