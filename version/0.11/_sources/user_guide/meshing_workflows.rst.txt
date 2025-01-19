.. _ref_user_guide_meshing_workflows:

Using meshing workflows
=======================
PyFluent supports accessing all Fluent meshing functionalities, including 
guided meshing workflows.

Watertight geometry meshing workflow
------------------------------------
This simple example shows how you use the watertight geometry meshing workflow.

Import geometry
~~~~~~~~~~~~~~~

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    import_filename = examples.download_file('mixing_elbow.pmdb', 'pyfluent/mixing_elbow')
    meshing = pyfluent.launch_fluent(
        mode="meshing", precision='double', processor_count=2
    )
    meshing.workflow.InitializeWorkflow(WorkflowType='Watertight Geometry')
    meshing.workflow.TaskObject['Import Geometry'].Arguments = dict(
        FileName=import_filename, LengthUnit='in'
    )
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

    meshing.workflow.TaskObject['Describe Geometry'].UpdateChildTasks(
        SetupTypeChanged=False
    )
    meshing.workflow.TaskObject['Describe Geometry'].Arguments = dict(
        SetupType='The geometry consists of only fluid regions with no voids'
    )
    meshing.workflow.TaskObject['Describe Geometry'].UpdateChildTasks(
        SetupTypeChanged=True
    )
    meshing.workflow.TaskObject['Describe Geometry'].Execute()

Update boundaries
~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Update Boundaries'].Arguments = {
        'BoundaryLabelList': ['wall-inlet'],
        'BoundaryLabelTypeList': ['wall'],
        'OldBoundaryLabelList': ['wall-inlet'],
        'OldBoundaryLabelTypeList': ['velocity-inlet'],
    }
    meshing.workflow.TaskObject['Update Boundaries'].Execute()

Update regions
~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Update Regions'].Execute()

Add boundary layers
~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Add Boundary Layers'].AddChildToTask()
    meshing.workflow.TaskObject['Add Boundary Layers'].InsertCompoundChildTask()
    meshing.workflow.TaskObject['smooth-transition_1'].Arguments = {
        'BLControlName': 'smooth-transition_1',
    }
    meshing.workflow.TaskObject['Add Boundary Layers'].Arguments = {}
    meshing.workflow.TaskObject['smooth-transition_1'].Execute()

Generate volume mesh
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Generate the Volume Mesh'].Arguments = {
        'VolumeFill': 'poly-hexcore',
        'VolumeFillControls': {
            'HexMaxCellLength': 0.3,
        },
    }
    meshing.workflow.TaskObject['Generate the Volume Mesh'].Execute()

Switch to solution mode
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    solver = meshing.switch_to_solver()

Fault-tolerant meshing workflow
-------------------------------
This simple example shows how you use the fault-tolerant meshing workflow.

Import CAD and part management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    import_filename = examples.download_file(
        'exhaust_system.fmd', 'pyfluent/exhaust_system'
    )
    meshing = pyfluent.launch_fluent(
        precision='double', processor_count=2, mode="meshing"
    )
    meshing.workflow.InitializeWorkflow(WorkflowType='Fault-tolerant Meshing')
    meshing.PartManagement.InputFileChanged(
        FilePath=import_filename, IgnoreSolidNames=False, PartPerBody=False
    )
    meshing.PMFileManagement.FileManager.LoadFiles()
    meshing.PartManagement.Node['Meshing Model'].Copy(
        Paths=[
            '/dirty_manifold-for-wrapper,' + '1/dirty_manifold-for-wrapper,1/main,1',
            '/dirty_manifold-for-wrapper,' + '1/dirty_manifold-for-wrapper,1/flow-pipe,1',
            '/dirty_manifold-for-wrapper,' + '1/dirty_manifold-for-wrapper,1/outpipe3,1',
            '/dirty_manifold-for-wrapper,' + '1/dirty_manifold-for-wrapper,1/object2,1',
            '/dirty_manifold-for-wrapper,' + '1/dirty_manifold-for-wrapper,1/object1,1',
        ]
    )
    meshing.PartManagement.ObjectSetting[
        'DefaultObjectSetting'
    ].OneZonePer.setState('part')
    meshing.workflow.TaskObject[
        'Import CAD and Part Management'
    ].Arguments.setState(
        {
            'Context': 0,
            'CreateObjectPer': 'Custom',
            'FMDFileName': import_filename,
            'FileLoaded': 'yes',
            'ObjectSetting': 'DefaultObjectSetting',
            'Options': {
                'Line': False,
                'Solid': False,
                'Surface': False,
            },
        }
    )
    meshing.workflow.TaskObject['Import CAD and Part Management'].Execute()

Describe geometry and flow
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Describe Geometry and Flow'].Arguments.setState(
        {
            'AddEnclosure': 'No',
            'CloseCaps': 'Yes',
            'FlowType': 'Internal flow through the object',
        }
    )
    meshing.workflow.TaskObject['Describe Geometry and Flow'].UpdateChildTasks(
        SetupTypeChanged=False
    )
    meshing.workflow.TaskObject['Describe Geometry and Flow'].Arguments.setState(
        {
            'AddEnclosure': 'No',
            'CloseCaps': 'Yes',
            'DescribeGeometryAndFlowOptions': {
                'AdvancedOptions': True,
                'ExtractEdgeFeatures': 'Yes',
            },
            'FlowType': 'Internal flow through the object',
        }
    )
    meshing.workflow.TaskObject['Describe Geometry and Flow'].UpdateChildTasks(
        SetupTypeChanged=False
    )
    meshing.workflow.TaskObject['Describe Geometry and Flow'].Execute()

Enclose fluid regions (capping)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].Arguments.setState(
        {
            'CreatePatchPreferences': {
                'ShowCreatePatchPreferences': False,
            },
            'PatchName': 'inlet-1',
            'SelectionType': 'zone',
            'ZoneSelectionList': ['inlet.1'],
        }
    )
    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].Arguments.setState(
        {
            'CreatePatchPreferences': {
                'ShowCreatePatchPreferences': False,
            },
            'PatchName': 'inlet-1',
            'SelectionType': 'zone',
            'ZoneLocation': [
                '1',
                '351.68205',
                '-361.34322',
                '-301.88668',
                '396.96205',
                '-332.84759',
                '-266.69751',
                'inlet.1',
            ],
            'ZoneSelectionList': ['inlet.1'],
        }
    )
    meshing.workflow.TaskObject['Enclose Fluid Regions (Capping)'].AddChildToTask()

    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].InsertCompoundChildTask()
    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].Arguments.setState({})
    meshing.workflow.TaskObject['inlet-1'].Execute()
    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].Arguments.setState(
        {
            'PatchName': 'inlet-2',
            'SelectionType': 'zone',
            'ZoneSelectionList': ['inlet.2'],
        }
    )
    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].Arguments.setState(
        {
            'PatchName': 'inlet-2',
            'SelectionType': 'zone',
            'ZoneLocation': [
                '1',
                '441.68205',
                '-361.34322',
                '-301.88668',
                '486.96205',
                '-332.84759',
                '-266.69751',
                'inlet.2',
            ],
            'ZoneSelectionList': ['inlet.2'],
        }
    )
    meshing.workflow.TaskObject['Enclose Fluid Regions (Capping)'].AddChildToTask()

    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].InsertCompoundChildTask()
    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].Arguments.setState({})
    meshing.workflow.TaskObject['inlet-2'].Execute()
    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].Arguments.setState(
        {
            'PatchName': 'inlet-3',
            'SelectionType': 'zone',
            'ZoneSelectionList': ['inlet'],
        }
    )
    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].Arguments.setState(
        {
            'PatchName': 'inlet-3',
            'SelectionType': 'zone',
            'ZoneLocation': [
                '1',
                '261.68205',
                '-361.34322',
                '-301.88668',
                '306.96205',
                '-332.84759',
                '-266.69751',
                'inlet',
            ],
            'ZoneSelectionList': ['inlet'],
        }
    )
    meshing.workflow.TaskObject['Enclose Fluid Regions (Capping)'].AddChildToTask()

    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].InsertCompoundChildTask()
    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].Arguments.setState({})
    meshing.workflow.TaskObject['inlet-3'].Execute()
    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].Arguments.setState(
        {
            'PatchName': 'outlet-1',
            'SelectionType': 'zone',
            'ZoneSelectionList': ['outlet'],
            'ZoneType': 'pressure-outlet',
        }
    )
    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].Arguments.setState(
        {
            'PatchName': 'outlet-1',
            'SelectionType': 'zone',
            'ZoneLocation': [
                '1',
                '352.22702',
                '-197.8957',
                '84.102381',
                '394.41707',
                '-155.70565',
                '84.102381',
                'outlet',
            ],
            'ZoneSelectionList': ['outlet'],
            'ZoneType': 'pressure-outlet',
        }
    )
    meshing.workflow.TaskObject['Enclose Fluid Regions (Capping)'].AddChildToTask()

    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].InsertCompoundChildTask()
    meshing.workflow.TaskObject[
        'Enclose Fluid Regions (Capping)'
    ].Arguments.setState({})
    meshing.workflow.TaskObject['outlet-1'].Execute()

Extract edge features
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Extract Edge Features'].Arguments.setState(
        {
            'ExtractMethodType': 'Intersection Loops',
            'ObjectSelectionList': ['flow_pipe', 'main'],
        }
    )
    meshing.workflow.TaskObject['Extract Edge Features'].AddChildToTask()

    meshing.workflow.TaskObject['Extract Edge Features'].InsertCompoundChildTask()

    meshing.workflow.TaskObject['edge-group-1'].Arguments.setState(
        {
            'ExtractEdgesName': 'edge-group-1',
            'ExtractMethodType': 'Intersection Loops',
            'ObjectSelectionList': ['flow_pipe', 'main'],
        }
    )
    meshing.workflow.TaskObject['Extract Edge Features'].Arguments.setState({})

    meshing.workflow.TaskObject['edge-group-1'].Execute()

Identify regions
~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Identify Regions'].Arguments.setState(
        {
            'SelectionType': 'zone',
            'X': 377.322045740589,
            'Y': -176.800676988458,
            'Z': -37.0764628583475,
            'ZoneSelectionList': ['main.1'],
        }
    )
    meshing.workflow.TaskObject['Identify Regions'].Arguments.setState(
        {
            'SelectionType': 'zone',
            'X': 377.322045740589,
                'Y': -176.800676988458,
            'Z': -37.0764628583475,
            'ZoneLocation': [
                '1',
                '213.32205',
                '-225.28068',
                '-158.25531',
                '541.32205',
                '-128.32068',
                '84.102381',
                'main.1',
            ],
            'ZoneSelectionList': ['main.1'],
        }
    )
    meshing.workflow.TaskObject['Identify Regions'].AddChildToTask()

    meshing.workflow.TaskObject['Identify Regions'].InsertCompoundChildTask()

    meshing.workflow.TaskObject['fluid-region-1'].Arguments.setState(
        {
            'MaterialPointsName': 'fluid-region-1',
            'SelectionType': 'zone',
            'X': 377.322045740589,
            'Y': -176.800676988458,
            'Z': -37.0764628583475,
            'ZoneLocation': [
                '1',
                '213.32205',
                '-225.28068',
                '-158.25531',
                '541.32205',
                '-128.32068',
                '84.102381',
                'main.1',
            ],
            'ZoneSelectionList': ['main.1'],
        }
    )
    meshing.workflow.TaskObject['Identify Regions'].Arguments.setState({})

    meshing.workflow.TaskObject['fluid-region-1'].Execute()
    meshing.workflow.TaskObject['Identify Regions'].Arguments.setState(
        {
            'MaterialPointsName': 'void-region-1',
            'NewRegionType': 'void',
            'ObjectSelectionList': ['inlet-1', 'inlet-2', 'inlet-3', 'main'],
            'X': 374.722045740589,
            'Y': -278.9775145640143,
            'Z': -161.1700719416913,
        }
    )
    meshing.workflow.TaskObject['Identify Regions'].AddChildToTask()

    meshing.workflow.TaskObject['Identify Regions'].InsertCompoundChildTask()

    meshing.workflow.TaskObject['Identify Regions'].Arguments.setState({})

    meshing.workflow.TaskObject['void-region-1'].Execute()

Define leakage threshold
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Define Leakage Threshold'].Arguments.setState(
        {
            'AddChild': 'yes',
            'FlipDirection': True,
            'PlaneDirection': 'X',
            'RegionSelectionSingle': 'void-region-1',
        }
    )
    meshing.workflow.TaskObject['Define Leakage Threshold'].AddChildToTask()

    meshing.workflow.TaskObject[
        'Define Leakage Threshold'
    ].InsertCompoundChildTask()
    meshing.workflow.TaskObject['leakage-1'].Arguments.setState(
        {
            'AddChild': 'yes',
            'FlipDirection': True,
            'LeakageName': 'leakage-1',
            'PlaneDirection': 'X',
            'RegionSelectionSingle': 'void-region-1',
        }
    )
    meshing.workflow.TaskObject['Define Leakage Threshold'].Arguments.setState(
        {
            'AddChild': 'yes',
        }
    )
    meshing.workflow.TaskObject['leakage-1'].Execute()

Update regions settings
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Update Region Settings'].Arguments.setState(
        {
            'AllRegionFilterCategories': ['2'] * 5 + ['1'] * 2,
            'AllRegionLeakageSizeList': ['none'] * 6 + ['6.4'],
            'AllRegionLinkedConstructionSurfaceList': ['n/a'] * 6 + ['no'],
            'AllRegionMeshMethodList': ['none'] * 6 + ['wrap'],
            'AllRegionNameList': [
                'main',
                'flow_pipe',
                'outpipe3',
                'object2',
                'object1',
                'void-region-1',
                'fluid-region-1',
            ],
            'AllRegionOversetComponenList': ['no'] * 7,
            'AllRegionSourceList': ['object'] * 5 + ['mpt'] * 2,
            'AllRegionTypeList': ['void'] * 6 + ['fluid'],
            'AllRegionVolumeFillList': ['none'] * 6 + ['tet'],
            'FilterCategory': 'Identified Regions',
            'OldRegionLeakageSizeList': [''],
            'OldRegionMeshMethodList': ['wrap'],
            'OldRegionNameList': ['fluid-region-1'],
            'OldRegionOversetComponenList': ['no'],
            'OldRegionTypeList': ['fluid'],
            'OldRegionVolumeFillList': ['hexcore'],
            'RegionLeakageSizeList': [''],
            'RegionMeshMethodList': ['wrap'],
            'RegionNameList': ['fluid-region-1'],
            'RegionOversetComponenList': ['no'],
            'RegionTypeList': ['fluid'],
            'RegionVolumeFillList': ['tet'],
        }
    )
    meshing.workflow.TaskObject['Update Region Settings'].Execute()


Choose mesh control options
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Choose Mesh Control Options'].Execute()

Generating surface mesh
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Generate the Surface Mesh'].Execute()

Update boundaries
~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Update Boundaries'].Execute()

Add boundary layers
~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Add Boundary Layers'].AddChildToTask()

    meshing.workflow.TaskObject['Add Boundary Layers'].InsertCompoundChildTask()

    meshing.workflow.TaskObject['aspect-ratio_1'].Arguments.setState(
        {
            'BLControlName': 'aspect-ratio_1',
        }
    )
    meshing.workflow.TaskObject['Add Boundary Layers'].Arguments.setState({})

    meshing.workflow.TaskObject['aspect-ratio_1'].Execute()

Generate volume mesh
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    meshing.workflow.TaskObject['Generate the Volume Mesh'].Arguments.setState(
        {
            'AllRegionNameList': [
                'main',
                'flow_pipe',
                'outpipe3',
                'object2',
                'object1',
                'void-region-1',
                'fluid-region-1',
            ],
            'AllRegionSizeList': ['11.33375'] * 7,
            'AllRegionVolumeFillList': ['none'] * 6 + ['tet'],
            'EnableParallel': True,
        }
    )
    meshing.workflow.TaskObject['Generate the Volume Mesh'].Execute()

Switch to solution mode
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    solver = meshing.switch_to_solver()