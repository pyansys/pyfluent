Define boundary conditions
==========================
PyFluent supports using :ref:`ref_solver_tui_commands`
and :ref:`ref_settings` to define boundary conditions.

Use solver TUI commands
-----------------------
The examples in this section show how you use :ref:`ref_solver_tui_commands`
to define boundary conditions.

Define boundary conditions
~~~~~~~~~~~~~~~~~~~~~~~~~~
This example shows a comparison between the TUI command and the
Python code for defining velocity boundary conditions at inlets.

**TUI command**

.. code:: scheme

    /define/boundary-counditions/set/velocity-inlet cold-inlet () vmag no 0.4 quit
    /define/boundary-counditions/set/velocity-inlet cold-inlet () ke-spec no no no yes quit
    /define/boundary-counditions/set/velocity-inlet cold-inlet() cold-inlet () turb-intensity 5 quit
    /define/boundary-counditions/set/velocity-inlet cold-inlet () cold-inlet () turb-hydraulic-diam 4 quit
    /define/boundary-counditions/set/velocity-inlet cold-inlet () cold-inlet () temperature no 293.15 quit

**Python code**

.. code:: python

    import ansys.fluent.core as pyfluent

    solver = pyfluent.launch_fluent(precision="double", processor_count=2, mode="solver")
    solver.tui.file.read_case("file.cas.h5")
    solver.tui.define.boundary_conditions.set.velocity_inlet(
        "cold-inlet", (), "vmag", "no", 0.4, "quit"
    )
    solver.tui.define.boundary_conditions.set.velocity_inlet(
        "cold-inlet", (), "ke-spec", "no", "no", "no", "yes", "quit"
    )
    solver.tui.define.boundary_conditions.set.velocity_inlet(
        "cold-inlet", (), "turb-intensity", 5, "quit"
    )
    solver.tui.define.boundary_conditions.set.velocity_inlet(
        "cold-inlet", (), "turb-hydraulic-diam", 4, "quit"
    )
    solver.tui.define.boundary_conditions.set.velocity_inlet(
        "cold-inlet", (), "temperature", "no", 293.15, "quit"
    )

Copy boundary conditions
~~~~~~~~~~~~~~~~~~~~~~~~
This example shows a comparison between the TUI command and the Python code for
copying boundary conditions to other zones.

**TUI command**

.. code:: scheme

    /define/boundary-conditions/copy-bc cold-inlet hot-inlet ()

**Python code**

.. code:: python

    solver.tui.define.boundary_conditions.copy_bc('cold-inlet','hot-inlet','()')

List zones
~~~~~~~~~~
This example shows a comparison between the TUI command and the Python code for
printing the types and IDs of all zones to the Fluent console.

**TUI command**

.. code:: scheme

    /define/boundary-conditions/list-zones

**Python code**

.. code:: python

    solver.tui.define.boundary_conditions.list_zones()

Modify cell zone conditions
~~~~~~~~~~~~~~~~~~~~~~~~~~~
This example shows a comparison between the TUI command and the Python code for
modifying cell zone conditions.

**TUI command**

.. code:: scheme

    /define/boundary-conditions/fluid elbow-fluid no no no no no 0 no 0 no 0 no 0 no 0 no 1 no yes yes no no no

**Python code**

.. code:: python

    # Enabling Laminar Zone
    solver.tui.define.boundary_conditions.fluid(
        "elbow-fluid",
        "no",
        "no",
        "no",
        "no",
        "no",
        0,
        "no",
        0,
        "no",
        0,
        "no",
        0,
        "no",
        0,
        "no",
        1,
        "no",
        "yes",
        "yes",
        "no",
        "no",
        "no",
    )

Use settings objects
----------------------
The examples in this section show how you use :ref:`ref_settings` to define
boundary conditions.

Define boundary conditions
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Python code**

.. code:: python

    solver.setup.boundary_conditions.velocity_inlet["cold-inlet"].vmag = {
        "option": "constant or expression",
        "constant": 0.4,
    }
    solver.setup.boundary_conditions.velocity_inlet[
        "cold-inlet"
    ].ke_spec = "Intensity and Hydraulic Diameter"
    solver.setup.boundary_conditions.velocity_inlet["cold-inlet"].turb_intensity = 5
    solver.setup.boundary_conditions.velocity_inlet[
        "cold-inlet"
    ].turb_hydraulic_diam = "4 [in]"
    solver.setup.boundary_conditions.velocity_inlet["cold-inlet"].t = {
        "option": "constant or expression",
        "constant": 293.15,
    }

Modify cell zone conditions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Python code**

.. code:: python

    # Enabling Laminar Zone
    solver.setup.cell_zone_conditions.fluid["elbow-fluid"] = {"laminar": True}
