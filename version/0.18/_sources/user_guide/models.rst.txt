Define models
===============
PyFluent supports using :ref:`ref_solver_tui_commands` and :ref:`ref_settings`
to define models.

Use solver TUI commands
-----------------------
The examples in this section show how you use :ref:`ref_solver_tui_commands` to define models.

Define energy model
~~~~~~~~~~~~~~~~~~~
This example shows a comparison between the TUI command and the
Python code for enabling and disabling the energy model.

**TUI command**

.. code:: scheme

    /define/models/energy yes no no no yes

**Python code**

.. code:: python

    import ansys.fluent.core as pyfluent

    solver = pyfluent.launch_fluent(precision="double", processor_count=2, mode="solver")
    solver.tui.file.read_case("file.cas.h5")
    solver.tui.define.models.energy("yes", "no", "no", "no", "yes")

Define viscous model
~~~~~~~~~~~~~~~~~~~~
This example shows a comparison between the TUI command and the
Python code for enabling and disabling various viscous models.

**TUI command**

.. code:: scheme

    /define/models/viscous/laminar yes
    /define/models/viscous/kw-sst yes
    /define/models/viscous/ke-standard yes

**Python code**

.. code:: python

    solver.tui.define.models.viscous.laminar("yes")
    solver.tui.define.models.viscous.kw_sst("yes")
    solver.tui.define.models.viscous.ke_standard("yes")

Define radiation model
~~~~~~~~~~~~~~~~~~~~~~
This example shows a comparison between the TUI command and the
Python code for enabling and disabling various radiation models.

**TUI command**

.. code:: scheme

    /define/models/radiation/s2s yes
    /define/models/radiation/p1 yes

**Python code**

.. code:: python

    solver.tui.define.models.radiation.s2s("yes")
    solver.tui.define.models.radiation.p1("yes")

Define multiphase model
~~~~~~~~~~~~~~~~~~~~~~~
This example shows a comparison between the TUI command and the
Python code for defining different multiphase models.

**TUI command**

.. code:: scheme

    /define/models/multiphase/model vof
    /define/models/multiphase/model eulerian
    /define/models/multiphase/model mixture
    /define/models/multiphase/model wetsteam

**Python code**

.. code:: python

    solver.tui.define.models.multiphase.model("vof")
    solver.tui.define.models.multiphase.model("eulerian")
    solver.tui.define.models.multiphase.model("mixture")
    solver.tui.define.models.multiphase.model("wetsteam")

Use settings objects
--------------------
The examples in this section show how you use :ref:`ref_settings` to
define models.

Enable energy model
~~~~~~~~~~~~~~~~~~~

**Python code**

.. code:: python

    solver.setup.models.energy.enabled = True

Enable viscous model
~~~~~~~~~~~~~~~~~~~~

**Python code**

.. code:: python

    solver.setup.models.viscous.k_epsilon_model.enabled = True
    solver.setup.models.viscous.k_omega_model.enabled = True
