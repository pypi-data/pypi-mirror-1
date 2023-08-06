# -*- coding: utf-8 -*-

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, Extension


c_ext = Extension('_superfcgi', ['superfcgi/_superfcgi.c'], libraries=['fcgi'],
                  include_dirs=['/usr/local/include', '/usr/include'],
                  library_dirs=['/usr/local/lib', '/usr/lib'])

setup(name='superfcgi',
      version='0.1.3',
      description='The only one true way to run WSGI apps through fastcgi',
      long_description='The only one true way to run WSGI apps through fastcgi',
      author='Victor Kotseruba',
      author_email='barbuzaster@gmail.com',
      license='MIT',
      platforms=['Posix', 'MacOS X', 'Windows'],
      classifiers=['Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Programming Language :: C',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
                   'Topic :: Software Development :: Libraries :: Python Modules'],
      packages=['superfcgi','superfcgi.management','superfcgi.management.commands'],
      entry_points = {
        'console_scripts': [
            'superfcgi = superfcgi.superfcgi:run',
            ]
        },
      ext_package='superfcgi',
      ext_modules=[c_ext],
      zip_safe=False,
     ) 
