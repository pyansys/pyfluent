"""Wrappers oversolution variables gRPC service of Fluent."""

import math
from typing import Dict, List, Optional

import grpc
import numpy as np

from ansys.api.fluent.v0 import field_data_pb2 as FieldDataProtoModule
from ansys.api.fluent.v0 import solution_variables_pb2 as SvarProtoModule
from ansys.api.fluent.v0 import solution_variables_pb2_grpc as SvarGrpcModule
from ansys.fluent.core.services.field_data import (
    _FieldDataConstants,
    override_help_text,
)
from ansys.fluent.core.services.interceptors import (
    GrpcErrorInterceptor,
    TracingInterceptor,
)
from ansys.fluent.core.solver.error_message import allowed_name_error_message


class SolutionVariablesService:
    """Solution variables service of Fluent."""

    def __init__(self, channel: grpc.Channel, metadata):
        """__init__ method ofsolution variables service class."""
        intercept_channel = grpc.intercept_channel(
            channel,
            GrpcErrorInterceptor(),
            TracingInterceptor(),
        )
        self.__stub = SvarGrpcModule.solution_variablesStub(intercept_channel)
        self.__metadata = metadata

    def get_solution_variables_data(self, request):
        """GetSvarData RPC ofsolution variables service."""
        return self.__stub.GetSvarData(request, metadata=self.__metadata)

    def set_solution_variables_data(self, request):
        """SetSvarData RPC ofsolution variables service."""
        return self.__stub.SetSvarData(request, metadata=self.__metadata)

    def get_solution_variabless_info(self, request):
        """GetSvarsInfo RPC ofsolution variables service."""
        return self.__stub.GetSvarsInfo(request, metadata=self.__metadata)

    def get_zones_info(self, request):
        """GetZonesInfo RPC ofsolution variables service."""
        return self.__stub.GetZonesInfo(request, metadata=self.__metadata)


class SolutionVariablesInfo:
    """Provide access to Fluent solution variables and Zones information.

    Example
    -------

    .. code-block:: python

        >>> solution_variables_info = solver_session.solution_variables_info
        >>>
        >>> solution_variabless_info_wall_fluid = solution_variables_info.get_solution_variabless_info(zone_names=['wall' , "fluid"], domain_name="mixture")
        >>> solution_variabless_info_wall_fluid.solution_variabless
        >>> ['SV_CENTROID', 'SV_D', 'SV_H', 'SV_K', 'SV_P', 'SV_T', 'SV_U', 'SV_V', 'SV_W']
        >>> solution_variables_info_centroid = solution_variabless_info_wall_fluid['SV_CENTROID']
        >>> solution_variables_info_centroid
        >>> name:SV_CENTROID dimension:3 field_type:<class 'numpy.float64'>
        >>>
        >>> zones_info = solution_variables_info.get_zones_info()
        >>> zones_info.zones
        >>> ['fluid', 'wall', 'symmetry', 'pressure-outlet-7', 'velocity-inlet-6', 'velocity-inlet-5', 'default-interior']
        >>> zone_info = zones_info['wall']
        >>> zone_info
        >>> name:wall count: 3630 zone_id:3 zone_type:wall thread_type:Face
    """

    class SolutionVariables:
        """Class containing information for multiple solution variables."""

        class SolutionVariable:
            """Class containing information for single solution variable."""

            def __init__(self, solution_variables_info):
                self.name = solution_variables_info.name
                self.dimension = solution_variables_info.dimension
                self.field_type = _FieldDataConstants.proto_field_type_to_np_data_type[
                    solution_variables_info.fieldType
                ]

            def __repr__(self):
                return f"name:{self.name} dimension:{self.dimension} field_type:{self.field_type}"

        def __init__(self, solution_variabless_info):
            self._solution_variabless_info = {}
            for solution_variables_info in solution_variabless_info:
                self._solution_variabless_info[
                    solution_variables_info.name
                ] = SolutionVariablesInfo.SolutionVariables.SolutionVariable(
                    solution_variables_info
                )

        def _filter(self, solution_variabless_info):
            self._solution_variabless_info = {
                k: v
                for k, v in self._solution_variabless_info.items()
                if k
                in [
                    solution_variables_info.name
                    for solution_variables_info in solution_variabless_info
                ]
            }

        def __getitem__(self, name):
            return self._solution_variabless_info.get(name, None)

        @property
        def solution_variabless(self) -> List[str]:
            return list(self._solution_variabless_info.keys())

    class ZonesInfo:
        """Class containing information for multiple zones."""

        class ZoneInfo:
            """Class containing information for single zone."""

            class PartitionsInfo:
                """Class containing information for partitions."""

                def __init__(self, partition_info):
                    self.count = partition_info.count
                    self.start_index = (
                        partition_info.startIndex if self.count > 0 else 0
                    )
                    self.end_index = partition_info.endIndex if self.count > 0 else 0

            def __init__(self, zone_info):
                self.name = zone_info.name
                self.zone_id = zone_info.zoneId
                self.zone_type = zone_info.zoneType
                self.thread_type = zone_info.threadType
                self.partitions_info = [
                    self.PartitionsInfo(partition_info)
                    for partition_info in zone_info.partitionsInfo
                ]

            @property
            def count(self) -> int:
                return sum(
                    [partition_info.count for partition_info in self.partitions_info]
                )

            def __repr__(self):
                partition_str = ""
                for i, partition_info in enumerate(self.partitions_info):
                    partition_str += f"\n\t{i}. {partition_info.count}[{partition_info.start_index}:{partition_info.end_index}]"
                return f"name:{self.name} count: {self.count} zone_id:{self.zone_id} zone_type:{self.zone_type} threadType:{'Cell' if self.thread_type == SvarProtoModule.ThreadType.CELL_THREAD else 'Face'}{partition_str}"

        def __init__(self, zones_info, domains_info):
            self._zones_info = {}
            self._domains_info = {}
            for zone_info in zones_info:
                self._zones_info[zone_info.name] = self.ZoneInfo(zone_info)
            for domain_info in domains_info:
                self._domains_info[domain_info.name] = domain_info.domainId

        def __getitem__(self, name):
            return self._zones_info.get(name, None)

        @property
        def zones(self) -> List[str]:
            return list(self._zones_info.keys())

        @property
        def domains(self) -> List[str]:
            return list(self._domains_info.keys())

        def domain_id(self, domain_name) -> int:
            return self._domains_info.get(domain_name, None)

    def __init__(
        self,
        service: SolutionVariablesService,
    ):
        self._service = service

    def get_solution_variabless_info(
        self, zone_names: List[str], domain_name: str = "mixture"
    ) -> SolutionVariables:
        """Get solution variables info for zones in the domain.

        Parameters
        ----------
        zone_names : List[str]
            List of zone names.
        domain_name: str, optional
            Domain name.The default is ``mixture``.

        Returns
        -------
        SolutionVariablesInfo.SolutionVariables
            Object containing information for solution variables which are common for list of zone names.
        """

        allowed_zone_names = _AllowedZoneNames(self)
        allowed_domain_names = _AllowedDomainNames(self)
        solution_variabless_info = None
        for zone_name in zone_names:
            request = SvarProtoModule.GetSvarsInfoRequest(
                domainId=allowed_domain_names.valid_name(domain_name),
                zoneId=allowed_zone_names.valid_name(zone_name),
            )
            response = self._service.get_solution_variabless_info(request)
            if solution_variabless_info is None:
                solution_variabless_info = SolutionVariablesInfo.SolutionVariables(
                    response.solution_variablessInfo
                )
            else:
                solution_variabless_info._filter(response.solution_variablessInfo)
        return solution_variabless_info

    def get_zones_info(self) -> ZonesInfo:
        """Get Zones info.

        Parameters
        ----------
        None

        Returns
        -------
        SolutionVariablesInfo.ZonesInfo
            Object containing information for all zones.
        """
        request = SvarProtoModule.GetZonesInfoRequest()
        response = self._service.get_zones_info(request)
        return SolutionVariablesInfo.ZonesInfo(response.zonesInfo, response.domainsInfo)


class SvarError(ValueError):
    """Exception class for errors insolution variables name."""

    def __init__(self, solution_variables_name: str, allowed_values: List[str]):
        self.solution_variables_name = solution_variables_name
        super().__init__(
            allowed_name_error_message(
                "solution_variables", solution_variables_name, allowed_values
            )
        )


class ZoneError(ValueError):
    """Exception class for errors in Zone name."""

    def __init__(self, zone_name: str, allowed_values: List[str]):
        self.zone_name = zone_name
        super().__init__(allowed_name_error_message("zone", zone_name, allowed_values))


class _AllowedNames:
    def is_valid(self, name):
        return name in self()


class _AllowedSvarNames:
    def __init__(self, solution_variables_info: SolutionVariablesInfo):
        self._solution_variables_info = solution_variables_info

    def __call__(
        self, zone_names: List[str], domain_name: str = "mixture"
    ) -> List[str]:
        return self._solution_variables_info.get_solution_variabless_info(
            zone_names=zone_names, domain_name=domain_name
        ).solution_variabless

    def is_valid(
        self,
        solution_variables_name,
        zone_names: List[str],
        domain_name: str = "mixture",
    ):
        return solution_variables_name in self(
            zone_names=zone_names, domain_name=domain_name
        )

    def valid_name(
        self,
        solution_variables_name,
        zone_names: List[str],
        domain_name: str = "mixture",
    ):
        if not self.is_valid(
            solution_variables_name, zone_names=zone_names, domain_name=domain_name
        ):
            raise SvarError(
                solution_variables_name=solution_variables_name,
                allowed_values=self(zone_names=zone_names, domain_name=domain_name),
            )
        return solution_variables_name


class _AllowedZoneNames(_AllowedNames):
    def __init__(self, solution_variables_info: SolutionVariablesInfo):
        self._zones_info = solution_variables_info.get_zones_info()

    def __call__(self) -> List[str]:
        return self._zones_info.zones

    def valid_name(self, zone_name):
        if not self.is_valid(zone_name):
            raise ZoneError(
                zone_name=zone_name,
                allowed_values=self(),
            )
        return self._zones_info[zone_name].zone_id


class _AllowedDomainNames(_AllowedNames):
    def __init__(self, solution_variables_info: SolutionVariablesInfo):
        self._zones_info = solution_variables_info.get_zones_info()

    def __call__(self) -> List[str]:
        return self._zones_info.domains

    def valid_name(self, domain_name):
        if not self.is_valid(domain_name):
            raise ZoneError(
                domain_name=domain_name,
                allowed_values=self(),
            )
        return self._zones_info.domain_id(domain_name)


class _SvarMethod:
    class _Arg:
        def __init__(self, accessor):
            self._accessor = accessor

        def allowed_values(self):
            return sorted(self._accessor())

    def __init__(self, solution_variables_accessor, args_allowed_values_accessors):
        self._solution_variables_accessor = solution_variables_accessor
        for arg_name, accessor in args_allowed_values_accessors.items():
            setattr(self, arg_name, _SvarMethod._Arg(accessor))

    def __call__(self, *args, **kwargs):
        return self._solution_variables_accessor(*args, **kwargs)


def extract_solution_variabless(solution_variabless_data):
    """Extractssolution variables data via a server call."""

    def _extract_solution_variables(
        field_datatype, field_size, solution_variabless_data
    ):
        field_arr = np.empty(field_size, dtype=field_datatype)
        field_datatype_item_size = np.dtype(field_datatype).itemsize
        index = 0
        for solution_variables_data in solution_variabless_data:
            chunk = solution_variables_data.payload
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

    zones_solution_variables_data = {}
    for array in solution_variabless_data:
        if array.WhichOneof("array") == "payloadInfo":
            zones_solution_variables_data[
                array.payloadInfo.zone
            ] = _extract_solution_variables(
                _FieldDataConstants.proto_field_type_to_np_data_type[
                    array.payloadInfo.fieldType
                ],
                array.payloadInfo.fieldSize,
                solution_variabless_data,
            )
        elif array.WhichOneof("array") == "header":
            continue

    return zones_solution_variables_data


class SolutionVariablesData:
    """Provides access to Fluentsolution variables data on zones.

    Example
    -------
    .. code-block:: python
        >>>
        >>> solution_variables_data = solver_session.solution_variables_data
        >>>
        >>> sv_t_wall_fluid=solver_session.solution_variables_data.get_solution_variables_data(solution_variables_name="SV_T", domain_name="mixture", zone_names=["fluid", "wall"])
        >>>
        >>> sv_t_wall_fluid.domain
        >>> 'mixture'
        >>>
        >>> sv_t_wall_fluid.zones
        >>> ['fluid', 'wall']
        >>>
        >>> fluid_temp = sv_t_wall_fluid['fluid']
        >>> fluid_temp.size
        >>> 13852
        >>> fluid_temp.dtype
        >>> float64
        >>> fluid_temp
        >>> array([600., 600., 600., ..., 600., 600., 600.])
        >>>
        >>> wall_temp_array = solution_variables_data.get_array("SV_T", "wall")
        >>> fluid_temp_array =solution_variables_data.get_array("SV_T", "fluid")
        >>> wall_temp_array[:]= 500
        >>> fluid_temp_array[:]= 600
        >>> zone_names_to_solution_variables_data = {'wall':wall_temp_array, 'fluid':fluid_temp_array}
        >>> solution_variables_data.set_solution_variables_data(solution_variables_name="SV_T", domain_name="mixture", zone_names_to_solution_variables_data=zone_names_to_solution_variables_data)
    """

    class Data:
        def __init__(self, domain_name, zone_id_name_map, solution_variables_data):
            self._domain_name = domain_name
            self._data = {
                zone_id_name_map[zone_id]: zone_data
                for zone_id, zone_data in solution_variables_data.items()
            }

        @property
        def domain(self):
            return self._domain_name

        @property
        def zones(self):
            return list(self._data.keys())

        @property
        def data(self):
            return self._data

        def __getitem__(self, name):
            return self._data.get(name, None)

    def __init__(
        self,
        service: SolutionVariablesService,
        solution_variables_info: SolutionVariablesInfo,
    ):
        self._service = service
        self._solution_variables_info = solution_variables_info

    def _update_solution_variables_info(self):
        self._allowed_zone_names = _AllowedZoneNames(self._solution_variables_info)

        self._allowed_domain_names = _AllowedDomainNames(self._solution_variables_info)

        self._allowed_solution_variables_names = _AllowedSvarNames(
            self._solution_variables_info
        )
        solution_variables_args = dict(
            zone_names=self._allowed_zone_names,
            solution_variables_name=self._allowed_solution_variables_names,
        )

        self.get_solution_variables_data = override_help_text(
            _SvarMethod(
                solution_variables_accessor=self.get_solution_variables_data,
                args_allowed_values_accessors=solution_variables_args,
            ),
            SolutionVariablesData.get_solution_variables_data,
        )

    def get_array(
        self, solution_variables_name: str, zone_name: str, domain_name: str = "mixture"
    ) -> np.zeros:
        """Get numpy zeros array for thesolution variables on a zone.

        This array can be populated  with values to setsolution variables data.
        """
        self._update_solution_variables_info()

        zones_info = self._solution_variables_info.get_zones_info()
        if zone_name in zones_info.zones:
            solution_variabless_info = (
                self._solution_variables_info.get_solution_variabless_info(
                    zone_names=[zone_name], domain_name=domain_name
                )
            )
            if solution_variables_name in solution_variabless_info.solution_variabless:
                return np.zeros(
                    zones_info[zone_name].count
                    * solution_variabless_info[solution_variables_name].dimension,
                    dtype=solution_variabless_info[solution_variables_name].field_type,
                )

    def get_solution_variables_data(
        self,
        solution_variables_name: str,
        zone_names: List[str],
        domain_name: Optional[str] = "mixture",
    ) -> Data:
        """Getsolution variables data on zones.

        Parameters
        ----------
        solution_variables_name : str
            Name of the solution variable.
        zone_names: List[str]
            Zone names list forsolution variables data.
        domain_name : str, optional
            Domain name. The default is ``mixture``.

        Returns
        -------
        SolutionVariablesData.Data
            Object containingsolution variables data.
        """
        self._update_solution_variables_info()
        solution_variabless_request = SvarProtoModule.GetSvarDataRequest(
            provideBytesStream=_FieldDataConstants.bytes_stream,
            chunkSize=_FieldDataConstants.chunk_size,
        )
        solution_variabless_request.domainId = self._allowed_domain_names.valid_name(
            domain_name
        )
        solution_variabless_request.name = (
            self._allowed_solution_variables_names.valid_name(
                solution_variables_name, zone_names, domain_name
            )
        )
        zone_id_name_map = {}
        for zone_name in zone_names:
            zone_id = self._allowed_zone_names.valid_name(zone_name)
            zone_id_name_map[zone_id] = zone_name
            solution_variabless_request.zones.append(zone_id)

        return SolutionVariablesData.Data(
            domain_name,
            zone_id_name_map,
            extract_solution_variabless(
                self._service.get_solution_variables_data(solution_variabless_request)
            ),
        )

    def set_solution_variables_data(
        self,
        solution_variables_name: str,
        zone_names_to_solution_variables_data: Dict[str, np.array],
        domain_name: str = "mixture",
    ) -> None:
        """Setsolution variables data on zones.

        Parameters
        ----------
        solution_variables_name : str
            Name of the solution variable.
        zone_names_to_solution_variables_data: Dict[str, np.array]
            Dictionary containing zone names forsolution variables data.
        domain_name : str, optional
            Domain name. The default is ``mixture``.

        Returns
        -------
        None
        """
        self._update_solution_variables_info()
        domain_id = self._allowed_domain_names.valid_name(domain_name)
        zone_ids_to_solution_variables_data = {
            self._allowed_zone_names.valid_name(zone_name): solution_variables_data
            for zone_name, solution_variables_data in zone_names_to_solution_variables_data.items()
        }

        def generate_set_solution_variables_data_requests():
            set_solution_variables_data_requests = []

            set_solution_variables_data_requests.append(
                SvarProtoModule.SetSvarDataRequest(
                    header=SvarProtoModule.SvarHeader(
                        name=solution_variables_name, domainId=domain_id
                    )
                )
            )

            for (
                zone_id,
                solution_variables_data,
            ) in zone_ids_to_solution_variables_data.items():
                max_array_size = (
                    _FieldDataConstants.chunk_size
                    / np.dtype(solution_variables_data.dtype).itemsize
                )
                solution_variables_data_list = np.array_split(
                    solution_variables_data,
                    math.ceil(solution_variables_data.size / max_array_size),
                )
                set_solution_variables_data_requests.append(
                    SvarProtoModule.SetSvarDataRequest(
                        payloadInfo=SvarProtoModule.Info(
                            fieldType=_FieldDataConstants.np_data_type_to_proto_field_type[
                                solution_variables_data.dtype.type
                            ],
                            fieldSize=solution_variables_data.size,
                            zone=zone_id,
                        )
                    )
                )
                set_solution_variables_data_requests += [
                    SvarProtoModule.SetSvarDataRequest(
                        payload=SvarProtoModule.Payload(
                            floatPayload=FieldDataProtoModule.FloatPayload(
                                payload=solution_variables_data
                            )
                        )
                        if solution_variables_data.dtype.type == np.float32
                        else SvarProtoModule.Payload(
                            doublePayload=FieldDataProtoModule.DoublePayload(
                                payload=solution_variables_data
                            )
                        )
                        if solution_variables_data.dtype.type == np.float64
                        else SvarProtoModule.Payload(
                            intPayload=FieldDataProtoModule.IntPayload(
                                payload=solution_variables_data
                            )
                        )
                        if solution_variables_data.dtype.type == np.int32
                        else SvarProtoModule.Payload(
                            longPayload=FieldDataProtoModule.LongPayload(
                                payload=solution_variables_data
                            )
                        )
                    )
                    for solution_variables_data in solution_variables_data_list
                    if solution_variables_data.size > 0
                ]

            for (
                set_solution_variables_data_request
            ) in set_solution_variables_data_requests:
                yield set_solution_variables_data_request

        self._service.set_solution_variables_data(
            generate_set_solution_variables_data_requests()
        )
