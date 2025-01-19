.. _ref_user_guide:

==========
User guide
==========
Anyone who wants to use PyFluent can import its Python modules and develop
Python code to control and monitor Ansys Fluent.

..
   This toctree must be a top level index to get it to show up in
   pydata_sphinx_theme

.. toctree::
   :maxdepth: 1
   :hidden:

   launching_ansys_fluent
   specify_file_paths
   tui_commands
   meshing_workflow/index
   general_settings
   solver_settings
   models
   materials
   boundary_conditions
   solution


Overview
--------
You use the :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>` method
to launch an instance of Fluent that runs as a server in the background.

You can launch Fluent in solution mode with this code:

.. code:: python

    from ansys.fluent.core import launch_fluent

    solver = launch_fluent(mode="solver")

You can launch Fluent in meshing mode with this code:

.. code:: python

    from ansys.fluent.core import launch_fluent

    meshing = launch_fluent(mode="meshing")


For more information, see :ref:`ref_user_guide_launch`
and :ref:`ref_launcher`.

You can use PyFluent to create and initialize multiple, independent session
objects. Each session object provides full access to the Fluent components
relevant to the session's current mode (solution or meshing).

Solution mode session
---------------------
A solution mode session has an active ``solver`` object that provides two
distinct interfaces to the solver:

- ``tui`` object
- ``root`` object

For general guidance on using these two objects, see
:ref:`ref_user_guide_solver_settings`.

Solver ``tui`` object
~~~~~~~~~~~~~~~~~~~~~
The solver ``tui`` object is a complete Python exposure of the Fluent solver TUI
(text user interface). This object allows straightforward execution of solver
commands and modification of solve settings in a manner that is familiar to
existing Fluent users:

.. code:: python

    tui = solver.tui

    tui.file.read_case("pipe.cas.h5")

    tui.define.models.energy("yes")

For the full hierarchy under the solver ``tui`` object, see :ref:`ref_solver_tui_commands`.
For general guidance on using TUI commands, see :ref:`ref_user_guide_tui_commands`.

Solver ``root`` object
~~~~~~~~~~~~~~~~~~~~~~
The solver ``root`` object exposes most of the solver capabilities covered by
the solver ``tui`` object and provides significant additional interface features
that are not possible via the ``tui`` object:

.. code:: python

    solver.file.read(file_type="case", file_name="pipe.cas.h5")

    solver.setup.models.energy.enabled = True

    energy_is_enabled = solver.setup.models.energy.enabled()

For the full hierarchy under the solver ``root`` object, see :ref:`ref_solver_tui`.
For additional interface features, see :ref:`ref_settings`.

Meshing mode session
--------------------
A meshing mode session has an active ``meshing`` object that provides two
distinct interfaces to the mesher:

- ``tui`` object
- meshing workflow, which consists of :ref:`meshing <ref_meshing_datamodel_meshing>` and :ref:`workflow <ref_meshing_datamodel_workflow>` properties and the
  :ref:`PartManagement <ref_meshing_datamodel_PartManagement>` and :ref:`PMFileMangement <ref_meshing_datamodel_PMFileManagement>` classes

Meshing ``tui`` object
~~~~~~~~~~~~~~~~~~~~~~
The meshing ``tui`` object is a complete Python exposure of the Fluent meshing
TUI (text user interface). This object allows straightforward execution of
meshing commands and modification of meshing settings in a manner that is
familiar to existing Fluent users:

.. code:: python

    tui = meshing_session.tui

    tui.mesh.prepare_for_solve("yes")

    tui.file.write_case("pipe.cas.h5")

For the full hierarchy under the meshing ``tui`` object, see
:ref:`ref_meshing_tui`. For general guidance on using TUI commands, see
:ref:`ref_user_guide_tui_commands`.

``Meshing`` and ``Workflow`` properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``meshing`` object has :ref:`meshing <ref_meshing_datamodel_meshing>` and :ref:`workflow <ref_meshing_datamodel_workflow>` properties that together
provide access to Fluent's meshing workflows. This interface is consistent with
the Python meshing workflow interface that Fluent meshing exposes directly:

.. code:: python

    workflow = meshing_session.workflow

    workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

    import_geometry = workflow.TaskObject["Import Geometry"]

    import_geometry.Arguments = {"FileName":"pipe.scdoc.pmdb"}

    import_geometry.Execute()

    meshing = meshing_session.meshing

    meshing.GlobalSettings.LengthUnit.set_state("mm")

For additional examples, see :ref:`ref_user_guide_meshing_workflows` for
classic meshing workflow interface that appear in journals or
:ref:`ref_user_guide_new_meshing_workflows` for the new object oriented
meshing workflow interface.
For information on the full interface, see :ref:`ref_meshing_datamodel`.

Search for Fluent settings or commands
--------------------------------------
A global search method is available for Fluent settings or commands:

.. code:: python

    >>> import ansys.fluent.core as pyfluent
    >>> pyfluent.search("geometry")
    <meshing_session>.tui.file.import_.cad_geometry (Command)
    <meshing_session>.tui.display.update_scene.select_geometry (Command)
    <meshing_session>.meshing.ImportGeometry (Command)
    <meshing_session>.meshing.LoadCADGeometry (Command)
    <solver_session>.tui.solve.initialize.compute_defaults.geometry (Command)
    <solver_session>.tui.report.reference_values.compute.geometry (Command)
    <solver_session>.tui.define.geometry (Command)
    <solver_session>.tui.mesh.geometry (Object)
    <solver_session>.setup.boundary_conditions.geometry["<name>"] (Object)
    <solver_session>.setup.geometry (Object)
    <solver_session>.solution.report_definitions.surface["<name>"].geometry (Parameter)
    <solver_session>.solution.report_definitions.volume["<name>"].geometry (Parameter)
    <solver_session>.results.graphics.mesh["<name>"].geometry (Parameter)
    <solver_session>.results.graphics.contour["<name>"].geometry (Parameter)

See :ref:`ref_search` for full documentation of the search method.

Session object
--------------
In either a solution or meshing mode session, the ``session`` object provides a
more direct interaction via its ``scheme_eval`` attribute:

.. code:: python

    unsteady = solver.scheme_eval.scheme_eval("(rp-unsteady?)")

The argument to the ``scheme_eval`` attribute is a string that contains any
scheme code that can be executed in Fluent for the current mode.

Surface field and mesh data services are available in solution mode only via the
``field_data`` object attribute of the session object:

.. code:: python

    surface_data = solver.field_data.get_fields()

For more information, see :ref:`ref_field_data`.

The connection status of any session can be verified with:

.. code:: python

    health = solver.health_check.status()

``"SERVING"`` is returned if and only if the connection is healthy.

Streaming
---------
Streaming of a Fluent transcript is automatically started by default. You can
stop and start the streaming of a transcript manually with:

.. code:: python

    solver.transcript.stop()

    solver.transcript.start()

You can enable and disable the streaming of events pertaining to various solver
event types via the ``events`` attribute of a solution mode session:

.. code:: python

    solver.events.start()

For more information, see :ref:`ref_events`.

.. _ref_logging_user_guide:

Logging to file and debugging
-----------------------------
PyFluent logging to file is by default disabled. Logging can be enabled with:

.. code:: python

    import ansys.fluent.core as pyfluent
    pyfluent.logging.enable()

the last command being equivalent to ``pyfluent.logging.enable('DEBUG')``,
using the default PyFluent logging level.
See the possible logging level values in
`<https://docs.python.org/3/library/logging.html#logging-levels>`_.

PyFluent by default creates and logs to a file named ``pyfluent.log`` in the
current working directory (see :func:`ansys.fluent.core.logging.enable` for more details).

The global logging level of PyFluent, after logging has been enabled,
can also be controlled with:

.. code:: python

    pyfluent.logging.set_global_level('DEBUG')

which is equivalent to ``pyfluent.logging.set_global_level(10)``.

See also :func:`ansys.fluent.core.logging.enable`,
:func:`ansys.fluent.core.logging.list_loggers` and
:func:`ansys.fluent.core.logging.set_global_level`.

PyFluent loggers use the standard Python logging library, for more details see
`<https://docs.python.org/3/library/logging.html>`_.

Additional documentation about the PyFluent logging module is available
in the :ref:`logging module documentation <ref_logging>`.

.. _ref_logging_env_var:

Environment variable
~~~~~~~~~~~~~~~~~~~~
Global logging can also be enabled automatically on PyFluent startup through the
environment variable ``PYFLUENT_LOGGING``, which can be set for example
to values ``DEBUG`` or ``10``. Setting ``PYFLUENT_LOGGING`` to ``0`` or ``OFF`` does
not initialize logging to file on startup, the same behavior as if this variable was
not set.




