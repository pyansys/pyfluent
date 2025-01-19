""".. _ref_exhaust_system_settings_api:

Fault-tolerant meshing workflow using settings objects
------------------------------------------------------
This example sets up and solves a three-dimensional turbulent fluid flow
in a manifold exhaust system, which is common in the automotive industry,
using the PyFluent Settings API. Predicting the flow field in the area of the
mixing region is important to designing the junction properly.

This example uses the guided workflow for fault-tolerant meshing because it
is appropriate for geometries that can have imperfections, such as gaps and
leakages.

**Workflow tasks**

The fault-tolerant meshing workflow guides you through these tasks:

- Import a CAD geometry and manage individual parts
- Generate a surface mesh
- Cap inlets and outlets
- Extract a fluid region
- Define leakages
- Extract edge features
- Set up size controls
- Generate a volume mesh

**Problem description**

In the manifold exhaust system, air flows through the three inlets
with a uniform velocity of 1 m/s. The air then exits through the outlet.
A small pipe is placed in the main portion of the manifold where edge
extraction is considered. The example also includes a known small leakage
to demonstrate the automatic leakage detection aspects of the meshing workflow.
"""

###############################################################################
# Example Setup
# -------------
# Before you can use the fault-tolerant meshing workflow, you must set up the
# example and initialize this workflow.
#
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports, which includes downloading and importing
# the geometry file.

# sphinx_gallery_thumbnail_path = '_static/exhaust_system_settings.png'
import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

import_file_name = examples.download_file(
    "exhaust_system.fmd", "pyfluent/exhaust_system"
)

###############################################################################
# Launch Fluent
# ~~~~~~~~~~~~~
# Launch Fluent as a service in meshing mode with double precision running on
# two processors and print Fluent version.

meshing = pyfluent.launch_fluent(
    precision="double",
    processor_count=2,
    mode="meshing",
)
print(meshing.get_fluent_version())

###############################################################################
# Initialize workflow
# ~~~~~~~~~~~~~~~~~~~
# Initialize the fault-tolerant meshing workflow.

meshing.workflow.InitializeWorkflow(WorkflowType="Fault-tolerant Meshing")

###############################################################################
# Fault-folerant meshing workflow
# -------------------------------
# The fault-tolerant meshing workflow guides you through the many tasks that
# follow.
#
# Import CAD and manage parts
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import the CAD geometry file (``exhaust_system.fmd``) and selectively manage some
# parts.

meshing.upload(import_file_name)
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
meshing.PartManagement.ObjectSetting["DefaultObjectSetting"].OneZonePer.set_state(
    "part"
)
cad_import = meshing.workflow.TaskObject["Import CAD and Part Management"]
cad_import.Arguments.set_state(
    {
        "Context": 0,
        "CreateObjectPer": "Custom",
        "FMDFileName": import_file_name,
        "FileLoaded": "yes",
        "ObjectSetting": "DefaultObjectSetting",
        "Options": {
            "Line": False,
            "Solid": False,
            "Surface": False,
        },
    }
)
cad_import.Execute()

###############################################################################
# Describe geometry and flow
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Describe the geometry and the flow characteristics.

describe_geom = meshing.workflow.TaskObject["Describe Geometry and Flow"]
describe_geom.Arguments.set_state(
    {
        "AddEnclosure": "No",
        "CloseCaps": "Yes",
        "FlowType": "Internal flow through the object",
    }
)
describe_geom.UpdateChildTasks(SetupTypeChanged=False)
describe_geom.Arguments.set_state(
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
describe_geom.UpdateChildTasks(SetupTypeChanged=False)
describe_geom.Execute()

###############################################################################
# Enclose openings
# ~~~~~~~~~~~~~~~~
# Enclose (cap) any openings in the geometry.

###############################################################################
# .. image:: /_static/exhaust_system_011.png
#   :width: 400pt
#   :align: center

###############################################################################
# .. image:: /_static/exhaust_system_012.png
#   :width: 400pt
#   :align: center
capping = meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"]
capping.Arguments.set_state(
    {
        "CreatePatchPreferences": {
            "ShowCreatePatchPreferences": False,
        },
        "PatchName": "inlet-1",
        "SelectionType": "zone",
        "ZoneSelectionList": ["inlet.1"],
    }
)
capping.Arguments.set_state(
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
capping.AddChildToTask()

capping.InsertCompoundChildTask()
capping.Arguments.set_state({})
meshing.workflow.TaskObject["inlet-1"].Execute()
capping.Arguments.set_state(
    {
        "PatchName": "inlet-2",
        "SelectionType": "zone",
        "ZoneSelectionList": ["inlet.2"],
    }
)
capping.Arguments.set_state(
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
capping.AddChildToTask()

capping.InsertCompoundChildTask()
capping.Arguments.set_state({})
meshing.workflow.TaskObject["inlet-2"].Execute()
capping.Arguments.set_state(
    {
        "PatchName": "inlet-3",
        "SelectionType": "zone",
        "ZoneSelectionList": ["inlet"],
    }
)
capping.Arguments.set_state(
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
capping.AddChildToTask()

capping.InsertCompoundChildTask()
capping.Arguments.set_state({})
meshing.workflow.TaskObject["inlet-3"].Execute()
capping.Arguments.set_state(
    {
        "PatchName": "outlet-1",
        "SelectionType": "zone",
        "ZoneSelectionList": ["outlet"],
        "ZoneType": "pressure-outlet",
    }
)
capping.Arguments.set_state(
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
capping.AddChildToTask()

capping.InsertCompoundChildTask()
capping.Arguments.set_state({})
meshing.workflow.TaskObject["outlet-1"].Execute()

###############################################################################
# Extract edge features
# ~~~~~~~~~~~~~~~~~~~~~
# Extract edge features.
edge_features = meshing.workflow.TaskObject["Extract Edge Features"]
edge_features.Arguments.set_state(
    {
        "ExtractMethodType": "Intersection Loops",
        "ObjectSelectionList": ["flow_pipe", "main"],
    }
)
edge_features.AddChildToTask()

edge_features.InsertCompoundChildTask()
edge_group = meshing.workflow.TaskObject["edge-group-1"]
edge_group.Arguments.set_state(
    {
        "ExtractEdgesName": "edge-group-1",
        "ExtractMethodType": "Intersection Loops",
        "ObjectSelectionList": ["flow_pipe", "main"],
    }
)
edge_features.Arguments.set_state({})

edge_group.Execute()

###############################################################################
# Identify regions
# ~~~~~~~~~~~~~~~~
# Identify regions.
identify_regions = meshing.workflow.TaskObject["Identify Regions"]
identify_regions.Arguments.set_state(
    {
        "SelectionType": "zone",
        "X": 377.322045740589,
        "Y": -176.800676988458,
        "Z": -37.0764628583475,
        "ZoneSelectionList": ["main.1"],
    }
)
identify_regions.Arguments.set_state(
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
identify_regions.AddChildToTask()

identify_regions.InsertCompoundChildTask()
fluid_region_1 = meshing.workflow.TaskObject["fluid-region-1"]
fluid_region_1.Arguments.set_state(
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
identify_regions.Arguments.set_state({})

fluid_region_1.Execute()
identify_regions.Arguments.set_state(
    {
        "MaterialPointsName": "void-region-1",
        "NewRegionType": "void",
        "ObjectSelectionList": ["inlet-1", "inlet-2", "inlet-3", "main"],
        "X": 374.722045740589,
        "Y": -278.9775145640143,
        "Z": -161.1700719416913,
    }
)
identify_regions.AddChildToTask()

identify_regions.InsertCompoundChildTask()

identify_regions.Arguments.set_state({})

meshing.workflow.TaskObject["void-region-1"].Execute()

###############################################################################
# Define thresholds for leakages
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define thresholds for potential leakages.
leakage_threshold = meshing.workflow.TaskObject["Define Leakage Threshold"]
leakage_threshold.Arguments.set_state(
    {
        "AddChild": "yes",
        "FlipDirection": True,
        "PlaneDirection": "X",
        "RegionSelectionSingle": "void-region-1",
    }
)
leakage_threshold.AddChildToTask()

leakage_threshold.InsertCompoundChildTask()
leakage_1 = meshing.workflow.TaskObject["leakage-1"]
leakage_1.Arguments.set_state(
    {
        "AddChild": "yes",
        "FlipDirection": True,
        "LeakageName": "leakage-1",
        "PlaneDirection": "X",
        "RegionSelectionSingle": "void-region-1",
    }
)
leakage_threshold.Arguments.set_state(
    {
        "AddChild": "yes",
    }
)
leakage_1.Execute()

###############################################################################
# Review region settings
# ~~~~~~~~~~~~~~~~~~~~~~
# Review the region settings.
update_region = meshing.workflow.TaskObject["Update Region Settings"]
update_region.Arguments.set_state(
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
update_region.Execute()


###############################################################################
# Set mesh control options
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Set mesh control options.

meshing.workflow.TaskObject["Choose Mesh Control Options"].Execute()

###############################################################################
# Generate surface mesh
# ~~~~~~~~~~~~~~~~~~~~~
# Generate the surface mesh.

###############################################################################
# .. image:: /_static/exhaust_system_013.png
#   :width: 500pt
#   :align: center

meshing.workflow.TaskObject["Generate the Surface Mesh"].Execute()

###############################################################################
# Confirm and update boundaries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Confirm and update the boundaries.

meshing.workflow.TaskObject["Update Boundaries"].Execute()

###############################################################################
# Add boundary layers
# ~~~~~~~~~~~~~~~~~~~
# Add boundary layers.

meshing.workflow.TaskObject["Add Boundary Layers"].AddChildToTask()

meshing.workflow.TaskObject["Add Boundary Layers"].InsertCompoundChildTask()

meshing.workflow.TaskObject["aspect-ratio_1"].Arguments.set_state(
    {
        "BLControlName": "aspect-ratio_1",
    }
)
meshing.workflow.TaskObject["Add Boundary Layers"].Arguments.set_state({})

meshing.workflow.TaskObject["aspect-ratio_1"].Execute()

###############################################################################
# Generate volume mesh
# ~~~~~~~~~~~~~~~~~~~~
# Generate the volume mesh.

###############################################################################
# .. image:: /_static/exhaust_system_014.png
#   :width: 500pt
#   :align: center
volume_mesh_gen = meshing.workflow.TaskObject["Generate the Volume Mesh"]
volume_mesh_gen.Arguments.set_state(
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
volume_mesh_gen.Execute()

###############################################################################
# Check mesh
# ~~~~~~~~~~
# Check the mesh.

meshing.tui.mesh.check_mesh()

###############################################################################
# Solve and postprocess
# ---------------------
# Once you have completed the fault tolerate meshing workflow, you can solve and
# postprcess the results.
#
# Switch to solution mode
# ~~~~~~~~~~~~~~~~~~~~~~~
# Switch to the solution mode.

solver = meshing.switch_to_solver()

solver.mesh.check()

###############################################################################
# Select turbulence model
# ~~~~~~~~~~~~~~~~~~~~~~~
# Select the kw sst turbulence model.

viscous = solver.setup.models.viscous

viscous.model = "k-omega"
viscous.k_omega_model = "sst"

###############################################################################
# Set velocity and turbulence boundary conditions for first inlet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the velocity and turbulence boundary conditions for the first inlet
# (``inlet-1``).

boundary_conditions = solver.setup.boundary_conditions

boundary_conditions.velocity_inlet["inlet-1"] = {
    "momentum": {
        "velocity_specification_method": "Magnitude, Normal to Boundary",
        "velocity": {
            "value": 1,
        },
    },
}

###############################################################################
# Set same boundary conditions for other velocity inlets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the same boundary conditions for the other velocity inlets (``inlet_2``
# and ``inlet_3``).

boundary_conditions.copy(
    from_="inlet-1",
    to=["inlet-2", "inlet-3"],
)

###############################################################################
# Set boundary conditions at outlet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the boundary conditions at the outlet (``outlet-1``).

boundary_conditions.pressure_outlet["outlet-1"].turbulence.turbulent_intensity = 0.05

###############################################################################
# Initialize flow field
# ~~~~~~~~~~~~~~~~~~~~~
# Initialize the flow field using hybrid initialization.

solver.solution.initialization.hybrid_initialize()

###############################################################################
# Start calculation
# ~~~~~~~~~~~~~~~~~
# Start the calculation by requesting 100 iterations.

###############################################################################
# .. image:: /_static/exhaust_system_015.png
#   :width: 500pt
#   :align: center

solver.solution.run_calculation.iterate(iter_count=100)

###############################################################################
# Write the case and data files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

solver.file.write(
    file_type="case-data",
    file_name="exhaust_system.cas.h5",
)

###############################################################################
# Configure graphics picture export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Since Fluent is being run without the GUI, we will need to export plots as
# picture files. Edit the picture settings to use a custom resolution so that
# the images are large enough.

graphics = solver.results.graphics
# use_window_resolution option not active inside containers or Ansys Lab environment
if graphics.picture.use_window_resolution.is_active():
    graphics.picture.use_window_resolution = False
graphics.picture.x_resolution = 1920
graphics.picture.y_resolution = 1440

###############################################################################
# Create path lines
# ~~~~~~~~~~~~~~~~~
# Create path lines highlighting the flow field, display it, then export the
# image for inspection.

###############################################################################
# .. image:: /_static/exhaust_system_016.png
#   :width: 500pt
#   :align: center

graphics.pathline["pathlines-1"] = {
    "field": "time",
    "accuracy_control": {
        "tolerance": 0.001,
    },
    "skip": 5,
    "release_from_surfaces": ["inlet-1", "inlet-2", "inlet-3"],
}
graphics.pathline["pathlines-1"].display()

graphics.views.restore_view(view_name="isometric")
graphics.views.auto_scale()
graphics.picture.save_picture(file_name="pathlines-1.png")

###############################################################################
# Create iso-surface
# ~~~~~~~~~~~~~~~~~~
# Create an iso-surface through the manifold geometry.

solver.results.surfaces.iso_surface["surf-x-coordinate"] = {
    "field": "x-coordinate",
    "zones": ["fluid-region-1"],
    "iso_values": [0.38],
}

###############################################################################
# Create contours of velocity magnitude
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create contours of the velocity magnitude throughout the manifold
# along with the mesh. Display it and export the image for inspection.

###############################################################################
# .. image:: /_static/exhaust_system_017.png
#   :width: 500pt
#   :align: center

graphics.contour["contour-velocity"] = {
    "field": "velocity-magnitude",
    "surfaces_list": ["surf-x-coordinate"],
    "node_values": False,
    "range_option": {
        "option": "auto-range-on",
        "auto_range_on": {
            "global_range": False,
        },
    },
}
graphics.mesh["mesh-1"] = {
    "surfaces_list": "*",
}
graphics.contour["contour-velocity"].display()

graphics.views.restore_view(view_name="right")
graphics.views.auto_scale()
graphics.picture.save_picture(file_name="contour-velocity.png")

###############################################################################
# Create scene
# ~~~~~~~~~~~~
# Create a scene containing the mesh and the contours. Display it and export
# the image for inspection.

###############################################################################
# .. image:: /_static/exhaust_system_018.png
#   :width: 500pt
#   :align: center

solver.results.scene["scene-1"] = {}
scene1 = solver.results.scene["scene-1"]
scene1.graphics_objects.add(name="mesh-1")
scene1.graphics_objects["mesh-1"].transparency = 90
scene1.graphics_objects.add(name="contour-velocity")
scene1.display()

graphics.views.camera.position(xyz=[1.70, 1.14, 0.29])
graphics.views.camera.up_vector(xyz=[-0.66, 0.72, -0.20])
graphics.picture.save_picture(file_name="scene-1.png")

#########################################################################
# Close Fluent
# ~~~~~~~~~~~~
# Close Fluent.

solver.exit()
