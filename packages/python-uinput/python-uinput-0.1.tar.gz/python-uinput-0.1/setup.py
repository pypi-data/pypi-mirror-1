# -*- coding: utf-8 -*-

import sys
reload(sys).setdefaultencoding('utf-8')

import os
from distutils.core import setup, Extension

pysuinput_module = Extension('uinput._suinput',
                             sources=['src/pysuinput.c'],
                             libraries=['suinput'],
                             )

codes_module = Extension('uinput.codes',
                         sources=['src/codes.c'])

setup(name='python-uinput',
      version='0.1',
      description='Simple Python API to the Linux uinput-system.',
      author='Tuomas Räsänen',
      author_email='tuos@codegrove.org',
      url='http://codegrove.org/python-uinput/',
      download_url='http://codegrove.org/python-uinput/python-uinput-0.1.tar.gz',
      package_dir={'uinput': 'src'},
      packages=['uinput'],
      ext_modules=[pysuinput_module, codes_module],
      license='LGPLv3+',
      platforms=['Linux'],
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Operating System Kernels :: Linux",
        ],
      long_description="""
A high-level API to programmatically generate Linux input events.
""",
      )
