Apply solution settings
=======================

PyFluent allows you to use :ref:`ref_solver_tui_commands` and
:ref:`ref_settings` to apply solution settings, initialize, and solve.

Use solver TUI commands
-----------------------
The examples on this page show how you use :ref:`ref_solver_tui_commands` to
apply solution settings.

Select solution method 
~~~~~~~~~~~~~~~~~~~~~~
This example shows a comparison between the TUI command and the Python code for
selecting the pressure velocity coupling scheme and setting the gradient
options. Five solution methods (Index-Model) are available: 20-SIMPLE,
21-SIMPLEC, 22-PISO, 24-Coupled, and 25-Fractional Step.

**TUI command**

.. code:: scheme

    /solve/set/p-v-coupling 24
    /solve/set/gradient-scheme yes
    /solve/set/gradient-scheme no yes 

**Python code**

.. code:: python

    import ansys.fluent.core as pyfluent

    solver = pyfluent.launch_fluent(precision="double", processor_count=2, mode="solver")
    solver.tui.file.read_case("file.cas.h5")
    solver.tui.solve.set.p_v_coupling(24)  # Coupled
    solver.tui.solve.set.gradient_scheme("yes")  # Green-Gauss Node Based
    solver.tui.solve.set.gradient_scheme("no", "yes")  # Least Squares Cell Based
    
Select solution controls 
~~~~~~~~~~~~~~~~~~~~~~~~
This example shows a comparison between the TUI command and the Python code for
selecting pressure velocity controls.

**TUI command**

.. code:: scheme

    /solve/set/p-v-controls 0.3 0.4

**Python code**

.. code:: python

    solver.tui.solve.set.p_v_controls(0.3,0.4) # Momentum and Pressure

Create report definition
~~~~~~~~~~~~~~~~~~~~~~~~
This example shows a comparison between the TUI command and the Python code for
creating a report definition.

**TUI command**

.. code:: scheme

    /solve/report-definitions outlet-temp-avg surface-massavg field temperature surface-names outlet () quit

**Python code**

.. code:: python

    solver.tui.solve.report_definitions.add(
        "outlet-temp-avg",
        "surface-massavg",
        "field",
        "temperature",
        "surface-names",
        "outlet",
        "()",
        "quit",
    )

Initialize and solve 
~~~~~~~~~~~~~~~~~~~~
This example shows a comparison between the TUI command and the Python code for
initializing and performing a specified number of iterations.

**TUI command**

.. code:: scheme

    /solve/initialize/hyb-initialization
    /solve/iterate 100

**Python code**

.. code:: python

    solver.tui.solve.initialize.hyb_initialization()
    solver.tui.solve.iterate(100)

Use settings objects
--------------------
This example shows how you use :ref:`ref_settings` to apply solution settings.

**Python code**

.. code:: python

    solver.solution.initialization.hybrid_initialize()
    solver.solution.run_calculation.iterate(number_of_iterations=150)
