#!/usr/bin/env python

# Setup script for the pxc200 module

from distutils import core

PXC_SRC = "/projects/mems/ext_source/linux/pxc-0.81"

kw = {'name':"pxc200",
      'description':"""Adds support for the Imagenation PXC-200 frame grabber
to the Python Imaging Library""",
      'version': "1.0",
      'author': "MEMS Exchange",
      'author_email': "mems-dev@mems-exchange.org",
      'url': "http://www.mems-exchange.org/software/pxc200/",

      'ext_modules': [core.Extension('pxc200',
                                      sources=["pxc200module.c"],
                                      include_dirs = [PXC_SRC]),
                      ]
      }

# If we're running Python 2.3, add extra information
if hasattr(core, 'setup_keywords'):
    if 'classifiers' in core.setup_keywords:
        kw['classifiers'] = ['Development Status :: 5 - Production/Stable',
            'License :: OSI Approved :: Python License (CNRI Python License)',
            'Operating System :: POSIX :: Linux',
            'Topic :: Multimedia :: Graphics :: Capture'
           ]
    if 'download_url' in core.setup_keywords:
        kw['download_url'] = ('http://www.mems-exchange.org/software/files'
                              '/pxc200/pxc200-%s.tar.gz' % kw['version'])

core.setup(**kw)





