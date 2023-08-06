Running a server
================

Pydap comes with a lightweight and scalable OPeNDAP server, implemented as a `WSGI <http://wsgi.org/>`_ application. Being a WSGI `application <http://wsgi.org/wsgi/Applications>`_, Pydap can run on a variety of `servers <http://wsgi.org/wsgi/Servers>`_, including Apache, IIS or even as a standalone Python process. It can also be seamless combined with different `middleware <http://wsgi.org/wsgi/Middleware_and_Utilities>`_ for authentication/authorization, GZip compression, and much more.

In order to distribute your data first you need to install a proper `handler <handlers.html>`_, that will convert between the data format and the DAP data model. Currently, only the `NetCDF handler <handlers.html#netcdf>`_ has been ported to Pydap 3.0 from the old 2.x series, but there are handlers for relational databases, HFD5, Matlab, etc., that can be easily ported -- send an email to the `mailing list <http://groups.google.com/group/pydap/>`_ if you need a specific handler.

Running standalone
------------------

If you just want to quickly test the Pydap server, you can run it as a standalone Python application using the server that comes with `Python Paste <http://pythonpaste.org/>`_:

.. code-block:: bash

    $ paster create -t pydap myserver

To run the server just issue the command:

.. code-block:: bash

    $ paster serve ./myserver/server.ini

This will run the server on http://localhost:8001/, serving files from ``./myserver/data/``. By default the server will listen only to local requests, ie, from the same machine. You can change this by editing the ``server.ini`` file; and you can also change the port number, though for ports lower than 1024 you will probably need to run the script as root.

To change the default directory listing, the help page and the HTML form, simply edit the corresponding templates in ``./myserver/templates/``. The HTML form template is fairly complex, since it contain some application logic and some Javascript code, so be careful to not break anything.

Running Pydap with Apache
-------------------------

For a robust deployment you should run Pydap with Apache, using `mod_wsgi <http://modwsgi.org/>`_. After `installing mod_wsgi <http://code.google.com/p/modwsgi/wiki/InstallationInstructions>`_, create a Pydap sandbox in a directory *outside* your DocumentRoot, say ``/usr/local/pydap/``:

.. code-block:: bash

    $ paster create -t pydap /usr/local/pydap/

Now make sure that the Apache user has write permission to the directory ``/usr/local/pydap/python-eggs``, so it can unpack egg files without problems.

You can find more information on the `mod_wsgi configuration guide <http://code.google.com/p/modwsgi/wiki/QuickConfigurationGuide>`_.

