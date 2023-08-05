#!/usr/bin/env python

import sys

try:
    from setuptools import setup
except:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

readme = file('doc/Readme.txt','rb').read()

classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
]

# We'd like to let debian install the /etc/tilecache.cfg,
# but put them in tilecache/tilecache.cfg using setuptools
# otherwise. 
extra = { }
if "--debian" in sys.argv:
   extra['data_files']=[('/etc', ['webprocessingserver.cfg'])]
   sys.argv.remove("--debian")
else:
   extra['data_files']=[('WebProcessingServer', ['webprocessingserver.cfg'])]
    
setup(name='WPServer',
      version='1.0',
      description='a web mapping transformation library',
      author='Christohper Schmidt',
      author_email='crschmidt@crschmidt.net',
      url='http://code.google.com/p/webprocessingserver/',
      long_description=readme,
      packages=['WebProcessingServer', 'WebProcessingServer.Action', 'WebProcessingServer.Service', 'vectorformats', 'vectorformats.Formats'],
      scripts=['wps.cgi', 'wps.fcgi','wps_install_config.py', 
               'wps_http_server.py'],
      zip_safe=False,
      license="Clear BSD",
      classifiers=classifiers, 
      **extra 
     )
