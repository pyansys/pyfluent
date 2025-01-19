.. _ref_fields_guide:

Fields
======

PyFluent provides several services that allow you to access field data in different ways.
Every PyFluent solution and meshing ``Session`` object contains a ``fields`` object. In both
solution and meshing modes, the ``fields`` object contains ``field_data``, ``field_data_streaming``
and ``field_info`` children. In solution mode, the ``fields`` object also has ``reduction``,
``solution_variable_data`` and ``solution_variable_info`` children.

.. toctree::
   :maxdepth: 1
   :hidden:

   field_data
   field_info
   reduction
   solution_data
