Radiation model
===============

Setting up and querying the model
---------------------------------

.. code:: python

    >>> import ansys.fluent.core as pyfluent
    >>> radiation = pyfluent.Radiation(settings_source=solver)
    >>> from pprint import pprint
    >>> pprint(radiation.get_state(), width=1)
    {'model': 'none',
     'solar_load': {'solar_model': 'none',
                    'sun_direction_vector_definition': None}}
    >>> pprint(radiation.model.allowed_values(), width=1)
    ['none',
     'p1',
     's2s',
     'discrete-ordinates',
     'monte-carlo']
    >>> radiation.model.set_state("monte-carlo")
    >>> pprint(radiation.get_state(), width=1)
    {'model': 'monte-carlo',
     'monte_carlo': {'number_of_histories': 100000,
                     'target_cells_per_volume_cluster': 1,
                     'under_relaxation': 0.5},
     'multiband': None,
     'solar_load': {'solar_model': 'none',
                    'sun_direction_vector_definition': None},
     'solve_frequency': {'iteration_interval': 10}}
    >>> radiation.monte_carlo.number_of_histories.set_state(1e7)
    >>> radiation.multiband.create("solar").set_state({
    >>>    "start": 0,
    >>>    "end": 2.8,
    >>> })
    >>> radiation.multiband.create("thermal-ir").set_state({
    >>>    "start": 2.8,
    >>>    "end": 100,
    >>> })
    >>> radiation_freq = radiation.solve_frequency
    >>> pprint(radiation_freq.get_state(), width=1)
    {'iteration_interval': 10}
    >>> pprint(radiation.get_state(), width=1)
    {'model': 'monte-carlo',
     'monte_carlo': {'number_of_histories': 10000000.0,
                     'target_cells_per_volume_cluster': 1,
                     'under_relaxation': 0.5},
     'multiband': {'solar': {'end': 2.8,
                             'name': 'solar',
                             'start': 0},
                   'thermal-ir': {'end': 100,
                                  'name': 'thermal-ir',
                                  'start': 2.8}},
     'solar_load': {'solar_model': 'none',
                    'sun_direction_vector_definition': None},
     'solve_frequency': {'iteration_interval': 10}}