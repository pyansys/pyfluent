.. _ref_settings:

Settings objects
================
Settings objects provide a natural way to access and modify Fluent settings and
issue commands with a hierarchy of objects.

Top-level settings objects
--------------------------
The top-level settings object is available as the :ref:`root<settings_root_section>`
property of ``session.solver``.

.. code-block::

  >>> import ansys.fluent.core as pyfluent
  >>> solver = pyfluent.launch_fluent(mode="solver")
  >>> root = solver


The ``root`` object contains attributes such as ``file``, ``setup``,
``solution``, and ``results``.  These objects are also instances of settings
objects and roughly mirror the outline view in Fluent.

Types of settings objects
-------------------------
A settings object can be one of the primitive types, like ``Integer``, ``Real``,
``String``, and ``Boolean``. It can also be a container object, of which there
are three types: ``Group``, ``NamedObject``, and ``ListObject``.

- The ``Group`` type is a static container with predefined child objects that
  can be accessed via attributes. For example, ``setup.models.energy``
  refers to the ``energy`` child of the ``models`` child of the ``setup`` object. The
  names of the child objects of a group can be accessed with the ``child_names``
  attribute of a ``Group`` object.

- The ``NamedObject`` type is a container holding dynamically created named objects of
  its specified child type (accessible via a ``child_object_type`` attribute),
  similar to a dictionary. A specified named object can be accessed using the
  index operator. For example, ``root.setup.boundary_conditions.velocity_inlet['inlet2']``
  refers to the ``velocity_object`` object with the name ``inlet2``. The current
  list of named object children can be accessed with the ``get_object_names()`` method
  of the container class.

- The ``ListObject`` type is a container holding dynamically created unnamed objects of
  its specified child type (accessible via a ``child_object_type`` attribute) in a
  list. Children of a ``ListObject`` object can be accessed using the index operator.
  For example, ``root.setup.cell_zone_conditions.fluid['fluid-1'].source_terms['mass'][2]``
  refers to the third (starting from index 0) mass source entry for the fluid zone
  named ``fluid-1``. The current number of child objects can be accessed with the
  ``get_size()`` method.


Object state
------------
You can access the state of any object by "calling" it. For container objects,
this returns the state of the children as a dictionary for ``Group`` and
``NamedObject`` types or as a list for ``ListObject`` types:

.. code-block::

  >>> root.setup.models.viscous.model()
  'k-epsilon-standard'


.. code-block::

  >>> from pprint import pprint
  >>> pprint (root.setup.models.energy())
  {'enabled': True,
   'inlet_diffusion': True,
   'kinetic_energy': False,
   'pressure_work': False,
   'viscous_dissipation': False}
  >>> root.setup.boundary_conditions.velocity_inlet['inlet1'].vmag.constant()
  10.0


To modify the state of any object, you can assign the corresponding attribute
in its parent object. This assignment can be done at any level. For ``Group``
and ``NamedObject`` types, the state value is a dictionary. For the
``ListObject`` type, the state value is a list.

.. code-block::

  >>> root.setup.models.viscous.model = 'laminar'
  >>> root.setup.models.energy = { 'enabled' : False }
  >>> root.setup.boundary_conditions.velocity['inlet1'].vmag.constant = 14


You can also access the state of an object with the ``get_state`` method and
modify it with the ``set_state`` method.

You can print the current state in a simple text format with the
``print_state`` method. For example, assume you entered:

.. code-block::

  >>> root.setup.models.print_state()


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
and can be either the primitive type or the container type.

Additional metadata
-------------------
Settings objects have some additional metadata that you can use the
``get_attr`` and ``get_attrs`` methods to access. 

This example accesses the list of allowed values at a particular state for
the viscous model:

.. code-block::

  >>> root.setup.models.viscous.model.get_attr('allowed-values')
  ['inviscid', 'laminar', 'k-epsilon-standard', 'k-omega-standard', 'mixing-length', 'spalart-allmaras', 'k-kl-w', 'transition-sst', 'reynolds-stress', 'scale-adaptive-simulation', 'detached-eddy-simulation', 'large-eddy-simulation']
 

.. code-block::

  >>> root.setup.models.viscous.model.get_attrs(['allowed-values'])
  {'allowed-values': ['inviscid', 'laminar', 'k-epsilon', 'k-omega', 'mixing-length', 'spalart-allmaras', 'k-kl-w', 'transition-sst', 'reynolds-stress', 'scale-adaptive-simulation', 'detached-eddy-simulation', 'large-eddy-simulation']}


This example accesses the list of zone surfaces:

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


Attributes are dynamic. Values can change based on the app
state.

Active objects and commands
---------------------------
Objects and commands can be active or inactive based on the app state.
The ``is_active()`` method returns ``True`` if an object or command
is active at a particular time.

The ``get_active_child_names`` method returns the list of
active children:

.. code-block::

  >>> root.setup.models.get_active_child_names()
  ['energy', 'multiphase', 'viscous']


The ``get_active_command_names`` method returns the list of active
commands:

.. code-block::

  >>> root.solution.run_calculation.get_active_command_names()
  ['iterate']


.. _settings_root_section:

Root object
-----------
The ``root`` object is the top-level settings object. It contains all other
settings objects in a hierarchical structure. For more information, see :ref:`root`.
