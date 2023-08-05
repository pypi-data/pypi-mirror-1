#!/usr/bin/env python

"""$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/setup.py $
$Id: setup.py 27557 2005-10-13 14:49:08Z dbinger $

Setup script for Dulcinea
"""

from distutils import core
from distutils.extension import Extension
unused = Extension # for import checker.  Extension import is for side effect.
from quixote.ptl.qx_distutils import qx_build_py

kw = {'name': "Dulcinea",
      'version': "0.11",
      'description': ("A package of modules useful for developing "
                      "Quixote/Durus applications."),
      'author': "CNRI",
      'author_email': "quixote@mems-exchange.org",
      'url': "http://www.mems-exchange.org/software/dulcinea/",
      'license': "see LICENSE.txt",

      'package_dir': {'dulcinea':'lib'},
      'packages': ['dulcinea',
                   'dulcinea.ui',
                   'dulcinea.ui.lib',
                   'dulcinea.ui.form2',
                   'dulcinea.ui.user'],
      'scripts': ['bin/start-scgi.py',
                  'bin/opendb',
                  'bin/unused_imports.py',
                  'bin/codecheck',
                  'bin/check_durus.py',
                  'bin/site',
                  'bin/expire_session.py',
                  'bin/start-durus.py',
                  'bin/start-apache.py',
                  'bin/unknown.py'],
      'cmdclass': {'build_py': qx_build_py},
     }

# If we're running Python 2.3, add extra information
if hasattr(core, 'setup_keywords'):
    if 'classifiers' in core.setup_keywords:
        kw['classifiers'] = ['Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Operating System :: Unix',
          'Topic :: Software Development :: Libraries',
          ]
    if 'download_url' in core.setup_keywords:
        kw['download_url'] = ('http://www.mems-exchange.org/software/files'
                              '/dulcinea/Dulcinea-%s.tar.gz' % kw['version'])

core.setup(**kw)
