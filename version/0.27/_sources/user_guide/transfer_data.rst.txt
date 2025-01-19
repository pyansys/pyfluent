.. _ref_data_transfer_guide:

Transferring session data
=========================

You use the :func:`transfer_case() <ansys.fluent.core.utils.data_transfer.transfer_case>` function to transfer a case or mesh file between
PyFluent sessions. You must specify a source session and one or more
destination solver sessions.

Sample usage
------------

This example shows how you use the :func:`transfer_case() <ansys.fluent.core.utils.data_transfer.transfer_case>` function to read a mesh file in a
meshing session and transfer it to a solver session.

.. code:: python

  >>> import ansys.fluent.core as pyfluent
  >>> from ansys.fluent.core.examples import download_file
  >>> from ansys.fluent.core.utils.data_transfer import transfer_case

  >>> mesh_file_name = download_file(
  >>>     "mixing_elbow.msh.h5",
  >>>     "pyfluent/mixing_elbow"
  >>> )
  >>> pure_meshing_session = pyfluent.launch_fluent(
  >>>     mode=pyfluent.FluentMode.PURE_MESHING
  >>> )
  >>> pure_meshing_session.tui.file.read_mesh(
  >>>     import_file_name
  >>> )

  >>> solver_session = pyfluent.launch_fluent(
  >>>     mode=pyfluent.FluentMode.SOLVER
  >>> )

  >>> transfer_case(
  >>>     source_instance=meshing,
  >>>     solvers=[solver],
  >>>     file_type="mesh",
  >>>     file_name_stem='',
  >>>     num_files_to_try=1,
  >>>     clean_up_temp_file=True,
  >>>     overwrite_previous=True
  >>> )


Similarly, you can use the :func:`transfer_case() <ansys.fluent.core.utils.data_transfer.transfer_case>` function to transfer a case file between PyFluent
sessions.