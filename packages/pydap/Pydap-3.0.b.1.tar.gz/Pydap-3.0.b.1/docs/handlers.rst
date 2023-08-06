Handlers
========

Handlers are special Python modules that convert between a given data format and the data model used by Pydap (defined in the ``pydap.model`` module). There are handlers for NetCDF, HDF 4 & 5, Matlab, relational databases, Grib 1 & 2, CSV, Seabird CTD files, and a few more. Currently, only the NetCDF handler has been ported to the 3.0 branch of Pydap.

Installing data handlers
------------------------

NetCDF
~~~~~~

You can install the NetCDF handler using EasyInstall:

.. code-block:: bash

    $ easy_install pydap.handlers.netcdf

This will take care of the necessary dependencies. You don't even need to have to NetCDF libraries installed, since the handler will automatically install a pure Python NetCDF library called `pupynere <http://pypi.python.org/pypi/pupynere/>`_.
