.. _ref_field_data_guide:

.. vale Google.Spacing = NO

Field data
==========

You can use field data objects to access Fluent surface, scalar, vector, and pathlines data.

Accessing field data objects
----------------------------

To work with field data, ensure the Fluent solver is launched and the relevant data is made available.
You can do this either by loading both case and data files or by reading a case file and initializing.

.. code-block:: python

  >>> import ansys.fluent.core as pyfluent
  >>> from ansys.fluent.core.examples import download_file
  >>> solver = pyfluent.launch_fluent(mode=pyfluent.FluentMode.SOLVER)
  >>> case_path = download_file(file_name="exhaust_system.cas.h5", directory="pyfluent/exhaust_system")
  >>> data_path = download_file(file_name="exhaust_system.dat.h5", directory="pyfluent/exhaust_system")
  >>> solver.settings.file.read_case_data(file_name=case_path)

  >>> field_data = solver.fields.field_data  # This creates an instance of the FieldData class.

Simple requests
---------------

Here are the methods for requesting each type of field:

- ``get_surface_data`` for surface data.
- ``get_scalar_field_data`` for scalar field data.
- ``get_vector_field_data`` for vector field data.
- ``get_pathlines_field_data`` for pathlines field data.

Get surface data
~~~~~~~~~~~~~~~~
You can request surface vertices for a given surface name by calling
the ``get_surface_data`` method and specifying ``Vertices`` for ``data_types``.

.. code-block:: python

  >>> from ansys.fluent.core.services.field_data import SurfaceDataType

  >>> vertices_data = field_data.get_surface_data(
  >>>     surfaces=["inlet"], data_types=[SurfaceDataType.Vertices]
  >>> )
  # The method retrieves surface vertex coordinates as a NumPy array.
  # Shape: (389, 3) - This means 389 vertices, each defined by 3 coordinates (x, y, z).
  >>> vertices_data["inlet"][SurfaceDataType.Vertices].shape
  (389, 3)
  >>> vertices_data["inlet"][SurfaceDataType.Vertices][5]
  # Example: The 6th vertex (zero-based indexing) has coordinates [-0.3469, 0.0, -0.0386].
  array([-0.34689394,  0.        , -0.03863097], dtype=float32)

You can call the same method to get the corresponding surface face normals and centroids
by specifying ``FacesNormal`` and ``FacesCentroid`` for ``data_types`` respectively.

.. code-block:: python

  >>> faces_normal_and_centroid_data = field_data.get_surface_data(
  >>>     data_types=[SurfaceDataType.FacesNormal, SurfaceDataType.FacesCentroid],
  >>>     surfaces=["inlet"]
  >>> )
  # FacesNormal shape: (262, 3) - 262 face normals, each with 3 components (x, y, z).
  # FacesCentroid shape: (262, 3) - Centroids for each of the 262 faces, given as (x, y, z).
  >>> faces_normal_and_centroid_data["inlet"][SurfaceDataType.FacesNormal].shape
  (262, 3)
  >>> faces_normal_and_centroid_data["inlet"][SurfaceDataType.FacesCentroid][15]
  # Example: The centroid of the 16th face has coordinates [-0.3463, 0.0, -0.0328].
  array([-0.34634298,  0.        , -0.03276413], dtype=float32)

You can request face connectivity data for given ``surfaces`` by calling
the ``get_surface_data`` method and specifying ``FacesConnectivity`` for ``data_types``.

.. code-block:: python

  >>> faces_connectivity_data = field_data.get_surface_data(
  >>>     data_types=[SurfaceDataType.FacesConnectivity], surfaces=["inlet"]
  >>> )
  # FacesConnectivity provides indices of vertices for each face. For example:
  # Face 6 is connected to vertices 4, 5, 12, and 11.
  >>> faces_connectivity_data["inlet"][SurfaceDataType.FacesConnectivity][5]
  array([ 4,  5, 12, 11])

Get scalar field data
~~~~~~~~~~~~~~~~~~~~~
You can call the ``get_scalar_field_data`` method to get scalar field data, such as absolute pressure:

.. code-block:: python

  >>> abs_press_data = field_data.get_scalar_field_data(
  >>>     field_name="absolute-pressure", surfaces=["inlet"]
  >>> )
  # Shape: (389,) - A single scalar value (e.g., pressure) for each of the 389 vertices.
  >>> abs_press_data["inlet"].shape
  (389,)
  >>> abs_press_data["inlet"][120]
  # Example: The absolute pressure at the 121st vertex is 102031.4 Pascals.
  102031.4

Get vector field data
~~~~~~~~~~~~~~~~~~~~~
You can call the ``get_vector_field_data`` method to get vector field data.

.. code-block:: python

  >>> velocity_vector_data = field_data.get_vector_field_data(field_name="velocity", surfaces=["inlet", "inlet1"])
  # Shape: (262, 3) - Velocity vectors for 262 faces, each with components (vx, vy, vz) for 'inlet'.
  >>> velocity_vector_data["inlet"].shape
  (262, 3)
  # Shape: (265, 3) - Velocity vectors for 265 faces, each with components (vx, vy, vz) for 'inlet1'.
  >>> velocity_vector_data["inlet1"].shape
  (265, 3)

Get pathlines field data
~~~~~~~~~~~~~~~~~~~~~~~~
You can call the ``get_pathlines_field_data`` method to get pathlines field data.

.. code-block:: python

  >>> path_lines_data = field_data.get_pathlines_field_data(
  >>>     field_name="velocity", surfaces=["inlet"]
  >>> )
  # Vertices shape: (29565, 3) - 29565 pathline points, each with coordinates (x, y, z).
  # Lines: A list where each entry contains indices of vertices forming a pathline.
  # Velocity shape: (29565,) - Scalar velocity values at each pathline point.
  >>> path_lines_data["inlet"]["vertices"].shape
  (29565, 3)
  >>> len(path_lines_data["inlet"]["lines"])
  29303
  >>> path_lines_data["inlet"]["velocity"].shape
  (29565,)
  >>> path_lines_data["inlet"]["lines"][100]
  # Example: Pathline 101 connects vertices 100 and 101.
  array([100, 101])

Making multiple requests in a single transaction
------------------------------------------------
You can get data for multiple fields in a single transaction.

First, create a transaction object for field data.

.. code-block:: python

  >>> transaction = solver.fields.field_data.new_transaction()
  # This creates a new transaction object for batching multiple requests.

Then combine requests for multiple fields using ``add_<items>_request`` methods in a single transaction:

- ``add_surfaces_request`` adds a surfaces request.
- ``add_scalar_fields_request`` adds a scalar fields request.
- ``add_vector_fields_request`` adds a vector fields request.
- ``add_pathlines_fields_request`` adds a pathlines fields request.

.. code-block:: python

  >>> transaction.add_surfaces_request(
  >>>     surfaces=[1], data_types=[SurfaceDataType.Vertices, SurfaceDataType.FacesCentroid]
  >>> )
  # Adds a request for surface data such as vertices and centroids.
  >>> transaction.add_scalar_fields_request(
  >>>     surfaces=[1, 2], field_name="pressure", node_value=True, boundary_value=True
  >>> )
  # Adds a request for scalar field data like pressure.
  >>> transaction.add_vector_fields_request(
  >>>     surfaces=[1, 2], field_name="velocity"
  >>> )
  # Adds a request for vector field data like velocity.

You can call the ``get_fields`` method to execute the transaction and retrieve the data:

.. code-block:: python

  >>> payload_data = transaction.get_fields()
  # Executes all requests and returns the combined field data.

``payload_data`` is a dictionary containing the requested fields as a numpy array in the following order:

``tag -> surface_id [int] -> field_name [str] -> field_data[np.array]``

.. note::
   ``get_fields`` call also clears all requests, so that subsequent calls to this method
   yield nothing until more requests are added.


Tag
---
A tag is tuple of input, value pairs for which field data is generated.

For example, if you request the scalar field data for element location, in the
dictionary, ``tag`` is ``(('type','scalar-field'), ('dataLocation', 1), ('boundaryValues',False))``.
Similarly, if you request the boundary values for node location, ``tag`` is
``(('type','scalar-field'), ('dataLocation', 0), ('boundaryValues',True)``.

Surface ID
----------
The surface ID is the same one that is passed in the request.

Field name
----------
A request returns multiple fields. The number of fields depends on the request
type.

Surface request
~~~~~~~~~~~~~~~
The response to a surface request contains any of the following fields,
depending on the request arguments:

- ``faces``, which contain face connectivity
- ``vertices``, which contain node coordinates
- ``centroid``, which contains face centroids
- ``face-normal``, which contains face normals

Scalar field request
~~~~~~~~~~~~~~~~~~~~
The response to a scalar field request contains a single field with the same
name as the scalar field name passed in the request.

Vector field request
~~~~~~~~~~~~~~~~~~~~
The response to a vector field request contains two fields:

- ``vector field``, with the same name as the vector field name that is passed
 in the request
- ``vector-scale``, a float value indicating the vector scale.

Pathlines field request
~~~~~~~~~~~~~~~~~~~~~~~
The response to a pathlines field request contains the following fields:

- ``pathlines-count``, which contains pathlines count.
- ``lines``, which contain pathlines connectivity.
- ``vertices``, which contain node coordinates.
- ``field name``, which contains pathlines field. field name is the same name as
  the scalar field name passed in the request.
- ``particle-time``, which contains particle time, if requested.
- ``additional field name``, which contains additional field, if requested.
  additional field name is the same name as the additional field name passed in
  the request.

Allowed values
--------------
Additionally there is an ``allowed_values`` method provided on all of
``field_name``, ``surface_name`` and ``surface_ids`` which tells you what object
names are accessible.

Some sample use cases are demonstrated below:

.. code-block:: python

  >>> field_data.get_scalar_field_data.field_name.allowed_values()
  ['abs-angular-coordinate', 'absolute-pressure', 'angular-coordinate',
  'anisotropic-adaption-cells', 'aspect-ratio', 'axial-coordinate', 'axial-velocity',
  'boundary-cell-dist', 'boundary-layer-cells', 'boundary-normal-dist', ...]

  >>> transaction = field_data.new_transaction()
  >>> transaction.add_scalar_fields_request.field_name.allowed_values()
  ['abs-angular-coordinate', 'absolute-pressure', 'angular-coordinate',
  'anisotropic-adaption-cells', 'aspect-ratio', 'axial-coordinate', 'axial-velocity',
  'boundary-cell-dist', 'boundary-layer-cells', 'boundary-normal-dist', ...]

  >>> field_data.get_scalar_field_data.surface_name.allowed_values()
  ['in1', 'in2', 'in3', 'inlet', 'inlet1', 'inlet2', 'out1', 'outlet', 'solid_up:1', 'solid_up:1:830', 'solid_up:1:830-shadow']

  >>> field_data.get_surface_data.surface_ids.allowed_values()
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


Field data streaming
--------------------

PyFluent's field data streaming service allows you to dynamically observe changes
in field data by tracking its values in real time. You can integrate PyFluent's
field data streaming callback mechanism with visualization
tools from the Python ecosystem, making it easy to visualize the data of interest.

.. note::
   In **Meshing mode**, only 'field_data_streaming' provides a valid interface as of now.
   Other methods currently return an empty array when used in Meshing mode.

   The 'field_data_streaming' is available only for the **Meshing mode**.

The following example demonstrates how to update mesh data in **Meshing mode**
using the field data streaming mechanism:

.. code-block:: python

  >>> import ansys.fluent.core as pyfluent
  >>> from ansys.fluent.core import examples

  >>> # Download example geometry file
  >>> import_file_name = examples.download_file(
  >>>     "mixing_elbow.pmdb", "pyfluent/mixing_elbow"
  >>> )

  >>> # Launch Fluent in Meshing mode
  >>> meshing = pyfluent.launch_fluent(mode="meshing")

  >>> # Dictionary to store mesh data
  >>> mesh_data = {}

  >>> # Define a callback function to process streamed field data
  >>> def plot_mesh(index, field_name, data):
  >>>     if data is not None:
  >>>         if index in mesh_data:
  >>>             mesh_data[index].update({field_name: data})
  >>>         else:
  >>>             mesh_data[index] = {field_name: data}

  >>> # Register the callback function
  >>> meshing.fields.field_data_streaming.register_callback(plot_mesh)

  >>> # Start field data streaming with byte stream and chunk size
  >>> meshing.fields.field_data_streaming.start(provideBytesStream=True, chunkSize=1024)

  >>> # Initialize the Meshing workflow
  >>> meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

  >>> # Import the geometry into the workflow
  >>> meshing.workflow.TaskObject["Import Geometry"].Arguments = {
  >>>    "FileName": import_file_name,
  >>>    "LengthUnit": "in",
  >>> }

  >>> meshing.workflow.TaskObject["Import Geometry"].Execute()
