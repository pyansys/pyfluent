"""Meshing workflow specialization of the Workflow module that wraps and extends the
core functionality."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from ansys.fluent.core.services.datamodel_se import PyMenuGeneric
from ansys.fluent.core.utils.fluent_version import FluentVersion
from ansys.fluent.core.workflow import ClassicWorkflow, Workflow


class ClassicMeshingWorkflow(ClassicWorkflow):
    """Provides meshing specialization of the workflow wrapper."""

    def __init__(
        self,
        workflow: PyMenuGeneric,
        meshing: PyMenuGeneric,
        fluent_version: FluentVersion,
    ) -> None:
        """Initialize ClassicMeshingWorkflow.

        Parameters
        ----------
        workflow : PyMenuGeneric
            Underlying workflow object.
        meshing : PyMenuGeneric
            Meshing object.
        fluent_version: FluentVersion
            Version information of the current fluent session.
        """
        super().__init__(
            workflow=workflow, command_source=meshing, fluent_version=fluent_version
        )


class MeshingWorkflow(Workflow):
    """Provides meshing specialization of the workflow wrapper that extends the core
    functionality in an object-oriented manner."""

    def __init__(
        self,
        workflow: PyMenuGeneric,
        meshing: PyMenuGeneric,
        name: str,
        identifier: str,
        fluent_version: FluentVersion,
    ) -> None:
        """Initialize MeshingWorkflow.

        Parameters
        ----------
        workflow : PyMenuGeneric
            Underlying workflow object.
        meshing : PyMenuGeneric
            Meshing object.
        name: str
            Workflow name to initialize it.
        identifier: str
            Workflow name to identify it from global settings.
        fluent_version: FluentVersion
            Version information of the current fluent session.
        """
        super().__init__(
            workflow=workflow, command_source=meshing, fluent_version=fluent_version
        )
        self._meshing = meshing
        self._name = name
        self._identifier = identifier

    def reinitialize(self) -> None:
        """Initialize a workflow."""
        self._new_workflow(name=self._name)

    def __getattribute__(self, item: str):
        if (
            item != "reinitialize"
            and not item.startswith("_")
            and not getattr(self._meshing.GlobalSettings, self._identifier)()
        ):
            raise RuntimeError(
                f"'{self._name}' objects are inaccessible from other workflows."
            )
        return super().__getattribute__(item)


class WatertightMeshingWorkflow(MeshingWorkflow):
    """Provides watertight meshing specialization of the workflow wrapper."""

    def __init__(
        self,
        workflow: PyMenuGeneric,
        meshing: PyMenuGeneric,
        fluent_version: FluentVersion,
    ) -> None:
        """Initialize WatertightMeshingWorkflow.

        Parameters
        ----------
        workflow : PyMenuGeneric
            The underlying workflow object.
        meshing : PyMenuGeneric
            The meshing object.
        fluent_version: FluentVersion
            Version information of the current fluent session.
        """
        super().__init__(
            workflow=workflow,
            meshing=meshing,
            name="Watertight Geometry",
            identifier="EnableCleanCAD",
            fluent_version=fluent_version,
        )


class FaultTolerantMeshingWorkflow(MeshingWorkflow):
    """Provides fault-tolerant meshing specialization of the workflow wrapper."""

    def __init__(
        self,
        workflow: PyMenuGeneric,
        meshing: PyMenuGeneric,
        part_management: PyMenuGeneric,
        pm_file_management: PyMenuGeneric,
        fluent_version: FluentVersion,
    ) -> None:
        """Initialize FaultTolerantMeshingWorkflow.

        Parameters
        ----------
        workflow : PyMenuGeneric
            The underlying workflow object.
        meshing : PyMenuGeneric
            The meshing object.
        part_management : PyMenuGeneric
            The part-management object.
        pm_file_management : PyMenuGeneric
            The part-management file-management object.
        fluent_version: FluentVersion
            Version information of the current fluent session.
        """
        super().__init__(
            workflow=workflow,
            meshing=meshing,
            name="Fault-tolerant Meshing",
            identifier="EnableComplexMeshing",
            fluent_version=fluent_version,
        )
        self._part_management = part_management
        self._pm_file_management = pm_file_management

    @property
    def part_management(self) -> Optional[PyMenuGeneric]:
        """Access part-management in fault-tolerant mode.

        Returns
        -------
        Optional[PyMenuGeneric]
            Part-management.
        """
        return self._part_management

    @property
    def pm_file_management(self):
        """Access the part-management file-management object in fault-tolerant mode.

        Returns
        -------
        Optional[PyMenuGeneric]
            Part-management file-management object .
        """
        return self._pm_file_management


class TwoDimensionalMeshingWorkflow(MeshingWorkflow):
    """Provides 2D meshing specialization of the workflow wrapper."""

    def __init__(
        self,
        workflow: PyMenuGeneric,
        meshing: PyMenuGeneric,
        fluent_version: FluentVersion,
    ) -> None:
        """Initialize TwoDimensionalMeshingWorkflow.

        Parameters
        ----------
        workflow : PyMenuGeneric
            The underlying workflow object.
        meshing : PyMenuGeneric
            The meshing object.
        fluent_version: FluentVersion
            Version information of the current fluent session.
        """
        super().__init__(
            workflow=workflow,
            meshing=meshing,
            name="2D Meshing",
            identifier="EnablePrime2dMeshing",
            fluent_version=fluent_version,
        )


class TopologyBasedMeshingWorkflow(MeshingWorkflow):
    """Provides topology-based meshing specialization of the workflow wrapper."""

    def __init__(
        self,
        workflow: PyMenuGeneric,
        meshing: PyMenuGeneric,
        fluent_version: FluentVersion,
    ) -> None:
        """Initialize TopologyBasedMeshingWorkflow.

        Parameters
        ----------
        workflow : PyMenuGeneric
            The underlying workflow object.
        meshing : PyMenuGeneric
            The meshing object.
        fluent_version: FluentVersion
            Version information of the current fluent session.
        """
        super().__init__(
            workflow=workflow,
            meshing=meshing,
            name="Topology Based Meshing",
            identifier="EnablePrimeMeshing",
            fluent_version=fluent_version,
        )


class WorkflowMode(Enum):
    """Enumerates over supported Fluent meshing workflow modes."""

    CLASSIC_MESHING_MODE = ClassicMeshingWorkflow
    WATERTIGHT_MESHING_MODE = WatertightMeshingWorkflow
    FAULT_TOLERANT_MESHING_MODE = FaultTolerantMeshingWorkflow
    TWO_DIMENSIONAL_MESHING_MODE = TwoDimensionalMeshingWorkflow
    TOPOLOGY_BASED_MESHING_MODE = TopologyBasedMeshingWorkflow
