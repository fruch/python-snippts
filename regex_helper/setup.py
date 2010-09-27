from distutils.core import setup
import py2exe

import sys; sys.argv.append('py2exe')

py2exe_options = dict(
                      ascii=False,  # Exclude encodings
                      excludes=['_ssl',  # Exclude _ssl
                                'pyreadline', 'difflib', 'doctest',
                                'optparse', 'pickle', 'calendar'],  # Exclude standard library
                      dll_excludes=['msvcr71.dll'],  # Exclude msvcr71
                      compressed=True,  # Compress library.zip
                      bundle_files=1
                      )

setup(name='<Name>',
      version='1.0',
      description='<Description>',
      author='Israel Fruchter',

      console=[{'script': "regex_helper.py"}],
      options={'py2exe': py2exe_options},
      zipfile = None,
      )

