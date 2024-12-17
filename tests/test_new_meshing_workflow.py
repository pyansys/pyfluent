import time
from typing import Iterable

import pytest

from ansys.fluent.core import FluentVersion, examples
from ansys.fluent.core.workflow import camel_to_snake_case


@pytest.mark.nightly
@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_new_watertight_workflow(new_meshing_session):
    # Import geometry
    import_file_name = examples.download_file(
        "mixing_elbow.pmdb", "pyfluent/mixing_elbow"
    )
    watertight = new_meshing_session.watertight()
    watertight.import_geometry.file_name.set_state(import_file_name)
    assert watertight.import_geometry.length_unit() == "mm"
    watertight.import_geometry.length_unit.set_state("in")
    assert watertight.import_geometry.length_unit.get_state() == "in"
    watertight.import_geometry()

    # Add local sizing
    watertight.add_local_sizing.add_child_to_task()
    watertight.add_local_sizing()

    # Generate surface mesh
    watertight.create_surface_mesh.cfd_surface_mesh_controls.max_size.set_state(0.3)
    assert watertight.create_surface_mesh.cfd_surface_mesh_controls.max_size() == 0.3
    watertight.create_surface_mesh()

    # Describe geometry
    watertight.describe_geometry.update_child_tasks(setup_type_changed=False)
    watertight.describe_geometry.setup_type.set_state(
        "The geometry consists of only fluid regions with no voids"
    )
    watertight.describe_geometry.update_child_tasks(setup_type_changed=True)
    watertight.describe_geometry()

    # Update boundaries
    watertight.update_boundaries.boundary_label_list.set_state(["wall-inlet"])
    watertight.update_boundaries.boundary_label_type_list.set_state(["wall"])
    watertight.update_boundaries.old_boundary_label_list.set_state(["wall-inlet"])
    watertight.update_boundaries.old_boundary_label_type_list.set_state(
        ["velocity-inlet"]
    )
    watertight.update_boundaries()

    # Update regions
    watertight.update_regions()

    # Add boundary layers
    watertight.add_boundary_layer.add_child_to_task()
    watertight.add_boundary_layer.insert_compound_child_task()
    watertight.add_boundary_layer.arguments = {}
    watertight.add_boundary_layer_child_1.bl_control_name.set_state(
        "smooth-transition_1"
    )
    watertight.add_boundary_layer_child_1()

    # Generate volume mesh
    watertight.create_volume_mesh.volume_fill.set_state("poly-hexcore")
    watertight.create_volume_mesh.volume_fill_controls.hex_max_cell_length.set_state(
        0.3
    )
    watertight.create_volume_mesh()

    # Switch to solution mode
    solver = new_meshing_session.switch_to_solver()
    assert solver


@pytest.mark.nightly
@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_new_fault_tolerant_workflow(new_meshing_session):
    meshing = new_meshing_session

    # Import CAD and part management
    import_file_name = examples.download_file(
        "exhaust_system.fmd", "pyfluent/exhaust_system"
    )
    fault_tolerant = meshing.fault_tolerant()
    meshing.PartManagement.InputFileChanged(
        FilePath=import_file_name, IgnoreSolidNames=False, PartPerBody=False
    )
    meshing.PMFileManagement.FileManager.LoadFiles()
    meshing.PartManagement.Node["Meshing Model"].Copy(
        Paths=[
            "/dirty_manifold-for-wrapper," + "1/dirty_manifold-for-wrapper,1/main,1",
            "/dirty_manifold-for-wrapper,"
            + "1/dirty_manifold-for-wrapper,1/flow-pipe,1",
            "/dirty_manifold-for-wrapper,"
            + "1/dirty_manifold-for-wrapper,1/outpipe3,1",
            "/dirty_manifold-for-wrapper," + "1/dirty_manifold-for-wrapper,1/object2,1",
            "/dirty_manifold-for-wrapper," + "1/dirty_manifold-for-wrapper,1/object1,1",
        ]
    )
    meshing.PartManagement.ObjectSetting["DefaultObjectSetting"].OneZonePer.set_state(
        "part"
    )
    fault_tolerant.import_cad_and_part_management.context.set_state(0)
    fault_tolerant.import_cad_and_part_management.create_object_per.set_state("Custom")
    fault_tolerant.import_cad_and_part_management.fmd_file_name.set_state(
        import_file_name
    )
    fault_tolerant.import_cad_and_part_management.file_loaded.set_state("yes")
    fault_tolerant.import_cad_and_part_management.object_setting.set_state(
        "DefaultObjectSetting"
    )
    fault_tolerant.import_cad_and_part_management.options.line.set_state(False)
    fault_tolerant.import_cad_and_part_management.options.solid.set_state(False)
    fault_tolerant.import_cad_and_part_management.options.surface.set_state(False)
    fault_tolerant.import_cad_and_part_management()

    # Describe geometry and flow
    fault_tolerant.describe_geometry_and_flow.add_enclosure.set_state("No")
    fault_tolerant.describe_geometry_and_flow.close_caps.set_state("Yes")
    fault_tolerant.describe_geometry_and_flow.flow_type.set_state(
        "Internal flow through the object"
    )
    fault_tolerant.describe_geometry_and_flow.update_child_tasks(
        setup_type_changed=False
    )

    fault_tolerant.describe_geometry_and_flow.add_enclosure.set_state("No")
    fault_tolerant.describe_geometry_and_flow.close_caps.set_state("Yes")
    fault_tolerant.describe_geometry_and_flow.describe_geometry_and_flow_options.advanced_options.set_state(
        True
    )
    fault_tolerant.describe_geometry_and_flow.describe_geometry_and_flow_options.extract_edge_features.set_state(
        "Yes"
    )
    fault_tolerant.describe_geometry_and_flow.flow_type.set_state(
        "Internal flow through the object"
    )
    fault_tolerant.describe_geometry_and_flow.update_child_tasks(
        setup_type_changed=False
    )
    fault_tolerant.describe_geometry_and_flow()

    # Enclose fluid regions (capping)
    fault_tolerant.enclose_fluid_regions_fault.create_patch_preferences.show_create_patch_preferences.set_state(
        False
    )
    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("inlet-1")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(
        ["inlet.1"]
    )

    fault_tolerant.enclose_fluid_regions_fault.create_patch_preferences.show_create_patch_preferences.set_state(
        False
    )
    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("inlet-1")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_location.set_state(
        [
            "1",
            "351.68205",
            "-361.34322",
            "-301.88668",
            "396.96205",
            "-332.84759",
            "-266.69751",
            "inlet.1",
        ]
    )
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(
        ["inlet.1"]
    )
    fault_tolerant.enclose_fluid_regions_fault.add_child_to_task()
    fault_tolerant.enclose_fluid_regions_fault.insert_compound_child_task()
    fault_tolerant.enclose_fluid_regions_fault.arguments.set_state({})
    fault_tolerant.enclose_fluid_regions_fault_child_1()

    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("inlet-2")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(
        ["inlet.2"]
    )

    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("inlet-2")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_location.set_state(
        [
            "1",
            "441.68205",
            "-361.34322",
            "-301.88668",
            "486.96205",
            "-332.84759",
            "-266.69751",
            "inlet.2",
        ]
    )
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(
        ["inlet.2"]
    )
    fault_tolerant.enclose_fluid_regions_fault.add_child_to_task()
    fault_tolerant.enclose_fluid_regions_fault.insert_compound_child_task()
    fault_tolerant.enclose_fluid_regions_fault.arguments.set_state({})
    fault_tolerant.enclose_fluid_regions_fault_child_2()

    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("inlet-3")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(["inlet"])

    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("inlet-3")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_location.set_state(
        [
            "1",
            "261.68205",
            "-361.34322",
            "-301.88668",
            "306.96205",
            "-332.84759",
            "-266.69751",
            "inlet",
        ]
    )
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(["inlet"])
    fault_tolerant.enclose_fluid_regions_fault.add_child_to_task()
    fault_tolerant.enclose_fluid_regions_fault.insert_compound_child_task()
    fault_tolerant.enclose_fluid_regions_fault.arguments.set_state({})
    fault_tolerant.enclose_fluid_regions_fault_child_3()

    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("outlet-1")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(["outlet"])
    fault_tolerant.enclose_fluid_regions_fault.zone_type.set_state("pressure-outlet")

    fault_tolerant.enclose_fluid_regions_fault.patch_name.set_state("outlet-1")
    fault_tolerant.enclose_fluid_regions_fault.selection_type.set_state("zone")
    fault_tolerant.enclose_fluid_regions_fault.zone_location.set_state(
        [
            "1",
            "352.22702",
            "-197.8957",
            "84.102381",
            "394.41707",
            "-155.70565",
            "84.102381",
            "outlet",
        ]
    )
    fault_tolerant.enclose_fluid_regions_fault.zone_selection_list.set_state(["outlet"])
    fault_tolerant.enclose_fluid_regions_fault.zone_type.set_state("pressure-outlet")
    fault_tolerant.enclose_fluid_regions_fault.add_child_to_task()
    fault_tolerant.enclose_fluid_regions_fault.insert_compound_child_task()
    fault_tolerant.enclose_fluid_regions_fault.arguments.set_state({})
    fault_tolerant.enclose_fluid_regions_fault_child_4()

    # Extract edge features
    fault_tolerant.extract_edge_features.extract_method_type.set_state(
        "Intersection Loops"
    )
    fault_tolerant.extract_edge_features.object_selection_list.set_state(
        ["flow_pipe", "main"]
    )
    fault_tolerant.extract_edge_features.add_child_to_task()
    fault_tolerant.extract_edge_features.insert_compound_child_task()

    fault_tolerant.extract_edge_features.extract_edges_name.set_state("edge-group-1")
    fault_tolerant.extract_edge_features.extract_method_type.set_state(
        "Intersection Loops"
    )
    fault_tolerant.extract_edge_features.object_selection_list.set_state(
        ["flow_pipe", "main"]
    )

    fault_tolerant.extract_edge_features.arguments.set_state({})
    fault_tolerant.extract_edge_features_child_1()

    # Identify regions
    fault_tolerant.identify_regions.selection_type.set_state("zone")
    fault_tolerant.identify_regions.x.set_state(377.322045740589)
    fault_tolerant.identify_regions.y.set_state(-176.800676988458)
    fault_tolerant.identify_regions.z.set_state(-37.0764628583475)
    fault_tolerant.identify_regions.zone_selection_list.set_state(["main.1"])

    fault_tolerant.identify_regions.selection_type.set_state("zone")
    fault_tolerant.identify_regions.x.set_state(377.322045740589)
    fault_tolerant.identify_regions.y.set_state(-176.800676988458)
    fault_tolerant.identify_regions.z.set_state(-37.0764628583475)
    fault_tolerant.identify_regions.zone_location.set_state(
        [
            "1",
            "213.32205",
            "-225.28068",
            "-158.25531",
            "541.32205",
            "-128.32068",
            "84.102381",
            "main.1",
        ]
    )
    fault_tolerant.identify_regions.zone_selection_list.set_state(["main.1"])
    fault_tolerant.identify_regions.add_child_to_task()
    fault_tolerant.identify_regions.insert_compound_child_task()
    fault_tolerant.identify_regions.x.set_state(377.322045740589)
    fault_tolerant.identify_regions.y.set_state(-176.800676988458)
    fault_tolerant.identify_regions.z.set_state(-37.0764628583475)

    fault_tolerant.identify_regions_child_1.material_points_name.set_state(
        "fluid-region-1"
    )
    fault_tolerant.identify_regions_child_1.selection_type.set_state("zone")
    fault_tolerant.identify_regions.zone_location.set_state(
        [
            "1",
            "213.32205",
            "-225.28068",
            "-158.25531",
            "541.32205",
            "-128.32068",
            "84.102381",
            "main.1",
        ]
    )
    fault_tolerant.identify_regions.zone_selection_list.set_state(["main.1"])
    fault_tolerant.identify_regions.arguments.set_state({})
    fault_tolerant.identify_regions_child_1()

    fault_tolerant.identify_regions.material_points_name.set_state("void-region-1")
    fault_tolerant.identify_regions.new_region_type.set_state("void")
    fault_tolerant.identify_regions.object_selection_list.set_state(
        ["inlet-1", "inlet-2", "inlet-3", "main"]
    )
    fault_tolerant.identify_regions.x.set_state(374.722045740589)
    fault_tolerant.identify_regions.y.set_state(-278.9775145640143)
    fault_tolerant.identify_regions.z.set_state(-161.1700719416913)
    fault_tolerant.identify_regions.add_child_to_task()
    fault_tolerant.identify_regions.insert_compound_child_task()
    fault_tolerant.identify_regions.arguments.set_state({})
    fault_tolerant.identify_regions_child_2()

    # Define leakage threshold
    fault_tolerant.define_leakage_threshold.add_child.set_state("yes")
    fault_tolerant.define_leakage_threshold.flip_direction.set_state(True)
    fault_tolerant.define_leakage_threshold.plane_direction.set_state("X")
    fault_tolerant.define_leakage_threshold.region_selection_single.set_state(
        "void-region-1"
    )
    fault_tolerant.define_leakage_threshold.add_child_to_task()
    fault_tolerant.define_leakage_threshold.insert_compound_child_task()

    fault_tolerant.define_leakage_threshold.add_child.set_state("yes")

    fault_tolerant.define_leakage_threshold_child_1.arguments.set_state(
        {
            "add_child": "yes",
            "flip_direction": True,
            "leakage_name": "leakage-1",
            "plane_direction": "X",
            "region_selection_single": "void-region-1",
        }
    )

    fault_tolerant.define_leakage_threshold_child_1()

    # Update regions settings
    fault_tolerant.update_region_settings.all_region_filter_categories.set_state(
        ["2"] * 5 + ["1"] * 2
    )
    fault_tolerant.update_region_settings.all_region_leakage_size_list.set_state(
        ["none"] * 6 + ["6.4"]
    )
    fault_tolerant.update_region_settings.all_region_linked_construction_surface_list.set_state(
        ["n/a"] * 6 + ["no"]
    )
    fault_tolerant.update_region_settings.all_region_mesh_method_list.set_state(
        ["none"] * 6 + ["wrap"]
    )
    fault_tolerant.update_region_settings.all_region_name_list.set_state(
        [
            "main",
            "flow_pipe",
            "outpipe3",
            "object2",
            "object1",
            "void-region-1",
            "fluid-region-1",
        ]
    )
    fault_tolerant.update_region_settings.all_region_overset_componen_list.set_state(
        ["no"] * 7
    )
    fault_tolerant.update_region_settings.all_region_source_list.set_state(
        ["object"] * 5 + ["mpt"] * 2
    )
    fault_tolerant.update_region_settings.all_region_type_list.set_state(
        ["void"] * 6 + ["fluid"]
    )
    fault_tolerant.update_region_settings.all_region_volume_fill_list.set_state(
        ["none"] * 6 + ["tet"]
    )
    fault_tolerant.update_region_settings.filter_category.set_state(
        "Identified Regions"
    )
    fault_tolerant.update_region_settings.old_region_leakage_size_list.set_state([""])
    fault_tolerant.update_region_settings.old_region_mesh_method_list.set_state(
        ["wrap"]
    )
    fault_tolerant.update_region_settings.old_region_name_list.set_state(
        ["fluid-region-1"]
    )
    fault_tolerant.update_region_settings.old_region_overset_componen_list.set_state(
        ["no"]
    )
    fault_tolerant.update_region_settings.old_region_type_list.set_state(["fluid"])
    fault_tolerant.update_region_settings.old_region_volume_fill_list.set_state(
        ["hexcore"]
    )
    fault_tolerant.update_region_settings.region_leakage_size_list.set_state([""])
    fault_tolerant.update_region_settings.region_mesh_method_list.set_state(["wrap"])
    fault_tolerant.update_region_settings.region_name_list.set_state(["fluid-region-1"])
    fault_tolerant.update_region_settings.region_overset_componen_list.set_state(["no"])
    fault_tolerant.update_region_settings.region_type_list.set_state(["fluid"])
    fault_tolerant.update_region_settings.region_volume_fill_list.set_state(["tet"])
    fault_tolerant.update_region_settings()

    # Choose mesh control options
    fault_tolerant.choose_mesh_control_options()

    # Generate surface mesh
    if meshing.get_fluent_version() < FluentVersion.v251:
        fault_tolerant.generate_the_surface_mesh()
    else:
        fault_tolerant.generate_surface_mesh()

    # Update boundaries
    fault_tolerant.update_boundaries_ftm()

    # Add boundary layers
    fault_tolerant.add_boundary_layer_ftm.add_child_to_task()
    fault_tolerant.add_boundary_layer_ftm.insert_compound_child_task()
    fault_tolerant.add_boundary_layer_ftm.arguments.set_state({})
    fault_tolerant.add_boundary_layer_ftm_child_1.bl_control_name.set_state(
        "aspect-ratio_1"
    )
    fault_tolerant.add_boundary_layer_ftm_child_1()

    # Generate volume mesh
    if meshing.get_fluent_version() < FluentVersion.v251:
        generate_volume_mesh = fault_tolerant.generate_the_volume_mesh
    else:
        generate_volume_mesh = fault_tolerant.create_volume_mesh
    generate_volume_mesh.all_region_name_list.set_state(
        [
            "main",
            "flow_pipe",
            "outpipe3",
            "object2",
            "object1",
            "void-region-1",
            "fluid-region-1",
        ]
    )
    generate_volume_mesh.all_region_size_list.set_state(["11.33375"] * 7)
    generate_volume_mesh.all_region_volume_fill_list.set_state(["none"] * 6 + ["tet"])
    generate_volume_mesh.enable_parallel.set_state(True)
    generate_volume_mesh()

    # Generate volume mesh
    solver = meshing.switch_to_solver()
    assert solver


@pytest.mark.nightly
@pytest.mark.codegen_required
@pytest.mark.fluent_version("==24.2")
def test_new_2d_meshing_workflow(new_meshing_session):
    # Import geometry
    import_file_name = examples.download_file("NACA0012.fmd", "pyfluent/airfoils")
    two_dim_mesh = new_meshing_session.two_dimensional_meshing()

    two_dim_mesh.load_cad_geometry_2d.file_name = import_file_name
    two_dim_mesh.load_cad_geometry_2d.length_unit = "mm"
    two_dim_mesh.load_cad_geometry_2d.refaceting.refacet = False
    two_dim_mesh.load_cad_geometry_2d()

    # Set regions and boundaries
    two_dim_mesh.update_regions_2d()
    two_dim_mesh.update_boundaries_2d.selection_type = "zone"
    two_dim_mesh.update_boundaries_2d()

    # Define global sizing
    two_dim_mesh.define_global_sizing_2d.curvature_normal_angle = 20
    two_dim_mesh.define_global_sizing_2d.max_size = 2000.0
    two_dim_mesh.define_global_sizing_2d.min_size = 5.0
    two_dim_mesh.define_global_sizing_2d.size_functions = "Curvature"
    two_dim_mesh.define_global_sizing_2d()

    # Add local sizing
    two_dim_mesh.add_local_sizing_2d.add_child = "yes"
    two_dim_mesh.add_local_sizing_2d.boi_control_name = "boi_1"
    two_dim_mesh.add_local_sizing_2d.boi_execution = "Body Of Influence"
    two_dim_mesh.add_local_sizing_2d.boi_face_label_list = ["boi"]
    two_dim_mesh.add_local_sizing_2d.boi_size = 50.0
    two_dim_mesh.add_local_sizing_2d.boi_zoneor_label = "label"
    two_dim_mesh.add_local_sizing_2d.draw_size_control = True
    two_dim_mesh.add_local_sizing_2d.add_child_and_update(defer_update=False)

    two_dim_mesh.add_local_sizing_2d.add_child = "yes"
    two_dim_mesh.add_local_sizing_2d.boi_control_name = "edgesize_1"
    two_dim_mesh.add_local_sizing_2d.boi_execution = "Edge Size"
    two_dim_mesh.add_local_sizing_2d.boi_size = 5.0
    two_dim_mesh.add_local_sizing_2d.boi_zoneor_label = "label"
    two_dim_mesh.add_local_sizing_2d.draw_size_control = True
    two_dim_mesh.add_local_sizing_2d.edge_label_list = ["airfoil-te"]
    two_dim_mesh.add_local_sizing_2d.add_child_and_update(defer_update=False)

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

    # Add boundary layer
    two_dim_mesh.add_2d_boundary_layers.add_child = "yes"
    two_dim_mesh.add_2d_boundary_layers.bl_control_name = "aspect-ratio_1"
    two_dim_mesh.add_2d_boundary_layers.number_of_layers = 4
    two_dim_mesh.add_2d_boundary_layers.offset_method_type = "aspect-ratio"
    two_dim_mesh.add_2d_boundary_layers.add_child_and_update(defer_update=False)

    two_dim_mesh.generate_initial_surface_mesh.surface_2d_preferences.merge_edge_zones_based_on_labels = (
        "no"
    )
    two_dim_mesh.generate_initial_surface_mesh.surface_2d_preferences.merge_face_zones_based_on_labels = (
        "no"
    )
    two_dim_mesh.generate_initial_surface_mesh.surface_2d_preferences.show_advanced_options = (
        True
    )
    two_dim_mesh.generate_initial_surface_mesh()

    two_dim_mesh.add_2d_boundary_layers_child_1.revert()
    two_dim_mesh.add_2d_boundary_layers_child_1.add_child = "yes"
    two_dim_mesh.add_2d_boundary_layers_child_1.bl_control_name = "uniform_1"
    two_dim_mesh.add_2d_boundary_layers_child_1.first_layer_height = 2
    two_dim_mesh.add_2d_boundary_layers_child_1.number_of_layers = 4
    two_dim_mesh.add_2d_boundary_layers_child_1.offset_method_type = "uniform"
    two_dim_mesh.add_2d_boundary_layers_child_1()

    two_dim_mesh.generate_initial_surface_mesh.surface_2d_preferences.merge_edge_zones_based_on_labels = (
        "no"
    )
    two_dim_mesh.generate_initial_surface_mesh.surface_2d_preferences.merge_face_zones_based_on_labels = (
        "no"
    )
    two_dim_mesh.generate_initial_surface_mesh.surface_2d_preferences.show_advanced_options = (
        True
    )
    two_dim_mesh.generate_initial_surface_mesh()

    two_dim_mesh._task("uniform_1").revert()
    two_dim_mesh._task("uniform_1").add_child = "yes"
    two_dim_mesh._task("uniform_1").bl_control_name = "smooth-transition_1"
    two_dim_mesh._task("uniform_1").first_layer_height = 2
    two_dim_mesh._task("uniform_1").number_of_layers = 7
    two_dim_mesh._task("uniform_1").offset_method_type = "smooth-transition"
    two_dim_mesh._task("uniform_1")()

    two_dim_mesh.generate_initial_surface_mesh.surface_2d_preferences.merge_edge_zones_based_on_labels = (
        "no"
    )
    two_dim_mesh.generate_initial_surface_mesh.surface_2d_preferences.merge_face_zones_based_on_labels = (
        "no"
    )
    two_dim_mesh.generate_initial_surface_mesh.surface_2d_preferences.show_advanced_options = (
        True
    )
    two_dim_mesh.generate_initial_surface_mesh()

    # Switch to solution mode
    solver = new_meshing_session.switch_to_solver()
    assert solver


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=23.2")
def test_updating_state_in_new_meshing_workflow(new_meshing_session):
    # Import geometry
    import_file_name = examples.download_file(
        "mixing_elbow.pmdb", "pyfluent/mixing_elbow"
    )
    watertight = new_meshing_session.watertight()
    assert watertight.import_geometry.length_unit() == "mm"
    assert watertight.import_geometry.cad_import_options.feature_angle() == 40.0
    assert (
        watertight.import_geometry.cad_import_options.one_zone_per.allowed_values()
        == ["body", "face", "object"]
    )
    assert watertight.import_geometry.cad_import_options.one_zone_per() == "body"
    watertight.import_geometry.arguments = {
        "file_name": import_file_name,
        "length_unit": "in",
        "cad_import_options": {"feature_angle": 35, "one_zone_per": "object"},
    }
    assert watertight.import_geometry.cad_import_options.feature_angle() == 35.0
    assert (
        watertight.import_geometry.cad_import_options.one_zone_per.get_state()
        == "object"
    )
    assert watertight.import_geometry.length_unit.get_state() == "in"
    watertight.import_geometry.cad_import_options.feature_angle = 25.0
    assert watertight.import_geometry.cad_import_options.feature_angle() == 25.0
    watertight.import_geometry.cad_import_options.one_zone_per = "face"
    assert watertight.import_geometry.cad_import_options.one_zone_per() == "face"
    watertight.import_geometry()


def _assert_snake_case_attrs(attrs: Iterable):
    for attr in attrs:
        assert str(attr).islower()


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=23.2")
def test_snake_case_attrs_in_new_meshing_workflow(new_meshing_session):
    # Import geometry
    import_file_name = examples.download_file(
        "mixing_elbow.pmdb", "pyfluent/mixing_elbow"
    )
    watertight = new_meshing_session.watertight()
    dir_watertight = dir(watertight)
    dir_watertight.remove("_FirstTask")
    _assert_snake_case_attrs(dir_watertight)
    dir_watertight_import_geometry = dir(watertight.import_geometry)
    dir_watertight_import_geometry.remove("_NextTask")
    _assert_snake_case_attrs(dir_watertight_import_geometry)
    _assert_snake_case_attrs(watertight.import_geometry.arguments())
    _assert_snake_case_attrs(watertight.import_geometry.cad_import_options())
    _assert_snake_case_attrs(dir(watertight.import_geometry.cad_import_options))
    watertight.import_geometry.file_name.set_state(import_file_name)
    watertight.import_geometry.length_unit = "in"
    watertight.import_geometry()


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_workflow_and_data_model_methods_new_meshing_workflow(new_meshing_session):
    # Import geometry
    meshing = new_meshing_session
    import_file_name = examples.download_file(
        "mixing_elbow.pmdb", "pyfluent/mixing_elbow"
    )
    watertight = meshing.watertight()

    # Checks if any of the unwanted attrs are present in dir call
    assert (set(dir(watertight)) - watertight._unwanted_attrs) == set(dir(watertight))

    for attr in watertight._unwanted_attrs:
        with pytest.raises(AttributeError):
            getattr(watertight, attr)

    watertight.import_geometry.rename(new_name="import_geom_wtm")
    assert "import_geometry" not in watertight.task_names()
    assert "import_geom_wtm" in watertight.task_names()
    assert len(watertight.tasks()) == 11
    watertight.import_geom_wtm.file_name = import_file_name
    watertight.import_geom_wtm.length_unit = "in"
    watertight.import_geom_wtm()
    _next_possible_tasks = [
        "<Insertable 'import_boi_geometry' task>",
        "<Insertable 'set_up_rotational_periodic_boundaries' task>",
        "<Insertable 'create_local_refinement_regions' task>",
        "<Insertable 'custom_journal_task' task>",
    ]
    assert sorted(
        [repr(x) for x in watertight.import_geom_wtm.insertable_tasks()]
    ) == sorted(_next_possible_tasks)
    watertight.import_geom_wtm.insertable_tasks.import_boi_geometry.insert()
    assert sorted(
        [repr(x) for x in watertight.import_geom_wtm.insertable_tasks()]
    ) == sorted(_next_possible_tasks)
    watertight.import_geom_wtm.insertable_tasks.set_up_rotational_periodic_boundaries.insert()
    assert len(watertight.tasks()) == 13


@pytest.mark.fluent_version(">=23.2")
@pytest.mark.codegen_required
def test_watertight_workflow(mixing_elbow_geometry_filename, new_meshing_session):
    watertight = new_meshing_session.watertight()
    watertight.import_geometry.file_name = mixing_elbow_geometry_filename
    watertight.import_geometry()
    add_local_sizing = watertight.add_local_sizing
    assert not add_local_sizing.tasks()
    add_local_sizing._add_child(state={"boi_face_label_list": ["cold-inlet"]})
    assert not add_local_sizing.tasks()
    added_sizing = add_local_sizing.add_child_and_update(
        state={"boi_face_label_list": ["elbow-fluid"]}
    )
    assert len(add_local_sizing.tasks()) == 1
    assert added_sizing
    assert added_sizing.boi_face_label_list() == ["elbow-fluid"]


@pytest.mark.fluent_version(">=23.2")
@pytest.mark.codegen_required
def test_watertight_workflow_children(
    mixing_elbow_geometry_filename, new_meshing_session
):
    watertight = new_meshing_session.watertight()
    watertight.import_geometry.file_name = mixing_elbow_geometry_filename
    watertight.import_geometry()
    add_local_sizing = watertight.add_local_sizing
    assert not add_local_sizing.tasks()
    add_local_sizing._add_child(state={"boi_face_label_list": ["cold-inlet"]})
    assert not add_local_sizing.tasks()
    added_sizing = add_local_sizing.add_child_and_update(
        state={"boi_face_label_list": ["elbow-fluid"]}
    )
    assert len(add_local_sizing.tasks()) == 1
    assert added_sizing
    assert added_sizing.boi_face_label_list() == ["elbow-fluid"]
    assert added_sizing.name() == "facesize_1"
    assert len(added_sizing.arguments())
    added_sizing_by_name = add_local_sizing.compound_child("facesize_1")
    added_sizing_by_pos = add_local_sizing.last_child()
    assert added_sizing.arguments() == added_sizing_by_name.arguments()
    assert added_sizing.arguments() == added_sizing_by_pos.arguments()
    assert added_sizing.python_name() == "add_local_sizing_child_1"
    describe_geometry = watertight.describe_geometry
    describe_geometry_children = describe_geometry.tasks()
    assert len(describe_geometry_children) == 2
    describe_geometry_child_task_python_names = describe_geometry.task_names()
    assert describe_geometry_child_task_python_names == [
        "enclose_fluid_regions",
        "create_regions",
    ]


@pytest.mark.fluent_version(">=24.1")
@pytest.mark.codegen_required
def test_watertight_workflow_dynamic_interface(
    mixing_elbow_geometry_filename, new_meshing_session
):
    watertight = new_meshing_session.watertight()
    watertight.import_geometry.file_name = mixing_elbow_geometry_filename
    watertight.import_geometry()
    create_volume_mesh = watertight.create_volume_mesh
    assert create_volume_mesh is not None
    watertight.delete_tasks(list_of_tasks=["create_volume_mesh"])
    assert "create_volume_mesh" not in watertight.task_names()

    assert sorted(
        [repr(x) for x in watertight.add_boundary_layer.insertable_tasks()]
    ) == sorted(
        [
            "<Insertable 'add_boundary_type' task>",
            "<Insertable 'update_boundaries' task>",
            "<Insertable 'set_up_rotational_periodic_boundaries' task>",
            "<Insertable 'modify_mesh_refinement' task>",
            "<Insertable 'improve_surface_mesh' task>",
            "<Insertable 'create_volume_mesh' task>",
            "<Insertable 'manage_zones_ftm' task>",
            "<Insertable 'update_regions' task>",
            "<Insertable 'custom_journal_task' task>",
        ]
    )
    watertight.add_boundary_layer.insertable_tasks.create_volume_mesh.insert()
    assert "create_volume_mesh" in watertight.task_names()
    create_volume_mesh = watertight.create_volume_mesh
    assert create_volume_mesh is not None

    assert (
        watertight.describe_geometry.create_regions.arguments()[
            "number_of_flow_volumes"
        ]
        == 1
    )
    watertight.delete_tasks(list_of_tasks=["create_regions"])
    assert "create_regions" not in watertight.task_names()
    assert watertight.describe_geometry.enclose_fluid_regions
    watertight.describe_geometry.enclose_fluid_regions.delete()
    assert "enclose_fluid_regions" not in watertight.task_names()
    watertight.create_volume_mesh.delete()
    assert "create_volume_mesh" not in watertight.task_names()


@pytest.mark.fluent_version("==23.2")
@pytest.mark.codegen_required
def test_fault_tolerant_workflow(exhaust_system_geometry_filename, new_meshing_session):
    fault_tolerant = new_meshing_session.fault_tolerant()
    part_management = fault_tolerant.part_management
    file_name = exhaust_system_geometry_filename
    part_management.LoadFmdFile(FilePath=file_name)
    part_management.MoveCADComponentsToNewObject(
        Paths=[r"/Bottom,1", r"/Left,1", r"/Others,1", r"/Right,1", r"/Top,1"]
    )
    part_management.Node["Object"].Rename(NewName=r"Engine")
    import_cad = fault_tolerant.import_cad_and_part_management
    import_cad.Arguments.setState(
        {
            r"CreateObjectPer": r"Custom",
            r"FMDFileName": file_name,
            r"FileLoaded": r"yes",
            r"ObjectSetting": r"DefaultObjectSetting",
        }
    )
    import_cad()


@pytest.mark.fluent_version(">=23.2")
@pytest.mark.codegen_required
def test_extended_wrapper(new_meshing_session, mixing_elbow_geometry_filename):
    watertight = new_meshing_session.watertight()
    import_geometry = watertight.import_geometry
    assert import_geometry.Arguments() == {}
    import_geometry.Arguments = dict(FileName=mixing_elbow_geometry_filename)
    assert 8 < len(import_geometry.arguments.get_state()) < 15
    assert len(import_geometry.arguments.get_state(explicit_only=True)) == 1
    import_geometry.arguments.set_state(dict(file_name=None))
    time.sleep(5)
    assert import_geometry.arguments.get_state(explicit_only=True) == dict(
        file_name=None
    )
    assert import_geometry.arguments.get_state()["file_name"] is None
    import_geometry.arguments.set_state(dict(file_name=mixing_elbow_geometry_filename))
    time.sleep(5)
    assert import_geometry.arguments.get_state(explicit_only=True) == dict(
        file_name=mixing_elbow_geometry_filename
    )
    assert import_geometry.file_name() == mixing_elbow_geometry_filename
    import_geometry.file_name.set_state("bob")
    time.sleep(5)
    assert import_geometry.file_name() == "bob"
    import_geometry.file_name.set_state(mixing_elbow_geometry_filename)
    import_geometry()
    add_local_sizing = watertight.add_local_sizing
    assert not add_local_sizing.tasks()
    # new_meshing_session.workflow.TaskObject["Add Local Sizing"]._add_child(state={"BOIFaceLabelList": ["elbow-fluid"]})
    add_local_sizing._add_child(state={"boi_face_label_list": ["cold-inlet"]})
    assert not add_local_sizing.tasks()

    added_sizing = add_local_sizing.add_child_and_update(
        state={"boi_face_label_list": ["elbow-fluid"]}
    )
    assert len(add_local_sizing.tasks()) == 1
    assert added_sizing
    assert added_sizing.boi_face_label_list() == ["elbow-fluid"]
    # restart
    watertight = new_meshing_session.watertight()
    assert import_geometry.state() == "Out-of-date"
    import_geometry(FileName=mixing_elbow_geometry_filename, AppendMesh=False)
    assert import_geometry.state() == "Up-to-date"
    import_geometry_state = import_geometry.arguments()
    assert len(import_geometry_state) > 2


@pytest.mark.fluent_version(">=23.1")
@pytest.mark.skip
def test_meshing_workflow_structure(new_meshing_session):
    """
    o Workflow
    |
    |--o Import Geometry
    |
    |--o Add Local Sizing
    |
    |--o Generate the Surface Mesh
    |
    |--o Describe Geometry
    |  |
    |  |--o Enclose Fluid Regions (Capping)
    |  |
    |  |--o Create Regions
    |
    |--o Update Regions
    |
    |--o Add Boundary Layers
    |
    |--o Generate the Volume Mesh
    """
    w = new_meshing_session.workflow
    w.InitializeWorkflow(WorkflowType="Watertight Geometry")

    task_names = (
        "Import Geometry",
        "Add Local Sizing",
        "Generate the Surface Mesh",
        "Describe Geometry",
        "Enclose Fluid Regions (Capping)",
        "Create Regions",
        "Update Regions",
        "Add Boundary Layers",
        "Generate the Volume Mesh",
    )

    (
        import_geom,
        add_sizing,
        gen_surf_mesh,
        describe_geometry,
        cap,
        create_regions,
        update_regions,
        add_boundary_layers,
        gen_vol_mesh,
    ) = all_tasks = [w._task(name) for name in task_names]

    def upstream_names(task):
        return {upstream.name() for upstream in task.get_direct_upstream_tasks()}

    def downstream_names(task):
        return {downstream.name() for downstream in task.get_direct_downstream_tasks()}

    assert upstream_names(import_geom) == set()
    assert downstream_names(import_geom) == {
        "Generate the Surface Mesh",
        "Add Local Sizing",
    }

    assert upstream_names(add_sizing) == {"Import Geometry"}
    assert downstream_names(add_sizing) == {"Generate the Surface Mesh"}

    assert upstream_names(gen_surf_mesh) == {"Import Geometry", "Add Local Sizing"}
    assert downstream_names(gen_surf_mesh) == {
        "Describe Geometry",
        "Add Boundary Layers",
        "Generate the Volume Mesh",
    }

    assert upstream_names(describe_geometry) == {
        "Generate the Surface Mesh",
        "Add Boundary Layers",
    }
    assert downstream_names(describe_geometry) == {
        "Update Regions",
        "Add Boundary Layers",
        "Generate the Volume Mesh",
    }

    assert upstream_names(cap) == {
        "Describe Geometry",
        "Add Boundary Layers",
        "Generate the Surface Mesh",
    }
    assert downstream_names(cap) == {
        "Describe Geometry",
        "Add Boundary Layers",
        "Generate the Volume Mesh",
    }

    assert upstream_names(create_regions) == {
        "Describe Geometry",
        "Add Boundary Layers",
        "Generate the Surface Mesh",
    }
    assert downstream_names(create_regions) == {
        "Describe Geometry",
        "Add Boundary Layers",
        "Generate the Volume Mesh",
        "Update Regions",
    }

    assert upstream_names(update_regions) == {"Describe Geometry"}
    assert downstream_names(update_regions) == {"Generate the Volume Mesh"}

    assert upstream_names(add_boundary_layers) == {
        "Describe Geometry",
        "Generate the Surface Mesh",
    }
    assert downstream_names(add_boundary_layers) == {
        "Describe Geometry",
        "Generate the Volume Mesh",
    }

    assert upstream_names(gen_vol_mesh) == {
        "Update Regions",
        "Describe Geometry",
        "Add Boundary Layers",
        "Generate the Surface Mesh",
    }
    assert downstream_names(gen_vol_mesh) == set()

    for task in all_tasks:
        assert {sub_task.name() for sub_task in task.tasks()} == (
            {
                "Enclose Fluid Regions (Capping)",
                "Create Regions",
            }
            if task is describe_geometry
            else set()
        )

    for task in all_tasks:
        assert {sub_task.name() for sub_task in task.inactive_tasks()} == (
            {
                "Apply Share Topology",
                "Update Boundaries",
            }
            if task is describe_geometry
            else set()
        )

    task_ids = [task.get_id() for task in all_tasks]
    # uniqueness test
    assert len(set(task_ids)) == len(task_ids)
    # ordering test
    idxs = [int(id[len("TaskObject") :]) for id in task_ids]
    assert sorted(idxs) == idxs
    """Given the workflow::

            Workflow
            ├── Import Geometry
            ├── Add Local Sizing
            ├── Generate the Surface Mesh ── Insert Next Task
                                            ├── Add Boundary Type
                                            ├── Update Boundaries
                                            ├── ...
    """
    assert set(gen_surf_mesh.GetNextPossibleTasks()) == {
        "AddBoundaryType",
        "UpdateBoundaries",
        "SetUpPeriodicBoundaries",
        "LinearMeshPattern",
        "ManageZones",
        "ModifyMeshRefinement",
        "ImproveSurfaceMesh",
        "RunCustomJournal",
    }

    children = w.tasks()
    expected_task_order = (
        "Import Geometry",
        "Add Local Sizing",
        "Generate the Surface Mesh",
        "Describe Geometry",
        "Update Regions",
        "Add Boundary Layers",
        "Generate the Volume Mesh",
    )

    actual_task_order = tuple(child.name() for child in children)

    assert actual_task_order == expected_task_order

    assert [child.name() for child in children[3].tasks()] == [
        "Enclose Fluid Regions (Capping)",
        "Create Regions",
    ]

    gen_surf_mesh.InsertNextTask(CommandName="AddBoundaryType")

    children = w.tasks()
    expected_task_order = (
        "Import Geometry",
        "Add Local Sizing",
        "Generate the Surface Mesh",
        "Add Boundary Type",
        "Describe Geometry",
        "Update Regions",
        "Add Boundary Layers",
        "Generate the Volume Mesh",
    )

    actual_task_order = tuple(child.name() for child in children)

    assert actual_task_order == expected_task_order

    assert [child.name() for child in children[4].tasks()] == [
        "Enclose Fluid Regions (Capping)",
        "Create Regions",
    ]


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=23.2")
def test_new_workflow_structure(new_meshing_session):
    meshing = new_meshing_session
    watertight = meshing.watertight()
    assert watertight.import_geometry.arguments()
    with pytest.raises(AttributeError):
        watertight.TaskObject["Import Geometry"]


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=23.2")
def test_attrs_in_watertight_meshing_workflow(new_meshing_session):
    # Import geometry
    import_file_name = examples.download_file(
        "mixing_elbow.pmdb", "pyfluent/mixing_elbow"
    )
    watertight = new_meshing_session.watertight()
    unwanted_attrs = {"fault_tolerant", "part_management", "pm_file_management"}
    assert set(dir(watertight)) - unwanted_attrs == set(dir(watertight))

    for attr in unwanted_attrs:
        with pytest.raises(AttributeError):
            getattr(watertight, attr)

    watertight.import_geometry.file_name.set_state(import_file_name)
    watertight.import_geometry.length_unit = "in"
    watertight.import_geometry()

    assert watertight.import_geometry.file_name()
    # Reinitialize the workflow:
    watertight = new_meshing_session.watertight()
    assert not watertight.import_geometry.file_name()


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=23.2")
def test_ordered_children_in_enhanced_meshing_workflow(new_meshing_session):
    watertight = new_meshing_session.watertight()
    assert set([repr(x) for x in watertight.tasks()]) == {
        "<Task 'Add Boundary Layers'>",
        "<Task 'Add Local Sizing'>",
        "<Task 'Apply Share Topology'>",
        "<Task 'Create Regions'>",
        "<Task 'Describe Geometry'>",
        "<Task 'Enclose Fluid Regions (Capping)'>",
        "<Task 'Generate the Surface Mesh'>",
        "<Task 'Generate the Volume Mesh'>",
        "<Task 'Import Geometry'>",
        "<Task 'Update Boundaries'>",
        "<Task 'Update Regions'>",
    }


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=23.2")
def test_attrs_in_fault_tolerant_meshing_workflow(new_meshing_session):
    # Import CAD
    import_file_name = examples.download_file(
        "exhaust_system.fmd", "pyfluent/exhaust_system"
    )

    fault_tolerant = new_meshing_session.fault_tolerant()
    assert "watertight" not in dir(fault_tolerant)

    with pytest.raises(AttributeError):
        fault_tolerant.watertight()

    fault_tolerant.import_cad_and_part_management.context.set_state(0)
    fault_tolerant.import_cad_and_part_management.create_object_per.set_state("Custom")
    fault_tolerant.import_cad_and_part_management.fmd_file_name.set_state(
        import_file_name
    )

    assert fault_tolerant.import_cad_and_part_management.fmd_file_name()
    # Reinitialize the workflow:
    fault_tolerant = new_meshing_session.fault_tolerant()
    assert not fault_tolerant.import_cad_and_part_management.fmd_file_name()


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=23.2")
def test_switch_between_workflows(new_meshing_session):
    meshing = new_meshing_session

    # Initialize to watertight and store
    watertight = meshing.watertight()

    assert watertight.import_geometry.arguments()

    # Wrong Attribute
    with pytest.raises(AttributeError):
        watertight.import_cad_and_part_management.arguments()

    # Initialize to fault-tolerant and store
    fault_tolerant = meshing.fault_tolerant()

    assert fault_tolerant.import_cad_and_part_management.arguments()

    # 'import_geometry' is a watertight workflow command which is not available now
    # since we have changed to fault-tolerant in the backend.
    with pytest.raises(RuntimeError):
        watertight.import_geometry.arguments()

    # Re-initialize watertight
    watertight = meshing.watertight()

    # 'import_cad_and_part_management' is a fault-tolerant workflow command which is not
    # available now since we have changed to watertight in the backend.
    with pytest.raises(RuntimeError):
        fault_tolerant.import_cad_and_part_management.arguments()

    assert watertight.import_geometry.arguments()

    meshing.workflow.InitializeWorkflow(WorkflowType="Fault-tolerant Meshing")

    # 'import_geometry' is a watertight workflow command which is not available now
    # since we have changed to fault-tolerant in the backend.
    with pytest.raises(RuntimeError):
        watertight.import_geometry.arguments()

    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

    # 'import_cad_and_part_management' is a fault-tolerant workflow command which is not
    # available now since we have changed to watertight in the backend.
    with pytest.raises(RuntimeError):
        fault_tolerant.import_cad_and_part_management.arguments()

    # Re-initialize fault-tolerant
    fault_tolerant = meshing.fault_tolerant()
    assert fault_tolerant.import_cad_and_part_management.arguments()


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.2")
def test_new_meshing_workflow_without_dm_caching(
    disable_datamodel_cache, new_meshing_session
):
    import_file_name = examples.download_file(
        "mixing_elbow.pmdb", "pyfluent/mixing_elbow"
    )

    watertight = new_meshing_session.watertight()
    watertight.import_geometry.file_name = import_file_name
    watertight.import_geometry.length_unit.set_state("in")
    watertight.import_geometry()

    watertight.add_local_sizing.add_child_to_task()
    watertight.add_local_sizing()

    watertight.create_volume_mesh()

    watertight.import_geometry.rename(new_name="import_geom_wtm")
    time.sleep(2)
    assert "import_geometry" not in watertight.task_names()
    assert "import_geom_wtm" in watertight.task_names()
    assert watertight.import_geom_wtm.arguments()

    with pytest.raises(AttributeError):
        watertight.import_geometry

    watertight.delete_tasks(list_of_tasks=["add_local_sizing"])
    time.sleep(2)
    assert "add_local_sizing" not in watertight.task_names()

    assert sorted(
        [repr(x) for x in watertight.import_geom_wtm.insertable_tasks()]
    ) == sorted(
        [
            "<Insertable 'add_local_sizing' task>",
            "<Insertable 'import_boi_geometry' task>",
            "<Insertable 'set_up_rotational_periodic_boundaries' task>",
            "<Insertable 'create_local_refinement_regions' task>",
            "<Insertable 'custom_journal_task' task>",
        ]
    )

    watertight.import_geom_wtm.insertable_tasks.add_local_sizing.insert()
    assert "add_local_sizing" in watertight.task_names()


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_new_meshing_workflow_switching_without_dm_caching(
    disable_datamodel_cache, new_meshing_session
):
    watertight = new_meshing_session.watertight()

    fault_tolerant = new_meshing_session.fault_tolerant()
    with pytest.raises(RuntimeError):
        watertight.import_geometry.arguments()
    assert fault_tolerant.import_cad_and_part_management.arguments()

    watertight = new_meshing_session.watertight()
    with pytest.raises(RuntimeError):
        fault_tolerant.import_cad_and_part_management.arguments()
    assert watertight.import_geometry.arguments()


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.2")
def test_new_meshing_workflow_validate_arguments(new_meshing_session):
    watertight = new_meshing_session.watertight()
    watertight.create_regions.number_of_flow_volumes = 1
    with pytest.raises(ValueError):
        watertight.create_regions.number_of_flow_volumes = 1.2
    assert watertight.create_regions.arguments()["number_of_flow_volumes"] == 1
    with pytest.raises(ValueError):
        watertight.create_regions.arguments.update_dict(
            dict(number_of_flow_volumes=1.2)
        )
    assert watertight.create_regions.arguments()["number_of_flow_volumes"] == 1

    watertight.create_regions.number_of_flow_volumes = 2
    with pytest.raises(ValueError):
        watertight.create_regions.number_of_flow_volumes = 1.2
    assert watertight.create_regions.arguments()["number_of_flow_volumes"] == 2
    with pytest.raises(ValueError):
        watertight.create_regions.arguments.update_dict(
            dict(number_of_flow_volumes=1.2)
        )
    assert watertight.create_regions.arguments()["number_of_flow_volumes"] == 2

    watertight.create_regions.number_of_flow_volumes = None
    with pytest.raises(ValueError):
        watertight.create_regions.number_of_flow_volumes = 1.2
    assert watertight.create_regions.arguments()["number_of_flow_volumes"] == 1
    with pytest.raises(ValueError):
        watertight.create_regions.arguments.update_dict(
            dict(number_of_flow_volumes=1.2)
        )
    assert watertight.create_regions.arguments()["number_of_flow_volumes"] == 1


def test_camel_to_snake_case_convertor():
    assert camel_to_snake_case("ImportGeometry") == "import_geometry"
    assert camel_to_snake_case("Prism2dPreferences") == "prism_2d_preferences"
    assert camel_to_snake_case("Abc2DDef") == "abc_2d_def"
    assert camel_to_snake_case("Abc2d") == "abc_2d"
    assert camel_to_snake_case("abc2d") == "abc2d"
    assert camel_to_snake_case("AbC2d5Cb") == "ab_c2d_5_cb"
    assert camel_to_snake_case("abC2d5Cb") == "ab_c2d_5_cb"
    assert camel_to_snake_case("abC2d5Cb555klOp") == "ab_c2d_5_cb_555kl_op"
    assert camel_to_snake_case("a") == "a"
    assert camel_to_snake_case("A") == "a"
    assert camel_to_snake_case("a5$c") == "a5$c"
    assert camel_to_snake_case("A5$C") == "a5$c"
    assert camel_to_snake_case("A5Dc$") == "a5_dc$"
    assert camel_to_snake_case("Abc2DDc$") == "abc_2d_dc$"
    assert camel_to_snake_case("A2DDc$") == "a2d_dc$"
    assert camel_to_snake_case("") == ""
    assert camel_to_snake_case("BOIZoneorLabel") == "boi_zoneor_label"
    assert camel_to_snake_case("BOIZoneOrLabel") == "boi_zone_or_label"
    assert camel_to_snake_case("NumberofLayers") == "numberof_layers"
    assert camel_to_snake_case("NumberOfLayers") == "number_of_layers"
    assert (
        camel_to_snake_case("Set_Up_Rotational_Periodic_Boundaries")
        == "set_up_rotational_periodic_boundaries"
    )


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_duplicate_tasks_in_workflow(new_meshing_session):
    # Import geometry
    meshing = new_meshing_session
    watertight = meshing.watertight()

    assert sorted(
        [repr(x) for x in watertight.import_geometry.insertable_tasks()]
    ) == sorted(
        [
            "<Insertable 'import_boi_geometry' task>",
            "<Insertable 'set_up_rotational_periodic_boundaries' task>",
            "<Insertable 'create_local_refinement_regions' task>",
            "<Insertable 'custom_journal_task' task>",
        ]
    )
    assert "add_local_sizing" in watertight.task_names()
    watertight.add_local_sizing.delete()
    assert "add_local_sizing" not in watertight.task_names()
    assert "<Insertable 'add_local_sizing' task>" in [
        repr(x) for x in watertight.import_geometry.insertable_tasks()
    ]
    watertight.import_geometry.insertable_tasks.add_local_sizing.insert()
    assert "<Insertable 'add_local_sizing' task>" not in [
        repr(x) for x in watertight.import_geometry.insertable_tasks()
    ]
    watertight.import_geometry.insertable_tasks.import_boi_geometry.insert()
    watertight.import_geometry.insertable_tasks.import_boi_geometry.insert()
    watertight.import_geometry.insertable_tasks.import_boi_geometry.insert()
    assert set(watertight.task_names()) == {
        "import_geometry",
        "create_surface_mesh",
        "describe_geometry",
        "apply_share_topology",
        "enclose_fluid_regions",
        "update_boundaries",
        "create_regions",
        "update_regions",
        "add_boundary_layer",
        "create_volume_mesh",
        "add_local_sizing",
        "import_boi_geometry",
        "import_boi_geometry_1",
        "import_boi_geometry_2",
    }
    assert watertight.import_boi_geometry_1.arguments()


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_object_oriented_task_inserting_in_workflows(new_meshing_session):
    meshing = new_meshing_session
    watertight = meshing.watertight()
    assert sorted(
        [repr(x) for x in watertight.import_geometry.insertable_tasks()]
    ) == sorted(
        [
            "<Insertable 'import_boi_geometry' task>",
            "<Insertable 'set_up_rotational_periodic_boundaries' task>",
            "<Insertable 'create_local_refinement_regions' task>",
            "<Insertable 'custom_journal_task' task>",
        ]
    )
    assert "set_up_rotational_periodic_boundaries" not in watertight.task_names()
    watertight.import_geometry.insertable_tasks.set_up_rotational_periodic_boundaries.insert()
    assert "set_up_rotational_periodic_boundaries" in watertight.task_names()
    assert sorted(
        [repr(x) for x in watertight.import_geometry.insertable_tasks()]
    ) == sorted(
        [
            "<Insertable 'import_boi_geometry' task>",
            "<Insertable 'create_local_refinement_regions' task>",
            "<Insertable 'custom_journal_task' task>",
        ]
    )
    watertight.import_geometry.insertable_tasks.import_boi_geometry.insert()
    watertight.import_geometry.insertable_tasks.import_boi_geometry.insert()
    assert "import_boi_geometry" in watertight.task_names()
    assert "import_boi_geometry_1" in watertight.task_names()
    assert watertight.import_boi_geometry.arguments()
    assert watertight.import_boi_geometry_1.arguments()


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_loaded_workflow(new_meshing_session):
    meshing = new_meshing_session
    saved_workflow_path = examples.download_file(
        "sample_watertight_workflow.wft", "pyfluent/meshing_workflows"
    )
    loaded_workflow = meshing.load_workflow(file_path=saved_workflow_path)
    assert "set_up_rotational_periodic_boundaries" in loaded_workflow.task_names()
    assert "import_boi_geometry" in loaded_workflow.task_names()
    # The below snippet is randomly failing in CI
    # assert loaded_workflow.import_boi_geometry_1.arguments()


@pytest.mark.skip("https://github.com/ansys/pyfluent/issues/3065")
@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_created_workflow(new_meshing_session):
    meshing = new_meshing_session
    created_workflow = meshing.create_workflow()

    assert sorted([repr(x) for x in created_workflow.insertable_tasks()]) == sorted(
        [
            "<Insertable 'import_geometry' task>",
            "<Insertable 'load_cad_geometry' task>",
            "<Insertable 'import_cad_and_part_management' task>",
            "<Insertable 'custom_journal_task' task>",
        ]
    )

    created_workflow.insertable_tasks()[0].insert()

    assert created_workflow.insertable_tasks() == []

    assert "<Insertable 'add_local_sizing' task>" in [
        repr(x) for x in created_workflow.import_geometry.insertable_tasks()
    ]
    created_workflow.import_geometry.insertable_tasks.add_local_sizing.insert()
    assert "<Insertable 'add_local_sizing' task>" not in [
        repr(x) for x in created_workflow.import_geometry.insertable_tasks()
    ]
    assert sorted(created_workflow.task_names()) == sorted(
        ["import_geometry", "add_local_sizing"]
    )


@pytest.fixture
def new_meshing_session2(new_meshing_session):
    return new_meshing_session


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_independent_meshing_sessions(new_meshing_session, new_meshing_session2):
    meshing_1 = new_meshing_session
    meshing_2 = new_meshing_session2

    watertight = meshing_1.watertight()
    assert watertight.import_geometry.arguments()

    ft = meshing_1.fault_tolerant()
    assert ft.import_cad_and_part_management.arguments()

    watertight = meshing_1.watertight()
    assert watertight.import_geometry.arguments()

    fault_tolerant = meshing_2.fault_tolerant()
    assert fault_tolerant.import_cad_and_part_management.arguments()


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_independent_meshing_sessions_without_dm_caching(
    disable_datamodel_cache, new_meshing_session, new_meshing_session2
):
    meshing_1 = new_meshing_session
    meshing_2 = new_meshing_session2

    watertight = meshing_1.watertight()
    assert watertight.import_geometry.arguments()

    fault_tolerant = meshing_2.fault_tolerant()
    assert fault_tolerant.import_cad_and_part_management.arguments()


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.2")
def test_switching_workflow_interface(new_meshing_session):
    wt1 = new_meshing_session.watertight()
    ft = new_meshing_session.fault_tolerant()
    tw = new_meshing_session.two_dimensional_meshing()
    cw = new_meshing_session.create_workflow()
    saved_workflow_path = examples.download_file(
        "sample_watertight_workflow.wft", "pyfluent/meshing_workflows"
    )
    lw = new_meshing_session.load_workflow(file_path=saved_workflow_path)
    wt2 = new_meshing_session.watertight()
    del wt1, ft, tw, cw, lw, wt2


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_duplicate_children_of_compound_task(
    new_meshing_session, mixing_elbow_geometry_filename
):
    watertight = new_meshing_session.watertight()
    watertight.import_geometry.file_name = mixing_elbow_geometry_filename
    watertight.import_geometry()
    watertight.add_local_sizing.add_child_and_update(
        state={
            "boi_control_name": "wall",
            "boi_face_label_list": ["wall-elbow", "wall-inlet"],
            "boi_size": 10,
        }
    )
    watertight.add_local_sizing.add_child_and_update(
        state={
            "boi_control_name": "inlet",
            "boi_face_label_list": ["wall-inlet", "cold-inlet", "hot-inlet"],
            "boi_size": 10,
        }
    )
    watertight.add_local_sizing.add_child_and_update(
        state={
            "boi_control_name": "outlet",
            "boi_face_label_list": ["outlet"],
            "boi_size": 10,
        }
    )

    assert {
        "add_local_sizing_child_1",
        "add_local_sizing_child_2",
        "add_local_sizing_child_3",
    }.issubset(set(watertight.task_names()))

    assert watertight.add_local_sizing.task_names() == [
        "add_local_sizing_child_1",
        "add_local_sizing_child_2",
        "add_local_sizing_child_3",
    ]

    assert watertight.tasks()[-2].name() == "inlet"
    assert watertight.tasks()[-2].python_name() == "add_local_sizing_child_2"

    assert watertight.add_local_sizing.tasks()[-1].name() == "outlet"
    assert (
        watertight.add_local_sizing.tasks()[-1].python_name()
        == "add_local_sizing_child_3"
    )


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_current_workflow(new_meshing_session):
    meshing = new_meshing_session

    with pytest.raises(RuntimeError):
        meshing.current_workflow

    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

    assert meshing.current_workflow.import_geometry

    with pytest.raises(AttributeError):
        meshing.current_workflow.import_cad_and_part_management

    meshing.workflow.InitializeWorkflow(WorkflowType="Fault-tolerant Meshing")

    assert meshing.current_workflow.import_cad_and_part_management

    with pytest.raises(AttributeError):
        meshing.current_workflow.import_geometry


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_mark_as_updated(new_meshing_session):
    meshing = new_meshing_session

    watertight = meshing.watertight()

    assert meshing.workflow.TaskObject["Import Geometry"].State() == "Out-of-date"
    assert meshing.workflow.TaskObject["Describe Geometry"].State() == "Out-of-date"
    assert meshing.workflow.TaskObject["Add Local Sizing"].State() == "Out-of-date"

    watertight.import_geometry.mark_as_updated()
    watertight.describe_geometry.mark_as_updated()
    watertight.add_local_sizing.mark_as_updated()

    assert meshing.workflow.TaskObject["Import Geometry"].State() == "Forced-up-to-date"
    assert (
        meshing.workflow.TaskObject["Describe Geometry"].State() == "Forced-up-to-date"
    )
    assert (
        meshing.workflow.TaskObject["Add Local Sizing"].State() == "Forced-up-to-date"
    )


@pytest.mark.fluent_version(">=24.1")
@pytest.mark.codegen_required
def test_accessors_for_argument_sub_items(new_meshing_session):
    meshing = new_meshing_session
    watertight = meshing.watertight()

    import_geom = watertight.import_geometry
    assert import_geom.length_unit.default_value() == "mm"
    assert "allowed_values" in dir(import_geom.length_unit)
    assert import_geom.arguments.length_unit.allowed_values() == [
        "m",
        "cm",
        "mm",
        "in",
        "ft",
        "um",
        "nm",
    ]
    assert import_geom.arguments.length_unit() == "mm"
    import_geom.length_unit.set_state("cm")
    assert import_geom.arguments.length_unit.get_state() == "cm"
    import_geom.arguments.length_unit = "in"
    assert import_geom.arguments.length_unit() == "in"
    import_geom.arguments["length_unit"] = "m"
    assert import_geom.arguments["length_unit"] == "m"
    meshing.workflow.TaskObject["Import Geometry"].Arguments = dict(LengthUnit="in")
    assert import_geom.arguments.length_unit() == "in"

    assert not import_geom.arguments.mesh_unit.is_read_only()
    assert import_geom.arguments.length_unit.is_active()
    assert not import_geom.arguments.file_name.is_read_only()
    assert not import_geom.arguments.file_name()
    import_geom.arguments.file_name = "xyz.txt"
    assert import_geom.arguments.file_name() == "xyz.txt"
    with pytest.raises(AttributeError) as msg:
        import_geom.arguments.file = "sample.txt"
    assert msg.value.args[0] == "No attribute named 'file' in 'Import Geometry'."
    with pytest.raises(AttributeError):
        import_geom.arguments.CadImportOptions.OneZonePer = "face"

    assert import_geom.arguments.cad_import_options()
    assert import_geom.arguments.cad_import_options.one_zone_per()

    assert import_geom.arguments.file_format.get_attrib_value("allowedValues") == [
        "CAD",
        "Mesh",
    ]
    assert import_geom.arguments.file_format.allowed_values() == ["CAD", "Mesh"]

    assert not import_geom.arguments.cad_import_options.one_zone_per.is_read_only()
    assert import_geom.arguments.cad_import_options.one_zone_per() == "body"
    import_geom.arguments.cad_import_options.one_zone_per.set_state("face")
    assert import_geom.arguments.cad_import_options.one_zone_per() == "face"
    import_geom.arguments.cad_import_options.one_zone_per = "object"
    assert import_geom.arguments.cad_import_options.one_zone_per() == "object"

    volume_mesh_gen = watertight.create_volume_mesh
    assert (
        volume_mesh_gen.arguments.volume_fill_controls.type.default_value()
        == "Cartesian"
    )

    # Test particular to string type (allowed_values() only available in string types)
    assert volume_mesh_gen.arguments.volume_fill_controls.type.allowed_values() == [
        "Octree",
        "Cartesian",
    ]
    feat_angle = import_geom.arguments.cad_import_options.feature_angle
    assert feat_angle.default_value() == 40.0

    # Test particular to numerical type (min() only available in numerical types)
    assert feat_angle.min() == 0.0

    # Test intended to fail in numerical type (allowed_values() only available in string types)
    with pytest.raises(AttributeError) as msg:
        assert feat_angle.allowed_values()
    assert (
        msg.value.args[0]
        == "'PyNumericalCommandArgumentsSubItem' object has no attribute 'allowed_values'"
    )

    # Test intended to fail in numerical type (allowed_values() only available in string types)
    with pytest.raises(AttributeError) as msg:
        assert import_geom.arguments.num_parts.allowed_values()
    assert (
        msg.value.args[0]
        == "'PyNumericalCommandArgumentsSubItem' object has no attribute 'allowed_values'"
    )

    # Test intended to fail in string type (min() only available in numerical types)
    with pytest.raises(AttributeError) as msg:
        assert import_geom.arguments.length_unit.min()
    assert (
        msg.value.args[0]
        == "'PyTextualCommandArgumentsSubItem' object has no attribute 'min'"
    )


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=25.1")
def test_scenario_with_common_python_names_from_fdl(new_meshing_session):
    meshing = new_meshing_session

    fault_tolerant = meshing.fault_tolerant()

    # Check if all task names are unique.
    assert len(fault_tolerant.task_names()) == len(set(fault_tolerant.task_names()))

    # APIName from fdl file
    assert "create_volume_mesh" in fault_tolerant.task_names()
    assert "generate_volume_mesh" in fault_tolerant.task_names()
    assert "generate_surface_mesh" in fault_tolerant.task_names()

    watertight = meshing.watertight()
    # Check if all task names are unique.
    assert len(watertight.task_names()) == len(set(watertight.task_names()))

    two_dimensional = meshing.two_dimensional_meshing()
    # Check if all task names are unique.
    assert len(two_dimensional.task_names()) == len(set(two_dimensional.task_names()))


@pytest.mark.skip("Failing in GitHub")
@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=25.1")
def test_return_state_changes(new_meshing_session):
    meshing = new_meshing_session
    wt = meshing.watertight()
    import_file_name = examples.download_file(
        "mixing_elbow.pmdb", "pyfluent/mixing_elbow"
    )

    wt.import_geometry.file_name.set_state(import_file_name)

    # trigger creation of downstream task when this task is updated:
    wt.describe_geometry.multizone.set_state("Yes")
    wt.describe_geometry()

    assert wt.add_multizone_controls


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=25.1")
def test_recursive_update_dict(new_meshing_session):
    meshing = new_meshing_session
    fault_tolerant = meshing.fault_tolerant()
    import_file_name = examples.download_file(
        "exhaust_system.fmd", "pyfluent/exhaust_system"
    )

    import_cad = fault_tolerant.import_cad_and_part_management
    import_cad.feature_angle = 35
    import_cad.fmd_file_name = import_file_name
    import_cad()

    descr_geom = fault_tolerant.describe_geometry_and_flow
    descr_geom.arguments()
    descr_geom.flow_type = "Internal flow through the object"
    descr_geom.add_enclosure = "Yes"
    descr_geom.close_caps = "Yes"
    descr_geom.local_refinement_regions = "Yes"
    descr_geom.describe_geometry_and_flow_options.moving_objects = "Yes"
    descr_geom.describe_geometry_and_flow_options.advanced_options = True
    descr_geom.describe_geometry_and_flow_options.porous_regions = "Yes"
    descr_geom.describe_geometry_and_flow_options.enable_overset = "Yes"
    descr_geom.describe_geometry_and_flow_options.extract_edge_features = "Yes"
    descr_geom.describe_geometry_and_flow_options.zero_thickness = "Yes"
    descr_geom.arguments()
    assert meshing.workflow.TaskObject["Describe Geometry and Flow"].Arguments()[
        "DescribeGeometryAndFlowOptions"
    ] == {
        "AdvancedOptions": True,
        "EnableOverset": "Yes",
        "ExtractEdgeFeatures": "Yes",
        "MovingObjects": "Yes",
        "PorousRegions": "Yes",
        "ZeroThickness": "Yes",
    }


@pytest.mark.skip("Pending fix.")
@pytest.mark.fluent_version(">=25.2")
def test_meshing_workflow_api_updates_for_server_events(
    new_meshing_session,
):
    meshing = new_meshing_session
    wt = meshing.watertight()
    wt.describe_geometry.multizone.set_state("Yes")
    wt.describe_geometry()

    add_multizone_controls = None
    attr_err_count = 0

    while add_multizone_controls is None and attr_err_count <= 10:
        try:
            add_multizone_controls = wt.add_multizone_controls
        except AttributeError:
            attr_err_count += 1
            time.sleep(1)

    assert attr_err_count == 0
    assert add_multizone_controls
