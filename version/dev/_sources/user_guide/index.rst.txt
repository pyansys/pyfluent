.. _ref_user_guide:

==========
User guide
==========

.. toctree::
   :maxdepth: 1
   :hidden:

   session/index
   solver_settings/index
   meshing/index
   fields/index
   events
   monitors
   transfer_data
   units
   file_transfer
   offline/index
   journal
   log
   usability
   make_container_image
   legacy/index


Welcome to the PyFluent user guide. This guide helps you understand how to use PyFluent to
leverage the power of Ansys Fluent for your CFD simulations.


A simple example
----------------

.. code:: python

  >>> import ansys.fluent.core as pyfluent
  >>> meshing = pyfluent.launch_fluent(mode=pyfluent.FluentMode.MESHING, product_version=pyfluent.FluentVersion.v251)
  >>> watertight = meshing.watertight()
  >>> watertight.import_geometry.file_name = pyfluent.examples.download_file("mixing_elbow.pmdb","pyfluent/mixing_elbow")
  >>> watertight.import_geometry()
  >>> watertight.create_volume_mesh()
  >>> meshing.switch_to_solver()
  >>> setup, solution = solver.settings.setup, solver.settings.solution
  >>> setup.boundary_conditions.set_zone_type(zone_list=["cold-inlet", "hot-inlet"], new_type="velocity-inlet")
  >>> setup.boundary_conditions.set_zone_type(zone_list=["outlet"], new_type="pressure-outlet")
  >>> setup.cell_zone_conditions.set_zone_type(zone_list="elbow-fluid", new_type="fluid")
  >>> solution.initialization.hybrid_initialize()
  >>> solution.run_calculation.iterate(iter_count=100)
  >>> velocity_data = solver.fields.field_data.get_vector_field_data(field_name="velocity", surfaces=["cold-inlet"])


Key features
------------

Launching Fluent from PyFluent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:ref:`Start a Fluent session <ref_launch_guide>` locally or remotely with a variety of launch options, or connect
to an existing session. Interact with Fluent through the session object returned by either the launch
or connect methods.

PyFluent sessions
~~~~~~~~~~~~~~~~~
:ref:`Understand how to work with PyFluent session objects <ref_session_guide>`.

Guided meshing workflows
~~~~~~~~~~~~~~~~~~~~~~~~
Leverage intuitive, :ref:`guided workflows <ref_meshing_guide>` to create high-quality meshes.

Solution mode and settings objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utilize :ref:`settings objects <ref_settings>` to configure and control your simulation. Get familiar
with the basics of setting up and executing your physics problem using Python.

Field data extraction
~~~~~~~~~~~~~~~~~~~~~
:ref:`Extract solution and mesh data <ref_fields_guide>` for analysis and post-processing.
Access and modify field data arrays for physical variables of interest at your chosen locations.
Choose to apply reduction functions or create and compute expressions using Fluent's powerful
expression language.

Offline features
~~~~~~~~~~~~~~~~

.. vale Google.Spacing = NO

:ref:`Get rapid access to Fluent case and solution data through offline tools<ref_offline_guide>`.
PyFluent offers Python classes that represent case, data, and project files, enabling you to work with
Fluent data efficiently offline. The :obj:`~ansys.fluent.core.file_session.FileSession` class mimics the functionality of live 
:ref:`live session objects <ref_session_guide>`, allowing you to access field data and other relevant information without a live Fluent session.

.. vale Google.Spacing = YES

