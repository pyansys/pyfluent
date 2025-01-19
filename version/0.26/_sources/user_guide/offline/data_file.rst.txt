.. _ref_data_file_guide:

.. vale Google.Spacing = NO

DataFile
========

The :obj:`~ansys.fluent.core.filereader.data_file.DataFile` class allows you to access solution data without a live Fluent session.
You command :obj:`~ansys.fluent.core.filereader.data_file.DataFile` objects to read your Fluent data files before you access the data through
the :obj:`~ansys.fluent.core.filereader.data_file.DataFile` methods. 

Sample usage
------------

This example shows how to command a :obj:`~ansys.fluent.core.filereader.data_file.DataFile` object to access case and data files, and query its interface:

.. code-block:: python

  >>> from ansys.fluent.core import examples
  >>> from ansys.fluent.core.filereader.data_file import DataFile
  >>> from ansys.fluent.core.filereader.case_file import CaseFile

  >>> data_file_name = examples.download_file("elbow1.dat.h5", "pyfluent/file_session")
  >>> reader = DataFile(data_file_name=data_file_name, case_file_handle=CaseFile(case_file_name))
  >>> reader.case_file
  'elbow1.cas.h5'
  >>> reader.variables()
  {'flow-time': 0.0,
   'solvertime': 43.13454608435059,
   'time-step': 0,
    .....
   'vbm/trim': []}
  >>> reader.get_phases()
  ['phase-1']
  >>> reader.get_face_variables("phase-1")
  ['SV_ARTIFICIAL_WALL_FLAG',
   'SV_D',
   'SV_DENSITY',
    .....
   'SV_WALL_YPLUS_UTAU',
   '']
   >>> reader.get_cell_variables("phase-1")
   ['SV_BF_V',
    'SV_D',
    'SV_DENSITY',
     .....
    'SV_V',
    'SV_W',
    '']
   >>> reader.get_face_scalar_field_data("phase-1", "SV_T", 4)
   array([293.14999, 293.14999, 293.14999, ..., 293.14999, 293.14999,
       293.14999])
   >>> reader.get_face_vector_field_data("phase-1", 4)
   array([ 3.32643010e-01,  6.64311343e-03,  0.00000000e+00, ...,
        4.56052223e-01,  2.45034248e-01, -1.24726618e-15])
