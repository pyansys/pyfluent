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
  >>> from ansys.fluent.core.filereader.casereader import CaseReader

  >>> case_filepath = examples.download_file("Static_Mixer_Parameters.cas.h5", "pyfluent/static_mixer")
  >>> reader = CaseReader(case_filepath=case_filepath)
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

    >>> reader = CaseReader(project_filepath="Dir1/Dir2/project.flprj")

- **Reads ``rp_vars`` and ``config_vars`` variables**
  The CaseFile class can provide the ``rp_vars`` and ``config_vars`` variables:
  
  .. code-block:: python

    >>> reader.rp_vars()
    >>> reader.config_vars()


.. automodule:: ansys.fluent.core.filereader.case_file
   :members:
   :show-inheritance:
   :undoc-members:
   :exclude-members: __weakref__, __dict__
   :special-members: __init__
   :autosummary:
