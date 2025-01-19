.. _ref_solver_settings_guide:

Solver settings objects
=======================

.. vale Google.Spacing = NO

Solver settings objects provide a natural way to access and modify Fluent solver
settings and issue commands to be executed in the Fluent solver. 
An appropriate call to the :func:`~ansys.fluent.core.launcher.launcher.launch_fluent`
function returns an object whose interface directly exposes the :ref:`ref_root` of the solver settings hierarchy.

.. vale Google.Spacing = YES


New format for accessing solver settings objects
------------------------------------------------

To simplify the usage of Fluent solver settings and improve readability, 
you can now instantiate settings objects directly using a more intuitive syntax. 
This new approach allows for straightforward access to various settings without 
navigating through the hierarchical structure of the solver settings.

Example usage
-------------

.. code-block:: python

  >>> import ansys.fluent.core as pyfluent
  >>> solver = pyfluent.launch_fluent(mode=pyfluent.FluentMode.SOLVER)
  >>> inlet1 = pyfluent.VelocityInlet(settings_source=solver, name="inlet-1")


This format provides a more natural way to create and interact with settings objects, 
making your code easier to read and maintain. By abstracting the underlying hierarchy, 
users can focus on the specific settings they need without dealing with potential changes 
in the Fluent API structure.

Accessing solver settings
-------------------------

Following the introduction of the new format, the traditional method remains available for those 
who prefer the existing hierarchy.

.. code-block:: python

  >>> file = solver.settings.file
  >>> setup = solver.settings.setup
  >>> solution = solver.settings.solution
  >>> results = solver.settings.results


Types of settings objects
-------------------------

.. vale Google.Spacing = NO

A settings object can be one of the primitive types: :obj:`~ansys.fluent.core.solver.flobject.Integer`,
:obj:`~ansys.fluent.core.solver.flobject.Real`,
:obj:`~ansys.fluent.core.solver.flobject.String`, and
:obj:`~ansys.fluent.core.solver.flobject.Boolean`. A settings object can also be one of the three types
of container objects: :obj:`~ansys.fluent.core.solver.flobject.Group`,
:obj:`~ansys.fluent.core.solver.flobject.NamedObject`, and
:obj:`~ansys.fluent.core.solver.flobject.ListObject`.

- The :obj:`~ansys.fluent.core.solver.flobject.Group` type is a static container with predefined child objects that
  can be accessed as attributes. For example, using the expression ``solver.settings.setup.models.energy``,
  which resolves to :obj:`~ansys.fluent.core.generated.solver.settings_232.energy.energy`,
  which is a child of :obj:`~ansys.fluent.core.generated.solver.settings_232.models_1.models`,
  which itself is a child of :obj:`~ansys.fluent.core.generated.solver.settings_232.setup.setup`, and each of those
  three objects is a ``Group``.
  The names of the child objects of a group can be accessed
  via ``<Group>.child_names``.

- The :obj:`~ansys.fluent.core.solver.flobject.NamedObject` type is a container holding dynamically
  created named objects. For
  a given ``NamedObject`` container, each contained object is of the same
  specific type. A given named object can be accessed using the index operator. For example,
  ``solver.settings.setup.boundary_conditions.velocity_inlet['inlet2']`` yields a ``velocity_inlet``
  object with the name ``inlet2``, assuming it exists. The current list of named object
  children can be accessed via ``<NamedObject>.get_object_names()``.

- The :obj:`~ansys.fluent.core.solver.flobject.ListObject` type is a container holding dynamically
  created unnamed objects of
  its specified child type (accessible via a ``child_object_type`` attribute) in a
  list. Children of a ``ListObject`` object can be accessed using the index operator.
  For example, ``solver.settings.setup.cell_zone_conditions.fluid['fluid-1'].source_terms['mass'][2]``
  refers to the third (starting from index 0) mass source entry for the fluid zone
  named ``fluid-1``. The current number of child objects can be accessed with the
  ``get_size()`` method.

.. vale Google.Spacing = YES


Object state
------------
You can access the state of any object by "calling" it. This returns the state of the children
as a dictionary for ``Group`` and ``NamedObject`` types or as a list for ``ListObject`` types:

.. code-block::

  >>> import ansys.fluent.core as pyfluent
  >>> viscous = pyfluent.solver.Viscous(settings_source=solver)
  >>> viscous.model()
  'k-epsilon-standard'


.. code-block::

  >>> import ansys.fluent.core as pyfluent
  >>> energy = pyfluent.solver.Energy(settings_source=solver)
  >>> from pprint import pprint
  >>> pprint (energy(), width=1)
  {'enabled': True,
   'inlet_diffusion': True,
   'kinetic_energy': False,
   'pressure_work': False,
   'viscous_dissipation': False}
  >>> inlet1 = pyfluent.solver.VelocityInlet(settings_source=solver, name="inlet1")
  >>> inlet1.vmag.constant()
  10.0


To modify the state of any object, you can assign the corresponding attribute
in its parent object. This assignment can be done at any level. For ``Group``
and ``NamedObject`` types, the state value is a dictionary. For the
``ListObject`` type, the state value is a list.

.. code-block::

  >>> import ansys.fluent.core as pyfluent
  >>> viscous = pyfluent.solver.Viscous(settings_source=solver)
  >>> viscous.model = 'laminar'
  >>> energy = pyfluent.solver.Energy(settings_source=solver)
  >>> energy = { 'enabled' : False }
  >>> inlet1 = pyfluent.solver.VelocityInlet(settings_source=solver, name="inlet1")
  >>> inlet1.vmag.constant = 14


You can also access the state of an object with the ``get_state()`` method and
modify it with the ``set_state()`` method.

``Real`` and ``RealList`` settings objects can incorporate units alongside values. If an object
supports units, you can retrieve its value and units as an ``ansys.units.Quantity`` object using
the ``as_quantity()`` method. Alternatively, you can obtain the same information as a tuple by
calling the ``state_with_units()`` method. You can call the ``state_with_units()`` method on a
container object. It returns a dictionary where relevant values are represented as tuples containing
the value and units.

Both ``ansys.units.Quantity`` objects and value-unit tuples can be used with the
``set_state()`` method of ``Real`` or ``RealList`` objects.

.. code-block::

  >>> diam_obj = hydraulic_diameter.as_quantity()
  >>> diam_tup = hydraulic_diameter.state_with_units()
  >>> assert diam_tup == (diam_obj.value, diam_obj.units.name)
  >>> hydraulic_diameter.set_state(2.0 * diam_obj)
  >>> assert hydraulic_diameter.units == diam_obj.units


You can print the current state in a simple text format with the
``print_state`` method. For example, assume you entered:

.. code-block::

  >>> import ansys.fluent.core as pyfluent
  >>> models = pyfluent.solver.Models(settings_source=solver)
  >>> models.print_state()


The following output is returned:

.. code-block::

  viscous :
    k_epsilon_model : standard
    near_wall_treatment : standard-wall-fn?
    model : k-epsilon-standard
    options :
      viscous_heating : False
      curvature_correction : False
      production_kato_launder : False
      production_limiter : False
  energy :
    enabled : True
    pressure_work : False
    viscous_dissipation : False
    inlet_diffusion : True
    kinetic_energy : False
  multiphase :
    number_of_phases : 0
    models : none

Commands
--------
Commands are methods of settings objects that you use to modify the state of
the application. For example, the ``hybrid_initialize()`` method of
``solution.initialization`` initializes the solution using the hybrid
initialization method. The ``command_names`` attribute of a settings object
provides the names of its commands.

If keyword arguments are needed, you can use commands to pass them. To access a
list of valid arguments, use the ``arguments`` attribute. If you do not specify
an argument, its default value is used. Arguments are also settings objects
and can be of either primitive or container type.

Additional metadata
-------------------
Settings object methods are provided to access some additional metadata. There are
a number of explicit methods and two generic methods: ``get_attr()`` and ``get_attrs()``.

The following examples access the list of allowed values for a particular state of
the viscous model. All string and string list objects have an ``allowed_values()``
method, which returns a list of allowed string values if such a constraint currently applies
for that object or returns ``None`` otherwise.


.. code-block::

  >>> import ansys.fluent.core as pyfluent
  >>> viscous = pyfluent.solver.Viscous(settings_source=solver)
  >>> viscous.model.allowed_values()
  ['inviscid', 'laminar', 'k-epsilon-standard', 'k-omega-standard', 'mixing-length', 'spalart-allmaras', 'k-kl-w', 'transition-sst', 'reynolds-stress', 'scale-adaptive-simulation', 'detached-eddy-simulation', 'large-eddy-simulation']


.. code-block::

  >>> import ansys.fluent.core as pyfluent
  >>> viscous = pyfluent.solver.Viscous(settings_source=solver)
  >>> viscous.model.get_attr('allowed-values')
  ['inviscid', 'laminar', 'k-epsilon-standard', 'k-omega-standard', 'mixing-length', 'spalart-allmaras', 'k-kl-w', 'transition-sst', 'reynolds-stress', 'scale-adaptive-simulation', 'detached-eddy-simulation', 'large-eddy-simulation']


.. code-block::

  >>> import ansys.fluent.core as pyfluent
  >>> viscous = pyfluent.solver.Viscous(settings_source=solver)
  >>> viscous.model.get_attrs(['allowed-values'])
  {'allowed-values': ['inviscid', 'laminar', 'k-epsilon', 'k-omega', 'mixing-length', 'spalart-allmaras', 'k-kl-w', 'transition-sst', 'reynolds-stress', 'scale-adaptive-simulation', 'detached-eddy-simulation', 'large-eddy-simulation']}


These examples accesses the list of zone surfaces:

.. code-block::

  >>> solver.settings.solution.report_definitions.flux["mass_flow_rate"] = {}
  >>> solver.settings.solution.report_definitions.flux["mass_flow_rate"].boundaries.allowed_values()
  ['symmetry-xyplane', 'hot-inlet', 'cold-inlet', 'outlet', 'wall-inlet', 'wall-elbow', 'interior--elbow-fluid']


.. code-block::

  >>> solver.settings.solution.report_definitions.flux["mass_flow_rate"] = {}
  >>> solver.settings.solution.report_definitions.flux["mass_flow_rate"].boundaries.get_attr("allowed-values")
  ['symmetry-xyplane', 'hot-inlet', 'cold-inlet', 'outlet', 'wall-inlet', 'wall-elbow', 'interior--elbow-fluid']


.. code-block::

  >>> solver.settings.solution.report_definitions.flux["mass_flow_rate"] = {}
  >>> solver.settings.solution.report_definitions.flux["mass_flow_rate"].boundaries.get_attrs(["allowed-values"])
  {'allowed-values': ['symmetry-xyplane', 'hot-inlet', 'cold-inlet', 'outlet', 'wall-inlet', 'wall-elbow', 'interior--elbow-fluid']}


The following table contains metadata names, corresponding methods to access this metadata, whether the method can return None, applicable object types, and returned data types:

==================  ==================  =================  =====================  ====================
Metadata name       Method              Can return None    Type applicability     Metadata type
==================  ==================  =================  =====================  ====================
``is-active?``      ``is_active``       no                 all                    ``bool``
``is-read-only?``   ``is_read_only``    no                 all                    ``bool``
``default-value``   ``default``         yes                all primitives         type of primitive
``allowed-values``  ``allowed_values``  yes                ``str``, ``str list``  ``str list``
``min``             ``min``             yes                ``int``, ``float``     ``int`` or ``float``
``max``             ``max``             yes                ``int``, ``float``     ``int`` or ``float``
==================  ==================  =================  =====================  ====================


Using the ``get_attr()`` method requires knowledge of metadata names, their applicability, and
the ability to interpret the raw values of the metadata. You can avoid all these issues by
using the explicitly named methods. Note also that the metadata is dynamic, which means
values can change based on the application state. A ``None`` value signifies that no value
is currently designated for this metadata.


This simple example shows you how to use a number of these explicit metadata access methods
in a single solver session:

.. code-block::

  >>> import ansys.fluent.core as pyfluent
  >>> from ansys.fluent.core import examples
  >>> from pprint import pprint
  >>> import_file_name = examples.download_file("mixing_elbow.msh.h5", "pyfluent/mixing_elbow")
  >>> solver = pyfluent.launch_fluent(mode=pyfluent.FluentMode.SOLVER)
  >>> solver.settings.file.read(file_type="case", file_name=import_file_name)
  Fast-loading...
  ...Done
  >>> viscous = pyfluent.solver.Viscous(settings_source=solver)
  >>> viscous.is_active()
  True
  >>> viscous.model.is_read_only()
  False
  >>> viscous.model.default_value()
  >>> pprint(viscous.model.allowed_values(), width=1)
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
  >>> cold_inlet = pyfluent.solver.VelocityInlet(settings_source=solver, name="cold-inlet")
  >>> cold_inlet.turb_intensity.min()
  0
  >>> cold_inlet.turb_intensity.max()
  1


Active objects and commands
---------------------------
Objects and commands can be active or inactive based on the application state.
The ``is_active()`` method returns ``True`` if an object or command
is currently active.

The ``get_active_child_names()`` method returns a list of
active children::

  >>> import ansys.fluent.core as pyfluent
  >>> models = pyfluent.solver.Models(settings_source=solver)
  >>> models.get_active_child_names()
  ['energy', 'multiphase', 'viscous']

The ``get_active_command_names()`` method returns the list of active
commands::

  >>> solver.settings.solution.run_calculation.get_active_command_names()
  ['iterate']

Wildcards
---------
You can use wildcards when using named objects, list objects, and string list settings.
For named objects and list objects, for instance::

  >>> import ansys.fluent.core as pyfluent
  >>> fluid = pyfluent.solver.FluidCellZone(settings_source=solver, name="*")
  >>> fluid.source_terms["*mom*"]()
  {'fluid': {'source_terms': {'x-momentum': [], 'y-momentum': [], 'z-momentum': []}}}

Also, when you have one or more velocity inlets with "inlet" in their names::

  >>> import ansys.fluent.core as pyfluent
  >>> inlet = pyfluent.solver.VelocityInlet(settings_source=solver, name="*inlet*")
  >>> inlet.vmag()
  {'velo-inlet_2': {'vmag': {'option': 'value', 'value': 50}},
  'velo-inlet_1': {'vmag': {'option': 'value', 'value': 35}}

For string lists with allowed values, for instance::

  >>> solver.results.graphics.contour['contour-1'].surfaces_list = 'in*'

sets ``surfaces_list`` to all matches of surface names starting with ``in``, so when you prompt for the
list of surfaces::

  >>> solver.results.graphics.contour['contour-1'].surfaces_list()
  ['in1', 'in2']

The following list summarizes common wildcards:

- ``*`` indicates zero or more occurrences of the preceding element. For example, ``'in*'`` lists
  only items starting with "in" such as in1 and in2, whereas *in* lists only items that have
  the string "in" within the name.

- ``?`` substitutes for a single unknown character. For example, ``'gr?y'`` would list "grey" and "gray".

- ``[]`` indicates a range of numbers or characters at the beginning of a string. For example,
  ``'[to]'`` would match anything starting with "t" and anything starting with "o" in the name. Using
  ``'[a-z]'`` would match anything starting with a character between "a" and "z" inclusively, or
  using ``'[0-9]'`` would match the initial character with any number between "0" and "9" inclusively.

- ``^`` indicates a Boolean NOT function, or negation. For example, ``'^*in*'`` would list anything
  not containing "in".

- ``|`` indicates a Boolean OR function. For example, ``'*part*|*solid*'`` would list anything
  containing either "part" or "solid" such as "part2-solid-1", "part2-solid-2", "part-3",
  "solid", and "solid-1".

- ``&`` indicates a Boolean AND function. For example, ``'*part*&*solid*'`` would list anything
  containing both "part" and "solid" such as "part2-solid-1" and "part2-solid-2".


.. toctree::
   :maxdepth: 1
   :hidden:

   set_up/index
   solution
