.. _ref_reduction:

Reduction
=========

You can use reduction functions on Fluent data from one
or across multiple remote Fluent sessions.

Accessing reduction functions
-----------------------------

In order to access reduction function, import it and launch the fluent solver.
Then, make boundary conditions data, etc. available (for example, by reading case files):

.. code-block:: python

  >>> from ansys.fluent.core.solver.function import reduction
  >>> import ansys.fluent.core as pyfluent
  >>> from ansys.fluent.core.examples import download_file
  >>> solver = pyfluent.launch_fluent(mode="solver")
  >>> case_path = download_file("Static_Mixer_main.cas.h5", "pyfluent/static_mixer")
  >>> solver.file.read(file_type="case", file_name=case_path)


Simple usage
------------

You can use the reduction functions from PyFluent simply by initializing the solution
and accessing the select functions with the required parameters.

For example, in the below case, do hybrid initialization of the solution and perform
an area-average of absolute pressure over the velocity inlet.

.. code-block:: python

  >>> solver.solution.initialization.hybrid_initialize()
  >>> reduction.area_average(
  >>>   expr="AbsolutePressure",
  >>>   locations=solver.setup.boundary_conditions.velocity_inlet,
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

  >>> solver.solution.initialization.hybrid_initialize()
  >>> reduction.area(
  >>>   locations=[solver.setup.boundary_conditions.velocity_inlet["inlet1"]]
  >>> )
  7.565427133371293e-07

Instead, one can use the context argument:

.. code-block:: python

  >>> solver.solution.initialization.hybrid_initialize()
  >>> reduction.area(locations=["inlet1"], ctxt=solver)
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

Area integrated average
~~~~~~~~~~~~~~~~~~~~~~~
Compute the area integrated averaged of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.area_integrated_average(expression, locations)

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

Volume integrated average
~~~~~~~~~~~~~~~~~~~~~~~~~
Compute the volume integrated averaged of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.volume_integrated_average(expression, locations)

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

Mass integrated average
~~~~~~~~~~~~~~~~~~~~~~~
Compute the total mass-weighted value of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.mass_integrated_average(expression, locations)

.. note::
   Only boundaries and face zones are allowed locations. It cannot be a user-defined surface.

Mass flow
~~~~~~~~~
Compute the total mass flow rate of the specified locations.

.. code-block:: python

  >>> reduction.mass_flow(locations)

.. note::
   Only boundaries and face zones are allowed locations. It cannot be a user-defined surface.

Mass flow average
~~~~~~~~~~~~~~~~~
Compute the mass-flow-weighted average value of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.mass_flow_average(expression, locations)

Mass flow integrated average
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Compute the total mass-flow-weighted value of the specified expression over the specified locations.

.. code-block:: python

  >>> reduction.mass_flow_integrated_average(expression, locations)


Example use cases
-----------------
You can either calculate the area of one inlet or the combine area of all
the velocity inlets with the below examples:

.. code-block:: python

  >>> area_inlet_1 = reduction.area(
  >>>   locations=[solver.setup.boundary_conditions.velocity_inlet["inlet1"]],
  >>> )
  7.565427133371293e-07

  >>> area_inlet = reduction.area(
  >>>   locations=[solver.setup.boundary_conditions.velocity_inlet],
  >>> )
  1.513085401926681e-06

You can calculate the area average of "Absolute Pressure" over the entire set of velocity
inlets as shown:

.. code-block:: python

  >>> reduction.area_average(
  >>>   expr="AbsolutePressure",
  >>>   locations=solver.setup.boundary_conditions.velocity_inlet,
  >>> )
  101325.0000000001

You can calculate the area integrated average of "Absolute Pressure" over the velocity inlet 1
as shown:

.. code-block:: python

  >>> reduction.area_integrated_average(
  >>>   expr="AbsolutePressure",
  >>>   locations=[solver.setup.boundary_conditions.velocity_inlet["inlet1"]],
  >>> )
  0.07665669042888468

You can calculate the geometric centroid of the velocity inlet 2 as shown:

.. code-block:: python

  >>> reduction.centroid(
  >>>   locations=[solver.setup.boundary_conditions.velocity_inlet["inlet2"]]
  >>> )
  [-0.001000006193379666, -0.002999999999999999, 0.001500047988232209]

You can calculate the moment vector about a single-valued expression
for the specified locations as shown:

.. code-block:: python

  >>> reduction.moment(
  >>>   expr="Force(['wall'])",
  >>>   locations=[solver.setup.boundary_conditions.velocity_inlet["inlet2"]]
  >>> )
  [ 1.15005117e-24,  1.15218653e-24, -6.60723735e-20]

You can calculate the moment vector about the specified point for the
specified locations as shown:

.. code-block:: python

  >>> reduction.moment(
  >>>   expr="['inlet1']",
  >>>   locations=[solver.setup.boundary_conditions.velocity_inlet["inlet2"]]
  >>> )
  [ 1.15005117e-24,  1.15218653e-24, -6.60723735e-20]

.. currentmodule:: ansys.fluent.core.solver.function

.. autosummary::
    :toctree: _autosummary
    :template: flobject-module-template.rst
    :recursive:

    reduction