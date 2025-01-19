.. _ref_new_meshing_workflows_guide:

Meshing workflow
================
You can use PyFluent to access the new, enhanced meshing workflows.

Watertight geometry meshing workflow
------------------------------------
Use the **Watertight Geometry** workflow for watertight CAD geometries that
require little cleanup. This is useful for clean geometries that have already
been prepped in another software, such as Ansys SpaceClaim.
The following example shows how to use the Watertight Geometry workflow.

Import geometry
~~~~~~~~~~~~~~~

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    import_file_name = examples.download_file('mixing_elbow.pmdb', 'pyfluent/mixing_elbow')
    meshing = pyfluent.launch_fluent(
        mode="meshing", precision=pyfluent.Precision.DOUBLE, processor_count=2
    )
    watertight = meshing.watertight()
    watertight.import_geometry.file_name.set_state(import_file_name)
    watertight.import_geometry.length_unit.set_state('in')
    watertight.import_geometry()

Add local sizing
~~~~~~~~~~~~~~~~

.. code:: python

    watertight.add_local_sizing.add_child_to_task()
    watertight.add_local_sizing()

Generate surface mesh
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    watertight.create_surface_mesh.cfd_surface_mesh_controls.max_size.set_state(0.3)
    watertight.create_surface_mesh()

Describe geometry
~~~~~~~~~~~~~~~~~

.. code:: python

    watertight.describe_geometry.update_child_tasks(setup_type_changed=False)
    watertight.describe_geometry.setup_type.set_state("The geometry consists of only fluid regions with no voids")
    watertight.describe_geometry.update_child_tasks(setup_type_changed=True)
    watertight.describe_geometry()

Update boundaries
~~~~~~~~~~~~~~~~~

.. code:: python

    watertight.update_boundaries.boundary_label_list.set_state(["wall-inlet"])
    watertight.update_boundaries.boundary_label_type_list.set_state(["wall"])
    watertight.update_boundaries.old_boundary_label_list.set_state(["wall-inlet"])
    watertight.update_boundaries.old_boundary_label_type_list.set_state(["velocity-inlet"])
    watertight.update_boundaries()

Update regions
~~~~~~~~~~~~~~

.. code:: python

    watertight.update_regions()

Add boundary layers
~~~~~~~~~~~~~~~~~~~

.. code:: python

    watertight.add_boundary_layer.add_child_to_task()
    watertight.add_boundary_layer.insert_compound_child_task()
    watertight.task("smooth-transition_1").bl_control_name.set_state("smooth-transition_1")
    watertight.add_boundary_layer.arguments = {}
    watertight.task("smooth-transition_1")()

Generate volume mesh
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    watertight.create_volume_mesh.volume_fill.set_state("poly-hexcore")
    watertight.create_volume_mesh.volume_fill_controls.hex_max_cell_length.set_state(0.3)
    watertight.create_volume_mesh()

Switch to solution mode
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    solver = meshing.switch_to_solver()

Fault-tolerant meshing workflow
-------------------------------
Use the **Fault-tolerant** meshing workflow for complex CAD geometries that need
cleanup or modification, such as addressing overlaps, intersections, holes, and duplicates.
The following example shows how to use the fault-tolerant workflow.

Import CAD and part management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    import_file_name = examples.download_file(
        "exhaust_system.fmd", "pyfluent/exhaust_system"
    )
    meshing = pyfluent.launch_fluent(precision=pyfluent.Precision.DOUBLE, processor_count=2, mode="meshing")
    fault_tolerant = meshing.fault_tolerant()
    meshing.PartManagement.InputFileChanged(
        FilePath=import_file_name, IgnoreSolidNames=False, PartPerBody=False
    )
    meshing.PMFileManagement.FileManager.LoadFiles()
    meshing.PartManagement.Node["Meshing Model"].Copy(
        Paths=[
            "/dirty_manifold-for-wrapper," + "1/dirty_manifold-for-wrapper,1/main,1",
            "/dirty_manifold-for-wrapper," + "1/dirty_manifold-for-wrapper,1/flow-pipe,1",
            "/dirty_manifold-for-wrapper," + "1/dirty_manifold-for-wrapper,1/outpipe3,1",
            "/dirty_manifold-for-wrapper," + "1/dirty_manifold-for-wrapper,1/object2,1",
            "/dirty_manifold-for-wrapper," + "1/dirty_manifold-for-wrapper,1/object1,1",
        ]
    )
    meshing.PartManagement.ObjectSetting["DefaultObjectSetting"].OneZonePer.set_state("part")
    fault_tolerant.import_cad_and_part_management.context.set_state(0)
    fault_tolerant.import_cad_and_part_management.create_object_per.set_state("Custom")
    fault_tolerant.import_cad_and_part_management.fmd_file_name.set_state(import_file_name)
    fault_tolerant.import_cad_and_part_management.file_loaded.set_state("yes")
    fault_tolerant.import_cad_and_part_management.object_setting.set_state("DefaultObjectSetting")
    fault_tolerant.import_cad_and_part_management.options.line.set_state(False)
    fault_tolerant.import_cad_and_part_management.options.solid.set_state(False)
    fault_tolerant.import_cad_and_part_management.options.surface.set_state(False)
    fault_tolerant.import_cad_and_part_management()

Describe geometry and flow
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    fault_tolerant.describe_geometry_and_flow.add_enclosure.set_state("No")
    fault_tolerant.describe_geometry_and_flow.close_caps.set_state("Yes")
    fault_tolerant.describe_geometry_and_flow.flow_type.set_state("Internal flow through the object")
    fault_tolerant.describe_geometry_and_flow.update_child_tasks(setup_type_changed=False)

    fault_tolerant.describe_geometry_and_flow.add_enclosure.set_state("No")
    fault_tolerant.describe_geometry_and_flow.close_caps.set_state("Yes")
    fault_tolerant.describe_geometry_and_flow.describe_geometry_and_flow_options.advanced_options.set_state(True)
    fault_tolerant.describe_geometry_and_flow.describe_geometry_and_flow_options.extract_edge_features.set_state("Yes")
    fault_tolerant.describe_geometry_and_flow.flow_type.set_state("Internal flow through the object")
    fault_tolerant.describe_geometry_and_flow.update_child_tasks(setup_type_changed=False)
    fault_tolerant.describe_geometry_and_flow()

Enclose fluid regions (capping)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    fault_tolerant.enclose_fluid_regions_fault.create_patch_preferences.show_create_patch_preferences.set_state(False)
    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("inlet-1")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(["inlet.1"])

    fault_tolerant.enclose_fluid_regions_fault.create_patch_preferences.show_create_patch_preferences.set_state(False)
    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("inlet-1")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_location.set_state([
                "1",
                "351.68205",
                "-361.34322",
                "-301.88668",
                "396.96205",
                "-332.84759",
                "-266.69751",
                "inlet.1",
            ])
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(["inlet.1"])
    fault_tolerant.enclose_fluid_regions_fault.add_child_to_task()
    fault_tolerant.enclose_fluid_regions_fault.insert_compound_child_task()
    fault_tolerant.enclose_fluid_regions_fault.arguments.set_state({})
    fault_tolerant.task("inlet-1")()

    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("inlet-2")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(["inlet.2"])

    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("inlet-2")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_location.set_state([
                "1",
                "441.68205",
                "-361.34322",
                "-301.88668",
                "486.96205",
                "-332.84759",
                "-266.69751",
                "inlet.2",
            ])
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(["inlet.2"])
    fault_tolerant.enclose_fluid_regions_fault.add_child_to_task()
    fault_tolerant.enclose_fluid_regions_fault.insert_compound_child_task()
    fault_tolerant.enclose_fluid_regions_fault.arguments.set_state({})
    fault_tolerant.task("inlet-2")()

    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("inlet-3")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(["inlet"])

    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("inlet-3")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_location.set_state([
                "1",
                "261.68205",
                "-361.34322",
                "-301.88668",
                "306.96205",
                "-332.84759",
                "-266.69751",
                "inlet",
            ])
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(["inlet"])
    fault_tolerant.enclose_fluid_regions_fault.add_child_to_task()
    fault_tolerant.enclose_fluid_regions_fault.insert_compound_child_task()
    fault_tolerant.enclose_fluid_regions_fault.arguments.set_state({})
    fault_tolerant.task("inlet-3")()

    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("outlet-1")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(["outlet"])
    fault_tolerant.enclose_fluid_regions_fault.zone_type.set_state("pressure-outlet")

    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("outlet-1")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_location.set_state([
                "1",
                "352.22702",
                "-197.8957",
                "84.102381",
                "394.41707",
                "-155.70565",
                "84.102381",
                "outlet",
            ])
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(["outlet"])
    fault_tolerant.enclose_fluid_regions_fault.zone_type.set_state("pressure-outlet")
    fault_tolerant.enclose_fluid_regions_fault.add_child_to_task()
    fault_tolerant.enclose_fluid_regions_fault.insert_compound_child_task()
    fault_tolerant.enclose_fluid_regions_fault.arguments.set_state({})
    fault_tolerant.task("outlet-1")()

Extract edge features
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    fault_tolerant.extract_edge_features.extract_method_type.set_state("Intersection Loops")
    fault_tolerant.extract_edge_features.object_selection_list.set_state(["flow_pipe", "main"])
    fault_tolerant.extract_edge_features.add_child_to_task()
    fault_tolerant.extract_edge_features.insert_compound_child_task()

    fault_tolerant.extract_edge_features.extract_edges_name.set_state("edge-group-1")
    fault_tolerant.extract_edge_features.extract_method_type.set_state("Intersection Loops")
    fault_tolerant.extract_edge_features.object_selection_list.set_state(["flow_pipe", "main"])

    fault_tolerant.extract_edge_features.arguments.set_state({})
    fault_tolerant.task("edge-group-1")()

Identify regions
~~~~~~~~~~~~~~~~

.. code:: python

    fault_tolerant.identify_regions.selection_type.set_state("zone")
    fault_tolerant.identify_regions.x.set_state(377.322045740589)
    fault_tolerant.identify_regions.y.set_state(-176.800676988458)
    fault_tolerant.identify_regions.z.set_state(-37.0764628583475)
    fault_tolerant.identify_regions.zone_selection_list.set_state(["main.1"])

    fault_tolerant.identify_regions.selection_type.set_state("zone")
    fault_tolerant.identify_regions.x.set_state(377.322045740589)
    fault_tolerant.identify_regions.y.set_state(-176.800676988458)
    fault_tolerant.identify_regions.z.set_state(-37.0764628583475)
    fault_tolerant.identify_regions.zone_location.set_state([
                "1",
                "213.32205",
                "-225.28068",
                "-158.25531",
                "541.32205",
                "-128.32068",
                "84.102381",
                "main.1",
            ])
    fault_tolerant.identify_regions.zone_selection_list.set_state(["main.1"])
    fault_tolerant.identify_regions.add_child_to_task()
    fault_tolerant.identify_regions.insert_compound_child_task()

    fault_tolerant.task("fluid-region-1").material_points_name.set_state("fluid-region-1")
    fault_tolerant.task("fluid-region-1").selection_type.set_state("zone")
    fault_tolerant.identify_regions.x.set_state(377.322045740589)
    fault_tolerant.identify_regions.y.set_state(-176.800676988458)
    fault_tolerant.identify_regions.z.set_state(-37.0764628583475)
    fault_tolerant.identify_regions.zone_location.set_state([
                "1",
                "213.32205",
                "-225.28068",
                "-158.25531",
                "541.32205",
                "-128.32068",
                "84.102381",
                "main.1",
            ])
    fault_tolerant.identify_regions.zone_selection_list.set_state(["main.1"])
    fault_tolerant.identify_regions.arguments.set_state({})
    fault_tolerant.task("fluid-region-1")()

    fault_tolerant.identify_regions.material_points_name.set_state("void-region-1")
    fault_tolerant.identify_regions.new_region_type.set_state("void")
    fault_tolerant.identify_regions.object_selection_list.set_state(["inlet-1", "inlet-2", "inlet-3", "main"])
    fault_tolerant.identify_regions.x.set_state(374.722045740589)
    fault_tolerant.identify_regions.y.set_state(-278.9775145640143)
    fault_tolerant.identify_regions.z.set_state(-161.1700719416913)
    fault_tolerant.identify_regions.add_child_to_task()
    fault_tolerant.identify_regions.insert_compound_child_task()
    fault_tolerant.identify_regions.arguments.set_state({})
    fault_tolerant.task("void-region-1")()

Define leakage threshold
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    fault_tolerant.define_leakage_threshold.add_child.set_state("yes")
    fault_tolerant.define_leakage_threshold.flip_direction.set_state(True)
    fault_tolerant.define_leakage_threshold.plane_direction.set_state("X")
    fault_tolerant.define_leakage_threshold.region_selection_single.set_state("void-region-1")
    fault_tolerant.define_leakage_threshold.add_child_to_task()
    fault_tolerant.define_leakage_threshold.insert_compound_child_task()

    fault_tolerant.task("leakage-1").arguments.set_state(
        {
            "AddChild": "yes",
            "FlipDirection": True,
            "LeakageName": "leakage-1",
            "PlaneDirection": "X",
            "RegionSelectionSingle": "void-region-1",
        }
    )

    fault_tolerant.define_leakage_threshold.add_child.set_state("yes")

    fault_tolerant.task("leakage-1")()

Update regions settings
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    fault_tolerant.update_region_settings.all_region_filter_categories.set_state(["2"] * 5 + ["1"] * 2)
    fault_tolerant.update_region_settings.all_region_leakage_size_list.set_state(["none"] * 6 + ["6.4"])
    fault_tolerant.update_region_settings.all_region_linked_construction_surface_list.set_state(["n/a"] * 6 + ["no"])
    fault_tolerant.update_region_settings.all_region_mesh_method_list.set_state(["none"] * 6 + ["wrap"])
    fault_tolerant.update_region_settings.all_region_name_list.set_state([
                "main",
                "flow_pipe",
                "outpipe3",
                "object2",
                "object1",
                "void-region-1",
                "fluid-region-1",
            ])
    fault_tolerant.update_region_settings.all_region_overset_componen_list.set_state(["no"] * 7)
    fault_tolerant.update_region_settings.all_region_source_list.set_state(["object"] * 5 + ["mpt"] * 2)
    fault_tolerant.update_region_settings.all_region_type_list.set_state(["void"] * 6 + ["fluid"])
    fault_tolerant.update_region_settings.all_region_volume_fill_list.set_state(["none"] * 6 + ["tet"])
    fault_tolerant.update_region_settings.filter_category.set_state("Identified Regions")
    fault_tolerant.update_region_settings.old_region_leakage_size_list.set_state([""])
    fault_tolerant.update_region_settings.old_region_mesh_method_list.set_state(["wrap"])
    fault_tolerant.update_region_settings.old_region_name_list.set_state(["fluid-region-1"])
    fault_tolerant.update_region_settings.old_region_overset_componen_list.set_state(["no"])
    fault_tolerant.update_region_settings.old_region_type_list.set_state(["fluid"])
    fault_tolerant.update_region_settings.old_region_volume_fill_list.set_state(["hexcore"])
    fault_tolerant.update_region_settings.region_leakage_size_list.set_state([""])
    fault_tolerant.update_region_settings.region_mesh_method_list.set_state(["wrap"])
    fault_tolerant.update_region_settings.region_name_list.set_state(["fluid-region-1"])
    fault_tolerant.update_region_settings.region_overset_componen_list.set_state(["no"])
    fault_tolerant.update_region_settings.region_type_list.set_state(["fluid"])
    fault_tolerant.update_region_settings.region_volume_fill_list.set_state(["tet"])
    fault_tolerant.update_region_settings()

Choose mesh control options
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    fault_tolerant.choose_mesh_control_options()

Generate surface mesh
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    fault_tolerant.generate_surface_mesh()

Update boundaries
~~~~~~~~~~~~~~~~~

.. code:: python

    fault_tolerant.update_boundaries_ftm()

Add boundary layers
~~~~~~~~~~~~~~~~~~~

.. code:: python

    fault_tolerant.add_boundary_layer_ftm.add_child_to_task()
    fault_tolerant.add_boundary_layer_ftm.insert_compound_child_task()
    fault_tolerant.task("aspect-ratio_1").bl_control_name.set_state("aspect-ratio_1")
    fault_tolerant.add_boundary_layer_ftm.arguments.set_state({})
    fault_tolerant.task("aspect-ratio_1")()

Generate volume mesh
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    fault_tolerant.create_volume_mesh.all_region_name_list.set_state([
                "main",
                "flow_pipe",
                "outpipe3",
                "object2",
                "object1",
                "void-region-1",
                "fluid-region-1",
            ])
    fault_tolerant.create_volume_mesh.all_region_size_list.set_state(["11.33375"] * 7)
    fault_tolerant.create_volume_mesh.all_region_volume_fill_list.set_state(["none"] * 6 + ["tet"])
    fault_tolerant.create_volume_mesh.enable_parallel.set_state(True)
    fault_tolerant.create_volume_mesh()

Switch to solution mode
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    solver = meshing.switch_to_solver()


2D meshing workflow
-------------------
Use the **2D** meshing workflow to mesh specific two-dimensional geometries.
The following example shows how to use the 2D meshing workflow.

Import geometry
~~~~~~~~~~~~~~~

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    import_file_name = examples.download_file('NACA0012.fmd', 'pyfluent/airfoils')
    meshing = pyfluent.launch_fluent(
        mode="meshing", precision=pyfluent.Precision.DOUBLE, processor_count=2
    )
    two_dim_mesh = meshing.two_dimensional_meshing()

    two_dim_mesh.load_cad_geometry_2d.file_name = import_file_name
    two_dim_mesh.load_cad_geometry_2d.length_unit = "mm"
    two_dim_mesh.load_cad_geometry_2d.refaceting.refacet = False
    two_dim_mesh.load_cad_geometry_2d()

Set regions and boundaries
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    two_dim_mesh.update_regions_2d()
    two_dim_mesh.update_boundaries_2d.selection_type = "zone"
    two_dim_mesh.update_boundaries_2d()

Define global sizing
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    two_dim_mesh.define_global_sizing_2d.curvature_normal_angle = 20
    two_dim_mesh.define_global_sizing_2d.max_size = 2000.0
    two_dim_mesh.define_global_sizing_2d.min_size = 5.0
    two_dim_mesh.define_global_sizing_2d.size_functions = "Curvature"
    two_dim_mesh.define_global_sizing_2d()

Adding BOI
~~~~~~~~~~

.. code:: python

    two_dim_mesh.add_local_sizing_2d.add_child = "yes"
    two_dim_mesh.add_local_sizing_2d.boi_control_name = "boi_1"
    two_dim_mesh.add_local_sizing_2d.boi_execution = "Body Of Influence"
    two_dim_mesh.add_local_sizing_2d.boi_face_label_list = ["boi"]
    two_dim_mesh.add_local_sizing_2d.boi_size = 50.0
    two_dim_mesh.add_local_sizing_2d.boi_zoneor_label = "label"
    two_dim_mesh.add_local_sizing_2d.draw_size_control = True
    two_dim_mesh.add_local_sizing_2d.add_child_and_update(defer_update=False)

Set edge sizing
~~~~~~~~~~~~~~~

.. code:: python

    two_dim_mesh.add_local_sizing_2d.add_child = "yes"
    two_dim_mesh.add_local_sizing_2d.boi_control_name = "edgesize_1"
    two_dim_mesh.add_local_sizing_2d.boi_execution = "Edge Size"
    two_dim_mesh.add_local_sizing_2d.boi_size = 5.0
    two_dim_mesh.add_local_sizing_2d.boi_zoneor_label = "label"
    two_dim_mesh.add_local_sizing_2d.draw_size_control = True
    two_dim_mesh.add_local_sizing_2d.edge_label_list = ["airfoil-te"]
    two_dim_mesh.add_local_sizing_2d.add_child_and_update(defer_update=False)

Set curvature sizing
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    two_dim_mesh.add_local_sizing_2d.add_child = "yes"
    two_dim_mesh.add_local_sizing_2d.boi_control_name = "curvature_1"
    two_dim_mesh.add_local_sizing_2d.boi_curvature_normal_angle = 10
    two_dim_mesh.add_local_sizing_2d.boi_execution = "Curvature"
    two_dim_mesh.add_local_sizing_2d.boi_max_size = 2
    two_dim_mesh.add_local_sizing_2d.boi_min_size = 1.5
    two_dim_mesh.add_local_sizing_2d.boi_scope_to = "edges"
    two_dim_mesh.add_local_sizing_2d.boi_zoneor_label = "label"
    two_dim_mesh.add_local_sizing_2d.draw_size_control = True
    two_dim_mesh.add_local_sizing_2d.edge_label_list = ["airfoil"]
    two_dim_mesh.add_local_sizing_2d.add_child_and_update(defer_update=False)

Add boundary layer
~~~~~~~~~~~~~~~~~~

.. code:: python

    two_dim_mesh.add_2d_boundary_layers.add_child = "yes"
    two_dim_mesh.add_2d_boundary_layers.bl_control_name = "aspect-ratio_1"
    two_dim_mesh.add_2d_boundary_layers.number_of_layers = 4
    two_dim_mesh.add_2d_boundary_layers.offset_method_type = "aspect-ratio"
    two_dim_mesh.add_2d_boundary_layers.add_child_and_update(defer_update=False)

Generate surface mesh
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    two_dim_mesh.generate_initial_surface_mesh.surface2_d_preferences.merge_edge_zones_based_on_labels = (
        "no"
    )
    two_dim_mesh.generate_initial_surface_mesh.surface2_d_preferences.merge_face_zones_based_on_labels = (
        "no"
    )
    two_dim_mesh.generate_initial_surface_mesh.surface2_d_preferences.show_advanced_options = (
        True
    )
    two_dim_mesh.generate_initial_surface_mesh()

    two_dim_mesh.task("aspect-ratio_1").revert()
    two_dim_mesh.task("aspect-ratio_1").add_child = "yes"
    two_dim_mesh.task("aspect-ratio_1").bl_control_name = "uniform_1"
    two_dim_mesh.task("aspect-ratio_1").first_layer_height = 2
    two_dim_mesh.task("aspect-ratio_1").number_of_layers = 4
    two_dim_mesh.task("aspect-ratio_1").offset_method_type = "uniform"
    two_dim_mesh.task("aspect-ratio_1")()

    two_dim_mesh.generate_initial_surface_mesh.surface2_d_preferences.merge_edge_zones_based_on_labels = (
        "no"
    )
    two_dim_mesh.generate_initial_surface_mesh.surface2_d_preferences.merge_face_zones_based_on_labels = (
        "no"
    )
    two_dim_mesh.generate_initial_surface_mesh.surface2_d_preferences.show_advanced_options = (
        True
    )
    two_dim_mesh.generate_initial_surface_mesh()

    two_dim_mesh.task("uniform_1").revert()
    two_dim_mesh.task("uniform_1").add_child = "yes"
    two_dim_mesh.task("uniform_1").bl_control_name = "smooth-transition_1"
    two_dim_mesh.task("uniform_1").first_layer_height = 2
    two_dim_mesh.task("uniform_1").number_of_layers = 7
    two_dim_mesh.task("uniform_1").offset_method_type = "smooth-transition"
    two_dim_mesh.task("uniform_1")()

    two_dim_mesh.generate_initial_surface_mesh.surface2_d_preferences.merge_edge_zones_based_on_labels = (
        "no"
    )
    two_dim_mesh.generate_initial_surface_mesh.surface2_d_preferences.merge_face_zones_based_on_labels = (
        "no"
    )
    two_dim_mesh.generate_initial_surface_mesh.surface2_d_preferences.show_advanced_options = (
        True
    )
    two_dim_mesh.generate_initial_surface_mesh()

Switch to solution mode
~~~~~~~~~~~~~~~~~~~~~~~

Switching to solver is not allowed in 2D Meshing mode.


Creating new meshing workflow
-----------------------------
Use the ``create_workflow()`` method to create a custom workflow.
The following example shows how to use this method.

Create workflow
~~~~~~~~~~~~~~~

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    import_file_name = examples.download_file('mixing_elbow.pmdb', 'pyfluent/mixing_elbow')
    meshing = pyfluent.launch_fluent(
        mode="meshing", precision=pyfluent.Precision.DOUBLE, processor_count=2
    )
    created_workflow = meshing.create_workflow()

Insert first task
~~~~~~~~~~~~~~~~~

.. code:: python

    created_workflow.insertable_tasks.import_geometry.insert()
    created_workflow.import_geometry.file_name.set_state(import_file_name)
    created_workflow.import_geometry.length_unit.set_state('in')
    created_workflow.import_geometry()

Insert next task
~~~~~~~~~~~~~~~~

.. code:: python

    created_workflow.import_geometry.insertable_tasks.add_local_sizing.insert()
    created_workflow.add_local_sizing()


Loading a saved meshing workflow
--------------------------------
Use the ``load_workflow()`` method to create a custom workflow.
The following example shows how to use this method.

Load workflow
~~~~~~~~~~~~~

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    saved_workflow_path = examples.download_file(
        "sample_watertight_workflow.wft", "pyfluent/meshing_workflow"
    )
    meshing = pyfluent.launch_fluent(
        mode="meshing", precision=pyfluent.Precision.DOUBLE, processor_count=2
    )
    loaded_workflow = meshing.load_workflow(file_path=saved_workflow_path)


Insert new task
---------------
You can insert new tasks into the meshing workflow in an object-oriented manner.

.. code:: python

    import ansys.fluent.core as pyfluent

    meshing = pyfluent.launch_fluent(
        mode="meshing", precision=pyfluent.Precision.DOUBLE, processor_count=2
    )
    watertight = meshing.watertight()
    watertight.import_geometry.insertable_tasks()
    watertight.import_geometry.insertable_tasks.set_up_rotational_periodic_boundaries.insert()

Duplicate tasks
~~~~~~~~~~~~~~~

.. code:: python

    watertight.import_geometry.insertable_tasks.import_boi_geometry.insert()
    watertight.import_geometry.insertable_tasks.import_boi_geometry.insert()
    assert watertight.import_boi_geometry.arguments()
    assert watertight.import_boi_geometry_1.arguments()


Current meshing workflow
------------------------
Use the ``current_workflow`` property to access an already loaded workflow.
The following example shows how to use this method.

Current workflow
~~~~~~~~~~~~~~~~

.. code:: python

    meshing.current_workflow

.. Note::
   The ``current_workflow`` property raises an attribute error when no workflow is initialized.


Mark as updated
---------------
Use the ``mark_as_updated()`` method to forcefully mark a task as updated.

.. code:: python

    watertight.import_geometry.mark_as_updated()


Sample use of ``arguments``
----------------------------
This simple example shows how to use the ``arguments`` attributes and explicit
attribute access methods in a watertight geometry meshing workflow.

.. Note::
   The ``command_arguments()`` method is deprecated.

.. code:: python

    >>> import ansys.fluent.core as pyfluent
    >>> from ansys.fluent.core import examples

    >>> import_file_name = examples.download_file("mixing_elbow.pmdb", "pyfluent/mixing_elbow")
    >>> meshing = pyfluent.launch_fluent(
    >>>     mode=pyfluent.FluentMode.MESHING,
    >>>     precision=pyfluent.Precision.DOUBLE,
    >>>     processor_count=2
    >>> )
    >>> watertight = meshing.watertight()

    >>> import_geometry = watertight.import_geometry
    >>> import_geometry.arguments()
    >>> import_geometry.arguments.file_name.is_read_only()
    >>> import_geometry.arguments.length_unit.is_active()
    >>> import_geometry.arguments.length_unit.allowed_values()
    >>> import_geometry.arguments.length_unit.default_value()
    >>> import_geometry.arguments.length_unit()
    >>> import_geometry.arguments.cad_import_options.one_zone_per()
    >>> import_geometry.arguments.cad_import_options.feature_angle.min()
