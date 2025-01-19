Battery model
=============

Setting up and querying the model
---------------------------------

.. code:: python

    >>> battery = solver.settings.setup.models.battery
    >>> battery.enabled.set_state(True)
    >>> battery.solution_method.allowed_values()
    ['cht-coupling', 'fmu-cht-coupling', 'circuit-network', 'msmd', 'msmd-rom']