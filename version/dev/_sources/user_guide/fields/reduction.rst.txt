.. _ref_reduction_guide:

Reduction
=========

You can use reduction functions on Fluent data from one or across multiple remote Fluent sessions.
PyFluent provides both **functional** and **object-oriented** approaches to applying reduction functions.
While both are supported, the **functional approach** is emphasized for its flexibility,
particularly when working with multiple solver sessions.

Introduction to Reduction Functions
-----------------------------------

Reduction functions perform operations like computing averages, integrals, and sums over specified data locations,
such as areas or volumes.

To demonstrate the following examples, first initialize two separate solver sessions
with two separate examples case files as follows:

.. code-block:: python

    >>> import ansys.fluent.core as pyfluent
    >>> from ansys.fluent.core.solver.function import reduction
    >>> from ansys.fluent.core.examples import download_file

    >>> solver1 = pyfluent.launch_fluent(mode=pyfluent.FluentMode.SOLVER)
    >>> case_path = download_file(file_name="exhaust_system.cas.h5", directory="pyfluent/exhaust_system")
    >>> data_path = download_file(file_name="exhaust_system.dat.h5", directory="pyfluent/exhaust_system")
    >>> solver1.settings.file.read_case_data(file_name=case_path)

    >>> solver2 = pyfluent.launch_fluent(mode=pyfluent.FluentMode.SOLVER)
    >>> case_path = download_file("elbow1.cas.h5", "pyfluent/file_session")
    >>> data_path = download_file("elbow1.dat.h5", "pyfluent/file_session")
    >>> solver2.settings.file.read_case_data(file_name=case_path)

    >>> solver = solver1


Functional Usage
----------------

The **functional approach** is preferred for its:

1. **Conciseness**: Avoids deeply nested paths in code.
2. **Flexibility**: Supports reductions over multiple solver sessions or complex data sources.

Reduction functions can be accessed directly via the `reduction` module.
Here's how to set up a simple example:

.. code-block:: python

  >>> from ansys.fluent.core import VelocityInlets
  >>> # Compute the minimum of absolute pressure across multiple solvers
  >>> reduction.minimum(
    ...     expression="AbsolutePressure",
    ...     locations=[VelocityInlets(settings_source=solver) for solver in [solver1, solver2]],
    ... )
    101343.2241809384


Object-Oriented Usage
---------------------
The **object-oriented approach** leverages solver instance attributes
like `solver.fields.reduction` to perform reductions. While this approach
is intuitive for single-solver scenarios, it may be less suited to multi-solver or functional-style workflows.

To use reduction functions within a specific solver instance, initialize the solver and access the functions via `solver.fields.reduction`:

.. code-block:: python

  >>> solver.fields.reduction.area_average(
  ...     expression="AbsolutePressure",
  ...     locations=solver.settings.setup.boundary_conditions.velocity_inlet,
  ... )
  101957.2452989816

For convenience, context-aware reductions are also supported:

.. code-block:: python

  >>> solver.fields.reduction.area(locations=["inlet1"])
  0.002555675491754098

  >>> reduction.area(locations=["inlet1"], ctxt=solver)
  0.002555675491754098


Reduction Functions: Capabilities
----------------------------------

The following reduction functions are available in PyFluent:

- **Area**: Compute the total area.
.. code-block:: python

  >>> reduction.area(locations)

- **Area Average**: Compute the area-averaged value of an expression.
.. code-block:: python

  >>> reduction.area_average(expression, locations)

- **Area Integral**: Compute the integrated area of an expression.
.. code-block:: python

  >>> reduction.area_integral(expression, locations)

- **Volume**: Compute the total volume.
.. code-block:: python

  >>> reduction.volume(locations)

.. note::
   Only boundaries and face zones are allowed locations. It cannot be a user-defined surface.

- **Volume Average**: Compute the volume-averaged value of an expression.
.. code-block:: python

  >>> reduction.volume_average(expression, locations)

- **Volume Integral**: Compute the integrated volume of an expression.
.. code-block:: python

  >>> reduction.volume_integral(expression, locations)

- **Centroid**: Compute the geometric centroid.
.. code-block:: python

  >>> reduction.centroid(locations)

- **Force**: Compute the total force vector on specified walls.
.. code-block:: python

  >>> reduction.force(locations)

- **Pressure Force**: Compute the pressure force vector on specified walls.
.. code-block:: python

  >>> reduction.pressure_force(locations)

- **Viscous Force**: Compute the viscous force vector on specified walls.
.. code-block:: python

  >>> reduction.viscous_force(locations)

- **Moment**: Compute the moment vector about the specified point (which can be single-valued expression).
.. code-block:: python

  >>> reduction.moment(expression, locations)

- **Count**: Compute the total number of cells in specified locations.
.. code-block:: python

  >>> reduction.count(locations)

- **Count if**: Compute the conditional count.
.. code-block:: python

  >>> reduction.count_if(condition, locations)

- **Minimum**: Compute the minimum value of an expression.
.. code-block:: python

  >>> reduction.minimum(expression, locations)

- **Maximum**: Compute the maximum value of an expression.
.. code-block:: python

  >>> reduction.maximum(expression, locations)

- **Mass average**: Compute the mass-weighted average of an expression.
.. code-block:: python

  >>> reduction.mass_average(expression, locations)

.. note::
   Only boundaries and face zones are allowed locations. It cannot be a user-defined surface.

- **Mass integral**: Compute the integrated mass-weighted value of an expression.
.. code-block:: python

  >>> reduction.mass_integral(expression, locations)

.. note::
   Only boundaries and face zones are allowed locations. It cannot be a user-defined surface.

- **Mass flow average absolute**: Compute the mass-flow-weighted absolute average of an expression.
.. code-block:: python

  >>> reduction.mass_flow_average_absolute(expression, locations)

- **Mass flow average**: Compute the mass-flow-weighted average of an expression.
.. code-block:: python

  >>> reduction.mass_flow_average(expression, locations)

- **Mass flow integral**: Compute the integrated mass-flow-weighted value of an expression.
.. code-block:: python

  >>> reduction.mass_flow_integral(expression, locations)

- **Sum**: Compute the sum of an expression over locations.
.. code-block:: python

  >>> reduction.sum(expression, locations, weight)

- **Sum If**: Compute the conditional sum of an expression.
.. code-block:: python

  >>> reduction.sum_if(expression, condition, locations, weight)

.. note::
   The fluxes are evaluated on boundaries and face zones. So, for 'volume', 'mass_flow',
   'mass_average' and 'mass_integrated_average' the chosen location cannot be a
   user-defined surface.

Each function supports both the functional and object-oriented formats. See the following examples for typical use cases.

Examples
--------

**Example: Area Average**

Functional:

.. code-block:: python

  >>> reduction.area_average(
  ...     expression="AbsolutePressure",
  ...     locations=solver.setup.boundary_conditions.velocity_inlet,
  ... )
  101957.2452989816

Object-Oriented:

.. code-block:: python

  >>> solver.fields.reduction.area_average(
  ...     expression="AbsolutePressure",
  ...     locations=solver.settings.setup.boundary_conditions.velocity_inlet,
  ... )
  101957.2452989816

**Example: Minimum Across Multiple Solvers**

.. code-block:: python

  >>> reduction.minimum(
  ...     expression="AbsolutePressure",
  ...     locations=[
  ...         solver1.setup.boundary_conditions.pressure_outlet,
  ...         solver2.setup.boundary_conditions.pressure_outlet,
  ...     ],
  ... )
  101325.0

**Example: Using Boundary Abstractions**

.. code-block:: python

  >>> reduction.minimum(
  ...     expression="AbsolutePressure",
  ...     locations=[
  ...         VelocityInlets(settings_source=solver) for solver in [solver1, solver2]
  ...     ],
  ... )
  101343.2241809384

**Example: Geometric centroid of the velocity inlet 2**

.. code-block:: python

  >>> cent = reduction.centroid(
  >>>   locations=[solver.settings.setup.boundary_conditions.velocity_inlet["inlet2"]]
  >>> )
  >>> cent.array
  array([-2.85751176e-02, -7.92555538e-20, -4.41951790e-02])

**Example: Geometric centroid of the velocity inlets over multiple solvers**

.. code-block:: python

  >>> cent = reduction.centroid(
  >>>   locations=[VelocityInlets(settings_source=solver) for solver in [solver1, solver2]]
  >>> )
  >>> cent.array
  array([-0.35755706, -0.15706201, -0.02360788])


**Example: Sum with area as weight**

.. code-block:: python

  >>> reduction.sum(
  >>>   expression="AbsolutePressure",
  >>>   locations=[solver.settings.setup.boundary_conditions.velocity_inlet],
  >>>   weight="Area"
  >>> )
  80349034.56621933

**Example: Conditional sum**

.. code-block:: python

  >>> reduction.sum_if(
  >>>   expression="AbsolutePressure",
  >>>   condition="AbsolutePressure > 0[Pa]",
  >>>   locations=[solver.settings.setup.boundary_conditions.velocity_inlet],
  >>>   weight="Area"
  >>> )
  80349034.56621933

.. note:: Boundary abstractions such as `PressureOutlets` and `VelocityInlets` simplify workflows by removing the need to specify complex paths.
