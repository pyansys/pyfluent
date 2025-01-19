.. _ref_data_transfer:

Transfer data
=============

You use the `'transfer_case`` method to transfer a case or mesh file between
instances of Fluent. You must specify a source instance and one or more
destination instances.

Sample usage
------------

To use the ``transfer_case`` method to transfer a mesh or a case file, you import the
file and pass the source, destination instances, and the file type. You can either
generate the files in the parent instance or just read the file.

This example shows how you use the ``transfer_case`` method to read a mesh file in a
pure meshing session and transfer it to a solver session.

.. code-block:: python

  >>> import ansys.fluent.core as pyfluent
  >>> from ansys.fluent.core.examples import download_file
  >>> from ansys.fluent.core.utils.data_transfer import transfer_case

  >>> mesh_file_name = download_file("mixing_elbow.msh.h5", "pyfluent/mixing_elbow")
  >>> pure_meshing_session = pyfluent.launch_fluent(mode="pure-meshing")
  >>> pure_meshing_session.tui.file.read_mesh(import_file_name)

  >>> solver_session = pyfluent.launch_fluent(mode="solver")

  >>> transfer_case(
  >>>     source_instance=meshing,
  >>>     solvers=[solver],
  >>>     file_type="mesh",
  >>>     file_name_stem='',
  >>>     num_files_to_try=1,
  >>>     clean_up_temp_file=True,
  >>>     overwrite_previous=True
  >>> )


Similarly, you can use the ``transfer_case`` method to transfer a case file from one instance of Fluent
to another.

.. automodule:: ansys.fluent.core.utils.data_transfer
   :members:
   :show-inheritance:
   :undoc-members:
   :exclude-members: __weakref__, __dict__
   :special-members: __init__
   :autosummary:
