.. _ref_reduction_guide:

Reduction
=========

You can use reduction functions on Fluent data from one
or across multiple remote Fluent sessions.

Accessing reduction functions
-----------------------------

In order to access reduction function, import it and launch the Fluent solver.
Then, make boundary conditions data, etc. available (for example, by reading case files):

.. code-block:: python

  >>> import ansys.fluent.core as pyfluent
  >>> from ansys.fluent.core.examples import download_file
  >>> solver = pyfluent.launch_fluent(mode=pyfluent.FluentMode.SOLVER)
  >>> case_path = download_file("Static_Mixer_main.cas.h5", "pyfluent/static_mixer")
  >>> solver.settings.file.read(file_type="case", file_name=case_path)


Simple usage
------------

You can use the reduction functions from PyFluent simply by initializing the solution
and accessing the select functions with the required parameters.

For example, in the below case, do hybrid initialization of the solution and perform
an area-average of absolute pressure over the velocity inlet.

.. code-block:: python

  >>> solver.settings.solution.initialization.hybrid_initialize()
  >>> solver.fields.reduction.area_average(
  >>>   expression="AbsolutePressure",
  >>>   locations=solver.settings.setup.boundary_conditions.velocity_inlet,
  >>> )
  101325.0000000001

Similarly one can use the other functions available currently with PyFluent.

.. note::
   The fluxes are evaluated on boundaries and face zones. So, for 'volume', 'mass_flow',
   'mass_average' and 'mass_integrated_average' the chosen location cannot be a
   user-defined surface.

Usage of context
----------------

You can also use the context argument available with all the reduction functions
to mention the context instead of listing down the entire path of the locations,
and the path to the location is identified automatically.

For example, to calculate area of a location one has to do:

.. code-block:: python

  >>> solver.settings.solution.initialization.hybrid_initialize()
  >>> solver.fields.reduction.area(
  >>>   locations=[solver.settings.setup.boundary_conditions.velocity_inlet["inlet1"]]
  >>> )
  7.565427133371293e-07

Instead, one can use the context argument:

.. code-block:: python

  >>> solver.settings.solution.initialization.hybrid_initialize()
  >>> solver.fields.reduction.area(locations=["inlet1"], ctxt=solver)
  7.565427133371293e-07


Current capabilities
--------------------
At present, PyFluent allows the usage of the following reduction functions:

Area
~~~~
Compute the total area of the specified locations.

.. code-block:: python

  >>> reduction.area(locations)

Area average
~~~~~~~~~~~~
Compute the area averaged value of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.area_average(expression, locations)

Area integral
~~~~~~~~~~~~~
Compute the area integrated averaged of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.area_integral(expression, locations)

Volume
~~~~~~
Compute the total volume of the specified locations.

.. code-block:: python

  >>> reduction.volume(locations)

.. note::
   Only boundaries and face zones are allowed locations. It cannot be a user-defined surface.

Volume average
~~~~~~~~~~~~~~
Compute the volume averaged value of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.volume_average(expression, locations)

Volume integral
~~~~~~~~~~~~~~~
Compute the volume integrated averaged of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.volume_integral(expression, locations)

Centroid
~~~~~~~~
Compute the geometric centroid of the specified locations as a vector.

.. code-block:: python

  >>> reduction.centroid(locations)

Force
~~~~~
Compute the force acting on the locations specified (should be walls) as a vector.

.. code-block:: python

  >>> reduction.force(locations)

Pressure force
~~~~~~~~~~~~~~
Compute the pressure force acting on the locations specified (should be walls) as a vector.

.. code-block:: python

  >>> reduction.pressure_force(locations)

Viscous force
~~~~~~~~~~~~~
Compute the viscous force acting on the locations specified (should be walls) as a vector.

.. code-block:: python

  >>> reduction.viscous_force(locations)

Moment
~~~~~~
Compute the moment vector about the specified point (which can be single-valued expression)
for the specified locations.

.. code-block:: python

  >>> reduction.moment(expression, locations)

Count
~~~~~
Compute the total number of cells included in the specified locations.

.. code-block:: python

  >>> reduction.count(locations)

Count if
~~~~~~~~
Compute the total number of cells included in the specified locations if a condition is satisfied.

.. code-block:: python

  >>> reduction.count_if(condition, locations)

Minimum
~~~~~~~
Compute the minimum of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.minimum(expression, locations)

Maximum
~~~~~~~
Compute the maximum of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.maximum(expression, locations)

Mass average
~~~~~~~~~~~~
Compute the mass-weighted average value of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.mass_average(expression, locations)

.. note::
   Only boundaries and face zones are allowed locations. It cannot be a user-defined surface.

Mass integral
~~~~~~~~~~~~~
Compute the total mass-weighted value of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.mass_integral(expression, locations)

.. note::
   Only boundaries and face zones are allowed locations. It cannot be a user-defined surface.

Mass flow average absolute
~~~~~~~~~~~~~~~~~~~~~~~~~~
Compute the mass-flow-weighted absolute average value of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.mass_flow_average_absolute(expression, locations)


Mass flow average
~~~~~~~~~~~~~~~~~
Compute the mass-flow-weighted average value of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.mass_flow_average(expression, locations)

Mass flow integral
~~~~~~~~~~~~~~~~~~
Compute the total mass-flow-weighted value of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.mass_flow_integral(expression, locations)

Sum
~~~
Compute the sum of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.sum(expression, locations, weight)

Sum if
~~~~~~
Compute the sum of the specified expression over the specified locations if a condition is satisfied.

.. code-block:: python

  >>> reduction.sum_if(expression, condition, locations, weight)

Example use cases
-----------------
You can either calculate the area of one inlet or the combine area of all
the velocity inlets with the below examples:

.. code-block:: python

  >>> area_inlet_1 = solver.fields.reduction.area(
  >>>   locations=[solver.settings.setup.boundary_conditions.velocity_inlet["inlet1"]],
  >>> )
  7.565427133371293e-07

  >>> area_inlet = solver.fields.reduction.area(
  >>>   locations=[solver.settings.setup.boundary_conditions.velocity_inlet],
  >>> )
  1.513085401926681e-06

You can calculate the area average of "Absolute Pressure" over the entire set of velocity
inlets as shown:

.. code-block:: python

  >>> solver.fields.reduction.area_average(
  >>>   expression="AbsolutePressure",
  >>>   locations=solver.settings.setup.boundary_conditions.velocity_inlet,
  >>> )
  101325.0000000001

You can calculate the area integrated average of "Absolute Pressure" over the velocity inlet 1
as shown:

.. code-block:: python

  >>> solver.fields.reduction.area_integral(
  >>>   expression="AbsolutePressure",
  >>>   locations=[solver.settings.setup.boundary_conditions.velocity_inlet["inlet1"]],
  >>> )
  0.07665669042888468

You can calculate the geometric centroid of the velocity inlet 2 as shown:

.. code-block:: python

  >>> solver.fields.reduction.centroid(
  >>>   locations=[solver.settings.setup.boundary_conditions.velocity_inlet["inlet2"]]
  >>> )
  x: -0.001000006193379666
  y: -0.002999999999999999
  z: 0.001500047988232209

You can calculate the moment vector about a single-valued expression
for the specified locations as shown:

.. code-block:: python

  >>> solver.fields.reduction.moment(
  >>>   expression="Force(['wall'])",
  >>>   locations=[solver.settings.setup.boundary_conditions.velocity_inlet["inlet2"]]
  >>> )
  [ 1.15005117e-24,  1.15218653e-24, -6.60723735e-20]

You can calculate the moment vector about the specified point for the
specified locations as shown:

.. code-block:: python

  >>> solver.fields.reduction.moment(
  >>>   expression="['inlet1']",
  >>>   locations=[solver.settings.setup.boundary_conditions.velocity_inlet["inlet2"]]
  >>> )
  [ 1.15005117e-24,  1.15218653e-24, -6.60723735e-20]

One can calculate sum of Absolute Pressure over all nodes of velocity inlet with area as weight.

.. code-block:: python

  >>> solver.fields.reduction.sum(
  >>>   expression="AbsolutePressure",
  >>>   locations=[solver.settings.setup.boundary_conditions.velocity_inlet],
  >>>   weight="Area"
  >>> )
  20670300.0

You can also calculate the sum with a condition:

.. code-block:: python

  >>> solver.fields.reduction.sum_if(
  >>>   expression="AbsolutePressure",
  >>>   condition="AbsolutePressure > 0[Pa]",
  >>>   locations=[solver.settings.setup.boundary_conditions.velocity_inlet],
  >>>   weight="Area"
  >>> )
  20670300.0
