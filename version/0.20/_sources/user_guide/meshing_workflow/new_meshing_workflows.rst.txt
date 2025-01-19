.. _ref_user_guide_new_meshing_workflows:

Meshing workflow
================
You can use PyFluent to access the new, enhanced meshing workflows.

Watertight geometry meshing workflow
------------------------------------
Use the **Watertight Geometry** workflow for water-tight CAD geometries that
do not require much in the way of clean-up or modifications.
The following example shows you how to use the Watertight Geometry workflow.

Import geometry
~~~~~~~~~~~~~~~

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    import_file_name = examples.download_file('mixing_elbow.pmdb', 'pyfluent/mixing_elbow')
    meshing = pyfluent.launch_fluent(
        mode="meshing", precision='double', processor_count=2
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
Use the **Fault-tolerant** meshing workflow for more complicated non-water-tight CAD
geometries that may require some form of clean-up or modification (for example,
defects such as overlaps, intersections, holes, duplicates, etc).
The following example shows you how to use the fault-tolerant workflow.

Import CAD and part management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    import_file_name = examples.download_file(
        "exhaust_system.fmd", "pyfluent/exhaust_system"
    )
    meshing = pyfluent.launch_fluent(precision="double", processor_count=2, mode="meshing")
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

    fault_tolerant.generate_the_surface_mesh()

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

    fault_tolerant.generate_the_volume_mesh.all_region_name_list.set_state([
                "main",
                "flow_pipe",
                "outpipe3",
                "object2",
                "object1",
                "void-region-1",
                "fluid-region-1",
            ])
    fault_tolerant.generate_the_volume_mesh.all_region_size_list.set_state(["11.33375"] * 7)
    fault_tolerant.generate_the_volume_mesh.all_region_volume_fill_list.set_state(["none"] * 6 + ["tet"])
    fault_tolerant.generate_the_volume_mesh.enable_parallel.set_state(True)
    fault_tolerant.generate_the_volume_mesh()

Switch to solution mode
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    solver = meshing.switch_to_solver()
