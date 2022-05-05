""".. _ref_exhaust_system_tui_api:

Exhaust System: Fault-tolerant Meshing
----------------------------------------------

This test covers the setup and solution of a three-dimensional
turbulent fluid flow in a manifold exhaust system using fault
tolerant mehing worflow.

This test queries the following using PyTest:

- Meshing workflow tasks state before and after the task execution
- Flux report after solution, approximately 0 kg/s
"""

from functools import partial

from pytest import approx
from util.meshing_workflow import (  # noqa: F401
    assign_task_arguments,
    execute_task_with_pre_and_postcondition_checks,
    exhaust_system_geometry,
    new_fault_tolerant_workflow,
    new_fault_tolerant_workflow_session,
    new_mesh_session,
)
from util.solver import check_report_definition_result


def test_exhaust_system(new_fault_tolerant_workflow_session, exhaust_system_geometry):

    session = new_fault_tolerant_workflow_session
    workflow = session.workflow

    assign_task_args = partial(
        assign_task_arguments, workflow=workflow, check_state=True
    )

    execute_task_with_pre_and_postconditions = partial(
        execute_task_with_pre_and_postcondition_checks, workflow=workflow
    )

    ###############################################################################
    # Import the CAD geometry
    session.part_management.InputFileChanged(
        FilePath=exhaust_system_geometry,
        IgnoreSolidNames=False,
        PartPerBody=False,
    )
    session.PMFileManagement.FileManager.LoadFiles()
    session.part_management.Node["Meshing Model"].Copy(
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
    session.part_management.ObjectSetting["DefaultObjectSetting"].OneZonePer.setState(
        "part"
    )
    workflow.TaskObject["Import CAD and Part Management"].Arguments.setState(
        {
            "Context": 0,
            "CreateObjectPer": "Custom",
            "FMDFileName": "import_filenamed",
            "FileLoaded": "yes",
            "ObjectSetting": "DefaultObjectSetting",
            "Options": {
                "Line": False,
                "Solid": False,
                "Surface": False,
            },
        }
    )
    execute_task_with_pre_and_postconditions(task_name="Import CAD and Part Management")

    ###############################################################################
    # Provide a description for the geometry and the flow characteristics.
    workflow.TaskObject["Describe Geometry and Flow"].Arguments.setState(
        {
            "AddEnclosure": "No",
            "CloseCaps": "Yes",
            "FlowType": "Internal flow through the object",
        }
    )
    workflow.TaskObject["Describe Geometry and Flow"].UpdateChildTasks(
        SetupTypeChanged=False
    )
    workflow.TaskObject["Describe Geometry and Flow"].Arguments.setState(
        {
            "AddEnclosure": "No",
            "CloseCaps": "Yes",
            "DescribeGeometryAndFlowOptions": {
                "AdvancedOptions": True,
                "ExtractEdgeFeatures": "Yes",
            },
            "FlowType": "Internal flow through the object",
        }
    )
    workflow.TaskObject["Describe Geometry and Flow"].UpdateChildTasks(
        SetupTypeChanged=False
    )
    execute_task_with_pre_and_postconditions(task_name="Describe Geometry and Flow")

    ###############################################################################
    # Cover any openings in your geometry.

    workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.setState(
        {
            "CreatePatchPreferences": {
                "ShowCreatePatchPreferences": False,
            },
            "PatchName": "inlet-1",
            "SelectionType": "zone",
            "ZoneSelectionList": ["inlet.1"],
        }
    )
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.setState(
        {
            "CreatePatchPreferences": {
                "ShowCreatePatchPreferences": False,
            },
            "PatchName": "inlet-1",
            "SelectionType": "zone",
            "ZoneLocation": [
                "1",
                "351.68205",
                "-361.34322",
                "-301.88668",
                "396.96205",
                "-332.84759",
                "-266.69751",
                "inlet.1",
            ],
            "ZoneSelectionList": ["inlet.1"],
        }
    )
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].AddChildToTask()
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].InsertCompoundChildTask()
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.setState({})
    execute_task_with_pre_and_postconditions(task_name="inlet-1")
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.setState(
        {
            "PatchName": "inlet-2",
            "SelectionType": "zone",
            "ZoneSelectionList": ["inlet.2"],
        }
    )
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.setState(
        {
            "PatchName": "inlet-2",
            "SelectionType": "zone",
            "ZoneLocation": [
                "1",
                "441.68205",
                "-361.34322",
                "-301.88668",
                "486.96205",
                "-332.84759",
                "-266.69751",
                "inlet.2",
            ],
            "ZoneSelectionList": ["inlet.2"],
        }
    )
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].AddChildToTask()
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].InsertCompoundChildTask()
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.setState({})
    execute_task_with_pre_and_postconditions(task_name="inlet-2")
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.setState(
        {
            "PatchName": "inlet-3",
            "SelectionType": "zone",
            "ZoneSelectionList": ["inlet"],
        }
    )
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.setState(
        {
            "PatchName": "inlet-3",
            "SelectionType": "zone",
            "ZoneLocation": [
                "1",
                "261.68205",
                "-361.34322",
                "-301.88668",
                "306.96205",
                "-332.84759",
                "-266.69751",
                "inlet",
            ],
            "ZoneSelectionList": ["inlet"],
        }
    )
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].AddChildToTask()
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].InsertCompoundChildTask()
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.setState({})
    execute_task_with_pre_and_postconditions(task_name="inlet-3")
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.setState(
        {
            "PatchName": "outlet-1",
            "SelectionType": "zone",
            "ZoneSelectionList": ["outlet"],
            "ZoneType": "pressure-outlet",
        }
    )
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.setState(
        {
            "PatchName": "outlet-1",
            "SelectionType": "zone",
            "ZoneLocation": [
                "1",
                "352.22702",
                "-197.8957",
                "84.102381",
                "394.41707",
                "-155.70565",
                "84.102381",
                "outlet",
            ],
            "ZoneSelectionList": ["outlet"],
            "ZoneType": "pressure-outlet",
        }
    )
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].AddChildToTask()
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].InsertCompoundChildTask()
    workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.setState({})
    execute_task_with_pre_and_postconditions(task_name="outlet-1")

    ###############################################################################
    # Extract edge features.
    workflow.TaskObject["Extract Edge Features"].Arguments.setState(
        {
            "ExtractMethodType": "Intersection Loops",
            "ObjectSelectionList": ["flow_pipe", "main"],
        }
    )
    workflow.TaskObject["Extract Edge Features"].AddChildToTask()
    workflow.TaskObject["Extract Edge Features"].InsertCompoundChildTask()
    workflow.TaskObject["edge-group-1"].Arguments.setState(
        {
            "ExtractEdgesName": "edge-group-1",
            "ExtractMethodType": "Intersection Loops",
            "ObjectSelectionList": ["flow_pipe", "main"],
        }
    )
    workflow.TaskObject["Extract Edge Features"].Arguments.setState({})
    execute_task_with_pre_and_postconditions(task_name="edge-group-1")

    ###############################################################################
    # Identify regions.
    workflow.TaskObject["Identify Regions"].Arguments.setState(
        {
            "SelectionType": "zone",
            "X": 377.322045740589,
            "Y": -176.800676988458,
            "Z": -37.0764628583475,
            "ZoneSelectionList": ["main.1"],
        }
    )
    workflow.TaskObject["Identify Regions"].Arguments.setState(
        {
            "SelectionType": "zone",
            "X": 377.322045740589,
            "Y": -176.800676988458,
            "Z": -37.0764628583475,
            "ZoneLocation": [
                "1",
                "213.32205",
                "-225.28068",
                "-158.25531",
                "541.32205",
                "-128.32068",
                "84.102381",
                "main.1",
            ],
            "ZoneSelectionList": ["main.1"],
        }
    )
    workflow.TaskObject["Identify Regions"].AddChildToTask()
    workflow.TaskObject["Identify Regions"].InsertCompoundChildTask()
    workflow.TaskObject["fluid-region-1"].Arguments.setState(
        {
            "MaterialPointsName": "fluid-region-1",
            "SelectionType": "zone",
            "X": 377.322045740589,
            "Y": -176.800676988458,
            "Z": -37.0764628583475,
            "ZoneLocation": [
                "1",
                "213.32205",
                "-225.28068",
                "-158.25531",
                "541.32205",
                "-128.32068",
                "84.102381",
                "main.1",
            ],
            "ZoneSelectionList": ["main.1"],
        }
    )
    workflow.TaskObject["Identify Regions"].Arguments.setState({})
    execute_task_with_pre_and_postconditions(task_name="fluid-region-1")
    workflow.TaskObject["Identify Regions"].Arguments.setState(
        {
            "MaterialPointsName": "void-region-1",
            "NewRegionType": "void",
            "ObjectSelectionList": ["inlet-1", "inlet-2", "inlet-3", "main"],
            "X": 374.722045740589,
            "Y": -278.9775145640143,
            "Z": -161.1700719416913,
        }
    )
    workflow.TaskObject["Identify Regions"].AddChildToTask()
    workflow.TaskObject["Identify Regions"].InsertCompoundChildTask()
    workflow.TaskObject["Identify Regions"].Arguments.setState({})
    execute_task_with_pre_and_postconditions(task_name="void-region-1")

    ###############################################################################
    # Define thresholds for any potential leakages.
    session.workflow.TaskObject["Define Leakage Threshold"].Arguments.setState(
        {
            "AddChild": "yes",
            "FlipDirection": True,
            "PlaneDirection": "X",
            "RegionSelectionSingle": "void-region-1",
        }
    )
    workflow.TaskObject["Define Leakage Threshold"].AddChildToTask()
    workflow.TaskObject["Define Leakage Threshold"].InsertCompoundChildTask()
    workflow.TaskObject["leakage-1"].Arguments.setState(
        {
            "AddChild": "yes",
            "FlipDirection": True,
            "LeakageName": "leakage-1",
            "PlaneDirection": "X",
            "RegionSelectionSingle": "void-region-1",
        }
    )
    workflow.TaskObject["Define Leakage Threshold"].Arguments.setState(
        {
            "AddChild": "yes",
        }
    )
    execute_task_with_pre_and_postconditions(task_name="leakage-1")

    ###############################################################################
    # Review your region settings.
    workflow.TaskObject["Update Region Settings"].Arguments.setState(
        {
            "AllRegionFilterCategories": ["2"] * 5 + ["1"] * 2,
            "AllRegionLeakageSizeList": ["none"] * 6 + ["6.4"],
            "AllRegionLinkedConstructionSurfaceList": ["n/a"] * 6 + ["no"],
            "AllRegionMeshMethodList": ["none"] * 6 + ["wrap"],
            "AllRegionNameList": [
                "main",
                "flow_pipe",
                "outpipe3",
                "object2",
                "object1",
                "void-region-1",
                "fluid-region-1",
            ],
            "AllRegionOversetComponenList": ["no"] * 7,
            "AllRegionSourceList": ["object"] * 5 + ["mpt"] * 2,
            "AllRegionTypeList": ["void"] * 6 + ["fluid"],
            "AllRegionVolumeFillList": ["none"] * 6 + ["tet"],
            "FilterCategory": "Identified Regions",
            "OldRegionLeakageSizeList": [""],
            "OldRegionMeshMethodList": ["wrap"],
            "OldRegionNameList": ["fluid-region-1"],
            "OldRegionOversetComponenList": ["no"],
            "OldRegionTypeList": ["fluid"],
            "OldRegionVolumeFillList": ["hexcore"],
            "RegionLeakageSizeList": [""],
            "RegionMeshMethodList": ["wrap"],
            "RegionNameList": ["fluid-region-1"],
            "RegionOversetComponenList": ["no"],
            "RegionTypeList": ["fluid"],
            "RegionVolumeFillList": ["tet"],
        }
    )
    execute_task_with_pre_and_postconditions(task_name="Update Region Settings")

    ###############################################################################
    # Select options for controlling the mesh.
    execute_task_with_pre_and_postconditions(task_name="Choose Mesh Control Options")

    ###############################################################################
    # Generate the surface mesh.
    execute_task_with_pre_and_postconditions(task_name="Generate the Surface Mesh")

    ###############################################################################
    # Confirm and update the boundaries.
    execute_task_with_pre_and_postconditions(task_name="Update Boundaries")

    ###############################################################################
    # Add boundary layers.
    workflow.TaskObject["Add Boundary Layers"].AddChildToTask()
    workflow.TaskObject["Add Boundary Layers"].InsertCompoundChildTask()
    workflow.TaskObject["aspect-ratio_1"].Arguments.setState(
        {
            "BLControlName": "aspect-ratio_1",
        }
    )
    workflow.TaskObject["Add Boundary Layers"].Arguments.setState({})
    execute_task_with_pre_and_postconditions(task_name="aspect-ratio_1")

    ###############################################################################
    # Generate the volume mesh.
    workflow.TaskObject["Generate the Volume Mesh"].Arguments.setState(
        {
            "AllRegionNameList": [
                "main",
                "flow_pipe",
                "outpipe3",
                "object2",
                "object1",
                "void-region-1",
                "fluid-region-1",
            ],
            "AllRegionSizeList": ["11.33375"] * 7,
            "AllRegionVolumeFillList": ["none"] * 6 + ["tet"],
            "EnableParallel": True,
        }
    )
    execute_task_with_pre_and_postconditions(task_name="Generate the Volume Mesh")

    ###############################################################################
    # Check the mesh in Meshing mode
    session.tui.meshing.mesh.check_mesh()

    ###############################################################################
    # Switch to Solution mode
    session.tui.meshing.switch_to_solution_mode("yes")

    ###############################################################################
    # Check the mesh in Solver mode
    session.tui.solver.mesh.check()

    ###############################################################################
    # Set the units for length
    session.tui.solver.define.units("length", "mm")

    ###############################################################################
    # Select kw sst turbulence model
    session.tui.solver.define.models.viscous.kw_sst("yes")

    ###############################################################################
    # Set the velocity and turbulence boundary conditions for the first inlet
    # (inlet-1).
    session.tui.solver.define.boundary_conditions.set.velocity_inlet(
        "inlet-1", [], "vmag", "no", 1, "quit"
    )
    ###############################################################################
    # Apply the same conditions for the other velocity inlet boundaries (inlet_2,
    # and inlet_3).
    session.tui.solver.define.boundary_conditions.copy_bc(
        "inlet-1", "inlet-2", "inlet-3", ()
    )

    ###############################################################################
    # Set the boundary conditions at the outlet (outlet-1).
    session.tui.solver.define.boundary_conditions.set.pressure_outlet(
        "outlet-1", [], "turb-intensity", 5, "quit"
    )
    session.tui.solver.solve.monitors.residual.plot("yes")

    ###############################################################################
    # Initialize the flow field using the Initialization
    session.tui.solver.solve.initialize.hyb_initialization()

    ###############################################################################
    # Start the calculation by requesting 100 iterations
    session.tui.solver.solve.set.number_of_iterations(100)
    session.tui.solver.solve.iterate()

    ###############################################################################
    # Assert the returned mass flux report definition value
    root = session.get_settings_root()
    root.solution.report_definitions.flux["mass_flow_rate"] = {}
    root.solution.report_definitions.flux["mass_flow_rate"].zone_names = [
        "inlet-1",
        "inlet-2",
        "inlet-3",
        "outlet-1",
    ]

    check_report_definition = partial(
        check_report_definition_result,
        report_definitions=root.solution.report_definitions,
    )

    check_report_definition(
        report_definition_name="mass_flow_rate",
        expected_result=approx(-6.036667e-07, abs=1e-3),
    )

    ###############################################################################
