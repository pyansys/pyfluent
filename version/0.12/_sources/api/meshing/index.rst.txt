.. _ref_meshing:

Meshing
=======
The ``meshing`` module allows you to use Fluent meshing capabilities from Python.
Meshing workflows and meshing TUI commands are available.

Workflow example
----------------

.. code:: python

    import ansys.fluent.core as pyfluent

    meshing = pyfluent.launch_fluent(mode="meshing")
    meshing.transcript.start()
    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    meshing.workflow.TaskObject["Import Geometry"].Arguments = {"FileName": "cylinder.agdb"}
    meshing.workflow.TaskObject["Import Geometry"].Execute()
    meshing.tui.mesh.check_mesh()
    exit()

You can manually convert existing Fluent meshing workflow journals to
session-based PyFluent scripts. Examples follow of a Fluent journal and the
equivalent PyFluent script.

**Fluent journal**

.. code:: scheme

    (%py-exec "workflow.InitializeWorkflow(WorkflowType=r'Watertight Geometry')")
    (%py-exec "workflow.TaskObject['Import Geometry'].Arguments.set_state({r'FileName': r'file.pmdb',r'LengthUnit': r'in',})")
    (%py-exec "workflow.TaskObject['Import Geometry'].Execute()")
    (%py-exec "workflow.TaskObject['Add Local Sizing'].AddChildToTask()")
    (%py-exec "workflow.TaskObject['Add Local Sizing'].Execute()")
    (%py-exec "workflow.TaskObject['Generate the Surface Mesh'].Arguments.set_state({r'CFDSurfaceMeshControls': {r'MaxSize': 0.3,},})")
    (%py-exec "workflow.TaskObject['Generate the Surface Mesh'].Execute()")
    (%py-exec "workflow.TaskObject['Describe Geometry'].UpdateChildTasks(SetupTypeChanged=False)")
    (%py-exec "workflow.TaskObject['Describe Geometry'].Arguments.set_state({r'SetupType': r'The geometry consists of only fluid regions with no voids',})")
    (%py-exec "workflow.TaskObject['Describe Geometry'].UpdateChildTasks(SetupTypeChanged=True)")
    (%py-exec "workflow.TaskObject['Describe Geometry'].Execute()")
    (%py-exec "workflow.TaskObject['Update Boundaries'].Arguments.set_state({r'BoundaryLabelList': [r'wall-inlet'],r'BoundaryLabelTypeList': [r'wall'],r'OldBoundaryLabelList': [r'wall-inlet'],r'OldBoundaryLabelTypeList': [r'velocity-inlet'],})")
    (%py-exec "workflow.TaskObject['Update Boundaries'].Execute()")
    (%py-exec "workflow.TaskObject['Update Regions'].Execute()")
    (%py-exec "workflow.TaskObject['Add Boundary Layers'].AddChildToTask()")
    (%py-exec "workflow.TaskObject['Add Boundary Layers'].InsertCompoundChildTask()")
    (%py-exec "workflow.TaskObject['smooth-transition_1'].Arguments.set_state({r'BLControlName': r'smooth-transition_1',})")
    (%py-exec "workflow.TaskObject['Add Boundary Layers'].Arguments.set_state({})")
    (%py-exec "workflow.TaskObject['smooth-transition_1'].Execute()")
    (%py-exec "workflow.TaskObject['Generate the Volume Mesh'].Arguments.set_state({r'VolumeFill': r'poly-hexcore',r'VolumeFillControls': {r'HexMaxCellLength': 0.3,},})")
    (%py-exec "workflow.TaskObject['Generate the Volume Mesh'].Execute()")

**PyFluent script**

.. code:: python

    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    meshing.workflow.TaskObject["Import Geometry"].Arguments = {
        "FileName": import_filename,
        "LengthUnit": "in",
    }
    meshing.workflow.TaskObject["Import Geometry"].Execute()
    meshing.workflow.TaskObject["Add Local Sizing"].AddChildToTask()
    meshing.workflow.TaskObject["Add Local Sizing"].Execute()
    meshing.workflow.TaskObject["Generate the Surface Mesh"].Arguments = {
        "CFDSurfaceMeshControls": {"MaxSize": 0.3}
    }
    meshing.workflow.TaskObject["Generate the Surface Mesh"].Execute()
    meshing.workflow.TaskObject["Describe Geometry"].UpdateChildTasks(
        SetupTypeChanged=False
    )
    meshing.workflow.TaskObject["Describe Geometry"].Arguments = {
        SetupType: "The geometry consists of only fluid regions with no voids"
    }
    meshing.workflow.TaskObject["Describe Geometry"].UpdateChildTasks(SetupTypeChanged=True)
    meshing.workflow.TaskObject["Describe Geometry"].Execute()
    meshing.workflow.TaskObject["Update Boundaries"].Arguments = {
        "BoundaryLabelList": ["wall-inlet"],
        "BoundaryLabelTypeList": ["wall"],
        "OldBoundaryLabelList": ["wall-inlet"],
        "OldBoundaryLabelTypeList": ["velocity-inlet"],
    }
    meshing.workflow.TaskObject["Update Boundaries"].Execute()
    meshing.workflow.TaskObject["Update Regions"].Execute()
    meshing.workflow.TaskObject["Add Boundary Layers"].AddChildToTask()
    meshing.workflow.TaskObject["Add Boundary Layers"].InsertCompoundChildTask()
    meshing.workflow.TaskObject["smooth-transition_1"].Arguments = {
        "BLControlName": "smooth-transition_1",
    }
    meshing.workflow.TaskObject["Add Boundary Layers"].Arguments = {}
    meshing.workflow.TaskObject["smooth-transition_1"].Execute()
    meshing.workflow.TaskObject["Generate the Volume Mesh"].Arguments = {
        "VolumeFill": "poly-hexcore",
        "VolumeFillControls": {
            "HexMaxCellLength": 0.3,
        },
    }
    meshing.workflow.TaskObject["Generate the Volume Mesh"].Execute()

TUI commands example
--------------------

.. code:: python

    import ansys.fluent.core as pyfluent

    meshing_session = pyfluent.launch_fluent(mode="meshing")
    meshing_session.tui.file.read_case("elbow.cas.gz")
    solver = meshing_session.switch_to_solver()
    solver.tui.define.models.unsteady_2nd_order("yes")
    exit()

.. currentmodule:: ansys.fluent.core.meshing

.. autosummary::
   :toctree: _autosummary

.. toctree::
   :maxdepth: 2
   :hidden:

   tui/index
   datamodel/index
   