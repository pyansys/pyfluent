.. _ref_case_reader:

CaseFile
========

The CaseFile class provides a reader for Fluent case files.

Sample usage
------------

You can use the CaseFile class by importing it and passing a case file path.
This example shows how to have the CaseFile class read a case file (.cas.h5)
from the ``examples`` repository:

.. code-block:: python

  >>> from ansys.fluent.core import examples
  >>> from ansys.fluent.core.filereader.case_file import CaseFile

  >>> case_filepath = examples.download_file("Static_Mixer_Parameters.cas.h5", "pyfluent/static_mixer")
  >>> reader = CaseFile(case_filepath=case_filepath)
  >>> reader.precision()
  2
  >>> reader.num_dimensions()
  3
  >>> {p.name: p.value for p in reader.input_parameters()}
  {'inlet1_vel': '1 [m/s]', 'inlet1_temp': '300 [K]', 'inlet2_vel': '1 [m/s]', 'inlet2_temp': '350 [K]'}
  >>> {p.name: p.units for p in reader.output_parameters()}
  {'outlet-temp-avg-op': 'K', 'outlet-vel-avg-op': 'm s^-1'}

Additional features
-------------------
Along with basic functionality, the CaseFile class provides many additional features, including these:

- **Supports multiple file formats**
  The CaseFile class can read Fluent case files (CAS, CAS.HF, and CAS.GZ) in both text and binary formats.
- **Takes a project path as an argument**
  The CaseFile class has an option for taking a Fluent project path (FLPRJ) as an argument and locating
  the case file path:
  
  .. code-block:: python

    >>> reader = CaseFile(project_filepath="Dir1/Dir2/project.flprj")

- **Reads ``rp_vars`` and ``config_vars`` variables**
  The CaseFile class can provide the ``rp_vars`` and ``config_vars`` variables:
  
  .. code-block:: python

    >>> reader.rp_vars()
    >>> reader.config_vars()

- **Extracts mesh data**
  The CaseReader can be used to extract mesh data. This example shows how to
  have the CaseFile class read a case file (.cas.h5) from the ``examples``
  repository and extract and use mesh data:

  .. code-block:: python

      >>> from ansys.fluent.core import examples
      >>> from ansys.fluent.core.filereader.case_file import CaseFile

      >>> case_filepath = examples.download_file("elbow1.cas.h5", "pyfluent/file_session")
      >>> reader = CaseFile(case_filepath=case_filepath)
      >>> reader.get_mesh().get_surface_ids()
      [3, 4, 5, 6, 7, 9]
      >>> reader.get_mesh().get_surface_names()
      ['wall',
       'symmetry',
       'pressure-outlet-7',
       'velocity-inlet-6',
       'velocity-inlet-5',
       'default-interior']
      >>> reader.get_mesh().get_surface_locs(3)
      [0, 3629]
      >>> reader.get_mesh().get_connectivity(3)
      array([   4,    3,    2, ...,  727,  694, 3809], dtype=uint32)
      >>> reader.get_mesh().get_vertices(3)
      array([ 0.        , -0.1016    ,  0.        , ...,  0.00620755,
       -0.19304685,  0.03033731])


.. automodule:: ansys.fluent.core.filereader.case_file
   :members:
   :show-inheritance:
   :undoc-members:
   :exclude-members: __weakref__, __dict__
   :special-members: __init__
   :autosummary:
