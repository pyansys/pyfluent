""".. _xxx:

Turbomachinery Setup and Analysis Using the Turbo Workflow
----------------------------------------------------------
This example sets up and solves a three-dimensional fluid flow through the
first three rows of a one and a half stage axial compressor, courtesy of
TFD Hannover. The compressor configuration is encountered in the aerospace
and turbomachinery industry. It is often important to predict the flow field
through the various components of a compressor in order to properly design
the turbomachine.

This example uses the guided workflow for turbomachinery setup and analysis
because it is appropriate for describing the type of turbo machine and its
configuration, importing the geometry, and defining turbo-related mappings
and physics conditions, before finally creating a turbo-specific topology
and reporting tools.

**Workflow tasks**

The Turbomachinery Setup and Analysis Using the Turbo Workflow guides you through these tasks:

- Describe and configure the turbomachinery
- Import the turbo-specific geometry
- Define the turbo-related mappings and physics conditions
- Create turbo-specific topology and reporting tools for postprocessing

**Problem description**

The first three rows of the 4.5 stage axial Hannover compressor (Courtesy of TFD Hannover) have an
inlet guide vane, rotor and stator. The inlet guide vane has 26 vanes, the rotor has 23 blades and
rotates at a velocity of 17,100 RPM and the stator has 30 passages. The total pressure at the inlet
is 60,000 Pa and a radial equilibrium distribution of static pressure at the outlet, with a static
pressure of 60500 Pa at the outlet along the hub.
"""

# sphinx_gallery_thumbnail_path = '_static/turbo_machinery.png'

###############################################################################
# Example Setup
# -------------
# Before you can use the turbo workflow, you must set up the
# example and initialize this workflow.
#
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports, which includes downloading and importing
# the geometry files.

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

inlet_guide_vane_file, rotor_file, stator_file = [
    examples.download_file(CAD_file, "pyfluent/turbo_workflow")
    for CAD_file in ["IGV.gtm", "R1.gtm", "S1.gtm"]
]

###############################################################################
# Launch Fluent
# ~~~~~~~~~~~~~
# Launch Fluent as a service in solver mode with double precision running on
# four processors.

solver_session = pyfluent.launch_fluent(
    precision="double", processor_count=4, mode="solver"
)

###############################################################################
# Initialize workflow
# ~~~~~~~~~~~~~~~~~~~
# Initialize the turbo workflow.

solver_session.tui.turbo_workflow.workflow.enable()

###############################################################################
# Edit turbo-related preferences
# ------------------------------
# The Turbo Workflow partially involves setting up an association between cell
# and face zones and their proper region assignments in the turbo topology.
# For turbo-related geometries with a large number of components, these mappings
# can be more easily automated and optimized using Preferences where you can
# instruct Fluent to look for certain string configurations and in a certain order.
#
# Updating inlet region
# ~~~~~~~~~~~~~~~~~~~~~
# Change the default value to: *inflow*, *in*

solver_session.tui.preferences.turbo_workflow.face_zone_settings.inlet_region(
    '"*inflow* *in*"'
)

###############################################################################
# Updating outlet region
# ~~~~~~~~~~~~~~~~~~~~~~
# Change the default value to: *outflow*, *out*

solver_session.tui.preferences.turbo_workflow.face_zone_settings.outlet_region(
    '"*outflow* *out*"'
)

###############################################################################
# Updating periodic 1 region
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change the default value to: "*per*1*, *per*"

solver_session.tui.preferences.turbo_workflow.face_zone_settings.periodic1_region(
    '"*per*1* *per*"'
)

###############################################################################
# Updating search order
# ~~~~~~~~~~~~~~~~~~~~~
# Change the default value to:
# *int*, *def*, *bld*, *blade*, *tip*2*, *tip*b*, *tip*out*, *tip*, *sym*,
# *per*1*, *per*2*, *per*b*, *high*per*, *per*, *hub*, *shr*, *cas*, *inflow*, *outflow*,
# *in*, *out*

solver_session.tui.preferences.turbo_workflow.face_zone_settings.fzsearch_order(
    '"*int* *def* *bld* *blade* *tip*2* *tip*b* *tip*out* *tip* *sym* *per*1* *per*2* *per*b* *high*per* *per* *hub* *shr* *cas* *inflow* *outflow* *in* *out*"'
)

###############################################################################
# Define workflow tasks
# ---------------------
#
# Describe component
# ~~~~~~~~~~~~~~~~~~
# Describe the turbomachinery component.

solver_session.solverworkflow.TWF_BasicMachineDescription(
    ComponentType="Axial Compressor",
    ComponentName="hannover",
    NumRows=3,
    OldRowNameList=["stator_1", "rotor_1", "stator_2"],
    NewRowNameList=["igv", "r1", "s1"],
    OldNumOfBladesList=["3", "3", "3"],
    NewNumOfBladesList=["26", "23", "30"],
)

###############################################################################
# Define blade row scope
# ~~~~~~~~~~~~~~~~~~~~~~
# Define the scope of the blade-row analysis.

solver_session.solverworkflow.TWF_BladeRowAnalysisScope()

###############################################################################
# Import Mesh
# ~~~~~~~~~~~
# Import mesh files.

solver_session.solverworkflow.TWF_ImportMesh(
    MeshFilePath=inlet_guide_vane_file,
    MeshFilePath_old="",
    MeshName="IGV.gtm",
)

solver_session.solverworkflow.TWF_ImportMesh(
    MeshFilePath=rotor_file,
    MeshFilePath_old="",
    MeshName="R1.gtm",
)

solver_session.solverworkflow.TWF_ImportMesh(
    MeshFilePath=stator_file,
    MeshFilePath_old="",
    MeshName="S1.gtm",
)

###############################################################################
# Association mesh
# ~~~~~~~~~~~~~~~~
# Associate the mesh.

solver_session.solverworkflow.TWF_AssociateMesh(
    UseWireframe=True,
    RenameCellZones="Yes, using row names",
    OldAMCellZonesList=[
        "igv-inlet,igv-passage-main",
        "r1-passage-main",
        "s1-passage-main",
    ],
    NewAMCellZonesList=["igv.1,igv.2", "r1", "s1"],
)

###############################################################################
# Define map regions
# ~~~~~~~~~~~~~~~~~~
# Define map regions.

solver_session.solverworkflow.TWF_MapRegionInfo(
    UseWireframe=True,
)

###############################################################################
# Create CFD model
# ~~~~~~~~~~~~~~~~
# Create the CFD model.

solver_session.solverworkflow.TWF_CreateCFDModel()

###############################################################################
# Define turbo physics
# ~~~~~~~~~~~~~~~~~~
# Define the turbo-related physics conditions.

solver_session.solverworkflow.TWF_TurboPhysics(
    states={
        "RotatingSpeed": 1790.708,
        "OperatingPressure": 0,
        "Energy": True,
        "WorkingFluid": {"AirIdealGas": True},
    }
)

###############################################################################
# Turbo regions and zones
# ~~~~~~~~~~~~~~~~~~~~~~~
# Define the turbo-related region and zone boundary conditions.

solver_session.solverworkflow.TWF_TurboRegionsZones(
    states={
        "InflowOutflowType": "Pressure Inlet, Pressure Outlet",
        "GuageTotalPressure": 60000,
        "TotalTemperature": 288.15,
        "FlowDirection": "Normal to Boundary",
        "Guagepressure": 60500,
        "RadialEquilibriumPressureDistribution": True,
    }
)

###############################################################################
# Define turbo-related topology
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define the turbo-related topology.

solver_session.solverworkflow.TWF_TurboTopology(
    TopologyName="turbo_topology_1", UseWireFrame=True
)

###############################################################################
# Describe turbo surfaces
# ~~~~~~~~~~~~~~~~~~~~~~~
# Define turbo-specific iso-surfaces.

solver_session.solverworkflow.TWF_TurboSurfaces(
    NumIsoSurfaces=3,
    OldIsoSurfaceNameList=["twf_span_1", "twf_span_2", "twf_span_3"],
    NewIsoSurfaceNameList=["twf_span_25", "twf_span_50", "twf_span_75"],
)

###############################################################################
# Create report definitions and monitors
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create report definitions and monitors.

solver_session.solverworkflow.TWF_ReportDefMonitors()

###############################################################################
# Complete workflow setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Complete workflow setup.

solver_session.solverworkflow.TWF_CompleteWorkflowSetup()

#########################################################################
# Close Fluent
# ~~~~~~~~~~~~
# Close Fluent.

solver_session.exit()

###############################################################################
