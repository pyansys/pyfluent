""".. _ref_mixing_elbow_tui_api:

Watertight geometry meshing workflow
------------------------------------
This example sets up and solves a three-dimensional turbulent fluid flow
and heat transfer problem in a mixing elbow, which is common in piping
systems in power plants and process industries. Predicting the flow field
and temperature field in the area of the mixing region is important to
designing the junction properly.

This example uses the guided workflow for watertight geometry meshing
because it is appropriate for geometries that can have no imperfections,
such as gaps and leakages.

**Workflow tasks**

The watertight geometry meshing workflow guides you through these tasks:

- Import a CAD geometry
- Generate a surface mesh
- Describe the geometry
- Generate a volume mesh

**Problem description**

A cold fluid at 20 deg C flows into the pipe through a large inlet. It then mixes
with a warmer fluid at 40 deg C that enters through a smaller inlet located at
the elbow. The pipe dimensions are in inches, and the fluid properties and
boundary conditions are given in SI units. Because the Reynolds number for the
flow at the larger inlet is ``50, 800``, a turbulent flow model is required.
"""

###############################################################################
# Example Setup
# -------------
# Before you can use the watertight geometry meshing workflow, you must set up the
# example and initialize this workflow.
#
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports, which includes downloading and importing
# the geometry file.

# sphinx_gallery_thumbnail_path = '_static/mixing_elbow.png'
import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

pyfluent.CONTAINER_MOUNT_PATH = pyfluent.EXAMPLES_PATH
import_file_name = examples.download_file("mixing_elbow.pmdb", "pyfluent/mixing_elbow")

###############################################################################
# Launch Fluent
# ~~~~~~~~~~~~~
# Launch Fluent as a service in meshing mode with double precision running on
# two processors.

meshing = pyfluent.launch_fluent(
    precision="double",
    processor_count=2,
    mode="meshing",
)


###############################################################################
# Initialize workflow
# ~~~~~~~~~~~~~~~~~~~
# Initialize the watertight geometry meshing workflow.

meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")


###############################################################################
# Watertight geometry meshing workflow
# ------------------------------------
# The fault-tolerant meshing workflow guides you through the several tasks that
# follow.
#
# Import CAD and set length units
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import the CAD geometry and set the length units to inches.
geo_import = meshing.workflow.TaskObject["Import Geometry"]
geo_import.Arguments = {
    "FileName": import_file_name,
    "LengthUnit": "in",
}

# Import geometry
# ~~~~~~~~~~~~~~~
# Import the geometry.

geo_import.Execute()

###############################################################################
# Add local sizing
# ~~~~~~~~~~~~~~~~
# Add local sizing. This task asks whether you want to add local sizing controls
# to the faceted geometry. You can keep the default settings and execute the task.
add_local_sizing = meshing.workflow.TaskObject["Add Local Sizing"]
add_local_sizing.AddChildToTask()
add_local_sizing.Execute()

###############################################################################
# Generate surface mesh
# ~~~~~~~~~~~~~~~~~~~~~
# Generate the surface mash. In this task, you can set various properties of the
# surface mesh for the faceted geometry. For ``"MaxSize"``, set ``0.3``.
surface_mesh_gen = meshing.workflow.TaskObject["Generate the Surface Mesh"]
surface_mesh_gen.Arguments = {"CFDSurfaceMeshControls": {"MaxSize": 0.3}}
surface_mesh_gen.Execute()

###############################################################################
# Describe geometry
# ~~~~~~~~~~~~~~~~~
# Describe the geometry. In this task, you are prompted with questions
# relating to the nature of the imported geometry, which defines
# the fluid region. The geometry consists of only fluid regions.
describe_geo = meshing.workflow.TaskObject["Describe Geometry"]
describe_geo.UpdateChildTasks(SetupTypeChanged=False)
describe_geo.Arguments = {
    "SetupType": "The geometry consists of only fluid regions with no voids"
}
describe_geo.UpdateChildTasks(SetupTypeChanged=True)
describe_geo.Execute()

###############################################################################
# Update boundaries
# ~~~~~~~~~~~~~~~~~
# Update the boundaries. Set ``"BoundaryLabelTypeList"`` to ``"wall"`` and
# update the boundaries.
update_boundaries = meshing.workflow.TaskObject["Update Boundaries"]
update_boundaries.Arguments = {
    "BoundaryLabelList": ["wall-inlet"],
    "BoundaryLabelTypeList": ["wall"],
    "OldBoundaryLabelList": ["wall-inlet"],
    "OldBoundaryLabelTypeList": ["velocity-inlet"],
}
update_boundaries.Execute()

###############################################################################
# Update regions
# ~~~~~~~~~~~~~~
# Update the regions. In this task, you can review the names and types of
# the various regions that have been generated from your imported geometry and
# change them as needed. You can keep the default settings.

meshing.workflow.TaskObject["Update Regions"].Execute()

###############################################################################
# Add boundary layers
# ~~~~~~~~~~~~~~~~~~~
# Add boundary layers, which consist of setting properties for the
# boundary layer mesh. You can keep the default settings.
add_boundary_layers = meshing.workflow.TaskObject["Add Boundary Layers"]
add_boundary_layers.AddChildToTask()
add_boundary_layers.InsertCompoundChildTask()
smooth_transition_1 = meshing.workflow.TaskObject["smooth-transition_1"]
smooth_transition_1.Arguments = {
    "BLControlName": "smooth-transition_1",
}
add_boundary_layers.Arguments = {}
smooth_transition_1.Execute()

###############################################################################
# Generate volume mesh
# ~~~~~~~~~~~~~~~~~~~~
# Generate the volume mesh, which consists of setting properties for the
# volume mesh. Set ``"VolumeFill"`` to ``"poly-hexcore"``.
volume_mesh_gen = meshing.workflow.TaskObject["Generate the Volume Mesh"]
volume_mesh_gen.Arguments = {
    "VolumeFill": "poly-hexcore",
    "VolumeFillControls": {
        "HexMaxCellLength": 0.3,
    },
}
volume_mesh_gen.Execute()

###############################################################################
# .. image:: /_static/mixing_elbow_011.png
#   :width: 500pt
#   :align: center

###############################################################################
# Check mesh in meshing mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Check the mesh in meshing mode

meshing.tui.mesh.check_mesh()

###############################################################################
# Save mesh file
# ~~~~~~~~~~~~~~
# Save the mesh file (``mixing_elbow.msh.h5``).

meshing.tui.file.write_mesh("mixing_elbow.msh.h5")

###############################################################################
# Solve and postprocess
# ---------------------
# Once you have completed the watertight geometry meshing workflow, you can
# solve and postprcess the results.
#
# Switch to solution mode
# ~~~~~~~~~~~~~~~~~~~~~~~
# Switch to solution mode. Now that a high-quality mesh has been generated
# using Fluent in meshing mode, you can switch to solver mode to complete the
# setup of the simulation. Because you have just checked the mesh, set ``"yes"``
# to switch to the solution mode.

solver = meshing.switch_to_solver()

###############################################################################
# Check mesh in solver mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Check the mesh in solver mode. The mesh check lists the minimum and maximum
# x, y, and z values from the mesh in the default SI units of meters. It also
# reports a number of other mesh features that are checked. Any errors in the
# mesh are reported. Ensure that the minimum volume is not negative because
# Fluent cannot begin a calculation when this is the case.

solver.tui.mesh.check()

###############################################################################
# Enable heat transfer
# ~~~~~~~~~~~~~~~~~~~~
# Enable heat transfer by activating the energy equation.

solver.tui.define.models.energy("yes", ", ", ", ", ", ", ", ")

###############################################################################
# Create material
# ~~~~~~~~~~~~~~~
# Create a material named ``"water-liquid"``.

solver.tui.define.materials.copy("fluid", "water-liquid")

###############################################################################
# Set up cell zone conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set up the cell zone conditions for the fluid zone (``elbow-fluid``)``. Set the
# material to ``"water-liquid"``.

solver.tui.define.boundary_conditions.fluid(
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
# Set up boundary conditions for CFD analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set up the boundary conditions for the inlets, outlet, and walls for CFD
# analysis.

# cold inlet (cold-inlet), Setting: Value:
# Velocity Specification Method: Magnitude, Normal to Boundary
velocity_inlet = solver.tui.define.boundary_conditions.set.velocity_inlet
velocity_inlet("cold-inlet", [], "vmag", "no", 0.4, "quit")
velocity_inlet("cold-inlet", [], "ke-spec", "no", "no", "no", "yes", "quit")
velocity_inlet("cold-inlet", [], "turb-intensity", 5, "quit")
velocity_inlet("cold-inlet", [], "turb-hydraulic-diam", 4, "quit")
velocity_inlet("cold-inlet", [], "temperature", "no", 293.15, "quit")

# hot inlet (hot-inlet), Setting: Value:
# Velocity Specification Method: Magnitude, Normal to Boundary

velocity_inlet("hot-inlet", [], "vmag", "no", 1.2, "quit")
velocity_inlet("hot-inlet", [], "ke-spec", "no", "no", "no", "yes", "quit")
velocity_inlet("hot-inlet", [], "turb-intensity", 5, "quit")
velocity_inlet("hot-inlet", [], "turb-hydraulic-diam", 1, "quit")
velocity_inlet("hot-inlet", [], "temperature", "no", 313.15, "quit")

# pressure outlet (outlet), Setting: Value:
# Backflow Turbulent Intensity: 5 [%]
# Backflow Turbulent Viscosity Ratio: 4
pressure_outlet = solver.tui.define.boundary_conditions.set.pressure_outlet
pressure_outlet("outlet", [], "turb-intensity", 5, "quit")
pressure_outlet("outlet", [], "turb-viscosity-ratio", 4, "quit")

###############################################################################
# Enable plotting of residuals during calculation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Enable plotting of residuals during the calculation.

solver.tui.solve.monitors.residual.plot("yes")

###############################################################################
# Create surface report definition
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a surface report definition of the average temperature at the outlet
# named ``"outlet-temp-avg"``.

solver.tui.solve.report_definitions.add(
    "outlet-temp-avg",
    "surface-massavg",
    "field",
    "temperature",
    "surface-names",
    "outlet",
    "()",
    "quit",
)

###############################################################################
# Create expression report definition
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a report definition of single value expression type computing the difference
# of area-averaged static pressure over cold-inlet and oulet. The name of the
# report definition is ``"ave-pressure-diff"``.

solver.tui.solve.report_definitions.add(
    "ave-pressure-diff",
    "single-val-expression",
    "define",
    "\"AreaAve(StaticPressure, ['cold-inlet'])-AreaAve(StaticPressure, ['outlet'])\"",
    "quit",
)

###############################################################################
# Create convergence condition
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a convergence condition for ``outlet-temp-avg``.

# - Set ``"add"`` to ``"con-outlet-temp-avg"``.
# - Set ``"report-defs"`` to ``"outlet-temp-avg"``.
# - Set ``"stop-criterion"`` to ``"1e-04"``.
# - Set ``"initial-values-to-ignore"`` to ``"20"``.
# - Set ``"previous-values-to-consider"`` to ``"15"``.
# - Set ``"print?"``to ``"yes"``.
# - Set ``"frequency"`` to ``"3"``.
#
# These settings cause Fluent to consider the solution converged when the
# surface report definition value for each of the previous 15 iterations is
# within 0.001% of the current value. Convergence of the values is checked
# every 3 iterations. The first 20 iterations are ignored, allowing for any
# initial solution dynamics to settle out. Note that the value printed to the
# console is the deviation between the current and previous iteration values
# only.

solver.tui.solve.convergence_conditions(
    "conv-reports",
    "add",
    "con-outlet-temp-avg",
    "initial-values-to-ignore",
    "20",
    "previous-values-to-consider",
    "15",
    "print?",
    "yes",
    "report-defs",
    "outlet-temp-avg",
    "stop-criterion",
    "1e-04",
    "quit",
    "quit",
    "condition",
    "1",
    "frequency",
    "3",
    "quit",
)
solver.tui.solve.convergence_conditions("frequency", "3", "quit")

###############################################################################
# Initialize flow field
# ~~~~~~~~~~~~~~~~~~~~~
# Initialize the flow field using hybrid initialization.

solver.tui.solve.initialize.hyb_initialization()

###############################################################################
# Save case file
# ~~~~~~~~~~~~~~
# Solve the case file (``mixing_elbow1.cas.h5``).

solver.tui.file.write_case("mixing_elbow1.cas.h5")

###############################################################################
# Solve for 100 iterations
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Solve for 100 iterations.

solver.tui.solve.iterate(100)

###############################################################################
# .. image:: /_static/mixing_elbow_012.png
#   :width: 500pt
#   :align: center

###############################################################################
# .. image:: /_static/mixing_elbow_013.png
#   :width: 500pt
#   :align: center

###############################################################################
# Save data file
# ~~~~~~~~~~~~~~
# Save the data file (``mixing_elbow1.dat.h5``).

solver.tui.file.write_data("mixing_elbow1.dat.h5")

###############################################################################
# Configure graphics picture export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Since Fluent is being run without the GUI, we will need to export plots as
# picture files. Edit the picture settings to use a custom resolution so that
# the images are large enough.

picture = solver.tui.display.set.picture
# use-window-container TUI option not available inside containers or Ansys Lab environment
if "use_window_resolution" in dir(picture):
    picture.use_window_resolution("no")
picture.x_resolution("1920")
picture.y_resolution("1440")

###############################################################################
# Create definition for velocity magnitude contours
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create and display a definition for the velocity magnitude contours on the
# symmetry plane. Then display it and export the image for inspection.
#
# - Set ``"contour"`` to ``"contour-vel"``.
# - Set ``"field"`` to ``"velocity-magnitude"``.
# - Set ``"surfaces-list"`` to ``"symmetry-xyplane"``.
# - Set ``"display"`` to ``"contour-vel contour"``.

solver.tui.display.objects.create(
    "contour",
    "contour-vel",
    "filled?",
    "yes",
    "node-values?",
    "yes",
    "field",
    "velocity-magnitude",
    "surfaces-list",
    "symmetry-xyplane",
    "()",
    "coloring",
    "banded",
    "quit",
)

solver.tui.display.objects.display("contour-vel")

views = solver.tui.display.views
views.restore_view("front")
views.auto_scale()
solver.tui.display.save_picture("contour-vel.png")

###############################################################################
# .. image:: /_static/mixing_elbow_014.png
#   :width: 500pt
#   :align: center

###############################################################################
# Create definition for temperature contours
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create and display a definition for temperature contours on the symmetry
# plane. Then display it and export the image for inspection.
#
# - Set ``"contour"`` to ``"contour-temp"``.
# - Set ``"field"`` to ``"temperature"``.
# - Set ``"surfaces-list"`` to ``"symmetry-xyplane"``.
# - Set ``"display"`` to ``"contour-temp contour"``.

solver.tui.display.objects.create(
    "contour",
    "contour-temp",
    "filled?",
    "yes",
    "node-values?",
    "yes",
    "field",
    "temperature",
    "surfaces-list",
    "symmetry-xyplane",
    "()",
    "coloring",
    "smooth",
    "quit",
)

solver.tui.display.objects.display("contour-temp")

views = solver.tui.display.views
views.restore_view("front")
views.auto_scale()
solver.tui.display.save_picture("contour-temp.png")

###############################################################################
# .. image:: /_static/mixing_elbow_015.png
#   :width: 500pt
#   :align: center

###############################################################################
# Create velocity vectors
# ~~~~~~~~~~~~~~~~~~~~~~~
# Create and display velocity vectors on the symmetry-xyplane plane. Then
# display it and export the image for inspection.
#
# - Set ``"vector"`` to ``"vector-vel"``.
# - Set ``"style"`` to ``"arrow"``.
# - Set ``"surface-list"`` to ``"symmetry-xyplane"``.
# - Set ``"scale"`` to ``"4"``.
# - Set ``"skip"`` to ``"2"``.

solver.tui.display.objects.create(
    "vector",
    "vector-vel",
    "style",
    "arrow",
    "surface-list",
    "symmetry-xyplane",
    "()",
    "scale",
    "scale-f",
    "4",
    "quit",
    "skip",
    "2",
    "quit",
)

solver.tui.display.objects.display("vector-vel")

views = solver.tui.display.views
views.restore_view("front")
views.auto_scale()
solver.tui.display.save_picture("vector-vel.png")

###############################################################################
# .. image:: /_static/mixing_elbow_tui_016.png
#   :width: 500pt
#   :align: center

###############################################################################
# Create iso-surface
# ~~~~~~~~~~~~~~~~~~
# Create an iso-surface representing the intersection of the plane z=0 and the
# surface outlet. Name it ``"z=0_outlet"``.

solver.tui.surface.iso_surface(
    "z-coordinate", "z=0_outlet", "outlet", "()", "()", "0", "()"
)

###############################################################################
# Display and save XY plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Display and save an XY plot of the temperature profile across the centerline
# of the outlet for the initial solution.

solver.tui.display.objects.create(
    "xy",
    "xy-outlet-temp",
    "y-axis-function",
    "temperature",
    "surfaces-list",
    "z=0_outlet",
    "()",
    "quit",
)

###############################################################################
# .. image:: /_static/mixing_elbow_017.png
#   :width: 500pt
#   :align: center

###############################################################################
# Write final case file and data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Write the final case file and the data.

solver.tui.file.write_case_data("mixing_elbow2_tui.cas.h5")

#########################################################################
# Close Fluent
# ~~~~~~~~~~~~
# Close Fluent.

solver.exit()

###############################################################################
