.. _ref_meshing_workflows_guide:

Classic meshing workflow
========================
You can use PyFluent to access the classic meshing workflows
which align with the journal syntax.

Watertight geometry meshing workflow
------------------------------------
Use the **Watertight Geometry** workflow for watertight CAD geometries that
require little cleanup. This is useful for clean geometries that have already
been prepped in another software, such as Ansys SpaceClaim.
The following example shows you how to use the Watertight Geometry workflow.

Import geometry
~~~~~~~~~~~~~~~

.. code:: python

    >>> import ansys.fluent.core as pyfluent
    >>> from ansys.fluent.core import examples

    >>> import_file_name = examples.download_file('mixing_elbow.pmdb', 'pyfluent/mixing_elbow')
    >>> meshing = pyfluent.launch_fluent(
    >>>     mode=pyfluent.FluentMode.MESHING, precision=pyfluent.Precision.DOUBLE, processor_count=2
    >>> )
    >>> workflow = meshing.workflow
    >>> workflow.InitializeWorkflow(WorkflowType='Watertight Geometry')
    >>> tasks = workflow.TaskObject
    >>> import_geometry = tasks['Import Geometry']
    >>> import_geometry.Arguments.set_state({
    >>>     'FileName': import_file_name, 'LengthUnit': 'in'
    >>> })
    >>> import_geometry.Execute()

Add local sizing
~~~~~~~~~~~~~~~~

.. code:: python

    >>> add_local_sizing = tasks['Add Local Sizing']
    >>> add_local_sizing.AddChildToTask()
    >>> add_local_sizing.Execute()

Generate surface mesh
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> create_surface_mesh = tasks['Generate the Surface Mesh']
    >>> create_surface_mesh.Arguments = {
    >>>     'CFDSurfaceMeshControls': {'MaxSize': 0.3}
    >>> }
    >>> create_surface_mesh.Execute()

Describe geometry
~~~~~~~~~~~~~~~~~

.. code:: python

    >>> describe_geometry = tasks["Describe Geometry"]
    >>> describe_geometry.UpdateChildTasks(
    >>>     SetupTypeChanged=False
    >>> )
    >>> describe_geometry.Arguments = {
    >>>     SetupType: "The geometry consists of only fluid regions with no voids"
    >>> }
    >>> describe_geometry.UpdateChildTasks(SetupTypeChanged=True)
    >>> describe_geometry.Execute()

Update boundaries
~~~~~~~~~~~~~~~~~

.. code:: python

    >>> update_boundaries = tasks["Update Boundaries"]
    >>> update_boundaries.Arguments.set_state({
    >>>     "BoundaryLabelList": ["wall-inlet"],
    >>>     "BoundaryLabelTypeList": ["wall"],
    >>>     "OldBoundaryLabelList": ["wall-inlet"],
    >>>     "OldBoundaryLabelTypeList": ["velocity-inlet"],
    >>> })
    >>> update_boundaries.Execute()

Update regions
~~~~~~~~~~~~~~

.. code:: python

    tasks["Update Regions"].Execute()

Add boundary layers
~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> add_boundary_layers = tasks["Add Boundary Layers"]
    >>> add_boundary_layers.AddChildToTask()
    >>> add_boundary_layers.InsertCompoundChildTask()
    >>> transition = tasks["smooth-transition_1"]
    >>> transition.Arguments.set_state({
    >>>     "BLControlName": "smooth-transition_1",
    >>> })
    >>> add_boundary_layers.Arguments.set_state({})
    >>> transition.Execute()

Generate volume mesh
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> create_volume_mesh = tasks["Generate the Volume Mesh"]
    >>> create_volume_mesh.Arguments = {
    >>>     "VolumeFill": "poly-hexcore",
    >>>     "VolumeFillControls": {
    >>>         "HexMaxCellLength": 0.3,
    >>>     },
    >>> }
    >>> create_volume_mesh.Execute()

Switch to solution mode
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> solver = meshing.switch_to_solver()

Fault-tolerant meshing workflow
-------------------------------
Use the **Fault-tolerant** meshing workflow for complex CAD geometries that need
cleanup or modification, such as addressing overlaps, intersections, holes, and duplicates.
The following example shows how to use the fault-tolerant workflow.

Import CAD and part management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> import ansys.fluent.core as pyfluent
    >>> from ansys.fluent.core import examples

    >>> import_file_name = examples.download_file(
    >>>     "exhaust_system.fmd", "pyfluent/exhaust_system"
    >>> )
    >>> meshing = pyfluent.launch_fluent(
    >>>     precision=pyfluent.Precision.DOUBLE,
    >>>     processor_count=2,
    >>>     mode=pyfluent.FluentMode.MESHING
    >>> )
    >>> workflow = meshing.workflow
    >>> workflow.InitializeWorkflow(WorkflowType="Fault-tolerant Meshing")
    >>> part_management = meshing.PartManagement
    >>> file_management = meshing.PMFileManagement
    >>> part_management.InputFileChanged(
    >>>     FilePath=import_file_name,
    >>>     IgnoreSolidNames=False,
    >>>     PartPerBody=False
    >>> )
    >>> file_management.FileManager.LoadFiles()
    >>> part_management.Node["Meshing Model"].Copy(
    >>>     Paths=[
    >>>         "/dirty_manifold-for-wrapper," + "1/dirty_manifold-for-wrapper,1/main,1",
    >>>         "/dirty_manifold-for-wrapper," + "1/dirty_manifold-for-wrapper,1/flow-pipe,1",
    >>>         "/dirty_manifold-for-wrapper," + "1/dirty_manifold-for-wrapper,1/outpipe3,1",
    >>>         "/dirty_manifold-for-wrapper," + "1/dirty_manifold-for-wrapper,1/object2,1",
    >>>         "/dirty_manifold-for-wrapper," + "1/dirty_manifold-for-wrapper,1/object1,1",
    >>>     ]
    >>> )
    >>> part_management.ObjectSetting["DefaultObjectSetting"].OneZonePer.set_state("part")
    >>> tasks = workflow.TaskObject
    >>> import_cad = tasks["Import CAD and Part Management"]
    >>> import_cad.Arguments.set_state(
    >>>     {
    >>>         "Context": 0,
    >>>         "CreateObjectPer": "Custom",
    >>>         "FMDFileName": import_file_name,
    >>>         "FileLoaded": "yes",
    >>>         "ObjectSetting": "DefaultObjectSetting",
    >>>         "Options": {
    >>>             "Line": False,
    >>>             "Solid": False,
    >>>             "Surface": False,
    >>>         }
    >>>     },
    >>> )
    >>> import_cad.Execute()

Describe geometry and flow
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> describe_geometry = tasks["Describe Geometry and Flow"]
    >>> describe_geometry.Arguments.set_state(
    >>>     {
    >>>         "AddEnclosure": "No",
    >>>         "CloseCaps": "Yes",
    >>>         "FlowType": "Internal flow through the object",
    >>>     }
    >>> )
    >>> describe_geometry.UpdateChildTasks(
    >>>     SetupTypeChanged=False
    >>> )
    >>> describe_geometry.Arguments.set_state(
    >>>     {
    >>>         "AddEnclosure": "No",
    >>>         "CloseCaps": "Yes",
    >>>         "DescribeGeometryAndFlowOptions": {
    >>>             "AdvancedOptions": True,
    >>>             "ExtractEdgeFeatures": "Yes",
    >>>         },
    >>>         "FlowType": "Internal flow through the object",
    >>>     }
    >>> )
    >>> describe_geometry.UpdateChildTasks(
    >>>     SetupTypeChanged=False
    >>> )
    >>> describe_geometry.Execute()

Enclose fluid regions (capping)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> enclose = tasks["Enclose Fluid Regions (Capping)"]
    >>> enclose.Arguments.set_state(
    >>>     {
    >>>         "CreatePatchPreferences": {
    >>>             "ShowCreatePatchPreferences": False,
    >>>         },
    >>>         "PatchName": "inlet-1",
    >>>         "SelectionType": "zone",
    >>>         "ZoneSelectionList": ["inlet.1"],
    >>>     }
    >>> )
    >>> enclose.Arguments.set_state(
    >>>     {
    >>>         "CreatePatchPreferences": {
    >>>             "ShowCreatePatchPreferences": False,
    >>>         },
    >>>         "PatchName": "inlet-1",
    >>>         "SelectionType": "zone",
    >>>         "ZoneLocation": [
    >>>             "1",
    >>>             "351.68205",
    >>>             "-361.34322",
    >>>             "-301.88668",
    >>>             "396.96205",
    >>>             "-332.84759",
    >>>             "-266.69751",
    >>>             "inlet.1",
    >>>         ],
    >>>         "ZoneSelectionList": ["inlet.1"],
    >>>     }
    >>> )
    >>> enclose.AddChildToTask()
    >>> enclose.InsertCompoundChildTask()
    >>> enclose.Arguments.set_state({})
    >>> tasks["inlet-1"].Execute()
    >>> enclose.Arguments.set_state(
    >>>     {
    >>>         "PatchName": "inlet-2",
    >>>         "SelectionType": "zone",
    >>>         "ZoneSelectionList": ["inlet.2"],
    >>>     }
    >>> )
    >>> enclose.Arguments.set_state(
    >>>     {
    >>>         "PatchName": "inlet-2",
    >>>         "SelectionType": "zone",
    >>>         "ZoneLocation": [
    >>>             "1",
    >>>             "441.68205",
    >>>             "-361.34322",
    >>>             "-301.88668",
    >>>             "486.96205",
    >>>             "-332.84759",
    >>>             "-266.69751",
    >>>             "inlet.2",
    >>>         ],
    >>>         "ZoneSelectionList": ["inlet.2"],
    >>>     }
    >>> )
    >>> enclose.AddChildToTask()

    >>> enclose.InsertCompoundChildTask()
    >>> enclose.Arguments.set_state({})
    >>> tasks["inlet-2"].Execute()
    >>> enclose.Arguments.set_state(
    >>>     {
    >>>         "PatchName": "inlet-3",
    >>>         "SelectionType": "zone",
    >>>         "ZoneSelectionList": ["inlet"],
    >>>     }
    >>> )
    >>> enclose.Arguments.set_state(
    >>>     {
    >>>         "PatchName": "inlet-3",
    >>>         "SelectionType": "zone",
    >>>        "ZoneLocation": [
    >>>             "1",
    >>>             "261.68205",
    >>>             "-361.34322",
    >>>             "-301.88668",
    >>>             "306.96205",
    >>>             "-332.84759",
    >>>             "-266.69751",
    >>>             "inlet",
    >>>         ],
    >>>         "ZoneSelectionList": ["inlet"],
    >>>     }
    >>> )
    >>> enclose.AddChildToTask()

    >>> enclose.InsertCompoundChildTask()
    >>> enclose.Arguments.set_state({})
    meshing.workflow.TaskObject["inlet-3"].Execute()
    >>> enclose.Arguments.set_state(
    >>>     {
    >>>         "PatchName": "outlet-1",
    >>>         "SelectionType": "zone",
    >>>         "ZoneSelectionList": ["outlet"],
    >>>         "ZoneType": "pressure-outlet",
    >>>     }
    >>> )
    >>> enclose.Arguments.set_state(
    >>>     {
    >>>         "PatchName": "outlet-1",
    >>>         "SelectionType": "zone",
    >>>         "ZoneLocation": [
    >>>             "1",
    >>>             "352.22702",
    >>>             "-197.8957",
    >>>             "84.102381",
    >>>             "394.41707",
    >>>             "-155.70565",
    >>>             "84.102381",
    >>>             "outlet",
    >>>         ],
    >>>         "ZoneSelectionList": ["outlet"],
    >>>         "ZoneType": "pressure-outlet",
    >>>     }
    >>> )
    >>> enclose.AddChildToTask()

    >>> enclose.InsertCompoundChildTask()
    >>> enclose.Arguments.set_state({})
    >>> tasks["outlet-1"].Execute()


Extract edge features
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> extract_edge_features = tasks["Extract Edge Features"]
    >>> extract_edge_features.Arguments.set_state(
    >>>     {
    >>>         "ExtractMethodType": "Intersection Loops",
    >>>         "ObjectSelectionList": ["flow_pipe", "main"],
    >>>     }
    >>> )
    >>> extract_edge_features.AddChildToTask()

    >>> extract_edge_features.InsertCompoundChildTask()

    >>> edge_group = tasks["edge-group-1"]
    >>> edge_group.Arguments.set_state(
    >>>     {
    >>>         "ExtractEdgesName": "edge-group-1",
    >>>         "ExtractMethodType": "Intersection Loops",
    >>>         "ObjectSelectionList": ["flow_pipe", "main"],
    >>>     }
    >>> )
    >>> extract_edge_features.Arguments.set_state({})

    >>> edge_group.Execute()

Identify regions
~~~~~~~~~~~~~~~~

.. code:: python

    >>> identify_regions = tasks["Identify Regions"]
    >>> identify_regions.Arguments.set_state(
    >>>     {
    >>>         "SelectionType": "zone",
    >>>         "X": 377.322045740589,
    >>>         "Y": -176.800676988458,
    >>>         "Z": -37.0764628583475,
    >>>         "ZoneSelectionList": ["main.1"],
    >>>     }
    >>> )
    >>> identify_regions.Arguments.set_state(
    >>>     {
    >>>         "SelectionType": "zone",
    >>>         "X": 377.322045740589,
    >>>         "Y": -176.800676988458,
    >>>         "Z": -37.0764628583475,
    >>>         "ZoneLocation": [
    >>>             "1",
    >>>             "213.32205",
    >>>             "-225.28068",
    >>>             "-158.25531",
    >>>             "541.32205",
    >>>             "-128.32068",
    >>>             "84.102381",
    >>>             "main.1",
    >>>         ],
    >>>         "ZoneSelectionList": ["main.1"],
    >>>     }
    >>> )
    >>> identify_regions.AddChildToTask()

    >>> identify_regions.InsertCompoundChildTask()

    >>> tasks["fluid-region-1"].Arguments.set_state(
    >>>     {
    >>>         "MaterialPointsName": "fluid-region-1",
    >>>         "SelectionType": "zone",
    >>>         "X": 377.322045740589,
    >>>         "Y": -176.800676988458,
    >>>         "Z": -37.0764628583475,
    >>>         "ZoneLocation": [
    >>>             "1",
    >>>             "213.32205",
    >>>             "-225.28068",
    >>>             "-158.25531",
    >>>             "541.32205",
    >>>             "-128.32068",
    >>>             "84.102381",
    >>>             "main.1",
    >>>         ],
    >>>         "ZoneSelectionList": ["main.1"],
    >>>     }
    >>> )
    >>> identify_regions.Arguments.set_state({})

    >>> tasks["fluid-region-1"].Execute()
    >>> identify_regions.Arguments.set_state(
    >>>     {
    >>>         "MaterialPointsName": "void-region-1",
    >>>         "NewRegionType": "void",
    >>>         "ObjectSelectionList": ["inlet-1", "inlet-2", "inlet-3", "main"],
    >>>         "X": 374.722045740589,
    >>>         "Y": -278.9775145640143,
    >>>         "Z": -161.1700719416913,
    >>>     }
    >>> )
    >>> identify_regions.AddChildToTask()

    >>> identify_regions.InsertCompoundChildTask()

    >>> identify_regions.Arguments.set_state({})

    >>> tasks["void-region-1"].Execute()

Define leakage threshold
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> define_leakage_threshold = tasks["Define Leakage Threshold"]
    >>> define_leakage_threshold.Arguments.set_state(
    >>>     {
    >>>         "AddChild": "yes",
    >>>         "FlipDirection": True,
    >>>         "PlaneDirection": "X",
    >>>         "RegionSelectionSingle": "void-region-1",
    >>>     }
    >>> )
    >>> define_leakage_threshold.AddChildToTask()

    >>> define_leakage_threshold.InsertCompoundChildTask()
    >>> tasks["leakage-1"].Arguments.set_state(
    >>>     {
    >>>         "AddChild": "yes",
    >>>         "FlipDirection": True,
    >>>         "LeakageName": "leakage-1",
    >>>         "PlaneDirection": "X",
    >>>         "RegionSelectionSingle": "void-region-1",
    >>>     }
    >>> )
    >>> define_leakage_threshold.Arguments.set_state(
    >>>     {
    >>>         "AddChild": "yes",
    >>>     }
    >>> )
    >>> tasks["leakage-1"].Execute()

Update regions settings
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> update_region_settings = tasks["Update Region Settings"]
    >>> update_region_settings.Arguments.set_state(
    >>>     {
    >>>         "AllRegionFilterCategories": ["2"] * 5 + ["1"] * 2,
    >>>         "AllRegionLeakageSizeList": ["none"] * 6 + ["6.4"],
    >>>         "AllRegionLinkedConstructionSurfaceList": ["n/a"] * 6 + ["no"],
    >>>         "AllRegionMeshMethodList": ["none"] * 6 + ["wrap"],
    >>>         "AllRegionNameList": [
    >>>             "main",
    >>>             "flow_pipe",
    >>>             "outpipe3",
    >>>             "object2",
    >>>             "object1",
    >>>             "void-region-1",
    >>>             "fluid-region-1",
    >>>         ],
    >>>         "AllRegionOversetComponenList": ["no"] * 7,
    >>>         "AllRegionSourceList": ["object"] * 5 + ["mpt"] * 2,
    >>>         "AllRegionTypeList": ["void"] * 6 + ["fluid"],
    >>>         "AllRegionVolumeFillList": ["none"] * 6 + ["tet"],
    >>>         "FilterCategory": "Identified Regions",
    >>>         "OldRegionLeakageSizeList": [""],
    >>>         "OldRegionMeshMethodList": ["wrap"],
    >>>         "OldRegionNameList": ["fluid-region-1"],
    >>>         "OldRegionOversetComponenList": ["no"],
    >>>         "OldRegionTypeList": ["fluid"],
    >>>         "OldRegionVolumeFillList": ["hexcore"],
    >>>         "RegionLeakageSizeList": [""],
    >>>         "RegionMeshMethodList": ["wrap"],
    >>>         "RegionNameList": ["fluid-region-1"],
    >>>         "RegionOversetComponenList": ["no"],
    >>>         "RegionTypeList": ["fluid"],
    >>>         "RegionVolumeFillList": ["tet"],
    >>>     }
    >>> )
    >>> update_region_settings.Execute()

Choose mesh control options
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> tasks["Choose Mesh Control Options"].Execute()

Generate surface mesh
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> tasks["Generate the Surface Mesh"].Execute()

Update boundaries
~~~~~~~~~~~~~~~~~

.. code:: python

    >>> tasks["Update Boundaries"].Execute()

Add boundary layers
~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> add_boundary_layers = tasks["Add Boundary Layers"]
    >>> add_boundary_layers.AddChildToTask()

    >>> add_boundary_layers.InsertCompoundChildTask()

    >>> aspect_ratio_1 = tasks["aspect-ratio_1"]
    >>> aspect_ratio_1.Arguments.set_state(
    >>>     {
    >>>         "BLControlName": "aspect-ratio_1",
    >>>     }
    >>> )
    >>> add_boundary_layers.Arguments.set_state({})

    >>> aspect_ratio_1.Execute()

Generate volume mesh
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> create_volume_mesh = tasks["Generate the Volume Mesh"]
    >>> create_volume_mesh.Arguments.set_state(
    >>>     {
    >>>         "AllRegionNameList": [
    >>>             "main",
    >>>             "flow_pipe",
    >>>             "outpipe3",
    >>>             "object2",
    >>>             "object1",
    >>>             "void-region-1",
    >>>             "fluid-region-1",
    >>>         ],
    >>>         "AllRegionSizeList": ["11.33375"] * 7,
    >>>         "AllRegionVolumeFillList": ["none"] * 6 + ["tet"],
    >>>         "EnableParallel": True,
    >>>     }
    >>> )
    >>> create_volume_mesh.Execute()

Switch to solution mode
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> solver = meshing.switch_to_solver()


2D meshing workflow
-------------------
Use the **2D** meshing workflow to mesh specific two-dimensional geometries.
The following example shows how to use the 2D Meshing workflow.

Import geometry
~~~~~~~~~~~~~~~

.. code:: python

    >>> import ansys.fluent.core as pyfluent
    >>> from ansys.fluent.core import examples

    >>> import_file_name = examples.download_file('NACA0012.fmd', 'pyfluent/airfoils')
    >>> meshing = pyfluent.launch_fluent(
    >>>     mode=pyfluent.FluentMode.MESHING,
    >>>     precision=pyfluent.Precision.DOUBLE,
    >>>     processor_count=2
    >>> )
    >>> workflow = meshing.workflow
    >>> tasks = workflow.TaskObject
    >>> load_cad = workflow.TaskObject["Load CAD Geometry"]
    >>> load_cad.Arguments.set_state(
    >>>     {
    >>>         r"FileName": import_file_name,
    >>>         r"LengthUnit": r"mm",
    >>>         r"Refaceting": {
    >>>             r"Refacet": False,
    >>>         },
    >>>     }
    >>> )
    >>> load_cad.Execute()

Update regions and boundaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> update_regions = tasks["Update Regions"]
    >>> update_boundaries = tasks["Update Boundaries"]
    >>> update_regions.Execute()
    >>> update_boundaries.Arguments.set_state(
    >>>     {
    >>>         r"SelectionType": r"zone",
    >>>     }
    >>> )
    >>> update_boundaries.Execute()

Define global sizing
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> define_global_sizing = tasks["Define Global Sizing"]
    >>> define_global_sizing.Arguments.set_state(
    >>>     {
    >>>         r"CurvatureNormalAngle": 20,
    >>>         r"MaxSize": 2000,
    >>>         r"MinSize": 5,
    >>>         r"SizeFunctions": r"Curvature",
    >>>     }
    >>> )
    >>> define_global_sizing.Execute()

Add body of influence
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> add_local_sizing = tasks["Add Local Sizing"]
    >>> add_local_sizing.Arguments.set_state(
    >>>     {
    >>>         r"AddChild": r"yes",
    >>>         r"BOIControlName": r"boi_1",
    >>>         r"BOIExecution": r"Body Of Influence",
    >>>         r"BOIFaceLabelList": [r"boi"],
    >>>         r"BOISize": 50,
    >>>         r"BOIZoneorLabel": r"label",
    >>>         r"DrawSizeControl": True,
    >>>     }
    >>> )
    >>> add_local_sizing.AddChildAndUpdate(DeferUpdate=False)

Set edge sizing
~~~~~~~~~~~~~~~

.. code:: python

    >>> add_local_sizing.Arguments.set_state(
    >>>     {
    >>>         r"AddChild": r"yes",
    >>>         r"BOIControlName": r"edgesize_1",
    >>>         r"BOIExecution": r"Edge Size",
    >>>         r"BOISize": 5,
    >>>         r"BOIZoneorLabel": r"label",
    >>>         r"DrawSizeControl": True,
    >>>         r"EdgeLabelList": [r"airfoil-te"],
    >>>     }
    >>> )
    >>> add_local_sizing.AddChildAndUpdate(DeferUpdate=False)

Set curvature sizing
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> add_local_sizing.Arguments.set_state(
    >>>     {
    >>>         r"AddChild": r"yes",
    >>>         r"BOIControlName": r"curvature_1",
    >>>         r"BOICurvatureNormalAngle": 10,
    >>>         r"BOIExecution": r"Curvature",
    >>>         r"BOIMaxSize": 2,
    >>>         r"BOIMinSize": 1.5,
    >>>         r"BOIScopeTo": r"edges",
    >>>         r"BOIZoneorLabel": r"label",
    >>>         r"DrawSizeControl": True,
    >>>         r"EdgeLabelList": [r"airfoil"],
    >>>     }
    >>> )
    >>> add_local_sizing.AddChildAndUpdate(DeferUpdate=False)

Add boundary layer
~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> add_boundary_layers = tasks["Add 2D Boundary Layers"]
    >>> add_boundary_layers.Arguments.set_state(
    >>>     {
    >>>         r"AddChild": r"yes",
    >>>         r"BLControlName": r"aspect-ratio_1",
    >>>         r"NumberOfLayers": 4,
    >>>         r"OffsetMethodType": r"aspect-ratio",
    >>>     }
    >>> )
    >>> add_boundary_layers.AddChildAndUpdate(
    >>>     DeferUpdate=False
    >>> )

Generate surface mesh
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> create_surface_mesh = tasks["Generate the Surface Mesh"]
    >>> create_surface_mesh.Arguments.set_state(
    >>>     {
    >>>         r"Surface2DPreferences": {
    >>>             r"MergeEdgeZonesBasedOnLabels": r"no",
    >>>             r"MergeFaceZonesBasedOnLabels": r"no",
    >>>             r"ShowAdvancedOptions": True,
    >>>         },
    >>>     }
    >>> )
    >>> create_surface_mesh.Execute()

    >>> aspect_ratio_1 = tasks["aspect-ratio_1"]
    >>> aspect_ratio_1.Revert()
    >>> aspect_ratio_1.Arguments.set_state(
    >>>     {
    >>>         r"AddChild": r"yes",
    >>>         r"BLControlName": r"uniform_1",
    >>>         r"FirstLayerHeight": 2,
    >>>         r"NumberOfLayers": 4,
    >>>         r"OffsetMethodType": r"uniform",
    >>>     }
    >>> )
    >>> aspect_ratio_1.Execute()

    >>> create_surface_mesh = tasks["Generate the Surface Mesh"]
    >>> create_surface_mesh.Arguments.set_state(None)
    >>> create_surface_mesh.Arguments.set_state(
    >>>     {
    >>>         r"Surface2DPreferences": {
    >>>             r"MergeEdgeZonesBasedOnLabels": r"no",
    >>>             r"MergeFaceZonesBasedOnLabels": r"no",
    >>>             r"ShowAdvancedOptions": True,
    >>>         },
    >>>     }
    >>> )
    >>> create_surface_mesh.Execute()

    >>> uniform_1 = tasks["uniform_1"]
    >>> uniform_1.Revert()
    >>> uniform_1.Arguments.set_state(
    >>>     {
    >>>         r"AddChild": r"yes",
    >>>         r"BLControlName": r"smooth-transition_1",
    >>>         r"FirstLayerHeight": 2,
    >>>         r"NumberOfLayers": 7,
    >>>         r"OffsetMethodType": r"smooth-transition",
    >>>     }
    >>> )
    >>> uniform_1.Execute()

    >>> create_surface_mesh.Arguments.set_state(None)
    >>> create_surface_mesh.Arguments.set_state(
    >>>     {
    >>>         r"Surface2DPreferences": {
    >>>             r"MergeEdgeZonesBasedOnLabels": r"no",
    >>>             r"MergeFaceZonesBasedOnLabels": r"no",
    >>>             r"ShowAdvancedOptions": True,
    >>>         },
    >>>     }
    >>> )
    >>> create_surface_mesh.Execute()

Export Fluent 2D mesh
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> export_mesh = tasks["Export Fluent 2D Mesh"]
    >>> export_mesh.Arguments.set_state(
    >>>     {
    >>>         r"FileName": r"mesh1.msh.h5",
    >>>     }
    >>> )
    >>> export_mesh.Execute()

Switch to solver mode
~~~~~~~~~~~~~~~~~~~~~

Switching to solver mode is not allowed in 2D Meshing mode.


State access
------------
You can call the ``TaskObject`` container to get its state:

.. code:: python

    >>> tasks()

The ``TaskObject`` container supports dictionary semantics:

.. code:: python

    >>> for name, object_dict in meshing.workflow.TaskObject.items():
    >>>     print(f"Task name: {name}, state: {object_dict}")
