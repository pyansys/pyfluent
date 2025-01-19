.. _ref_file_transfer_guide:

File transfer
=============

File transfer service allows you to upload a file to the server and download a file from the server. You can optionally specify
the name of the file that is being uploaded to the server, default is the name of the uploading file.
You can optionally specify the download directory while downloading the file from the server, default is the current working directory.
You can define your file transfer service and use it as ``launch_fluent(file_transfer_service=<name_of_the_file_transfer_service>)``.

The following file transfer services are supported:

#. **Local file transfer service**:

   * :ref:`Local file transfer service <ref_file_transfer_service>` can be used for Fluent launched in the standalone mode.

#. **Remote file transfer service**:

   * :ref:`Remote file transfer service <ref_file_transfer_service>` is based on the `gRPC client <https://filetransfer.tools.docs.pyansys.com/version/stable/>`_ and `gRPC server <https://filetransfer-server.tools.docs.pyansys.com/version/stable/>`_.

   * It can be used for Fluent launched in the container mode.

Examples
--------

.. code-block:: python

   >>> import ansys.fluent.core as pyfluent
   >>> from ansys.fluent.core import examples
   >>> from ansys.fluent.core.utils.file_transfer_service import LocalFileTransferStrategy, RemoteFileTransferStrategy

   >>> case_file_name = examples.download_file("mixing_elbow.cas.h5", "pyfluent/mixing_elbow")
   >>> mesh_file_name = examples.download_file("mixing_elbow.msh.h5", "pyfluent/mixing_elbow")

   >>> # Local file transfer service
   >>> meshing_session = pyfluent.launch_fluent(mode=pyfluent.FluentMode.MESHING, file_transfer_service=LocalFileTransferStrategy())
   >>> meshing_session.upload(file_name=mesh_file_name, remote_file_name="elbow.msh.h5")
   >>> meshing_session.meshing.File.ReadMesh(FileName="elbow.msh.h5")
   >>> meshing_session.meshing.File.WriteMesh(FileName="write_elbow.msh.h5")
   >>> meshing_session.download(file_name="write_elbow.msh.h5", local_directory="<local_directory_path>")

   >>> # Remote file transfer service
   >>> solver_session = pyfluent.launch_fluent(mode=pyfluent.FluentMode.SOLVER, file_transfer_service=RemoteFileTransferStrategy())
   >>> solver_session.upload(file_name=case_file_name, remote_file_name="elbow.cas.h5")
   >>> solver_session.file.read_case(file_name="elbow.cas.h5")
   >>> solver_session.file.write_case(file_name="write_elbow.cas.h5")
   >>> solver_session.download(file_name="write_elbow.cas.h5", local_directory="<local_directory_path>")
