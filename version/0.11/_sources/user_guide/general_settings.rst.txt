Applying general settings
=========================
PyFluent supports using both :ref:`ref_solver_tui_commands` and 
:ref:`ref_settings` to apply general settings.

The examples in this topic show how you use :ref:`ref_solver_tui_commands`
to run solver meshing commands and set up units.

Check the mesh
--------------
This example shows a comparison between the TUI command and the
Python code for performing mesh consistency checks and displaying a
report in the console. This report lists domain extents, volume statistics,
face area statistics, any warnings, and information about failures.
The level of information shown depends on the setting specified for
the verbosity (level 0 to 3).

**TUI command**

.. code:: scheme

    /mesh/check
    /mesh/check-verbosity 1

**Python code**

.. code:: python

    import ansys.fluent.core as pyfluent
    solver = pyfluent.launch_fluent(precision='double', processor_count=2, mode="solver")
    solver.tui.file.read_case('file.cas.h5')
    solver.tui.mesh.check()

Report mesh quality
-------------------
This example shows a comparison between the TUI command and the
Python code for displaying information about the quality of the mesh in the
console, including the minimum orthogonal quality and maximum aspect ratio.

**TUI command**

.. code:: scheme

    /mesh/quality

**Python code**

.. code:: python

    solver.tui.mesh.quality()

Scale mesh
------------
This example shows a comparison between the TUI command and the
Python code for scaling the mesh in each of the active Cartesian
coordinate directions.

**TUI command**

.. code:: scheme

    /mesh/scale 1 1 1

**Python code**

.. code:: python

    solver.tui.mesh.scale(1,1,1)

Define units
--------------
The following example shows a comparison between the TUI command and the
Python code for setting the unit conversion factors.

**TUI command**

.. code:: scheme

    /define/units length 'in'

**Python code**

.. code:: python

    solver.tui.define.units('length', 'in')