"""
End-to-end Fluent Solver Workflow using Watertight Meshing
-----------------------------------------------------------------------------
This test covers the setup and solution of a three-dimensional
turbulent fluid flow and heat transfer problem in a mixing elbow. The mixing
elbow configuration is encountered in piping systems in power plants and
processindustries. It is often important to predict the flow field and
temperature field in the area of the mixing regionin order to properly design
the junction.

This test queries the following using PyTest:

- Meshing workflow tasks state before and after the task execution
- Report definitions check after solution
"""

from functools import partial

from pytest import approx
from util.meshing_workflow import (  # noqa: F401
    assign_task_arguments,
    execute_task_with_pre_and_postcondition_checks,
    mixing_elbow_geometry,
    new_mesh_session,
    new_watertight_workflow,
    new_watertight_workflow_session,
)
from util.solver import check_report_definition_result


def test_mixing_elbow(create_mesh_session, mixing_elbow_geometry):

    session = new_watertight_workflow_session
    workflow = session.meshing.workflow

    assign_task_args = partial(
        assign_task_arguments, workflow=workflow, check_state=True
    )

    execute_task_with_pre_and_postconditions = partial(
        execute_task_with_pre_and_postcondition_checks, workflow=workflow
    )

    ###############################################################################
    # Import the CAD geometry
    # Query the task state before and after task execution
    assign_task_args(
        task_name="Import Geometry",
        FileName=mixing_elbow_geometry,
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
        task_name="Generate the Surface Mesh",
        CFDSurfaceMeshControls={"MaxSize": 0.3},
    )

    execute_task_with_pre_and_postconditions(task_name="Generate the Surface Mesh")

    ###############################################################################
    # Describe the geometry
    # Query the task state before and after task execution
    workflow.TaskObject["Describe Geometry"].UpdateChildTasks(SetupTypeChanged=False)
    assign_task_args(
        task_name="Describe Geometry",
        SetupType="The geometry consists of only fluid regions with no voids",
    )
    workflow.TaskObject["Describe Geometry"].UpdateChildTasks(SetupTypeChanged=True)

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
    workflow.TaskObject["Add Boundary Layers"].AddChildToTask()
    workflow.TaskObject["Add Boundary Layers"].InsertCompoundChildTask()
    assign_task_args(
        task_name="smooth-transition_1", BLControlName="smooth-transition_1"
    )
    workflow.TaskObject["Add Boundary Layers"].Arguments = {}

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
    session.meshing.tui.mesh.check_mesh()

    ###############################################################################
    # Switch to Solution mode
    session.meshing.tui.switch_to_solution_mode("yes")

    ###############################################################################
    # Check the mesh in Solver mode
    session.solver.tui.mesh.check()

    ###############################################################################
    # Set the working units for the mesh
    session.solver.tui.define.units("length", "in")

    ###############################################################################
    # Enable heat transfer by activating the energy equation.
    session.solver.tui.define.models.energy("yes", ", ", ", ", ", ", ", ")

    ###############################################################################
    # Create a new material called water-liquid.
    session.solver.tui.define.materials.copy("fluid", "water-liquid")

    ###############################################################################
    # Set up the cell zone conditions for the fluid zone (elbow-fluid). Select
    # water-liquid from the Material list.
    session.solver.tui.define.boundary_conditions.fluid(
        "elbow-fluid",
        "yes",
        "water-liquid",
        "no",
        "no",
        "no",
        "no",
        "0",
        "no",
        "0",
        "no",
        "0",
        "no",
        "0",
        "no",
        "0",
        "no",
        "1",
        "no",
        "no",
        "no",
        "no",
        "no",
    )

    ###############################################################################
    # Set up the boundary conditions
    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "cold-inlet", [], "vmag", "no", 0.4, "quit"
    )
    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "cold-inlet", [], "ke-spec", "no", "no", "no", "yes", "quit"
    )
    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "cold-inlet", [], "turb-intensity", 5, "quit"
    )
    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "cold-inlet", [], "turb-hydraulic-diam", 4, "quit"
    )
    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "cold-inlet", [], "temperature", "no", 293.15, "quit"
    )

    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "hot-inlet", [], "vmag", "no", 1.2, "quit"
    )
    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "hot-inlet", [], "ke-spec", "no", "no", "no", "yes", "quit"
    )
    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "hot-inlet", [], "turb-intensity", 5, "quit"
    )
    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "hot-inlet", [], "turb-hydraulic-diam", 1, "quit"
    )
    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "hot-inlet", [], "temperature", "no", 313.15, "quit"
    )

    session.solver.tui.define.boundary_conditions.set.pressure_outlet(
        "outlet", [], "turb-intensity", 5, "quit"
    )
    session.solver.tui.define.boundary_conditions.set.pressure_outlet(
        "outlet", [], "turb-viscosity-ratio", 4, "quit"
    )

    ###############################################################################
    # Enable the plotting of residuals during the calculation.
    session.solver.tui.solve.monitors.residual.plot("yes")

    ###############################################################################
    # Initialize the flow field using the Hybrid Initialization
    session.solver.tui.solve.initialize.hyb_initialization()

    ###############################################################################
    # Solve for 250 Iterations.
    session.solver.tui.solve.iterate(250)

    ###############################################################################
    # Assert the returned mass flow rate report definition value
    session.solver.root.solution.report_definitions.flux["mass_flow_rate"] = {}
    session.solver.root.solution.report_definitions.flux[
        "mass_flow_rate"
    ].zone_names = [
        "cold-inlet",
        "hot-inlet",
        "outlet",
    ]

    check_report_definition = partial(
        check_report_definition_result,
        report_definitions=session.solver.root.solution.report_definitions,
    )

    check_report_definition(
        report_definition_name="mass_flow_rate",
        expected_result=approx(-2.985690364942784e-06, abs=1e-3),
    )

    ###############################################################################
    # Assert the returned temperature report definition value on the outlet surface
    session.solver.root.solution.report_definitions.surface["temperature_outlet"] = {}
    session.solver.root.solution.report_definitions.surface[
        "temperature_outlet"
    ].report_type = "surface-massavg"
    session.solver.root.solution.report_definitions.surface[
        "temperature_outlet"
    ].field = "temperature"
    session.solver.root.solution.report_definitions.surface[
        "temperature_outlet"
    ].surface_names = ["outlet"]

    check_report_definition(
        report_definition_name="temperature_outlet",
        expected_result=approx(296.229, rel=1e-3),
    )

    ###############################################################################
