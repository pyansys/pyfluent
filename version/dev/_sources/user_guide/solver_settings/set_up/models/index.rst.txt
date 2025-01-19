.. _ref_models_guide:

.. vale Google.Spacing = NO

Physics models
==============

The guide for each Python physics model uses a :obj:`~ansys.fluent.core.session_solver.Solver` session object
created using the code below. For the physics models to be active you generally
need to have loaded a case or mesh file; e.g.:

.. code:: python

    >>> import ansys.fluent.core as pyfluent
    >>> from ansys.fluent.core import examples
    >>> file_name = examples.download_file("mixing_elbow.cas.h5", "pyfluent/mixing_elbow")
    >>> solver = pyfluent.launch_fluent()
    >>> solver.settings.file.read_case(file_name=file_name)


.. toctree::
   :maxdepth: 1
   :hidden:

   energy
   viscous
   dpm
   radiation
   species
   battery

