===============
 webprocessingserver 
===============

---------------------------------------
Simple Python geographic feature server
---------------------------------------

:Author: crschmidt@metacarta.com
:Copyright: (c) 2007 Christohper Schmidt. All Rights Reserved.
:Version: 1.0 
:Manual group: GIS Utilities

DESCRIPTION
===========
WebProcessingServer is a simple Python-based geographic feature server. It
allows you to transform geographic vector features via a number of different
processing backends.

WebProcessingServer will run under Python CGI, mod_python, or as a standalone
server. 

WebProcessingServer is released under a license similar to the BSD license.

RUNNING UNDER CGI
=================

* Extract the code to some web directory (e.g. in /var/www).
* Permit CGI execution in the WebProcessingServer directory.
  For example, if WebProcessingServer is to be run with Apache, the
  following must be added in your Apache configuration,   
  where /var/www/webprocessingserver is the directory resulting from
  the code extraction. 
  
  ::

    <Directory /var/www/webprocessingserver>
         AddHandler cgi-script .cgi
         Options +ExecCGI
    </Directory>

Python Prerequisites
--------------------
In order to use WebProcessingServer, you must have the simplejson module
installed. If you do not, you can add it by doing the following:

  $ wget http://cheeseshop.python.org/packages/source/s/simplejson/simplejson-1.7.1.tar.gz
  $ tar -zvxf simplejson-1.7.1.tar.gz
  $ cp -r simplejson-1.7.1/simplejson /var/www/webprocessingserver

Note that these instructions are for Linux systems: the end goal is to extract
the simplejson directory from the distribution and put it in the root of your
WebProcessingServer install.

Non-standard Python Location
----------------------------
If your Python is not at /usr/bin/python on your system, you will need to
change the first line of wps.cgi to reference the location of
your Python binary. A common example is:

  ::

     #!/usr/local/bin/python

Under Apache, you might see an error message like:

  ::

    [Wed Mar 14 19:55:30 2007] [error] [client 127.0.0.1] (2)No such file or 
      directory: exec of '/www/wps.cgi' failed

to indicate this problem.

You can typically locate where Python is installed on your system via the
command 'which python'.

Windows users: If you are using Windows, you should change the first line 
of wps.cgi to read:

  ::

    #!C:/Python/python.exe -u

C:/Python should match the location Python is installed under on your 
system. In Python 2.5, this location is C:/Python25 by default.  

RUNNING UNDER MOD_PYTHON
========================

* Extract the code to some web directory (e.g. /var/www).
* Add the following to your Apache configuration, under a <Directory> heading:
  
  ::
  
      AddHandler python-program .py
      PythonPath sys.path+['/path/to/webprocessingserver']
      PythonHandler WebProcessingServer.Server
      PythonOption WebProcessingServerConfig /path/to/webprocessingserver.cfg
  
* An example might look like:

  ::
  
    <Directory /var/www/webprocessingserver/>
       AddHandler python-program .py
       PythonPath sys.path+['/var/www/webprocessingserver']
       PythonHandler WebProcessingServer.Server 
       PythonOption WebProcessingServerConfig
                    /var/www/webprocessingserver/webprocessingserver.cfg
    </Directory>
  
* In this example, /var/www/webprocessingserver is the directory resulting from
  the code extraction. 
* Visit the URL described above, replacing wps.cgi with 
  webprocessingserver.py
* If you see an empty GeoRSS file you have set up your configuration correctly.
  Congrats!
* Note that mod_python has not yet been well tested, and may not work well
  for all data sources.

 
RUNNING STANDALONE (UNDER WSGI)
===============================

WebProcessingServer comes with a standalone HTTP server which uses the WSGI
handler.  This implementation depends on *Python Paste*, which can be
downloaded from:
  
  http://cheeseshop.python.org/pypi/Paste

For versions of Python earlier than 2.5, you will also need to install 
wsgiref:

  http://cheeseshop.python.org/pypi/wsgiref

Once you have all the prerequisites installed, simply run:

  ::
  
    python wps_http_server.py

This will start a webserver listening on port 8080.


RUNNING UNDER FASTCGI
=====================

WebProcessingServer comes with a fastcgi implementation. In order to use this 
implementation, you will need to install flup, available from:
  
  http://trac.saddi.com/flup

This implementation also depends on Python Paste, which can be downloaded 
from:
  
  http://cheeseshop.python.org/pypi/Paste

Once you have done this, you can configure your fastcgi server to use
webprocessingserver.fcgi.

Configuring FastCGI is beyond the scope of this documentation.

CONFIGURATION
=============
WebProcessingServer is configured by a config file, defaulting to
webprocessingserver.cfg. 

SEE ALSO
========

http://code.google.com/p/webprocessingserver/

