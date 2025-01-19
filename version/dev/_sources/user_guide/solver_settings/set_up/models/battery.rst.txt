Battery model
=============

Setting up and querying the model
---------------------------------

.. code:: python

    >>> import ansys.fluent.core as pyfluent
    >>> battery = pyfluent.Battery(settings_source=solver)
    >>> battery.enabled.set_state(True)
    >>> battery.solution_method.allowed_values()
    ['cht-coupling', 'fmu-cht-coupling', 'circuit-network', 'msmd', 'msmd-rom']