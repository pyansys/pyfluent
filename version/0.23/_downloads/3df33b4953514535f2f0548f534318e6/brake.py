"""
#################################
Automotive Brake Thermal Analysis
#################################

Objective:
==========

Braking surfaces get heated due to frictional heating during braking.
High temperature affects the braking performance and life of the braking system.
This example demonstrates:

* Fluent setup and simulation using PyFluent
* Post processing using PyVista (3D Viewer) and Matplotlib (2D graphs)

"""

####################################################################################
# Import required libraries/modules
# ==================================================================================

import csv
from pathlib import Path

import matplotlib.pyplot as plt

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
import ansys.fluent.visualization.pyvista as pv

###############################################################################
# Specifying save path
# ====================
# save_path can be specified as Path("E:/", "pyfluent-examples-tests") or
# Path("E:/pyfluent-examples-tests") in a Windows machine for example,  or
# Path("~/pyfluent-examples-tests") in Linux.
save_path = Path(pyfluent.EXAMPLES_PATH)

import_filename = examples.download_file(
    "brake.msh",
    "pyfluent/examples/Brake-Thermal-PyVista-Matplotlib",
    save_path=save_path,
)

####################################################################################
# Fluent Solution Setup
# ==================================================================================

####################################################################################
# Launch Fluent session with solver mode
# --------------------------------------

session = pyfluent.launch_fluent(precision="double", processor_count=2, version="3d")
session.health_check.status()

####################################################################################
# Import mesh
# ------------

session.settings.file.read_case(file_name=import_filename)

############################
# Define models and material
# --------------------------
session.settings.setup.models.energy = {"enabled": True}
session.settings.setup.general.solver.time = "unsteady-2nd-order-bounded"
session.tui.define.materials.copy("solid", "steel")

#########################################
# Solve only energy equation (conduction)
# ---------------------------------------
session.tui.solve.set.equations("flow", "no", "kw", "no")

##########################################################################################
# Define disc rotation
# --------------------
# (15.79 rps corresponds to 100 km/h car speed
# with 0.28 m of axis height from ground)
session.settings.setup.cell_zone_conditions.solid["disc2"] = {
    "solid_motion": {
        "solid_motion_zone_motion_function": "none",
        "solid_motion_axis_direction": [0, 1, 0],
        "solid_motion_axis_origin": [-0.035, -0.821, 0.045],
        "solid_motion_velocity": [0, 0, 0],
        "solid_omega": -15.79,
        "solid_relative_to_thread": "absolute",
        "enable": True,
    }
}
session.settings.setup.cell_zone_conditions.solid["disc1"] = {
    "solid_motion": {
        "solid_motion_zone_motion_function": "none",
        "solid_motion_axis_direction": [0, 1, 0],
        "solid_motion_axis_origin": [-0.035, -0.821, 0.045],
        "solid_motion_velocity": [0, 0, 0],
        "solid_omega": -15.79,
        "solid_relative_to_thread": "absolute",
        "enable": True,
    }
}

##########################################################################################
# Apply frictional heating on pad-disc surfaces
# ----------------------------------------------
# Wall thickness 0f 2 mm has been assumed and 2e9 w/m3 is the heat generation which
# has been calculated from kinetic energy change due to braking.

session.settings.setup.boundary_conditions.wall["wall-pad-disc2"] = {
    "thermal": {"q_dot": {"value": 2000000000}, "wall_thickness": {"value": 0.002}}
}
session.settings.setup.boundary_conditions.wall["wall_pad-disc1"] = {
    "thermal": {"q_dot": {"value": 2000000000}, "wall_thickness": {"value": 0.002}}
}

##########################################################################################
# Apply convection cooling on outer surfaces due to air flow
# -----------------------------------------------------------
# Outer surfaces are applied a constant htc of 100 W/(m2 K)
# and 300 K free stream temperature

session.tui.define.boundary_conditions.set.wall(
    "wall-disc*",
    "wall-geom*",
    "()",
    "thermal-bc",
    "yes",
    "convection",
    "convective-heat-transfer-coefficient",
    "no",
    100,
    "q",
)

##########################################################################################
# Initialize
# ----------
# Initialize with 300 K temperature

session.settings.solution.initialization.initialization_type = "standard"
session.settings.solution.initialization.standard_initialize()

###############################################################################################
# Post processing setup
# ---------------------
# * Report definitions and monitor plots
# * Set contour plot properties
# * Set views and camera
# * Set animation object

session.settings.solution.report_definitions.volume["max-pad-temperature"] = {}
session.settings.solution.report_definitions.volume[
    "max-pad-temperature"
].report_type = "volume-max"
session.settings.solution.report_definitions.volume["max-pad-temperature"] = {
    "field": "temperature",
    "cell_zones": ["geom-1-innerpad", "geom-1-outerpad"],
}

session.settings.solution.report_definitions.volume["max-disc-temperature"] = {}
session.settings.solution.report_definitions.volume[
    "max-disc-temperature"
].report_type = "volume-max"
session.settings.solution.report_definitions.volume["max-disc-temperature"] = {
    "field": "temperature",
    "cell_zones": ["disc1", "disc2"],
}

session.settings.solution.monitor.report_plots.create(name="max-temperature")
session.settings.solution.monitor.report_plots["max-temperature"] = {
    "report_defs": ["max-pad-temperature", "max-disc-temperature"]
}

report_file_path = Path(save_path) / "max-temperature.out"
session.settings.solution.monitor.report_files.create(name="max-temperature")
session.settings.solution.monitor.report_files["max-temperature"] = {
    "report_defs": ["max-pad-temperature", "max-disc-temperature"],
    "file_name": str(report_file_path),
}
session.settings.solution.monitor.report_files["max-temperature"].report_defs = [
    "max-pad-temperature",
    "max-disc-temperature",
    "flow-time",
]

session.settings.results.graphics.contour.create(name="contour-1")
session.settings.results.graphics.contour["contour-1"] = {
    "boundary_values": True,
    "range_option": {"auto_range_on": {"global_range": True}},
    "field": "temperature",
    "draw_mesh": False,
    "coloring": {"smooth": False},
    "color_map": {
        "user_skip": 9,
        "log_scale": False,
        "visible": True,
        "width": 6,
        "show_all": True,
        "font_name": "Helvetica",
        "font_size": 0.032,
        "font_automatic": True,
        "length": 0.54,
        "size": 100,
        "format": "%0.2e",
        "position": 1,
        "color": "field-velocity",
    },
    "mesh_object": "",
    "node_values": True,
    "contour_lines": False,
    "display_state_name": "None",
    "filled": True,
}

session.settings.results.graphics.contour["temperature"] = {}
session.settings.results.graphics.contour["temperature"] = {
    "field": "temperature",
    "surfaces_list": "wall*",
    "color_map": {
        "visible": True,
        "size": 100,
        "color": "field-velocity",
        "log_scale": False,
        "format": "%0.1f",
        "user_skip": 9,
        "show_all": True,
        "position": 1,
        "font_name": "Helvetica",
        "font_automatic": True,
        "font_size": 0.032,
        "length": 0.54,
        "width": 6,
        "bground_transparent": True,
        "bground_color": "#CCD3E2",
        "title_elements": "Variable and Object Name",
    },
    "range_option": {
        "option": "auto-range-off",
        "auto_range_off": {"maximum": 400.0, "minimum": 300, "clip_to_range": False},
    },
}

session.settings.results.graphics.views.restore_view(view_name="top")
session.settings.results.graphics.views.camera.zoom(factor=2)
session.settings.results.graphics.views.save_view(view_name="animation-view")

session.settings.solution.calculation_activity.solution_animations[
    "animate-temperature"
] = {}
session.settings.solution.calculation_activity.solution_animations[
    "animate-temperature"
] = {
    "animate_on": "temperature",
    "frequency_of": "flow-time",
    "flow_time_frequency": 0.05,
    "view": "animation-view",
}

##################################################################################################
# Run simulation
# ---------------
# * Run simulation for 2 seconds flow time
# * Set time step size
# * Set number of time steps and maximum number of iterations per time step

session.settings.solution.run_calculation.transient_controls.time_step_size = 0.01
session.settings.solution.run_calculation.dual_time_iterate(
    time_step_count=200, max_iter_per_step=5
)

##################################################################################################
# Save simulation data
# --------------------
# Write case and data files
save_case_data_as = Path(save_path) / "brake-final.cas.h5"
session.settings.file.write(file_type="case-data", file_name=str(save_case_data_as))

###############################################
# Post processing with PyVista (3D visualization)
# ===============================================

###############################################
# Create a graphics session
# -------------------------
graphics_session1 = pv.Graphics(session)

###############################################
# Temperature contour object
# --------------------------
contour1 = graphics_session1.Contours["temperature"]

###############################################
# Check available options for contour object
# -------------------------------------------

contour1()

###############################################
# Set contour properties
# ----------------------

contour1.field = "temperature"
contour1.surfaces_list = [
    "wall-disc1",
    "wall-disc2",
    "wall-pad-disc2",
    "wall_pad-disc1",
    "wall-geom-1-bp_inner",
    "wall-geom-1-bp_outer",
    "wall-geom-1-innerpad",
    "wall-geom-1-outerpad",
]
contour1.range.option = "auto-range-off"
contour1()
contour1.range.auto_range_off.minimum = 300
contour1.range.auto_range_off.maximum = 400

###############################################
# Display contour
# ---------------

contour1.display()

# %%
# .. image:: ../../_static/brake_surface_temperature.png
#    :align: center
#    :alt: Brake Surface Temperature Contour

# %%
#    Brake Surface Temperature

###############################################
# Post processing with Matplotlib (2D graph)
# ===============================================

###############################################
# Read monitor file
# -----------------

X = []
Y = []
Z = []
i = -1
with open(report_file_path, "r") as datafile:
    plotting = csv.reader(datafile, delimiter=" ")
    for rows in plotting:
        i = i + 1
        if i > 2:
            X.append(float(rows[3]))
            Y.append(float(rows[2]))
            Z.append(float(rows[1]))

###############################################
# Plot graph
# ----------


plt.title("Maximum Temperature", fontdict={"color": "darkred", "size": 20})
plt.plot(X, Z, label="Max. Pad Temperature", color="red")
plt.plot(X, Y, label="Max. Disc Temperature", color="blue")
plt.xlabel("Time (sec)")
plt.ylabel("Max Temperature (K)")
plt.legend(loc="lower right", shadow=True, fontsize="x-large")

###############################################
# Show graph
# ----------

plt.show()

# %%
# .. image:: ../../_static/brake_maximum_temperature.png
#    :align: center
#    :alt: Brake Maximum Temperature

# %%
#    Brake Maximum Temperature

####################################################################################
# Close the session
# ==================================================================================

session.exit()

# sphinx_gallery_thumbnail_path = '_static/brake_surface_temperature-thumbnail.png'
