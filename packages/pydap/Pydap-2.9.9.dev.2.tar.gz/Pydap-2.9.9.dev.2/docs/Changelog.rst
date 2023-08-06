Changelog
=========

3.0
---

To be released.

* Renamed package name from ``dap`` to ``Pydap``.

* Renamed module name from ``dap`` to ``pydap``.
* Rewrote data model, and renamed it from ``dap.dtypes`` to
  ``pydap.model``.

* Sequences can be filtered using a pseudo-array syntax.

* Grids are now a sublass of structures.

* Grids can be sliced using boolean arrays.

* Unified the syntax used for filtering local and remote sequences.

* Client is now able to open remote URLs with constraint expressions in
  them, honoring slices.

* Opendap types (``Float32``, ``Int32``, etc.) are now classes instead of
  strings.

* Using Sphinx and Paver for documentation, website and maintenance.

2.2.6.6
-------

Released 2008-09-12 21:41

* Error response now is always verbose, showing the full traceback,
  even for know exceptions.

2.2.6.5
-------

Released 2008-09-05 15:56

* Added a better error handler, with more information.

* Fixed problem when building URLs in Windows, was using ``\`` instead of
  ``/``.

2.2.6.4
-------

Released 2008-04-30 10:32

* Fixed bug in that caused the HTML response to fail with recent versions
  of Paste. The ``httpexceptions`` WSGI middleware is no longer required.

2.2.6.3
-------

Released 2008-01-04 19:21

* Fixed bug in WSGI application, closing the handler properly.

2.2.6.2
-------

Released 2007-12-10 17:32

* Fixed bug in the DAS parser, found by Charles Carleton, with an overflow
  on ``Int32`` bigger than Python's integers. The cast to long inside the
  ``array.array`` object would cause the overflow.

2.2.6.1
-------

Released 2007-11-05 13:25

* Added timeout option to the client.

* Removed implicit genexp in client to make code compatible with
  Python 2.3.

2.2.6
-----

Released 2007-09-13 23:13

* Fixed concurrency issues on the server.

2.2.5.10
--------

Released 2007-07-19 09:00

* Fixed a small bug in the client where the cache information was
  not being used to retrieve the DAS and the DDS (only the DODS
  response) -- thanks to Darren Hardy <dhardy@bren.ucsb.edu>.

* Brian Granger made the ``ArrayType`` object more compatible with
  numpy arrays.

2.2.5.9
-------

Released 2007-04-10 17:43

* Added proper support in the client for the "Alias" attribute type.

2.2.5.8
-------

Released 2007-02-16 16:03

* Fixed bug in the evaluation of values from DAS. Bytes are decoded
  assuming unsigned values (0:255) instead of signed (-128:127).

2.2.5.7
-------

Released 2006-12-12 15:20

* Values from the DAS are now evaluated using the right precision. This
  means ``missing_values`` defined as ``Float32``, eg, will have the same
  representation as the data.

2.2.5.6
-------

Released 2006-12-11 17:56

* Moved DAP proxy to the main tree (``dap.wsgi.proxy``).

* When opening local files, client tries to unwrap arrayterators.

2.2.5.5
-------

Released 2006-11-28 13:27

* Fixed bug in client when requesting data with step > 1.

* DAS parser now returns single attributes as simple values,
  instead of a list of only one element.

* DAS parser add attributes to maps from a variable of the same
  name from the root dataset. Eg, a grid with a map ``latitude``
  will have its attributes copied from a variable ``latitude``
  in the main dataset, if it exists and it the map has no attributes.

2.2.5.4
-------

Released 2006-11-25 20:53

* Fixed bug when generating the DAS response from attributes
  contained in 0D numpy arrays.

* Additional parameters in the Paste Deploy configuration file
  are now being passed to the ``environ`` dict.

* WSGI app now honors ``x-wsgiorg.throw_errors`` specification from
  http://wsgi.org/wsgi/Specifications/throw_errors.

2.2.5.3
-------

Released 2006-11-22 17:21

* Fixed bug where the requested variables were being passed unquoted
  in the response from ``dap.helper.parse_querystring``.

2.2.5.2
-------

Released 2006-11-22 11:58

* Fixed another small bug in ``xdr.py`` when encoding numpy arrays
  of strings.

2.2.5.1
-------

Released 2006-11-15 09:48

* Fixed a small bug in the XDR encoding that only appeared in the
  SCGI server, thanks to Dallas Masters.

2.2.5
-----

Released 2006-11-14 09:12

* Fixed directory listing in ``DapServerApplication``: output was
  being returned as a string instead of a list, making the WSGI server
  iterate over each character.

* Changed server (``dap.wsgi.application.SimpleApplication``) to
  ignore exceptions derived from ``paste.httpexceptions.HTTPException``.
  This allows the HTML response to raise a ``HTTPSeeOther`` exception,
  redirecting the user to the corresponding ASCII response after a
  POST.

* Made server **much** faster by using numpy's ``array.astype`` instead
  of Python's native ``array.array``. This makes it at least 10x faster
  for big datasets.

2.2.4
-----

Released 2006-11-06 14:27

* Changes mostly related to plugin development: added a namespace
  for the packages; made ``parse_querystring()`` return Python slices
  instead of strings.

* Changed the DAS response to work with GrADS by ommiting attributes
  from array and maps in grids.

* Fixed ``USER_AGENT`` that was not being passed to httplib2.

2.2.3
-----

Released 2006-10-23 08:36

* Moved server template to ``dap/wsgi/``.

* Created template for writing new plugins in ``dap/plugins/``.

2.2.2
-----

Released 2006-10-13 13:43

* Empty directories from paster template where not being included.
  Added stub files in ``MANIFEST.in`` to include them.

2.2.1
-----

Released 2006-10-11 15:42

* Fixed small bug when deepcopying dtypes (data attribute was not
  begin copied).

* Added a generic error catcher when the server fails, returning a
  DAP-formatted error message.

2.2.0
-----

Released 2006-10-17 19:01

* Moved client to use httplib2, giving us cache and authentication
  for free.

* Sequences are now iterable (this should've always been the case).

* Sequence filtering is now much more pythonic: sequences can be
  filtered using generator expressions or list comprehensions.

* Removed old logger because it was too slow.

* Rewrote ``dtypes.py`` for consistency.

* Moved ``trim()`` function to a ``constrain()`` function that
  builds the dataset instead of trimming it down.

* Module now uses Numpy exclusively.

* Moved plugins (netCDF, Matlab, SQL, compress) out of module.

* Responses (DDS, DAS, DODS, ASCII, HTML, JSON, etc.) are now
  pluggable, like plugins (handlers).

* Cleaned up the netCDF plugin *a lot*.

* Major improvements to the SQL plugin.

* Server should use ``environ['wsgi.errors']`` for logging.

* Server uses Cheetah template for directory listing; templates can
  be overwritten to customize the server.

* Created a server template based on Paste Script.

2.1.6
-----

Released 2006-07-20 11:02

* Removed fpconst dependency.

2.1.5
-----

Released 2006-05-19 14:44

* Added patch from Rob Cermak to support Alias tag.

* Added patch from Peter Desnoyers making server compatible with
  ncks.

* Added patch from Peter Desnoyers to run ``dap-server.py`` in foreground.

* Added a "host" option to ``dap-server.py``.

* Fixed ordering of Grid maps in the DDS to match the dimensions.
  This is necessary for compatibility with Ferret.

* Fixed bug when unpacking arrays of bytes (thanks to David Poulter).

* Fixed bug with Grids inside constructors (thanks to Nelson
  Castillo).

2.1.4
-----

Released 2006-02-22 15:34

* Fixed bug in ``xdr.py`` (thanks to Gerald Manipon).

2.1.3
-----

Released 2006-02-08 19:52

* Allow multiple filters when filtering sequences.

2.1.2
-----

Released 2006-02-08 14:02

* Fixed bug when ``PATH_INFO`` is empty.

2.1.1
-----

Released 2006-01-31 11:10

* Fixed netCDF shape (thanks to Bob Drach).

* Fixed bug in THREDDS catalog generator.

2.1.0
-----

Released 2006-01-26 13:28

* New release.
