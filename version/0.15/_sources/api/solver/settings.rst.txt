.. _ref_settings:

Solver settings objects
=======================
Solver settings objects provide a natural way to access and modify Fluent solver
settings and issue commands to be executed in the Fluent solver.

Accessing solver settings
-------------------------
An appropriate call to the ``launch_fluent`` function returns an object (named ``solver`` in
the following code snippets) whose interface directly exposes the
:ref:`root<settings_root_section>` of the solver settings hierarchy.

.. code-block::

  >>> import ansys.fluent.core as pyfluent
  >>> solver = pyfluent.launch_fluent(mode="solver")


The ``solver`` object contains attributes such as ``file``, ``setup``, ``solution``, and
``results``, which are also instances of settings objects. Note that the last three are
top-level nodes in the outline tree view in Fluent's graphical user interface (GUI) --- much
of this settings hierarchy has been designed in close alignment with this GUI hierarchy.

Types of settings objects
-------------------------
A settings object can be one of the primitive types: ``Integer``, ``Real``,``String``, and
``Boolean``. A settings object can also be one of the three types of container objects:
``Group``, ``NamedObject``, and ``ListObject``.

- The ``Group`` type is a static container with predefined child objects that
  can be accessed as attributes. For example, in ``setup.models.energy``
  ``energy`` is a child of ``models``, which itself is a child of ``setup``, and each of those 
  three objects is a ``Group``. The names of the child objects of a group can be accessed 
  via ``<Group>.child_names``.

- The ``NamedObject`` type is a container holding dynamically created named objects. For
  a given ``NamedObject`` container, each contained object is of the same
  specific type. A given named object can be accessed using the index operator. For example,
  ``solver.setup.boundary_conditions.velocity_inlet['inlet2']`` yields a ``velocity_inlet``
  object with the name ``inlet2``, assuming it exists. The current list of named object
  children can be accessed via ``<NamedObject>.get_object_names()``.

- The ``ListObject`` type is a container holding dynamically created unnamed objects of
  its specified child type (accessible via a ``child_object_type`` attribute) in a
  list. Children of a ``ListObject`` object can be accessed using the index operator.
  For example, ``solver.setup.cell_zone_conditions.fluid['fluid-1'].source_terms['mass'][2]``
  refers to the third (starting from index 0) mass source entry for the fluid zone
  named ``fluid-1``. The current number of child objects can be accessed with the
  ``get_size()`` method.


Object state
------------
You can access the state of any object by "calling" it. This returns the state of the children 
as a dictionary for ``Group`` and ``NamedObject`` types or as a list for ``ListObject`` types:

.. code-block::

  >>> solver.setup.models.viscous.model()
  'k-epsilon-standard'


.. code-block::

  >>> from pprint import pprint
  >>> pprint (solver.setup.models.energy())
  {'enabled': True,
   'inlet_diffusion': True,
   'kinetic_energy': False,
   'pressure_work': False,
   'viscous_dissipation': False}
  >>> solver.setup.boundary_conditions.velocity_inlet['inlet1'].vmag.constant()
  10.0


To modify the state of any object, you can assign the corresponding attribute
in its parent object. This assignment can be done at any level. For ``Group``
and ``NamedObject`` types, the state value is a dictionary. For the
``ListObject`` type, the state value is a list.

.. code-block::

  >>> solver.setup.models.viscous.model = 'laminar'
  >>> solver.setup.models.energy = { 'enabled' : False }
  >>> solver.setup.boundary_conditions.velocity_inlet['inlet1'].vmag.constant = 14


You can also access the state of an object with the ``get_state`` method and
modify it with the ``set_state`` method.

You can print the current state in a simple text format with the
``print_state`` method. For example, assume you entered:

.. code-block::

  >>> solver.setup.models.print_state()


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
a number of explicit methods and two generic methods: ``get_attr`` and ``get_attrs``.

The following examples access the list of allowed values for a particular state of
the viscous model. All string and string list objects have an ``allowed_values``
method, which returns a list of allowed string values if such a constraint currently applies
for that object or returns ``None`` otherwise.


.. code-block::

  >>> solver.setup.models.viscous.model.allowed_values()
  ['inviscid', 'laminar', 'k-epsilon-standard', 'k-omega-standard', 'mixing-length', 'spalart-allmaras', 'k-kl-w', 'transition-sst', 'reynolds-stress', 'scale-adaptive-simulation', 'detached-eddy-simulation', 'large-eddy-simulation']


.. code-block::

  >>> solver.setup.models.viscous.model.get_attr('allowed-values')
  ['inviscid', 'laminar', 'k-epsilon-standard', 'k-omega-standard', 'mixing-length', 'spalart-allmaras', 'k-kl-w', 'transition-sst', 'reynolds-stress', 'scale-adaptive-simulation', 'detached-eddy-simulation', 'large-eddy-simulation']


.. code-block::

  >>> solver.setup.models.viscous.model.get_attrs(['allowed-values'])
  {'allowed-values': ['inviscid', 'laminar', 'k-epsilon', 'k-omega', 'mixing-length', 'spalart-allmaras', 'k-kl-w', 'transition-sst', 'reynolds-stress', 'scale-adaptive-simulation', 'detached-eddy-simulation', 'large-eddy-simulation']}


These examples accesses the list of zone surfaces:

.. code-block::

  >>> root.solution.report_definitions.flux["mass_flow_rate"] = {}
  >>> root.solution.report_definitions.flux[
          "mass_flow_rate"
      ].zone_names.allowed_values()
  ['symmetry-xyplane', 'hot-inlet', 'cold-inlet', 'outlet', 'wall-inlet', 'wall-elbow', 'interior--elbow-fluid']


.. code-block::

  >>> root.solution.report_definitions.flux["mass_flow_rate"] = {}
  >>> root.solution.report_definitions.flux[
          "mass_flow_rate"
      ].zone_names.get_attr("allowed-values")
  ['symmetry-xyplane', 'hot-inlet', 'cold-inlet', 'outlet', 'wall-inlet', 'wall-elbow', 'interior--elbow-fluid']


.. code-block::

  >>> root.solution.report_definitions.flux["mass_flow_rate"] = {}
  >>> root.solution.report_definitions.flux[
          "mass_flow_rate"
      ].zone_names.get_attrs(["allowed-values"])
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


Using the ``get_attr`` method requires knowledge of metadata names, their applicability, and
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
  >>> import_filename = examples.download_file("mixing_elbow.msh.h5", "pyfluent/mixing_elbow")
  >>> solver = pyfluent.launch_fluent(mode="solver")
  >>> solver.file.read(file_type="case", file_name=import_filename)
  Fast-loading...
  ...Done
  >>> solver.setup.models.viscous.is_active()
  True
  >>> solver.setup.models.viscous.model.is_read_only()
  False
  >>> solver.setup.models.viscous.model.default_value()
  >>> pprint(solver.setup.models.viscous.model.allowed_values())
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
  >>> solver.setup.boundary_conditions.velocity_inlet['cold-inlet'].turb_intensity.min()
  0
  >>> solver.setup.boundary_conditions.velocity_inlet['cold-inlet'].turb_intensity.max()
  1


Active objects and commands
---------------------------
Objects and commands can be active or inactive based on the application state.
The ``is_active()`` method returns ``True`` if an object or command
is currently active.

The ``get_active_child_names`` method returns a list of
active children:

.. code-block::

  >>> solver.setup.models.get_active_child_names()
  ['energy', 'multiphase', 'viscous']


The ``get_active_command_names`` method returns the list of active
commands:

.. code-block::

  >>> solver.solution.run_calculation.get_active_command_names()
  ['iterate']


.. _settings_root_section:

Root object
-----------
The ``root`` object (named solver in the preceding examples) is the top-level
solver settings object. It contains all other settings objects in a hierarchical structure.
For more information, see :ref:`root`.
