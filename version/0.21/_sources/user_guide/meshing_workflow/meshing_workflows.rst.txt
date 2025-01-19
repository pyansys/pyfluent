.. _ref_user_guide_meshing_workflows:

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

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    import_file_name = examples.download_file('mixing_elbow.pmdb', 'pyfluent/mixing_elbow')
    meshing = pyfluent.launch_fluent(
        mode="meshing", precision='double', processor_count=2
    )
    meshing.workflow.InitializeWorkflow(WorkflowType='Watertight Geometry')
    meshing.workflow.TaskObject['Import Geometry'].Arguments = {
        'FileName': import_file_name, 'LengthUnit': 'in'
    }
    meshing.workflow.TaskObject['Import Geometry'].Execute()

Add local sizing
~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Add Local Sizing'].AddChildToTask()
    meshing.workflow.TaskObject['Add Local Sizing'].Execute()

Generate surface mesh
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Generate the Surface Mesh'].Arguments = {
        'CFDSurfaceMeshControls': {'MaxSize': 0.3}
    }
    meshing.workflow.TaskObject['Generate the Surface Mesh'].Execute()

Describe geometry
~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Describe Geometry"].UpdateChildTasks(
        SetupTypeChanged=False
    )
    meshing.workflow.TaskObject["Describe Geometry"].Arguments = {
        SetupType: "The geometry consists of only fluid regions with no voids"
    }
    meshing.workflow.TaskObject["Describe Geometry"].UpdateChildTasks(SetupTypeChanged=True)
    meshing.workflow.TaskObject["Describe Geometry"].Execute()

Update boundaries
~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Update Boundaries"].Arguments = {
        "BoundaryLabelList": ["wall-inlet"],
        "BoundaryLabelTypeList": ["wall"],
        "OldBoundaryLabelList": ["wall-inlet"],
        "OldBoundaryLabelTypeList": ["velocity-inlet"],
    }
    meshing.workflow.TaskObject["Update Boundaries"].Execute()

Update regions
~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Update Regions"].Execute()

Add boundary layers
~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Add Boundary Layers"].AddChildToTask()
    meshing.workflow.TaskObject["Add Boundary Layers"].InsertCompoundChildTask()
    meshing.workflow.TaskObject["smooth-transition_1"].Arguments = {
        "BLControlName": "smooth-transition_1",
    }
    meshing.workflow.TaskObject["Add Boundary Layers"].Arguments = {}
    meshing.workflow.TaskObject["smooth-transition_1"].Execute()

Generate volume mesh
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Generate the Volume Mesh"].Arguments = {
        "VolumeFill": "poly-hexcore",
        "VolumeFillControls": {
            "HexMaxCellLength": 0.3,
        },
    }
    meshing.workflow.TaskObject["Generate the Volume Mesh"].Execute()

Switch to solution mode
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    solver = meshing.switch_to_solver()

Fault-tolerant meshing workflow
-------------------------------
Use the **Fault-tolerant** meshing workflow for complex CAD geometries that need
cleanup or modification, such as addressing overlaps, intersections, holes, and duplicates.
The following example shows how to use the fault-tolerant workflow.

Import CAD and part management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    import_file_name = examples.download_file(
        "exhaust_system.fmd", "pyfluent/exhaust_system"
    )
    meshing = pyfluent.launch_fluent(precision="double", processor_count=2, mode="meshing")
    meshing.workflow.InitializeWorkflow(WorkflowType="Fault-tolerant Meshing")
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
    meshing.PartManagement.ObjectSetting["DefaultObjectSetting"].OneZonePer.set_state("part")
    meshing.workflow.TaskObject["Import CAD and Part Management"].Arguments.set_state(
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
    meshing.workflow.TaskObject["Import CAD and Part Management"].Execute()

Describe geometry and flow
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Describe Geometry and Flow"].Arguments.set_state(
        {
            "AddEnclosure": "No",
            "CloseCaps": "Yes",
            "FlowType": "Internal flow through the object",
        }
    )
    meshing.workflow.TaskObject["Describe Geometry and Flow"].UpdateChildTasks(
        SetupTypeChanged=False
    )
    meshing.workflow.TaskObject["Describe Geometry and Flow"].Arguments.set_state(
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
    meshing.workflow.TaskObject["Describe Geometry and Flow"].UpdateChildTasks(
        SetupTypeChanged=False
    )
    meshing.workflow.TaskObject["Describe Geometry and Flow"].Execute()

Enclose fluid regions (capping)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.set_state(
        {
            "CreatePatchPreferences": {
                "ShowCreatePatchPreferences": False,
            },
            "PatchName": "inlet-1",
            "SelectionType": "zone",
            "ZoneSelectionList": ["inlet.1"],
        }
    )
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.set_state(
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
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].AddChildToTask()

    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].InsertCompoundChildTask()
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.set_state({})
    meshing.workflow.TaskObject["inlet-1"].Execute()
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.set_state(
        {
            "PatchName": "inlet-2",
            "SelectionType": "zone",
            "ZoneSelectionList": ["inlet.2"],
        }
    )
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.set_state(
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
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].AddChildToTask()

    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].InsertCompoundChildTask()
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.set_state({})
    meshing.workflow.TaskObject["inlet-2"].Execute()
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.set_state(
        {
            "PatchName": "inlet-3",
            "SelectionType": "zone",
            "ZoneSelectionList": ["inlet"],
        }
    )
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.set_state(
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
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].AddChildToTask()

    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].InsertCompoundChildTask()
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.set_state({})
    meshing.workflow.TaskObject["inlet-3"].Execute()
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.set_state(
        {
            "PatchName": "outlet-1",
            "SelectionType": "zone",
            "ZoneSelectionList": ["outlet"],
            "ZoneType": "pressure-outlet",
        }
    )
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.set_state(
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
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].AddChildToTask()

    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].InsertCompoundChildTask()
    meshing.workflow.TaskObject["Enclose Fluid Regions (Capping)"].Arguments.set_state({})
    meshing.workflow.TaskObject["outlet-1"].Execute()


Extract edge features
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Extract Edge Features"].Arguments.set_state(
        {
            "ExtractMethodType": "Intersection Loops",
            "ObjectSelectionList": ["flow_pipe", "main"],
        }
    )
    meshing.workflow.TaskObject["Extract Edge Features"].AddChildToTask()

    meshing.workflow.TaskObject["Extract Edge Features"].InsertCompoundChildTask()

    meshing.workflow.TaskObject["edge-group-1"].Arguments.set_state(
        {
            "ExtractEdgesName": "edge-group-1",
            "ExtractMethodType": "Intersection Loops",
            "ObjectSelectionList": ["flow_pipe", "main"],
        }
    )
    meshing.workflow.TaskObject["Extract Edge Features"].Arguments.set_state({})

    meshing.workflow.TaskObject["edge-group-1"].Execute()

Identify regions
~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Identify Regions"].Arguments.set_state(
        {
            "SelectionType": "zone",
            "X": 377.322045740589,
            "Y": -176.800676988458,
            "Z": -37.0764628583475,
            "ZoneSelectionList": ["main.1"],
        }
    )
    meshing.workflow.TaskObject["Identify Regions"].Arguments.set_state(
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
    meshing.workflow.TaskObject["Identify Regions"].AddChildToTask()

    meshing.workflow.TaskObject["Identify Regions"].InsertCompoundChildTask()

    meshing.workflow.TaskObject["fluid-region-1"].Arguments.set_state(
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
    meshing.workflow.TaskObject["Identify Regions"].Arguments.set_state({})

    meshing.workflow.TaskObject["fluid-region-1"].Execute()
    meshing.workflow.TaskObject["Identify Regions"].Arguments.set_state(
        {
            "MaterialPointsName": "void-region-1",
            "NewRegionType": "void",
            "ObjectSelectionList": ["inlet-1", "inlet-2", "inlet-3", "main"],
            "X": 374.722045740589,
            "Y": -278.9775145640143,
            "Z": -161.1700719416913,
        }
    )
    meshing.workflow.TaskObject["Identify Regions"].AddChildToTask()

    meshing.workflow.TaskObject["Identify Regions"].InsertCompoundChildTask()

    meshing.workflow.TaskObject["Identify Regions"].Arguments.set_state({})

    meshing.workflow.TaskObject["void-region-1"].Execute()

Define leakage threshold
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Define Leakage Threshold"].Arguments.set_state(
        {
            "AddChild": "yes",
            "FlipDirection": True,
            "PlaneDirection": "X",
            "RegionSelectionSingle": "void-region-1",
        }
    )
    meshing.workflow.TaskObject["Define Leakage Threshold"].AddChildToTask()

    meshing.workflow.TaskObject["Define Leakage Threshold"].InsertCompoundChildTask()
    meshing.workflow.TaskObject["leakage-1"].Arguments.set_state(
        {
            "AddChild": "yes",
            "FlipDirection": True,
            "LeakageName": "leakage-1",
            "PlaneDirection": "X",
            "RegionSelectionSingle": "void-region-1",
        }
    )
    meshing.workflow.TaskObject["Define Leakage Threshold"].Arguments.set_state(
        {
            "AddChild": "yes",
        }
    )
    meshing.workflow.TaskObject["leakage-1"].Execute()

Update regions settings
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Update Region Settings"].Arguments.set_state(
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
    meshing.workflow.TaskObject["Update Region Settings"].Execute()

Choose mesh control options
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Choose Mesh Control Options"].Execute()

Generate surface mesh
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Generate the Surface Mesh"].Execute()

Update boundaries
~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Update Boundaries"].Execute()

Add boundary layers
~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Add Boundary Layers"].AddChildToTask()

    meshing.workflow.TaskObject["Add Boundary Layers"].InsertCompoundChildTask()

    meshing.workflow.TaskObject["aspect-ratio_1"].Arguments.set_state(
        {
            "BLControlName": "aspect-ratio_1",
        }
    )
    meshing.workflow.TaskObject["Add Boundary Layers"].Arguments.set_state({})

    meshing.workflow.TaskObject["aspect-ratio_1"].Execute()

Generate volume mesh
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Generate the Volume Mesh"].Arguments.set_state(
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
    meshing.workflow.TaskObject["Generate the Volume Mesh"].Execute()

Switch to solution mode
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    solver = meshing.switch_to_solver()


2D meshing workflow
-------------------
Use the **2D** meshing workflow to mesh specific two-dimensional geometries.
The following example shows how to use the 2D Meshing workflow.

Import geometry
~~~~~~~~~~~~~~~

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    import_file_name = examples.download_file('NACA0012.fmd', 'pyfluent/airfoils')
    meshing = pyfluent.launch_fluent(
        mode="meshing", precision='double', processor_count=2
    )
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

Set regions and boundaries
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Update Regions"].Execute()
    meshing.workflow.TaskObject["Update Boundaries"].Arguments.set_state(
        {
            r"SelectionType": r"zone",
        }
    )
    meshing.workflow.TaskObject["Update Boundaries"].Execute()

Define global sizing
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Define Global Sizing"].Arguments.set_state(
        {
            r"CurvatureNormalAngle": 20,
            r"MaxSize": 2000,
            r"MinSize": 5,
            r"SizeFunctions": r"Curvature",
        }
    )
    meshing.workflow.TaskObject["Define Global Sizing"].Execute()

Add body of influence
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

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

Set edge sizing
~~~~~~~~~~~~~~~

.. code:: python

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

Set curvature sizing
~~~~~~~~~~~~~~~~~~~~

.. code:: python

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

Add boundary layer
~~~~~~~~~~~~~~~~~~

.. code:: python

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

Generate surface mesh
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

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

Export Fluent 2D mesh
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject["Export Fluent 2D Mesh"].Arguments.set_state(
        {
            r"FileName": r"mesh1.msh.h5",
        }
    )
    meshing.workflow.TaskObject["Export Fluent 2D Mesh"].Execute()

Switch to solver mode
~~~~~~~~~~~~~~~~~~~~~

Switching to solver mode is not allowed in 2D Meshing mode.


Sample use of ``CommandArguments``
----------------------------------
This simple example shows how to use the ``CommandArgument`` attributes and explicit
attribute access methods in a watertight geometry meshing workflow.

.. Note::
   ``CommandArgument`` attributes are read-only.

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    import_file_name = examples.download_file("mixing_elbow.pmdb", "pyfluent/mixing_elbow")
    meshing = pyfluent.launch_fluent(mode="meshing", precision="double", processor_count=2)
    w = meshing.workflow
    w.InitializeWorkflow(WorkflowType="Watertight Geometry")

    w.TaskObject["Import Geometry"].CommandArguments()
    w.TaskObject["Import Geometry"].CommandArguments.FileName.is_read_only()
    w.TaskObject["Import Geometry"].CommandArguments.LengthUnit.is_active()
    w.TaskObject["Import Geometry"].CommandArguments.LengthUnit.allowed_values()
    w.TaskObject["Import Geometry"].CommandArguments.LengthUnit.default_value()
    w.TaskObject["Import Geometry"].CommandArguments.LengthUnit()
    w.TaskObject["Import Geometry"].CommandArguments.CadImportOptions.OneZonePer()
    w.TaskObject["Import Geometry"].CommandArguments.CadImportOptions.FeatureAngle.min()

Some improvements
-----------------
You can call the TaskObject to get it's state:

.. code:: python

    meshing.workflow.TaskObject()

Items of the TaskObject can now be accessed in settings dictionary style:

.. code:: python

    for name, object in meshing.workflow.TaskObject.items():
        ...
