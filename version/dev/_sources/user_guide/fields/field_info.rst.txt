.. _ref_field_info_guide:

.. vale Google.Spacing = NO

Field info
==========

You can use field info objects to access Fluent field information.

Accessing field info objects
----------------------------

.. code:: python

  >>> import ansys.fluent.core as pyfluent
  >>> solver = pyfluent.launch_fluent(mode=pyfluent.FluentMode.SOLVER)
  >>> solver.settings.file.read(file_type="case-dats", file_name=mixing_elbow_case_path)
  >>> solver.settings.solution.initialization.hybrid_initialize()


The field info object is an attribute of the :obj:`~ansys.fluent.core.session_solver.Solver` object:

.. code-block:: python

  >>> field_info = solver.fields.field_info

Sample requests
---------------

Here are the methods for requesting field information:

- ``get_scalar_fields_info`` for getting fields information.
- ``get_range`` for getting the range of the field.
- ``get_vector_fields_info`` for getting vector fields information.
- ``get_surfaces_info`` for getting the surfaces information.

Get scalar fields info
~~~~~~~~~~~~~~~~~~~~~~
You can request the fields information (field name, domain, and section) by
calling the ``get_scalar_fields_info`` method.

.. code-block:: python

  >>> field_info.get_scalar_fields_info()
  {'pressure': {'display_name': 'Static Pressure', 'section': 'Pressure...', 'domain': 'mixture'},
   'pressure-coefficient': {'display_name': 'Pressure Coefficient', 'section': 'Pressure...', 'domain': 'mixture'},
   'dynamic-pressure': {'display_name': 'Dynamic Pressure', 'section': 'Pressure...', 'domain': 'mixture'},
   'absolute-pressure': {'display_name': 'Absolute Pressure', 'section': 'Pressure...', 'domain': 'mixture'},
    ...}

Get range
~~~~~~~~~
You can request the range (minimum and maximum values) for a given ``field`` by
calling the ``get_range`` method. It takes a ``field`` argument which can be obtained
from the keys of the dictionary returned by ``get_scalar_fields_info`` method.

.. code-block:: python

  >>> field_info.get_range("velocity")
  [0.0, 0.0]
  >>> field_info.get_range("cell-weight")
  [8.0, 24.0]

Get vector fields info
~~~~~~~~~~~~~~~~~~~~~~
You can request the vector fields information by calling the
``get_vector_fields_info`` method.

.. code-block:: python

  >>> field_info.get_vector_fields_info()
  {'velocity': {'x-component': 'x-velocity', 'y-component': 'y-velocity', 'z-component': 'z-velocity'},
   'relative-velocity': {'x-component': 'relative-x-velocity', 'y-component': 'relative-y-velocity', 'z-component': 'relative-z-velocity'}}

Get surfaces info
~~~~~~~~~~~~~~~~~
You can request the surfaces information (surface name, ID, and type) by
calling the ``get_surfaces_info`` method.

.. code-block:: python

  >>> field_info.get_surfaces_info()
  {'symmetry-xyplane': {'surface_id': [5], 'zone_id': 29, 'zone_type': 'symmetry', 'type': 'zone-surf'},
   'hot-inlet': {'surface_id': [4], 'zone_id': 30, 'zone_type': 'velocity-inlet', 'type': 'zone-surf'},
   'cold-inlet': {'surface_id': [3], 'zone_id': 31, 'zone_type': 'velocity-inlet', 'type': 'zone-surf'},
   'outlet': {'surface_id': [2], 'zone_id': 32, 'zone_type': 'pressure-outlet', 'type': 'zone-surf'},
   'wall-inlet': {'surface_id': [1], 'zone_id': 33, 'zone_type': 'wall', 'type': 'zone-surf'},
   'wall-elbow': {'surface_id': [0], 'zone_id': 34, 'zone_type': 'wall', 'type': 'zone-surf'}}


