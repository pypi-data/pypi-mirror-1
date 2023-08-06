import sys
from distutils.core import setup

trosnoth_version = '1.1.0'

def main():
    if 'py2exe' in sys.argv:
        import py2exe

        # Make sure py2exe knows which data files to include.
        import os
        paths = ['trosnoth/data/blocks',
                 'trosnoth/data/fonts',
                 'trosnoth/data/music',
                 'trosnoth/data/sprites',
                 'trosnoth/data/startupMenu',
                 'trosnoth/data/statGeneration'
                 ]

        data = []
        for path in paths:
            files = []
            for filename in os.listdir(path):
                if filename in ('__init__.py', '__init__.pyc'):
                    continue
                fn = os.path.join(path, filename)
                if os.path.isfile(fn):
                    files.append(fn)
            data.append((path, files))

        moreargs = {'console': ['scripts/trosnoth', 'scripts/trosnoth-editor',
                                    'scripts/trosnoth-discoverer'],
                    'data_files': data,
                   }
    else:
        moreargs = {}
        
    setup(name = 'trosnoth',
        version = trosnoth_version,
        description = 'Trosnoth network platform game',
        author = 'J.D. Bartlett et al',
        author_email = 'josh@trosnoth.org',
        url = 'http://www.trosnoth.org/',
        packages = ['trosnoth',
            'trosnoth.data',
            'trosnoth.data.blocks',
            'trosnoth.data.fonts',
            'trosnoth.data.music',
            'trosnoth.data.sound',
            'trosnoth.data.sprites',
            'trosnoth.data.startupMenu',
            'trosnoth.data.statGeneration',
            'trosnoth.src',
            'trosnoth.src.gui',
            'trosnoth.src.gui.fonts',
            'trosnoth.src.gui.framework',
            'trosnoth.src.gui.menu',
            'trosnoth.src.gui.screenManager',
            'trosnoth.src.gui.sound',
            'trosnoth.src.messages',
            'trosnoth.src.model',
            'trosnoth.src.network',
            'trosnoth.src.trosnothgui',
            'trosnoth.src.trosnothgui.ingame',
            'trosnoth.src.trosnothgui.pregame',
            'trosnoth.src.utils',
            'trosnoth.tools',
            'trosnoth.tools.map_editor',
            ],
        # Mapping says which files each package needs.
        package_data = {'trosnoth.data.blocks': ['*.block', '*.png', '*.bmp'],
                        'trosnoth.data.fonts': ['*.ttf', '*.TTF'],
                        'trosnoth.data.music': ['*.ogg'],
                        'trosnoth.data.sprites': ['*.png', '*.bmp'],
                        'trosnoth.data.startupMenu': ['*'],
                        'trosnoth.data.statGeneration': ['*.htm'],
                        'trosnoth': ['gpl.txt']
                        },
          
        scripts = ['scripts/trosnoth', 'scripts/trosnoth-editor',
                'scripts/trosnoth-discoverer'],
        long_description = 'Trosnoth is a very very addictive and fun network team game.' ,

        install_requires = [
            'pygame>=1.7',
            'twisted>=2.4'
        ],

        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: MacOS X',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications',
            'Framework :: Twisted',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.4',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Topic :: Games/Entertainment :: Arcade',
            'Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games',
        ],
        **moreargs
    ) 


if __name__ == '__main__':
    main()
