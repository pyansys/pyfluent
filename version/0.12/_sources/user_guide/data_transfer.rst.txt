.. _ref_data_transfer:

Data transfer
=============

Data transfer helps in transferring a case or a mesh file between instances of Fluent.
You must specify a source instance and one or multiple destination instances.

Sample usage
------------

You can use the `'transfer_case`` method to transfer either a mesh or a case file by importing it
and passing the source and destination instances along with the file type. You can either
generate the files in the parent instance or just read it.

This example shows how to use the `` use the ``transfer_case`` by reading a mesh file in a
pure meshing session and transferring it to a solver session.

.. code-block:: python

  >>> import ansys.fluent.core as pyfluent
  >>> from ansys.fluent.core.examples import download_file
  >>> from ansys.fluent.core.utils.data_transfer import transfer_case

  >>> mesh_filename = download_file("mixing_elbow.msh.h5", "pyfluent/mixing_elbow")
  >>> pure_meshing_session = pyfluent.launch_fluent(mode="pure-meshing")
  >>> pure_meshing_session.tui.file.read_mesh(import_filename)

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


Similarly, you can also use the ``transfer_case`` method to transfer a case file from one instance of Fluent
to another.
