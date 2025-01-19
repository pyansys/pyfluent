.. _ref_file_session_guide:

.. vale Google.Spacing = NO

File Session
============

The :obj:`~ansys.fluent.core.file_session.FileSession` class mimics the functionality of :ref:`live session objects <ref_session_guide>`, allowing you
to access field data and other relevant information without a live Fluent session.
You command :obj:`~ansys.fluent.core.file_session.FileSession` objects to read your input files before you access the data through
the :obj:`~ansys.fluent.core.file_session.FileSession` object methods. 

Sample usage
------------

The following examples cover both single-phase and multiphase cases. After case and data files are
loaded, field information is accessed and some field data is extracted. Here, the extraction uses two approaches:
a transaction-based approach where multiple data requests are bundled into each transaction and a direct approach
where a sequence of separate requests are made.

Single-phase
~~~~~~~~~~~~

.. code-block:: python

  >>> from ansys.fluent.core import examples
  >>> from ansys.fluent.core.file_session import FileSession

  >>> case_file_name = examples.download_file("elbow1.cas.h5", "pyfluent/file_session")
  >>> data_file_name = examples.download_file("elbow1.dat.h5", "pyfluent/file_session")
  >>> file_session = FileSession()
  >>> file_session.read_case(case_file_name)
  >>> file_session.read_data(data_file_name)

  >>> file_session.fields.field_info.get_scalar_field_range("SV_T")
  [293.1446694544748, 313.1515948109515]
  >>> file_session.fields.field_info.get_surfaces_info()
  {'wall': {'surface_id': [3],
   'zone_id': -1,
   'zone_type': 'wall',
   'type': 'plane'},
   'symmetry': {'surface_id': [4],
   'zone_id': -1,
   'zone_type': 'wall',
   'type': 'plane'},
    .....
   'default-interior': {'surface_id': [9],
   'zone_id': -1,
   'zone_type': 'wall',
   'type': 'plane'}}
  >>> file_session.fields.field_info.get_scalar_fields_info()
  {'SV_ARTIFICIAL_WALL_FLAG': {'display_name': 'SV_ARTIFICIAL_WALL_FLAG',
   'section': 'field-data',
   'domain': 'phase-1'},
   'SV_D': {'display_name': 'SV_D',
   'section': 'field-data',
   'domain': 'phase-1'},
   .....
   'SV_WALL_YPLUS_UTAU': {'display_name': 'SV_WALL_YPLUS_UTAU',
   'section': 'field-data',
   'domain': 'phase-1'}}
   >>> file_session.fields.field_info.get_vector_fields_info()
   {'velocity': {'x-component': 'SV_U',
    'y-component': 'SV_V',
    'z-component': 'SV_W'}}
   >>> transaction = file_session.fields.field_data.new_transaction()
   >>> transaction.add_surfaces_request([3, 4])
   >>> transaction.add_scalar_fields_request("SV_T", [3, 4])
   >>> transaction.add_vector_fields_request("velocity", [3, 4])
   >>> transaction.get_fields()
   {(('type', 'scalar-field'),
     ('dataLocation', 1),
     ('boundaryValues',
      False)): {3: {'SV_T': array([293.14999, 293.14999, 293.14999, ..., 293.14999, 293.14999,
             293.14999])}, 4: {'SV_T': array([293.14999, 293.14999, 293.14999, ..., 293.14999, 293.14999,
             293.14999])}},
    (('type',
      'vector-field'),): {3: {'velocity': array([0., 0., 0., ..., 0., 0., 0.]), 'vector-scale': array([0.1])},
     4: {'velocity': array([ 3.32643010e-01,  6.64311343e-03,  0.00000000e+00, ...,
              4.56052223e-01,  2.45034248e-01, -1.24726618e-15]),
      'vector-scale': array([0.1])}},
    (('type',
      'surface-data'),): {3: {'faces': array([   4,    3,    2, ...,  727,  694, 3809], dtype=uint32), 'vertices': array([ 0.        , -0.1016    ,  0.        , ...,  0.00620755,
             -0.19304685,  0.03033731])},
     4: {'faces': array([   4,  295,  294, ...,  265, 1482, 2183], dtype=uint32),
      'vertices': array([ 0.        , -0.1016    ,  0.        , ...,  0.06435075,
             -0.08779959,  0.        ])}}
   >>> from ansys.fluent.core.services.field_data import SurfaceDataType
   >>> file_session.fields.field_data.get_surface_data([SurfaceDataType.Vertices], [3, 4])[3].shape
   (3810, 3)
   >>> file_session.fields.field_data.get_surface_data(data_types=[SurfaceDataType.Vertices], surfaces=[3, 4])[3][1500][0]
   0.12405861914157867
   >>> file_session.fields.field_data.get_scalar_field_data("SV_T", surfaces=["wall"])["wall"].shape
   (3630,)
   >>> file_session.fields.field_data.get_scalar_field_data("SV_T", surfaces=["wall"])["wall"][1500]
   293.18071329432047
   >>> file_session.fields.field_data.get_vector_field_data("velocity", surfaces=["symmetry"])["symmetry"].shape
   (2018, 3)
   >>> file_session.fields.field_data.get_vector_field_data("velocity", surfaces=["symmetry"])["symmetry"][1000][0]
   0.001690600193527586


Multiphase
~~~~~~~~~~~

.. code-block:: python

  >>> from ansys.fluent.core import examples
  >>> from ansys.fluent.core.file_session import FileSession

  >>> case_file_name = examples.download_file("mixing_elbow_mul_ph.cas.h5", "pyfluent/file_session")
  >>> data_file_name = examples.download_file("mixing_elbow_mul_ph.dat.h5", "pyfluent/file_session")
  >>> file_session = FileSession()
  >>> file_session.read_case(case_file_name)
  >>> file_session.read_data(data_file_name)

  >>> file_session.fields.field_info.get_scalar_field_range("phase-2:SV_P")
  [0.0, 1.5435200335871788e-11]
  >>> file_session.fields.field_info.get_scalar_fields_info()
  {'phase-1:SV_ARTIFICIAL_WALL_FLAG': {'display_name': 'SV_ARTIFICIAL_WALL_FLAG',
   'section': 'field-data',
   'domain': 'phase-1'},
   'phase-1:SV_DENSITY': {'display_name': 'SV_DENSITY',
   'section': 'field-data',
   'domain': 'phase-1'},
   .....
   'phase-4:': {'display_name': '',
   'section': 'field-data',
   'domain': 'phase-4'}}
   >>> file_session.fields.field_info.get_vector_fields_info()
   {'phase-1:velocity': {'x-component': 'phase-1: SV_U',
    'y-component': 'phase-1: SV_V',
    'z-component': 'phase-1: SV_W'},
    .....
    'phase-4:velocity': {'x-component': 'phase-4: SV_U',
    'y-component': 'phase-4: SV_V',
    'z-component': 'phase-4: SV_W'}}
   >>> transaction = file_session.fields.field_data.new_transaction()
   >>> transaction.add_scalar_fields_request("phase-1:SV_DENSITY", [30])
   >>> transaction.add_vector_fields_request("phase-1:velocity", [30])
   >>> transaction.get_fields()
   {(('type', 'scalar-field'),
     ('dataLocation', 1),
     ('boundaryValues',
      False)): {30: {'phase-1:SV_DENSITY': array([1.225, .....          1.225])}},
    (('type',
      'vector-field'),): {30: {'phase-1:velocity': array([0., ..... 0.]),
      'vector-scale': array([0.1])}}}
   >>> from ansys.fluent.core.services.field_data import SurfaceDataType
   >>> file_session.fields.field_data.get_surface_data([SurfaceDataType.Vertices], [30])[30].shape
   (79, 3)
   >>> file_session.fields.field_data.get_surface_data([SurfaceDataType.Vertices], [30])[30][50][0]
   0.14896461503555408
   >>> file_session.fields.field_data.get_scalar_field_data("phase-1:SV_P", surfaces=["wall-elbow"])["wall-elbow"].shape
   (2168,)
   >>> file_session.fields.field_data.get_scalar_field_data("phase-1:SV_P", surfaces=["wall-elbow"])["wall-elbow"][1100]
   1.4444035696104466e-11
   >>> file_session.fields.field_data.get_vector_field_data("phase-2:velocity", surfaces=["wall-elbow"])["wall-elbow"].shape
   (2168, 3)
   >>> file_session.fields.field_data.get_vector_field_data("phase-2:velocity", surfaces=["wall-elbow"])["wall-elbow"][1000][0]
   0.0


Visualization sample usage
--------------------------

You can use the `ansys-fluent-visualization <https://visualization.fluent.docs.pyansys.com/version/stable/>`_ package to display the
mesh and to visualize results via contours, vectors and other
post-processing objects.


.. code-block:: python

  >>> from ansys.fluent.visualization import set_config
  >>> set_config(blocking=True, set_view_on_display="isometric")
  >>> import ansys.fluent.core as pyfluent
  >>> from ansys.fluent.core import examples
  >>> from ansys.fluent.visualization.matplotlib import Plots
  >>> from ansys.fluent.visualization.pyvista import Graphics
  >>> from ansys.fluent.core.file_session import FileSession
  >>> fileSession=FileSession()
  >>> fileSession.read_case("elbow1.cas.h5")
  >>> fileSession.read_data("elbow1.dat.h5")
  >>> graphics = Graphics(session=fileSession)

Display mesh at wall.

.. code-block:: python

  >>> mesh1 = graphics.Meshes["mesh-1"]
  >>> mesh1.show_edges = True
  >>> mesh1.surfaces_list = [ "wall"]
  >>> mesh1.display("w1")

Display temperature contour at symmetry.

.. code-block:: python

  >>> contour1 = graphics.Contours["mesh-1"]
  >>> contour1.node_values = False
  >>> contour1.field = "SV_T"
  >>> contour1.surfaces_list = ['symmetry']
  >>> contour1.display('w2')

Display velocity vector data at symmetry and wall.

.. code-block:: python

  >>> velocity_vector = graphics.Vectors["velocity-vector"]
  >>> velocity_vector.field = "SV_T"
  >>> velocity_vector.surfaces_list = ['symmetry', 'wall']
  >>> velocity_vector.display("w3")
