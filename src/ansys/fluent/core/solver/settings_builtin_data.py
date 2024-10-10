"""Data for for builtin setting classes."""

from ansys.fluent.core import FluentVersion

# {<class name>: (<kind>, <path>)}
DATA = {
    "Setup": ("Singleton", "setup"),
    "General": ("Singleton", "setup.general"),
    "Models": ("Singleton", "setup.models"),
    "Multiphase": ("Singleton", "setup.models.multiphase"),
    "Energy": ("Singleton", "setup.models.energy"),
    "Viscous": ("Singleton", "setup.models.viscous"),
    "Radiation": (
        "Singleton",
        {
            FluentVersion.v251: "setup.models.radiation",
            FluentVersion.v242: "setup.models.radiation",
            FluentVersion.v241: "setup.models.radiation",
            FluentVersion.v232: "setup.models.radiation",
        },
    ),
    "Species": (
        "Singleton",
        {
            FluentVersion.v251: "setup.models.species",
            FluentVersion.v242: "setup.models.species",
            FluentVersion.v241: "setup.models.species",
            FluentVersion.v232: "setup.models.species",
        },
    ),
    "DiscretePhase": (
        "Singleton",
        {
            FluentVersion.v251: "setup.models.discrete_phase",
            FluentVersion.v242: "setup.models.discrete_phase",
            FluentVersion.v241: "setup.models.discrete_phase",
            FluentVersion.v232: "setup.models.discrete_phase",
            FluentVersion.v231: "setup.models.discrete_phase",
        },
    ),
    "Injections": (
        "Singleton",
        {
            FluentVersion.v251: "setup.models.discrete_phase.injections",
            FluentVersion.v242: "setup.models.discrete_phase.injections",
            FluentVersion.v241: "setup.models.discrete_phase.injections",
            FluentVersion.v232: "setup.models.discrete_phase.injections",
            FluentVersion.v231: "setup.models.discrete_phase.injections",
        },
    ),
    "Injection": (
        "NamedObject",
        {
            FluentVersion.v251: "setup.models.discrete_phase.injections",
            FluentVersion.v242: "setup.models.discrete_phase.injections",
            FluentVersion.v241: "setup.models.discrete_phase.injections",
            FluentVersion.v232: "setup.models.discrete_phase.injections",
            FluentVersion.v231: "setup.models.discrete_phase.injections",
        },
    ),
    "VirtualBladeModel": (
        "Singleton",
        {
            FluentVersion.v251: "setup.models.virtual_blade_model",
            FluentVersion.v242: "setup.models.virtual_blade_model",
            FluentVersion.v241: "setup.models.virtual_blade_model",
            FluentVersion.v232: "setup.models.virtual_blade_model",
            FluentVersion.v231: "setup.models.virtual_blade_model",
        },
    ),
    "Optics": (
        "Singleton",
        {
            FluentVersion.v251: "setup.models.optics",
            FluentVersion.v242: "setup.models.optics",
            FluentVersion.v241: "setup.models.optics",
            FluentVersion.v232: "setup.models.optics",
            FluentVersion.v231: "setup.models.optics",
        },
    ),
    "Structure": (
        "Singleton",
        {
            FluentVersion.v251: "setup.models.structure",
            FluentVersion.v242: "setup.models.structure",
            FluentVersion.v241: "setup.models.structure",
            FluentVersion.v232: "setup.models.structure",
        },
    ),
    "Ablation": (
        "Singleton",
        {
            FluentVersion.v251: "setup.models.ablation",
            FluentVersion.v242: "setup.models.ablation",
            FluentVersion.v241: "setup.models.ablation",
            FluentVersion.v232: "setup.models.ablation",
        },
    ),
    "EChemistry": (
        "Singleton",
        {
            FluentVersion.v251: "setup.models.echemistry",
            FluentVersion.v242: "setup.models.echemistry",
            FluentVersion.v241: "setup.models.echemistry",
        },
    ),
    "Battery": (
        "Singleton",
        {
            FluentVersion.v251: "setup.models.battery",
            FluentVersion.v242: "setup.models.battery",
            FluentVersion.v241: "setup.models.battery",
        },
    ),
    "SystemCoupling": (
        "Singleton",
        {
            FluentVersion.v251: "setup.models.system_coupling",
            FluentVersion.v242: "setup.models.system_coupling",
            FluentVersion.v241: "setup.models.system_coupling",
        },
    ),
    "Sofc": (
        "Singleton",
        {
            FluentVersion.v251: "setup.models.sofc",
            FluentVersion.v242: "setup.models.sofc",
            FluentVersion.v241: "setup.models.sofc",
        },
    ),
    "Pemfc": (
        "Singleton",
        {
            FluentVersion.v251: "setup.models.pemfc",
            FluentVersion.v242: "setup.models.pemfc",
        },
    ),
    "Materials": ("Singleton", "setup.materials"),
    "FluidMaterials": ("Singleton", "setup.materials.fluid"),
    "FluidMaterial": ("NamedObject", "setup.materials.fluid"),
    "SolidMaterials": ("Singleton", "setup.materials.solid"),
    "SolidMaterial": ("NamedObject", "setup.materials.solid"),
    "MixtureMaterials": ("Singleton", "setup.materials.mixture"),
    "MixtureMaterial": ("NamedObject", "setup.materials.mixture"),
    "ParticleMixtureMaterials": ("Singleton", "setup.materials.particle_mixture"),
    "ParticleMixtureMaterial": ("NamedObject", "setup.materials.particle_mixture"),
    "CellZoneConditions": ("Singleton", "setup.cell_zone_conditions"),
    "CellZoneCondition": (
        "NamedObject",
        {
            FluentVersion.v251: "setup.cell_zone_conditions",
            FluentVersion.v242: "setup.cell_zone_conditions",
            FluentVersion.v241: "setup.cell_zone_conditions",
            FluentVersion.v232: "setup.cell_zone_conditions",
            FluentVersion.v231: "setup.cell_zone_conditions",
        },
    ),
    "FluidCellZones": ("Singleton", "setup.cell_zone_conditions.fluid"),
    "FluidCellZone": ("NamedObject", "setup.cell_zone_conditions.fluid"),
    "SolidCellZones": ("Singleton", "setup.cell_zone_conditions.solid"),
    "SolidCellZone": ("NamedObject", "setup.cell_zone_conditions.solid"),
    "BoundaryConditions": ("Singleton", "setup.boundary_conditions"),
    "BoundaryCondition": (
        "NamedObject",
        {
            FluentVersion.v251: "setup.boundary_conditions",
            FluentVersion.v242: "setup.boundary_conditions",
            FluentVersion.v241: "setup.boundary_conditions",
            FluentVersion.v232: "setup.boundary_conditions",
            FluentVersion.v231: "setup.boundary_conditions",
        },
    ),
    "AxisBoundaries": ("Singleton", "setup.boundary_conditions.axis"),
    "AxisBoundary": ("NamedObject", "setup.boundary_conditions.axis"),
    "DegassingBoundaries": ("Singleton", "setup.boundary_conditions.degassing"),
    "DegassingBoundary": ("NamedObject", "setup.boundary_conditions.degassing"),
    "ExhaustFanBoundaries": ("Singleton", "setup.boundary_conditions.exhaust_fan"),
    "ExhaustFanBoundary": ("NamedObject", "setup.boundary_conditions.exhaust_fan"),
    "FanBoundaries": ("Singleton", "setup.boundary_conditions.fan"),
    "FanBoundary": ("NamedObject", "setup.boundary_conditions.fan"),
    "GeometryBoundaries": ("Singleton", "setup.boundary_conditions.geometry"),
    "GeometryBoundary": ("NamedObject", "setup.boundary_conditions.geometry"),
    "InletVentBoundaries": ("Singleton", "setup.boundary_conditions.inlet_vent"),
    "InletVentBoundary": ("NamedObject", "setup.boundary_conditions.inlet_vent"),
    "IntakeFanBoundaries": ("Singleton", "setup.boundary_conditions.intake_fan"),
    "IntakeFanBoundary": ("NamedObject", "setup.boundary_conditions.intake_fan"),
    "InterfaceBoundaries": ("Singleton", "setup.boundary_conditions.interface"),
    "InterfaceBoundary": ("NamedObject", "setup.boundary_conditions.interface"),
    "InteriorBoundaries": ("Singleton", "setup.boundary_conditions.interior"),
    "InteriorBoundary": ("NamedObject", "setup.boundary_conditions.interior"),
    "MassFlowInlets": ("Singleton", "setup.boundary_conditions.mass_flow_inlet"),
    "MassFlowInlet": ("NamedObject", "setup.boundary_conditions.mass_flow_inlet"),
    "MassFlowOutlets": ("Singleton", "setup.boundary_conditions.mass_flow_outlet"),
    "MassFlowOutlet": ("NamedObject", "setup.boundary_conditions.mass_flow_outlet"),
    "NetworkBoundaries": ("Singleton", "setup.boundary_conditions.network"),
    "NetworkBoundary": ("NamedObject", "setup.boundary_conditions.network"),
    "NetworkEndBoundaries": ("Singleton", "setup.boundary_conditions.network_end"),
    "NetworkEndBoundary": ("NamedObject", "setup.boundary_conditions.network_end"),
    "OutflowBoundaries": ("Singleton", "setup.boundary_conditions.outflow"),
    "OutflowBoundary": ("NamedObject", "setup.boundary_conditions.outflow"),
    "OutletVentBoundaries": ("Singleton", "setup.boundary_conditions.outlet_vent"),
    "OutletVentBoundary": ("NamedObject", "setup.boundary_conditions.outlet_vent"),
    "OversetBoundaries": ("Singleton", "setup.boundary_conditions.overset"),
    "OversetBoundary": ("NamedObject", "setup.boundary_conditions.overset"),
    "PeriodicBoundaries": ("Singleton", "setup.boundary_conditions.periodic"),
    "PeriodicBoundary": ("NamedObject", "setup.boundary_conditions.periodic"),
    "PorousJumpBoundaries": ("Singleton", "setup.boundary_conditions.porous_jump"),
    "PorousJumpBoundary": ("NamedObject", "setup.boundary_conditions.porous_jump"),
    "PressureFarFieldBoundaries": (
        "Singleton",
        "setup.boundary_conditions.pressure_far_field",
    ),
    "PressureFarFieldBoundary": (
        "NamedObject",
        "setup.boundary_conditions.pressure_far_field",
    ),
    "PressureInlets": ("Singleton", "setup.boundary_conditions.pressure_inlet"),
    "PressureInlet": ("NamedObject", "setup.boundary_conditions.pressure_inlet"),
    "PressureOutlets": ("Singleton", "setup.boundary_conditions.pressure_outlet"),
    "PressureOutlet": ("NamedObject", "setup.boundary_conditions.pressure_outlet"),
    "RadiatorBoundaries": ("Singleton", "setup.boundary_conditions.radiator"),
    "RadiatorBoundary": ("NamedObject", "setup.boundary_conditions.radiator"),
    "RansLesInterfaceBoundaries": (
        "Singleton",
        "setup.boundary_conditions.rans_les_interface",
    ),
    "RansLesInterfaceBoundary": (
        "NamedObject",
        "setup.boundary_conditions.rans_les_interface",
    ),
    "RecirculationInlets": (
        "Singleton",
        "setup.boundary_conditions.recirculation_inlet",
    ),
    "RecirculationInlet": (
        "NamedObject",
        "setup.boundary_conditions.recirculation_inlet",
    ),
    "RecirculationOutlets": (
        "Singleton",
        "setup.boundary_conditions.recirculation_outlet",
    ),
    "RecirculationOutlet": (
        "NamedObject",
        "setup.boundary_conditions.recirculation_outlet",
    ),
    "ShadowBoundaries": ("Singleton", "setup.boundary_conditions.shadow"),
    "ShadowBoundary": ("NamedObject", "setup.boundary_conditions.shadow"),
    "SymmetryBoundaries": ("Singleton", "setup.boundary_conditions.symmetry"),
    "SymmetryBoundary": ("NamedObject", "setup.boundary_conditions.symmetry"),
    "VelocityInlets": ("Singleton", "setup.boundary_conditions.velocity_inlet"),
    "VelocityInlet": ("NamedObject", "setup.boundary_conditions.velocity_inlet"),
    "WallBoundaries": ("Singleton", "setup.boundary_conditions.wall"),
    "WallBoundary": ("NamedObject", "setup.boundary_conditions.wall"),
    "NonReflectingBoundaries": (
        "Singleton",
        {
            FluentVersion.v251: "setup.boundary_conditions.non_reflecting_bc",
            FluentVersion.v242: "setup.boundary_conditions.non_reflecting_bc",
            FluentVersion.v241: "setup.boundary_conditions.non_reflecting_bc",
        },
    ),
    "NonReflectingBoundary": (
        "NamedObject",
        {
            FluentVersion.v251: "setup.boundary_conditions.non_reflecting_bc",
            FluentVersion.v242: "setup.boundary_conditions.non_reflecting_bc",
            FluentVersion.v241: "setup.boundary_conditions.non_reflecting_bc",
        },
    ),
    "PerforatedWallBoundaries": (
        "Singleton",
        {
            FluentVersion.v251: "setup.boundary_conditions.perforated_wall",
            FluentVersion.v242: "setup.boundary_conditions.perforated_wall",
            FluentVersion.v241: "setup.boundary_conditions.perforated_wall",
        },
    ),
    "PerforatedWallBoundary": (
        "NamedObject",
        {
            FluentVersion.v251: "setup.boundary_conditions.perforated_wall",
            FluentVersion.v242: "setup.boundary_conditions.perforated_wall",
            FluentVersion.v241: "setup.boundary_conditions.perforated_wall",
        },
    ),
    "MeshInterfaces": (
        "Singleton",
        {
            FluentVersion.v251: "setup.mesh_interfaces",
            FluentVersion.v242: "setup.mesh_interfaces",
            FluentVersion.v241: "setup.mesh_interfaces",
            FluentVersion.v232: "setup.mesh_interfaces",
        },
    ),
    "DynamicMesh": ("Singleton", {FluentVersion.v251: "setup.dynamic_mesh"}),
    "ReferenceValues": ("Singleton", "setup.reference_values"),
    "ReferenceFrames": (
        "Singleton",
        {
            FluentVersion.v251: "setup.reference_frames",
            FluentVersion.v242: "setup.reference_frames",
            FluentVersion.v241: "setup.reference_frames",
            FluentVersion.v232: "setup.reference_frames",
        },
    ),
    "ReferenceFrame": (
        "NamedObject",
        {
            FluentVersion.v251: "setup.reference_frames",
            FluentVersion.v242: "setup.reference_frames",
            FluentVersion.v241: "setup.reference_frames",
            FluentVersion.v232: "setup.reference_frames",
        },
    ),
    "NamedExpressions": (
        "Singleton",
        {
            FluentVersion.v251: "setup.named_expressions",
            FluentVersion.v242: "setup.named_expressions",
            FluentVersion.v241: "setup.named_expressions",
            FluentVersion.v232: "setup.named_expressions",
        },
    ),
    "NamedExpression": (
        "NamedObject",
        {
            FluentVersion.v251: "setup.named_expressions",
            FluentVersion.v242: "setup.named_expressions",
            FluentVersion.v241: "setup.named_expressions",
            FluentVersion.v232: "setup.named_expressions",
        },
    ),
    "Solution": ("Singleton", "solution"),
    "Methods": ("Singleton", "solution.methods"),
    "Controls": ("Singleton", "solution.controls"),
    "ReportDefinitions": ("Singleton", "solution.report_definitions"),
    "Monitor": (
        "Singleton",
        {
            FluentVersion.v251: "solution.monitor",
            FluentVersion.v242: "solution.monitor",
            FluentVersion.v241: "solution.monitor",
            FluentVersion.v232: "solution.monitor",
            FluentVersion.v231: "solution.monitor",
        },
    ),
    "Residual": (
        "Singleton",
        {
            FluentVersion.v251: "solution.monitor.residual",
            FluentVersion.v242: "solution.monitor.residual",
            FluentVersion.v241: "solution.monitor.residual",
        },
    ),
    "ReportFiles": (
        "Singleton",
        {
            FluentVersion.v251: "solution.monitor.report_files",
            FluentVersion.v242: "solution.monitor.report_files",
            FluentVersion.v241: "solution.monitor.report_files",
            FluentVersion.v232: "solution.monitor.report_files",
            FluentVersion.v231: "solution.monitor.report_files",
        },
    ),
    "ReportFile": (
        "NamedObject",
        {
            FluentVersion.v251: "solution.monitor.report_files",
            FluentVersion.v242: "solution.monitor.report_files",
            FluentVersion.v241: "solution.monitor.report_files",
            FluentVersion.v232: "solution.monitor.report_files",
            FluentVersion.v231: "solution.monitor.report_files",
        },
    ),
    "ReportPlots": (
        "Singleton",
        {
            FluentVersion.v251: "solution.monitor.report_plots",
            FluentVersion.v242: "solution.monitor.report_plots",
            FluentVersion.v241: "solution.monitor.report_plots",
            FluentVersion.v232: "solution.monitor.report_plots",
            FluentVersion.v231: "solution.monitor.report_plots",
        },
    ),
    "ReportPlot": (
        "NamedObject",
        {
            FluentVersion.v251: "solution.monitor.report_plots",
            FluentVersion.v242: "solution.monitor.report_plots",
            FluentVersion.v241: "solution.monitor.report_plots",
            FluentVersion.v232: "solution.monitor.report_plots",
            FluentVersion.v231: "solution.monitor.report_plots",
        },
    ),
    "ConvergenceConditions": (
        "Singleton",
        {
            FluentVersion.v251: "solution.monitor.convergence_conditions",
            FluentVersion.v242: "solution.monitor.convergence_conditions",
            FluentVersion.v241: "solution.monitor.convergence_conditions",
            FluentVersion.v232: "solution.monitor.convergence_conditions",
            FluentVersion.v231: "solution.monitor.convergence_conditions",
        },
    ),
    "CellRegisters": (
        "Singleton",
        {
            FluentVersion.v251: "solution.cell_registers",
            FluentVersion.v242: "solution.cell_registers",
            FluentVersion.v241: "solution.cell_registers",
            FluentVersion.v232: "solution.cell_registers",
            FluentVersion.v231: "solution.cell_registers",
        },
    ),
    "CellRegister": (
        "NamedObject",
        {
            FluentVersion.v251: "solution.cell_registers",
            FluentVersion.v242: "solution.cell_registers",
            FluentVersion.v241: "solution.cell_registers",
            FluentVersion.v232: "solution.cell_registers",
            FluentVersion.v231: "solution.cell_registers",
        },
    ),
    "Initialization": ("Singleton", "solution.initialization"),
    "CalculationActivity": (
        "Singleton",
        {
            FluentVersion.v251: "solution.calculation_activity",
            FluentVersion.v242: "solution.calculation_activity",
            FluentVersion.v241: "solution.calculation_activity",
            FluentVersion.v232: "solution.calculation_activity",
            FluentVersion.v231: "solution.calculation_activity",
        },
    ),
    "ExecuteCommands": (
        "Singleton",
        {
            FluentVersion.v251: "solution.calculation_activity.execute_commands",
            FluentVersion.v242: "solution.calculation_activity.execute_commands",
            FluentVersion.v241: "solution.calculation_activity.execute_commands",
            FluentVersion.v232: "solution.calculation_activity.execute_commands",
            FluentVersion.v231: "solution.calculation_activity.execute_commands",
        },
    ),
    "CaseModification": (
        "Singleton",
        {
            FluentVersion.v251: "solution.calculation_activity.case_modification",
            FluentVersion.v242: "solution.calculation_activity.case_modification",
            FluentVersion.v241: "solution.calculation_activity.case_modification",
        },
    ),
    "RunCalculation": ("Singleton", "solution.run_calculation"),
    "Results": ("Singleton", "results"),
    "Surfaces": ("Singleton", "results.surfaces"),
    "PointSurfaces": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.point_surface",
            FluentVersion.v242: "results.surfaces.point_surface",
            FluentVersion.v241: "results.surfaces.point_surface",
            FluentVersion.v232: "results.surfaces.point_surface",
        },
    ),
    "PointSurface": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.point_surface",
            FluentVersion.v242: "results.surfaces.point_surface",
            FluentVersion.v241: "results.surfaces.point_surface",
            FluentVersion.v232: "results.surfaces.point_surface",
        },
    ),
    "LineSurfaces": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.line_surface",
            FluentVersion.v242: "results.surfaces.line_surface",
            FluentVersion.v241: "results.surfaces.line_surface",
            FluentVersion.v232: "results.surfaces.line_surface",
        },
    ),
    "LineSurface": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.line_surface",
            FluentVersion.v242: "results.surfaces.line_surface",
            FluentVersion.v241: "results.surfaces.line_surface",
            FluentVersion.v232: "results.surfaces.line_surface",
        },
    ),
    "RakeSurfaces": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.rake_surface",
            FluentVersion.v242: "results.surfaces.rake_surface",
            FluentVersion.v241: "results.surfaces.rake_surface",
            FluentVersion.v232: "results.surfaces.rake_surface",
        },
    ),
    "RakeSurface": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.rake_surface",
            FluentVersion.v242: "results.surfaces.rake_surface",
            FluentVersion.v241: "results.surfaces.rake_surface",
            FluentVersion.v232: "results.surfaces.rake_surface",
        },
    ),
    "PlaneSurfaces": ("Singleton", "results.surfaces.plane_surface"),
    "PlaneSurface": ("NamedObject", "results.surfaces.plane_surface"),
    "IsoSurfaces": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.iso_surface",
            FluentVersion.v242: "results.surfaces.iso_surface",
            FluentVersion.v241: "results.surfaces.iso_surface",
            FluentVersion.v232: "results.surfaces.iso_surface",
        },
    ),
    "IsoSurface": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.iso_surface",
            FluentVersion.v242: "results.surfaces.iso_surface",
            FluentVersion.v241: "results.surfaces.iso_surface",
            FluentVersion.v232: "results.surfaces.iso_surface",
        },
    ),
    "IsoClips": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.iso_clip",
            FluentVersion.v242: "results.surfaces.iso_clip",
            FluentVersion.v241: "results.surfaces.iso_clip",
        },
    ),
    "IsoClip": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.iso_clip",
            FluentVersion.v242: "results.surfaces.iso_clip",
            FluentVersion.v241: "results.surfaces.iso_clip",
        },
    ),
    "ZoneSurfaces": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.zone_surface",
            FluentVersion.v242: "results.surfaces.zone_surface",
            FluentVersion.v241: "results.surfaces.zone_surface",
        },
    ),
    "ZoneSurface": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.zone_surface",
            FluentVersion.v242: "results.surfaces.zone_surface",
            FluentVersion.v241: "results.surfaces.zone_surface",
        },
    ),
    "PartitionSurfaces": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.partition_surface",
            FluentVersion.v242: "results.surfaces.partition_surface",
            FluentVersion.v241: "results.surfaces.partition_surface",
        },
    ),
    "PartitionSurface": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.partition_surface",
            FluentVersion.v242: "results.surfaces.partition_surface",
            FluentVersion.v241: "results.surfaces.partition_surface",
        },
    ),
    "TransformSurfaces": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.transform_surface",
            FluentVersion.v242: "results.surfaces.transform_surface",
            FluentVersion.v241: "results.surfaces.transform_surface",
        },
    ),
    "TransformSurface": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.transform_surface",
            FluentVersion.v242: "results.surfaces.transform_surface",
            FluentVersion.v241: "results.surfaces.transform_surface",
        },
    ),
    "ImprintSurfaces": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.imprint_surface",
            FluentVersion.v242: "results.surfaces.imprint_surface",
            FluentVersion.v241: "results.surfaces.imprint_surface",
        },
    ),
    "ImprintSurface": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.imprint_surface",
            FluentVersion.v242: "results.surfaces.imprint_surface",
            FluentVersion.v241: "results.surfaces.imprint_surface",
        },
    ),
    "PlaneSlices": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.plane_slice",
            FluentVersion.v242: "results.surfaces.plane_slice",
            FluentVersion.v241: "results.surfaces.plane_slice",
        },
    ),
    "PlaneSlice": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.plane_slice",
            FluentVersion.v242: "results.surfaces.plane_slice",
            FluentVersion.v241: "results.surfaces.plane_slice",
        },
    ),
    "SphereSlices": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.sphere_slice",
            FluentVersion.v242: "results.surfaces.sphere_slice",
            FluentVersion.v241: "results.surfaces.sphere_slice",
        },
    ),
    "SphereSlice": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.sphere_slice",
            FluentVersion.v242: "results.surfaces.sphere_slice",
            FluentVersion.v241: "results.surfaces.sphere_slice",
        },
    ),
    "QuadricSurfaces": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.quadric_surface",
            FluentVersion.v242: "results.surfaces.quadric_surface",
            FluentVersion.v241: "results.surfaces.quadric_surface",
        },
    ),
    "QuadricSurface": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.quadric_surface",
            FluentVersion.v242: "results.surfaces.quadric_surface",
            FluentVersion.v241: "results.surfaces.quadric_surface",
        },
    ),
    "SurfaceCells": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.surface_cells",
            FluentVersion.v242: "results.surfaces.surface_cells",
            FluentVersion.v241: "results.surfaces.surface_cells",
        },
    ),
    "SurfaceCell": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.surface_cells",
            FluentVersion.v242: "results.surfaces.surface_cells",
            FluentVersion.v241: "results.surfaces.surface_cells",
        },
    ),
    "ExpressionVolumes": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.expression_volume",
        },
    ),
    "ExpressionVolume": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.expression_volume",
        },
    ),
    "GroupSurfaces": (
        "Singleton",
        {
            FluentVersion.v251: "results.surfaces.group_surface",
        },
    ),
    "GroupSurface": (
        "NamedObject",
        {
            FluentVersion.v251: "results.surfaces.group_surface",
        },
    ),
    "Graphics": ("Singleton", "results.graphics"),
    "Meshes": ("Singleton", "results.graphics.mesh"),
    "Mesh": ("NamedObject", "results.graphics.mesh"),
    "Contours": ("Singleton", "results.graphics.contour"),
    "Contour": ("NamedObject", "results.graphics.contour"),
    "Vectors": ("Singleton", "results.graphics.vector"),
    "Vector": ("NamedObject", "results.graphics.vector"),
    "Pathlines": (
        "Singleton",
        {
            FluentVersion.v251: "results.graphics.pathline",
            FluentVersion.v242: "results.graphics.pathline",
            FluentVersion.v241: "results.graphics.pathline",
            FluentVersion.v232: "results.graphics.pathline",
            FluentVersion.v231: "results.graphics.pathline",
        },
    ),
    "Pathline": (
        "NamedObject",
        {
            FluentVersion.v251: "results.graphics.pathline",
            FluentVersion.v242: "results.graphics.pathline",
            FluentVersion.v241: "results.graphics.pathline",
            FluentVersion.v232: "results.graphics.pathline",
            FluentVersion.v231: "results.graphics.pathline",
        },
    ),
    "ParticleTracks": (
        "Singleton",
        {
            FluentVersion.v251: "results.graphics.particle_track",
            FluentVersion.v242: "results.graphics.particle_track",
            FluentVersion.v241: "results.graphics.particle_track",
            FluentVersion.v232: "results.graphics.particle_track",
            FluentVersion.v231: "results.graphics.particle_track",
        },
    ),
    "ParticleTrack": (
        "NamedObject",
        {
            FluentVersion.v251: "results.graphics.particle_track",
            FluentVersion.v242: "results.graphics.particle_track",
            FluentVersion.v241: "results.graphics.particle_track",
            FluentVersion.v232: "results.graphics.particle_track",
            FluentVersion.v231: "results.graphics.particle_track",
        },
    ),
    "LICs": ("Singleton", "results.graphics.lic"),
    "LIC": ("NamedObject", "results.graphics.lic"),
    "Plots": (
        "Singleton",
        {
            FluentVersion.v251: "results.plot",
            FluentVersion.v242: "results.plot",
            FluentVersion.v241: "results.plot",
            FluentVersion.v232: "results.plot",
            FluentVersion.v231: "results.plot",
        },
    ),
    "XYPlots": (
        "Singleton",
        {
            FluentVersion.v251: "results.plot.xy_plot",
            FluentVersion.v242: "results.plot.xy_plot",
            FluentVersion.v241: "results.plot.xy_plot",
            FluentVersion.v232: "results.plot.xy_plot",
            FluentVersion.v231: "results.plot.xy_plot",
        },
    ),
    "XYPlot": (
        "NamedObject",
        {
            FluentVersion.v251: "results.plot.xy_plot",
            FluentVersion.v242: "results.plot.xy_plot",
            FluentVersion.v241: "results.plot.xy_plot",
            FluentVersion.v232: "results.plot.xy_plot",
            FluentVersion.v231: "results.plot.xy_plot",
        },
    ),
    "Histogram": (
        "Singleton",
        {
            FluentVersion.v251: "results.plot.histogram",
            FluentVersion.v242: "results.plot.histogram",
            FluentVersion.v241: "results.plot.histogram",
        },
    ),
    "CumulativePlots": (
        "Singleton",
        {
            FluentVersion.v251: "results.plot.cumulative_plot",
            FluentVersion.v242: "results.plot.cumulative_plot",
            FluentVersion.v241: "results.plot.cumulative_plot",
        },
    ),
    "CumulativePlot": (
        "NamedObject",
        {
            FluentVersion.v251: "results.plot.cumulative_plot",
            FluentVersion.v242: "results.plot.cumulative_plot",
            FluentVersion.v241: "results.plot.cumulative_plot",
        },
    ),
    "ProfileData": (
        "Singleton",
        {
            FluentVersion.v251: "results.plot.profile_data",
            FluentVersion.v242: "results.plot.profile_data",
        },
    ),
    "InterpolatedData": (
        "Singleton",
        {
            FluentVersion.v251: "results.plot.interpolated_data",
            FluentVersion.v242: "results.plot.interpolated_data",
        },
    ),
    "Scenes": (
        "Singleton",
        {
            FluentVersion.v251: "results.scene",
            FluentVersion.v242: "results.scene",
            FluentVersion.v241: "results.scene",
            FluentVersion.v232: "results.scene",
            FluentVersion.v231: "results.scene",
        },
    ),
    "Scene": (
        "NamedObject",
        {
            FluentVersion.v251: "results.scene",
            FluentVersion.v242: "results.scene",
            FluentVersion.v241: "results.scene",
            FluentVersion.v232: "results.scene",
            FluentVersion.v231: "results.scene",
        },
    ),
    "SceneAnimation": (
        "Singleton",
        {
            FluentVersion.v251: "results.animations.scene_animation",
            FluentVersion.v242: "results.animations.scene_animation",
            FluentVersion.v241: "results.animations.scene_animation",
        },
    ),
    "Report": (
        "Singleton",
        {
            FluentVersion.v251: "results.report",
            FluentVersion.v242: "results.report",
            FluentVersion.v241: "results.report",
            FluentVersion.v232: "results.report",
            FluentVersion.v231: "results.report",
        },
    ),
    "DiscretePhaseHistogram": (
        "Singleton",
        {
            FluentVersion.v251: "results.report.discrete_phase.histogram",
            FluentVersion.v242: "results.report.discrete_phase.histogram",
            FluentVersion.v241: "results.report.discrete_phase.histogram",
            FluentVersion.v232: "results.report.discrete_phase.histogram",
            FluentVersion.v231: "results.report.discrete_phase.histogram",
        },
    ),
    "Fluxes": (
        "Singleton",
        {
            FluentVersion.v251: "results.report.fluxes",
            FluentVersion.v242: "results.report.fluxes",
            FluentVersion.v241: "results.report.fluxes",
            FluentVersion.v232: "results.report.fluxes",
            FluentVersion.v231: "results.report.fluxes",
        },
    ),
    "SurfaceIntegrals": (
        "Singleton",
        {
            FluentVersion.v251: "results.report.surface_integrals",
            FluentVersion.v242: "results.report.surface_integrals",
            FluentVersion.v241: "results.report.surface_integrals",
            FluentVersion.v232: "results.report.surface_integrals",
            FluentVersion.v231: "results.report.surface_integrals",
        },
    ),
    "VolumeIntegrals": (
        "Singleton",
        {
            FluentVersion.v251: "results.report.volume_integrals",
            FluentVersion.v242: "results.report.volume_integrals",
            FluentVersion.v241: "results.report.volume_integrals",
            FluentVersion.v232: "results.report.volume_integrals",
            FluentVersion.v231: "results.report.volume_integrals",
        },
    ),
    "InputParameters": (
        "Singleton",
        {
            FluentVersion.v251: "parameters.input_parameters",
            FluentVersion.v242: "parameters.input_parameters",
            FluentVersion.v241: "parameters.input_parameters",
        },
    ),
    "OutputParameters": (
        "Singleton",
        {
            FluentVersion.v251: "parameters.output_parameters",
            FluentVersion.v242: "parameters.output_parameters",
            FluentVersion.v241: "parameters.output_parameters",
        },
    ),
    "CustomFieldFunctions": (
        "Singleton",
        {
            FluentVersion.v251: "results.custom_field_functions",
        },
    ),
    "CustomFieldFunction": (
        "NamedObject",
        {
            FluentVersion.v251: "results.custom_field_functions",
        },
    ),
    "CustomVectors": (
        "Singleton",
        {
            FluentVersion.v251: "results.custom_vectors",
            FluentVersion.v242: "results.custom_vectors",
            FluentVersion.v241: "results.custom_vectors",
        },
    ),
    "CustomVector": (
        "NamedObject",
        {
            FluentVersion.v251: "results.custom_vectors",
            FluentVersion.v242: "results.custom_vectors",
            FluentVersion.v241: "results.custom_vectors",
        },
    ),
    "SimulationReports": (
        "Singleton",
        {
            FluentVersion.v251: "results.report.simulation_reports",
            FluentVersion.v242: "results.report.simulation_reports",
            FluentVersion.v241: "results.report.simulation_reports",
            FluentVersion.v232: "results.report.simulation_reports",
            FluentVersion.v231: "results.report.simulation_reports",
        },
    ),
}
