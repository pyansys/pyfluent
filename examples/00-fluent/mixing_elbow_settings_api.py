""".. _ref_mixing_elbow_settings_api_beta:

Fluent setup and solution using Settings objects
------------------------------------------------
This example sets up and solves a three-dimensional turbulent fluid flow
and heat transfer problem in a mixing elbow, which is common in piping
systems in power plants and process industries. Predicting the flow field
and temperature field in the area of the mixing region is important to
designing the junction properly.

This example uses the ``settings`` modules (beta).

**Problem description**

A cold fluid at 20 deg C flows into the pipe through a large inlet. It then mixes
with a warmer fluid at 40 deg C that enters through a smaller inlet located at
the elbow. The pipe dimensions are in inches, and the fluid properties and
boundary conditions are given in SI units. Because the Reynolds number for the
flow at the larger inlet is ``50, 800``, a turbulent flow model is required.
"""
# sphinx_gallery_thumbnail_path = '_static/mixing_elbow_settings.png'
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports, which includes downloading and importing
# the geometry file.

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

import_filename = examples.download_file("mixing_elbow.msh.h5", "pyfluent/mixing_elbow")

# Launch Fluent
# ~~~~~~~~~~~~~
# Launch Fluent as a service in meshing mode with double precision running on
# two processors.

session = pyfluent.launch_fluent(precision="double", processor_count=2)

###############################################################################
# Import mesh and perform mesh check
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import the mesh and perform a mesh check, which lists the minimum and maximum
# x, y, and z values from the mesh in the default SI units of meters. The mesh
# check also reports a number of other mesh features that are checked. Any errors
# in the mesh are reported. Ensure that the minimum volume is not negative because
# Fluent cannot begin a calculation when this is the case.

session.solver.root.file.read(file_type="case", file_name=import_filename)
session.solver.tui.mesh.check()

###############################################################################
# Set working units for mesh
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the working units for the mesh to inches.Because the default SI units are
# used for everything except length, you do not have to change any other units
# in this example. If you want working units for length to be other than inches
# (for example, millimeters), make the appropriate change.

session.solver.tui.define.units("length", "in")

###############################################################################
# Enable heat transfer
# ~~~~~~~~~~~~~~~~~~~~
# Enable heat transfer by activating the energy equation.

session.solver.root.setup.models.energy.enabled = True

###############################################################################
# Create a material
# ~~~~~~~~~~~~~~~~~
# Create a material named ``"water-liquid"``.

session.solver.root.setup.materials.copy_database_material_by_name(
    type="fluid", name="water-liquid"
)

###############################################################################
# Set up cell zone conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set up the cell zone conditions for the fluid zone (elbow-fluid). Set ``material``
# to ``"water-liquid"``.

session.solver.root.setup.cell_zone_conditions.fluid[
    "elbow-fluid"
].material = "water-liquid"

###############################################################################
# Set up boundary conditions for CFD analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set up the boundary conditions for the inlets, outlet, and walls for CFD
# analysis.

# cold inlet (cold-inlet), Setting: Value:
# Velocity Specification Method: Magnitude, Normal to Boundary
# Velocity Magnitude: 0.4 [m/s]
# Specification Method: Intensity and Hydraulic Diameter
# Turbulent Intensity: 5 [%]
# Hydraulic Diameter: 4 [inch]
# Temperature: 293.15 [K]

session.solver.root.setup.boundary_conditions.velocity_inlet["cold-inlet"].vmag = {
    "option": "constant or expression",
    "constant": 0.4,
}
session.solver.root.setup.boundary_conditions.velocity_inlet[
    "cold-inlet"
].ke_spec = "Intensity and Hydraulic Diameter"
session.solver.root.setup.boundary_conditions.velocity_inlet[
    "cold-inlet"
].turb_intensity = 5
session.solver.root.setup.boundary_conditions.velocity_inlet[
    "cold-inlet"
].turb_hydraulic_diam = "4 [in]"
session.solver.root.setup.boundary_conditions.velocity_inlet["cold-inlet"].t = {
    "option": "constant or expression",
    "constant": 293.15,
}

# hot inlet (hot-inlet), Setting: Value:
# Velocity Specification Method: Magnitude, Normal to Boundary
# Velocity Magnitude: 1.2 [m/s]
# Specification Method: Intensity and Hydraulic Diameter
# Turbulent Intensity: 5 [%]
# Hydraulic Diameter: 1 [inch]
# Temperature: 313.15 [K]

session.solver.root.setup.boundary_conditions.velocity_inlet["hot-inlet"].vmag = {
    "option": "constant or expression",
    "constant": 1.2,
}
session.solver.root.setup.boundary_conditions.velocity_inlet[
    "hot-inlet"
].ke_spec = "Intensity and Hydraulic Diameter"
session.solver.root.setup.boundary_conditions.velocity_inlet[
    "hot-inlet"
].turb_hydraulic_diam = "1 [in]"
session.solver.root.setup.boundary_conditions.velocity_inlet["hot-inlet"].t = {
    "option": "constant or expression",
    "constant": 313.15,
}

# pressure outlet (outlet), Setting: Value:
# Backflow Turbulent Intensity: 5 [%]
# Backflow Turbulent Viscosity Ratio: 4

session.solver.root.setup.boundary_conditions.pressure_outlet[
    "outlet"
].turb_viscosity_ratio = 4

###############################################################################
# Disable plotting of residuals during calculation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Disable plotting of residuals during the calculation.

session.solver.tui.solve.monitors.residual.plot("no")

###############################################################################
# Initialize flow field
# ~~~~~~~~~~~~~~~~~~~~~
# Initialize the flow field using the hybrid initialization.

session.solver.root.solution.initialization.hybrid_initialize()

###############################################################################
# Solve for 150 iterations
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Solve for 150 iterations.

session.solver.root.solution.run_calculation.iterate.get_attr("arguments")
session.solver.root.solution.run_calculation.iterate(number_of_iterations=150)

###############################################################################
# Create and display velocity vectors
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create and display velocity vectors on the symmetry-xyplane plane.

session.solver.root.results.graphics.vector["velocity_vector_symmetry"] = {}
session.solver.root.results.graphics.vector["velocity_vector_symmetry"].print_state()
session.solver.root.results.graphics.vector[
    "velocity_vector_symmetry"
].field = "temperature"
session.solver.root.results.graphics.vector[
    "velocity_vector_symmetry"
].surfaces_list = [
    "symmetry-xyplane",
]
session.solver.root.results.graphics.vector[
    "velocity_vector_symmetry"
].scale.scale_f = 4
session.solver.root.results.graphics.vector["velocity_vector_symmetry"].style = "arrow"

###############################################################################
# .. image:: /_static/mixing_elbow_016.png
#   :width: 500pt
#   :align: center

###############################################################################
# Compute mass flow rate
# ~~~~~~~~~~~~~~~~~~~~~~
# Compute the mass flow rate.

session.solver.root.solution.report_definitions.flux["mass_flow_rate"] = {}
session.solver.root.solution.report_definitions.flux[
    "mass_flow_rate"
].zone_names.get_attr("allowed-values")
session.solver.root.solution.report_definitions.flux["mass_flow_rate"].zone_names = [
    "cold-inlet",
    "hot-inlet",
    "outlet",
]
session.solver.root.solution.report_definitions.flux["mass_flow_rate"].print_state()
session.solver.root.solution.report_definitions.compute(report_defs=["mass_flow_rate"])

#########################################################################
# Close Fluent
# ~~~~~~~~~~~~
# Close Fluent.

session.exit()
