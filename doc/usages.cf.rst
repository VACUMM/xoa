.. _usages.cf:

Using the :mod:`xoa.cf` module
##############################

Introduction
============

This module is an application and extension of a subset of the
`CF conventions <http://cfconventions.org/>`_.
It has two intents:

* Searching :class:`xarray.DataArray` variables or coordinates with another
  :class:`xarray.DataArray` or a :class:`xarray.Dataset`,
  by scanning name and attributes like ``units`` and ``standard_name``.
* Formatting :class:`xarray.DataArray` variables or coordinates with
  unique ``name``, and ``standard_name``, ``long_name`` and ``units``
  attributes, with support of staggered grid location syntax.

Accessing the current specifications
====================================

Scanning and formatting actions are based on specifications,
and this module natively includes a
:ref:`default configuration <appendix.cf.default>`
for various oceanographic, sea surface and atmospheric variables and coordinates.
A distinction is made between
data variables (:ref:`data_vars <appendix.cf.data_vars>`)
and coordinates (:ref:`coords <appendix.cf.coords>`), like in :mod:`xarray`.

Getting the current specifications for data variables and coordinates
with the :func:`~xoa.cf.get_cf_specs` function:

.. ipython:: python

    from xoa import cf
    cfspecs = cf.get_cf_specs()
    cfspecs["data_vars"] is cfspecs.data_vars
    cfspecs["data_vars"] is cfspecs.coords
    cfspecs.data_vars.names[:3]
    cfspecs.coords.names[:3]

See the appendix :ref:`appendix.cf.default` for the
list of available default specifications.

Data variables
--------------

.. ipython:: python

    from pprint import pprint
    pprint(cfspecs.data_vars['sst'])


Description of specification keys:

.. list-table:: CF specs for :ref:`appendix.cf.data_vars`

    * - Key
      - Type
      - Description
    * - name
      - list(str)
      - Names
    * - ``standard_name``
      - list(str)
      - "standard_name" attributes
    * - ``long_name``
      - list(str)
      - "long_name" attributes
    * - ``units``
      - list(str)
      - "units" attributes
    * - ``domain``
      - choice
      - Domain of application, within {'generic', 'atmos', 'ocean', 'surface'}
    * - ``search_order``
      - str
      - Search order within properties as combination of letters: `[n]name`, `[s]tandard_name`, `[u]nits`
    * - ``cmap``
      - str
      - Colormap specification
    * - ``inherit``
      - str
      - Inherit specification from another data variable
    * - ``select``
      - eval
      - Item selection evaluated and applied to the array
    * - ``squeeze``
      - list(str)
      - List of dimensions that must be squeezed out

.. note:: The `standard_name`, `long_name` and `units` attributes are
    internally stored in as a dict in the `attrs` key.

Get name and attributes only:

.. ipython:: python

    print(cfspecs.data_vars.get_name("sst"))
    print(cfspecs.data_vars.get_attrs("sst"))


Coordinates
-----------

.. ipython:: python

    from pprint import pprint
    pprint(cfspecs.coords['lon'])

Description of specification keys:

.. list-table:: CF specs for :ref:`appendix.cf.coords`

    * - Key
      - Type
      - Description
    * - name
      - list(str)
      - Names
    * - ``standard_name``
      - list(str)
      - "standard_name" attributes
    * - ``long_name``
      - list(str)
      - "long_name" attributes
    * - ``units``
      - list(str)
      - "units" attributes
    * - ``axis``
      - str
      - "axis" attribute like X, Y, Z, T or F
    * - ``search_order``
      - str
      - Search order within properties as combination of letters: `[n]name`, `[s]tandard_name`, `[u]nits`
    * - ``inherit``
      - str
      - Inherit specification from another data variable

.. note:: The `standard_name`, `long_name`, `units` and `axis` attributes are
    internally stored in as a dict in the `attrs` key.

Get name and attributes only:

.. ipython:: python

    print(cfspecs.coords.get_name("lon"))
    print(cfspecs.coords.get_attrs("lon"))

Searching within a :class:`~xarray.Dataset` or  :class:`~xarray.DataArray`
==========================================================================

Let's define a minimal dataset:

.. ipython:: python

    @suppress
    import xarray as xr, numpy as np
    nx = 3
    lon = xr.DataArray(np.arange(3, dtype='d'), dims='mylon',
        attrs={'standard_name': 'longitude'})
    temp = xr.DataArray(np.arange(20, 23, dtype='d'), dims='mylon',
        coords={'mylon': lon},
        attrs={'standard_name': 'sea_water_temperature'})
    sal = xr.DataArray(np.arange(33, 36, dtype='d'), dims='mylon',
        coords={'mylon': lon},
        attrs={'standard_name': 'sea_water_salinity'})
    ds = xr.Dataset({'mytemp': temp, 'mysal': sal})

All these arrays are CF compliant according to their
``standard_name`` attribute, despite their name is not really explicit.

Check if they match known or explicit CF items:

.. ipython:: python

    cfspecs.coords.match(lon, "lon") # explicit
    cfspecs.coords.match(lon, "lat") # explicit
    cfspecs.coords.match(lon) # any known
    cfspecs.data_vars.match(temp) # any known
    cfspecs.data_vars.match(sal) # any known

Search for known CF items:

.. ipython:: python

    mytemp = cfspecs.search(ds, "temp")
    mylon = cfspecs.search(mytemp, "lon")

Datasets are searched for data variables ("data_vars") and
data variables are searched for coordinates ("coords").
You can also search for coordinates in datasets, for instance like this:

.. ipython:: python

    cfspecs.coords.search(ds, "lon")

.. seealso::
    - CF items:
      :cfcoord:`lon` :cfcoord:`lat` :cfdatavar:`temp` :cfdatavar:`sal`
    - Methods: :meth:`xoa.cf.CFCoordSpecs.match`
      :meth:`xoa.cf.CFVarSpecs.match` :meth:`xoa.cf.CFSpecs.search`
      :meth:`xoa.cf.CFCoordSpecs.search` :meth:`xoa.cf.CFVarSpecs.search`


Formatting
==========

It is possible to format, or even auto-format data variables and coordinates.

During an auto-formatting, each array is matched against CF specs,
and the array is formatting when a matching is successfull.
If the array contains coordinates, the same process is applied on them,
as soon as the ``format_coords`` keyword is ``True``.

**Explicit formatting:**

.. ipython:: python

    cfspecs.format_coord(lon, "lon")
    cfspecs.format_data_var(temp, "temp")

**Auto-formatting:**

.. ipython:: python

    ds2 = cfspecs.auto_format(ds)
    ds2.temp
    ds2.lon

.. seealso::
    :meth:`xoa.cf.CFSpecs.format_coord`
    :meth:`xoa.cf.CFSpecs.format_data_var`
    :meth:`xoa.cf.CFSpecs.auto_format`
    :meth:`xoa.cf.CFSpecs.auto_format`

Using the accessors
===================

Accessors for :class:`xarray.Dataset` and :class:`xarray.DataArray`
can be registered with the :func:`xoa.cf.register_cf_accessors`:

.. ipython:: python

    import xoa
    xoa.register_accessors(cf="cfd")

The accessor is named here `cfd` to no conflict with the
`cf` accessor of
`cf-xarray <https://cf-xarray.readthedocs.io/en/latest/>`_.


.. note:: All xoa accessors can be be registered with
    :func:`xoa.egister_accessors`. Note also that all functionalities
    of the `cf` accessor are also available with the more global
    `xoa` accessor.

These accessors make it easy to use some of the :class:`xoa.cf.CFSpecs`
capabilities.
Here are examples of use:

.. ipython:: python

    temp
    temp.cfd.get("lon") # access by .get
    ds.cfd.get("temp") # access by .get
    ds.cfd.lon # access by attribute
    ds.cfd.coords.lon  # specific search = ds.cf.coords.get("lon")
    ds.cfd.temp # access by attribute
    ds.cfd["temp"].name # access by item
    ds.cfd.data_vars.temp.name  # specific search = ds.cf.coords.get("temp")
    ds.cfd.data_vars.bathy is None # returns None when not found
    ds.cfd.temp.cfd.lon.name  # chaining
    ds.cfd.temp.cfd.name # CF name, not real name
    ds.cfd.temp.cfd.attrs # attributes, merged with CF attrs
    ds.cfd.temp.cfd.standard_name # single attribute
    ds.mytemp.cfd.auto_format() # or ds.temp.cfd()
    ds.cfd.auto_format() # or ds.cfd()

As you can see, accessing an accessor attribute or item make an
implicit call to :class:`~xoa.cf.DataArrayCFAccessor.get`.
The root accessor :attr:`cf` agive accessor to
two sub-accessors, :attr:`~xoa.cf.DatasetCFAccessor.data_vars`
and :attr:`~xoa.cf.DatasetCFAccessor.coords`,
for being able to specialize the searches.

.. seealso::
    :class:`xoa.cf.DataArrayCFAccessor`
    :class:`xoa.cf.DatasetCFAccessor`

Changing the CF specs
=====================

Default user file
-----------------

The :mod:`xoa.cf` module has internal defaults as shown
in appendix :ref:`appendix.cf.default`.

You can extend these defaults with a user file,
whose location is printable with the following command,
at the line containing "user CF specs file":

.. command-output:: xoa info paths

Update the current specs
------------------------

The current specs can be updated with different methods.

From a well **structured dictionary**:

.. ipython:: python

    cfspecs.load_cfg({"data_vars": {"banana": {"standard_name": "banana"}}})
    cfspecs.data_vars["banana"]

From a **configuration file**: instead of the dictionary as an argument
to :meth:`~xoa.cf.CfSpecs.load_cfg` method, you can give either a
file name or a **multi-line string** with the same content as
the file.
Following the previous example:

.. code-block:: ini

    [data_vars]
        [[banana]]
            standard_name: banana

If you only want to update a :attr:`~xoa.cf.CFSpecs.category`,
you can use such method (here :meth:`~xoa.cf.CFVarSpecs.set_specs`):

.. ipython:: python

    cfspecs.data_vars.set_specs("banana", name="bonono")
    cfspecs.data_vars["banana"]["name"]

Alternatively, a :class:`xoa.cf.CFSpecs` instance can be loaded
with the :meth:`~xoa.cf.CfSpecs.load_cfg` method, as explained below.

Create new specs from scratch
-----------------------------

To create new specs, you must instantiate the :class:`xoa.cf.CFSpecs` class,
with an input type as those presented above:

- A config file name.
- A Multi-line string in the format of a config file.
- A dictionary.
- A :class:`configobj.ConfigObj` instance.
- Another :class:`~xoa.cf.CFSpecs` instance.
- A list of them, with the having priority over the lasts.

The initialization also accepts two options:

- ``default``: wether to load or not the default internal config.
- ``user``: wether to load or not the user config file.

An config created **from default and user configs**:

.. ipython:: python

    banana_specs = {"data_vars": {"banana": {"attrs": {"standard_name": "banana"}}}}
    mycfspecs = cf.CFSpecs(banana_specs)
    mycfspecs["data_vars"]["sst"]["attrs"]["standard_name"]
    mycfspecs["data_vars"]["banana"]["attrs"]["standard_name"]

An config created **from scratch**:

.. ipython:: python

    mycfspecs = cf.CFSpecs(banana_specs, default=False, user=False)
    mycfspecs.pprint(depth=2)

An config created **from two other configs**:

.. ipython:: python

    cfspecs_banana = cf.CFSpecs(banana_specs, default=False, user=False)
    apple_specs = {"data_vars": {"apple": {"attrs": {"long_name": "Big apple"}}}}
    cfspecs_apple = cf.CFSpecs(apple_specs, default=False, user=False)
    cfspecs_fruits = cf.CFSpecs([cfspecs_apple, cfspecs_banana],
        default=False, user=False)
    cfspecs_fruits.data_vars.names

Replacing the currents CF specs
-------------------------------

As shown before, the currents CF specs are accessible with the
:func:`xoa.cf.get_cf_specs` function.
You can replace them with the :class:`xoa.cf.set_cf_specs` class,
to be used as a fonction.

.. ipython:: python

    cfspecs_old = cf.get_cf_specs()
    cf.set_cf_specs(cfspecs_banana)
    cf.get_cf_specs() is cfspecs_banana
    cf.set_cf_specs(cfspecs_old)
    cf.get_cf_specs() is cfspecs_old

In case of a temporary change, you can used :class:`~xoa.cf.set_cf_specs`
in a context statement:

.. ipython:: python

    with cf.set_cf_specs(cfspecs_banana) as myspecs:
        print('inside', cf.get_cf_specs() is cfspecs_banana)
        print('inside', myspecs is cf.get_cf_specs())
    print('outside', cf.get_cf_specs() is cfspecs_old)

Application with an accessor usage:

.. ipython:: python


    data = xr.DataArray([5], attrs={'standard_name': 'sea_surface_banana'})
    ds = xr.Dataset({'toto': data})
    mycfspecs = cf.CFSpecs({"data_vars": {"ssb":
        {"standard_name": "sea_surface_banana"}}})
    with cf.set_cf_specs(mycfspecs):
        print(ds.cfd.get("ssb"))


