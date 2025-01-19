Define materials
==================
PyFluent supports using :ref:`ref_solver_tui_commands` and 
:ref:`ref_settings` to define materials.

Use solver TUI commands
-----------------------
This example shows a comparison between the TUI command and the
Python code for defining the fluid material being modelled on a cell zone.

**TUI command**

.. code:: scheme

    /define/materials elbow-fluid yes water-liquid no no no no 0 no 0 no 0 no 0 no 0 no 1 no no no no no

**Python code**

.. code:: python

    import ansys.fluent.core as pyfluent

    solver = pyfluent.launch_fluent(precision="double", processor_count=2, mode="solver")
    solver.tui.file.read_case("file.cas.h5")
    solver.tui.define.materials.copy("fluid", "water-liquid")
    solver.tui.define.boundary_conditions.fluid(
        "elbow-fluid",
        "yes",
        "water-liquid",
        "no",
        "no",
        "no",
        "no",
        "0",
        "no",
        "0",
        "no",
        "0",
        "no",
        "0",
        "no",
        "0",
        "no",
        "1",
        "no",
        "no",
        "no",
        "no",
        "no",
    )

Use settings objects
--------------------
This example shows how you use :ref:`ref_settings` to define materials.

Copy material from database
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Python code**

.. code:: python

    solver.setup.materials.copy_database_material_by_name(type="fluid", name="water-liquid")
    solver.setup.cell_zone_conditions.fluid["elbow-fluid"].material = "water-liquid"

Create new material
~~~~~~~~~~~~~~~~~~~

**Python code**

.. code:: python

    mysolid = solver.setup.materials.solid.create("mysolid")
    mysolid.chemical_formula = "SiO2"
    mysolid.density.value = 2650
    mysolid.specific_heat.value = 1887
    mysolid.thermal_conductivity.value = 7.6

.. code:: python

    myfluid = solver.setup.materials.fluid.create("myfluid")
    myfluid.chemical_formula = "H2O"
    myfluid.density.value = 1000
    myfluid.specific_heat.value = 4186
    myfluid.thermal_conductivity.value = 0.6
    myfluid.viscosity.value = 1.03e-3