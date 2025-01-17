"""Wrappers over FieldData gRPC service of Fluent."""

from dataclasses import dataclass, field
from enum import Enum
from functools import reduce
import logging
import time
from typing import Callable, Dict, List, Tuple
import weakref

import grpc
import numpy as np

from ansys.api.fluent.v0 import field_data_pb2 as FieldDataProtoModule
from ansys.api.fluent.v0 import field_data_pb2_grpc as FieldGrpcModule
from ansys.fluent.core.exceptions import DisallowedValuesError
from ansys.fluent.core.services.interceptors import (
    BatchInterceptor,
    ErrorStateInterceptor,
    GrpcErrorInterceptor,
    TracingInterceptor,
)
from ansys.fluent.core.services.streaming import StreamingService
from ansys.fluent.core.utils.deprecate import deprecate_argument, deprecate_arguments

logger = logging.getLogger("pyfluent.field_data")


def override_help_text(func, func_to_be_wrapped):
    """Override function help text."""
    if func_to_be_wrapped.__doc__:
        func.__doc__ = "\n" + func_to_be_wrapped.__doc__
    func.__name__ = func_to_be_wrapped.__qualname__
    return func


# this can be switched to False in scenarios where the field_data request inputs are
# fed by results of field_info queries, which might be true in GUI code.
validate_inputs = True


class FieldDataService(StreamingService):
    """FieldData service of Fluent."""

    def __init__(
        self, channel: grpc.Channel, metadata: List[Tuple[str, str]], fluent_error_state
    ):
        """__init__ method of FieldDataService class."""
        intercept_channel = grpc.intercept_channel(
            channel,
            GrpcErrorInterceptor(),
            ErrorStateInterceptor(fluent_error_state),
            TracingInterceptor(),
            BatchInterceptor(),
        )
        super().__init__(
            stub=FieldGrpcModule.FieldDataStub(intercept_channel), metadata=metadata
        )

    def get_scalar_field_range(self, request):
        """GetRange RPC of FieldData service."""
        return self._stub.GetRange(request, metadata=self._metadata)

    def get_scalar_fields_info(self, request):
        """GetFieldsInfo RPC of FieldData service."""
        return self._stub.GetFieldsInfo(request, metadata=self._metadata)

    def get_vector_fields_info(self, request):
        """GetVectorFieldsInfo RPC of FieldData service."""
        return self._stub.GetVectorFieldsInfo(request, metadata=self._metadata)

    def get_surfaces_info(self, request):
        """GetSurfacesInfo RPC of FieldData service."""
        return self._stub.GetSurfacesInfo(request, metadata=self._metadata)

    def get_fields(self, request):
        """GetFields RPC of FieldData service.

        Raises
        ------
        RuntimeError
            If an empty chunk encountered during field extraction.
        """
        chunk_iterator = self._stub.GetFields(request, metadata=self._metadata)
        if not chunk_iterator.is_active():
            raise RuntimeError(
                "Unexpectedly encountered empty chunk during field extraction."
            )
        return chunk_iterator

    def get_solver_mesh_nodes(
        self, request: FieldDataProtoModule.GetSolverMeshNodesRequest
    ):
        """GetSolverMeshNodesDouble RPC of FieldData service."""
        responses = self._stub.GetSolverMeshNodesDouble(
            request, metadata=self._metadata
        )
        nested_nodes = []
        for response in responses:
            nested_nodes.append(response.nodes)
        return nested_nodes

    def get_solver_mesh_elements(
        self, request: FieldDataProtoModule.GetSolverMeshElementsRequest
    ):
        """GetSolverMeshElements RPC of FieldData service."""
        responses = self._stub.GetSolverMeshElements(request, metadata=self._metadata)
        elementss = []
        for response in responses:
            elementss.append(response.elements)
        return elementss


class FieldInfo:
    """Provides access to Fluent field information.

    Methods
    -------
    get_scalar_field_range(field: str, node_value: bool, surface_ids: List[int])
    -> List[float]
        Get the range (minimum and maximum values) of the field.

    get_scalar_fields_info(self) -> dict
        Get fields information (field name, domain, and section).

    get_vector_fields_info(self) -> dict
        Get vector fields information.

    get_surfaces_info(self) -> dict
        Get surfaces information (surface name, ID, and type).
    """

    def __init__(
        self,
        service: FieldDataService,
        is_data_valid: Callable[[], bool],
    ):
        """__init__ method of FieldInfo class."""
        self._service = service
        self._is_data_valid = is_data_valid

    def get_scalar_field_range(
        self, field: str, node_value: bool = False, surface_ids: List[int] = None
    ) -> List[float]:
        """Get the range (minimum and maximum values) of the field.

        Parameters
        ----------
        field: str
            Field name
        node_value: bool
        surface_ids : List[int], optional
            List of surface IDS for the surface data.

        Returns
        -------
        List[float]
        """
        if not surface_ids:
            surface_ids = []
        request = FieldDataProtoModule.GetRangeRequest()
        request.fieldName = field
        request.nodeValue = node_value
        request.surfaceid.extend(
            [FieldDataProtoModule.SurfaceId(id=int(id)) for id in surface_ids]
        )
        response = self._service.get_scalar_field_range(request)
        return [response.minimum, response.maximum]

    def get_scalar_fields_info(self) -> Dict[str, Dict]:
        """Get fields information (field name, domain, and section).

        Returns
        -------
        Dict
        """
        request = FieldDataProtoModule.GetFieldsInfoRequest()
        response = self._service.get_scalar_fields_info(request)
        return {
            field_info.solverName: {
                "display_name": field_info.displayName,
                "section": field_info.section,
                "domain": field_info.domain,
                "quantity_name": field_info.quantity_name,
            }
            for field_info in response.fieldInfo
        }

    def get_vector_fields_info(self) -> Dict[str, Dict]:
        """Get vector fields information (vector components).

        Returns
        -------
        Dict
        """
        request = FieldDataProtoModule.GetVectorFieldsInfoRequest()
        response = self._service.get_vector_fields_info(request)
        return {
            vector_field_info.displayName: {
                "x-component": vector_field_info.xComponent,
                "y-component": vector_field_info.yComponent,
                "z-component": vector_field_info.zComponent,
            }
            for vector_field_info in response.vectorFieldInfo
        }

    def get_surfaces_info(self) -> Dict[str, Dict]:
        """Get surfaces information (surface name, ID, and type).

        Returns
        -------
        Dict
        """
        request = FieldDataProtoModule.GetSurfacesInfoResponse()
        response = self._service.get_surfaces_info(request)
        info = {
            surface_info.surfaceName: {
                "surface_id": [surf.id for surf in surface_info.surfaceId],
                "zone_id": surface_info.zoneId.id,
                "zone_type": surface_info.zoneType,
                "type": surface_info.type,
            }
            for surface_info in response.surfaceInfo
        }
        return info

    def validate_scalar_fields(self, field_name: str):
        """Validate scalar fields."""
        _AllowedScalarFieldNames(
            self._is_data_valid, info=self.get_scalar_fields_info()
        ).valid_name(field_name)

    def validate_vector_fields(self, field_name: str):
        """Validate vector fields."""
        _AllowedVectorFieldNames(
            self._is_data_valid, info=self.get_vector_fields_info()
        ).valid_name(field_name)

    def validate_surfaces(self, surfaces: List[str]):
        """Validate surfaces."""
        for surface in surfaces:
            _AllowedSurfaceNames(info=self.get_surfaces_info()).valid_name(surface)


class FieldUnavailable(RuntimeError):
    """Raised when field is unavailable."""

    pass


class SurfaceDataType(Enum):
    """Provides surface data types."""

    Vertices = "vertices"
    FacesConnectivity = "faces"
    FacesNormal = "face-normal"
    FacesCentroid = "centroid"


class _AllowedNames:
    def __init__(self, field_info: FieldInfo | None = None, info: dict | None = None):
        self._field_info = field_info
        self._info = info

    def is_valid(self, name, respect_data_valid=True):
        """Checks validity."""
        return name in self(respect_data_valid)


class _AllowedFieldNames(_AllowedNames):
    def __init__(
        self,
        is_data_valid: Callable[[], bool],
        field_info: FieldInfo | None = None,
        info: dict | None = None,
    ):
        super().__init__(field_info=field_info, info=info)
        self._is_data_valid = is_data_valid

    def valid_name(self, field_name):
        """Returns valid names."""
        if validate_inputs:
            names = self
            if not names.is_valid(field_name, respect_data_valid=False):
                raise self._field_name_error(
                    context="field",
                    name=field_name,
                    allowed_values=list(names(respect_data_valid=False).keys()),
                )
            if not names.is_valid(field_name, respect_data_valid=True):
                raise self._field_unavailable_error(
                    f"{field_name} is not a currently available field."
                )
        return field_name


class _AllowedSurfaceNames(_AllowedNames):
    def __call__(self, respect_data_valid: bool = True) -> List[str]:
        return self._info if self._info else self._field_info.get_surfaces_info()

    def valid_name(self, surface_name: str) -> str:
        """Returns valid names.

        Raises
        ------
        DisallowedValuesError
            If surface name is invalid.
        """
        if validate_inputs and not self.is_valid(surface_name):
            raise DisallowedValuesError("surface", surface_name, self())
        return surface_name


class _AllowedSurfaceIDs(_AllowedNames):
    def __call__(self, respect_data_valid: bool = True) -> List[int]:
        try:
            return [
                info["surface_id"][0]
                for _, info in self._field_info.get_surfaces_info().items()
            ]
        except (KeyError, IndexError):
            pass


class _AllowedScalarFieldNames(_AllowedFieldNames):
    _field_name_error = DisallowedValuesError
    _field_unavailable_error = FieldUnavailable

    def __call__(self, respect_data_valid: bool = True) -> List[str]:
        field_dict = (
            self._info if self._info else self._field_info.get_scalar_fields_info()
        )
        return (
            field_dict
            if (not respect_data_valid or self._is_data_valid())
            else [
                name
                for name, info in field_dict.items()
                if info["section"] in ("Mesh...", "Cell Info...")
            ]
        )


class _AllowedVectorFieldNames(_AllowedFieldNames):
    _field_name_error = DisallowedValuesError
    _field_unavailable_error = FieldUnavailable

    def __call__(self, respect_data_valid: bool = True) -> List[str]:
        return (
            self._info
            if self._info
            else (
                self._field_info.get_vector_fields_info()
                if (not respect_data_valid or self._is_data_valid())
                else []
            )
        )

    def is_valid(self, name, respect_data_valid=True):
        """Checks validity."""
        return name in self(respect_data_valid)


class _FieldMethod:
    class _Arg:
        def __init__(self, accessor):
            self._accessor = accessor

        def allowed_values(self):
            """Returns set of allowed values."""
            return sorted(self._accessor())

    def __init__(self, field_data_accessor, args_allowed_values_accessors):
        self._field_data_accessor = field_data_accessor
        for arg_name, accessor in args_allowed_values_accessors.items():
            setattr(self, arg_name, _FieldMethod._Arg(accessor))

    def __call__(self, *args, **kwargs):
        return self._field_data_accessor(*args, **kwargs)


def _data_type_convertor(args_dict):
    d_type_list = []
    d_type_map = {
        "provide_vertices": SurfaceDataType.Vertices,
        "provide_faces": SurfaceDataType.FacesConnectivity,
        "provide_faces_centroid": SurfaceDataType.FacesCentroid,
        "provide_faces_normal": SurfaceDataType.FacesNormal,
    }
    for key, val in d_type_map.items():
        if args_dict.get(key):
            d_type_list.append(val)
        args_dict.pop(key, None)
    if args_dict.get("data_types") is None:
        args_dict["data_types"] = d_type_list
    return args_dict


class FieldTransaction:
    """Populates Fluent field data on surfaces."""

    def __init__(
        self,
        service: FieldDataService,
        field_info: FieldInfo,
        allowed_surface_ids,
        allowed_surface_names,
        allowed_scalar_field_names,
        allowed_vector_field_names,
    ):
        """__init__ method of FieldTransaction class."""
        self._service = service
        self._field_info = field_info
        self._fields_request = get_fields_request()

        self._allowed_surface_names = allowed_surface_names
        self._allowed_scalar_field_names = allowed_scalar_field_names
        self._allowed_vector_field_names = allowed_vector_field_names

        surface_args = dict(
            surface_ids=allowed_surface_ids,
            surface_names=self._allowed_surface_names,
        )
        scalar_field_args = {
            **dict(field_name=self._allowed_scalar_field_names),
            **surface_args,
        }
        self.add_scalar_fields_request = override_help_text(
            _FieldMethod(
                field_data_accessor=self.add_scalar_fields_request,
                args_allowed_values_accessors=scalar_field_args,
            ),
            self.add_scalar_fields_request,
        )
        self.add_vector_fields_request = override_help_text(
            _FieldMethod(
                field_data_accessor=self.add_vector_fields_request,
                args_allowed_values_accessors={
                    **dict(field_name=self._allowed_vector_field_names),
                    **surface_args,
                },
            ),
            self.add_vector_fields_request,
        )
        self.add_surfaces_request = override_help_text(
            _FieldMethod(
                field_data_accessor=self.add_surfaces_request,
                args_allowed_values_accessors=surface_args,
            ),
            self.add_surfaces_request,
        )
        self.add_pathlines_fields_request = override_help_text(
            _FieldMethod(
                field_data_accessor=self.add_pathlines_fields_request,
                args_allowed_values_accessors=scalar_field_args,
            ),
            self.add_pathlines_fields_request,
        )

    @deprecate_argument(
        old_arg="surface_names",
        new_arg="surfaces",
        converter=lambda old_arg_val: old_arg_val or [],
    )
    @deprecate_argument(
        old_arg="surface_ids",
        new_arg="surfaces",
        converter=lambda old_arg_val: old_arg_val or [],
    )
    @deprecate_arguments(converter=_data_type_convertor)
    def add_surfaces_request(
        self,
        data_types: List[SurfaceDataType] | List[str],
        surfaces: List[int | str],
        overset_mesh: bool | None = False,
    ) -> None:
        """Add request to get surface data (vertices, face connectivity, centroids, and
        normals).

        Parameters
        ----------
        data_types : List[SurfaceDataType] | List[str],
            SurfaceDataType Enum members.
        surfaces : List[int | str]
            List of surface IDS or surface names for the surface data.
        overset_mesh : bool, optional
            Whether to get the overset met. The default is ``False``.

        Returns
        -------
        None
        """
        surface_ids = _get_surface_ids(
            field_info=self._field_info,
            allowed_surface_names=self._allowed_surface_names,
            surfaces=surfaces,
        )
        updated_data_types = []
        for d_type in data_types:
            if isinstance(d_type, str):
                updated_data_types.append(SurfaceDataType(d_type))
            else:
                updated_data_types.append(d_type)
        data_types = updated_data_types
        self._fields_request.surfaceRequest.extend(
            [
                FieldDataProtoModule.SurfaceRequest(
                    surfaceId=surface_id,
                    oversetMesh=overset_mesh,
                    provideFaces=SurfaceDataType.FacesConnectivity in data_types,
                    provideVertices=SurfaceDataType.Vertices in data_types,
                    provideFacesCentroid=SurfaceDataType.FacesCentroid in data_types,
                    provideFacesNormal=SurfaceDataType.FacesNormal in data_types,
                )
                for surface_id in surface_ids
            ]
        )

    @deprecate_argument(
        old_arg="surface_names",
        new_arg="surfaces",
        converter=lambda old_arg_val: old_arg_val or [],
    )
    @deprecate_argument(
        old_arg="surface_ids",
        new_arg="surfaces",
        converter=lambda old_arg_val: old_arg_val or [],
    )
    def add_scalar_fields_request(
        self,
        field_name: str,
        surfaces: List[int | str],
        node_value: bool | None = True,
        boundary_value: bool | None = True,
    ) -> None:
        """Add request to get scalar field data on surfaces.

        Parameters
        ----------
        field_name : str
            Name of the scalar field.
        surfaces : List[int | str]
            List of surface IDS or surface names for the surface data.
        node_value : bool, optional
            Whether to provide the nodal location. The default is ``True``. If
            ``False``, the element location is provided.
        boundary_value : bool, optional
            Whether to provide the slip velocity at the wall boundaries. The default
            is ``True``. When ``True``, no slip velocity is provided.

        Returns
        -------
        None
        """
        surface_ids = _get_surface_ids(
            field_info=self._field_info,
            allowed_surface_names=self._allowed_surface_names,
            surfaces=surfaces,
        )
        self._fields_request.scalarFieldRequest.extend(
            [
                FieldDataProtoModule.ScalarFieldRequest(
                    surfaceId=surface_id,
                    scalarFieldName=self._allowed_scalar_field_names.valid_name(
                        field_name
                    ),
                    dataLocation=(
                        FieldDataProtoModule.DataLocation.Nodes
                        if node_value
                        else FieldDataProtoModule.DataLocation.Elements
                    ),
                    provideBoundaryValues=boundary_value,
                )
                for surface_id in surface_ids
            ]
        )

    @deprecate_argument(
        old_arg="surface_names",
        new_arg="surfaces",
        converter=lambda old_arg_val: old_arg_val or [],
    )
    @deprecate_argument(
        old_arg="surface_ids",
        new_arg="surfaces",
        converter=lambda old_arg_val: old_arg_val or [],
    )
    def add_vector_fields_request(
        self,
        field_name: str,
        surfaces: List[int | str],
    ) -> None:
        """Add request to get vector field data on surfaces.

        Parameters
        ----------
        field_name : str
            Name of the vector field.
        surfaces : List[int | str]
            List of surface IDS or surface names for the surface data.

        Returns
        -------
        None
        """
        surface_ids = _get_surface_ids(
            field_info=self._field_info,
            allowed_surface_names=self._allowed_surface_names,
            surfaces=surfaces,
        )
        self._fields_request.vectorFieldRequest.extend(
            [
                FieldDataProtoModule.VectorFieldRequest(
                    surfaceId=surface_id,
                    vectorFieldName=self._allowed_vector_field_names.valid_name(
                        field_name,
                    ),
                )
                for surface_id in surface_ids
            ]
        )

    @deprecate_argument(
        old_arg="surface_names",
        new_arg="surfaces",
        converter=lambda old_arg_val: old_arg_val or [],
    )
    @deprecate_argument(
        old_arg="surface_ids",
        new_arg="surfaces",
        converter=lambda old_arg_val: old_arg_val or [],
    )
    def add_pathlines_fields_request(
        self,
        field_name: str,
        surfaces: List[int | str],
        additional_field_name: str | None = "",
        provide_particle_time_field: bool | None = False,
        node_value: bool | None = True,
        steps: int | None = 500,
        step_size: float | None = 500,
        skip: int | None = 0,
        reverse: bool | None = False,
        accuracy_control_on: bool | None = False,
        tolerance: float | None = 0.001,
        coarsen: int | None = 1,
        velocity_domain: str | None = "all-phases",
        zones: list | None = None,
    ) -> None:
        """Add request to get pathlines field on surfaces.

        Parameters
        ----------
        field_name : str
            Name of the scalar field to color pathlines.
        surfaces : List[int | str]
            List of surface IDS or surface names for the surface data.
        additional_field_name : str, optional
            Additional field if required.
        provide_particle_time_field: bool, optional
            Whether to provide the particle time. The default is ``False``.
        node_value : bool, optional
                    Whether to provide the nodal values. The default is ``True``. If
                    ``False``, element values are provided.
        steps: int, optional
            Pathlines steps. The default is ``500``
        step_size: float, optional
            Pathlines step size. The default is ``0.01``.
        skip: int, optional
            Pathlines to skip. The default is ``0``.
        reverse: bool, optional
            Whether to draw pathlines in a reverse direction. The default is ``False``.
        accuracy_control_on: bool, optional
            Whether to control accuracy. The default is ``False``.
        tolerance: float, optional
            Pathlines tolerance. The default is ``0.001``.
        coarsen: int, optional
            Pathlines coarsen. The default is ``1``.
        velocity_domain: str, optional
            Domain for pathlines. The default is ``"all-phases"``.
        zones: list, optional
            Zones for pathlines. The default is ``[]``.
        Returns
        -------
        None
        """
        if zones is None:
            zones = []
        surface_ids = _get_surface_ids(
            field_info=self._field_info,
            allowed_surface_names=self._allowed_surface_names,
            surfaces=surfaces,
        )
        self._fields_request.pathlinesFieldRequest.extend(
            [
                FieldDataProtoModule.PathlinesFieldRequest(
                    surfaceId=surface_id,
                    field=field_name,
                    additionalField=additional_field_name,
                    provideParticleTimeField=provide_particle_time_field,
                    dataLocation=(
                        FieldDataProtoModule.DataLocation.Nodes
                        if node_value
                        else FieldDataProtoModule.DataLocation.Elements
                    ),
                    steps=steps,
                    stepSize=step_size,
                    skip=skip,
                    reverse=reverse,
                    accuracyControlOn=accuracy_control_on,
                    tolerance=tolerance,
                    coarsen=coarsen,
                    velocityDomain=velocity_domain,
                    zones=zones,
                )
                for surface_id in surface_ids
            ]
        )

    def get_fields(self) -> Dict[int | Tuple, Dict[int, Dict[str, np.array]]]:
        """Get data for previously added requests and then clear all requests.

        Returns
        -------
        Dict[int, Dict[int, Dict[str, np.array]]]
            Data is returned as dictionary of dictionaries in the following structure:
            tag int | Tuple-> surface_id [int] -> field_name [str] -> field_data[np.array]

            The tag is a tuple for Fluent 2023 R1 or later.
        """
        return ChunkParser().extract_fields(
            self._service.get_fields(self._fields_request)
        )

    def __call__(self):
        self.get_fields()


class _FieldDataConstants:
    """Defines constants for Fluent field data."""

    # data mapping
    proto_field_type_to_np_data_type = {
        FieldDataProtoModule.FieldType.INT_ARRAY: np.int32,
        FieldDataProtoModule.FieldType.LONG_ARRAY: np.int64,
        FieldDataProtoModule.FieldType.FLOAT_ARRAY: np.float32,
        FieldDataProtoModule.FieldType.DOUBLE_ARRAY: np.float64,
    }
    np_data_type_to_proto_field_type = {
        np.int32: FieldDataProtoModule.FieldType.INT_ARRAY,
        np.int64: FieldDataProtoModule.FieldType.LONG_ARRAY,
        np.float32: FieldDataProtoModule.FieldType.FLOAT_ARRAY,
        np.float64: FieldDataProtoModule.FieldType.DOUBLE_ARRAY,
    }
    chunk_size = 256 * 1024
    bytes_stream = True
    payloadTags = {
        FieldDataProtoModule.PayloadTag.OVERSET_MESH: 1,
        FieldDataProtoModule.PayloadTag.ELEMENT_LOCATION: 2,
        FieldDataProtoModule.PayloadTag.NODE_LOCATION: 4,
        FieldDataProtoModule.PayloadTag.BOUNDARY_VALUES: 8,
    }


def _get_surface_ids(
    field_info: FieldInfo,
    allowed_surface_names,
    surfaces: List[int | str],
) -> List[int]:
    """Get surface IDs based on surface names or IDs.

    Parameters
    ----------
    surfaces : List[int] | List[str]
        List of surface IDs or surface names.

    Returns
    -------
    List[int]
    """
    surface_ids = []
    for surf in surfaces:
        if isinstance(surf, str):
            surface_ids.extend(
                field_info.get_surfaces_info()[allowed_surface_names.valid_name(surf)][
                    "surface_id"
                ]
            )
        else:
            surface_ids.append(surf)
    return surface_ids


def get_fields_request():
    """Populates a new field request."""
    return FieldDataProtoModule.GetFieldsRequest(
        provideBytesStream=_FieldDataConstants.bytes_stream,
        chunkSize=_FieldDataConstants.chunk_size,
    )


class ChunkParser:
    """Class for parsing field data stream received from Fluent.

    Parameters
    ----------
    callbacks_provider : object
    The object which can register and unregister callbacks.
    It provides callbacks, which are triggered with following arguments:
        zone_id : int

        field_name : str

        field : numpy array
    """

    def __init__(self, callbacks_provider: object = None):
        """__init__ method of ChunkParser class."""
        self._callbacks_provider = callbacks_provider

    def extract_fields(self, chunk_iterator) -> Dict[int, Dict[str, np.array]]:
        """Extracts field data received from Fluent.

        if callbacks_provider is set then callbacks are triggered with extracted data.
        """

        def _get_tag_for_surface_request():
            return (("type", "surface-data"),)

        def _get_tag_for_vector_field_request():
            return (("type", "vector-field"),)

        def _get_tag_for_scalar_field_request(scalar_field_request):
            return (
                ("type", "scalar-field"),
                ("dataLocation", scalar_field_request.dataLocation),
                ("boundaryValues", scalar_field_request.provideBoundaryValues),
            )

        def _get_tag_for_pathlines_field_request(pathlines_field_request):
            return (
                ("type", "pathlines-field"),
                ("field", pathlines_field_request.field),
            )

        def _extract_field(field_datatype, field_size, chunk_iterator):
            field_arr = np.empty(field_size, dtype=field_datatype)
            field_datatype_item_size = np.dtype(field_datatype).itemsize
            index = 0
            for chunk in chunk_iterator:
                if chunk.bytePayload:
                    count = min(
                        len(chunk.bytePayload) // field_datatype_item_size,
                        field_size - index,
                    )
                    field_arr[index : index + count] = np.frombuffer(
                        chunk.bytePayload, field_datatype, count=count
                    )
                    index += count
                    if index == field_size:
                        return field_arr
                else:
                    payload = (
                        chunk.floatPayload.payload
                        or chunk.intPayload.payload
                        or chunk.doublePayload.payload
                        or chunk.longPayload.payload
                    )
                    count = len(payload)
                    field_arr[index : index + count] = np.fromiter(
                        payload, dtype=field_datatype
                    )
                    index += count
                    if index == field_size:
                        return field_arr

        fields_data = {}
        for chunk in chunk_iterator:
            payload_info = chunk.payloadInfo
            surface_id = payload_info.surfaceId
            field_request_info = payload_info.fieldRequestInfo
            request_type = field_request_info.WhichOneof("request")
            if request_type is not None:
                payload_tag_id = (
                    _get_tag_for_surface_request()
                    if request_type == "surfaceRequest"
                    else (
                        _get_tag_for_scalar_field_request(
                            field_request_info.scalarFieldRequest
                        )
                        if request_type == "scalarFieldRequest"
                        else (
                            _get_tag_for_vector_field_request()
                            if request_type == "vectorFieldRequest"
                            else (
                                _get_tag_for_pathlines_field_request(
                                    field_request_info.pathlinesFieldRequest
                                )
                                if request_type == "pathlinesFieldRequest"
                                else None
                            )
                        )
                    )
                )
            else:
                if self._callbacks_provider is None:
                    payload_tag_id = reduce(
                        lambda x, y: x | y,
                        [
                            _FieldDataConstants.payloadTags[tag]
                            for tag in payload_info.payloadTag
                        ]
                        or [0],
                    )
                else:
                    payload_tag_id = None
            field = None
            if payload_tag_id is not None:
                field = _extract_field(
                    _FieldDataConstants.proto_field_type_to_np_data_type[
                        payload_info.fieldType
                    ],
                    payload_info.fieldSize,
                    chunk_iterator,
                )

            if self._callbacks_provider is not None:
                for callback_data in self._callbacks_provider.callbacks():
                    callback, args, kwargs = callback_data
                    # print('cb', surface_id, payload_info.fieldName)
                    callback(surface_id, payload_info.fieldName, field, *args, **kwargs)
            else:
                payload_data = fields_data.get(payload_tag_id)
                if not payload_data:
                    payload_data = fields_data[payload_tag_id] = {}
                surface_data = payload_data.get(surface_id)
                if surface_data:
                    if payload_info.fieldName in surface_data:
                        surface_data.update(
                            {
                                payload_info.fieldName: np.concatenate(
                                    (surface_data[payload_info.fieldName], field)
                                )
                            }
                        )
                    else:
                        surface_data.update({payload_info.fieldName: field})
                else:
                    payload_data[surface_id] = {payload_info.fieldName: field}
        return fields_data


# Root domain id in Fluent.
ROOT_DOMAIN_ID = 1


class ZoneType(Enum):
    """Zone types for mesh."""

    CELL = 1
    FACE = 2


@dataclass
class ZoneInfo:
    """Zone information for mesh.

    Attributes:
    -----------
    _id : int
        Zone ID.
    name : str
        Name of the zone.
    zone_type : ZoneType
        Type of the zone for mesh.
    """

    _id: int
    name: str
    zone_type: ZoneType


@dataclass
class Node:
    """Node class for mesh.

    Attributes:
    -----------
    x : float
        x-coordinate of the node.
    y : float
        y-coordinate of the node.
    z : float
        z-coordinate of the node.
    """

    _id: int
    x: float
    y: float
    z: float


class CellElementType(Enum):
    """Element types for a cell element."""

    # 3 nodes, 3 faces
    TRIANGLE = 1
    # 4 nodes, 4 faces
    TETRAHEDRON = 2
    # 4 nodes, 4 faces
    QUADRILATERAL = 3
    # 8 nodes, 6 faces
    HEXAHEDRON = 4
    # 5 nodes, 5 faces
    PYRAMID = 5
    # 6 nodes, 5 faces
    WEDGE = 6
    # Arbitrary number of nodes and faces
    POLYHEDRON = 7
    # 2 nodes, 1 face (only in 2D)
    GHOST = 8
    # 10 nodes, 4 faces
    QUADRATIC_TETRAHEDRON = 9
    # 20 nodes, 6 faces
    QUADRATIC_HEXAHEDRON = 10
    # 13 nodes, 5 faces
    QUADRATIC_PYRAMID = 11
    # 15 nodes, 5 faces
    QUADRATIC_WEDGE = 12


@dataclass
class Facet:
    """Facet class within a mesh element.

    Attributes:
    -----------
    node_indices : list[int]
        0-based node indices of the facet.
    """

    node_indices: list[int]


@dataclass
class Element:
    """Element class for mesh.

    Attributes:
    -----------
    element_type : CellElementType
        Element type of the element.
    node_indices : list[int]
        0-based node indices of the element. Populated for standard elements.
    facets : list[Facet]
        List of facets of the element. Populated for polyhedral elements.
    """

    _id: int
    element_type: CellElementType
    node_indices: list[int] = field(default_factory=list)
    facets: list[Facet] = field(default_factory=list)


@dataclass
class Mesh:
    """Mesh class for Fluent field data.

    Attributes:
    -----------
    nodes : list[Node]
        List of nodes in the mesh.
    elements : list[Element]
        List of elements in the mesh.
    """

    nodes: list[Node]
    elements: list[Element]


class FieldData:
    """Provides access to Fluent field data on surfaces."""

    def __init__(
        self,
        service: FieldDataService,
        field_info: FieldInfo,
        is_data_valid: Callable[[], bool],
        scheme_eval=None,
        get_zones_info: weakref.WeakMethod[Callable[[], list[ZoneInfo]]] | None = None,
    ):
        """__init__ method of FieldData class."""
        self._service = service
        self._field_info = field_info
        self.is_data_valid = is_data_valid
        self.scheme_eval = scheme_eval
        self.get_zones_info = lambda: get_zones_info()()

        self._allowed_surface_names = _AllowedSurfaceNames(field_info)

        self._allowed_surface_ids = _AllowedSurfaceIDs(field_info)

        self._allowed_scalar_field_names = _AllowedScalarFieldNames(
            is_data_valid, field_info
        )

        self._allowed_vector_field_names = _AllowedVectorFieldNames(
            is_data_valid, field_info
        )

        surface_args = dict(
            surface_ids=self._allowed_surface_ids,
            surface_name=self._allowed_surface_names,
        )
        scalar_field_args = {
            **dict(field_name=self._allowed_scalar_field_names),
            **surface_args,
        }
        self.get_scalar_field_data = override_help_text(
            _FieldMethod(
                field_data_accessor=self.get_scalar_field_data,
                args_allowed_values_accessors=scalar_field_args,
            ),
            self.get_scalar_field_data,
        )
        self.get_vector_field_data = override_help_text(
            _FieldMethod(
                field_data_accessor=self.get_vector_field_data,
                args_allowed_values_accessors={
                    **dict(field_name=self._allowed_vector_field_names),
                    **surface_args,
                },
            ),
            self.get_vector_field_data,
        )
        self.get_surface_data = override_help_text(
            _FieldMethod(
                field_data_accessor=self.get_surface_data,
                args_allowed_values_accessors=surface_args,
            ),
            self.get_surface_data,
        )
        self.get_pathlines_field_data = override_help_text(
            _FieldMethod(
                field_data_accessor=self.get_pathlines_field_data,
                args_allowed_values_accessors=scalar_field_args,
            ),
            self.get_pathlines_field_data,
        )

    def new_transaction(self):
        """Create a new field transaction."""
        return FieldTransaction(
            self._service,
            self._field_info,
            self._allowed_surface_ids,
            self._allowed_surface_names,
            self._allowed_scalar_field_names,
            self._allowed_vector_field_names,
        )

    def get_scalar_field_data(
        self,
        field_name: str,
        surfaces: List[int | str],
        node_value: bool | None = True,
        boundary_value: bool | None = True,
    ) -> Dict[int | str, np.array]:
        """Get scalar field data on a surface.

        Parameters
        ----------
        field_name : str
            Name of the scalar field.
        surfaces : List[int | str]
            List of surface IDS or surface names for the surface data.
        node_value : bool, optional
            Whether to provide data for the nodal location. The default is ``True``.
            When ``False``, data is provided for the element location.
        boundary_value : bool, optional
            Whether to provide slip velocity at the wall boundaries. The default is
            ``True``. When ``True``, no slip velocity is provided.

        Returns
        -------
        Dict[int | str, np.array]
            Returns a map of surface IDs (or names) to scalar field data.
        """
        surface_ids = _get_surface_ids(
            field_info=self._field_info,
            allowed_surface_names=self._allowed_surface_names,
            surfaces=surfaces,
        )
        fields_request = get_fields_request()
        fields_request.scalarFieldRequest.extend(
            [
                FieldDataProtoModule.ScalarFieldRequest(
                    surfaceId=surface_id,
                    scalarFieldName=self._allowed_scalar_field_names.valid_name(
                        field_name
                    ),
                    dataLocation=(
                        FieldDataProtoModule.DataLocation.Nodes
                        if node_value
                        else FieldDataProtoModule.DataLocation.Elements
                    ),
                    provideBoundaryValues=boundary_value,
                )
                for surface_id in surface_ids
            ]
        )

        fields = ChunkParser().extract_fields(self._service.get_fields(fields_request))
        scalar_field_data = next(iter(fields.values()))

        return {
            surface: scalar_field_data[surface_ids[count]][field_name]
            for count, surface in enumerate(surfaces)
        }

    def get_surface_data(
        self,
        data_types: List[SurfaceDataType],
        surfaces: List[int | str],
        overset_mesh: bool | None = False,
    ) -> Dict[int | str, Dict[SurfaceDataType, np.array | List[np.array]]]:
        """Get surface data (vertices, faces connectivity, centroids, and normals).

        Parameters
        ----------
        data_types : List[SurfaceDataType],
            SurfaceDataType Enum members.
        surfaces : List[int | str]
            List of surface IDS or surface names for the surface data.
        overset_mesh : bool, optional
            Whether to provide the overset method. The default is ``False``.

        Returns
        -------
        Dict[int | str, Dict[SurfaceDataType, np.array | List[np.array]]]
             Returns a map of surface IDs (or names) to face
             vertices, connectivity data, and normal or centroid data.
        """
        surface_ids = _get_surface_ids(
            field_info=self._field_info,
            allowed_surface_names=self._allowed_surface_names,
            surfaces=surfaces,
        )
        fields_request = get_fields_request()
        fields_request.surfaceRequest.extend(
            [
                FieldDataProtoModule.SurfaceRequest(
                    surfaceId=surface_id,
                    oversetMesh=overset_mesh,
                    provideFaces=SurfaceDataType.FacesConnectivity in data_types,
                    provideVertices=SurfaceDataType.Vertices in data_types,
                    provideFacesCentroid=SurfaceDataType.FacesCentroid in data_types,
                    provideFacesNormal=SurfaceDataType.FacesNormal in data_types,
                )
                for surface_id in surface_ids
            ]
        )
        fields = ChunkParser().extract_fields(self._service.get_fields(fields_request))
        surface_data = next(iter(fields.values()))

        ret_surf_data = {}
        for count, surface in enumerate(surfaces):
            ret_surf_data[surface] = {}
            for data_type in data_types:
                if data_type == SurfaceDataType.FacesConnectivity:
                    ret_surf_data[surface][data_type] = (
                        self._get_faces_connectivity_data(
                            surface_data[surface_ids[count]][
                                SurfaceDataType.FacesConnectivity.value
                            ]
                        )
                    )
                else:
                    ret_surf_data[surface][data_type] = surface_data[
                        surface_ids[count]
                    ][data_type.value].reshape(-1, 3)
        return ret_surf_data

    @staticmethod
    def _get_faces_connectivity_data(data):
        faces_data = []
        i = 0
        while i < len(data):
            end = i + 1 + data[i]
            faces_data.append(data[i + 1 : end])
            i = end
        return faces_data

    def get_vector_field_data(
        self,
        field_name: str,
        surfaces: List[int | str],
    ) -> Dict[int | str, np.array]:
        """Get vector field data on a surface.

        Parameters
        ----------
        field_name : str
            Name of the vector field.
        surfaces : List[int | str]
            List of surface IDS or surface names for the surface data.

        Returns
        -------
        Dict[int | str, np.array]
            Returns a  map of surface IDs (or names) to vector field data.
        """
        surface_ids = _get_surface_ids(
            field_info=self._field_info,
            allowed_surface_names=self._allowed_surface_names,
            surfaces=surfaces,
        )
        for surface_id in surface_ids:
            self.scheme_eval.string_eval(f"(surface? {surface_id})")
        fields_request = get_fields_request()
        fields_request.vectorFieldRequest.extend(
            [
                FieldDataProtoModule.VectorFieldRequest(
                    surfaceId=surface_id,
                    vectorFieldName=self._allowed_vector_field_names.valid_name(
                        field_name
                    ),
                )
                for surface_id in surface_ids
            ]
        )
        fields = ChunkParser().extract_fields(self._service.get_fields(fields_request))
        vector_field_data = next(iter(fields.values()))

        return {
            surface: vector_field_data[surface_ids[count]][field_name].reshape(-1, 3)
            for count, surface in enumerate(surfaces)
        }

    def get_pathlines_field_data(
        self,
        field_name: str,
        surfaces: List[int | str],
        additional_field_name: str | None = "",
        provide_particle_time_field: bool | None = False,
        node_value: bool | None = True,
        steps: int | None = 500,
        step_size: float | None = 500,
        skip: int | None = 0,
        reverse: bool | None = False,
        accuracy_control_on: bool | None = False,
        tolerance: float | None = 0.001,
        coarsen: int | None = 1,
        velocity_domain: str | None = "all-phases",
        zones: list | None = None,
    ) -> Dict:
        """Get the pathlines field data on a surface.

        Parameters
        ----------
        field_name : str
            Name of the scalar field to color pathlines.
        surfaces : List[int | str]
            List of surface IDS or surface names for the surface data.
        additional_field_name : str, optional
            Additional field if required.
        provide_particle_time_field: bool, optional
            Whether to provide the particle time. The default is ``False``.
        node_value : bool, optional
                    Whether to provide the nodal values. The default is ``True``. If
                    ``False``, element values are provided.
        steps: int, optional
            Pathlines steps. The default is ``500``
        step_size: float, optional
            Pathlines step size. The default is ``0.01``.
        skip: int, optional
            Pathlines to skip. The default is ``0``.
        reverse: bool, optional
            Whether to draw pathlines in reverse direction. The default is ``False``.
        accuracy_control_on: bool, optional
            Whether to control accuracy. The default is ``False``.
        tolerance: float, optional
            Pathlines tolerance. The default is ``0.001``.
        coarsen: int, optional
            Pathlines coarsen. The default is ``1``.
        velocity_domain: str, optional
            Domain for pathlines. The default is ``"all-phases"``.
        zones: list, optional
            Zones for pathlines. The default is ``[]``.

        Returns
        -------
        Dict
            Dictionary containing a map of surface IDs to the pathline data.
            For example, pathlines connectivity, vertices, and field.
        """
        if zones is None:
            zones = []
        surface_ids = _get_surface_ids(
            field_info=self._field_info,
            allowed_surface_names=self._allowed_surface_names,
            surfaces=surfaces,
        )
        fields_request = get_fields_request()
        fields_request.pathlinesFieldRequest.extend(
            [
                FieldDataProtoModule.PathlinesFieldRequest(
                    surfaceId=surface_id,
                    field=field_name,
                    additionalField=additional_field_name,
                    provideParticleTimeField=provide_particle_time_field,
                    dataLocation=(
                        FieldDataProtoModule.DataLocation.Nodes
                        if node_value
                        else FieldDataProtoModule.DataLocation.Elements
                    ),
                    steps=steps,
                    stepSize=step_size,
                    skip=skip,
                    reverse=reverse,
                    accuracyControlOn=accuracy_control_on,
                    tolerance=tolerance,
                    coarsen=coarsen,
                    velocityDomain=velocity_domain,
                    zones=zones,
                )
                for surface_id in surface_ids
            ]
        )
        fields = ChunkParser().extract_fields(self._service.get_fields(fields_request))
        pathlines_data = next(iter(fields.values()))

        path_lines_dict = {}

        for count, surface in enumerate(surfaces):
            path_lines_dict[surface] = {
                "vertices": pathlines_data[surface_ids[count]]["vertices"].reshape(
                    -1, 3
                ),
                "lines": self._get_faces_connectivity_data(
                    pathlines_data[surface_ids[count]]["lines"]
                ),
                field_name: pathlines_data[surface_ids[count]][field_name],
            }
        return path_lines_dict

    def get_mesh(self, zone: str | int) -> Mesh:
        """Get mesh for a zone.

        Parameters
        ----------
        zone : str | int
            Zone name or id. Currently, only cell zones are supported.

        Returns
        -------
        Mesh
            Mesh object containing nodes and elements.

        Raises
        ------
        ValueError
            If the zone is not found.
        NotImplementedError
            If a face zone is provided.
        """
        zone_info = None
        for zone_info in self.get_zones_info():
            if zone_info.name == zone or zone_info._id == zone:
                break
        if zone_info is None:
            raise ValueError(f"Zone {zone} not found.")
        if zone_info.zone_type == ZoneType.FACE:
            raise NotImplementedError("Face zone mesh is not supported.")

        # Mesh data is retrieved from the root domain in Fluent
        logger.info(f"Getting nodes data for zone {zone_info._id}")
        start_time = time.time()
        nodes_request = FieldDataProtoModule.GetSolverMeshNodesRequest(
            domain_id=ROOT_DOMAIN_ID, thread_id=zone_info._id
        )
        nested_nodes = self._service.get_solver_mesh_nodes(nodes_request)
        logger.info(f"Nodes data received in {time.time() - start_time} seconds")
        logger.info(f"Getting elements for zone {zone_info._id}")
        start_time = time.time()
        elements_request = FieldDataProtoModule.GetSolverMeshElementsRequest(
            domain_id=ROOT_DOMAIN_ID, thread_id=zone_info._id
        )
        elementss_pb = self._service.get_solver_mesh_elements(elements_request)
        logger.info(f"Elements data received in {time.time() - start_time} seconds")
        logger.info("Constructing nodes structure in PyFluent")
        start_time = time.time()
        node_count = sum(len(nodes) for nodes in nested_nodes)
        nodes = np.empty(node_count, dtype=Node)
        node_index_by_id = {}
        i = 0
        for nodes_pb in nested_nodes:
            for node_pb in nodes_pb:
                nodes[i] = Node(_id=node_pb.id, x=node_pb.x, y=node_pb.y, z=node_pb.z)
                node_index_by_id[node_pb.id] = i
                i += 1
        logger.info(
            f"Nodes structure constructed in {time.time() - start_time} seconds"
        )
        logger.info("Constructing elements structure in PyFluent")
        start_time = time.time()
        element_count = sum(len(elements) for elements in elementss_pb)
        elements = np.empty(element_count, dtype=Element)
        i = 0
        for elements_pb in elementss_pb:
            for element_pb in elements_pb:
                element_type = CellElementType(element_pb.element_type)
                if element_type == CellElementType.POLYHEDRON:
                    facets = []
                    for facet_pb in element_pb.facets:
                        facet = Facet(
                            node_indices=[node_index_by_id[id] for id in facet_pb.node]
                        )
                        facets.append(facet)
                    element = Element(
                        _id=element_pb.id,
                        element_type=element_type,
                        facets=facets,
                    )
                else:
                    element = Element(
                        _id=element_pb.id,
                        element_type=element_type,
                        node_indices=[
                            node_index_by_id[id] for id in element_pb.node_ids
                        ],
                    )
                elements[i] = element
                i += 1
        logger.info(
            f"Elements structure constructed in {time.time() - start_time} seconds"
        )
        logger.info("Returning mesh")
        return Mesh(nodes=nodes, elements=elements)
