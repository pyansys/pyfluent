Species model
=============

Setting up and querying the model
---------------------------------

.. code:: python

    >>> import ansys.fluent.core as pyfluent
    >>> solver.settings.file.read_case(file_name=file_name)
    >>> species = pyfluent.Species(settings_source=solver)
    >>> species.get_state()
    {'model': {'option': 'off', 'number_vol_spec': False}}
    >>> from pprint import pprint
    >>> pprint(species.model.option.allowed_values(), width=1)
    ['off',
     'species-transport',
     'non-premixed-combustion',
     'premixed-combustion',
     'partially-premixed-combustion',
     'pdf-transport']
    >>> species.model.option.set_state("species-transport")
    >>> pprint(species.get_state(), width=1)
    {'model': {'material': 'mixture-template',
               'number_vol_spec': 3,
               'option': 'species-transport'},
     'options': {'diffusion_energy_source': True,
                 'inlet_diffusion': False,
                 'multi_component_diffusion': False,
                 'save_gradients': False,
                 'species_transport_expert': False,
                 'thermal_diffusion': False},
     'reactions': {'enable_volumetric_reactions': False},
     'species_transport_expert_options': {'blending': False,
                                          'linearize_convection_source': False,
                                          'linearize_diffusion_source': False}}
    >>> species.model.material.get_state()
    'mixture-template'
    >>> species.model.material.allowed_values()
    ['mixture-template', 'air-2species-nitrogen', 'air-5species-park93', 'air-11species-park93', 'mars-5species-mckenzie',
     'mars-8species-park', 'mars-venus-16species-johnston', 'air-11species-gupta', 'acetylene-air', 'anthracite-volatiles-air',
     'battery-venting-gas-mixture', 'benzene-air', 'calcium-carbonate-decomposition', 'carbon-monoxide-air', 'inert-mixture',
     'coal-hv-volatiles-air', 'coal-lv-volatiles-air', 'coal-mv-volatiles-air', 'diesel-air', 'ethane-air', 'ethylene-air',
     'ethyl-alcohol-air', 'fuel-oil-air', 'gasoil-air', 'titan-13species-gokcen', 'titan-21species-gokcen', 'hydrogen-air',
     'hydrogen-peroxide-water-air', 'kerosene-air', 'lignite-volatiles-air', 'methane-air', 'methane-air-2step', 'methyl-alcohol-air',
     'n-butane-air', 'n-heptane-air', 'n-hexane-air', 'n-octane-air', 'n-pentane-air', 'peat-volatiles-air', 'pem-mixture',
     'propane-air', 'propane-air-2step', 'propylene-air', 'silane-hydrogen', 'silane-hydrogen-3-step', 'toluene-air', 'urea-water-air',
     'urea-water-deposits-air-brack', 'wood-volatiles-air']