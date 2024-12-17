from functools import partial

import pytest
from util.meshing_workflow import (
    assign_task_arguments,
    execute_task_with_pre_and_postcondition_checks,
)

from ansys.fluent.core import examples
from ansys.fluent.core.utils.fluent_version import FluentVersion


@pytest.mark.fluent_version(">=23.1")
@pytest.mark.nightly
@pytest.mark.codegen_required
def test_mixing_elbow_meshing_workflow(
    watertight_workflow_session,
    mixing_elbow_geometry_filename,
):
    """This test covers generic meshing workflow behaviour."""
    meshing_session = watertight_workflow_session
    workflow = meshing_session.workflow

    ###############################################################################

    assign_task_args = partial(
        assign_task_arguments, workflow=workflow, check_state=True
    )

    execute_task_with_pre_and_postconditions = partial(
        execute_task_with_pre_and_postcondition_checks,
        workflow=workflow,
    )

    ###############################################################################
    # Import the CAD geometry
    # Query the task state before and after task execution
    assign_task_args(
        task_name="Import Geometry",
        FileName=mixing_elbow_geometry_filename,
        LengthUnit="in",
    )

    execute_task_with_pre_and_postconditions(task_name="Import Geometry")

    ###############################################################################
    # Add local sizing
    # Query the task state before and after task execution
    workflow.TaskObject["Add Local Sizing"].AddChildToTask()

    execute_task_with_pre_and_postconditions(task_name="Add Local Sizing")

    ###############################################################################
    # Generate the surface mesh
    # Query the task state before and after task execution
    assign_task_args(
        task_name="Generate the Surface Mesh", CFDSurfaceMeshControls={"MaxSize": 0.3}
    )

    execute_task_with_pre_and_postconditions(task_name="Generate the Surface Mesh")

    ###############################################################################
    # Describe the geometry
    # Query the task state before and after task execution
    describe_geo = workflow.TaskObject["Describe Geometry"]
    describe_geo.UpdateChildTasks(SetupTypeChanged=False)
    assign_task_args(
        task_name="Describe Geometry",
        SetupType="The geometry consists of only fluid regions with no voids",
    )
    describe_geo.UpdateChildTasks(SetupTypeChanged=True)

    execute_task_with_pre_and_postconditions(task_name="Describe Geometry")

    ###############################################################################
    # Update Boundaries Task
    # Query the task state before and after task execution
    assign_task_args(
        task_name="Update Boundaries",
        BoundaryLabelList=["wall-inlet"],
        BoundaryLabelTypeList=["wall"],
        OldBoundaryLabelList=["wall-inlet"],
        OldBoundaryLabelTypeList=["velocity-inlet"],
    )

    execute_task_with_pre_and_postconditions(task_name="Update Boundaries")

    ###############################################################################
    # Update your regions
    # Query the task state before and after task execution

    execute_task_with_pre_and_postconditions(task_name="Update Regions")

    ###############################################################################
    # Add Boundary Layers
    # Query the task state before and after task execution
    add_boundary_layer = workflow.TaskObject["Add Boundary Layers"]
    add_boundary_layer.AddChildToTask()
    add_boundary_layer.InsertCompoundChildTask()
    assign_task_args(
        task_name="smooth-transition_1", BLControlName="smooth-transition_1"
    )
    add_boundary_layer.Arguments = {}

    execute_task_with_pre_and_postconditions(task_name="Add Boundary Layers")

    ###############################################################################
    # Generate the volume mesh
    # Query the task state before and after task execution
    assign_task_args(
        task_name="Generate the Volume Mesh",
        VolumeFill="poly-hexcore",
        VolumeFillControls={"HexMaxCellLength": 0.3},
    )

    execute_task_with_pre_and_postconditions(task_name="Generate the Volume Mesh")

    ###############################################################################
    # Check the mesh in Meshing mode
    # TODO: Remove the if condition after a stable version of 23.1 is available and update the commands as required.
    if meshing_session.get_fluent_version() < FluentVersion.v231:
        meshing_session.tui.mesh.check_mesh()


@pytest.mark.codegen_required
def test_meshing_workflow_raises_exception_on_invalid_task_name(
    watertight_workflow_session,
):
    try:
        watertight_workflow_session.workflow.TaskObject["no such task"]
    except Exception:
        pass
    else:
        assert False


"""
Cannot enable this test because meshing workflow makes invalid queries as
soon as the meshing application is started:

Error: workflow/cx-create-workflow-tree:Invalid query for child TaskType from parent /Workflow
Error Object: ()


def test_meshing_workflow_raises_exception_on_invalid_key_in_task_args(
    model_object_throws_on_invalid_arg,
    watertight_workflow_session,
    mixing_elbow_geometry_filename
):
    # task_names = ("Import Geometry", "Add Local Sizing")
    task_names = ("Add Local Sizing",)
    for task_name in task_names:
        task = watertight_workflow_session.workflow.TaskObject[task_name]
        try:
            task.Arguments = {"no such arg": 42}
        except Exception:
            pass
        else:
            assert False

def test_meshing_workflow_raises_exception_on_invalid_key_in_task_args_2(
    model_object_throws_on_invalid_arg,
    watertight_workflow_session,
    mixing_elbow_geometry_filename
):
    workflow = watertight_workflow_session.workflow
    assign_task_args = partial(
        assign_task_arguments, workflow=workflow, check_state=False
    )

    assign_task_args(
        task_name="Import Geometry", FileName=mixing_elbow_geometry_filename, LengthUnit="in"
    )

    workflow.TaskObject["Import Geometry"].Execute()

    try:
        assign_task_args(
            task_name="Add Local Sizing", XXX=42
        )
    except:
        pass
    else:
        assert False
"""


@pytest.mark.skip("Wait for later implementation.")
@pytest.mark.fluent_version(">=23.1")
@pytest.mark.codegen_required
def test_read_only_behaviour_of_command_arguments(new_meshing_session):
    session_new = new_meshing_session
    w = session_new.workflow
    m = session_new.meshing.ImportGeometry.create_instance
    w.InitializeWorkflow(WorkflowType="Watertight Geometry")
    import_geom = w.TaskObject["Import Geometry"]

    with pytest.raises(AttributeError):
        import_geom.arguments.MeshUnit.set_state("in")

    with pytest.raises(AttributeError):
        import_geom.arguments.CadImportOptions.OneZonePer.set_state(None)

    assert "set_state" in dir(m())
    assert "set_state" in dir(m().NumParts)


@pytest.mark.codegen_required
def test_dummy_journal_data_model_methods(new_meshing_session):
    session_new = new_meshing_session
    w = session_new.workflow
    w.InitializeWorkflow(WorkflowType="Watertight Geometry")
    import_geom = w.TaskObject["Import Geometry"]

    with pytest.raises(AttributeError):
        import_geom.delete_child()


@pytest.mark.codegen_required
def test_iterate_meshing_workflow_task_container(new_meshing_session):
    workflow = new_meshing_session.workflow
    workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    tasks = [task for task in workflow.TaskObject]
    assert len(tasks) == 11
    assert tasks[0].name() == "Import Geometry"


@pytest.mark.codegen_required
def test_nonexistent_attrs(new_meshing_session):
    meshing = new_meshing_session
    assert not hasattr(meshing.workflow, "xyz")
    with pytest.raises(AttributeError):
        meshing.workflow.xyz


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=23.2")
def test_old_workflow_structure(new_meshing_session):
    meshing = new_meshing_session
    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    assert meshing.workflow.TaskObject["Import Geometry"]
    with pytest.raises(AttributeError):
        meshing.workflow.import_geometry


@pytest.mark.nightly
@pytest.mark.codegen_required
@pytest.mark.fluent_version("==24.2")
def test_new_2d_meshing_workflow(new_meshing_session):
    # Import geometry
    import_file_name = examples.download_file("NACA0012.fmd", "pyfluent/airfoils")
    meshing = new_meshing_session
    meshing.workflow.InitializeWorkflow(WorkflowType="2D Meshing")
    meshing.workflow.TaskObject["Load CAD Geometry"].Arguments.set_state(
        {
            r"FileName": import_file_name,
            r"LengthUnit": r"mm",
            r"Refaceting": {
                r"Refacet": False,
            },
        }
    )
    meshing.workflow.TaskObject["Load CAD Geometry"].Execute()

    meshing.workflow.TaskObject["Update Regions"].Execute()
    meshing.workflow.TaskObject["Update Boundaries"].Arguments.set_state(
        {
            r"SelectionType": r"zone",
        }
    )
    meshing.workflow.TaskObject["Update Boundaries"].Execute()

    meshing.workflow.TaskObject["Define Global Sizing"].Arguments.set_state(
        {
            r"CurvatureNormalAngle": 20,
            r"MaxSize": 2000,
            r"MinSize": 5,
            r"SizeFunctions": r"Curvature",
        }
    )
    meshing.workflow.TaskObject["Define Global Sizing"].Execute()

    meshing.workflow.TaskObject["Add Local Sizing"].Arguments.set_state(
        {
            r"AddChild": r"yes",
            r"BOIControlName": r"boi_1",
            r"BOIExecution": r"Body Of Influence",
            r"BOIFaceLabelList": [r"boi"],
            r"BOISize": 50,
            r"BOIZoneorLabel": r"label",
            r"DrawSizeControl": True,
        }
    )
    meshing.workflow.TaskObject["Add Local Sizing"].AddChildAndUpdate(DeferUpdate=False)

    meshing.workflow.TaskObject["Add Local Sizing"].Arguments.set_state(
        {
            r"AddChild": r"yes",
            r"BOIControlName": r"edgesize_1",
            r"BOIExecution": r"Edge Size",
            r"BOISize": 5,
            r"BOIZoneorLabel": r"label",
            r"DrawSizeControl": True,
            r"EdgeLabelList": [r"airfoil-te"],
        }
    )
    meshing.workflow.TaskObject["Add Local Sizing"].AddChildAndUpdate(DeferUpdate=False)

    meshing.workflow.TaskObject["Add Local Sizing"].Arguments.set_state(
        {
            r"AddChild": r"yes",
            r"BOIControlName": r"curvature_1",
            r"BOICurvatureNormalAngle": 10,
            r"BOIExecution": r"Curvature",
            r"BOIMaxSize": 2,
            r"BOIMinSize": 1.5,
            r"BOIScopeTo": r"edges",
            r"BOIZoneorLabel": r"label",
            r"DrawSizeControl": True,
            r"EdgeLabelList": [r"airfoil"],
        }
    )
    meshing.workflow.TaskObject["Add Local Sizing"].AddChildAndUpdate(DeferUpdate=False)

    meshing.workflow.TaskObject["Add 2D Boundary Layers"].Arguments.set_state(
        {
            r"AddChild": r"yes",
            r"BLControlName": r"aspect-ratio_1",
            r"NumberOfLayers": 4,
            r"OffsetMethodType": r"aspect-ratio",
        }
    )
    meshing.workflow.TaskObject["Add 2D Boundary Layers"].AddChildAndUpdate(
        DeferUpdate=False
    )
    meshing.workflow.TaskObject["Generate the Surface Mesh"].Arguments.set_state(
        {
            r"Surface2DPreferences": {
                r"MergeEdgeZonesBasedOnLabels": r"no",
                r"MergeFaceZonesBasedOnLabels": r"no",
                r"ShowAdvancedOptions": True,
            },
        }
    )
    meshing.workflow.TaskObject["Generate the Surface Mesh"].Execute()

    meshing.workflow.TaskObject["aspect-ratio_1"].Revert()
    meshing.workflow.TaskObject["aspect-ratio_1"].Arguments.set_state(
        {
            r"AddChild": r"yes",
            r"BLControlName": r"uniform_1",
            r"FirstLayerHeight": 2,
            r"NumberOfLayers": 4,
            r"OffsetMethodType": r"uniform",
        }
    )
    meshing.workflow.TaskObject["aspect-ratio_1"].Execute()
    meshing.workflow.TaskObject["Generate the Surface Mesh"].Arguments.set_state(None)
    meshing.workflow.TaskObject["Generate the Surface Mesh"].Arguments.set_state(
        {
            r"Surface2DPreferences": {
                r"MergeEdgeZonesBasedOnLabels": r"no",
                r"MergeFaceZonesBasedOnLabels": r"no",
                r"ShowAdvancedOptions": True,
            },
        }
    )
    meshing.workflow.TaskObject["Generate the Surface Mesh"].Execute()
    meshing.workflow.TaskObject["uniform_1"].Revert()
    meshing.workflow.TaskObject["uniform_1"].Arguments.set_state(
        {
            r"AddChild": r"yes",
            r"BLControlName": r"smooth-transition_1",
            r"FirstLayerHeight": 2,
            r"NumberOfLayers": 7,
            r"OffsetMethodType": r"smooth-transition",
        }
    )
    meshing.workflow.TaskObject["uniform_1"].Execute()

    meshing.workflow.TaskObject["Generate the Surface Mesh"].Arguments.set_state(None)
    meshing.workflow.TaskObject["Generate the Surface Mesh"].Arguments.set_state(
        {
            r"Surface2DPreferences": {
                r"MergeEdgeZonesBasedOnLabels": r"no",
                r"MergeFaceZonesBasedOnLabels": r"no",
                r"ShowAdvancedOptions": True,
            },
        }
    )
    meshing.workflow.TaskObject["Generate the Surface Mesh"].Execute()

    meshing.workflow.TaskObject["Export Fluent 2D Mesh"].Arguments.set_state(
        {
            r"FileName": r"C:\ANSYSDev\PyFluent_Dev_01\pyfluent\out\case1.msh.h5",
        }
    )
    meshing.workflow.TaskObject["Export Fluent 2D Mesh"].Execute()

    # Switch to solution mode
    solver = meshing.switch_to_solver()
    assert solver


@pytest.mark.fluent_version(">=24.1")
def test_setting_none_type_tasks(new_meshing_session):
    meshing = new_meshing_session
    meshing.workflow.InitializeWorkflow(WorkflowType=r"Fault-tolerant Meshing")
    meshing.workflow.setState(
        {
            r"TaskObject:Describe Overset Features": {},
        }
    )
    meshing.workflow.TaskObject["Describe Overset Features"].CommandName.setState(
        r"OversetOptions"
    )

    assert (
        meshing.workflow.TaskObject["Describe Overset Features"].CommandName()
        == "DescribeOversetFeatures"
    )


@pytest.mark.fluent_version(">=24.2")
def test_meshing_workflow_data_model_subscriptions(
    new_meshing_session,
):
    meshing = new_meshing_session
    workflow = meshing.workflow

    workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

    def on_changed(obj):
        on_changed.changed = True

    on_changed.changed = False

    m = meshing.meshing
    ig = m.ImportGeometry.create_instance()
    # is not working for command arguments
    # ig.FileName.add_on_changed(on_changed)
    ig.FileName = "dummy"
    # assert on_changed.changed is True

    on_changed.changed = False

    workflow.Workflow.WorkflowType.add_on_changed(on_changed)
    workflow.InitializeWorkflow(WorkflowType="Fault-tolerant Meshing")
    assert on_changed.changed is True


@pytest.mark.skip("Pending server availability.")
@pytest.mark.fluent_version(">=25.1")
def test_meshing_workflow_data_model_subscriptions_with_new_dm_api(
    new_meshing_session_new_api_enabled,
):
    meshing = new_meshing_session_new_api_enabled
    workflow = meshing.workflow

    workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

    def on_changed(obj):
        on_changed.changed = True

    on_changed.changed = False

    m = meshing.meshing
    ig = m.ImportGeometry.create_instance()
    ig.FileName.add_on_changed(on_changed)
    ig.FileName = "dummy"
    # assert on_changed.changed is True

    on_changed.changed = False

    workflow.Workflow.WorkflowType.add_on_changed(on_changed)
    workflow.InitializeWorkflow(WorkflowType="Fault-tolerant Meshing")
    assert on_changed.changed is True
