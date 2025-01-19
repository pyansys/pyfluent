Applying solution settings
==========================

PyFluent allows you to use :ref:`ref_settings` to interact with solution settings, and initialize and solve.


Steady or transient solution model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

  >>> setup = pyfluent.Setup(settings_source=solver)
  >>> solver_time = setup.general.solver.time
  >>> solver_time.get_state()
  'steady'
  >>> solver_time.allowed_values()
  ['steady', 'unsteady-1st-order']
  >>> solver_time.set_state("unsteady-1st-order")


Pressure-based or density-based solver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

  >>> setup = pyfluent.Setup(settings_source=solver)
  >>> solver_type = setup.general.solver.type
  >>> solver_type.get_state()
  'pressure-based'
  >>> solver_type.allowed_values()
  ['pressure-based', 'density-based-implicit', 'density-based-explicit']
  >>> solver.settings.setup.general.solver.type.set_state("density-based-explicit")
  >>> solver_type.get_state()
  'density-based-explicit'


Velocity coupling scheme and gradient options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
.. code:: python

  >>> methods = pyfluent.Methods(settings_source=solver)
  >>> flow_scheme = methods.p_v_coupling.flow_scheme
  >>> flow_scheme.allowed_values()
  ['SIMPLE', 'SIMPLEC', 'PISO', 'Coupled']
  >>> flow_scheme.set_state("Coupled")
  >>> gradient_scheme = methods.gradient_scheme
  >>> gradient_scheme.allowed_values()
  ['green-gauss-node-based', 'green-gauss-cell-based', 'least-square-cell-based']
  >>> gradient_scheme.set_state("green-gauss-node-based")


Solution controls 
~~~~~~~~~~~~~~~~~

.. code:: python

  >>> controls = pyfluent.Controls(settings_source=solver)
  >>> p_v_controls = controls.p_v_controls
  >>> explicit_momentum_under_relaxation = p_v_controls.explicit_momentum_under_relaxation
  >>> explicit_momentum_under_relaxation.min()
  0
  >>> explicit_momentum_under_relaxation.max()
  1
  >>> explicit_momentum_under_relaxation.set_state(0.4)
  >>> flow_courant_number = p_v_controls.flow_courant_number
  >>> flow_courant_number.min()
  0
  >>> flow_courant_number.max()
  >>> flow_courant_number.set_state(0.3)


Create a report definition
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

  >>> rep_defs = pyfluent.ReportDefinitions(settings_source=solver)
  >>> surface_report_definitions = rep_defs.surface
  >>> defn_name = "outlet-temp-avg"
  >>> surface_report_definitions[defn_name] = {}
  >>> outlet_temperature = surface_report_definitions[defn_name]
  >>> outlet_temperature.report_type.set_state("surface-massavg")
  >>> outlet_temperature.field.set_state("temperature")


Initialize and solve 
~~~~~~~~~~~~~~~~~~~~

.. code:: python

  >>> solution = solver.settings.solution
  >>> solution.initialization.hybrid_initialize()
  >>> solution.run_calculation.iterate(iter_count=100)
