Handlers
========

Handlers are special Python modules that convert between a given data format and the data model used by Pydap (defined in the ``pydap.model`` module). They are necessary in order to Pydap be able to actually serve a dataset. There are handlers for NetCDF, HDF 4 & 5, Matlab, relational databases, Grib 1 & 2, CSV, Seabird CTD files, and a few more. Currently, only the NetCDF handler has been ported to the 3.0 branch of Pydap.

Installing data handlers
------------------------

NetCDF
~~~~~~

`NetCDF <http://www.unidata.ucar.edu/software/netcdf/>`_ is a format commonly used in oceanography, meteorology and climate science to store data in a machine-independent format. You can install the NetCDF handler using EasyInstall:

.. code-block:: bash

    $ easy_install pydap.handlers.netcdf

This will take care of the necessary dependencies. You don't even need to have to NetCDF libraries installed, since the handler will automatically install a pure Python NetCDF library called `pupynere <http://pypi.python.org/pypi/pupynere/>`_.

The NetCDF handler uses a buffered reader that access the data in contiguous blocks from disk, avoiding reading everything into memory at once. You can configure the size of the buffer by specifying a key in the ``server.ini`` file:

.. code-block:: ini

    [app:main]
    use = egg:pydap#server
    root = %(here)s/data
    templates = %(here)s/templates
    x-wsgiorg.throw_errors = 0
    pydap.handlers.netcdf.buf_size = 10000

In this example, the handler will read 10 thousand values at a time, converting the data and sending to the client before reading more blocks.

NCA
~~~

The ``pydap.handlers.nca`` is a simple handler for NetCDF aggregation (hence the name). The configuration is extremely simple. As an example, to aggregate model output in different files (say, ``output1.nc``, ``output2.nc``, etc.) along a new axis "ensemble" just create an INI file with the extension ``.nca``:

.. code-block:: ini

    ; output.nca
    [dataset]
    match = /path/to/output*.nc
    axis = ensemble
    ; below optional metadata:
    history = Test for NetCDF aggregator
    
    [ensemble]
    values = 1, 2, ...
    long_name = Ensemble members

This will assign the values 1, 2, and so on to each ensemble member. The new, aggregated dataset, will be accessed at the location of the INI file::

    http://server.example.com/output.nca

Another example: suppose we have monthly data in files ``data01.nc``, ``data02.nc``, ..., ``data12.nc``, and we want to aggregate along the time axis:

.. code-block:: ini

    [dataset]
    match = /path/to/data*.nc
    axis = TIME  # existing axis

The handler only works with NetCDF files for now, but in the future it should be changed to work with any other Pydap-supported data format. As all handlers, it can be installed using EasyInstall:

.. code-block:: bash

    $ easy_install pydap.handlers.nca

CDMS
~~~~

This is a handler that uses the ``cdms2.open`` function from `CDAT <http://www2-pcmdi.llnl.gov/cdat>`_/`CdatLite <http://proj.badc.rl.ac.uk/ndg/wiki/CdatLite>`_ to read files in any of the self-describing formats netCDF, HDF, GrADS/GRIB (GRIB with a GrADS control file), or PCMDI DRS. It can be installed using EasyInstall:

.. code-block:: bash

    $ easy_install pydap.handlers.cdms

The handler will automatically install CdatLite, which requires the NetCDF libraries to be installed on the system.

SQL
~~~


