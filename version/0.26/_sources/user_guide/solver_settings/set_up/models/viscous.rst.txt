Viscous model
=============

Setting up and querying the model
---------------------------------

.. code:: python

    >>> viscous = solver.settings.setup.models.viscous
    >>> from pprint import pprint
    >>> pprint(viscous.get_state(), width=1)
    {'k_omega_model': 'sst',
     'k_omega_options': {'kw_low_re_correction': False},
     'model': 'k-omega',
     'near_wall_treatment': {'wall_omega_treatment': 'correlation'},
     'options': {'corner_flow_correction': False,
                 'curvature_correction': False,
                 'production_kato_launder_enabled': False,
                 'production_limiter': {'clip_factor': 10.0,
                                        'enabled': True},
                 'viscous_heating': False},
     'transition_module': 'none',
     'turbulence_expert': {'restore_sst_v61': False,
                           'thermal_p_function': True,
                           'turb_non_newtonian': False},
     'user_defined': {'energy_prandtl': 'none',
                      'turb_visc_func': 'none',
                      'wall_prandtl': 'none'}}
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
    >>> viscous.options.corner_flow_correction.is_active()
    True
    >>> viscous.model.set_state('k-epsilon')
    >>> viscous.options.corner_flow_correction.is_active()
    False
    >>> viscous.k_epsilon_model.get_state()
    'standard'
    >>> viscous.k_omega_model.is_active()
    False
    >>> viscous.k_epsilon_model.allowed_values()
    ['standard',
     'realizable',
     'rng']
    >>> viscous.options.production_kato_launder_enabled.is_active()
    True
    >>> viscous.options.production_kato_launder_enabled.get_state()
    False
    >>> viscous.k_epsilon_model.set_state("realizable")
    >>> viscous.options.production_kato_launder_enabled.is_active()
    False
