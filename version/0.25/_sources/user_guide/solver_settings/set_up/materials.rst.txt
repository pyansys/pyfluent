Define materials
==================
PyFluent allows you to use :ref:`ref_settings` to interact with materials settings.

Copy material from database
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> import ansys.fluent.core as pyfluent
    >>> from ansys.fluent.core import examples
    >>> file_name = examples.download_file("mixing_elbow.cas.h5", "pyfluent/mixing_elbow")
    >>> solver = pyfluent.launch_fluent()
    >>> solver.settings.file.read_case(file_name=file_name)
    >>> materials = solver.settings.setup.materials
    >>> fluids = materials.fluid
    >>> fluids.make_a_copy(from_="air",to="air-2")
    >>> air_copy = fluids["air-2"]
    >>> from pprint import pprint
    >>> pprint(air_copy.get_state(), width=1)
    {'chemical_formula': '',
     'density': {'option': 'constant', 'value': 1.225},
     'name': 'air-2',
     'specific_heat': {'option': 'constant', 'value': 1006.43},
     'thermal_conductivity': {'option': 'constant', 'value': 0.0242},
     'viscosity': {'option': 'constant', 'value': 1.7894e-05}}
    >>> pprint(air_copy.viscosity.option.allowed_values(), width=1)
    ['constant',
     'piecewise-linear',
     'piecewise-polynomial',
     'polynomial',
     'expression',
     'power-law',
     'sutherland',
     'kinetic-theory']
    >>> air_copy.viscosity.value.set_state(1.81e-05)
    >>> solver.settings.setup.cell_zone_conditions.fluid["elbow-fluid"].material.set_state("air-2")


Create new material
~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> mysolid = materials.solid.create("mysolid")
    >>> mysolid.chemical_formula.set_state("SiO2")
    >>> mysolid.density.value.set_state(2650)
    >>> mysolid.specific_heat.value.set_state(1887)
    >>> mysolid.thermal_conductivity.value.set_state(7.6)


.. code:: python

    >>> myfluid = materials.fluid.create("myfluid")
    >>> myfluid.chemical_formula.set_state("H2O")
    >>> myfluid.density.value.set_state(1000)
    >>> myfluid.specific_heat.value.set_state(4186)
    >>> myfluid.thermal_conductivity.value.set_state(0.6)
    >>> myfluid.viscosity.value.set_state(1.03e-3)