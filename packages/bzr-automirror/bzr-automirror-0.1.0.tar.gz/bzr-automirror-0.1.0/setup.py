#!/usr/bin/env python
from distutils.core import setup


from info import (bzr_plugin_version,
                  bzr_minimum_version,
                  bzr_plugin_name,
                  __version__,
                 )

if __name__ == '__main__':
    setup(name="bzr-automirror",
          version=__version__,
          description="Automatically mirror Bazaar branches on every change.",
          author="Neil Martinsen-Burrell",
          author_email="nmb@wartburg.edu",
          url="https://launchpad.net/bzr-automirror",
          packages=['bzrlib.plugins.automirror',
                    'bzrlib.plugins.automirror.tests',
                    ],
          package_dir={'bzrlib.plugins.automirror': '.'},
          classifiers=['Development Status :: 4 - Beta',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: GNU General Public License (GPL)',
                       'Programming Language :: Python :: 2',
                       'Topic :: Software Development :: Version Control',
                      ]
          
         )
