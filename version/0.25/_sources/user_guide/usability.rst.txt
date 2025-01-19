.. _ref_usability_features:


Usability features
==================

API search
----------

The :ref:`API search <ref_search>` allows you to search for a word throughout Fluent's object hierarchy. It provides results
based on supported features, including semantic matching, wildcard pattern matching, whole word matching, and misspelled
word correction. Semantic search is the default, with English (``eng``) as the default language. For
a list of supported languages, see `OMW Version 1 <https://omwn.org/omw1.html>`_.

Examples
--------

.. code-block:: python

   >>> import ansys.fluent.core as pyfluent
   >>>
   >>> # Semantic search
   >>> pyfluent.search("font")
   <solver_session>.results.graphics.contour["<name>"].color_map.font_automatic (Parameter)
   <solver_session>.results.graphics.contour["<name>"].color_map.font_name (Parameter)
   <solver_session>.results.graphics.contour["<name>"].color_map.font_size (Parameter)
   <solver_session>.results.graphics.lic["<name>"].color_map.font_automatic (Parameter)
   <solver_session>.results.graphics.lic["<name>"].color_map.font_name (Parameter)
   <solver_session>.results.graphics.lic["<name>"].color_map.font_size (Parameter)
   <solver_session>.results.graphics.olic["<name>"].color_map.font_automatic (Parameter)
   <solver_session>.results.graphics.olic["<name>"].color_map.font_name (Parameter)
   <solver_session>.results.graphics.olic["<name>"].color_map.font_size (Parameter)
   ...
   <meshing_session>.preferences.Appearance.Charts.Font (Object)
   <meshing_session>.preferences.Appearance.Charts.Font.Axes (Parameter)
   <meshing_session>.preferences.Appearance.Charts.Font.AxesTitles (Parameter)
   <meshing_session>.preferences.Appearance.Charts.Font.Legend (Parameter)
   <meshing_session>.preferences.Appearance.Charts.Font.Title (Parameter)
   ...
   >>>
   >>> # Chinese semantic search
   >>> pyfluent.search("读", language="cmn")   # search 'read' in Chinese
   <solver_session>.setup.boundary_conditions.velocity_inlet["<name>"].multiphase.directional_spreading_method (Parameter)
   <solver_session>.setup.boundary_conditions.velocity_inlet["<name>"].phase["<name>"].multiphase.directional_spreading_method (Parameter)
   <solver_session>.setup.models.discrete_phase.injections["<name>"].initial_values.particle_size.rosin_rammler.spread (Parameter)
   <solver_session>.setup.physics.volumes.fluid["<name>"].boundaries.velocity_inlet["<name>"].phase["<name>"].multiphase.directional_spreading_method (Parameter)
   <solver_session>.setup.physics.volumes.solid["<name>"].boundaries.velocity_inlet["<name>"].phase["<name>"].multiphase.directional_spreading_method (Parameter)
   <solver_session>.tui.define.models.dpm.numerics.high_resolution_tracking.set_film_spreading_parameter (Command)
   <meshing_session>.MeshingUtilities.set_number_of_parallel_compute_threads (Command)
   <solver_session>.file.convert_hanging_nodes_during_read (Parameter)
   <solver_session>.file.export.settings.cgns_polyhedral_cpu_threads (Parameter)
   <solver_session>.file.import_.read (Command)
   <solver_session>.file.read (Command)
   <solver_session>.file.read_case (Command)
   ...
   >>>
   >>> # Whole word search
   >>> pyfluent.search("ApplicationFontSize", match_whole_word=True)
   <meshing_session>.preferences.Appearance.ApplicationFontSize (Parameter)
   <solver_session>.preferences.Appearance.ApplicationFontSize (Parameter)
   <meshing_session>.tui.preferences.appearance.application_font_size (Command)
   <solver_session>.tui.preferences.appearance.application_font_size (Command)
   >>>
   >>> # Wildcard pattern search
   >>> pyfluent.search("local*", wildcard=True)
   <solver_session>.solution.controls.advanced.expert.pseudo_time_method_usage.local_dt["<name>"] (Object)
   <solver_session>.solution.controls.advanced.expert.pseudo_time_method_usage.local_dt["<name>"].create (Command)
   <solver_session>.solution.controls.advanced.expert.pseudo_time_method_usage.local_dt["<name>"].delete (Command)
   <solver_session>.solution.controls.advanced.expert.pseudo_time_method_usage.local_dt["<name>"].enable_pseudo_time_method (Parameter)
   <solver_session>.solution.controls.advanced.expert.pseudo_time_method_usage.local_dt["<name>"].implicit_under_relaxation_factor (Parameter)
   <solver_session>.solution.controls.advanced.expert.pseudo_time_method_usage.local_dt["<name>"].list (Command)
   <solver_session>.solution.controls.advanced.expert.pseudo_time_method_usage.local_dt["<name>"].list_properties (Command)
   <solver_session>.solution.controls.advanced.expert.pseudo_time_method_usage.local_dt["<name>"].make_a_copy (Command)
   <solver_session>.solution.controls.advanced.expert.pseudo_time_method_usage.local_dt["<name>"].pseudo_time_scale_factor (Parameter)
   <solver_session>.solution.controls.advanced.expert.pseudo_time_method_usage.local_dt["<name>"].rename (Command)
   ...
   >>>
   >>> # Misspelled search
   >>> pyfluent.search("cfb_lma")
   <solver_session>.setup.models.viscous.geko_options.cbf_lam (Parameter)
   <solver_session>.tui.define.models.viscous.geko_options.cbf_lam (Command)
   >>>

