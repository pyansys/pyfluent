Discrete phase model
====================

Setting up and querying the model
---------------------------------

.. code:: python

    >>> dpm = solver.settings.setup.models.discrete_phase
    >>> dpm_models = dpm.physical_models
    >>> dpm_models.virtual_mass_force.enabled.get_state()
    >>> dpm_models.virtual_mass_force.virtual_mass_factor.is_active()
    False
    >>> dpm_models.virtual_mass_force.enabled.set_state(True)
    >>> dpm_models.virtual_mass_force.virtual_mass_factor.get_state()
    0.5