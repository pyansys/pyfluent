"""Wrappers over StateEngine based datamodel gRPC service of Fluent."""

from enum import Enum
import functools
import itertools
import logging
import os
from threading import RLock
from typing import Any, Callable, Iterator, NoReturn, Sequence

from google.protobuf.json_format import MessageToDict, ParseDict
import grpc

from ansys.api.fluent.v0 import datamodel_se_pb2 as DataModelProtoModule
from ansys.api.fluent.v0 import datamodel_se_pb2_grpc as DataModelGrpcModule
from ansys.api.fluent.v0.variant_pb2 import Variant
import ansys.fluent.core as pyfluent
from ansys.fluent.core.data_model_cache import DataModelCache, NameKey
from ansys.fluent.core.exceptions import InvalidArgument
from ansys.fluent.core.services.interceptors import (
    BatchInterceptor,
    ErrorStateInterceptor,
    GrpcErrorInterceptor,
    TracingInterceptor,
)
from ansys.fluent.core.services.streaming import StreamingService
from ansys.fluent.core.solver.error_message import allowed_name_error_message
from ansys.fluent.core.utils.fluent_version import FluentVersion

Path = list[tuple[str, str]]
_TValue = None | bool | int | float | str | Sequence["_TValue"] | dict[str, "_TValue"]
logger: logging.Logger = logging.getLogger("pyfluent.datamodel")

member_specs_oneof_fields = [
    x.name
    for x in DataModelProtoModule.MemberSpecs.DESCRIPTOR.oneofs_by_name["as"].fields
]


def _get_value_from_message_dict(d: dict[str, Any], key: list[str | Sequence[str]]):
    """Get value from a protobuf message dict by a sequence of keys.

    A key can also be a list of oneof types.
    """
    for k in key:
        if isinstance(k, str):
            d = d[k]
        else:
            d = next(filter(None, (d.get(x) for x in k)))
    return d


class DisallowedFilePurpose(ValueError):
    """Is raised when the specified file purpose is not in the allowed values."""

    def __init__(
        self,
        context: Any | None = None,
        name: Any | None = None,
        allowed_values: Any | None = None,
    ):
        """Initialize DisallowedFilePurpose."""
        super().__init__(
            allowed_name_error_message(
                context=context, trial_name=name, allowed_values=allowed_values
            )
        )


class InvalidNamedObject(RuntimeError):
    """Raised when the object is not a named object."""

    def __init__(self, class_name):
        """Initialize InvalidNamedObject."""
        super().__init__(f"{class_name} is not a named object class.")


class SubscribeEventError(RuntimeError):
    """Raised when server fails to subscribe from event."""

    def __init__(self, request):
        """Initialize SubscribeEventError."""
        super().__init__(f"Failed to subscribe event: {request}!")


class UnsubscribeEventError(RuntimeError):
    """Raised when server fails to unsubscribe from event."""

    def __init__(self, request):
        """Initialize UnsubscribeEventError."""
        super().__init__(f"Failed to unsubscribe event: {request}!")


class ReadOnlyObjectError(RuntimeError):
    """Raised on an attempt to mutate a read-only object."""

    def __init__(self, obj_name):
        """Initialize ReadOnlyObjectError."""
        super().__init__(f"{obj_name} is readonly!")


class Attribute(Enum):
    """Contains the standard names of data model attributes associated with the data
    model service."""

    IS_ACTIVE: str = "isActive"
    EXPOSURE_LEVEL: str = "exposureLevel"
    IS_READ_ONLY: str = "isReadOnly"
    DEFAULT: str = "default"
    FORCE_DEFAULT: str = "forceDefault"
    MIN: str = "min"
    MAX: str = "max"
    ALLOWED_VALUES: str = "allowedValues"
    EXCLUDED_VALUES: str = "excludedValues"
    MIN_LENGTH: str = "minLength"
    MAX_LENGTH: str = "maxLength"
    ERROR_STATUS: str = "errorStatus"
    USER_ERROR_STATUS: str = "userErrorStatus"
    MEMBERS: str = "members"
    DISPLAY_TEXT: str = "displayText"
    NAMES: str = "__names__"
    INTERNAL_NAMES: str = "__ids__"
    PATHS: str = "__paths__"
    ROOT_ID: str = "__root__"
    NAME: str = "_name_"
    REFERENCE_PATH: str = "referencePath"
    ARGUMENTS: str = "arguments"
    TOOL_TIP: str = "toolTip"
    SHOW_AT_PARENT_NODE: str = "showAtParentNode"
    WIDGET_TYPE: str = "widgetType"
    ECHO_MODE: str = "echoMode"
    IS_TREE_NODE: str = "isTreeNode"
    MIGRATION: str = "migration"
    DEPRECATED_VERSION: str = "deprecatedVersion"


class _FilterDatamodelNames:
    def __init__(self, service):
        self._filter_fn = getattr(service, "is_in_datamodel", None)

    def __call__(self, parent, names):
        if self._filter_fn is None:
            return names

        def validate_name(name):
            obj = getattr(parent, name)
            # might need to make this more flexible (e.g., enhanced workflow types)
            is_in_datamodel = isinstance(obj, (PyCommand, PyStateContainer))
            if is_in_datamodel:
                return self._filter_fn(parent.rules, convert_path_to_se_path(obj.path))
            else:
                return True

        return [name for name in names if validate_name(name)]


class DatamodelServiceImpl:
    """Wraps the StateEngine-based datamodel gRPC service of Fluent."""

    def __init__(
        self,
        channel: grpc.Channel,
        metadata: list[tuple[str, str]],
        fluent_error_state,
        file_transfer_service: Any | None = None,
    ) -> None:
        """__init__ method of DatamodelServiceImpl class."""
        intercept_channel = grpc.intercept_channel(
            channel,
            GrpcErrorInterceptor(),
            ErrorStateInterceptor(fluent_error_state),
            TracingInterceptor(),
            BatchInterceptor(),
        )
        self._stub = DataModelGrpcModule.DataModelStub(intercept_channel)
        self._metadata = metadata
        self.file_transfer_service = file_transfer_service

    # TODO: Remove it from the proto interface
    def initialize_datamodel(
        self, request: DataModelProtoModule.InitDatamodelRequest
    ) -> DataModelProtoModule.InitDatamodelResponse:
        """RPC initDatamodel of DataModel service."""
        return self._stub.initDatamodel(request, metadata=self._metadata)

    def get_attribute_value(
        self, request: DataModelProtoModule.GetAttributeValueRequest
    ) -> DataModelProtoModule.GetAttributeValueResponse:
        """RPC getAttributeValue of DataModel service."""
        return self._stub.getAttributeValue(request, metadata=self._metadata)

    def get_state(
        self, request: DataModelProtoModule.GetStateRequest
    ) -> DataModelProtoModule.GetStateResponse:
        """RPC getState of DataModel service."""
        return self._stub.getState(request, metadata=self._metadata)

    def rename(
        self, request: DataModelProtoModule.RenameRequest
    ) -> DataModelProtoModule.RenameResponse:
        """RPC rename of DataModel service."""
        return self._stub.rename(request, metadata=self._metadata)

    def get_object_names(
        self, request: DataModelProtoModule.GetObjectNamesRequest
    ) -> DataModelProtoModule.GetObjectNamesResponse:
        """RPC getObjectNames of DataModel service."""
        return self._stub.getObjectNames(request, metadata=self._metadata)

    def delete_child_objects(
        self, request: DataModelProtoModule.DeleteChildObjectsRequest
    ) -> DataModelProtoModule.DeleteChildObjectsResponse:
        """RPC deleteChildObjects of DataModel service."""
        return self._stub.deleteChildObjects(request, metadata=self._metadata)

    def set_state(
        self, request: DataModelProtoModule.SetStateRequest
    ) -> DataModelProtoModule.SetStateResponse:
        """RPC setState of DataModel service."""
        return self._stub.setState(request, metadata=self._metadata)

    def fix_state(
        self, request: DataModelProtoModule.FixStateRequest
    ) -> DataModelProtoModule.FixStateResponse:
        """RPC fixState of DataModel service."""
        return self._stub.fixState(request, metadata=self._metadata)

    def update_dict(
        self, request: DataModelProtoModule.UpdateDictRequest
    ) -> DataModelProtoModule.UpdateDictResponse:
        """RPC updateDict of DataModel service."""
        return self._stub.updateDict(request, metadata=self._metadata)

    def delete_object(
        self, request: DataModelProtoModule.DeleteObjectRequest
    ) -> DataModelProtoModule.DeleteObjectResponse:
        """RPC deleteObject of DataModel service."""
        return self._stub.deleteObject(request, metadata=self._metadata)

    def execute_command(
        self, request: DataModelProtoModule.ExecuteCommandRequest
    ) -> DataModelProtoModule.ExecuteCommandResponse:
        """RPC executeCommand of DataModel service."""
        logger.debug(f"Command: {request.command}")
        return self._stub.executeCommand(request, metadata=self._metadata)

    def execute_query(
        self, request: DataModelProtoModule.ExecuteQueryRequest
    ) -> DataModelProtoModule.ExecuteQueryResponse:
        """RPC executeQuery of DataModel service."""
        logger.debug(f"Query: {request.query}")
        return self._stub.executeQuery(request, metadata=self._metadata)

    def create_command_arguments(
        self, request: DataModelProtoModule.CreateCommandArgumentsRequest
    ) -> DataModelProtoModule.CreateCommandArgumentsResponse:
        """RPC createCommandArguments of DataModel service."""
        return self._stub.createCommandArguments(request, metadata=self._metadata)

    def delete_command_arguments(
        self, request: DataModelProtoModule.DeleteCommandArgumentsRequest
    ) -> DataModelProtoModule.DeleteCommandArgumentsResponse:
        """RPC deleteCommandArguments of DataModel service.

        Raises
        ------
        RuntimeError
            If command instancing is not supported.
        """
        try:
            return self._stub.deleteCommandArguments(request, metadata=self._metadata)
        except grpc.RpcError as ex:
            raise RuntimeError(
                f"The following exception was caught\n {ex.details()}\n "
                "while deleting a command instance. Command instancing is"
                "supported from Ansys 2023R2 onward."
            ) from None

    def get_specs(
        self, request: DataModelProtoModule.GetSpecsRequest
    ) -> DataModelProtoModule.GetSpecsResponse:
        """RPC getSpecs of DataModel service."""
        return self._stub.getSpecs(request, metadata=self._metadata)

    def get_static_info(
        self, request: DataModelProtoModule.GetStaticInfoRequest
    ) -> DataModelProtoModule.GetStaticInfoResponse:
        """RPC getStaticInfo of DataModel service."""
        return self._stub.getStaticInfo(request, metadata=self._metadata)

    def subscribe_events(
        self, request: DataModelProtoModule.SubscribeEventsRequest
    ) -> DataModelProtoModule.SubscribeEventsResponse:
        """RPC subscribeEvents of DataModel service."""
        return self._stub.subscribeEvents(request, metadata=self._metadata)

    def unsubscribe_events(
        self, request: DataModelProtoModule.UnsubscribeEventsRequest
    ) -> DataModelProtoModule.UnsubscribeEventsResponse:
        """RPC unsubscribeEvents of DataModel service."""
        return self._stub.unsubscribeEvents(request, metadata=self._metadata)


def _convert_value_to_variant(val: _TValue, var: Variant) -> None:
    """Convert a Python data type to Fluent's variant type."""
    if isinstance(val, bool):
        var.bool_state = val
    elif isinstance(val, int):
        var.int64_state = val
    elif isinstance(val, float):
        var.double_state = val
    elif isinstance(val, str):
        var.string_state = val
    elif isinstance(val, (list, tuple)):
        var.variant_vector_state.SetInParent()
        for item in val:
            item_var = var.variant_vector_state.item.add()
            _convert_value_to_variant(item, item_var)
    elif isinstance(val, dict):
        var.variant_map_state.SetInParent()
        for k, v in val.items():
            _convert_value_to_variant(v, var.variant_map_state.item[k])


def _convert_variant_to_value(var: Variant) -> _TValue:
    """Convert Fluent's variant type to a Python data type."""
    if var.HasField("bool_state"):
        return var.bool_state
    elif var.HasField("int64_state"):
        return var.int64_state
    elif var.HasField("double_state"):
        return var.double_state
    elif var.HasField("string_state"):
        return var.string_state
    elif var.HasField("bool_vector_state"):
        return var.bool_vector_state.item
    elif var.HasField("int64_vector_state"):
        return var.int64_vector_state.item
    elif var.HasField("double_vector_state"):
        return var.double_vector_state.item
    elif var.HasField("string_vector_state"):
        return var.string_vector_state.item
    elif var.HasField("variant_vector_state"):
        val = []
        for item in var.variant_vector_state.item:
            val.append(_convert_variant_to_value(item))
        return val
    elif var.HasField("variant_map_state"):
        val = {}
        for k, v in var.variant_map_state.item.items():
            val[k] = _convert_variant_to_value(v)
        return val


class EventSubscription:
    """EventSubscription class for any datamodel event."""

    def __init__(
        self,
        service,
        path,
        request_dict: dict[str, Any],
    ) -> None:
        """Subscribe to a datamodel event.

        Raises
        ------
        SubscribeEventError
            If server fails to subscribe from event.
        """
        self.is_subscribed: bool = False
        self._service: DatamodelService = service
        self.path: str = path
        response = service.subscribe_events(request_dict)
        response = response[0]
        if response["status"] != DataModelProtoModule.STATUS_SUBSCRIBED:
            raise SubscribeEventError(request_dict)
        else:
            self.is_subscribed = True
        self.tag: str = response["tag"]
        self._service.subscriptions.add(self.tag, self)

    def unsubscribe(self) -> None:
        """Unsubscribe the datamodel event.

        Raises
        ------
        UnsubscribeEventError
            If server fails to unsubscribe from event.
        """
        if self.is_subscribed:
            self._service.event_streaming.unregister_callback(self.tag)
            response = self._service.unsubscribe_events([self.tag])
            response = response[0]
            if response["status"] != DataModelProtoModule.STATUS_UNSUBSCRIBED:
                raise UnsubscribeEventError(self.tag)
            else:
                self.is_subscribed = False
            self._service.subscriptions.remove(self.tag)


class SubscriptionList:
    """Stores subscription objects by tag."""

    def __init__(self):
        """Initialize SubscriptionList."""
        self._subscriptions = {}
        self._lock = RLock()

    def __contains__(self, tag: str) -> bool:
        with self._lock:
            return tag in self._subscriptions

    def add(self, tag: str, subscription: EventSubscription) -> None:
        """Add a subscription object.

        Parameters
        ----------
        tag : str
            Subscription tag.
        subscription : EventSubscription
            Subscription object.
        """
        with self._lock:
            self._subscriptions[tag] = subscription

    def remove(self, tag: str) -> None:
        """Remove a subscription object.

        Parameters
        ----------
        tag : str
            Subscription tag.
        """
        with self._lock:
            self._subscriptions.pop(tag, None)

    def unsubscribe_while_deleting(
        self, rules: str, path: str, deletion_stage: str
    ) -> None:
        """Unsubscribe corresponding subscription objects while the datamodel object is
        being deleted.

        Parameters
        ----------
        rules : str
            Datamodel object rules.
        path : str
            Datamodel object path.
        deletion_stage : {"before", "after"}
            All subscription objects except those of on-deleted type are unsubscribed
            before the datamodel object is deleted. On-deleted subscription objects are
            unsubscribed after the datamodel object is deleted.
        """
        with self._lock:
            delete_tag = f"/{rules}/deleted"
            after = deletion_stage == "after"
            keys_to_unsubscribe = []
            for k, v in self._subscriptions.items():
                if v.path.startswith(path) and not (
                    after ^ v.tag.startswith(delete_tag)
                ):
                    keys_to_unsubscribe.append(k)
            for k in reversed(keys_to_unsubscribe):
                self._subscriptions[k].unsubscribe()

    def unsubscribe_all(self) -> None:
        """Unsubscribe all subscription objects."""
        with self._lock:
            while self._subscriptions:
                v = next(reversed(self._subscriptions.values()))
                v.unsubscribe()


class DatamodelService(StreamingService):
    """Pure Python wrapper of DatamodelServiceImpl."""

    def __init__(
        self,
        channel: grpc.Channel,
        metadata: list[tuple[str, str]],
        version: FluentVersion,
        fluent_error_state,
        file_transfer_service: Any | None = None,
    ) -> None:
        """__init__ method of DatamodelService class."""
        self._impl = DatamodelServiceImpl(channel, metadata, fluent_error_state)
        super().__init__(
            stub=self._impl._stub,
            metadata=metadata,
        )
        self.event_streaming = None
        self.subscriptions = SubscriptionList()
        self.file_transfer_service = file_transfer_service
        self.cache = DataModelCache() if pyfluent.DATAMODEL_USE_STATE_CACHE else None
        self.version = version

    def get_attribute_value(self, rules: str, path: str, attribute: str) -> _TValue:
        """Get attribute value."""
        request = DataModelProtoModule.GetAttributeValueRequest(
            rules=rules, path=path, attribute=attribute
        )
        response = self._impl.get_attribute_value(request)
        return _convert_variant_to_value(response.result)

    def get_state(self, rules: str, path: str) -> _TValue:
        """Get state."""
        request = DataModelProtoModule.GetStateRequest(rules=rules, path=path)
        response = self._impl.get_state(request)
        return _convert_variant_to_value(response.state)

    def get_object_names(self, rules: str, path: str) -> list[str]:
        """Get object names."""
        request = DataModelProtoModule.GetObjectNamesRequest()
        request.rules = rules
        request.path = path
        response = self._impl.get_object_names(request)
        return response.names

    def rename(self, rules: str, path: str, new_name: str) -> None:
        """Rename an object."""
        request = DataModelProtoModule.RenameRequest()
        request.rules = rules
        request.path = path
        request.new_name = new_name
        request.wait = True
        response = self._impl.rename(request)
        if self.cache is not None:
            self.cache.update_cache(
                rules,
                response.state,
                response.deletedpaths,
                version=self.version,
            )

    def delete_child_objects(
        self, rules: str, path: str, obj_type: str, child_names: list[str]
    ) -> None:
        """Delete child objects."""
        request = DataModelProtoModule.DeleteChildObjectsRequest()
        request.rules = rules
        request.path = path + "/" + obj_type
        for name in child_names:
            request.child_names.names.append(name)
        request.wait = True
        response = self._impl.delete_child_objects(request)
        if self.cache is not None:
            self.cache.update_cache(
                rules,
                response.state,
                response.deletedpaths,
                version=self.version,
            )

    def delete_all_child_objects(self, rules: str, path: str, obj_type: str) -> None:
        """Delete all child objects."""
        request = DataModelProtoModule.DeleteChildObjectsRequest()
        request.rules = rules
        request.path = path + "/" + obj_type
        request.delete_all = True
        request.wait = True
        response = self._impl.delete_child_objects(request)
        if self.cache is not None:
            self.cache.update_cache(
                rules,
                response.state,
                response.deletedpaths,
                version=self.version,
            )

    def set_state(self, rules: str, path: str, state: _TValue) -> None:
        """Set state."""
        request = DataModelProtoModule.SetStateRequest(
            rules=rules, path=path, wait=True
        )
        _convert_value_to_variant(state, request.state)
        response = self._impl.set_state(request)
        if self.cache is not None:
            self.cache.update_cache(
                rules,
                response.state,
                response.deletedpaths,
                version=self.version,
            )

    def fix_state(self, rules, path) -> None:
        """Fix state."""
        request = DataModelProtoModule.FixStateRequest()
        request.rules = rules
        request.path = convert_path_to_se_path(path)
        response = self._impl.fix_state(request)
        if self.cache is not None:
            self.cache.update_cache(
                rules,
                response.state,
                response.deletedpaths,
                version=self.version,
            )

    def update_dict(
        self,
        rules: str,
        path: str,
        dict_state: dict[str, _TValue],
        recursive=False,
    ) -> None:
        """Update the dict."""
        request = DataModelProtoModule.UpdateDictRequest(
            rules=rules, path=path, wait=True, recursive=recursive
        )
        _convert_value_to_variant(dict_state, request.dicttomerge)
        response = self._impl.update_dict(request)
        if self.cache is not None:
            self.cache.update_cache(
                rules,
                response.state,
                response.deletedpaths,
                version=self.version,
            )

    def delete_object(self, rules: str, path: str) -> None:
        """Delete an object."""
        request = DataModelProtoModule.DeleteObjectRequest(
            rules=rules, path=path, wait=True
        )
        response = self._impl.delete_object(request)
        if self.cache is not None:
            self.cache.update_cache(
                rules,
                response.state,
                response.deletedpaths,
                version=self.version,
            )

    def execute_command(
        self, rules: str, path: str, command: str, args: dict[str, _TValue]
    ) -> _TValue:
        """Execute the command."""
        request = DataModelProtoModule.ExecuteCommandRequest(
            rules=rules, path=path, command=command, wait=True
        )
        _convert_value_to_variant(args, request.args)
        response = self._impl.execute_command(request)
        if self.cache is not None:
            self.cache.update_cache(
                rules,
                response.state,
                response.deletedpaths,
                version=self.version,
            )
        return _convert_variant_to_value(response.result)

    def execute_query(
        self, rules: str, path: str, query: str, args: dict[str, _TValue]
    ) -> _TValue:
        """Execute the query."""
        request = DataModelProtoModule.ExecuteQueryRequest(
            rules=rules, path=path, query=query
        )
        _convert_value_to_variant(args, request.args)
        response = self._impl.execute_query(request)
        return _convert_variant_to_value(response.result)

    def create_command_arguments(self, rules: str, path: str, command: str) -> str:
        """Create command arguments."""
        request = DataModelProtoModule.CreateCommandArgumentsRequest(
            rules=rules, path=path, command=command
        )
        response = self._impl.create_command_arguments(request)
        return response.commandid

    def delete_command_arguments(
        self, rules: str, path: str, command: str, commandid: str
    ) -> None:
        """Delete command arguments."""
        request = DataModelProtoModule.DeleteCommandArgumentsRequest(
            rules=rules, path=path, command=command, commandid=commandid
        )
        self._impl.delete_command_arguments(request)

    def get_specs(
        self,
        rules: str,
        path: str,
    ) -> dict[str, Any]:
        """Get specifications."""
        request = DataModelProtoModule.GetSpecsRequest(
            rules=rules,
            path=path,
        )
        return MessageToDict(
            self._impl.get_specs(request).member, use_integers_for_enums=True
        )

    def get_static_info(self, rules: str) -> dict[str, Any]:
        """Get static info."""
        request = DataModelProtoModule.GetStaticInfoRequest(rules=rules)
        return MessageToDict(
            self._impl.get_static_info(request).info, use_integers_for_enums=True
        )

    def subscribe_events(self, request_dict: dict[str, Any]) -> dict[str, Any]:
        """Subscribe events."""
        request = DataModelProtoModule.SubscribeEventsRequest()
        ParseDict(request_dict, request)
        return [
            MessageToDict(x, use_integers_for_enums=True)
            for x in self._impl.subscribe_events(request).response
        ]

    def unsubscribe_events(self, tags: list[str]) -> dict[str, Any]:
        """Unsubscribe events."""
        request = DataModelProtoModule.UnsubscribeEventsRequest()
        request.tag[:] = tags
        return [
            MessageToDict(x, use_integers_for_enums=True)
            for x in self._impl.unsubscribe_events(request).response
        ]

    def unsubscribe_all_events(self) -> None:
        """Unsubscribe all subscribed events."""
        self.subscriptions.unsubscribe_all()

    def add_on_child_created(
        self, rules: str, path: str, child_type: str, obj, cb: Callable
    ) -> EventSubscription:
        """Add on child created."""
        request_dict = {
            "eventrequest": [
                {
                    "rules": rules,
                    "createdEventRequest": {
                        "parentpath": path,
                        "childtype": child_type,
                    },
                }
            ]
        }
        subscription = EventSubscription(self, path, request_dict)
        self.event_streaming.register_callback(subscription.tag, obj, cb)
        return subscription

    def add_on_deleted(
        self, rules: str, path: str, obj, cb: Callable
    ) -> EventSubscription:
        """Add on deleted."""
        request_dict = {
            "eventrequest": [
                {
                    "rules": rules,
                    "deletedEventRequest": {"path": path},
                }
            ]
        }
        subscription = EventSubscription(self, path, request_dict)
        self.event_streaming.register_callback(subscription.tag, obj, cb)
        return subscription

    def add_on_changed(
        self, rules: str, path: str, obj, cb: Callable
    ) -> EventSubscription:
        """Add on changed."""
        request_dict = {
            "eventrequest": [
                {
                    "rules": rules,
                    "modifiedEventRequest": {"path": path},
                }
            ]
        }
        subscription = EventSubscription(self, path, request_dict)
        self.event_streaming.register_callback(subscription.tag, obj, cb)
        return subscription

    def add_on_affected(
        self, rules: str, path: str, obj, cb: Callable
    ) -> EventSubscription:
        """Add on affected."""
        request_dict = {
            "eventrequest": [
                {
                    "rules": rules,
                    "affectedEventRequest": {"path": path},
                }
            ]
        }
        subscription = EventSubscription(self, path, request_dict)
        self.event_streaming.register_callback(subscription.tag, obj, cb)
        return subscription

    def add_on_affected_at_type_path(
        self, rules: str, path: str, child_type: str, obj, cb: Callable
    ) -> EventSubscription:
        """Add on affected at type path."""
        request_dict = {
            "eventrequest": [
                {
                    "rules": rules,
                    "affectedEventRequest": {
                        "path": path,
                        "subtype": child_type,
                    },
                }
            ]
        }
        subscription = EventSubscription(self, path, request_dict)
        self.event_streaming.register_callback(subscription.tag, obj, cb)
        return subscription

    def add_on_command_executed(
        self, rules: str, path: str, command: str, obj, cb: Callable
    ) -> EventSubscription:
        """Add on command executed."""
        request_dict = {
            "eventrequest": [
                {
                    "rules": rules,
                    "commandExecutedEventRequest": {
                        "path": path,
                        "command": command,
                    },
                }
            ]
        }
        subscription = EventSubscription(self, path, request_dict)
        self.event_streaming.register_callback(subscription.tag, obj, cb)
        return subscription

    def add_on_attribute_changed(
        self, rules: str, path: str, attribute: str, obj, cb: Callable
    ) -> EventSubscription:
        """Add on attribute changed."""
        request_dict = {
            "eventrequest": [
                {
                    "rules": rules,
                    "attributeChangedEventRequest": {
                        "path": path,
                        "attribute": attribute,
                    },
                }
            ]
        }
        subscription = EventSubscription(self, path, request_dict)
        self.event_streaming.register_callback(subscription.tag, obj, cb)
        return subscription

    def add_on_command_attribute_changed(
        self, rules: str, path: str, command: str, attribute: str, obj, cb: Callable
    ) -> EventSubscription:
        """Add on command attribute changed."""
        request_dict = {
            "eventrequest": [
                {
                    "rules": rules,
                    "commandAttributeChangedEventRequest": {
                        "path": path,
                        "command": command,
                        "attribute": attribute,
                    },
                }
            ]
        }
        subscription = EventSubscription(self, path, request_dict)
        self.event_streaming.register_callback(subscription.tag, obj, cb)
        return subscription


def convert_path_to_se_path(path: Path) -> str:
    """Convert a path structure to a StateEngine path.

    Parameters
    ----------
    path : Path
        Path structure.

    Returns
    -------
    str
        stateengine path
    """
    se_path = ""
    for comp in path:
        se_path += "/" + comp[0]
        if comp[1]:
            se_path += ":" + comp[1]
    return se_path


class PyCallableStateObject:
    """Any object which can be called to get its state.

    Methods
    -------
    __call__()
        Get the state of the current object.
    """

    def __call__(self, *args, **kwds) -> Any:
        return self.get_state()


class PyStateContainer(PyCallableStateObject):
    """Object class using StateEngine based DatamodelService as backend. Use this class
    instead of directly calling DatamodelService's method.

    Methods
    -------
    get_attr(attrib)
        Get the attribute value of the current object.
    getAttribValue(attrib)
        Get the attribute value of the current object.
        (This method is the same as the get_attr(attrib)
        method.)
    get_state()
        Get the state of the current object.
    getState()
        Deprecated camel case alias of get_state.
    set_state()
        Set the state of the current object.
    setState()
        Deprecated camel case alias of set_state.
    __call__()
        Set the state of the current object if state is provided else get its state.
    """

    def __init__(
        self, service: DatamodelService, rules: str, path: Path | None = None
    ) -> None:
        """__init__ method of PyStateContainer class."""
        super().__init__()
        self.__dict__.update(
            dict(
                service=service,
                rules=rules,
                path=[] if path is None else path,
                cached_attrs={},
            )
        )

    def get_remote_state(self) -> Any:
        """Get state of the current object."""
        return self.service.get_state(self.rules, convert_path_to_se_path(self.path))

    def get_state(self) -> Any:
        """Get state."""
        if self.service.cache is not None:
            state = self.service.cache.get_state(self.rules, self, NameKey.DISPLAY)
            if self.service.cache.is_unassigned(state):
                state = self.get_remote_state()
        else:
            state = self.get_remote_state()
        return state

    getState = get_state

    def fix_state(self) -> None:
        """Fix state."""
        self.service.fix_state(self.rules, self.path)

    fixState = fix_state

    def set_state(self, state: Any | None = None, **kwargs) -> None:
        """Set state of the current object.

        Parameters
        ----------
        state : Any, optional
            state
        kwargs : Any
            Keyword arguments.

        Raises
        ------
        ReadOnlyObjectError
            If the object is read-only.
        """
        if self.get_attr(Attribute.IS_READ_ONLY.value):
            raise ReadOnlyObjectError(type(self).__name__)
        self.service.set_state(
            self.rules, convert_path_to_se_path(self.path), kwargs or state
        )

    setState = set_state

    def _get_remote_attr(self, attrib: str) -> Any:
        return self.service.get_attribute_value(
            self.rules, convert_path_to_se_path(self.path), attrib
        )

    def _get_cached_attr(self, attrib: str) -> Any:
        cached_val = self.cached_attrs.get(attrib)
        if cached_val is None:
            cached_val = self._get_remote_attr(attrib)
            try:  # will fail for Fluent 23.1 or before
                self.add_on_attribute_changed(
                    attrib,
                    functools.partial(dict.__setitem__, self.cached_attrs, attrib),
                )
                self.cached_attrs[attrib] = cached_val
            except Exception:
                pass
        return cached_val

    def get_attr(self, attrib: str) -> Any:
        """Get attribute value of the current object.

        Parameters
        ----------
        attrib : str
            Name of the attribute.

        Returns
        -------
        Any
            Value of the attribute.
        """
        if pyfluent.DATAMODEL_USE_ATTR_CACHE:
            return self._get_cached_attr(attrib)
        return self._get_remote_attr(attrib)

    getAttribValue = get_attr

    def is_active(self) -> bool:
        """Returns true if the object is active."""
        return true_if_none(self.get_attr(Attribute.IS_ACTIVE.value))

    def is_read_only(self) -> bool:
        """Checks whether the object is read only."""
        return false_if_none(self.get_attr(Attribute.IS_READ_ONLY.value))

    def help(self) -> None:
        """Print help string."""
        response = self.service.get_specs(
            self.rules, convert_path_to_se_path(self.path)
        )
        help_string = _get_value_from_message_dict(
            response, [member_specs_oneof_fields, "common", "helpstring"]
        )
        print(help_string)

    def __call__(self, *args, **kwargs) -> Any:
        if kwargs:
            self.set_state(kwargs)
        elif args:
            self.set_state(args)
        else:
            return self.get_state()

    def add_on_attribute_changed(
        self, attribute: str, cb: Callable
    ) -> EventSubscription:
        """Register a callback for when an attribute is changed.

        Parameters
        ----------
        attribute : str
            attribute name
        cb : Callable
            Callback function

        Returns
        -------
        EventSubscription
            EventSubscription instance which can be used to unregister the callback
        """
        return self.service.add_on_attribute_changed(
            self.rules, convert_path_to_se_path(self.path), attribute, self, cb
        )

    def add_on_command_attribute_changed(
        self, command: str, attribute: str, cb: Callable
    ) -> EventSubscription:
        """Register a callback for when an attribute is changed.

        Parameters
        ----------
        command : str
            command name
        attribute : str
            attribute name
        cb : Callable
            Callback function

        Returns
        -------
        EventSubscription
            EventSubscription instance which can be used to unregister the callback
        """
        return self.service.add_on_command_attribute_changed(
            self.rules, convert_path_to_se_path(self.path), command, attribute, self, cb
        )

    def __dir__(self):

        all_children = list(self.__dict__) + dir(type(self))

        filtered_children = _FilterDatamodelNames(self.service)(self, all_children)

        dir_set = set(filtered_children)
        if self.get_attr(Attribute.IS_READ_ONLY.value):
            dir_set = dir_set - {"setState", "set_state"}

        return sorted(dir_set)


class PyMenu(PyStateContainer):
    """Object class using StateEngine based DatamodelService as backend. Use this class
    instead of directly calling DatamodelService's method.

    Methods
    -------
    __setattr__(name, value)
        Set state of the child object
    rename(new_name)
    name()
    create_command_arguments(command)
    """

    def __init__(
        self, service: DatamodelService, rules: str, path: Path | None = None
    ) -> None:
        """__init__ method of PyMenu class."""
        super().__init__(service, rules, path)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set state of the child object.

        Parameters
        ----------
        name : str
            child object name
        value : Any
            state
        """
        if hasattr(self, name) and isinstance(getattr(self, name), PyStateContainer):
            getattr(self, name).set_state(value)
        else:
            super().__setattr__(name, value)

    def name(self) -> str:
        """Get the name of the named object.

        Returns
        -------
        str
            name

        Raises
        ------
        InvalidNamedObject
            If the object is not a named object.
        """
        try:
            return self._name_()
        except AttributeError:
            raise InvalidNamedObject(self.__class__.__name__)

    def _raise_method_not_yet_implemented_exception(self) -> NoReturn:
        raise AttributeError("This method is yet to be implemented in pyfluent.")

    def delete_child(self) -> None:
        """Delete child object."""
        self._raise_method_not_yet_implemented_exception()

    def rename(self, new_name: str) -> None:
        """Rename the named object.

        Parameters
        ----------
        new_name : str
            New name for the object.
        """
        self.service.rename(self.rules, convert_path_to_se_path(self.path), new_name)

    def delete_child_objects(self, obj_type: str, child_names: list[str]):
        """Delete the named objects in 'child_names' from  the container..

        Parameters
        ----------
        obj_type: str
            Type of the named object container.
        child_names : List[str]
            List of named objects.
        """
        for child_name in child_names:
            child_path = f"{convert_path_to_se_path(self.path)}/{obj_type}:{child_name}"
            # delete_child_objects doesn't stream back on-deleted events. Thus
            # unsubscribing all subscription objects before the deletion.
            for stage in ["before", "after"]:
                self.service.subscriptions.unsubscribe_while_deleting(
                    self.rules, child_path, stage
                )
        self.service.delete_child_objects(
            self.rules, convert_path_to_se_path(self.path), obj_type, child_names
        )

    deleteChildObjects = delete_child_objects

    def delete_all_child_objects(self, obj_type):
        """Delete all the named objects in the container.

         Parameters
        ----------
        obj_type: str
            Type of the named object container.
        """
        child_path = f"{convert_path_to_se_path(self.path)}/{obj_type}:"
        # delete_all_child_objects doesn't stream back on-deleted events. Thus
        # unsubscribing all subscription objects before the deletion.
        for stage in ["before", "after"]:
            self.service.subscriptions.unsubscribe_while_deleting(
                self.rules, child_path, stage
            )
        self.service.delete_all_child_objects(
            self.rules, convert_path_to_se_path(self.path), obj_type
        )

    deleteAllChildObjects = delete_all_child_objects

    def create_command_arguments(self, command: str) -> str:
        """Create command arguments.

        Parameters
        ----------
        command : str
            Command name

        Returns
        -------
        str
            Command ID
        """
        return self.service.create_command_arguments(
            self.rules, convert_path_to_se_path(self.path), command
        )

    def add_on_child_created(self, child_type: str, cb: Callable) -> EventSubscription:
        """Register a callback for when a child object is created.

        Parameters
        ----------
        child_type : str
            Type of the child object
        cb : Callable
            Callback function

        Returns
        -------
        EventSubscription
            EventSubscription instance which can be used to unregister the callback
        """
        return self.service.add_on_child_created(
            self.rules, convert_path_to_se_path(self.path), child_type, self, cb
        )

    def add_on_deleted(self, cb: Callable) -> EventSubscription:
        """Register a callback for when the object is deleted.

        Parameters
        ----------
        cb : Callable
            Callback function

        Returns
        -------
        EventSubscription
            EventSubscription instance which can be used to unregister the callback
        """
        return self.service.add_on_deleted(
            self.rules, convert_path_to_se_path(self.path), self, cb
        )

    def add_on_changed(self, cb: Callable) -> EventSubscription:
        """Register a callback for when the object is modified.

        Parameters
        ----------
        cb : Callable
            Callback function

        Returns
        -------
        EventSubscription
            EventSubscription instance which can be used to unregister the callback
        """
        return self.service.add_on_changed(
            self.rules, convert_path_to_se_path(self.path), self, cb
        )

    def add_on_affected(self, cb: Callable) -> EventSubscription:
        """Register a callback for when the object is affected.

        Parameters
        ----------
        cb : Callable
            Callback function

        Returns
        -------
        EventSubscription
            EventSubscription instance which can be used to unregister the callback
        """
        return self.service.add_on_affected(
            self.rules, convert_path_to_se_path(self.path), self, cb
        )

    def add_on_affected_at_type_path(
        self, child_type: str, cb: Callable
    ) -> EventSubscription:
        """Register a callback for when the object is affected at child type.

        Parameters
        ----------
        child_type : str
            child type
        cb : Callable
            Callback function

        Returns
        -------
        EventSubscription
            EventSubscription instance which can be used to unregister the callback
        """
        return self.service.add_on_affected_at_type_path(
            self.rules, convert_path_to_se_path(self.path), child_type, self, cb
        )

    def add_on_command_executed(self, command: str, cb: Callable) -> EventSubscription:
        """Register a callback for when a command is executed.

        Parameters
        ----------
        command : str
            command name
        cb : Callable
            Callback function

        Returns
        -------
        EventSubscription
            EventSubscription instance which can be used to unregister the callback
        """
        return self.service.add_on_command_executed(
            self.rules, convert_path_to_se_path(self.path), command, self, cb
        )


class PyParameter(PyStateContainer):
    """Object class using StateEngine based DatamodelService as backend.

    Use this class instead of directly calling DatamodelService's method.
    """

    def default_value(self) -> Any:
        """Get default value of the parameter."""
        return self.get_attr(Attribute.DEFAULT.value)

    def add_on_changed(self, cb: Callable) -> EventSubscription:
        """Register a callback for when the object is modified.

        Parameters
        ----------
        cb : Callable
            Callback function

        Returns
        -------
        EventSubscription
            EventSubscription instance which can be used to unregister the callback
        """
        return self.service.add_on_changed(
            self.rules, convert_path_to_se_path(self.path), self, cb
        )


def _bool_value_if_none(val: bool | None, default: bool) -> bool:
    if isinstance(val, bool) or val is None:
        return default if val is None else val
    raise TypeError(f"{val} should be a bool or None")


def true_if_none(val: bool | None) -> bool:
    """Returns true if 'val' is true or None, else returns false."""
    return _bool_value_if_none(val, default=True)


def false_if_none(val: bool | None) -> bool:
    """Returns false if 'val' is false or None, else returns true."""
    return _bool_value_if_none(val, default=False)


class PyTextual(PyParameter):
    """Provides interface for textual parameters."""

    def allowed_values(self) -> list[str]:
        """Get allowed values."""
        return self.get_attr(Attribute.ALLOWED_VALUES.value)


class PyNumerical(PyParameter):
    """Provides interface for numerical parameters."""

    def min(self) -> float:
        """Minimum value of the numerical parameter."""
        return self.get_attr(Attribute.MIN.value)

    def max(self) -> float:
        """Maximum value of the numerical parameter."""
        return self.get_attr(Attribute.MAX.value)


class PyDictionary(PyParameter):
    """Provides interface for dictionaries.

    Methods
    -------
    update_dict(dict_state)
        Update the state of the current object if the current object
        is a Dict in the data model, else throws RuntimeError
        (currently not showing up in Python). Update is executed according
        to dict.update semantics
    updateDict(dict_state)
        Update the state of the current object if the current object
        is a Dict in the data model, else throws RuntimeError
        (currently not showing up in Python). Update is executed according
        to dict.update semantics (same as update_dict(dict_state))]
    """

    def update_dict(self, dict_state: dict[str, Any], recursive=False) -> None:
        """Update the state of the current object if the current object is a Dict in the
        data model, else throws RuntimeError (currently not showing up in Python).
        Update is executed according to dict.update semantics.

        Parameters
        ----------
        dict_state : dict[str, Any]
            Incoming dict state

        recursive: bool
            Flag to update the nested dictionary structure.

        Raises
        ------
        ReadOnlyObjectError
            If the object is read-only.
        """
        if self.get_attr(Attribute.IS_READ_ONLY.value):
            raise ReadOnlyObjectError(type(self).__name__)
        self.service.update_dict(
            self.rules, convert_path_to_se_path(self.path), dict_state, recursive
        )

    updateDict = update_dict

    def __dir__(self):
        dir_list = set(list(self.__dict__.keys()) + dir(type(self)))
        if self.get_attr(Attribute.IS_READ_ONLY.value):
            dir_list = dir_list - {"updateDict", "update_dict"}

        return sorted(dir_list)


class PyNamedObjectContainer:
    """Container class using the StateEngine-based DatamodelService as the backend. Use
    this class instead of directly calling the DatamodelService's method.

    Methods
    -------
    __len__()
        Return a count of the child objects.
    __iter__()
        Return the next child object.
    __getitem__(key)
        Return the child object by key.
    __setitem__(key, value)
        Set the state of the child object by name.
    __delitem__(key)
        Delete the child object by name.
    """

    def __init__(
        self, service: DatamodelService, rules: str, path: Path | None = None
    ) -> None:
        """__init__ method of PyNamedObjectContainer class."""
        self.service = service
        self.rules = rules
        if path is None:
            self.path = []
        else:
            self.path = path

    def _get_child_object_names(self) -> list[str]:
        parent_path = self.path[0:-1]
        child_type_suffix = self.path[-1][0] + ":"
        response = self.service.get_specs(
            self.rules, convert_path_to_se_path(parent_path)
        )
        child_object_names = []
        for struct_type in ("singleton", "namedobject"):
            struct_field = response.get(struct_type)
            if struct_field:
                for member in struct_field["members"]:
                    if member.startswith(child_type_suffix):
                        child_object_names.append(member[len(child_type_suffix) :])
        return child_object_names

    def _get_child_object_display_names(self) -> list[str]:
        child_object_display_names = []
        for name in self._get_child_object_names():
            name_path = self.path[0:-1]
            name_path.append((self.path[-1][0], name))
            name_path.append(("_name_", ""))
            child_object_display_names.append(
                PyMenu(self.service, self.rules, name_path).get_state()
            )
        return child_object_display_names

    def get_object_names(self) -> Any:
        """Displays the name of objects within a container."""
        if self.service.version <= FluentVersion.v241:
            return self._get_child_object_display_names()
        else:
            return self.service.get_object_names(
                self.rules, convert_path_to_se_path(self.path)
            )

    getChildObjectDisplayNames = get_object_names

    def __len__(self) -> int:
        """Return a count of child objects.

        Returns
        -------
        int
            Count of child objects.
        """
        return len(self.get_object_names())

    def __iter__(self) -> Iterator[PyMenu]:
        """Return the next child object.

        Yields
        -------
        Iterator[PyMenu]
            Iterator of child objects.
        """
        for name in self.get_object_names():
            child_path = self.path[:-1]
            child_path.append((self.path[-1][0], name))
            yield getattr(self.__class__, f"_{self.__class__.__name__}")(
                self.service, self.rules, child_path
            )

    def _get_item(self, key: str) -> PyMenu:
        if key in self.get_object_names():
            child_path = self.path[:-1]
            child_path.append((self.path[-1][0], key))
            return getattr(self.__class__, f"_{self.__class__.__name__}")(
                self.service, self.rules, child_path
            )
        else:
            raise LookupError(
                f"{key} is not found at path " f"{convert_path_to_se_path(self.path)}"
            )

    def _del_item(self, key: str) -> None:
        if key in self.get_object_names():
            child_path = self.path[:-1]
            child_path.append((self.path[-1][0], key))
            se_path = convert_path_to_se_path(child_path)
            # All subscription objects except those of on-deleted type are unsubscribed
            # before the datamodel object is deleted.
            self.service.subscriptions.unsubscribe_while_deleting(
                self.rules, se_path, "before"
            )
            # On-deleted subscription objects are unsubscribed after the datamodel
            # object is deleted.
            self[key].add_on_deleted(
                lambda: self.service.subscriptions.unsubscribe_while_deleting(
                    self.rules, se_path, "after"
                )
            )
            self.service.delete_object(self.rules, se_path)
        else:
            raise LookupError(
                f"{key} is not found at path " f"{convert_path_to_se_path(self.path)}"
            )

    def __getitem__(self, key: str) -> PyMenu:
        """Return the child object by key.

        Parameters
        ----------
        key : str
            Name of the child object.

        Returns
        -------
        PyMenu
            Child object.
        """
        return self._get_item(key)

    def get(self, key: str) -> PyMenu | None:
        """Return the child object by key.

        Parameters
        ----------
        key : str
            Name of the child object.

        Returns
        -------
        PyMenu
            Child object.
        """
        try:
            return self._get_item(key)
        except LookupError:
            return

    def __setitem__(self, key: str, value: Any) -> None:
        """Set state of the child object by name.

        Parameters
        ----------
        key : str
            Name of the child object.
        value : Any
            State of the child object.
        """
        if isinstance(value, dict) and not value:
            value["_name_"] = key
        parent_state = {f"{self.__class__.__name__}:{key}": value}
        PyMenu(self.service, self.rules, self.path[:-1]).set_state(parent_state)

    def __delitem__(self, key: str) -> None:
        """Delete the child object by name.

        Parameters
        ----------
        key : str
            Name of the child object.
        """
        self._del_item(key)

    @staticmethod
    def _get_type_and_name(type_and_name):
        return type_and_name.split(":", maxsplit=1)

    def _compare_type(self, obj_type):
        child_obj_type = self.path[-1][0]
        return child_obj_type == obj_type

    def get_state(self):
        """Returns state of the container."""
        parent_state = PyMenu(self.service, self.rules, self.path[:-1]).get_state()
        returned_state = {}

        for key, value in parent_state.items():
            type_and_name = self._get_type_and_name(key)
            if len(type_and_name) == 2 and self._compare_type(type_and_name[0]):
                returned_state[type_and_name[1]] = value

        return dict(sorted(returned_state.items()))

    getState = __call__ = get_state


class PyQuery:
    """Query class using the StateEngine-based DatamodelService as the backend. Use this
    class instead of directly calling the DatamodelService's method.

    Methods
    -------
    __call__()
        Execute the query.
    help()
        Print the query help string.
    """

    def __init__(
        self,
        service: DatamodelService,
        rules: str,
        query: str,
        path: Path = None,
    ):
        """__init__ method of PyQuery class."""
        self.service = service
        self.rules = rules
        self.query = query
        if path is None:
            self.path = []
        else:
            self.path = path

    def __call__(self, *args, **kwds) -> Any:
        """Execute the query.

        Returns
        -------
        Any
            Return value.
        """
        return self.service.execute_query(
            self.rules, convert_path_to_se_path(self.path), self.query, kwds
        )

    def help(self) -> None:
        """Prints help string."""
        response = self.service.get_specs(
            self.rules, convert_path_to_se_path(self.path)
        )
        help_string = _get_value_from_message_dict(
            response, [member_specs_oneof_fields, "query", "helpstring"]
        )
        print(help_string)


class PyCommand:
    """Command class using the StateEngine-based DatamodelService as the backend. Use
    this class instead of directly calling the DatamodelService's method.

    Methods
    -------
    __call__()
        Execute the command.
    help()
        Print the command help string.
    """

    _full_static_info: dict[str, dict[str, Any]] = {}

    def __init__(
        self,
        service: DatamodelService,
        rules: str,
        command: str,
        path: Path | None = None,
    ) -> None:
        """__init__ method of PyCommand class."""
        self.service = service
        self.rules = rules
        self.command = command
        if path is None:
            self.path = []
        else:
            self.path = path
        self._static_info = None  # command's static info

    def _get_file_purpose(self, arg):
        try:
            cmd_instance = self.create_instance()
            arg_instance = getattr(cmd_instance, arg)
            file_purpose = arg_instance.get_attr("filePurpose")
            if file_purpose:
                if file_purpose == "input":
                    if _InputFile not in self.__class__.__bases__:
                        self.__class__.__bases__ += (_InputFile,)
                elif file_purpose == "output":
                    if _OutputFile not in self.__class__.__bases__:
                        self.__class__.__bases__ += (_OutputFile,)
                elif file_purpose == "inout":
                    if _InOutFile not in self.__class__.__bases__:
                        self.__class__.__bases__ += (_InOutFile,)
                else:
                    raise DisallowedFilePurpose(
                        "File purpose", file_purpose, ["input", "output", "inout"]
                    )
            del cmd_instance, arg_instance
            return file_purpose if file_purpose else None
        except AttributeError:
            pass

    def before_execute(self, value):
        """Executes before command execution."""
        if hasattr(self, "_do_before_execute"):
            return self._do_before_execute(value)
        else:
            return value

    def after_execute(self, value):
        """Executes after command execution."""
        if hasattr(self, "_do_after_execute"):
            self._do_after_execute(value)

    def __call__(self, *args, **kwds) -> Any:
        """Execute the command.

        Returns
        -------
        Any
            Return value.
        """
        for arg, value in kwds.items():
            if self._get_file_purpose(arg):
                kwds[arg] = self.before_execute(value)
        command = self.service.execute_command(
            self.rules, convert_path_to_se_path(self.path), self.command, kwds
        )
        for arg, value in kwds.items():
            if self._get_file_purpose(arg):
                self.after_execute(value)
        return command

    def help(self) -> None:
        """Prints help string."""
        response = self.service.get_specs(
            self.rules, convert_path_to_se_path(self.path)
        )
        help_string = _get_value_from_message_dict(
            response, [member_specs_oneof_fields, "common", "helpstring"]
        )
        print(help_string)

    def _create_command_arguments(self) -> str:
        commandid = self.service.create_command_arguments(
            self.rules, convert_path_to_se_path(self.path), self.command
        )
        return commandid

    def _get_static_info(self) -> dict[str, Any]:
        print(
            f"In PyCommand._get_static_info(), info is None? {self._static_info is None}"
        )
        if self._static_info is None:
            print("Because it's None, get it from the rules map")
            if self.rules not in PyCommand._full_static_info.keys():
                # Populate the static info with respect to a rules only if the
                # same info has not been obtained in another context already.
                # If the information is available, we can use it without additional remote calls.
                response = self.service.get_static_info(self.rules)
                print(f"This is the acquired response: {response}")
                PyCommand._full_static_info[self.rules] = response
            rules_static_info = PyCommand._full_static_info[self.rules]
            static_info_path = []
            for comp in self.path:
                static_info_path.append("namedobjects" if comp[1] else "singletons")
                static_info_path.append(comp[0])
            parent_static_info = _get_value_from_message_dict(
                rules_static_info, static_info_path
            )
            print(
                f"This is the parent_static_info: {parent_static_info}, call _get_value_from_message_dict"
            )
            self._static_info = _get_value_from_message_dict(
                parent_static_info, ["commands", self.command, "commandinfo"]
            )
        print(f"This is the returned info: {self._static_info}")
        return self._static_info

    def create_instance(self) -> "PyCommandArguments":
        """Create a command instance."""
        try:
            print("In PyCommand.create_instance(), calling _get_static_info()...")
            static_info = self._get_static_info()
            id = self._create_command_arguments()
            return PyCommandArguments(
                self.service,
                self.rules,
                self.command,
                self.path.copy(),
                id,
                static_info.get("args"),
            )
        except RuntimeError:
            logger.warning(
                "Create command arguments object is available from 23.1 onwards"
            )


class _InputFile:
    def _do_before_execute(self, value):
        try:
            file_names = value if isinstance(value, list) else [value]
            base_names = []
            for file_name in file_names:
                self.service.file_transfer_service.upload(file_name=file_name)
                base_names.append(os.path.basename(file_name))
            return base_names if isinstance(value, list) else base_names[0]
        except AttributeError:
            return value


class _OutputFile:
    def _do_after_execute(self, value):
        try:
            file_names = value if isinstance(value, list) else [value]
            for file_name in file_names:
                self.service.file_transfer_service.download(file_name=file_name)
        except AttributeError:
            pass


class _InOutFile(_InputFile, _OutputFile):
    pass


class PyCommandArgumentsSubItem(PyCallableStateObject):
    """Class representing command argument in datamodel."""

    def __init__(
        self,
        parent,
        name: str,
        service: DatamodelService,
        rules: str,
        path: Path,
        parent_arg,
    ) -> None:
        """__init__ method of PyCommandArgumentsSubItem class."""
        self.__dict__.update(
            dict(
                parent=parent,
                name=name,
                service=service,
                rules=rules,
                path=path,
                parent_arg=parent_arg,
            )
        )

    def get_state(self) -> Any:
        """Get state of the command argument."""
        parent_state = self.parent.get_state()
        return parent_state[self.name]

    getState = get_state

    def set_state(self, state) -> Any:
        """Set state of the command argument."""
        self.parent.set_state({self.name: state})

    setState = set_state

    def get_attr(self, attrib: str) -> Any:
        """Get attribute value of the command argument.

        Parameters
        ----------
        attrib : str
            attribute name

        Returns
        -------
        Any
            attribute value
        """
        attrib_path = f"{self.name}/{attrib}"
        return self.parent.get_attr(attrib_path)

    getAttribValue = get_attr

    def help(self) -> None:
        """Get help."""
        pass

    def __setattr__(self, key, value):
        if isinstance(value, PyCommandArgumentsSubItem):
            super().__setattr__(key, value)
        else:
            getattr(self, key).set_state(value)


class PyCommandArguments(PyStateContainer):
    """Class representing command arguments in datamodel."""

    def __init__(
        self,
        service: DatamodelService,
        rules: str,
        command: str,
        path: Path,
        id: str,
        static_info,
    ) -> None:
        """__init__ method of PyCommandArguments class."""
        super().__init__(service, rules, path)
        self.__dict__.update(
            dict(
                static_info=static_info,
                command=command,
                id=id,
            )
        )
        self.path.append((command, id))

    def __del__(self) -> None:
        try:
            self.service.delete_command_arguments(
                self.rules,
                convert_path_to_se_path(self.path[:-1]),
                self.path[-1][0],
                self.path[-1][1],
            )
        except Exception as exc:
            logger.info("__del__ %s: %s" % (type(exc).__name__, exc))

    def __getattr__(self, attr: str) -> PyCommandArgumentsSubItem | None:
        for arg in self.static_info:
            if arg["name"] == attr:
                mode = DataModelType.get_mode(arg["type"])
                py_class = mode.value[1]
                return py_class(self, attr, self.service, self.rules, self.path, arg)

    def get_attr(self, attrib: str) -> Any:
        """Get attribute value of the current object.

        Parameters
        ----------
        attrib : str
            Name of the attribute.

        Returns
        -------
        Any
            Value of the attribute.
        """
        return self._get_remote_attr(attrib)

    def __setattr__(self, key, value):
        if isinstance(value, PyCommandArgumentsSubItem):
            super().__setattr__(key, value)
        else:
            getattr(self, key).set_state(value)


class PyTextualCommandArgumentsSubItem(PyCommandArgumentsSubItem, PyTextual):
    """Class representing textual command argument in datamodel."""

    def __init__(
        self,
        parent,
        attr: str,
        service: DatamodelService,
        rules: str,
        path: Path,
        arg,
    ) -> None:
        """__init__ method of PyTextualCommandArgumentsSubItem class."""
        PyCommandArgumentsSubItem.__init__(
            self, parent, attr, service, rules, path, arg
        )
        PyTextual.__init__(self, service, rules, path)


class PyNumericalCommandArgumentsSubItem(PyCommandArgumentsSubItem, PyNumerical):
    """Class representing numerical command argument in datamodel."""

    def __init__(
        self,
        parent,
        attr: str,
        service: DatamodelService,
        rules: str,
        path: Path,
        arg,
    ) -> None:
        """__init__ method of PyNumericalCommandArgumentsSubItem class."""
        PyCommandArgumentsSubItem.__init__(
            self, parent, attr, service, rules, path, arg
        )
        PyNumerical.__init__(self, service, rules, path)


class PyDictionaryCommandArgumentsSubItem(PyCommandArgumentsSubItem, PyDictionary):
    """Class representing dictionary-like command argument in datamodel."""

    def __init__(
        self,
        parent,
        attr: str,
        service: DatamodelService,
        rules: str,
        path: Path,
        arg,
    ) -> None:
        """__init__ method of PyDictionaryCommandArgumentsSubItem class."""
        PyCommandArgumentsSubItem.__init__(
            self, parent, attr, service, rules, path, arg
        )
        PyDictionary.__init__(self, service, rules, path)


class PyParameterCommandArgumentsSubItem(PyCommandArgumentsSubItem, PyParameter):
    """Class representing generic parameter-like command argument in datamodel."""

    def __init__(
        self,
        parent,
        attr: str,
        service: DatamodelService,
        rules: str,
        path: Path,
        arg,
    ) -> None:
        """__init__ method of PyParameterCommandArgumentsSubItem class."""
        PyCommandArgumentsSubItem.__init__(
            self, parent, attr, service, rules, path, arg
        )
        PyParameter.__init__(self, service, rules, path)


class PySingletonCommandArgumentsSubItem(PyCommandArgumentsSubItem):
    """Class representing singleton-like command argument in datamodel."""

    def __init__(
        self,
        parent,
        attr: str,
        service: DatamodelService,
        rules: str,
        path: Path,
        arg,
    ) -> None:
        """__init__ method of PySingletonCommandArgumentsSubItem class."""
        PyCommandArgumentsSubItem.__init__(
            self, parent, attr, service, rules, path, arg
        )

    def __getattr__(self, attr: str) -> PyCommandArgumentsSubItem:
        arg = self.parent_arg["info"]["parameters"][attr]

        mode = DataModelType.get_mode(arg["type"])
        py_class = mode.value[1]
        return py_class(self, attr, self.service, self.rules, self.path, arg)


class DataModelType(Enum):
    """An enumeration over datamodel types."""

    # Really???

    # Tuple:   Name, Solver object type, Meshing flag, Launcher options
    # Really???
    TEXT = (["String", "ListString", "String List"], PyTextualCommandArgumentsSubItem)
    NUMBER = (
        ["Real", "Int", "ListReal", "Real List", "Integer", "ListInt"],
        PyNumericalCommandArgumentsSubItem,
    )
    DICTIONARY = (["Dict"], PyDictionaryCommandArgumentsSubItem)
    PARAMETER = (
        ["Bool", "Logical", "Logical List"],
        PyParameterCommandArgumentsSubItem,
    )
    MODELOBJECT = (["ModelObject"], PySingletonCommandArgumentsSubItem)

    @staticmethod
    def get_mode(mode: str) -> "DataModelType":
        """Returns the datamodel type.

        Parameters
        ----------
        mode : str
            mode

        Returns
        -------
        DataModelType
            datamodel type

        Raises
        ------
        InvalidArgument
            If an unknown mode is passed.
        """
        for m in DataModelType:
            if mode in m.value[0]:
                return m
        raise InvalidArgument(f"The specified mode: {mode} was not found.")


class PyMenuGeneric(PyMenu):
    """Generic PyMenu class for when generated API code is not available."""

    attrs = ("service", "rules", "path", "cached_attrs")

    def _get_child_names(self) -> tuple[list, list, list, list]:
        response = self.service.get_specs(
            self.rules, convert_path_to_se_path(self.path)
        )
        singleton_names = []
        creatable_type_names = []
        command_names = []
        query_names = []
        for struct_type in ("singleton", "namedobject"):
            struct_field = response.get(struct_type)
            if struct_field:
                for member in struct_field["members"]:
                    if ":" not in member:
                        singleton_names.append(member)
                creatable_type_names = struct_field.get("creatabletypes", [])
                command_names = [x["name"] for x in struct_field.get("commands", [])]
                query_names = [x["name"] for x in struct_field.get("queries", [])]
        return singleton_names, creatable_type_names, command_names, query_names

    def _get_child(self, name: str) -> PyNamedObjectContainer | PyCommand | PyQuery:
        singletons, creatable_types, commands, queries = self._get_child_names()
        if name in singletons:
            child_path = self.path + [(name, "")]
            return PyMenuGeneric(self.service, self.rules, child_path)
        elif name in creatable_types:
            child_path = self.path + [(name, "")]
            return PyNamedObjectContainerGeneric(self.service, self.rules, child_path)
        elif name in commands:
            return PyCommand(self.service, self.rules, name, self.path)
        elif name in queries:
            return PyQuery(self.service, self.rules, name, self.path)
        else:
            raise LookupError(
                f"{name} is not found at path " f"{convert_path_to_se_path(self.path)}"
            )

    def __dir__(self) -> list[str]:
        return list(itertools.chain(*self._get_child_names()))

    def __getattr__(self, name: str):
        if name in PyMenuGeneric.attrs:
            return super().__getattr__(name)
        else:
            return self._get_child(name)


class PySimpleMenuGeneric(PyMenu, PyDictionary):
    """A simple implementation of PyMenuGeneric applicable only for SINGLETONS.

    This is required for the stand-alone datamodel server to avoid the usage of
    'service.get_specs'
    """

    attrs = ("service", "rules", "path")

    def _get_child(self, name: str) -> "PySimpleMenuGeneric":
        child_path = self.path + [(name, "")]
        return PySimpleMenuGeneric(self.service, self.rules, child_path)

    def __getattr__(self, name: str):
        if name in PySimpleMenuGeneric.attrs:
            return super().__getattr__(name)
        else:
            return self._get_child(name)


class PyNamedObjectContainerGeneric(PyNamedObjectContainer):
    """Generic PyNamedObjectContainer class for when generated API code is not
    available."""

    def __iter__(self) -> Iterator[PyMenuGeneric]:
        for name in self.get_object_names():
            child_path = self.path[:-1]
            child_path.append((self.path[-1][0], name))
            yield PyMenuGeneric(self.service, self.rules, child_path)

    def _get_item(self, key: str) -> PyMenuGeneric:
        if key in self.get_object_names():
            child_path = self.path[:-1]
            child_path.append((self.path[-1][0], key))
            return PyMenuGeneric(self.service, self.rules, child_path)
        else:
            raise LookupError(
                f"{key} is not found at path " f"{convert_path_to_se_path(self.path)}"
            )
