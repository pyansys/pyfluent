.. _ref_session_guide:

.. vale Google.Spacing = NO

Using PyFluent sessions
=======================

You can obtain a PyFluent session object by calling either of the functions, :func:`launch_fluent()
<ansys.fluent.core.launcher.launcher.launch_fluent>` or :func:`connect_to_fluent() <ansys.fluent.core.launcher.launcher.connect_to_fluent>`. 


.. code:: python

  >>> import ansys.fluent.core as pyfluent
  >>> from ansys.fluent.core.examples import download_file
  >>> case_file_name = download_file("mixing_elbow.cas.h5", "pyfluent/mixing_elbow")
  >>> data_file_name = download_file("mixing_elbow.dat.h5", "pyfluent/mixing_elbow")
  >>> solver = pyfluent.launch_fluent(case_data_file_name=case_file_name)


Solution mode sessions
----------------------

The above :obj:`~ansys.fluent.core.session_solver.Solver` session object exposes a variety of Python child objects that provide access to the data
and functions of the connected Fluent solver. A consistent interface style is maintained across those Python objects
and each object adopts a specific responsibility that is reflected in its particular interface. For instance,
the :obj:`~ansys.fluent.core.session_solver.Solver` session provides child objects for solver settings and field data access respectively.
You can see these ``fields`` and ``settings`` children by executing ``dir(solver)``. You can discover the
children of ``fields`` and ``settings`` by calling ``dir(solver.fields)`` and ``dir(solver.settings)`` respectively,
and so on:

.. code:: python

  >>> solver_children = dir(solver)
  >>> settings = solver.settings
  >>> settings_children = dir(settings)
  >>> fields = solver.fields
  >>> fields_children = dir(fields)


You can call the Python ``help()`` function to find out more about each item in PyFluent. 

.. code:: python

  >>> help(solver.settings.file.read_case)


You can create additional PyFluent sessions. The following code creates a :obj:`~ansys.fluent.core.session_meshing.Meshing` mode
session that starts a second Fluent instance and is independent of your PyFluent :obj:`~ansys.fluent.core.session_solver.Solver` session.

.. code:: python

  >>> import ansys.fluent.core as pyfluent
  >>> meshing = pyfluent.launch_fluent(mode=pyfluent.FluentMode.MESHING)


A uniform interface exists across solver settings objects. For instance,
``get_state()``, ``set_state()`` and ``is_active()`` are ubiquitous methods,
and ``allowed_values()``, ``min()`` and ``max()`` are found on relevant items.
Here are some examples using the ``viscous`` and ``discrete_phase`` models.

.. code:: python

  >>> viscous_model = settings.setup.models.viscous.model
  >>> viscous_model.get_state()
	'k-omega'
  >>> from pprint import pprint
  >>> pprint(viscous_model.allowed_values())
	['inviscid',
	 'laminar',
	 'k-epsilon',
	 'k-omega',
	 'mixing-length',
	 'spalart-allmaras',
	 'k-kl-w',
	 'transition-sst',
	 'reynolds-stress',
	 'scale-adaptive-simulation',
	 'detached-eddy-simulation',
	 'large-eddy-simulation']
  >>> viscous_model.set_state("laminar")
  >>> viscous_model.get_state()
    'laminar'
  >>> discrete_phase = settings.setup.models.discrete_phase
  >>> discrete_phase.is_active()
    True
  >>> max_num_refinements = discrete_phase.numerics.tracking.accuracy_control.max_num_refinements
  >>> max_num_refinements.get_state()
	20
  >>> max_num_refinements.min(), max_num_refinements.max()
   (0, 1000000)
  

Some items in the solver settings object tree are methods that you call to request a particular
action in Fluent:

.. code:: python

  >>> solver.settings.solution.run_calculation.iterate(iter_count=100)


Note: You can find out more about solver settings objects here:
:ref:`ref_solver_settings_guide`. 

Objects under ``fields`` provide an interface with a style similar to
that of the ``settings`` objects:

.. code:: python

  >>> field_data = fields.field_data
  >>> transaction = field_data.new_transaction()
  >>> add_scalar_fields = transaction.add_scalar_fields_request
  >>> allowed_field_names = add_scalar_fields.field_name.allowed_values()
  >>> pprint(allowed_field_names[:min([len(allowed_field_names), 5])])
  ['abs-angular-coordinate',
   'absolute-pressure',
   'angular-coordinate',
   'anisotropic-adaption-cells',
   'aspect-ratio']
  >>> add_scalar_fields.surface_names.allowed_values()
  ['cold-inlet', 'hot-inlet', 'outlet', 'symmetry-xyplane', 'wall-elbow', 'wall-inlet']
  >>> add_scalar_fields(field_name='absolute-pressure', surfaces=['cold-inlet', 'hot-inlet', 'outlet', 'symmetry-xyplane', 'wall-elbow', 'wall-inlet'])
  >>> pressure_fields = transaction.get_fields()
  >>> solver.fields.reduction.sum_if(
  >>>     expression="AbsolutePressure",
  >>>     condition="AbsolutePressure > 0[Pa]",
  >>>     locations=[settings.setup.boundary_conditions.velocity_inlet["cold-inlet"]],
  >>>     weight="Area",
  >>> )
  15401477.28604886


Meshing mode sessions
---------------------

Meshing mode also provides an interface style that is consistent with the above interactions. Here is some
task-based meshing workflow code:

.. code:: python

  >>> watertight = meshing.watertight()
  >>> from ansys.fluent.core.examples import download_file
  >>> import_file_name = examples.download_file('mixing_elbow.pmdb', 'pyfluent/mixing_elbow')
  >>> import_geometry = watertight.import_geometry
  >>> import_geometry.file_name.set_state(import_file_name)
  >>> length_unit = import_geometry.length_unit
  >>> length_unit.get_state()
   "mm"
  >>> length_unit.allowed_values()
   ["m", "cm", "mm", "in", "ft", "um", "nm"]
  >>> length_unit.set_state("mm")
  >>> import_geometry()


Note: You can find out more about meshing workflows here:
:ref:`ref_new_meshing_workflows_guide`.

A :obj:`~ansys.fluent.core.session_meshing.Meshing` mode session object exposes additional child objects. For instance, ``meshing``
has ``fields`` and ``events`` children. Each has the same interface as the identically named
child of the :obj:`~ansys.fluent.core.session_solver.Solver` session object respectively.

You can also create a :obj:`~ansys.fluent.core.session_pure_meshing.PureMeshing` session:


.. code:: python

  >>> import ansys.fluent.core as pyfluent
  >>> pure_meshing = pyfluent.launch_fluent(mode=pyfluent.FluentMode.PURE_MESHING)


The only difference between the two meshing session types is that a pure session cannot be
switched to solution mode directly. The existence of the pure session type promotes creation
of minimal server images, which becomes significant in the context of containerization.


Switching between sessions
--------------------------

You switch between meshing and solution modes by calling the :obj:`switch_to_solver() <ansys.fluent.core.session_meshing.Meshing.switch_to_solver>` method.


.. code:: python

  >>> switched_solver = meshing.switch_to_solver()


The ``switched_solver`` session uses the same Fluent instance that was previously used by the
:obj:`~ansys.fluent.core.session_meshing.Meshing` session, which is now unusable.

A similar action with the :obj:`~ansys.fluent.core.session_pure_meshing.PureMeshing` session raises an exception:


.. code:: python

  >>> failed_solver = pure_meshing.switch_to_solver() # raises an AttributeError!


Note: there is no method to switch back to meshing mode from solution mode.


Sharing cases between sessions
------------------------------

An alternative to mode switching is to transfer your case between sessions, an operation
that's allowed both for pure and for regular meshing sessions:


.. code:: python

  >>> pure_meshing.transfer_mesh_to_solvers(solvers=[solver, switched_solver])


Ending PyFluent sessions
------------------------

Just as PyFluent session objects start and exist independently within a single Python interpreter session,
each session can be ended independently of the others. Calling the ``exit()`` method on the :obj:`~ansys.fluent.core.session_solver.Solver` and
:obj:`~ansys.fluent.core.session_pure_meshing.PureMeshing` session objects ends those PyFluent sessions and terminates the connected Fluent sessions:


.. code:: python

  >>> solver.exit()
  >>> pure_meshing.exit()


Each Fluent session terminates in this scenario because both PyFluent :ref:`Session <ref_session_guide>` objects were obtained by
calling the :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>` function. If the :func:`connect_to_fluent() <ansys.fluent.core.launcher.launcher.connect_to_fluent>` function were used instead, the
Fluent session would terminate upon the ``exit()`` method call if and only if the :func:`connect_to_fluent() <ansys.fluent.core.launcher.launcher.connect_to_fluent>`
function were called with the argument value ``cleanup_on_exit=True``.

Session exiting can also happen implicitly when :ref:`Session <ref_session_guide>` objects are garbage collected. The same rules apply
regarding Fluent termination whether the exit is explicit via an ``<session>.exit()`` method call or implicit.
Implicit exiting occurs via the Python garbage collector. Calling ``session.exit()`` is equivalent to the session
being garbage collected:


.. code:: python

  >>> def run_solver():
  >>>     solver = pyfluent.launch_fluent()
  >>>     # <insert some PyFluent solver actions>
  >>>     # solver is exited at the end of the function

When you end your Python interpreter session, all active PyFluent sessions are exited automatically.
