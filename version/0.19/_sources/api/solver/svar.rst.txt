.. _ref_svar_data:

SVAR data
=========

An SVAR is an array variable that holds the data for a particular
solved field (such as pressure or velocity). You can use svar_info
and svar_data objects to access Fluent SVAR info and data respectively.

Accessing SVAR objects
----------------------

Launch the fluent solver, and make SVAR objects available 
(for example, by reading case and data files):

.. code-block:: python

  >>> import ansys.fluent.core as pyfluent
  >>> from ansys.fluent.core import examples
  >>> import_filename = examples.download_file("mixing_elbow.msh.h5", "pyfluent/mixing_elbow")
  >>> solver = pyfluent.launch_fluent(mode="solver")
  >>> solver.file.read(file_type="case", file_name=import_filename)


The svar_info and svar_data objects are attributes of the solver object:

.. code-block:: python

  >>> svar_info = solver.svar_info
  >>> svar_data = solver.svar_data


SVAR info
---------
SVAR metadata information can be accessed via the following svar_info methods:

- ``get_zones_info`` for zone information.
- ``get_svars_info`` for SVAR information.

Get zone information
~~~~~~~~~~~~~~~~~~~~
You can access zone information by calling the ``get_zones_info`` method.

.. code-block:: python
  
  >>> zones_info = svar_info.get_zones_info()
  >>> zones_info.domains
  ['mixture']  
  >>>
  >>> zones_info.zones
  ['fluid', 'wall', 'symmetry', 'pressure-outlet-7', 'velocity-inlet-6', 'velocity-inlet-5', 'default-interior']
  >>>
  >>> zone_info = zones_info['wall']
  >>>
  >>> zone_info
  name:wall count: 3630 zone_id:3 zone_type:wall thread_type:Face
  >>>
  >>> zone_info.name 
  'wall'   
  >>>
  >>> zone_info.count 
  3630 
  >>>
  >>> zone_info.zone_id 
  3
  >>>
  >>> zone_info.zone_type 
  'wall'  
  
Get SVAR information
~~~~~~~~~~~~~~~~~~~~
You can request SVARs information for a given ``domain_name`` and list of ``zone_names``
by calling the ``get_svars_info`` method.

.. code-block:: python

  >>> svars_info_wall_fluid = svar_info.get_svars_info(zone_names=['wall' , "fluid"], domain_name="mixture")
  >>>
  >>> svars_info_wall_fluid.svars
  ['SV_CENTROID', 'SV_D', 'SV_H', 'SV_K', 'SV_P', 'SV_T', 'SV_U', 'SV_V', 'SV_W']
  >>>
  >>> svar_info_centroid = svars_info_wall_fluid['SV_CENTROID']
  >>>
  >>> svar_info_centroid
  name:SV_CENTROID dimension:3 field_type:<class 'numpy.float64'>
  >>>
  >>>svar_info_centroid.name 
  'SV_CENTROID'
  >>>
  >>>svar_info_centroid.dimension 
  >>>3
  >>>
  >>>svar_info_centroid.field_type 
  <class 'numpy.float64'> 
  
SVAR data
---------
SVAR data can be extracted and modified via the following svar_data object methods:

- ``get_svar_data`` to get SVAR data.
- ``set_svar_data`` to set SVAR data.


Get SVAR data
~~~~~~~~~~~~~
You can request SVAR data for a given ``domain_name`` and multiple ``zone_names`` by calling
the ``get_svar_data`` method and passing the particular ``svar_name``.

.. code-block:: python
  
    >>> sv_t_wall_fluid= svar_data.get_svar_data(svar_name="SV_T", zone_names=["fluid", "wall"], domain_name="mixture")
    >>>
    >>> sv_t_wall_fluid.domain
    'mixture'
    >>>
    >>> sv_t_wall_fluid.zones
    ['fluid', 'wall']
    >>>
    >>> fluid_temp = sv_t_wall_fluid['fluid']
    >>>
    >>> fluid_temp.size
    13852
    >>>
    >>> fluid_temp.dtype
    'float64'
    >>>
    >>> fluid_temp
    array([600., 600., 600., ..., 600., 600., 600.])
  
Set SVAR data
~~~~~~~~~~~~~
You can set SVAR data for a given ``domain_name`` by calling the ``set_svar_data``
method and passing required ``svar_name`` and dictionary of ``zone_name`` 
to numpy array of ``svar_data``

Additionally svar_data object also supports ``get_array`` method. This method can be used to 
generate ``numpy zeros array`` for a given ``domain_name``, ``zone_name`` and 
``svar_name``. This array can be populated and passed to ``set_svar_data``.

.. code-block:: python
  
    >>> wall_temp_array = svar_data.get_array("SV_T", "wall", "mixture")
    >>> fluid_temp_array = svar_data.get_array("SV_T", "fluid", "mixture")
    >>> wall_temp_array[:] = 500
    >>> fluid_temp_array[:] = 600
    >>> zone_names_to_svar_data = {'wall':wall_temp_array, 'fluid':fluid_temp_array}
    >>> svar_data.set_svar_data(svar_name="SV_T", zone_names_to_svar_data=zone_names_to_svar_data, domain_name="mixture")

.. currentmodule:: ansys.fluent.core.services

.. autosummary::
    :toctree: _autosummary
    :template: flobject-class-template.rst
    :recursive:

    svar.SVARInfo
    svar.SVARData
   