Energy model
============

Setting up and querying the model
---------------------------------

.. code:: python

    >>> import ansys.fluent.core as pyfluent
    >>> from ansys.fluent.core import examples
    >>> file_name = examples.download_file("mixing_elbow.cas.h5", "pyfluent/mixing_elbow")
    >>> solver = pyfluent.launch_fluent()
    >>> solver.settings.file.read_case(file_name=file_name)
    >>> energy = solver.settings.setup.models.energy
    >>> energy.enabled.get_state()
    True
    >>> from pprint import pprint
    >>> pprint(energy.get_state(), width=1)
    {'enabled': True,
     'inlet_diffusion': True,
     'kinetic_energy': False,
     'pressure_work': False,
     'viscous_dissipation': False}
    >>> energy.enabled.set_state(False)
    >>> pprint(energy.get_state(), width=1)
    {'enabled': False}
    >>> energy.enabled.set_state(True)
    >>> pprint(energy.get_state(), width=1)
    {'enabled': True,
     'viscous_dissipation': False,
     'pressure_work': False,
     'kinetic_energy': False,
     'inlet_diffusion': True}
    >>> energy.viscous_dissipation.set_state(True)
    >>> pprint(energy.get_state(), width=1)
    {'enabled': True,
     'inlet_diffusion': True,
     'viscous_dissipation': True}
    